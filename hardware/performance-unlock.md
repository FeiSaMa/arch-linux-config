# ThinkPad 性能释放调优记录

> **历史文档：** 本文记录的是最初调优的全过程，包含原始脚本和内嵌的命令。
> **当前可执行版本见：** `files/usr/local/bin/ppd-power-tune.sh`

日期: 2026-06-11
主机: ThinkPad / Arch Linux / Intel Core Ultra 7 356H / 内核 7.0.11-zen

---

## TL;DR

GNOME 右上角切 PPD 模式，六类参数自动跟随：

| 模式 | PL1 | PL2 | GT0 min_freq | NVMe 延迟 | ASPM | dirty_ratio | 满载温度 |
|------|-----|-----|-------------|----------|------|------------|---------|
| ⚡ 性能 | **75W** (↑15%) | **110W** (↑69%) | 700 MHz | 0 µs | performance | 10% | 94°C |
| 🌿 平衡 | 65W | **85W** (↑31%) | 650 MHz | 100 µs | powersave | 15% | 95°C |
| 🍃 省电 | **20W** (↓69%) | **35W** (↓46%) | 100 MHz | 500 µs | powersupersave | 20% | 52°C |

核心改动：`ppd-power-tune.sh` + `ppd-profile-monitor.service`。

```bash
# 部署
pkexec systemctl enable --now ppd-profile-monitor.service

# 检查日志
journalctl -u ppd-profile-monitor.service --since "5 min ago"

# 快速验证
journalctl -u ppd-profile-monitor.service -n 3 --no-pager

# 完整复原（一次性提权，覆盖所有管理参数）
# swappiness/journald/thinkfan/mitigations 需单独还原（见各节）
pkexec sh -c '
  systemctl disable --now ppd-profile-monitor.service
  rm /usr/local/bin/ppd-power-tune.sh /etc/systemd/system/ppd-profile-monitor.service
  systemctl daemon-reload
  # 复位 RAPL（MSR + MMIO 全部覆盖）
  for d in /sys/class/powercap/intel-rapl*/intel-rapl* /sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio*; do
    [ -f "$d/name" ] || continue
    case "$(cat "$d/name")" in
      package-0) echo 65000000 > "$d/constraint_0_power_limit_uw" 2>/dev/null || true
                 echo 65000000 > "$d/constraint_1_power_limit_uw" 2>/dev/null || true ;;
      psys)      echo 65000000 > "$d/constraint_0_power_limit_uw" 2>/dev/null || true
                 echo 100000000 > "$d/constraint_1_power_limit_uw" 2>/dev/null || true ;;
    esac
  done
  # 复位 GPU min_freq
  echo 100 > /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq 2>/dev/null || true
  echo 100 > /sys/class/drm/card0/device/tile0/gt1/freq0/min_freq 2>/dev/null || true
  # 复位 NVMe 电源延迟
  echo 100000 > /sys/module/nvme_core/parameters/default_ps_max_latency_us 2>/dev/null || true
  # 复位 PCIe ASPM
  echo powersave > /sys/module/pcie_aspm/parameters/policy 2>/dev/null || true
  # 复位 VM 参数
  echo 20 > /proc/sys/vm/dirty_ratio 2>/dev/null || true
  echo 10 > /proc/sys/vm/dirty_background_ratio 2>/dev/null || true
  echo 100 > /proc/sys/vm/vfs_cache_pressure 2>/dev/null || true
  # 复位 I/O scheduler
  echo kyber > /sys/block/nvme0n1/queue/scheduler 2>/dev/null || true
'
```

---

## 1. 核心: PL1/PL2 动态功率墙

### 目标
原厂 PL1=PL2=65W，CPU 满载 95~96°C。
性能模式有未使用的散热余量，省电模式缺少功率约束。

### 方案
`/usr/local/bin/ppd-power-tune.sh` 每 10 秒轮询 `/sys/firmware/acpi/platform_profile`，
按 PPD 模式写入 RAPL 功率限制。同时写 MSR + MMIO 两套接口（Arrow Lake 双 RAPL 驱动并存）。

### 功率值的设计依据

| 模式 | PL1 | PL2 | 为什么是这个值 |
|------|-----|-----|--------------|
| performance | **75W** | **110W** | 65W→75W 提 15% 功率，94°C 已达热边界。80W 预估 +4°C 会触 TJmax 降频 |
| balanced | 65W | **85W** | PL1 不变确保持续负载安全；PL2 给 20W 爆发，日常操作（编译/开应用）响应更快 |
| power-saver | **20W** | **35W** | EPP=power 时 CPU 仅 ~15W，20W 有余量且不拖 race-to-idle。30W 形同虚设 |

### 当前脚本（完整版）

最终脚本见第 8 节「最终脚本」处，包含 RAPL、GPU min_freq、NVMe 延迟、PCIe ASPM、VM dirty_ratio/cache_pressure、I/O scheduler 全部六类联动项。

