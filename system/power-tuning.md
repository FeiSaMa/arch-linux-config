# 电源与散热调优

电源和散热的详细调优记录见 `hardware/` 目录：

| 文件 | 说明 |
|------|------|
| `hardware/performance-unlock.md` | PPD 联动、RAPL 功率墙、GPU 频率、thinkfan 曲线等完整操作手册 |
| `hardware/changelog.md` | 11 轮迭代摘要 + 检查清单 |
| `hardware/hardware-specs.md` | 硬件配置清单（TDP、PL1/PL2 等） |

## 当前配置参数

| 项 | 值 |
|----|-----|
| 电源管理 | power-profiles-daemon（3 档: performance / balanced / low-power） |
| PL1 (performance) | 75W |
| PL2 (performance) | 110W |
| GT0 min_freq (performance) | 700 MHz |
| NVMe 延迟 (performance) | 0 µs |
| PCIe ASPM (performance) | performance |
| VM dirty_ratio (performance) | 10% |
| 风扇 | thinkfan + name-based hwmon 匹配 |
| Swap | zram-generator（30.8G, zstd） |
| swappiness | 1 |
| journald 上限 | 500M |
