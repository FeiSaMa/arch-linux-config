# ThinkPad T14 Gen1 软路由配置指南

## 网络拓扑

```
光猫/宽带 --- [enp0s31f6] T14 Gen1 (Arch Linux) --- [wlan0 AP] --- LAN 设备
                        │
                    NAT + DHCP + DNS
```

- **WAN**: 内置以太网口 `enp0s31f6`（接光猫/宽带）
- **LAN**: 内置 WiFi `wlp0s20f3`（作为 AP，提供 DHCP + DNS）
- **系统**: Arch Linux（全新安装）

---

## 一、安装 Arch Linux

### 1.1 确认网络硬件

```bash
# 查看网卡和 WiFi 芯片
lspci | grep -iE 'network|ethernet|wireless|wifi'

# 查看网络接口
ip link show
```

### 1.2 连接网络（Live 环境）

```bash
# 有线自动获取 IP（如果光猫是路由模式）
dhcpcd

# 或者 WiFi 连接
iwctl
# 在 iwctl 里：
# station wlan0 scan
# station wlan0 connect <SSID>
# exit
```

### 1.3 按 Arch Wiki 标准流程安装

```bash
# 分区（建议：EFI 512M + swap 4G + 剩余给 /）
fdisk -l
cfdisk /dev/nvme0n1

# 格式化
mkfs.fat -F32 /dev/nvme0n1p1
mkswap /dev/nvme0n1p2
mkfs.ext4 /dev/nvme0n1p3

# 挂载
mount /dev/nvme0n1p3 /mnt
mount --mkdir /dev/nvme0n1p1 /mnt/boot
swapon /dev/nvme0n1p2

# 安装基础系统（安装后不要重启）
pacstrap -K /mnt base base-devel linux linux-firmware vim sudo networkmanager dhcpcd dnsmasq hostapd nftables
genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt
```

---

## 二、基础系统配置

### 2.1 基本设置

```bash
# 时区
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
hwclock --systohc

# 本地化
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
echo "zh_CN.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

# 主机名
echo "router" > /etc/hostname
cat > /etc/hosts << EOF
127.0.0.1   localhost
::1         localhost
127.0.1.1   router.localdomain router
EOF

# root 密码
passwd
```

### 2.2 安装引导

```bash
# Intel CPU 微码
pacman -S intel-ucode

# GRUB
pacman -S grub efibootmgr
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

### 2.3 创建普通用户

```bash
useradd -m -G wheel feisama
passwd feisama
echo "%wheel ALL=(ALL:ALL) ALL" >> /etc/sudoers.d/wheel
```

---

## 三、网络配置

### 3.1 确认接口名称

```bash
# 查看接口（记下名称）
ip link show
```

典型名称：
- `enp0s31f6` — 内置以太网口（WAN）
- `wlp0s20f3` — 内置 WiFi（LAN AP）

### 3.2 配置 NetworkManager

```bash
systemctl enable NetworkManager
```

创建 WAN 连接（有线，DHCP 方式）：

```bash
nmcli connection add type ethernet con-name wan ifname enp0s31f6 ipv4.method auto
```

> **如果宽带需要 PPPoE 拨号**，改为：
> ```bash
> pacman -S ppp
> nmcli connection add type ethernet con-name wan ifname enp0s31f6 ipv4.method disabled
> nmcli connection add type pppoe con-name pppoe-wan ifname enp0s31f6 username "宽带账号" password "宽带密码" ipv4.method auto
> ```

### 3.3 配置 hostapd（WiFi AP）

```bash
# 查看 WiFi 支持的模式
iw list | grep "Supported interface modes" -A 8
```

创建 hostapd 配置：

```bash
cat > /etc/hostapd/hostapd.conf << 'EOF'
interface=wlp0s20f3
driver=nl80211
ssid=T14-Router
hw_mode=g
channel=6
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=YourPassword123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# 修改密码
# vim /etc/hostapd/hostapd.conf
```

> **注意**：如果 WiFi 芯片是 Intel AX200/AX210，支持 5GHz（`hw_mode=a`），建议用 5GHz 减少干扰。如果信道被 DFS 占用，选 36-48 之间的信道。

配置 hostapd 服务：

```bash
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' >> /etc/default/hostapd
systemctl enable hostapd
```

### 3.4 配置 dnsmasq（DHCP + DNS）

```bash
cat > /etc/dnsmasq.conf << 'EOF'
# 监听接口
interface=wlp0s20f3
bind-interfaces

# DHCP 范围（LAN 侧）
dhcp-range=192.168.2.50,192.168.2.200,255.255.255.0,24h

# 网关（本机 LAN 地址）
dhcp-option=3,192.168.2.1

# DNS 服务器
dhcp-option=6,192.168.2.1

# DNS 上游
server=223.5.5.5
server=114.114.114.114

# 缓存
cache-size=1000

# 域名解析
domain-needed
bogus-priv
expand-hosts
EOF

