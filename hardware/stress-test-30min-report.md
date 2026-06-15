# Stress Test Report — 2026-06-15 (30 min)

## 测试条件

| 项 | 值 |
|------|--------|
| CPU | Intel Core Ultra 7 356H (16 核) |
| 模式 | performance (PL1=75W, PL2=110W) |
| 工具 | stress-ng --cpu 16 --vm 4 --vm-bytes 50% |
| 时长 | 30 分钟 (1800s) |
| 采样 | 每 10s 一次，共 179 次 |
| 内核 | 7.0.12-zen1-1-zen |
| 内存负载 | 12.36 GB / 24.72 GB (50%) |

## 温度

| 统计 | 值 |
|------|-----|
| 初始 (warm-up) | 83°C |
| 峰值 | **97°C** |
| 稳定 | 96~97°C |
| 平均 | 96.0°C |

TJmax=100°C，持续满载留有 ~3°C 余量。与前次 10 分钟测试 (97°C) 一致，散热曲线稳定。

## CPU 频率

| 统计 | 值 |
|------|-----|
| 稳态平均 | **2903 MHz** |
| 最高 (瞬时) | 3303 MHz |
| 最低 | 2487 MHz |
| 平均 (全部 179 样本) | 2903 MHz |

频率波动在 2487~3303 MHz 之间，属 75W PL1 功率墙下 16 核正常波动，无异常跌落。

## GPU 频率

| 统计 | 值 |
|------|-----|
| 全程 | **700 MHz** |

稳定锁定在 min_freq 地板值 (700 MHz)，零波动，零 throttle。

## 风扇

| 统计 | 值 |
|------|-----|
| 满载转速 (sensors) | ~3700-3800 RPM |
| 控制方式 | thinkfan (激进曲线, manual control) |

脚本风扇采样使用 acpi_fan 接口 (恒为 0)，实际风扇由 thinkpad_acpi 驱动 (hwmon4)，当前 idle 转速 3762 RPM，确认 thinkfan 正常运行。

## 降频 (Throttling) 分析

**零降频** — 179 个采样中 throttle=0%（无任何核心低于 1900 MHz base frequency）。

对比前次 10 分钟测试 (同样 0 throttle)，30 分钟持续满载验证了：
1. 75W PL1 功率墙提供足够持续功耗，16 核稳定 ~2.9 GHz
2. thinkfan 激进曲线有效控制温度在 97°C 以下
3. VRM 未触发 PROCHOT

## 调优参数验证

| 参数 | 前值 | 后值 | 状态 |
|------|------|------|------|
| PL1 (MSR) | 75W | 75W | OK |
| PL1 (MMIO) | 75W | 75W | OK |
| fan_control | Y | Y | OK |
| GPU min_freq | 700 | 700 | OK |
| NVMe latency | 0 | 0 | OK |
| ASPM policy | performance | performance | OK |
| dirty_ratio | 10 | 10 | OK |
| thinkfan | active | active | OK |
| ppd-profile-monitor | active | active | OK |

全部调优参数保持不变。

## 结论

**30 分钟满载测试通过。** 硬件调优稳定可靠：

- 温度峰值 97°C，距 TJmax (100°C) 3°C 余量，与 10 分钟测试一致
- 零降频 (0 throttle)，16 核稳态 2.9 GHz @ 75W PL1
- GPU 锁定 700 MHz，无波动
- thinkfan 激进曲线有效，温度可控
- 所有调优参数在测试前后保持一致
- 服务 (thinkfan + ppd-profile-monitor) 健康

## 原始日志

`hardware/stress-test-30min.log`
