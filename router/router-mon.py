#!/usr/bin/env python3
"""T14 Router Monitor — split-screen (left=traffic, right=fastfetch). 120x33, ANSI."""

import json, time, sys, subprocess
from datetime import datetime
from urllib.request import urlopen, Request

API="http://127.0.0.1:9097"; KEY="20080201"; FPS=1; ROWS=33; W=60

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
    if v<1000: return f"{v:4}B/s"; v/=1000
    if v<1000: return f"{v:4.0f}K/s"; v/=1000; return f"{v:4.1f}M/s"

def rs(rule):
    u=(rule or "").upper()
    if "DIRECT" in u: return "D","\033[32m"
    if "REJECT" in u: return "R","\033[31m"
    return "P","\033[35m"

def pad(s,n): return (s or "")[:n].ljust(n)

def run():
    pu=pd=0; pt=time.time(); ps={}; ff_lines=[""]*ROWS
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

            # fastfetch
            try:
                raw=subprocess.run(["fastfetch","--logo","none","--pipe"],
                    capture_output=True,text=True,timeout=2).stdout
                ff_lines=raw.strip().split("\n")
            except: pass

            # BUILD LEFT
            L=[]
            L.append(f"\033[1m{pad('T14 ROUTER',W)}\033[0m")
            L.append(pad("-"*W,W))
            sca=max(us,ds,1); uw=int(min(us/sca*24,24)); dw=int(min(ds/sca*24,24))
            L.append(f"\033[36mUP  {'#'*uw}{' '*(24-uw)}  {fs(us)}\033[0m")
            L.append(f"\033[34mDN  {'#'*dw}{' '*(24-dw)}  {fs(ds)}\033[0m")
            L.append(pad("",W))
            L.append(pad(f"Up:{fb(ul)} Dn:{fb(dl)} Conns:{len(sc)}",W))
            pn=list(proxies.items()) if proxies else []
            nd=f"{pn[0][1][0][:14]} {pn[0][1][1]}" if pn else "--"
            L.append(pad(f"Node {nd}",W))
            L.append(pad("-"*W,W))
            L.append(pad(f"CONNS ({len(sc)})",W))
            for c in sc[:18]:
                meta=c.get("metadata",{}); cid=c.get("id","")
                dst=meta.get("host","") or meta.get("destinationIP","?")
                port=meta.get("destinationPort","")
                ds2,us2=speeds.get(cid,(0,0))
                dl2=fs(ds2) if ds2>0 else "    -"; ul2=fs(us2) if us2>0 else "    -"
                sym,clr=rs(c.get("rule",""))
                L.append(f" {clr}{sym}\033[0m {pad((dst+':'+(port or ''))[:20],20)} {dl2} {ul2}")
            for _ in range(18-len(sc[:18])): L.append(pad("",W))
            L.append(pad("\033[35mP=Proxy\033[0m \033[32mD=Direct\033[0m \033[31mR=Reject\033[0m",W))
            L.append(pad("-"*W,W))
            nd2=pn[0][1][0][:14] if pn else "--"
            L.append(pad(f"\033[31mq\033[0m quit | {nd2}",W))

            # BUILD RIGHT
            R=[]
            R.append(f"\033[1m{pad('SYSTEM',W)}\033[0m")
            R.append(pad("-"*W,W))
            shown=0
            for line in ff_lines:
                ls=line.strip()
                if not ls: continue
                if "feisama@router" in ls: continue
                if ls.replace("-","")=="": continue
                if "Terminal: sshd" in ls or "Terminal: timeout" in ls: continue
                if "Locale: C" in ls: continue
                if "\033[4" in ls or "\033[10" in ls: continue
                if shown>=24: break
                R.append(pad(line[:W],W)); shown+=1
            for _ in range(24-shown): R.append(pad("",W))
            R.append(pad("-"*W,W))
            R.append(pad(f"UP {fs(us)} DN {fs(ds)}",W))

            # --- RENDER (scroll margin - fixed status bar) ---
            out = "\033[2J\033[1;32r\033[1;1H"
            for i in range(ROWS - 1):
                lp = L[i] if i < len(L) else " "*W
                rp = R[i] if i < len(R) else " "*W
                out += f"{pad(lp,W)}{pad(rp,W)}\n"
            # fixed last row
            i = ROWS - 1
            lp = L[i] if i < len(L) else " "*W
            rp = R[i] if i < len(R) else " "*W
            out += f"\033[33;1H{pad(lp,W)}{pad(rp,W)}"
            sys.stdout.write(out)
            sys.stdout.flush()

            time.sleep(FPS)
        except Exception as e:
            sys.stdout.write(f"\033[r\033[2J\033[HERROR: {e}\n")
            sys.stdout.flush(); time.sleep(3)

if __name__=="__main__":
    try: run()
    except KeyboardInterrupt:
        sys.stdout.write("\033[r")  # reset scroll margins
        sys.exit(0)
