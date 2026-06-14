#!/usr/bin/env python3
"""
T14 Router Monitor — Full-screen Live Connection Dashboard
Runs on Linux console TTY (16-color mode), uses Mihomo REST API.
"""

import json
import time
import os
import sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

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

# -- Catppuccin-inspired ANSI color mapping for 16-color TTY --
# Rich on TERM=linux approximates these to nearest 16 ANSI colors
C = {
    "bg":      "black",
    "fg":      "white",
    "dim":     "bright_black",
    "cyan":    "cyan",
    "green":   "green",
    "yellow":  "yellow",
    "red":     "red",
    "magenta": "magenta",
    "blue":    "blue",
    "white":   "white",
    "border":  "bright_black",
}

# --- API helpers ---

def fetch_json(endpoint):
    """GET an endpoint, return parsed JSON or None on failure."""
    url = f"{API_BASE}{endpoint}"
    req = Request(url, headers={"Authorization": f"Bearer {SECRET}"})
    try:
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def fetch_conns():
    """Return list of active connections."""
    data = fetch_json("/connections")
    if not data:
        return [], 0, 0
    return data.get("connections", []), \
           data.get("downloadTotal", 0), \
           data.get("uploadTotal", 0)


def fetch_proxies():
    """Return proxy-group summary dict {name: type+now/avail}."""
    data = fetch_json("/proxies")
    if not data:
        return {}
    info = {}
    proxies = data.get("proxies", {})
    for name, p in proxies.items():
        if p.get("type") == "Selector":
            now = p.get("now", "?")
            info[name] = now
    return info


def fmt_bytes(n):
    """Human-readable bytes."""
    if n < 1024:
        return f"{n} B"
    for unit in ("KB", "MB", "GB"):
        n /= 1024
        if n < 1024:
            return f"{n:.1f} {unit}"
    return f"{n:.1f} TB"


def fmt_speed(bps):
    """Human-readable speed."""
    if bps < 1000:
        return f"{bps:.0f} B/s"
    bps /= 1000
    if bps < 1000:
        return f"{bps:.1f} K/s"
    bps /= 1000
    return f"{bps:.1f} M/s"


def rule_label(rule, rule_payload):
    """Return a short human-readable label for the rule."""
    if rule == "MATCH":
        return "GLOBAL"
    if rule_payload:
        return rule_payload[:18]
    return rule[:18]


def rule_style(rule):
    """Return (symbol, color_key) for a rule."""
    if "DIRECT" in (rule or "").upper():
        return ("D", C["green"])
    if "REJECT" in (rule or "").upper():
        return ("R", C["red"])
    return ("P", C["magenta"])


# --- ASCII sparkline ---

BLOCKS = " ▁▂▃▄▅▆▇█"


def sparkline(data, width=50):
    """Draw a tiny sparkline bar using Unicode block chars."""
    if not data or max(data) == 0:
        return BLOCKS[0] * width
    # resample to `width` buckets
    n = len(data)
    if n == 0:
        return BLOCKS[0] * width
    step = max(1, n / width)
    out = ""
    max_val = max(data) or 1
    for i in range(width):
        idx = int(i * step)
        if idx >= n:
            out += " "
            continue
        val = data[idx] / max_val
        out += BLOCKS[min(int(val * 8), 8)]
    return out


# --- Layout builders ---

HEADER = r"""
[bold white]▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖[/][bold bright_cyan]  T14  ROUTER  MONITOR  [/][bold white]▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖[/]
"""