systemctl enable dnsmasq
```

### 3.5 配置 nftables（NAT + 防火墙）

```bash
cat > /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        # 允许已建立的连接
        ct state established,related accept

        # 允许环回
        iif lo accept

        # 允许 LAN 侧访问本机
        iif wlp0s20f3 accept

        # 允许 SSH（WAN 侧可选）
        # tcp dport 22 accept

        # 允许 ICMP（ping）
        icmp type echo-request accept
        icmpv6 type echo-request accept

        # 记录并丢弃其他
        log prefix "nftables-drop: " counter drop
    }

    chain forward {
        type filter hook forward priority filter; policy drop;

        # 允许 LAN -> WAN
        iif wlp0s20f3 oif enp0s31f6 accept

        # 允许 WAN -> LAN 的已建立连接
        iif enp0s31f6 oif wlp0s20f3 ct state established,related accept

        # 如果使用 PPPoE，把 enp0s31f6 替换为 pppoe-wan
    }

    chain output {
        type filter hook output priority filter; policy accept
    }
}

table inet nat {
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;

        # MASQUERADE（WAN 接口）
        oif enp0s31f6 masquerade

        # 如果使用 PPPoE：
        # oif pppoe-wan masquerade
    }

    chain prerouting {
        type nat hook prerouting priority dstnat; policy accept
    }
}
EOF

systemctl enable nftables
```

### 3.6 启用 IP 转发

```bash
cat > /etc/sysctl.d/99-ip-forward.conf << 'EOF'
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
EOF
```

### 3.7 配置 LAN 接口 IP

给 WiFi 接口分配静态 IP（作为 LAN 网关）：

```bash
nmcli connection add type wifi con-name lan ifname wlp0s20f3 autoconnect yes \
  ipv4.method manual \
  ipv4.addresses 192.168.2.1/24 \
  ipv4.gateway "" \
  ipv4.dns "" \
  ipv6.method disabled
```

> **注意**：hostapd 会接管 WiFi 接口，NetworkManager 需要配置为不自动管理该接口，或者用 `unmanaged-devices` 排除：
> ```bash
> cat > /etc/NetworkManager/conf.d/90-unmanaged-wifi.conf << 'EOF'
> [keyfile]
> unmanaged-devices=interface-name:wlp0s20f3
> EOF
> ```

---

## 四、启动服务

```bash
# 重启 NetworkManager
systemctl restart NetworkManager

# 启动 hostapd
systemctl start hostapd

# 启动 dnsmasq
systemctl start dnsmasq

# 启动 nftables
systemctl start nftables

# 检查状态
systemctl status hostapd dnsmasq nftables
```

---

## 五、验证

### 5.1 在 T14 本机验证

```bash
# 查看接口 IP
ip addr show wlp0s20f3
ip addr show enp0s31f6

# 查看 NAT 规则
nft list ruleset

# 查看 DHCP 分配
journalctl -u dnsmasq | tail -20
```

### 5.2 用手机/其他设备验证

1. 搜索 WiFi `T14-Router`，输入密码连接
2. 连接后检查是否能获取到 `192.168.2.x` 的 IP
3. 打开浏览器访问网页

### 5.3 如果无法上网

```bash
# 检查 WAN 连接
nmcli connection show --active
ping -c 3 223.5.5.5

# 检查 NAT
tcpdump -i enp0s31f6 -n icmp
# 在 LAN 设备上 ping 223.5.5.5，看 WAN 口是否有流量

# 检查防火墙日志
journalctl -u nftables | grep "nftables-drop"
```

---

## 六、常见问题

### 6.1 光猫桥接 vs 路由模式

不确定宽带类型时，先按 DHCP 方式配置。如果插网线后 `enp0s31f6` 获取不到 IP，说明光猫是桥接模式，需要改用 PPPoE。

### 6.2 WiFi 信道选择

```bash
# 扫描周围 WiFi，选干扰少的信道
iw dev wlp0s20f3 scan | grep -E "freq|SSID"
```

### 6.3 开机自启

所有服务已 `enable`，重启测试：

```bash
reboot
# 重启后检查服务状态
systemctl status hostapd dnsmasq nftables
```

### 6.4 如果 WiFi 不支持 AP 模式

极少数 WiFi 芯片不支持 AP 模式。如果 `hostapd` 启动失败：

```bash
# 查看错误
journalctl -u hostapd -n 50

# 备选方案：用 USB 网卡做 AP，或外接交换机用有线 LAN
```

---

## 七、后续优化

- [ ] 配置 Clash 透明代理（参考 `~/refs/arch-linux-config/network/clash/`）
- [ ] 配置端口转发（`nft add rule inet nat prerouting ...`）
- [ ] 配置动态 DNS
- [ ] 配置流量统计（`vnstat`）
- [ ] 配置 AdGuard Home 替代 dnsmasq 做 DNS 过滤
