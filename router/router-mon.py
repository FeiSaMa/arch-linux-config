#!/usr/bin/env python3
"""
T14 Router Monitor — 38-row full-screen (ter-228b 60x38)
Manual line control, no Layout, no markup, no gaps.
"""

import json, time, sys
from datetime import datetime
from urllib.request import urlopen, Request
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

API  = "http://127.0.0.1:9097"
KEY  = "20080201"
FPS  = 1
ROWS = 38  # ter-228b on 1080p

# -- ANSI-safe styles --
B="bold"; D="bright_black"; W="white"
C="cyan"; BC="bold cyan"; BL="blue"; BB="bold blue"
Y="yellow"; R="red"; M="magenta"; G="green"

# -- helpers --
def api(endpoint):
    try:
        req = Request(f"{API}{endpoint}", headers={"Authorization": f"Bearer {KEY}"})
        with urlopen(req, timeout=3) as r: return json.loads(r.read().decode())
    except: return None

def get_conns():
    d = api("/connections")
    if not d: return [], 0, 0
    return d.get("connections",[]), d.get("downloadTotal",0), d.get("uploadTotal",0)

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
    if v < 1000:    return f"{v:.0f} B/s"
    v /= 1000
    if v < 1000:    return f"{v:.0f}K/s"
    v /= 1000
    return          f"{v:.1f}M/s"

def rs(rule):
    u = (rule or "").upper()
    if "DIRECT" in u: return "D", G
    if "REJECT" in u: return "R", R
    return "P", M

D60 = Text("─" * 60, style=D)  # divider

# -- line builders --
def H(ts):
    t = Text(); t.append("T14  ROUTER  MONITOR", B); t.append(" " * 22, D); t.append(ts, D)
    return t

def S(us, ds, sc):
    mw = 22; uw = int(min(us/sc*mw, mw)); dw = int(min(ds/sc*mw, mw))
    u = Text(); u.append("UP  ", BC); u.append("#"*uw, C); u.append(" "*(mw-uw) + " ", D)
    u.append(fs(us), BC)
    d = Text(); d.append("DN  ", BB); d.append("#"*dw, BL); d.append(" "*(mw-dw) + " ", D)
    d.append(fs(ds), BB)
    return u, d

def C(c, speeds):
    meta = c.get("metadata", {})
    cid  = c.get("id", "")
    dst  = meta.get("host","") or meta.get("destinationIP","?")
    port = meta.get("destinationPort","")
    ds, us = speeds.get(cid, (0, 0))
    dl = fs(ds) if ds > 0 else "      -"
    ul = fs(us) if us > 0 else "      -"
    sym, clr = rs(c.get("rule",""))
    t = Text()
    t.append(f"{sym} ", clr)
    t.append(f"{(dst + ':' + (port or ''))[:30].ljust(30)}", W)
    t.append(f"  {dl.rjust(7)}", clr)
    t.append(f"  {ul.rjust(7)}", D)
    return t

def build(ts, conns, speeds, dl, ul, us, ds, proxies):
    rows = []
    sc = max(us, ds, 1)

    rows.append(H(ts))                  # 1
    rows.append(D60)                     # 2
    rows.extend(S(us, ds, sc))          # 3-4
    rows.append(Text(""))               # 5

    tot = Text()
    tot.append(f"TOTAL  Up:{fb(ul).rjust(8)}", C)
    tot.append(f"  Dn:{fb(dl).rjust(8)}", BL)
    tot.append(f"  Conns:{len(conns)}", Y)
    rows.append(tot)                    # 6

    if proxies:
        pn = list(proxies.items())[0]
        nd = Text()
        nd.append(f"NODE   {pn[1][0][:26]}", W)
        nd.append(f"  {pn[1][1]}", Y)
        rows.append(nd)                 # 7
    else:
        rows.append(Text("NODE   --", D))

    rows.append(D60)                     # 8

    th = Text()
    th.append(f"CONNECTIONS ({len(conns)})", B)
    th.append(" " * 35, D)
    th.append("  DOWN      UP", D)
    rows.append(th)                     # 9

    shown = conns[:24]
    for c in shown:
        rows.append(C(c, speeds))       # 10-33
    for _ in range(24 - len(shown)):
        rows.append(Text(""))

    lg = Text()
    lg.append(" P=Proxy", M)
    lg.append("  D=Direct", G)
    lg.append("  R=Reject", R)
    rows.append(lg)                      # 34

    rows.append(D60)                     # 35

    ft = Text()
    ft.append("q quit", R)
    if proxies:
        ft.append(f"  |  {pn[1][0][:20]}", W)
    ft.append(f"  |  UP {fs(us)}", BC)
    ft.append(f"  DN {fs(ds)}", BB)
    rows.append(ft)                     # 36

    rows.append(Text(""))               # 37
    rows.append(Text(""))               # 38

    return Group(*rows)

# -- main --
def run():
    console = Console()
    pu = pd = 0; pt = time.time(); ps = {}
    with Live(console=console, refresh_per_second=FPS, screen=True) as live:
        while True:
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
                cid = c.get("id", ""); dc, uc = c.get("download",0), c.get("upload",0)
                if cid in ps:
                    od, ou = ps[cid]; speeds[cid] = (max(0,int((dc-od)/ela)), max(0,int((uc-ou)/ela)))
                else: speeds[cid] = (0, 0)
                ps[cid] = (dc, uc)
            ps = {k:v for k,v in ps.items() if k in {c.get("id","") for c in conns}}
            sc = sorted(conns, key=lambda c: speeds.get(c.get("id",""),(0,0))[0], reverse=True)
            live.update(build(ts, sc, speeds, dl, ul, us, ds, proxies))
            time.sleep(FPS)

if __name__ == "__main__":
    try: run()
    except KeyboardInterrupt: sys.exit(0)
