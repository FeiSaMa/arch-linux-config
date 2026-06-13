# 网络与安全

## 网络管理

| 组件 | 状态 |
|------|------|
| NetworkManager | 替代 systemd-networkd 接管网络 |
| 连通性检测 | 禁用 |
| DHCP | 自动（192.168.1.0/24） |
| DNS | NetworkManager 自动配置（192.168.1.1） |
| WiFi | 已保存 2 个网络（2603、Alexander的iPhone） |
| Tun | Clash Meta 虚拟网卡 |

```ini
/etc/NetworkManager/conf.d/20-connectivity.conf
[connectivity]
enabled=false
```

## 防火墙

```bash
ufw enable
ufw status verbose
# 默认：进站 deny，出站 allow
```

## 代理

```ini
# /etc/environment 中设置了 fcitx5 相关环境变量
# Clash Verge 代理核心：
#   - 系统服务：clash-verge-service.service
#   - 桌面 autostart：Clash Verge.desktop
#   - 代理 PAC 地址：http://127.0.0.1:33331/commands/pac
#   - GNOME 代理模式：none（当前未启用）
#   - 配置备份：network/clash/（含 profiles.yaml、verge.yaml、规则文件等）
```

## 网络连接

```
NAME           TYPE      DEVICE
有线连接 1     ethernet  enp0s31f6
Meta           tun       Meta
lo             loopback  lo
```

## DNS

当前通过 DHCP 获取（192.168.1.1），无自定义 DNS 配置。
