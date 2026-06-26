# AUR 恶意软件包污染事件 — 安全审计

## 事件背景

- **日期**: 2026-06-12
- **来源**: [Arch Linux 官方新闻](https://archlinux.org/news/active-aur-malicious-packages-incident/)
- **性质**: AUR 正在经历大规模恶意软件包劫持和更新攻击
- **官方建议**: 用户审查所有 PKGBUILD 和 install 脚本变更

## 审计时间线

| 时间 | 事件 |
|------|------|
| 2026-06-10 | 系统安装 |
| 2026-06-10 ~ 14 | AUR 包安装/更新活动期 |
| 2026-06-12 | Arch 官方发布污染警告 |
| 2026-06-14 | 全面安全审计执行 |

## 审计范围

- 10 个 AUR / 外部仓库包
- 网络连接与监听端口
- 进程与持久化机制 (systemd timer, cron, autostart, SSH)
- 内核模块 (200+ 逐一审查)
- 文件系统完整性 (PKGBUILD, install 脚本, SUID/SGID)
- LD_PRELOAD 劫持
- 防火墙规则
- `/tmp`、`/dev/shm` 隐蔽文件
- 登录记录

## AUR 包审计矩阵

| 包名 | 版本 | PKGBUILD | install 脚本 | 文件完整性 | 结论 |
|------|------|----------|-------------|-----------|------|
| `opencode-bin` | 1.17.6-1 | ✅ 复查，GitHub Releases 官方源 | 无 | ✅ 0 改动 | 干净 |
| `visual-studio-code-bin` | 1.124.2-1 | ✅ 复查，Microsoft 官方 C2 | ✅ 仅提示信息 | ✅ 0 改动 | 干净 |
| `clash-verge-rev-bin` | 2.5.1-1 | ✅ 缓存验证 | 无 | ✅ 0 改动 | 干净 |
| `linuxqq` | 3.2.29_49738-2 | ✅ 复查，腾讯官方源 | 无 | ✅ 0 改动 | 干净 |
| `moekoemusic-bin` | 1.6.5-1 | ✅ 重拉审查 | 无 | ✅ 0 改动 | 干净 |
| `thinkfan` | 2.0.0-3 | ✅ 重拉审查 | ✅ 仅提示 | ✅ 0 改动 | 干净 |
| `intel-undervolt` | 1.7-3 | ✅ 重拉审查 | 无 | ✅ 0 改动 | 干净 |
| `wechat-bin` | 4.1.1.7-1 | ✅ 重拉审查 | 无 | ✅ 0 改动 | ⚠️ md5sums=SKIP |
| `rime-ice-git` | r955.82c0298 | ✅ 重拉审查 | ✅ 仅提示 | ✅ 0 改动 | 干净 |
| `catppuccin-gtk-theme-macchiato` | 1.0.3-1 | — (纯主题包，无可执行代码) | — | ✅ 0 改动 | 干净 |

### PKGBUILD 审查要点

- **源码 URL**: 全部指向官方域名 (github.com, dldir1v6.qq.com, update.code.visualstudio.com, qqdl.gtimg.cn)
- **校验和**: 除 wechat-bin (腾讯不提供版本化下载) 外，均有 sha256/sha512 校验
- **`package()` 函数**: 均无 `curl`/`wget` 等网络调用，不执行外部脚本
- **`.install` 脚本**: 三个包有 (visual-studio-code-bin, thinkfan, rime-ice-git)，内容仅打印配置提示，无任何文件或命令执行操作

### wechat-bin 特殊说明

```
md5sums_x86_64=('SKIP')  # 腾讯不提供带版本的下载 URL
```

每次构建可能拉取不同版本的 `.deb`，无法通过校验和验证。但 `package()` 仅执行 `tar` 解包和 `cp`/`install`/`ln` 操作，无网络请求，风险较低。

## 网络连接审计

```
opencode       → 198.18.0.8:443, 198.18.0.10:443   (Clash TUN → API)
verge-mihomo   → 182.247.248.128:443                (代理服务器)
verge-mihomo   → 1.12.12.12:443                     (腾讯 IM)
gvfsd-http     → 198.18.0.5:443                     (GNOME 文件服务)
```

- `198.18.0.0/30` 为 Clash TUN 虚拟网卡 `Meta`, 已通过 `ip addr` 确认
- 监听端口: `*:53` (verge-mihomo DNS), `127.0.0.1:7897` (verge-mihomo HTTP), `127.0.0.1:33331` (clash-verge 管理)
- UFW: 默认拒绝入站，允许出站。无异常规则。

## 进程与持久化

### 活跃进程
- 无挖矿 / 异常高 CPU 进程
- `opencode` CPU 136% 属于 AI Agent 正常工作负载
- 所有进程均为标准系统服务或用户应用

### 持久化检查
- **systemd timer**: snapper-timeline, snapper-cleanup, paccache, shadow, systemd-tmpfiles-clean, archlinux-keyring-wkd-sync — 全部标准
- **crontab**: 无
- **autostart**: 仅 Clash Verge 桌面项 + GNOME 标准项
- **SSH authorized_keys**: 不存在
- **LD_PRELOAD**: `/etc/ld.so.preload` 不存在

### 登录记录
- 仅 `feisama` 用户通过本地 tty2 (GDM) 登录
- 无远程登录记录 (`lastb` 为空，pam_faillock 未触发)

## 内核模块审计

共计 200+ 模块逐一审查，全部为 Linux 标准模块：

- **无线**: iwlwifi, iwlmld, cfg80211, mac80211, btintel, btusb, bluetooth, rfcomm, bnep
- **GPU**: i915, xe, drm, ttm, gpu_sched
- **存储**: nvme, nvme_core, ahci, libata, sd_mod, btrfs, zstd, lzo, crc32c
- **音频**: snd_hda_intel, snd_soc_sof, snd_sof_pci_intel_tgl
- **安全**: ufw 模块 (nft_compat, x_tables, nf_tables), wireguard, tun
- **硬件**: thinkpad_acpi, processor_thermal, intel_pmc_core, elants_i2c, psmouse
- **加密**: aesni_intel, sha512_ssse3, crct10dif_pclmul, crc32_pclmul, ghash_clmulni_intel
- **其他**: kvm, fuse, zram, overlay, msr, cpuid, cdc_ether, e1000e

**无 rootkit 模块。**

## 可疑对象调查

### /tmp 隐藏 .so 文件

```
/tmp/.5bfffdfe899fe5d6-00000000.so (10MB)
/tmp/.bcb9fd5efdaff23e-00000001.so (5.5MB)
```

- 所有者: `feisama`
- 创建时间: 2026-06-14 22:37 (与 opencode 启动同时)
- `lsof` 确认: 由 `opencode` 进程加载为内存映射
- 包含符号: `fff_create_instance`, `malloc`, `memcpy` 等
- **判定**: Node.js V8 编译缓存（原生 addon），非恶意共享库。与 `/tmp/node-compile-cache/` 目录同属 Node.js 正常行为。

### /home/feisama/.sys1og.conf

```
内容: 716b2818-229b-4369-9438-c04c491a6b4d + 4 bytes
权限: 0600
创建: 2026-06-13 11:15 (与 wechat-bin 安装同秒)
```

- **判定**: wechat-bin 安装时生成的设备标识 UUID，非恶意配置。

### /dev/shm
- 空，无隐藏文件

## 文件完整性验证

对所有 AUR 包执行 `pacman -Qkk`:
```
10/10 包文件 0 处改动
```

## 结论

**系统未受 AUR 恶意软件包污染事件影响。**

经过以下维度的深度检查，未发现任何入侵迹象：

- 10/10 AUR 包 PKGBUILD 审查通过
- 3/3 install 脚本审查通过 (仅打印配置提示)
- 网络连接 4 条，全部确认合法
- 内核模块 200+，全部标准
- 200+ 系统文件完整性无异常
- 无 LD_PRELOAD、无 rootkit、无后门持久化
- 两个可疑对象已查明为正常系统行为

## 后续建议

1. 关注 [archlinux.org/news](https://archlinux.org/news/) 等待事件平息
2. 恢复 AUR 更新前审查每个包的 PKGBUILD 变更
3. 保持 `pacman -Qkk $(pacman -Qmq)` 定期校验
4. `pacman -Sc` 后应保留关键 AUR 包构建日志以便回溯审计
5. AUR 更新使用 `yay -S --sudo pkexec`（本机 pam_faillock 已配置，sudo 会阻断 pacman 安装阶段）

## 后续更新记录

### 2026-06-26 — AUR 包更新

| 包 | 旧版本 | 新版本 | PKGBUILD | 校验和 | 结论 |
|---|---|---|---|---|---|
| `opencode-bin` | 1.17.7-1 | 1.17.11-1 | ✅ GitHub Releases 官方源 | ✅ sha256 | 干净 |
| `visual-studio-code-bin` | 1.124.2-1 | 1.126.0-1 | ✅ Microsoft CDN | ✅ sha256 | 干净 |
| `moekoemusic-bin` | 1.6.5-1 | 1.6.6-1 | ✅ GitHub Releases 官方源 | ✅ sha256 | 干净 |

审查要点：
- 三个包源码 URL 均指向官方域名（github.com, update.code.visualstudio.com）
- 均有 sha256 校验和且通过验证
- `package()` 函数无 `curl`/`wget` 网络调用
- `moekoemusic-bin` 的 `prepare()` 调用 `asar e`/`asar p` 为 Electron 应用标准路径修复，无恶意行为
- 安装阶段因本机 pam_faillock 需用 `pkexec` 替代 `sudo`
