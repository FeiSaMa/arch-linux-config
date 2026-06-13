#!/usr/bin/env bash
set -uo pipefail

nmcli device disconnect wlp0s20f3 2>/dev/null || true

ip link set wlp0s20f3 down 2>/dev/null || true
sleep 1
ip link set wlp0s20f3 up 2>/dev/null || true
sleep 2

ip addr add 192.168.2.1/24 dev wlp0s20f3 2>/dev/null || true

pkill -f dnsmasq 2>/dev/null || true
sleep 1
nohup dnsmasq --port=5353 --interface=wlp0s20f3 --bind-interfaces \
  --dhcp-range=192.168.2.10,192.168.2.200,255.255.255.0,24h \
  --dhcp-option=3,192.168.2.1 --dhcp-option=6,192.168.2.1 \
  --no-resolv --server=8.8.8.8 --server=223.5.5.5 > /dev/null 2>&1 &

systemctl start hostapd

iptables-restore < /etc/iptables/iptables.rules 2>/dev/null || true

sleep 3
SECRET=$(grep "^secret:" /home/feisama/.local/share/io.github.clash-verge-rev.clash-verge-rev/config.yaml | awk "{print \$2}")
curl -s -X PUT http://127.0.0.1:9097/configs -H "Authorization: Bearer $SECRET" -H "Content-Type: application/json" -d "{}" > /dev/null 2>&1 || true
