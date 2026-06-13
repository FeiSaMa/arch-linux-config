# 软路由部署流程

从零设置第二台 ThinkPad 作为路由器。

## 前置条件

- Arch Linux 已安装（Btrfs + GRUB + 基础系统）
- 有线网口已连接主路由（自动获取 IP）
- 能通过 SSH 访问

## Phase 0: 基础安装

```bash
# SSH 连接到目标机器
ssh feisama@<TARGET_IP>

# 安装核心包
sudo pacman -S --needed dnsmasq linux-wifi-hotspot
```

## Phase 1: 配置热点

```bash
# 写入 hostapd 配置
sudo tee /etc/hostapd/hostapd.conf << 'EOF'
interface=wlp0s20f3
driver=nl80211
ssid=ThinkPad-Router
hw_mode=g
channel=6
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=ThinkPad@2024
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# 启用 hostapd 自启
sudo systemctl enable hostapd
```

## Phase 2: iptables 规则

```bash
# 启用 IP 转发
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-ipforward.conf
sudo sysctl -w net.ipv4.ip_forward=1

# 写入 iptables 规则
sudo iptables -t nat -A POSTROUTING -o enp0s31f6 -j MASQUERADE
sudo iptables -A FORWARD -i wlp0s20f3 -o enp0s31f6 -j ACCEPT
sudo iptables -A FORWARD -i enp0s31f6 -o wlp0s20f3 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -t nat -A PREROUTING -i wlp0s20f3 -p udp --dport 53 -j REDIRECT --to-port 5353
sudo iptables -t nat -A PREROUTING -i wlp0s20f3 -p tcp -j REDIRECT --to-port 7895

# 保存
sudo mkdir -p /etc/iptables
sudo iptables-save | sudo tee /etc/iptables/iptables.rules
```

## Phase 3: 部署自启脚本

```bash
# 创建热点自启脚本
sudo tee /usr/local/bin/hotspot-setup.sh << 'SCRIPT'
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
curl -s -X PUT http://127.0.0.1:9097/configs \
  -H "Authorization: Bearer $SECRET" \
  -H "Content-Type: application/json" -d "{}" > /dev/null 2>&1 || true
SCRIPT

sudo chmod +x /usr/local/bin/hotspot-setup.sh

# 创建 systemd 服务
sudo tee /etc/systemd/system/hotspot.service << 'EOF'
[Unit]
Description=WiFi Hotspot Setup
After=network.target clash-verge-service.service
Requires=clash-verge-service.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/hotspot-setup.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable hotspot
```

## Phase 4: 省电配置

```bash
# sysctl 省电
sudo tee /etc/sysctl.d/99-power-saving.conf << 'EOF'
vm.swappiness=1
vm.vfs_cache_pressure=100
vm.dirty_ratio=20
vm.dirty_background_ratio=10
kernel.nmi_watchdog=0
EOF

# 省电自启脚本
sudo tee /usr/local/bin/thinkpad-power-save.sh << 'SCRIPT'
#!/usr/bin/env bash
set -uo pipefail

echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || true
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo powersave > "$cpu" 2>/dev/null || true
done

echo 0 > /sys/class/backlight/*/brightness 2>/dev/null || true

echo powersupersave > /sys/module/pcie_aspm/parameters/policy 2>/dev/null || true
echo 500000 > /sys/module/nvme_core/parameters/default_ps_max_latency_us 2>/dev/null || true
iw dev wlp0s20f3 set power_save on 2>/dev/null || true
SCRIPT

sudo chmod +x /usr/local/bin/thinkpad-power-save.sh

# 自启服务
sudo tee /etc/systemd/system/thinkpad-power-save.service << 'EOF'
[Unit]
Description=ThinkPad Power Saving for Router
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/thinkpad-power-save.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable thinkpad-power-save
```

## Phase 5: 精简系统（可选）

```bash
# 移除 GNOME 桌面
sudo pacman -Rns --noconfirm gnome-desktop gnome-shell gdm gnome-control-center \
  gnome-software gnome-text-editor gnome-calculator gnome-clocks gnome-disk-utility \
  gnome-keyring baobab loupe snapshot file-roller ghostty chromium mission-center \
  foliate fragments neovim fastfetch yazi flatpak

# 移除开发工具和大应用
sudo pacman -Rns --noconfirm base-devel nodejs npm rust uv cmake go rustup \
  python-pip docker docker-compose inotify-tools stress-ng \
  wechat-bin moekoemusic-bin visual-studio-code-bin typora bilibili-tui-bin \
  linuxqq-nt-bwrap prismlauncher

# 移除音频/输入法/字体
sudo pacman -Rns --noconfirm alsa-firmware alsa-ucm-conf sof-firmware \
  fcitx5 fcitx5-configtool fcitx5-gtk fcitx5-qt fcitx5-rime rime-ice-git \
  noto-fonts noto-fonts-emoji ttf-jetbrains-mono ttf-jetbrains-mono-nerd \
  ttf-lxgw-wenkai-tc-mono ttf-sarasa-gothic wqy-zenhei terminus-font

# 移除其他不必要的包
sudo pacman -Rns --noconfirm bluez btrfs-assistant celluloid cmatrix \
  dosfstools easyeffects exfat-utils f2fs-tools gnome-font-viewer gnome-logs \
  gnome-weather grub-btrfs intel-media-driver lib32-mesa lib32-vulkan-intel \
  linux linux-lts linux-lts-headers man-db ntfs-3g os-prober pacman-contrib \
  papers snap-pac snapper udftools usbutils vulkan-intel w3m wget xfsprogs \
  zenity gst-plugin-pipewire pipewire-alsa pipewire-jack pipewire-pulse \
  wireplumber fprintd slirp4netns socat devtools dkms

# 清理孤儿包
sudo pacman -Rns --noconfirm $(pacman -Qtdq)
```

## Phase 6: GRUB 优化

```bash
# 禁用 os-prober、取消菜单等待
sudo sed -i 's/GRUB_TIMEOUT=5/GRUB_TIMEOUT=0/' /etc/default/grub
sudo sed -i 's/GRUB_DISABLE_OS_PROBER=false/GRUB_DISABLE_OS_PROBER=true/' /etc/default/grub
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

## Phase 7: 验证

```bash
# 服务状态
sudo systemctl is-active clash-verge-service hostapd

# 热点 IP
ip addr show wlp0s20f3 | grep 'inet '

# 代理测试
curl -s --connect-timeout 5 -x http://127.0.0.1:7897 https://www.github.com -o /dev/null -w '%{http_code}'

# 包数
sudo pacman -Q --explicit | wc -l
```

预期结果：

| 检查项 | 预期值 |
|--------|--------|
| Clash | active |
| hostapd | active |
| 热点 IP | 192.168.2.1 |
| GitHub | 301 |
| 包数 | ≈21 |