单次查看或手动应用：
```bash
/usr/local/bin/ppd-power-tune.sh apply
```

如需调整功率值（如试 PL1=80W），编辑 `/usr/local/bin/ppd-power-tune.sh` 中对应变量，单位为微瓦（`75000000` = 75W），改完 `systemctl restart ppd-profile-monitor.service` 生效。

### 服务文件

`/etc/systemd/system/ppd-profile-monitor.service`:

```ini
[Unit]
Description=PPD Profile Power Limit Monitor

[Service]
Type=exec
ExecStart=/usr/local/bin/ppd-power-tune.sh daemon
Restart=on-failure
RestartSec=5
TimeoutStartSec=10

[Install]
WantedBy=multi-user.target
```

### 架构决策备忘

| 决策 | 替代方案 | 为什么选这个 |
|------|---------|------------|
| 轮询 `platform_profile` | D-Bus 监听 PPD | D-Bus 信号在 service 环境下 pipe buffer 卡死；轮询 10s 足够快且 100% 可靠 |
| `find_domains` 按 name 搜索 | 硬编码 `:0`/`:1` | Arrow Lake 同时有 MSR + MMIO 两套 RAPL，硬编码只写到一个 |
| 启动时缓存域路径 | 每轮重新 glob | 路径 runtime 不变，缓存省 90% 每轮搜索开销 |
| `set -uo` 不加 `-e` | `set -euo` | sysfs 写入可能因竞争条件临时失败，`-e` 会杀死 daemon |
| 写入失败 `echo >&2` | 静默 `|| true` | stderr 落入 journal，可追溯；静默吞掉等于盲飞 |
| 无 `ExecStartPre` | 有独立的 init apply | daemon 首轮立即 apply，不需要 init 步骤 |
| 10s 轮询 | 5s / 2s | 10s 对 GNOME 手动切 profile 几乎无感，省一半开销 |

---

## 2. 辅助: 风扇曲线激进调优

`/etc/thinkfan.conf` — `levels:` 段整体提前 2~13°C：

```yaml
levels:
  - [0, 0, 40]   - [1, 35, 43]   - [2, 40, 48]   - [3, 45, 55]
  - [4, 50, 62]   - [5, 56, 68]   - [6, 62, 72]   - [7, 68, 100]
```

| 等级 | 改前范围 | 改后范围 |
|------|---------|---------|
| 0~2 | 0~50°C | 0~48°C (微调) |
| 3~4 | 48~65°C | 45~62°C (提前 3~5°C) |
| 5~7 | 62~100°C | 56~100°C (提前 6~12°C) |

原厂曲线（还原用）：
```
levels:
  - [0, 0, 40]   - [1, 38, 45]   - [2, 42, 50]   - [3, 48, 58]
  - [4, 55, 65]   - [5, 62, 75]   - [6, 70, 85]   - [7, 80, 100]
```

负载测试（performance 75W 下）：

| 负载 | 温度 | 风扇 |
|------|------|------|
| 空载 | 46~48°C | 2 |
| 2 核 | 75~78°C | 5~6 |
| 4 核 | 85~92°C | 7 |
| 8 核 | 94°C | 7 |

注：原厂 65W 下 95~96°C，现 75W 下 94°C — 多 15% 功率反降 1~2°C，风扇提前散热有效。

配置由 thinkfan 包管理，`fan_control=1` 和 `-b0` 均由 `/usr/lib/` 提供，无需在 `/etc/` 留存副本。

---

## 3. 辅助: 其他系统调优

| 项 | 改前 | 改后 | 文件 |
|----|------|------|------|
| vm.swappiness | 60 | **1** | `/etc/sysctl.d/99-swappiness.conf` |
| journald 上限 | 未设 (~4GB) | **500M** | `/etc/systemd/journald.conf` (追加行) |
| NTP 同步 | 未启动 | **timedatectl set-ntp true** | — |
| btrfs device path | MISSING | **已扫描** | — |

---

## 4. 已尝试但失败的方案

- **CPU 降压 (intel-undervolt)**: Arrow Lake (Ultra 7 356H) MSR 0x150 写入被内核拒绝
  (`Write to unrecognized MSR 0x150`)。硬件级锁定，无法 undervolt。
  包仍保留（未配置），若未来内核/firmware 支持（可能通过 MSR 0x1a4），可重新尝试。

---

## 5. 维护指南

### 风险矩阵

| 变更 | 风险 | 说明 |
|------|------|------|
| `ppd-power-tune.sh` + 服务 | 🟢 低 | RAPL sysfs 内核 ABI 从 3.13 起不变；`platform_profile` 从 5.12 起稳定 |
| `thinkfan.conf` | 🟢 低 | YAML 稳定，文件在 `/etc/` 不被包覆盖 |
| 其余配置 | 🟢 低 | 单行文件，删除即还原 |

