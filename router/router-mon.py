#!/usr/bin/env python3
"""
T14 Router Monitor — Full-screen 38 rows. ANSI clear + Rich text, no Live.
"""

import json, time, sys, os
from datetime import datetime
from urllib.request import urlopen, Request
from rich.console import Console
from rich.text import Text

API  = "http://127.0.0.1:9097"
KEY  = "20080201"
FPS  = 1
ROWS = 38

B="bold"; D="bright_black"; W="white"
C="cyan"; BC="bold cyan"; BL="blue"; BB="bold blue"
Y="yellow"; R="red"; M="magenta"; G="green"

def api(endpoint):
    try:
        req = Request(f"{API}{endpoint}", headers={"Authorization": f"Bearer {KEY}"})
        with urlopen(req, timeout=3) as r: return json.loads(r.read().decode())
    except: return None

def get_conns():
    d = api("/connections")
    return (d.get("connections",[]), d.get("downloadTotal",0), d.get("uploadTotal",0)) if d else ([],0,0)

def get_proxies():
    d = api("/proxies")
    if not d: return {}
    return {n: (p.get("now","?"), f"{p['history'][-1]['delay']}ms" if p.get("history") else "?")
            for n,p in d.get("proxies",{}).items() if p.get("type")=="Selector"}

def fb(n):
    if not n or n<1024: return f"{n or 0}B"
    n/=1024
    if n<1024: return f"{n:.0f}K"
    n/=1024
    if n<1024: return f"{n:.1f}M"
    return f"{n/1024:.1f}G"

def fs(bps):
    v = max(0, int(bps or 0))
    if v < 1000:    return f"{v:5}B/s"
    v /= 1000
    if v < 1000:    return f"{v:5.0f}K/s"
    v /= 1000
    return          f"{v:5.1f}M/s"

def rs(rule):
    u = (rule or "").upper()
    if "DIRECT" in u: return "D", G
    if "REJECT" in u: return "R", R
    return "P", M

def run():
    console = Console()
    pu=pd=0; pt=time.time(); ps={}

    while True:
        try:
            now = time.time()
            ts = datetime.now().strftime("%H:%M:%S")
            conns, dl, ul = get_conns()
            proxies = get_proxies()
            ela = max(now - pt, 0.1)
            us = max(0, int(((ul or 0) - pu) / ela))
            ds = max(0, int(((dl or 0) - pd) / ela))
            pu, pd, pt = ul or 0, dl or 0, now

            speeds = {}
            for c in conns:
                cid = c.get("id",""); dc, uc = c.get("download",0), c.get("upload",0)
                if cid in ps:
                    od, ou = ps[cid]; speeds[cid] = (max(0,int((dc-od)/ela)), max(0,int((uc-ou)/ela)))
                else: speeds[cid] = (0,0)
                ps[cid] = (dc, uc)
            ps = {k:v for k,v in ps.items() if k in {c.get("id","") for c in conns}}
            sc = sorted(conns, key=lambda c: speeds.get(c.get("id",""),(0,0))[0], reverse=True)

            # --- BUILD output ---
            lines = []
            D60 = "─" * 60

            # 1 header
            lines.append(f"T14  ROUTER  MONITOR                      {ts}")

            # 2 divider
            lines.append(D60)

            # 3-4 speed
            sca = max(us, ds, 1)
            uw = int(min(us/sca*24, 24)); dw = int(min(ds/sca*24, 24))
            lines.append(f"UP  {'#'*uw}{' '*(24-uw)}  {fs(us)}")
            lines.append(f"DN  {'#'*dw}{' '*(24-dw)}  {fs(ds)}")

            # 5 empty
            lines.append("")

            # 6 totals
            lines.append(f"TOTAL  Up:{fb(ul).rjust(8)}  Dn:{fb(dl).rjust(8)}  Conns:{len(sc)}")

            # 7 node
            if proxies:
                pn = list(proxies.items())[0]
                lines.append(f"NODE   {pn[1][0][:26]}  {pn[1][1]}")
            else:
                lines.append("NODE   --")

            # 8 divider
            lines.append(D60)

            # 9 table header
            lines.append(f"CONNECTIONS ({len(sc)})                                  DOWN     UP")

            # 10-33 connections
            shown = sc[:24]
            for c in shown:
                meta = c.get("metadata", {})
                cid = c.get("id","")
                dst = meta.get("host","") or meta.get("destinationIP","?")
                port = meta.get("destinationPort","")
                ds2, us2 = speeds.get(cid, (0,0))
                dl2 = fs(ds2) if ds2>0 else "     -"
                ul2 = fs(us2) if us2>0 else "     -"
                sym, _ = rs(c.get("rule",""))
                lines.append(f" {sym} {(dst+':'+(port or ''))[:30].ljust(30)}  {dl2}  {ul2}")

            # pad to 33 lines (after header=9, base=33)
            while len(lines) < 33:
                lines.append("")

            # 34 legend
            lines.append(" P=Proxy  D=Direct  R=Reject")

            # 35 divider
            lines.append(D60)

            # 36 footer
            nd = pn[1][0][:20] if proxies else "--"
            ft = f"q quit  |  {nd}  |  UP {fs(us)}  DN {fs(ds)}"
            lines.append(ft)

            # 37-38 empty
            lines.append("")
            lines.append("")

            # --- RENDER (ANSI clear + print) ---
            sys.stdout.write("\033[2J\033[H")  # clear screen, cursor home
            for i, line in enumerate(lines[:ROWS]):
                # Apply styling to known keywords
                # Since raw ANSI on TTY may not support Rich markup, use bold escape for title
                if i == 0:
                    sys.stdout.write(f"\033[1m{line}\033[0m\n")
                elif "UP  " in line and i < 5:
                    sys.stdout.write(f"\033[36m{line}\033[0m\n")  # cyan
                elif "DN  " in line and i < 5:
                    sys.stdout.write(f"\033[34m{line}\033[0m\n")  # blue
                elif "TOTAL" in line:
                    sys.stdout.write(f"\033[36m{line}\033[0m\n")  # cyan
                elif "q quit" in line:
                    sys.stdout.write(f"\033[31m{line[:6]}\033[0m{line[6:]}\n")  # red "q quit"
                elif "P=" in line:
                    sys.stdout.write(f"\033[35m{line[:8]}\033[0m\033[32m{line[8:18]}\033[0m\033[31m{line[18:]}\033[0m\n")
                elif line.startswith(" P") or line.startswith(" D") or line.startswith(" R"):
                    # connection lines
                    sym = line[1:2]
                    if sym == "P": clr = "\033[35m"
                    elif sym == "D": clr = "\033[32m"
                    else: clr = "\033[31m"
                    sys.stdout.write(f"{clr}{line[:2]}\033[0m{line[2:]}\n")
                else:
                    sys.stdout.write(f"{line}\n")
            sys.stdout.flush()

            time.sleep(FPS)
        except Exception as e:
            sys.stdout.write(f"\033[2J\033[1;31mERROR: {e}\033[0m\n")
            sys.stdout.flush()
            time.sleep(3)

if __name__ == "__main__":
    try: run()
    except KeyboardInterrupt: sys.exit(0)
