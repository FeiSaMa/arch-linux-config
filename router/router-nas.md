# T14 Gen1 NAS 配置

## 概述

在 T14 Gen1 软路由上叠加 NAS 功能，利用现有 ext4 根分区剩余空间提供 Samba 文件共享。

- **部署日期**: 2026-06-15
- **存储**: 内置 NVMe `/dev/nvme0n1p3` (ext4, 总 467 GiB, 可用 ~441 GiB)
- **共享协议**: SMB (Samba)
- **认证**: 仅 `feisama` 用户可访问

## 网络路径

```
LAN 设备 --- WiFi (wlp0s20f3) --- T14 Gen1 (192.168.2.1)
                                      │
                                      ├── router-mon (tty2 监控)
                                      ├── hostapd (WiFi AP)
                                      ├── dnsmasq (DHCP)
                                      ├── nftables (NAT + 防火墙)
                                      ├── mihomo (透明代理 TUN)
                                      └── samba (NAS 共享) ← 新增
```

## 关键文件

| 文件 | 路径 | 说明 |
|------|------|------|
| Samba 配置 | `/etc/samba/smb.conf` | 全局 + share 共享定义 |
| 共享目录 | `/srv/nas/share` | ext4 上的普通目录 |
| Samba 密码 | `smbpasswd` 数据库 | 用户 `feisama` |

## Samba 配置 (`/etc/samba/smb.conf`)

```ini
[global]
workgroup = WORKGROUP
server string = T14 Router NAS
security = user
map to guest = never
server min protocol = SMB2_02
ea support = yes
vfs objects = catia fruit streams_xattr
fruit:metadata = stream
fruit:model = MacSamba

[share]
path = /srv/nas/share
valid users = feisama
read only = no
browsable = yes
writable = yes
create mask = 0644
directory mask = 0755
force user = feisama
force group = feisama
```

### 设计决策

| 决策 | 值 | 原因 |
|------|-----|------|
| `security = user` | 用户认证 | 只有 feisama 能访问 |
| `map to guest = never` | 禁止匿名 | 未认证直接拒绝 |
| `valid users = feisama` | 单用户 | 只用路由器上的现有系统用户 |
| 无防火墙改动 | `iif wlp0s20f3 accept` | 现有规则已全部放行 LAN |
| `vfs objects = catia fruit` | Apple SMB 扩展 | iOS/iPadOS 文件操作必需 |
| `ea support = yes` | 扩展属性 | iOS 创建文件夹时写入元数据 |
| `server min protocol = SMB2_02` | SMB2+ | iOS 要求的最低协议版本 |

## 服务状态

```bash
systemctl is-enabled smb nmb   # → enabled
systemctl is-active smb nmb    # → active
```

- `smb.service` — SMB 文件共享守护进程（核心）
- `nmb.service` — NetBIOS 名称解析（Windows 网络发现）

## 访问方式

| 平台 | 地址 | 用户 | 密码 |
|------|------|------|------|
| Linux (mount) | `//192.168.2.1/share` | `feisama` | `20080201` |
| Linux (smb) | `smb://192.168.2.1/share` | `feisama` | `20080201` |
| Windows | `\\192.168.2.1\share` | `feisama` | `20080201` |
| macOS | `smb://192.168.2.1/share` | `feisama` | `20080201` |
| 手机 | 192.168.2.1 | `feisama` | `20080201` |

### 当前机器挂载命令

```bash
mkdir -p ~/NAS
pkexec mount -t cifs //192.168.2.1/share ~/NAS -o username=feisama,password=20080201,uid=1000,gid=1000,vers=3.0
```

## 当前已迁移内容

无 — 共享目录为空，等待后续优化时按需迁移。

## 安全边界

- **WAN 侧不可达** — nftables `chain input` 默认 `policy drop`，只放行 WAN SSH (端口 22)
- **LAN 侧可达** — `iif wlp0s20f3 accept` 放行所有 LAN 流量
- **未来可收紧** — 如需加固，可改为仅放行特定端口 (22, 53, 139, 445) 替代全放行

## 后续优化（待考虑）

- [ ] fstab 自动挂载（当前机器开机自动挂 NAS）
- [ ] 大文件迁移（Documents、WeChat 文件、moekoemusic 音乐缓存等）
- [ ] 备份策略（snapper 快照 / rsync）
- [ ] 收紧 LAN 防火墙规则（仅开放必要端口）
- [ ] 空间告警（磁盘使用率监控/通知）
- [ ] 性能影响评估（Samba 对 WiFi AP 频段和 CPU 的负载）
