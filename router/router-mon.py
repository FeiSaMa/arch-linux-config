#!/usr/bin/env python3
"""
T14 Router Monitor — Full-screen Dashboard (60-col layout for ter-228b)
Runs on Linux console TTY (16-color mode), uses Mihomo REST API.
"""

import json
import time
import sys
from datetime import datetime
from urllib.request import urlopen, Request

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

API_BASE = "http://127.0.0.1:9097"
SECRET = "20080201"
REFRESH_S = 1

# -- 16-color palette (approximating Catppuccin Macchiato) --
FG, DIM, CYAN, GREEN, YELLOW, RED, MAGENTA, BLUE, WHITE, BORDER = \
    "white", "bright_black", "cyan", "green", "yellow", "red", "magenta", "blue", "white", "bright_black"

BLOCKS = " ▁▂▃▄▅▆▇█"

# --- API ---

def fetch_json(endpoint):
    url = f"{API_BASE}{endpoint}"
    req = Request(url, headers={"Authorization": f"Bearer {SECRET}"})
    try:
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None

def fetch_conns():
    data = fetch_json("/connections")
    if not data:
        return [], 0, 0
    return data.get("connections", []), data.get("downloadTotal", 0), data.get("uploadTotal", 0)

def fetch_proxies():
    data = fetch_json("/proxies")
    if not data:
        return {}
    info = {}
    for name, p in data.get("proxies", {}).items():
        if p.get("type") == "Selector":
            now = p.get("now", "?")
            hist = p.get("history", [])
            delay = f"{hist[-1].get('delay',0)}ms" if hist else "?"
            info[name] = (now, delay)
    return info

def fmt_bytes(n):
    if n < 1024:     return f"{n}B"
    for unit in ("K", "M", "G"):
        n /= 1024
        if n < 1024: return f"{n:.0f}{unit}"
    return f"{n:.0f}G"

def fmt_spd(bps):
    if bps < 1000:   return f"{bps:.0f}B/s"
    bps /= 1000
    if bps < 1000:   return f"{bps:.0f}K/s"
    bps /= 1000;     return f"{bps:.1f}M/s"

def rlabel(rule, payload):
    if rule == "MATCH":
        return "ALL"
    return (payload or rule)[:12]

def rstyle(rule):
    u = (rule or "").upper()
    if "DIRECT" in u:   return ("D", GREEN)
    if "REJECT" in u:   return ("R", RED)
    return ("P", MAGENTA)

def sparkline(data, w=30):
    if not data or max(data, default=0) == 0:
        return BLOCKS[0] * w
    n, mx, out = len(data), max(data) or 1, ""
    step = max(1, n / w)
    for i in range(w):
        idx = int(i * step)
        if idx >= n:
            out += " "; continue
        out += BLOCKS[min(int(data[idx] / mx * 8), 8)]
    return out

# --- Layout ---

HEADER = Text(
    "[bold]T14 ROUTER MONITOR[/]",
    justify="center",
)

