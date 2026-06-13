# 系统提权规则

## 权限提升
- 当前机器（pam_faillock 已配置）：使用 `pkexec`，sudo 失败 3 次会锁定 10 分钟
- 新安装的机器（pam_faillock 未配置）：使用 `sudo`，pkexec 在 TTY 下需要 polkit 代理

AI 检测规则：`pkexec --version` 成功 → 用 pkexec；否则用 sudo。

示例：
```bash
# 新机器（推荐）
sudo cp file /etc/somewhere

# 当前机器（pam_faillock 已配置）
pkexec cp file /etc/somewhere
```

## GRUB 配置
GRUB 配置文件位于 `/etc/default/grub`，修改后需运行：
```bash
pkexec grub-mkconfig -o /boot/grub/grub.cfg     # 当前机器
sudo grub-mkconfig -o /boot/grub/grub.cfg        # 新机器
```

### GRUB 主题 CyberGRUB-2077
- 主题文件有两份：`/efi/grub/themes/CyberGRUB-2077/theme.txt`（ESP）和 `/boot/grub/themes/CyberGRUB-2077/theme.txt`（Btrfs），**修改必须同步两份**
- 菜单项字体：`Rajdhani Regular 24`（上游原值）；中文通过 GRUB 字体回退自动使用 Noto Sans CJK 显示
- 主题 refs 配置路径：`~/refs/arch-linux-config/files/boot/grub/themes/CyberGRUB-2077/theme.txt`
- 上游仓库：`https://github.com/adnksharp/CyberGRUB-2077`

## 配置同步规则

### 系统配置参考
涉及系统配置文件（如 `/etc/` 下的文件）的修改，先参考 `~/refs/arch-linux-config/` 中的已有文档。

### 硬件配置参考
涉及硬件相关修改（如 ThinkPad 电源管理、内核参数、CPU/GPU 调优等），先参考 `~/refs/arch-linux-config/hardware/` 中的已有文档。

### 硬件功能验证
当需要检查硬件是否运行正常时，除常规检测外还必须验证自定义调优参数是否生效：

```bash
# 1. 风扇控制
cat /sys/module/thinkpad_acpi/parameters/fan_control  # 应为 Y

# 2. RAPL 功率墙（MSR + MMIO 双接口需一致）
grep . /sys/class/powercap/intel-rapl*/intel-rapl:0/constraint_0_power_limit_uw
grep . /sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio:0/constraint_0_power_limit_uw

# 3. PPD 联动 — 三档切换验证
echo "=== performance ==="
cat /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq  # 应 700
cat /sys/module/nvme_core/parameters/default_ps_max_latency_us  # 应 0
cat /sys/module/pcie_aspm/parameters/policy | grep -oP '\[\K[^\]]+'  # 应 performance
cat /proc/sys/vm/dirty_ratio  # 应 10

echo "=== balanced ==="
# GT0=650, NVMe=100000, ASPM=powersave, dirty=15

echo "=== low-power ==="
# GT0=100, NVMe=500000, ASPM=powersupersave, dirty=20

# 4. 关键服务
systemctl is-active thinkfan ppd-profile-monitor.service  # 均应 active

# 5. Caffeine 联动（performance 模式下应自动开启）
gsettings get org.gnome.shell.extensions.caffeine cli-toggle 2>/dev/null || echo "需 GNOME 会话"
```

### 同步到 Git
对系统或硬件做出任何更改后，需同步到仓库并推送到 GitHub：

更新 `~/refs/arch-linux-config/` 中的文件（含 `hardware/` 子目录），然后：
```
git -C ~/refs/arch-linux-config add -A
git -C ~/refs/arch-linux-config commit -m "描述更改内容"
git -C ~/refs/arch-linux-config push
```
