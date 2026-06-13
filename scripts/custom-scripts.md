# 自定义脚本与 systemd 服务

所有脚本和服务文件的实际内容见 `files/` 目录。

## 文件清单

| 目标路径 | 仓库路径 |
|----------|---------|
| `/usr/local/bin/ppd-power-tune.sh` | `files/usr/local/bin/ppd-power-tune.sh` |
| `/etc/systemd/system/ppd-profile-monitor.service` | 内容见下方 |

## 自定义服务：ppd-profile-monitor.service

```ini
[Unit]
Description=PPD Profile Power Limit Monitor

[Service]
Type=exec
ExecStart=/usr/local/bin/ppd-power-tune.sh daemon
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 自定义服务：clash-verge-service.service

```ini
[Unit]
Description=Clash Verge Service
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/clash-verge-service
Group=feisama
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 用户 autostart：Clash Verge

路径：`~/.config/autostart/Clash Verge.desktop`（见 `home/` 目录）

## AI 恢复命令

```bash
sudo cp ~/refs/arch-linux-config/files/usr/local/bin/ppd-power-tune.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/ppd-power-tune.sh
sudo systemctl daemon-reload
```