### 滚动更新检查

```bash
systemctl is-active ppd-profile-monitor.service thinkfan
grep . /sys/class/powercap/intel-rapl*/intel-rapl:0/constraint_0_power_limit_uw
powerprofilesctl set balanced && sleep 12 && grep . /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
powerprofilesctl set performance && sleep 12 && grep . /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
```

### 完整恢复所有出厂设置

除上述核心复原命令外，其他变更：

```bash
pkexec sh -c '
  rm /etc/sysctl.d/99-swappiness.conf
  sysctl -w vm.swappiness=60
  sed -i "/^SystemMaxUse=500M/d" /etc/systemd/journald.conf
  systemctl restart systemd-journald
'
# 恢复 thinkfan 曲线（原厂值见第 2 节）
# 手动替换 /etc/thinkfan.conf 中 levels: 段，然后重启:
systemctl restart thinkfan
```

### 已知风险

- **硅脂老化**: 1 年后同功率温度可能升 3~5°C，届时降 PL1 到 70W 或换硅脂
- **RAPL 域全找不到**: `package-0` 找不到时脚本 `exit 1`，服务自动重启重试。`psys` 找不到仅 warning，不影响主功能。
- **写入最终不生效**: 若 MSR 与 MMIO 值不同，硬件取最小值。脚本同时写入两者确保无歧义。

---

## 6. 踩过的坑

1. **MMIO RAPL 未写入** — 初版只写 MSR，Arrow Lake 实际控制器在 MMIO 侧。`find_domains` 同时搜索 MSR + MMIO 解决。
2. **D-Bus 信号 pipe 卡死** — `gdbus monitor | while read` 在 systemd 下 buffer 阻塞。改轮询解决。
3. **`set -e` 杀死 daemon** — 单次 sysfs 写入失败 → 整个服务重启。去掉 `-e` 解决。
4. **`Requires=PPD` 过度约束** — PPD 崩溃连带杀死功率服务。改 `Wants=`，后完全移除（脚本不依赖 PPD）。
5. **`ExecStartPre` 冗余** — 多了个 init 步骤，daemon 首轮已做相同事。
6. **`/etc/` 屏蔽包更新** — thinkfan override.conf 迁到 `/etc/` 后包更新不再生效。删除副本回退到 `/usr/lib/`。

---

## 7. 后续维护: 2026-06-12 开机修复

### 故障现象
开机后 `systemctl --failed` 显示 `thinkfan.service` 启动失败。

### 原因分析

| 问题 | 根因 |
|------|------|
| thinkpad_hwmon 路径漂移 | 配置写死 `hwmon5`，重启后变为 `hwmon4` |
| NVMe hwmon 路径漂移 | 配置写死 `hwmon4`，重启后变为 `hwmon5` |
| `fan_control=1` 未生效 | `modprobe.d` 配置存在但模块在配置前已加载 |

### 修复操作

```bash
# 1. 修正 thinkpad_hwmon 路径 (hwmon5 → hwmon4)
# 2. 修正 NVMe 路径，改用 /sys/class/nvme/nvme0/ 更稳定
# 3. 重载 thinkpad_acpi 模块使 fan_control=1 生效
pkexec sh -c '
  sed -i "s/hwmon5/hwmon4/g" /etc/thinkfan.conf
  sed -i "s|/sys/devices/pci0000:00/0000:00:06.0/0000:04:00.0/nvme/nvme0/hwmon4/temp1_input|/sys/class/nvme/nvme0/hwmon5/temp1_input|" /etc/thinkfan.conf
  modprobe -r thinkpad_acpi && modprobe thinkpad_acpi
  systemctl restart thinkfan
'
```

### 教训
hwmon 编号 (`hwmon4`/`hwmon5`) 在每次重启后可能变化，属于内核设备枚举顺序不确定性。`/sys/class/` 下的 symlink 相对稳定，但 NVMe 的 hwmon 子目录编号仍会变。更彻底的方案是让 thinkfan 用 `sensors` 命令或 `-b0` 偏置模式规避路径依赖，但当前修复已足够。

### 验证
```bash
systemctl is-active thinkfan   # → active
systemctl --failed             # → 0 loaded units listed
```

---

## 8. 后续维护: 2026-06-12 开机全面审查

### 触发
修复 thinkfan 后，审查自本次开机所有日志，发现两个额外问题。

### 问题 1: MMIO RAPL 域遗漏

#### 现象
`ppd-power-tune.sh` 的 `find_domains` glob 模式 `intel-rapl*/intel-rapl*` 匹配不到 MMIO 域：
```
/sys/class/powercap/intel-rapl-mmio/intel-rapl-mmio:0 → package-0
```
实际路径格式为 `intel-rapl-mmio/intel-rapl-mmio:0`，glob 模式少了一层 `-mmio`。

#### 后果
MSR 侧写入 75W，但实际功率控制器在 MMIO 侧，仍锁在 65W。性能释放未生效。

