#!/usr/bin/env python3
"""
T14 Router Monitor — Split-screen: left=monitor, right=fastfetch.
60 cols (ter-228b), raw ANSI, 38 rows full.
"""

import json, time, sys, subprocess
from datetime import datetime
from urllib.request import urlopen, Request

API="http://127.0.0.1:9097"; KEY="20080201"; FPS=1; ROWS=38; W=30  # half width

def api(endpoint):
    try:
        req=Request(f"{API}{endpoint}",headers={"Authorization":f"Bearer {KEY}"})
        with urlopen(req,timeout=3) as r: return json.loads(r.read().decode())
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
    except: return " err"
    if v<1000: return f"{v:4}B/s"
    v/=1000
    if v<1000: return f"{v:4.0f}K/s"
    v/=1000
    return f"{v:4.1f}M/s"

def rs(rule):
    u=(rule or "").upper()
    if "DIRECT" in u: return "D","\033[32m"  # green
    if "REJECT" in u: return "R","\033[31m"  # red
    return "P","\033[35m"  # magenta

def pad(s,n): return (s or "")[:n].ljust(n)

def run():
    pu=pd=0; pt=time.time(); ps={}; ff_lines=[""]*ROWS
    last_ff=0

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

            # --- fastfetch (only on first run or every N refreshes) ---
            try:
                raw=subprocess.run(["fastfetch","--logo","none","--pipe"],
                    capture_output=True,text=True,timeout=2).stdout
                ff_lines=raw.strip().split("\n")
            except: pass

            # --- BUILD LEFT PANEL ---
            L=[]
            L.append(f"\033[1m{pad('T14 ROUTER',W)}\033[0m")                     # 1
            L.append(pad("─"*W,W))                                             # 2
            sca=max(us,ds,1); uw=int(min(us/sca*12,12)); dw=int(min(ds/sca*12,12))
            L.append(f"\033[36mUP  {'#'*uw}{' '*(12-uw)}  {fs(us)}\033[0m")  # 3
            L.append(f"\033[34mDN  {'#'*dw}{' '*(12-dw)}  {fs(ds)}\033[0m")  # 4
            L.append(pad("",W))                                                 # 5
            L.append(pad(f"Up:{fb(ul)} Dn:{fb(dl)} Conns:{len(sc)}",W))        # 6
            pn=list(proxies.items()) if proxies else []
            nd=f"{pn[0][1][0][:14]} {pn[0][1][1]}" if pn else "--"
            L.append(pad(f"Node {nd}",W))                                       # 7
            L.append(pad("─"*W,W))                                             # 8
            L.append(pad(f"CONNS ({len(sc)})",W))                               # 9
            for c in sc[:10]:
                meta=c.get("metadata",{})
                cid=c.get("id",""); dst=meta.get("host","") or meta.get("destinationIP","?")
                port=meta.get("destinationPort","")
                ds2,us2=speeds.get(cid,(0,0))
                dl2=fs(ds2) if ds2>0 else "    -"; ul2=fs(us2) if us2>0 else "    -"
                sym,clr=rs(c.get("rule",""))
                L.append(f" {clr}{sym}\033[0m {pad((dst+':'+(port or ''))[:20],20)} {dl2} {ul2}")
            for _ in range(10-len(sc[:10])): L.append(pad("",W))               # pad
            L.append(pad("\033[35mP=Proxy\033[0m \033[32mD=Direct\033[0m \033[31mR=Reject\033[0m",W))  # 20
            L.append(pad("─"*W,W))                                             # 21
            nd2=pn[0][1][0][:14] if pn else "--"
            L.append(pad(f"\033[31mq\033[0m quit | {nd2}",W))                  # 22

            # --- BUILD RIGHT PANEL from fastfetch ---
            R=[]
            R.append(f"\033[1m{pad('SYSTEM',W)}\033[0m")                          # 1
            R.append(pad("─"*W,W))                                              # 2

            # Show relevant fastfetch lines
            skip=0; shown=0; skip_lines={"feisama@router","-----"}
            for line in ff_lines:
                line_s = line.strip()
                # skip header lines, color palette, locale
                if not line_s: continue
                if "feisama@router" in line_s: continue
                if line_s.replace("-","") == "": continue
                if "Terminal: sshd" in line_s or "Terminal: timeout" in line_s: continue
                if "Locale: C" in line_s: continue
                if "\033[4" in line_s or "\033[10" in line_s: continue  # color blocks
                if shown >= 18: break
                R.append(pad(line[:W],W))
                shown+=1
            for _ in range(18-shown): R.append(pad("",W))                       # pad

            R.append(pad("─"*W,W))                                             # 22
            R.append(pad(f"UP {fs(us)} DN {fs(ds)}",W))                       # 23

            # --- RENDER ---
            sys.stdout.write("\033[2J\033[H")
            for i in range(min(len(L),len(R),ROWS)):
                lp=L[i] if i<len(L) else " "*W
                rp=R[i] if i<len(R) else " "*W
                sys.stdout.write(f"{pad(lp,W)} {pad(rp,W)}\n")
            # fill remaining rows
            for i in range(max(len(L),len(R)), ROWS):
                sys.stdout.write(" "*(2*W+1)+"\n")
            sys.stdout.flush()
            time.sleep(FPS)

        except Exception as e:
            sys.stdout.write(f"\033[2J\033[H\033[1;31mERROR: {e}\033[0m\n")
            sys.stdout.flush(); time.sleep(3)

if __name__=="__main__":
    try: run()
    except KeyboardInterrupt: sys.exit(0)