def build_layout(title_time, conns_data, speed, proxies):
    """Build the full-screen Rich Layout."""
    conns, dl_total, ul_total = conns_data

    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="stats", ratio=2),
        Layout(name="conn_panel", ratio=3),
    )
    layout["stats"].split(
        Layout(name="speed_panel"),
        Layout(name="traffic_panel"),
        Layout(name="nodes_panel"),
    )

    # -- header --
    layout["header"].update(Panel(
        Align.center(Text(HEADER + title_time, justify="center")),
        style=C["border"], box=box.HEAVY,
        padding=(0, 2),
    ))

    # -- speed panel --
    up_speed, dn_speed = speed
    bar_up = "█" * int(min(up_speed / (2_000_000) * 20, 20)) if up_speed else ""
    bar_dn = "█" * int(min(dn_speed / (2_000_000) * 20, 20)) if dn_speed else ""
    speed_text = Text()
    speed_text.append("UP\n", style=C["dim"])
    speed_text.append(f"[{C['cyan']}]{bar_up}[/] [bold {C['cyan']}]{fmt_speed(up_speed)}[/]\n\n")
    speed_text.append("DOWN\n", style=C["dim"])
    speed_text.append(f"[{C['blue']}]{bar_dn}[/] [bold {C['blue']}]{fmt_speed(dn_speed)}[/]")
    layout["speed_panel"].update(Panel(
        speed_text,
        title="[bold]THROUGHPUT[/]",
        border_style=C["border"], box=box.ROUNDED,
    ))

    # -- traffic panel --
    traffic_text = Text()
    traffic_text.append(f"[{C['white']}]Total Upload:[/]   [{C['cyan']}]{fmt_bytes(ul_total)}[/]\n")
    traffic_text.append(f"[{C['white']}]Total Download:[/] [{C['blue']}]{fmt_bytes(dl_total)}[/]\n")
    traffic_text.append(f"[{C['white']}]Active Conns:[/]   [{C['yellow']}]{len(conns)}[/]")
    layout["traffic_panel"].update(Panel(
        traffic_text,
        title="[bold]TOTALS[/]",
        border_style=C["border"], box=box.ROUNDED,
    ))

    # -- nodes panel --
    nodes_text = Text()
    if proxies:
        for name, now in list(proxies.items())[:8]:
            short = name[:16]
            nodes_text.append(f"[{C['dim']}]{short}[/] → [bold {C['white']}]{now}[/]\n")
    else:
        nodes_text.append("[bright_black]No data[/]")
    layout["nodes_panel"].update(Panel(
        nodes_text,
        title="[bold]PROXY NODES[/]",
        border_style=C["border"], box=box.ROUNDED,
    ))

    # -- connections table --
    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style=C["border"],
        show_header=True,
        header_style=f"bold {C['dim']}",
        expand=True,
    )
    table.add_column("SRC", width=15, no_wrap=True)
    table.add_column("DESTINATION", width=30)
    table.add_column("RULE", width=16)
    table.add_column("TRAFFIC", width=10, justify="right")
    table.add_column("", width=2)  # tiny spacer

    for c in conns:
        meta = c.get("metadata", {})
        src = meta.get("sourceIP", "?")
        dst = meta.get("host", "") or meta.get("destinationIP", "?")
        port = meta.get("destinationPort", "")
        dst_full = f"{dst}:{port}" if port else dst
        rule = rule_label(c.get("rule", ""), c.get("rulePayload", ""))
        sym, style_k = rule_style(c.get("rule", ""))
        traffic = fmt_bytes(c.get("download", 0))

        table.add_row(
            src[:14],
            dst_full[:28],
            f"[{style_k}]{rule}[/]",
            f"[{style_k}]{traffic}[/]",
            f"[{style_k}]{sym}[/]",
        )

    layout["conn_panel"].update(Panel(
        table,
        title=f"[bold]CONNECTIONS[/] ([{C['yellow']}]{len(conns)}[/])",
        border_style=C["border"], box=box.ROUNDED,
    ))

    # -- footer --
    footer_text = Text()
    footer_text.append(f" [{C['red']}]q[/] quit")
    footer_text.append(f"  [{C['green']}]↑[/]{fmt_speed(up_speed)}")
    footer_text.append(f"  [{C['blue']}]↓[/]{fmt_speed(dn_speed)}")
    footer_text.append(f"  [dim]conns: {len(conns)}[/]")
    layout["footer"].update(Panel(
        footer_text,
        style=C["border"], box=box.HEAVY,
    ))

    return layout


# --- Main loop ---

class Monitor:
    def __init__(self):
        self.console = Console()
        self.prev_ul = 0
        self.prev_dl = 0
        self.prev_ts = time.time()
        self.history = {"up": [0]*60, "down": [0]*60}

    def run(self):
        with Live(
            console=self.console,
            refresh_per_second=REFRESH_S,
            screen=True,
        ) as live:
            while True:
                now = time.time()
                title_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conns_data = fetch_conns()
                conns, dl_total, ul_total = conns_data
                proxies = fetch_proxies()

                # Compute speed
                elapsed = max(now - self.prev_ts, 0.1)
                up_speed = max(0, int((ul_total - self.prev_ul) / elapsed))
                dn_speed = max(0, int((dl_total - self.prev_dl) / elapsed))
                self.prev_ul = ul_total
                self.prev_dl = dl_total
                self.prev_ts = now

                # Update sparkline history
                self.history["up"].pop(0)
                self.history["up"].append(up_speed)
                self.history["down"].pop(0)
                self.history["down"].append(dn_speed)

                # Sort connections by download (desc), top 20
                conns_sorted = sorted(
                    conns,
                    key=lambda c: c.get("download", 0),
                    reverse=True,
                )[:25]

                layout = build_layout(
                    title_time,
                    (conns_sorted, dl_total, ul_total),
                    (up_speed, dn_speed),
                    proxies,
                )

                live.update(layout)
                time.sleep(REFRESH_S)


if __name__ == "__main__":
    try:
        Monitor().run()
    except KeyboardInterrupt:
        sys.exit(0)