#### 修复
glob 追加 `/sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio*`：
```bash
for d in /sys/class/powercap/intel-rapl*/intel-rapl* /sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio*; do
```

### 问题 2: `custom` profile 无兜底

#### 现象
GNOME 扩展设了 `custom` profile，`platform_profile` 返回 `custom`，脚本 `case *)` 只 `return 1` 不写入任何值。

#### 后果
功率值停留在上次已知 profile 的值，不更新。若开机时首次读到 `custom`，则完全不写入。

#### 修复
引入 `LAST_PROFILE` 变量，遇到未知 profile 时回退到上次已知值：
```bash
LAST_PROFILE=""
set_limits() {
    ...
    *)
        if [ -n "$LAST_PROFILE" ]; then
            echo "WARNING: unknown profile '$profile', keeping last known ($LAST_PROFILE)" >&2
            set_limits "$LAST_PROFILE"
        else
            echo "WARNING: unknown profile '$profile', no last known to fallback" >&2
        fi
        return 1 ;;
    esac
    LAST_PROFILE="$profile"
    ...
}
```

### 修复后验证

| 检查项 | 结果 |
|--------|------|
| MSR package-0 PL1/PL2 | 75W / 110W ✅ |
| MMIO package-0 PL1/PL2 | 75W / 110W ✅ |
| PSYS PL1/PL2 | 80W / 130W ✅ |
| `custom` profile 回退 | 保持上次已知值 ✅ |
| thinkfan 运行状态 | active ✅ |
| 无失败服务 | 0 loaded ✅ |

### 最终脚本
```bash
#!/usr/bin/env bash
set -uo pipefail

PROFILE="/sys/firmware/acpi/platform_profile"
NVME_PS="/sys/module/nvme_core/parameters/default_ps_max_latency_us"
ASPM_POLICY="/sys/module/pcie_aspm/parameters/policy"
NVME_SCHED="/sys/block/nvme0n1/queue/scheduler"
VM_DIRTY="/proc/sys/vm/dirty_ratio"
VM_DIRTY_BG="/proc/sys/vm/dirty_background_ratio"
VM_CACHE="/proc/sys/vm/vfs_cache_pressure"

PKG_DOMAINS=()
PSYS_DOMAINS=()
for d in /sys/class/powercap/intel-rapl*/intel-rapl* /sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio*; do
    [ -f "$d/name" ] || continue
    case "$(cat "$d/name")" in
        package-0) PKG_DOMAINS+=("$d") ;;
        psys)      PSYS_DOMAINS+=("$d") ;;
    esac
done

if [ "${#PKG_DOMAINS[@]}" -eq 0 ]; then
    echo "ERROR: no package-0 RAPL domain found. Check kernel/powercap support." >&2
    exit 1
fi
if [ "${#PSYS_DOMAINS[@]}" -eq 0 ]; then
    echo "WARNING: no psys RAPL domain found. Platform limits unchanged." >&2
fi

LAST_PROFILE=""
set_limits() {
    local profile="$1"
    local pkg_pl1 pkg_pl2 psys_pl1 psys_pl2 gt0_min gt1_min nvme_lat aspm
    local dirty_ratio dirty_bg cache_pressure
    case "$profile" in
        performance)
            pkg_pl1=75000000; pkg_pl2=110000000
            psys_pl1=80000000; psys_pl2=130000000
            gt0_min=700; gt1_min=450
            nvme_lat=0; aspm=performance
            dirty_ratio=10; dirty_bg=5; cache_pressure=50 ;;
        balanced)
            pkg_pl1=65000000; pkg_pl2=85000000
            psys_pl1=70000000; psys_pl2=95000000
            gt0_min=650; gt1_min=400
            nvme_lat=100000; aspm=powersave
            dirty_ratio=15; dirty_bg=7; cache_pressure=75 ;;
        low-power)
            pkg_pl1=20000000; pkg_pl2=35000000
            psys_pl1=25000000; psys_pl2=40000000
            gt0_min=100; gt1_min=100
            nvme_lat=500000; aspm=powersupersave
            dirty_ratio=20; dirty_bg=10; cache_pressure=100 ;;
        *)
            if [ -n "$LAST_PROFILE" ]; then
                echo "WARNING: unknown profile '$profile', keeping last known ($LAST_PROFILE)" >&2
                set_limits "$LAST_PROFILE"
            else
                echo "WARNING: unknown profile '$profile', no last known to fallback" >&2
            fi
            return 1 ;;
    esac
    LAST_PROFILE="$profile"
    for d in "${PKG_DOMAINS[@]}"; do
        echo "$pkg_pl1" > "$d/constraint_0_power_limit_uw" 2>/dev/null || echo "WARNING: failed to write $d/constraint_0" >&2
        echo "$pkg_pl2" > "$d/constraint_1_power_limit_uw" 2>/dev/null || echo "WARNING: failed to write $d/constraint_1" >&2
    done
    for d in "${PSYS_DOMAINS[@]}"; do
        echo "$psys_pl1" > "$d/constraint_0_power_limit_uw" 2>/dev/null || echo "WARNING: failed to write $d/constraint_0" >&2
        echo "$psys_pl2" > "$d/constraint_1_power_limit_uw" 2>/dev/null || echo "WARNING: failed to write $d/constraint_1" >&2
    done
    echo "$gt0_min" > /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq 2>/dev/null || echo "WARNING: failed to set GT0 min_freq" >&2
    echo "$gt1_min" > /sys/class/drm/card0/device/tile0/gt1/freq0/min_freq 2>/dev/null || echo "WARNING: failed to set GT1 min_freq" >&2
    echo "$nvme_lat" > "$NVME_PS" 2>/dev/null || echo "WARNING: failed to set NVME power saving" >&2
    echo "$aspm" > "$ASPM_POLICY" 2>/dev/null || echo "WARNING: failed to set ASPM policy" >&2
    echo "$dirty_ratio" > "$VM_DIRTY" 2>/dev/null || echo "WARNING: failed to set dirty_ratio" >&2
    echo "$dirty_bg" > "$VM_DIRTY_BG" 2>/dev/null || echo "WARNING: failed to set dirty_background_ratio" >&2
    echo "$cache_pressure" > "$VM_CACHE" 2>/dev/null || echo "WARNING: failed to set vfs_cache_pressure" >&2
    echo "Applied power limits for profile: $profile"
}

set_sched() {
    echo "none" > "$NVME_SCHED" 2>/dev/null || echo "WARNING: failed to set NVMe scheduler" >&2
}

case "${1:-}" in
    daemon)
        set_sched
        set_limits "$(cat "$PROFILE" 2>/dev/null || echo "unknown")"
        while true; do sleep 10; set_limits "$(cat "$PROFILE" 2>/dev/null || echo "unknown")"; done
        ;;
    apply)  set_limits "$(cat "$PROFILE")" ;;
    *)      echo "Usage: $0 {apply|daemon}"; exit 1 ;;
esac
```

