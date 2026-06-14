#!/usr/bin/env python3
"""T14 Router Monitor — curses full-screen TUI, 120x33 grid."""

import curses
import json
import time
import subprocess
from datetime import datetime
from urllib.request import urlopen, Request

API="http://127.0.0.1:9097"; KEY="20080201"; FPS=1

def api(endpoint):
    try:
        req=Request(f"{API}{endpoint}",headers={"Authorization":f"Bearer {KEY}"})
        with urlopen(req,timeout=2) as r: return json.loads(r.read().decode())
    except: return None

def get_conns():
    d=api("/connections")
    if not d: return [],0,0
    return d.get("connections",[]), d.get("downloadTotal",0), d.get("uploadTotal",0)

def get_proxies():
    d=api("/proxies")
    if not d: return {}
    return {n:(p.get("now","?"),f"{p['history'][-1]['delay']}ms" if p.get("history") else "?")
            for n,p in d.get("proxies",{}).items() if p.get("type")=="Selector"}

def fb(n):
    if not n or n<1024: return f"{n or 0}B"
    n/=1024
    if n<1024: return f"{n:.0f}K"; n/=1024
    if n<1024: return f"{n:.1f}M"
    return f"{n/1024:.1f}G"

def fs(bps):
    try: v=max(0,int(bps or 0))
    except: return "err"
    if v<1000: return f"{v:4}B/s"
    v/=1000
    if v<1000: return f"{v:4.0f}K/s"
    v/=1000
    return f"{v:4.1f}M/s"

def rs(rule):
    u=(rule or "").upper()
    if "DIRECT" in u: return "D", 2  # green
    if "REJECT" in u: return "R", 1  # red
    return "P", 5  # magenta

def run(stdscr):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)

    pu=pd=0; pt=time.time(); ps={}
    fp=curses.A_BOLD

    while True:
        try:
            now=time.time(); ts=datetime.now().strftime("%H:%M:%S")
            conns,dl,ul=get_conns()
            proxies=get_proxies()
            ela=max(now-pt,0.1)
            us=max(0,int(((ul or 0)-pu)/ela))
            ds=max(0,int(((dl or 0)-pd)/ela))
            pu,pd,pt=ul or 0,dl or 0,now

            speeds={}
            for c in conns:
                cid=c.get("id",""); dc,uc=c.get("download",0),c.get("upload",0)
                if cid in ps: od,ou=ps[cid]; speeds[cid]=(max(0,int((dc-od)/ela)),max(0,int((uc-ou)/ela)))
                else: speeds[cid]=(0,0)
                ps[cid]=(dc,uc)
            ps={k:v for k,v in ps.items() if k in {c.get("id","") for c in conns}}
            sc=sorted(conns,key=lambda c: speeds.get(c.get("id",""),(0,0))[0],reverse=True)

            # fastfetch (with native Arch logo)
            try:
                raw=subprocess.run(["fastfetch","--pipe"],
                    capture_output=True,text=True,timeout=2).stdout
                ff_lines=raw.split("\n")
            except: ff_lines=[]

            # get terminal size dynamically
            H,W=stdscr.getmaxyx()
            MW=W//2  # mid split

            # Top bar
            stdscr.addstr(0,0," T14 ROUTER MONITOR",curses.A_BOLD)
            stdscr.addstr(0,MW," Arch Linux",curses.A_BOLD)
            stdscr.addstr(0,W-9,ts)

            # Column dividers
            for y in range(H):
                try: stdscr.addch(y,MW-1,curses.ACS_VLINE)
                except: pass

            # Divider line
            stdscr.hline(1,0,curses.ACS_HLINE,W)
            stdscr.addch(1,MW-1,curses.ACS_PLUS)

            row=2

            # LEFT PANEL
            # Speed
            sca=max(us,ds,1); uw=int(min(us/sca*18,18)); dw=int(min(ds/sca*18,18))
            stdscr.addstr(row,1,f"UP  {'#'*uw}{' '*(18-uw)} {fs(us).rjust(10)}",curses.color_pair(6)|fp)
            row+=1
            stdscr.addstr(row,1,f"DN  {'#'*dw}{' '*(18-dw)} {fs(ds).rjust(10)}",curses.color_pair(4)|fp)
            row+=2

            stdscr.addstr(row,1,f"Up:{fb(ul)} Dn:{fb(dl)} Conns:{len(sc)}")
            row+=1
            pn=list(proxies.items()) if proxies else []
            nd=f"{pn[0][1][0][:14]} {pn[0][1][1]}" if pn else "--"
            stdscr.addstr(row,1,f"Node {nd}")
            row+=1

            stdscr.hline(row,0,curses.ACS_HLINE,MW-1)
            stdscr.addch(row,MW-1,curses.ACS_PLUS)
            row+=1

            stdscr.addstr(row,1,f"CONNS ({len(sc)})",fp)
            row+=1
            for c in sc[:18]:
                meta=c.get("metadata",{}); cid=c.get("id","")
                dst=meta.get("host","") or meta.get("destinationIP","?")
                port=meta.get("destinationPort","")
                ds2,us2=speeds.get(cid,(0,0))
                dl2=fs(ds2) if ds2>0 else "    -"; ul2=fs(us2) if us2>0 else "    -"
                sym,clr_pair=rs(c.get("rule",""))
                if row>=H-1: break
                stdscr.addstr(row,1,f" {sym} ",curses.color_pair(clr_pair)|fp)
                stdscr.addstr(row,3,f"{(dst+':'+(port or ''))[:22].ljust(22)} {dl2} {ul2}")
                row+=1
            # legend
            if row<H-3:
                row+=1
                stdscr.addstr(row,1,"P=Proxy",curses.color_pair(5))
                stdscr.addstr(row,10,"D=Direct",curses.color_pair(2))
                stdscr.addstr(row,20,"R=Reject",curses.color_pair(1))

            # RIGHT PANEL — fastfetch (native logo included)
            rr=2
            shown=0
            for line in ff_lines:
                ls=line.strip()
                if not ls: continue
                if "feisama@router" in ls: continue
                if ls.replace("-","")=="": continue
                if "Locale: C" in ls: continue
                if "\033[4" in line or "\033[10" in line: continue
                if shown>=24: break
                if rr>=H-3: break
                stdscr.addstr(rr, MW+1, line[:MW-2])
                rr+=1; shown+=1

            # Bottom bar
            stdscr.hline(H-2,0,curses.ACS_HLINE,W)
            stdscr.addch(H-2,MW-1,curses.ACS_PLUS)
            nd2=pn[0][1][0][:14] if pn else "--"
            stdscr.addstr(H-1,1,f"q quit | {nd2} | UP {fs(us)} DN {fs(ds)}",fp)

            stdscr.refresh()
            time.sleep(FPS)

        except KeyboardInterrupt: break
        except Exception as e:
            stdscr.addstr(H-1,1,f"ERROR: {e}"[:W-2],curses.color_pair(1))
            stdscr.refresh()
            time.sleep(2)

if __name__=="__main__":
    curses.wrapper(run)
