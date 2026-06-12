# 电源与散热调优

## 电源管理模式

`power-profiles-daemon` 接管 CPU 频率策略（替代默认 intel_pstate 直管）。

| Profile | CPU Governor | EPP | 场景 |
|---------|-------------|-----|------|
| performance | performance | performance | 插电/高性能 |
| balanced | powersave | balance_performance | 日常 |
| low-power | powersave | balance_power | 省电 |

## RAPL 功率限制（自定义脚本控制）

通过 `ppd-power-tune.sh` 在 3 档间动态切换 Intel CPU/平台功率限制：

| Profile | PKG PL1 | PKG PL2 | PSYS PL1 | PSYS PL2 |
|---------|---------|---------|----------|----------|
| performance | 75W | 110W | 80W | 130W |
| balanced | 65W | 85W | 70W | 95W |
| low-power | 20W | 35W | 25W | 40W |

## GPU 频率控制

| Profile | GT0 min | GT1 min |
|---------|---------|---------|
| performance | 700 MHz | 450 MHz |
| balanced | 650 MHz | 400 MHz |
| low-power | 100 MHz | 100 MHz |

## 风扇控制（thinkfan）

- 内核模块：`thinkpad_acpi fan_control=1`
- thinkfan 服务接管硬件 PWM 风扇控制
- 睡眠/唤醒 hook 自动关停/恢复风扇

## NVMe ASPM

| Profile | 延迟 | ASPM 策略 |
|---------|------|-----------|
| performance | 0 µs | performance |
| balanced | 100 µs | powersave |
| low-power | 500 µs | powersupersave |

## 交换与内存

```ini
# /etc/systemd/zram-generator.conf
[zram0]
zram-size = ram                    # 30.8G
compression-algorithm = zstd

# /etc/sysctl.d/99-swappiness.conf
vm.swappiness = 1                  # 极低交换倾向
```

## 日志限制

```ini
# /etc/systemd/journald.conf（自动维持）
SystemMaxUse=500M
```

## Intel Undervolt

`intel-undervolt` 已安装但尚未配置（`/etc/intel-undervolt.conf` 不存在）。

## 系统监控

- `mission-center` — GNOME 系统监视器
- `Vitals` GNOME 扩展 — 面板实时传感器（CPU/内存/网络/风扇/温度，1s 更新）
- `fastfetch` — CLI 系统信息
- `htop` — 进程管理
