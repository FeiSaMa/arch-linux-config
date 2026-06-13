#!/usr/bin/env python3
import yaml, json, os, sys, time

CFG = os.path.expanduser("~/.local/share/io.github.clash-verge-rev.clash-verge-rev")
SUB = f"{CFG}/profiles/RyF8MaZr707Q.yaml"
OUT = f"{CFG}/clash-verge.yaml"

with open(f"{CFG}/config.yaml") as f:
    base = f.read()

with open(SUB) as f:
    data = yaml.safe_load(f)

proxies = [p for p in data.get("proxies", []) if isinstance(p, dict) and "name" in p]
groups = [g for g in data.get("proxy-groups", []) if isinstance(g, dict)]

with open(OUT, "w") as f:
    f.write(base)
    f.write("\nproxies:\n")
    for p in proxies:
        items = ",".join(f"{k}: {json.dumps(v) if isinstance(v, str) else v}" for k, v in p.items() if v is not None)
        f.write(f"  - {{{items}}}\n")

    names = [json.dumps(p["name"]) for p in proxies if "name" in p]
    f.write("\nproxy-groups:\n")
    if names:
        f.write(f'  - {{name: "PROXY", type: select, proxies: [{",".join(names[:10])}]}}\n')
    f.write("\nrules:\n")
    f.write("  - MATCH,PROXY\n")

print(f"OK: {len(proxies)} proxies")
