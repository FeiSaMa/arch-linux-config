# 启用的服务

## 系统服务（15 个）

**初始 Arch 默认（~3 个）：** `getty@tty1.service`、`systemd-timesyncd.service`

**新增启用：**

| 服务 | 类型 | 作用 |
|------|------|------|
| `gdm.service` | 原生 | 图形显示管理器 |
| `NetworkManager.service` | 原生 | 网络管理 |
| `NetworkManager-wait-online.service` | 原生 | 等待网络就绪 |
| `NetworkManager-dispatcher.service` | 原生 | 网络事件分发 |
| `bluetooth.service` | 原生 | 蓝牙 |
| `power-profiles-daemon.service` | 原生 | CPU 电源模式 |
| `ufw.service` | 原生 | 防火墙 |
| `thinkfan.service` | 原生 | 风扇控制 |
| `thinkfan-sleep.service` | 原生 | 睡眠风扇关停 |
| `thinkfan-wakeup.service` | 原生 | 唤醒风扇恢复 |
| `grub-btrfsd.service` | 原生 | Btrfs 快照→GRUB 菜单 |
| `clash-verge-service.service` | 自定义 | 代理核心守护进程 |
| `ppd-profile-monitor.service` | 自定义 | 电源限制守护进程 |

## 用户服务（8 个）

```
pipewire.service
pipewire-pulse.service
wireplumber.service
xdg-user-dirs.service
gnome-keyring-daemon.socket
p11-kit-server.socket
pipewire-pulse.socket
pipewire.socket
```

## 当前启动目标

`graphical.target`（初始 Arch 安装默认 `multi-user.target`，由 `gdm` 拉入）
