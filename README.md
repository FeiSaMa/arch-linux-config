# Arch Linux 系统配置

> ThinkPad T14 Gen 7 · Intel Core Ultra 7 356H · GNOME 50 · Arch Linux

本仓库记录了我的 Arch Linux 系统完整配置，支持通过 opencode AI 一键恢复。

## 完整安装 + 恢复流程

| 步骤 | 内容 | 参考 |
|------|------|------|
| 1 | 安装 Arch Linux（Btrfs + GRUB + 基础配置） | [Shorin ArchLinux 安装指南](https://github.com/SHORiN-KiWATA/Shorin-ArchLinux-Guide/wiki/%E5%AE%89%E8%A3%85ArchLinux#%E6%89%8B%E5%8A%A8%E5%AE%89%E8%A3%85) |
| 2 | 创建 snapper #23 快照 "before desktop" | — |
| 3 | **从这里开始用 opencode 恢复** | `RESTORE.md` |

## 快速恢复

```bash
# 1. 安装前提（添加 archlinuxcn 源 → 安装 yay + opencode）
echo -e "\n[archlinuxcn]\nServer = https://mirrors.ustc.edu.cn/archlinuxcn/\$arch" | sudo tee -a /etc/pacman.conf
sudo pacman -Sy archlinuxcn-keyring yay git base-devel
yay -S opencode-bin

# 2. 克隆配置
git clone https://github.com/FeiSaMa/arch-linux-config ~/refs/arch-linux-config

# 3. 启动 opencode，告诉它：
#    "根据 ~/refs/arch-linux-config/RESTORE.md 恢复我的系统"
opencode
```

## 目录结构

```
├── RESTORE.md       → AI 恢复手册（7 阶段逐步恢复）
├── summary.md       → 系统变化总览
│
├── opencode/        → opencode 自身配置备份
├── home/            → dotfiles 实际文件
├── files/           → 系统配置文件实际文件
├── gnome/           → GNOME dconf / 扩展 / 壁纸备份
│
├── system/          → 系统配置文档（含 AI 安装命令）
├── desktop/         → 桌面配置文档
├── network/         → 网络与安全
├── scripts/         → 自定义脚本
└── hardware/        → 硬件调优记录
```