### 踩坑记录（追加）

| # | 坑 | 根因 | 修复 |
|---|-----|------|------|
| 7 | MMIO RAPL 未写入 | glob 模式 `intel-rapl*/intel-rapl*` 不匹配 `intel-rapl-mmio` | 追加第二个 glob 路径 |
| 8 | `custom` profile 静默跳过 | `case *)` 只 return，不写入 | 引入 `LAST_PROFILE` 回退 |

---

## 9. 后续维护: 2026-06-12 开机二次修复 — hwmon 编号漂移根治

### 故障现象
第二次开机后 `thinkfan.service` 再次 failed，hwmon 编号与上次修复后的配置不匹配。

### 原因分析
hwmon 编号 (`hwmonN`) 由内核设备枚举顺序决定，每次重启可能变化：

| 设备 | 上次修复后 | 本次开机 | 变化 |
|------|-----------|---------|------|
| thinkpad 传感器 | `hwmon4` | `hwmon5` | +1 |
| NVMe 传感器 | `hwmon5` | `hwmon4` | -1 |
| coretemp | `hwmon7` | `hwmon7` | 不变 |

### 根治方案

将 `/etc/thinkfan.conf` 从**硬编码 hwmon 路径**改为 **name-based 匹配**，按 `name` 文件内容搜索设备：

```yaml
sensors:
  - hwmon: /sys/class/hwmon
    name: coretemp
    indices: [1]

  - hwmon: /sys/class/hwmon
    name: thinkpad
    indices: [1, 3, 4, 5, 6, 7]

  - hwmon: /sys/class/hwmon
    name: nvme
    indices: [1]
```

thinkfan 在 `/sys/class/hwmon/` 下搜索 `name` 文件内容匹配的设备，不依赖 `hwmonN` 编号。

### 验证

```bash
systemctl is-active thinkfan   # → active
systemctl --failed             # → 0 loaded units listed
```

### 教训

| # | 教训 | 说明 |
|---|------|------|
| 11 | **hwmon 编号每次重启都可能变** | 内核设备枚举顺序不确定，`hwmonN` 不是稳定标识符 |
| 12 | **用 name 而非编号引用 hwmon** | `/sys/class/hwmon/hwmon*/name` 提供稳定名称，thinkfan 原生支持 `name:` 匹配 |
| 13 | **临时修复要标记为临时** | 上次修复改 `hwmon5→hwmon4` 是临时方案，应直接上 name-based 匹配 |

### 最终文件清单（更新）

```
/etc/thinkfan.conf                      (14行, name-based 匹配, 彻底解决漂移)
```

---

## 10. 后续维护: 2026-06-12 永久修复 — fan_control 打入 initramfs

