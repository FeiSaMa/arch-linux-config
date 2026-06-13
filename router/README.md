# 第二台 ThinkPad — 软路由配置

> ThinkPad T14 · Arch Linux · Intel Core Ultra 7 356H
> 用途：WiFi 热点 + Clash 透明代理路由器

## 网络拓扑

```
主路由 (192.168.1.1)
    │
    ├─ 本机 (192.168.1.16) — 有线
    │
    └─ 路由 ThinkPad (192.168.1.195) — 有线 enp0s31f6
                        │
                        └─ WiFi 热点 wlp0s20f3 (192.168.2.1)
                            └─ 手机/平板/笔记本 (192.168.2.x)
                                 全部流量 → Clash 透明代理
```

## 连接信息

| 项目 | 值 |
|------|-----|
| **WiFi 名称** | `ThinkPad-Router` |
| **WiFi 密码** | `ThinkPad@2024` |
| **网关 IP** | `192.168.2.1` |
| **DHCP 范围** | `192.168.2.10` - `192.168.2.200` |
| **SSH 地址** | `192.168.1.195` |
| **SSH 用户** | `feisama` |

## 精简状态

| 项目 | 改前 | 改后 |
|------|------|------|
| 显式安装包 | 115 个 | **21 个** |
| 运行服务 | 29 个 | **14 个** |
| GNOME 桌面 | ✅ | ❌ 已移除 |
| 大型应用 | chromium、code、微信等 | ❌ 全部移除 |
| 开发工具 | base-devel、rust、yay 等 | ❌ 全部移除 |

## 目录

| 文件 | 说明 |
|------|------|
| `setup.md` | 完整部署流程 |
| `files/hotspot-setup.sh` | WiFi 热点自启脚本 |
| `files/hostapd.conf` | hostapd 配置 |
| `files/iptables.rules` | iptables 规则 |
| `files/thinkpad-power-save.sh` | 省电脚本 |
| `files/99-power-saving.conf` | sysctl 省电参数 |
