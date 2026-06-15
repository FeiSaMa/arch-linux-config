# 硬件配置

## 主机

| 项 | 值 |
|------|--------|
| 型号 | Lenovo ThinkPad T14 Gen 7 |
| BIOS | N4TET17W (1.02), 2026-03-09 |

## CPU

| 项 | 值 |
|------|--------|
| 型号 | Intel Core Ultra 7 356H |
| 架构 | Panther Lake |
| 核心/线程 | 16 核 |
| 基础 TDP | 28W |
| PL1 (性能模式) | **75W** |
| PL2 (性能模式) | **110W** |
| 最高单核频率 | 4.7 GHz |
| 多核稳态频率 | ~3.0 GHz (75W) |

## GPU

| 项 | 值 |
|------|--------|
| 型号 | Intel Panther Lake [Intel Graphics] |
| 驱动 | xe |
| 最高频率 (rp0) | 2450 MHz |
| min_freq (性能模式) | 700 MHz |
| min_freq (平衡模式) | 650 MHz |
| min_freq (省电模式) | 100 MHz |

## 内存

| 项 | 值 |
|------|--------|
| 容量 | 30 GiB (LPDDR5x LPCAMM2, 可更换) |
| 型号 | Samsung M561K2LC4EE1-CCUYD (8×4 GiB 子通道, 单 LPCAMM2 模组) |
| 速率 | 9600 MT/s (运行于 7467 MT/s, Panther Lake 平台限制) |
| 电压 | 0.5 V (LPDDR5x) |
| 支持最大容量 | 128 GiB (SMBIOS) |
| Swap | 30 GiB (zram, zstd) |

## 存储

| 项 | 值 |
|------|--------|
| 型号 | Samsung MZVL81T0HFLB-00BLL (PM9C1a) |
| 容量 | 953.9 GiB (NVMe) |
| 接口 | M.2 2280, PCIe 4.0 ×4 (16.0 GT/s) |

## 网络

| 类型 | 型号 |
|------|--------|
| 有线 | Intel I219-V (Ethernet) |
| 无线 | Intel BE211 Wi-Fi 7 320MHz (CNVr2, M.2 2230) |
| WWAN | Quectel EM05-CN 4G (M.2 3042, USB 3-6) |

## 电池

| 项 | 值 |
|------|--------|
| 型号 | 5B11M90172 |
| 设计容量 | 60 Wh |
| 当前容量 | 60 Wh (100%) |
| 循环次数 | 2 |

## 分区

| 分区 | 大小 | 格式 | 用途 |
|------|------|------|------|
| nvme0n1p1 | 200 MiB | vfat | Windows EFI |
| nvme0n1p2 | 16 MiB | - | MSR |
| nvme0n1p3 | 700 GiB | ntfs | Windows |
| nvme0n1p4 | 841 MiB | ntfs | Windows 恢复 |
| nvme0n1p5 | 477 MiB | vfat | Arch Linux EFI |
| nvme0n1p6 | 252 GiB | btrfs | Arch Linux `/` + `/home` |

## 软件

| 项 | 值 |
|------|--------|
| 系统 | Arch Linux |
| 内核 | 7.0.11-zen1-1-zen |
| 桌面 | GNOME |
| 功率管理 | power-profiles-daemon |
