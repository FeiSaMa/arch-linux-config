# 软件包变化

## 官方仓库显式安装（75 个）

```
# Core/系统
base grub efibootmgr os-prober
networkmanager dhcpcd
snapper grub-btrfs snap-pac btrfs-assistant btrfs-progs
pacman-contrib
power-profiles-daemon
pipewire pipewire-pulse pipewire-alsa pipewire-jack wireplumber
ufw
zram-generator
linux-firmware
linux-zen-headers linux-lts-headers
intel-ucode intel-media-driver sof-firmware alsa-firmware alsa-ucm-conf
bluez

# GNOME 桌面
gnome-desktop gnome-shell gdm gnome-control-center gnome-software
gnome-tweaks gnome-text-editor gnome-calculator gnome-clocks
gnome-disk-utility gnome-keyring
baobab loupe showtime snapshot file-roller
ghostty

# 应用
chromium
mission-center
foliate fragments
nautilus-python
neovim github-cli
fastfetch yazi
flatpak
exfat-utils

# 图形驱动
vulkan-intel vulkan-icd-loader vulkan-tools
lib32-vulkan-intel lib32-vulkan-icd-loader

# 字体
noto-fonts noto-fonts-emoji noto-fonts-cjk
ttf-jetbrains-mono terminus-font
adobe-source-han-sans-cn-fonts

# 输入法
fcitx5 fcitx5-rime fcitx5-gtk fcitx5-qt fcitx5-configtool
rime-ice-git

# Shell
zsh zsh-autosuggestions zsh-completions zsh-syntax-highlighting
zsh-theme-powerlevel10k-git

# AUR 助手
yay paru
archlinuxcn-keyring

# 开发
base-devel inotify-tools

# 硬件调优
stress-ng intel-undervolt
```

## AUR 包（7 个）

| 包 | 说明 |
|-----|------|
| clash-verge-rev-bin | Clash 代理 GUI |
| visual-studio-code-bin | VS Code |
| opencode-bin | AI CLI 工具 |
| moekoemusic-bin | 音乐播放器 |
| wechat-bin | 微信 |
| thinkfan | ThinkPad 风扇守护进程 |
| catppuccin-gtk-theme-macchiato | GTK 主题 |

## Flatpak（7 个，system 级别）

```
Extension Manager
Pins (io.github.fabrialberio.pinapp)
Mesa (org.freedesktop.Platform.GL.default) x2
Intel VAAPI driver
GNOME Codecs Extra
GNOME Application Platform v50
```

## 孤儿包

当前无孤儿包（已清理）。
