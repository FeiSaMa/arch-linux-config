#!/usr/bin/env bash
set -uo pipefail

echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || true
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo powersave > "$cpu" 2>/dev/null || true
done

echo 0 > /sys/class/backlight/*/brightness 2>/dev/null || true

echo powersupersave > /sys/module/pcie_aspm/parameters/policy 2>/dev/null || true

echo 500000 > /sys/module/nvme_core/parameters/default_ps_max_latency_us 2>/dev/null || true

iw dev wlp0s20f3 set power_save on 2>/dev/null || true
