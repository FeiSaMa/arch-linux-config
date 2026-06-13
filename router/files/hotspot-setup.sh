#!/usr/bin/env bash
set -uo pipefail

# 断开 WiFi 客户端连接
nmcli device disconnect wlp0s20f3 2>/dev/null || true
sleep 2

# 彻底重置接口
ip link set wlp0s20f3 down
sleep 1
ip link set wlp0s20f3 up
sleep 2

# 配热点 IP
ip addr flush dev wlp0s20f3 2>/dev/null || true
ip addr add 192.168.2.1/24 dev wlp0s20f3
sleep 1

# 启动 dnsmasq（先杀旧进程）
pkill -f dnsmasq 2>/dev/null || true
sleep 1
nohup dnsmasq --port=5353 --interface=wlp0s20f3 --bind-interfaces   --dhcp-range=192.168.2.10,192.168.2.200,255.255.255.0,24h   --dhcp-option=3,192.168.2.1 --dhcp-option=6,192.168.2.1   --no-resolv --server=8.8.8.8 --server=223.5.5.5 > /dev/null 2>&1 \&

# 启动热点
systemctl restart hostapd
sleep 3

# 验证模式
iw dev wlp0s20f3 info | grep -q "type AP" || {
    echo "ERROR: WiFi not in AP mode, retrying..." >&2
    systemctl restart hostapd
    sleep 3
}

# 加载 iptables
iptables-restore < /etc/iptables/iptables.rules 2>/dev/null || true

# 刷新 Clash 订阅
sleep 3
SECRET=$(grep "^secret:" /home/feisama/.local/share/io.github.clash-verge-rev.clash-verge-rev/config.yaml | awk "{print \$2}")
curl -s -X PUT http://127.0.0.1:9097/configs   -H "Authorization: Bearer $SECRET"   -H "Content-Type: application/json" -d "{}" > /dev/null 2>&1 || true

# 生成 Clash 完整配置（含订阅节点）
python3 /home/feisama/.local/share/io.github.clash-verge-rev.clash-verge-rev/gen-config.py 2>/dev/null || true
