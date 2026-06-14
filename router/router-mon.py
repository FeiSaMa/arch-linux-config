#!/usr/bin/env python3
"""
T14 Router Monitor — Full-screen Dashboard for Linux console TTY
Uses Mihomo REST API. Explicit styles (no inline markup).
"""

import json
import time
import sys
from datetime import datetime
from urllib.request import urlopen, Request

from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

API_BASE = "http://127.0.0.1:9097"
SECRET = "20080201"
REFRESH_S = 1

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
    if n < 1024:
        return f"{n}B"
    for unit in ("K", "M", "G"):
        n /= 1024
        if n < 1024:
            return f"{n:.0f}{unit}"
    return f"{n:.0f}G"

def fmt_spd(bps):
    if bps < 1000:
        return f"{bps:.0f}B/s"
    bps /= 1000
    if bps < 1000:
        return f"{bps:.0f}K/s"
    bps /= 1000
    return f"{bps:.1f}M/s"

def rstyle(rule):
    u = (rule or "").upper()
    if "DIRECT" in u:
        return ("D", "green", "green")
    if "REJECT" in u:
        return ("R", "red", "red")
    return ("P", "magenta", "magenta")

# --- Build display ---

S_BOLD_CYAN = "bold cyan"
S_BOLD_BLUE = "bold blue"
S_CYAN = "cyan"
S_BLUE = "blue"
S_DIM = "bright_black"
S_BOLD = "bold"
S_WHITE = "white"
S_YELLOW = "yellow"
S_RED = "red"
S_MAGENTA = "magenta"

def build(time_str, conns_sorted, conn_speeds, dl_total, ul_total, up_spd, dn_spd, proxies):
    rows = []

    # --- HEADER ---
    header = Text()
    header.append("T14 ROUTER MONITOR", style="bold")
    header.append(f"  {time_str}", style=S_DIM)
    rows.append(Align.center(header))

    # --- DIVIDER ---
    rows.append(Text("─" * 60, style=S_DIM))

    # --- SPEED SECTION ---
    scale = max(up_spd, dn_spd, 1)
    up_w = int(min(up_spd / scale * 22, 22))
    dn_w = int(min(dn_spd / scale * 22, 22))

    # UP row
    up_line = Text()
    up_line.append("UP  ", style=S_BOLD_CYAN)
    up_line.append("#" * up_w, style=S_CYAN)
    up_line.append(" " * (22 - up_w))
    up_line.append(fmt_spd(up_spd).rjust(10), style=S_BOLD_CYAN)
    rows.append(up_line)

    # DOWN row
    dn_line = Text()
    dn_line.append("DN  ", style=S_BOLD_BLUE)
    dn_line.append("#" * dn_w, style=S_BLUE)
    dn_line.append(" " * (22 - dn_w))
    dn_line.append(fmt_spd(dn_spd).rjust(10), style=S_BOLD_BLUE)
    rows.append(dn_line)

    # TOTAL row
    total_line = Text()
    total_line.append(f"Total  Up:{fmt_bytes(ul_total).rjust(8)}", style=S_WHITE)
    total_line.append(f"  Dn:{fmt_bytes(dl_total).rjust(8)}", style=S_WHITE)
    total_line.append(f"  Conns:{len(conns_sorted)}", style=S_YELLOW)
    rows.append(total_line)

    # NODE row
    if proxies:
        first = list(proxies.items())[0]
        name, (now, delay) = first
        node_line = Text()
        node_line.append(f"Node  {now[:18]}", style=S_BOLD)
        node_line.append(f"  {delay}", style=S_YELLOW)
        rows.append(node_line)

    rows.append(Text("─" * 60, style=S_DIM))

    # --- CONNECTIONS TABLE ---
    c_header = Text()
    c_header.append("CONNECTIONS", style="bold")
    c_header.append(f" ({len(conns_sorted)})", style=S_YELLOW)
    c_header.append("                               ▲down ▼up", style=S_DIM)
    rows.append(c_header)

    for c in conns_sorted[:20]:
        meta = c.get("metadata", {})
        cid = c.get("id", "")
        dst = meta.get("host", "") or meta.get("destinationIP", "?")
        port = meta.get("destinationPort", "")
        dst_full = f"{dst}:{port}" if port else dst
        sym, clr_fg, clr = rstyle(c.get("rule", ""))
        dl_speed, ul_speed = conn_speeds.get(cid, (0, 0))
        dl_txt = fmt_spd(dl_speed) if dl_speed > 0 else " -"
        ul_txt = fmt_spd(ul_speed) if ul_speed > 0 else " -"

        c_line = Text()
        c_line.append(" ", style=clr_fg)
        c_line.append(sym, style=clr_fg)
        c_line.append(f" {dst_full[:28].ljust(28)}", style=S_WHITE)
        c_line.append(f"{dl_txt.rjust(8)}", style=clr_fg)
        c_line.append(f" {ul_txt.rjust(8)}", style=S_DIM)
        rows.append(c_line)

    # Legend
    legend = Text()
    legend.append(" P=Proxy ", style=S_MAGENTA)
    legend.append(" D=Direct ", style="green")
    legend.append(" R=Reject", style=S_RED)
    rows.append(legend)

    rows.append(Text("─" * 60, style=S_DIM))

    # --- FOOTER ---
    footer = Text()
    footer.append("q quit", style=S_RED)
    footer.append(f"  │  {len(proxies)} nodes", style=S_WHITE)
    footer.append(f"  │  ", style=S_DIM)
    footer.append(f"UP {fmt_spd(up_spd)}", style=S_BOLD_CYAN)
    footer.append(f"  DN {fmt_spd(dn_spd)}", style=S_BOLD_BLUE)
    rows.append(footer)

    return Group(*rows)


# --- MAIN ---

def run():
    console = Console()
    prev_ul = prev_dl = 0
    prev_ts = time.time()
    prev_conn_state = {}

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

            # per-connection speeds
            conn_speeds = {}
            for c in conns:
                cid = c.get("id", "")
                dl_cur = c.get("download", 0)
                ul_cur = c.get("upload", 0)
                if cid in prev_conn_state:
                    pd, pu = prev_conn_state[cid]
                    conn_speeds[cid] = (
                        max(0, int((dl_cur - pd) / elapsed)),
                        max(0, int((ul_cur - pu) / elapsed)),
                    )
                else:
                    conn_speeds[cid] = (0, 0)
                prev_conn_state[cid] = (dl_cur, ul_cur)
            active_ids = {c.get("id", "") for c in conns}
            prev_conn_state = {k: v for k, v in prev_conn_state.items() if k in active_ids}

            sorted_conns = sorted(
                conns,
                key=lambda c: conn_speeds.get(c.get("id", ""), (0, 0))[0],
                reverse=True,
            )[:20]

            group = build(ts, sorted_conns, conn_speeds, dl, ul, up_spd, dn_spd, proxies)
            live.update(group)
            time.sleep(REFRESH_S)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