def build(time_str, conns_sorted, dl_total, ul_total, up_spd, dn_spd, proxies):
    layout = Layout()
    layout.split(
        Layout(name="top", size=3),
        Layout(name="mid"),
        Layout(name="bot", size=3),
    )
    layout["mid"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=3),
    )

    # top: title + time
    top_txt = Text()
    top_txt.append(HEADER)
    top_txt.append(f"  [dim]{time_str}[/]")
    layout["top"].update(Panel(Align.center(top_txt), style=BORDER, box=box.HEAVY))

    # left: speed + totals + nodes
    left = Text()
    # speed bars (15 chars max)
    scale = max(up_spd, dn_spd, 1)
    bar_up = "█" * int(min(up_spd / scale * 13, 13))
    bar_dn = "█" * int(min(dn_spd / scale * 13, 13))
    left.append("[bold cyan]UP[/]\n")
    left.append(f"[cyan]{bar_up}[/] [bold]{fmt_spd(up_spd)}[/]\n\n")
    left.append("[bold blue]DOWN[/]\n")
    left.append(f"[blue]{bar_dn}[/] [bold]{fmt_spd(dn_spd)}[/]\n\n")
    left.append("[bold]TOTAL[/]\n")
    left.append(f"[cyan]Up[/]  {fmt_bytes(ul_total)}\n")
    left.append(f"[blue]Dn[/]  {fmt_bytes(dl_total)}\n")
    left.append(f"[{YELLOW}]Conns[/] {len(conns_sorted)}\n\n")
    left.append("[bold]NODES[/]\n")
    if proxies:
        for name, (now, delay) in list(proxies.items())[:5]:
            short = name[:14]
            left.append(f"[dim]{short}[/] → [bold]{now[:12]}[/] [{YELLOW}]{delay}[/]\n")
    else:
        left.append("[dim]no data[/]")
    layout["left"].update(Panel(left, title="[bold]NETWORK[/]", border_style=BORDER, box=box.ROUNDED))

    # right: connection table
    tbl = Table(box=box.SIMPLE, border_style=BORDER, expand=True, show_header=True, header_style=f"bold {DIM}")
    tbl.add_column("DESTINATION", width=28)
    tbl.add_column("", width=2)   # rule icon
    tbl.add_column("TRAFFIC", width=9, justify="right")

    for c in conns_sorted[:16]:
        meta = c.get("metadata", {})
        dst = meta.get("host", "") or meta.get("destinationIP", "?")
        port = meta.get("destinationPort", "")
        dst_full = f"{dst}:{port}" if port else dst
        rule = rlabel(c.get("rule", ""), c.get("rulePayload", ""))
        sym, clr = rstyle(c.get("rule", ""))
        traffic = fmt_bytes(c.get("download", 0))
        tbl.add_row(dst_full[:27], f"[bold {clr}]{sym}[/]", f"[{clr}]{traffic}[/]")

    layout["right"].update(Panel(
        tbl,
        title=f"[bold]CONNECTIONS[/] ([{YELLOW}]{len(conns_sorted)}[/])",
        border_style=BORDER, box=box.ROUNDED,
    ))

    # bottom: sparkline + controls
    bot = Text()
    bot.append(f"UP  [cyan]{sparkline(history_up, 18)}[/] [bold cyan]{fmt_spd(up_spd)}[/]  ")
    bot.append(f"DOWN [blue]{sparkline(history_dn, 18)}[/] [bold blue]{fmt_spd(dn_spd)}[/]  ")
    bot.append(f" [{RED}]q[/] quit")
    layout["bot"].update(Panel(bot, style=BORDER, box=box.HEAVY))

    return layout


# --- Globals for sparkline ---
history_up = [0] * 60
history_dn = [0] * 60


def run():
    global history_up, history_dn
    console = Console()
    prev_ul = prev_dl = 0
    prev_ts = time.time()

    with Live(console=console, refresh_per_second=REFRESH_S, screen=True) as live:
        while True:
            now = time.time()
            ts = datetime.now().strftime("%H:%M:%S")

            conns, dl, ul = fetch_conns()
            proxies = fetch_proxies()

            elapsed = max(now - prev_ts, 0.1)
            up_spd = max(0, int((ul - prev_ul) / elapsed))
            dn_spd = max(0, int((dl - prev_dl) / elapsed))
            prev_ul, prev_dl, prev_ts = ul, dl, now

            history_up.pop(0); history_up.append(up_spd)
            history_dn.pop(0); history_dn.append(dn_spd)

            sorted_conns = sorted(conns, key=lambda c: c.get("download", 0), reverse=True)[:16]

            layout = build(ts, sorted_conns, dl, ul, up_spd, dn_spd, proxies)
            live.update(layout)
            time.sleep(REFRESH_S)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
