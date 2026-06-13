# 调优变更日志

| 轮次 | 日期 | 变更 |
|------|------|------|
| 1 | 06-11 | 初始调优：PL1/PL2 动态功率墙、thinkfan 激进曲线、swappiness=1 |
| 2 | 06-12 | 修复 MMIO RAPL 遗漏（双接口写入）、`custom` profile 回退 |
| 3 | 06-12 | hwmon 编号漂移根治（name-based 匹配） |
| 4 | 06-12 | `fan_control=1` 打入 initramfs（MODULES=thinkpad_acpi） |
| 5 | 06-12 | pacman hook 滚动更新防护（journald + mkinitcpio） |
| 6 | 06-12 | MC 负载实测验证（75W 已达热边界） |
| 7 | 06-12 | GPU 最低频率联动（GT0/GT1 min_freq 跟随 PPD） |
| 8 | 06-12 | 屏幕亮度+键盘背光联动（已撤销，覆盖手动操作） |
| 9 | 06-12 | NVMe 延迟 + PCIe ASPM 纳入 PPD 联动 |
| 10 | 06-13 | VM dirty_ratio + vfs_cache_pressure + I/O scheduler none |

## 检查清单

```bash
# 服务状态
journalctl -u ppd-profile-monitor.service -b 0 -p err --no-pager
journalctl -u thinkfan -b 0 -p err --no-pager
systemctl --failed
systemctl is-active ppd-profile-monitor.service thinkfan

# 硬件状态
cat /sys/module/thinkpad_acpi/parameters/fan_control
grep . /sys/class/powercap/intel-rapl*/intel-rapl:0/constraint_0_power_limit_uw
grep . /sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio:0/constraint_0_power_limit_uw

# PPD 联动验证
powerprofilesctl set performance && sleep 12
cat /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq   # 应=700
cat /sys/module/nvme_core/parameters/default_ps_max_latency_us  # 应=0
cat /sys/module/pcie_aspm/parameters/policy                # 应=performance

powerprofilesctl set power-saver && sleep 12
cat /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq   # 应=100
cat /sys/module/nvme_core/parameters/default_ps_max_latency_us  # 应=500000
cat /sys/module/pcie_aspm/parameters/policy                # 应=powersupersave

powerprofilesctl set performance && sleep 12  # 恢复

# 系统配置
sysctl vm.swappiness
grep SystemMaxUse /etc/systemd/journald.conf
cat /proc/sys/vm/dirty_ratio
cat /proc/sys/vm/dirty_background_ratio
cat /proc/sys/vm/vfs_cache_pressure
cat /sys/block/nvme0n1/queue/scheduler

# 滚动更新防护
ls /etc/pacman.d/hooks/
find /etc -name "*.pacnew" 2>/dev/null

```
