# 调优改进循环

> 持续改进循环。每次执行：审查日志 → 检查稳定性/滚动更新 → 优化文档 → 写入/同步。

## 变更摘要

| 轮次 | 日期 | 变更 | 详情 |
|------|------|------|------|
| 1 | 06-12 | 创建 pacman hook（journald + mkinitcpio 滚动更新防护） | 补充文档附录 |
| 2 | 06-12 | 优化检查清单格式，统一表格 | 无功能变更 |
| 3 | 06-12 | 无变更 | 全通过 |
| 4 | 06-12 | 修正 PSYS 域不存在的误导性记录 | 全通过 |
| 5 | 06-12 | MC 负载实测 + 风扇读数修复（`fan` 函数） | 75W 已达热边界 |
| 6 | 06-12 | 无变更 | 全通过 |
| 7 | 06-12 | GPU 最低频率联动（GT0/GT1 min_freq 跟随 PPD） | 新增第 12 节 |
| 8 | 06-12 | 屏幕亮度 + 键盘背光联动 | 新增第 13 节 |
| 9 | 06-12 | **撤销** 亮度/背光联动（覆盖手动操作） | 第 13 节改为已撤销 |
| 10 | 06-12 | NVMe 延迟 + PCIe ASPM（modprobe + GRUB） | 新增第 14 节 |
| 11 | 06-12 | NVMe + ASPM 改为 PPD 联动，移除 modprobe/GRUB | 第 14 节更新 |
| 12 | 06-13 | VM dirty_ratio + vfs_cache_pressure + I/O scheduler none | 写入 ppd-power-tune.sh |
| 13 | 06-13 | Caffeine PPD 联动（自动切 performance） | 写入 ppd-power-tune.sh |

## 检查清单

```bash
# 1. 服务状态
journalctl -u ppd-profile-monitor.service -b 0 -p err --no-pager
journalctl -u thinkfan -b 0 -p err --no-pager
systemctl --failed
systemctl is-active ppd-profile-monitor.service thinkfan

# 2. 硬件状态
cat /sys/module/thinkpad_acpi/parameters/fan_control
grep . /sys/class/powercap/intel-rapl*/intel-rapl:0/constraint_0_power_limit_uw
grep . /sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio:0/constraint_0_power_limit_uw

# 2.5 PPD 联动状态（切到对应 profile 检查）
powerprofilesctl set performance && sleep 12
cat /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq   # 应=700
cat /sys/class/drm/card0/device/tile0/gt1/freq0/min_freq   # 应=450
cat /sys/module/nvme_core/parameters/default_ps_max_latency_us  # 应=0
cat /sys/module/pcie_aspm/parameters/policy                # 应=performance

powerprofilesctl set power-saver && sleep 12
cat /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq   # 应=100
cat /sys/module/nvme_core/parameters/default_ps_max_latency_us  # 应=500000
cat /sys/module/pcie_aspm/parameters/policy                # 应=powersupersave

powerprofilesctl set performance && sleep 12  # 恢复

# 3. 系统配置
sysctl vm.swappiness
grep SystemMaxUse /etc/systemd/journald.conf
timedatectl show --property NTPSynchronized
cat /proc/sys/vm/dirty_ratio
cat /proc/sys/vm/dirty_background_ratio
cat /proc/sys/vm/vfs_cache_pressure
cat /sys/block/nvme0n1/queue/scheduler

# 4. 滚动更新防护
ls /etc/pacman.d/hooks/
find /etc -name "*.pacnew" 2>/dev/null

# 5. Caffeine 联动（performance → ON，退出 → OFF）
systemd-run --user -M feisama@ -P gsettings get org.gnome.shell.extensions.caffeine cli-toggle
journalctl -u ppd-profile-monitor.service | grep -i caffeine | tail -5
```

---

## 有变更的轮次详情

### 第一轮 (06-12) — pacman hook 滚动更新防护

