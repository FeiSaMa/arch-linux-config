# Arch Linux 系统变化汇总

**生成日期：** 2026-06-12

**系统：** ThinkPad · Linux 7.0.11-zen1-1-zen · GNOME 50 · Zsh 5.9

---

## 统计总览

| 类别 | 数量 |
|------|------|
| 显式安装包（官方） | 75 个 |
| AUR 包 | 7 个 |
| Flatpak | 7 个 |
| 启用的系统服务 | 15 个 |
| 启用的用户服务 | 8 个 |
| 修改的系统配置文件 | 16 个 |
| 自定义 systemd 服务 | 2 个 |
| 自定义脚本 | 1 个 |
| Pacman hooks | 2 个 |
| GNOME Shell 扩展 | 19 个 |
| 已安装内核 | 2 个（linux-zen + linux-lts） |

## 按类别摘要

### 系统基础
- **双内核**：linux-zen（默认）+ linux-lts（备用）
- **Btrfs**：子卷布局 + zstd 压缩 + 快照系统
- **ZRAM**：30.8G 压缩交换，`vm.swappiness=1`
- **GRUB**：自定义内核参数（禁用 zswap/nmi_watchdog，关闭安全缓解 mitigations=off，Btrfs 子卷 rootflags=subvol=@）

### 桌面
- **GNOME 50** 完整桌面环境
- **19 个扩展**：平铺窗口、毛玻璃、系统监视、剪贴板、防息屏等
- **Catppuccin 主题**：深色模式 + 紫色强调色 + 自定义壁纸
- **快捷键全部重映射**

### 开发环境
- **Neovim** + LazyVim 配置
- **VS Code**
- **opencode**（AI CLI）
- **Zsh** + Powerlevel10k + 语法高亮 + 自动补全

### 中文支持
- **Fcitx5** + Rime 输入法（雾凇词库）
- 中文字体：Noto CJK + 思源黑体

### 网络与安全
- **NetworkManager** 接管网络
- **ufw** 防火墙已启用
- **Clash Verge** 代理核心

### 硬件调优
- **thinkfan**：ThinkPad 风扇控制
- **ppd-power-tune.sh**：三级 RAPL 功率限制 + GPU 频率 + ASPM 策略
- **Intel 微码**加载
- **日志限制 500M** 防膨胀

### 区域设置
- `zh_CN.UTF-8` 语言环境
- 时区 `Asia/Shanghai`
- 硬件时钟 `UTC`

---

所有完整文件见本目录下各 `.md` 文件。
