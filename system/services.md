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

## AI 启用命令

### 系统服务

```bash
sudo systemctl enable gdm.service
sudo systemctl enable NetworkManager.service
sudo systemctl enable NetworkManager-wait-online.service
sudo systemctl enable bluetooth.service
sudo systemctl enable power-profiles-daemon.service
sudo systemctl enable ufw.service
sudo systemctl enable thinkfan.service thinkfan-sleep.service thinkfan-wakeup.service
sudo systemctl enable grub-btrfsd.service
sudo systemctl enable ppd-profile-monitor.service
sudo systemctl enable clash-verge-service.service
```

### 用户服务

```bash
systemctl --user enable pipewire.service
systemctl --user enable pipewire-pulse.service
systemctl --user enable wireplumber.service
systemctl --user enable xdg-user-dirs.service
systemctl --user enable gnome-keyring-daemon.socket
systemctl --user enable p11-kit-server.socket
systemctl --user enable pipewire-pulse.socket
systemctl --user enable pipewire.socket
```

### UFW 防火墙

```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

## 当前启动目标

`graphical.target`（初始 Arch 安装默认 `multi-user.target`，由 `gdm` 拉入）