### 故障现象
`thinkfan.service` 启动失败，`fan_control=1` 参数未生效。

### 原因分析
`thinkpad_acpi` 模块在 initramfs 阶段就已加载，此时 `/etc/modprobe.d/` 尚未挂载，`fan_control=1` 配置未被读取。模块加载后参数固定为 `N`，后续 modprobe.d 配置不再生效。

### 修复操作

```bash
# 1. 将 thinkpad_acpi 加入 initramfs 模块列表
# 2. 重建 initramfs
pkexec sh -c '
  sed -i "s/^MODULES=()/MODULES=(thinkpad_acpi)/" /etc/mkinitcpio.conf
  mkinitcpio -P
'
```

### 原理
`MODULES=(thinkpad_acpi)` 让 initramfs 在早期阶段加载 `thinkpad_acpi` 模块，此时 `/etc/modprobe.d/99-thinkfan.conf` 中的 `options thinkpad_acpi fan_control=1` 被正确读取并应用。此后 udev 不会重复加载，参数永久生效。

### 验证
```bash
systemctl is-active thinkfan   # → active
systemctl --failed             # → 0 loaded units listed
cat /sys/module/thinkpad_acpi/parameters/fan_control  # → Y
```

### 教训

| # | 教训 | 说明 |
|---|------|------|
| 14 | **模块参数不生效先查加载时机** | modprobe.d 存在不代表参数生效，模块可能在 initramfs 阶段已加载 |
| 15 | **`MODULES=` 是 initramfs 阶段加载模块的标准方式** | 将模块加入 mkinitcpio.conf 的 MODULES 数组，确保早期加载时携带参数 |
| 16 | **重建 initramfs 后需重启验证** | `mkinitcpio -P` 重建后，当前会话仍需 `modprobe -r` 重载，下次启动自动生效 |

### 最终文件清单（更新）

```
/etc/mkinitcpio.conf                    (MODULES=(thinkpad_acpi), 永久修复)
```

---

## 附录: 操作日志 (2026-06-11)

本机通过 `pkexec` 提权（sudo 被 pam_faillock 锁定）。通用环境替换为 `sudo` 即可。

除上述核心改动外，还包括：

- **NTP 同步**: `timedatectl set-ntp true`
- **swappiness=1**: 30GB RAM + zram 几乎不需要换页
- **pacman 缓存**: 删除 11 个中断下载残留；`paccache.timer` 已启用
- **journald 500M**: 追加 `SystemMaxUse=500M` 到 `/etc/systemd/journald.conf`
- **/tmp 清理**: 移除 ppd-sync 残留脚本
- **btrfs device scan**: 修复 `devid 1 path MISSING`
- **ppd-sync 残留 symlink**: 删除

---

## 附录: 滚动更新防护 (2026-06-12)

### 风险矩阵

| 文件 | 包拥有 | 风险 | 防护 |
|------|--------|------|------|
| `/usr/local/bin/ppd-power-tune.sh` | 否 | 🟢 无 | 非包管理，更新不覆盖 |
| `/etc/systemd/system/ppd-profile-monitor.service` | 否 | 🟢 无 | 非包管理，更新不覆盖 |
| `/etc/thinkfan.conf` | 否 | 🟢 无 | 非包管理，更新不覆盖；name-based 匹配根治 hwmon 漂移 |
| `/etc/modprobe.d/99-thinkfan.conf` | 否 | 🟢 无 | 内容与包自带一致 |
| `/etc/sysctl.d/99-swappiness.conf` | 否 | 🟢 无 | 非包管理，更新不覆盖 |
| `/etc/systemd/journald.conf` | systemd | 🟢 低 | pacman hook 自动追加 `SystemMaxUse=500M` |
| `/etc/mkinitcpio.conf` | mkinitcpio | 🟢 低 | pacman hook 自动保持 `MODULES=(thinkpad_acpi)` |

### pacman hook

`/etc/pacman.d/hooks/merge-journald-conf.hook`:
```ini
[Trigger]
Operation = Upgrade
Type = Package
Target = systemd

[Action]
Description = Merging SystemMaxUse=500M into /etc/systemd/journald.conf...
When = PostTransaction
Exec = /bin/sh -c 'grep -q "^SystemMaxUse=500M" /etc/systemd/journald.conf || echo "SystemMaxUse=500M" >> /etc/systemd/journald.conf'
```

`/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook`:
```ini
[Trigger]
Operation = Upgrade
Type = Package
Target = mkinitcpio

[Action]
Description = Ensuring MODULES=(thinkpad_acpi) in /etc/mkinitcpio.conf...
When = PostTransaction
Exec = /bin/sh -c 'grep -q "^MODULES=(thinkpad_acpi)" /etc/mkinitcpio.conf || sed -i "s/^MODULES=()/MODULES=(thinkpad_acpi)/" /etc/mkinitcpio.conf'
```

---

## 11. 后续维护: 2026-06-12 MC 负载实测验证

