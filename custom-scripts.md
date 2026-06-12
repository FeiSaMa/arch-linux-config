# 自定义脚本与 systemd 服务

## 自定义脚本：/usr/local/bin/ppd-power-tune.sh

根据 `power-profiles-daemon` 的平台 profile 动态设置 RAPL/GPU/NVMe/ASPM 参数。

```bash
# 核心逻辑
set_limits() {
    local profile="$1"
    case "$profile" in
        performance)
            pkg_pl1=75000000; pkg_pl2=110000000        # 75W / 110W
            psys_pl1=80000000; psys_pl2=130000000       # 80W / 130W
            gt0_min=700; gt1_min=450                     # GPU MHz
            nvme_lat=0; aspm=performance
            ;;
        balanced)
            pkg_pl1=65000000; pkg_pl2=85000000          # 65W / 85W
            psys_pl1=70000000; psys_pl2=95000000         # 70W / 95W
            gt0_min=650; gt1_min=400
            nvme_lat=100000; aspm=powersave
            ;;
        low-power)
            pkg_pl1=20000000; pkg_pl2=35000000          # 20W / 35W
            psys_pl1=25000000; psys_pl2=40000000         # 25W / 40W
            gt0_min=100; gt1_min=100
            nvme_lat=500000; aspm=powersupersave
            ;;
    esac
    # 写入 RAPL powercap 约束
    # 设置 GPU min_freq
    # 设置 NVMe ASPM
    # 设置 PCIe ASPM 策略
}
```

## 自定义服务 1：clash-verge-service.service

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

## 自定义服务 2：ppd-profile-monitor.service

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

## 用户 autostart：Clash Verge

```ini
~/.config/autostart/Clash Verge.desktop
[Desktop Entry]
Type=Application
Name=Clash Verge
Exec=/usr/bin/clash-verge
```
