#!/usr/bin/env bash
set -uo pipefail

PROFILE="/sys/firmware/acpi/platform_profile"
NVME_PS="/sys/module/nvme_core/parameters/default_ps_max_latency_us"
ASPM_POLICY="/sys/module/pcie_aspm/parameters/policy"
NVME_SCHED="/sys/block/nvme0n1/queue/scheduler"
VM_DIRTY="/proc/sys/vm/dirty_ratio"
VM_DIRTY_BG="/proc/sys/vm/dirty_background_ratio"
VM_CACHE="/proc/sys/vm/vfs_cache_pressure"

WIFI_IFACE=""
for i in /sys/class/net/wl*/uevent; do
    WIFI_IFACE=$(basename "$(dirname "$i")")
    break
done

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
    local dirty_ratio dirty_bg cache_pressure wifi_ps
    case "$profile" in
        performance)
            pkg_pl1=75000000; pkg_pl2=110000000
            psys_pl1=80000000; psys_pl2=130000000
            gt0_min=700; gt1_min=450
            nvme_lat=0; aspm=performance
            dirty_ratio=10; dirty_bg=5; cache_pressure=50
            wifi_ps=off ;;
        balanced)
            pkg_pl1=65000000; pkg_pl2=85000000
            psys_pl1=70000000; psys_pl2=95000000
            gt0_min=650; gt1_min=400
            nvme_lat=100000; aspm=powersave
            dirty_ratio=15; dirty_bg=7; cache_pressure=75
            wifi_ps=on ;;
        low-power)
            pkg_pl1=20000000; pkg_pl2=35000000
            psys_pl1=25000000; psys_pl2=40000000
            gt0_min=100; gt1_min=100
            nvme_lat=500000; aspm=powersupersave
            dirty_ratio=20; dirty_bg=10; cache_pressure=100
            wifi_ps=on ;;
        *)
            if [ -n "$LAST_PROFILE" ]; then
                echo "WARNING: unknown profile '"$profile"', keeping last known ($LAST_PROFILE)" >&2
                set_limits "$LAST_PROFILE"
            else
                echo "WARNING: unknown profile '"$profile"', no last known to fallback" >&2
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
    if [ -n "$WIFI_IFACE" ]; then
        iw dev "$WIFI_IFACE" set power_save "$wifi_ps" 2>/dev/null || echo "WARNING: failed to set WiFi power_save" >&2
    fi
    echo "Applied power limits for profile: $profile"
}

set_sched() {
    echo "none" > "$NVME_SCHED" 2>/dev/null || echo "WARNING: failed to set NVMe scheduler" >&2
}

case "${1:-}" in
    daemon)
        set_sched
        start_ts=$SECONDS
        while [ $((SECONDS - start_ts)) -lt 30 ]; do
            profile=$(cat "$PROFILE" 2>/dev/null || echo "")
            if [ -n "$profile" ]; then break; fi
            sleep 2
        done
        set_limits "${profile:-unknown}"
        last_profile="$profile"
        counter=0
        while true; do
            sleep 10
            counter=$((counter + 1))
            profile=$(cat "$PROFILE" 2>/dev/null || echo "unknown")
            if [ "$profile" != "$last_profile" ] || [ $((counter % 30)) -eq 0 ]; then
                set_limits "$profile"
                last_profile="$profile"
            fi
        done
        ;;
    apply)  set_limits "$(cat "$PROFILE")" ;;
    *)      echo "Usage: $0 {apply|daemon}"; exit 1 ;;
esac