### 场景
MC (Minecraft, PrismLauncher, 分配 4GB 堆) 运行中，performance 模式下监测 2 分钟。

### 监测数据

| 时间 | MC CPU% | Package 温度 | 最高核心 | 风扇 (thinkfan) |
|------|---------|-------------|---------|----------------|
| 09:18 | 115% | 48°C | 58°C | level 2~4 |
| 09:19 | 127→157% | 68→96°C | 94°C | level 6→7 |
| 09:20 | 166→176% | 86°C 稳定 | 96°C | level 7 (3015 RPM) |

### 结论
- 75W PL1 下 Package 稳定 86°C，峰值核心 96°C，已接近 TJmax 100°C
- **不建议再提升 PL1**，当前已是热边界
- thinkfan 工作正常，`sensors` 显示 0 RPM 是读取接口不一致（读到 `acpi_fan` 而非 `thinkpad` hwmon）
- 已添加 `fan` 命令别名到 `~/.zshrc`，直接读取 thinkpad hwmon 获取准确转速

---

## 12. 后续维护: 2026-06-12 GPU 最低频率联动

### 背景
GPU 当前使用 Xe 驱动，`power_profile` 仅支持 `power_saving`（不可切换），但 `min_freq` 可写。通过按 PPD 模式调整 GPU 最低频率，减少频率跳变延迟，提升图形响应。

### 方案
在 `ppd-power-tune.sh` 的 `set_limits()` 中追加 GPU `min_freq` 写入：

| 模式 | GT0 min_freq (主渲染) | GT1 min_freq (媒体) | 说明 |
|------|----------------------|---------------------|------|
| performance | **700 MHz** (rp0=2450) | **450 MHz** (rp0=1200) | 减少频率爬升延迟，游戏/图形负载响应更快 |
| balanced | **650 MHz** (rpe=700) | **400 MHz** (rpe=450) | 保持效率，微幅提升 |
| low-power | **100 MHz** (rpn=100) | **100 MHz** (rpn=100) | 最低频率，最大限度省电 |

### 验证
```bash
# performance → GT0=700 GT1=450
# balanced    → GT0=650 GT1=400
# low-power   → GT0=100 GT1=100
cat /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq
cat /sys/class/drm/card0/device/tile0/gt1/freq0/min_freq
```

### 注意事项
- `power_profile` 不可写（Xe 驱动限制），`min_freq` 是当前唯一可调的 GPU 参数
- 频率上限 (`max_freq`) 保持默认，由硬件自动 boost 到 rp0
- 写入失败仅 warning，不影响 RAPL 功率控制主功能

---

## 13. 已撤销: 屏幕亮度 + 键盘背光联动 (2026-06-12)

曾尝试将屏幕亮度和键盘背光纳入 PPD 联动，但用户反馈需要随时手动调节，联动会覆盖手动操作。已从脚本中移除。

保留的联动项：功率墙 (RAPL) + GPU min_freq。屏幕亮度和键盘背光保持手动控制。

---

## 14. 后续维护: 2026-06-12 NVMe 延迟优化 + PCIe ASPM（已纳入 PPD 联动）

已整合到 `ppd-power-tune.sh`，跟随 PPD 模式自动切换，无需重启：

| 模式 | NVMe 省电延迟 | PCIe ASPM 策略 | 说明 |
|------|-------------|---------------|------|
| performance | **0** (禁用) | **performance** | 最低延迟，适合游戏/编译 |
| balanced | **100000** (默认) | **powersave** | 日常平衡 |
| low-power | **500000** (保守) | **powersupersave** | 最大限度省电 |

先前建立的 `/etc/modprobe.d/99-nvme-performance.conf` 和 GRUB 命令行 `pcie_aspm.policy=performance` 已移除，统一由脚本管理。

---

## 15. 后续维护: 2026-06-13 VM 脏页阈值 + 缓存压力 + I/O 调度器

### 背景
30GB 内存 + zram 环境下，默认 Linux VM 参数偏向服务端（容忍大量脏页），对桌面交互响应不友好。NVMe 使用 kyber 调度器引入不必要的内核调度开销。

### 方案
纳入 PPD 联动，写入 `ppd-power-tune.sh`：

| 模式 | dirty_ratio | dirty_background_ratio | vfs_cache_pressure | 设计意图 |
|------|------------|----------------------|-------------------|---------|
| performance | **10%** | **5%** | **50** | 低写回延迟，多缓存文件元数据 |
| balanced | **15%** | **7%** | **75** | 日常平衡 |
| low-power | **20%** | **10%** | **100** | 默认值，容忍更多脏页省电 |

I/O 调度器固定为 `none`（NVMe 零调度开销），daemon 启动时一次性写入。