审查发现 `journald.conf`（systemd 包）和 `mkinitcpio.conf`（mkinitcpio 包）会在包更新时被覆盖，创建两个 hook 自动修复：

- `/etc/pacman.d/hooks/merge-journald-conf.hook` — `PostTransaction` 自动追加 `SystemMaxUse=500M`
- `/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook` — `PostTransaction` 自动保持 `MODULES=(thinkpad_acpi)`

### 第五轮 (06-12) — MC 负载实测 + 风扇读数修复

**MC 实测数据（performance 模式，2 分钟）：**
- MC CPU%: 115% → 176%
- Package 温度: 48°C → 86°C（稳定），最高核心 96°C（距 TJmax 仅 4°C）
- 风扇: level 2→7, 3015 RPM

**结论：** 75W PL1 已是热边界，不建议再提升功率。

**修复：** `sensors` 误报 0 RPM（读到 `acpi_fan` 而非 `thinkpad` hwmon）。
`~/.zshrc` 添加 `fan` 函数直接读取 thinkpad hwmon：
```bash
fan() { cat /sys/class/hwmon/$(grep -l ^thinkpad /sys/class/hwmon/hwmon*/name | grep -oP "hwmon[0-9]+")/fan1_input && echo " RPM"; }
```

### 第七轮 (06-12) — GPU 最低频率联动

在 `ppd-power-tune.sh` 中按 PPD 模式写入 GT0/GT1 `min_freq`：

| 模式 | GT0 min_freq | GT1 min_freq |
|------|-------------|-------------|
| performance | 700 MHz | 450 MHz |
| balanced | 650 MHz | 400 MHz |
| low-power | 100 MHz | 100 MHz |

### 第八轮 (06-12) — 屏幕亮度 + 键盘背光联动（已撤销）

将屏幕亮度和键盘背光纳入 PPD 联动，但用户反馈覆盖手动操作不好用，**下一轮已撤销**。

### 第九轮 (06-12) — 撤销亮度/背光联动

从脚本中移除屏幕亮度和键盘背光写入，恢复手动控制。

### 第十轮 (06-12) — NVMe 延迟 + PCIe ASPM

- 新建 `/etc/modprobe.d/99-nvme-performance.conf`：`options nvme_core default_ps_max_latency_us=0`
- 修改 GRUB 命令行追加 `pcie_aspm.policy=performance`
- 运行 `grub-mkconfig`

### 第十一轮 (06-12) — NVMe + ASPM 改为 PPD 联动

移除 modprobe.d 和 GRUB 配置，整合到 `ppd-power-tune.sh` 动态切换：

| 模式 | NVMe 延迟 | PCIe ASPM |
|------|----------|-----------|
| performance | 0 | performance |
| balanced | 100000 | powersave |
| low-power | 500000 | powersupersave |

### 第十二轮 (06-13) — VM dirty_ratio + vfs_cache_pressure + I/O scheduler none

纳入 PPD 联动，写入 `ppd-power-tune.sh`：

| 模式 | dirty_ratio | dirty_background_ratio | vfs_cache_pressure |
|------|------------|----------------------|-------------------|
| performance | 10% | 5% | 50 |
| balanced | 15% | 7% | 75 |
| low-power | 20% | 10% | 100 |

- **I/O scheduler**: NVMe 固定 `none`，daemon 启动时一次性写入
- **设计意图**: 低延迟场景减少脏页阈值避免写回尖峰，performance 模式更激进保留文件缓存

### 第十三轮 (06-13) — PPD → Caffeine 联动

performance 模式时自动开启 Caffeine 防休眠，退出时自动关闭：

| PPD 模式变化 | Caffeine |
|-------------|---------|
| 切入选定 → performance | 开启（防休眠） |
| 切出 performance | 关闭 |

实现：`ppd-power-tune.sh` daemon 中通过 `systemd-run --user -M feisama@ gsettings set` 控制 caffeine 的 cli-toggle 键。
