#!/usr/bin/env python3
"""
T14 Router Monitor — Full-screen Dashboard
Layout for full-height, explicit Text() styles for TTY compat.
"""

import json
import time
import sys
from datetime import datetime
from urllib.request import urlopen, Request

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich import box

API_BASE = "http://127.0.0.1:9097"
SECRET = "20080201"
REFRESH_S = 1

# --- Styles ---
S_BOLD, S_DIM, S_WHITE, S_YELLOW, S_RED = "bold", "bright_black", "white", "yellow", "red"
S_CYAN, S_B_CYAN, S_BLUE, S_B_BLUE, S_MAGENTA, S_GREEN = (
    "cyan", "bold cyan", "blue", "bold blue", "magenta", "green")

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
    if n < 1024: return f"{n}B"
    for u in ("K","M","G"):
        n/=1024
        if n<1024: return f"{n:.0f}{u}"
    return f"{n:.0f}G"

def fmt_spd(bps):
    if bps < 1000: return f"{bps:.0f}B/s"
    bps/=1000
    if bps<1000: return f"{bps:.0f}K/s"
    bps/=1000; return f"{bps:.1f}M/s"

def rstyle(rule):
    u = (rule or "").upper()
    if "DIRECT" in u: return "D", S_GREEN
    if "REJECT" in u: return "R", S_RED
    return "P", S_MAGENTA

# --- Layout ---

def build(ts, conns, speeds, dl, ul, us, ds, proxies):
    layout = Layout()

    # Build left panel text
    left = Text()

    # UP bar
    scale = max(us, ds, 1)
    up_w = int(min(us / scale * 22, 22))
    left.append(Text("UP\n", style=S_B_CYAN))
    left.append(Text("#" * up_w + " " * (22 - up_w), style=S_CYAN))
    left.append(Text(f"\n{fmt_spd(us)}\n\n", style=S_B_CYAN))

    # DOWN bar
    dn_w = int(min(ds / scale * 22, 22))
    left.append(Text("DOWN\n", style=S_B_BLUE))
    left.append(Text("#" * dn_w + " " * (22 - dn_w), style=S_BLUE))
    left.append(Text(f"\n{fmt_spd(ds)}\n\n", style=S_B_BLUE))

    # Totals
    left.append(Text("TOTAL\n", style=S_BOLD))
    left.append(Text(f"Up  {fmt_bytes(ul)}\n", style=S_CYAN))
    left.append(Text(f"Dn  {fmt_bytes(dl)}\n", style=S_BLUE))
    left.append(Text(f"Conns {len(conns)}\n\n", style=S_YELLOW))

    # Node
    if proxies:
        first = list(proxies.items())[0]
        name, (now, delay) = first
        left.append(Text("NODE\n", style=S_BOLD))
        left.append(Text(f"{now[:16]}\n", style=S_WHITE))
        left.append(Text(f"{delay}", style=S_YELLOW))

    # Build connection list text
    conn_text = Text()

    for c in conns[:26]:
        meta = c.get("metadata", {})
        cid = c.get("id", "")
        dst = meta.get("host", "") or meta.get("destinationIP", "?")
        port = meta.get("destinationPort", "")
        dl_s, ul_s = speeds.get(cid, (0, 0))
        dl_t = fmt_spd(dl_s) if dl_s > 0 else "-"
        ul_t = fmt_spd(ul_s) if ul_s > 0 else "-"
        sym, clr = rstyle(c.get("rule", ""))

        line = Text()
        line.append(sym + " ", style=clr)
        line.append(f"{(dst+':'+port)[:26].ljust(26)}", style=S_WHITE)
        dl_t_pad = dl_t.rjust(8)
        ul_t_pad = ul_t.rjust(8)
        line.append(dl_t_pad, style=clr)
        line.append(" ")
        line.append(ul_t_pad, style=S_DIM)
        line.append("\n")
        conn_text.append(line)

    # Legend
    conn_text.append(Text(f"\n", style=S_DIM))
    conn_text.append(Text("P=Proxy", style=S_MAGENTA))
    conn_text.append(Text(" D=Direct", style=S_GREEN))
    conn_text.append(Text(" R=Reject", style=S_RED))

    # Bottom bar
    bot = Text()
    bot.append(Text("q quit", style=S_RED))
    if proxies:
        name, (now, delay) = list(proxies.items())[0]
        bot.append(Text(f"  |  {now[:14]}", style=S_WHITE))
    bot.append(Text(f"  |  UP {fmt_spd(us)}", style=S_B_CYAN))
    bot.append(Text(f"  DN {fmt_spd(ds)}", style=S_B_BLUE))

    # Placeholders with explicit text
    hdr = Text()
    hdr.append("T14 ROUTER MONITOR", style=S_BOLD)
    hdr.append(f"    {ts}", style=S_DIM)

    layout.split(
        Layout(Align.center(hdr), name="h", size=1),
        Layout(name="m"),
        Layout(name="b", size=1),
    )
    layout["m"].split_row(
        Layout(left, name="l", ratio=2),
        Layout(conn_text, name="r", ratio=3),
    )
    layout["b"].update(Align.center(bot))

    return layout


# --- Main ---

def run():
    console = Console()
    prev_ul = prev_dl = 0
    prev_ts = time.time()
    prev_state = {}

    with Live(console=console, refresh_per_second=REFRESH_S, screen=True) as live:
        while True:
            now = time.time()
            ts = datetime.now().strftime("%H:%M:%S")
            conns, dl, ul = fetch_conns()
            proxies = fetch_proxies()
            elapsed = max(now - prev_ts, 0.1)
            us = max(0, int((ul - prev_ul) / elapsed))
            ds = max(0, int((dl - prev_dl) / elapsed))
            prev_ul, prev_dl, prev_ts = ul, dl, now

            speeds = {}
            for c in conns:
                cid = c.get("id", "")
                dc, uc = c.get("download", 0), c.get("upload", 0)
                if cid in prev_state:
                    pd, pu = prev_state[cid]
                    speeds[cid] = (max(0, int((dc - pd) / elapsed)), max(0, int((uc - pu) / elapsed)))
                else:
                    speeds[cid] = (0, 0)
                prev_state[cid] = (dc, uc)
            active = {c.get("id", "") for c in conns}
            prev_state = {k: v for k, v in prev_state.items() if k in active}

            sorted_conns = sorted(conns, key=lambda c: speeds.get(c.get("id", ""), (0, 0))[0], reverse=True)[:26]

            layout = build(ts, sorted_conns, speeds, dl, ul, us, ds, proxies)
            live.update(layout)
            time.sleep(REFRESH_S)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