### 验证
```bash
cat /proc/sys/vm/dirty_ratio           # → 10 (performance)
cat /proc/sys/vm/dirty_background_ratio # → 5
cat /proc/sys/vm/vfs_cache_pressure     # → 50
cat /sys/block/nvme0n1/queue/scheduler  # → [none]
```

---

## 16. 后续维护: 2026-06-26 WiFi Power Save 纳入 PPD 联动

### 背景
Intel CNVi WiFi (Panther Lake PCH) 默认开启 802.11 省电模式，会增加 1-3ms 延迟抖动，对 SSH/游戏不利。应根据 PPD 模式自动切换。

### 方案
纳入 PPD 联动，写入 `ppd-power-tune.sh`：

| 模式 | WiFi power_save | 说明 |
|------|----------------|------|
| performance | **off** | 最低延迟，适合游戏/SSH |
| balanced | **on** | 省电，日常使用 |
| low-power | **on** | 最大省电 |

同时创建 NetworkManager dispatcher 脚本 `/etc/NetworkManager/dispatcher.d/90-wifi-powersave`，在 WiFi 重连时根据当前 PPD 模式立即设置 power_save，避免重启/daemon 轮询间隔内出现空洞。

### 文件

**`/usr/local/bin/ppd-power-tune.sh`** — `set_limits()` 增加：
```bash
wifi_ps=off    # performance
wifi_ps=on     # balanced / low-power
iw dev "$WIFI_IFACE" set power_save "$wifi_ps"
```

WiFi 接口自动检测（首个 wl* 设备）：
```bash
for i in /sys/class/net/wl*/uevent; do
    WIFI_IFACE=$(basename "$(dirname "$i")")
    break
done
```

**`/etc/NetworkManager/dispatcher.d/90-wifi-powersave`**：
```bash
#!/usr/bin/env bash
set -euo pipefail
IFACE="$1"; ACTION="$2"
[[ "$IFACE" == wl* ]] || exit 0
[[ "$ACTION" == up ]] || exit 0
PROFILE=$(cat /sys/firmware/acpi/platform_profile 2>/dev/null || echo "balanced")
case "$PROFILE" in
    performance) iw dev "$IFACE" set power_save off ;;
    *)           iw dev "$IFACE" set power_save on ;;
esac
```

### 验证
```bash
powerprofilesctl set performance && sleep 12
iw dev wlp0s20f3 get power_save   # → Power save: off

powerprofilesctl set balanced && sleep 12
iw dev wlp0s20f3 get power_save   # → Power save: on
```

---

## 17. 后续维护: 2026-06-26 NVMe 队列优化 + irqbalance

### NVMe read_ahead_kb 128 → 4096
NVMe 延迟极低（~0.1ms），128 KB 预读是为 HDD 设计的保守值。4096 KB 可提升大文件顺序读性能（游戏加载、编译、视频编辑）。持久化在 `ppd-power-tune.sh` 的 `set_sched()` 中。

### NVMe nomerges 0 → 2
NVMe 无需内核 IO 合并，`nomerges=2`（全部禁用合并）减少 CPU 开销。同样持久化在 `set_sched()` 中。

### irqbalance
16 核系统启用中断均衡分布，减少单核 IRQ 压力。`systemctl enable --now irqbalance`。

### set_sched() 完整代码
```bash
set_sched() {
    echo "none" > "$NVME_SCHED" 2>/dev/null || echo "WARNING: failed to set NVMe scheduler" >&2
    echo "4096" > /sys/block/nvme0n1/queue/read_ahead_kb 2>/dev/null || echo "WARNING: failed to set read_ahead" >&2
    echo "2" > /sys/block/nvme0n1/queue/nomerges 2>/dev/null || echo "WARNING: failed to set nomerges" >&2
}
```

### 验证
```bash
cat /sys/block/nvme0n1/queue/read_ahead_kb  # → 4096
cat /sys/block/nvme0n1/queue/nomerges        # → 2
cat /sys/block/nvme0n1/queue/scheduler        # → [none]
systemctl is-active irqbalance                # → active
```

---

## 18. 后续维护: 2026-06-26 zram 缩容 30.8GB → 16GB

### 背景
zram 配置为 `zram-size = ram`（100% RAM = 30.8 GB），但实际从未被使用（0 字节数据），浪费约 15 GB 内存给 zram 压缩窗口而非文件缓存。

### 方案
修改 `/etc/systemd/zram-generator.conf`：
```ini
[zram0]
zram-size = 16384
compression-algorithm = zstd
```

16 GB（~50% RAM）足以应对极端内存压力，剩余内存归还给内核文件缓存。

### 执行
```bash
swapoff /dev/zram0
sed -i 's/^zram-size = ram/zram-size = 16384/' /etc/systemd/zram-generator.conf
systemctl restart systemd-zram-setup@zram0.service
# swapon 由 dev-zram0.swap 自动触发
```

### 验证
```bash
free -h | grep Swap   # → 15Gi (was 30Gi)
zramctl                # → DISKSIZE=16G
```

