# mitigations=off 调优

> 日期: 2026-06-13
> 主机: ThinkPad T14 Gen 7 / Arch Linux / Intel Core Ultra 7 356H / 内核 7.0.11-zen

---

## 评估

关闭 CPU 安全漏洞缓解（Meltdown / Spectre 等），用安全换性能。

### 收益

- 系统调用 / 上下文切换快 **5-15%**（理论值，实际因 CPU 大部分漏洞已硬件修复，感知有限）
- 编译、内核加载、IO 密集型任务有微小提升
- 零成本，一行 GRUB 搞定

> **实测说明：** Panther Lake 的 `/sys/devices/system/cpu/vulnerabilities/` 中多数条目为 `Not affected`（硬件级修复），只有 Spectre v1/v2 类受 `mitigations=off` 影响。Intel 官方数据称这类缓解在现代 CPU 上的性能开销 <3%。实际桌面使用中差异不易察觉。

### 风险

- 暴露于已知 CPU 漏洞（但笔记本个人使用，被攻击概率极低）
- 某些内核的 CPU 调频 / C-state 行为可能有变化
- 重启生效

---

## 实施

```bash
# 1. 备份并修改 GRUB 命令行
cp /etc/default/grub /etc/default/grub.bak
sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/&mitigations=off /' /etc/default/grub

# 2. 重建 GRUB 配置
grub-mkconfig -o /boot/grub/grub.cfg

# 3. 重启生效
reboot
```

### 修改后内核命令行

```
loglevel=5 zswap.enabled=0 nmi_watchdog=0 mitigations=off
```

---

## 验证

重启后检查生效状态：

```bash
cat /proc/cmdline
# 应包含 mitigations=off
```

---

## 回滚

```bash
cp /etc/default/grub.bak /etc/default/grub
grub-mkconfig -o /boot/grub/grub.cfg
reboot
```

---

## 参考

- [Arch Wiki: Kernel module — Disabling mitigations](https://wiki.archlinux.org/title/Kernel_module#Disabling_mitigations)
- [Meltdown/Spectre 漏洞缓解说明](https://www.kernel.org/doc/html/latest/admin-guide/hw-vuln/index.html)
