# ThinkPad 性能调优记录

ThinkPad / Arch Linux / Intel Core Ultra 7 356H 的性能调优全过程记录。

## 文档清单

| 文件 | 说明 |
|------|------|
| `thinkpad-performance-unlock.md` | **操作手册** — 含完整脚本、各轮部署命令、回滚方案、维护指南 |
| `final-draft-thinking-process.md` | **思考记录** — 16 轮迭代全过程的决策链、问题排查、经验教训 |
| `improving-loop.md` | **变更日志** — 按轮次记录变更摘要、检查清单 |
| `hardware-specs.md` | 硬件配置清单（CPU/GPU/内存/存储/网络/电池） |
| `stress-test-report.md` | stress-ng 10 分钟压力测试分析报告 |
| `stress-test.log` | 压力测试原始采样数据（60 次，每 10s） |
| `mitigations-off.md` | `mitigations=off` 关闭 CPU 安全缓解的操作记录 |
| `LICENSE` | MIT 许可证 |

## 调优内容

- **功率墙动态切换** — GNOME 右上角切 PPD 模式，PL1/PL2 自动跟随
- **GPU 最低频率联动** — 按场景调整渲染/媒体频率，减少跳变延迟
- **NVMe 延迟优化** — 禁用 NVMe 电源状态，降低存储延迟
- **PCIe ASPM 联动** — 按模式切换链路电源策略
- **VM 脏页阈值 + 缓存压力联动** — 按模式降低写回延迟，保留文件元数据缓存
- **I/O 调度器 none** — NVMe 零调度开销
- **thinkfan 激进曲线** — name-based hwmon 匹配，根治编号漂移
- **Caffeine 联动** — 切 performance 模式时自动开 Caffeine 防休眠
- **滚动更新防护** — pacman hook 自动修复包更新覆盖的配置

## 快速部署

```bash
git clone https://github.com/FeiSaMa/thinkpad-tune.git
cd thinkpad-tune
# 按 thinkpad-performance-unlock.md 中的命令操作
```
