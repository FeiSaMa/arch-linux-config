# 软件包变化

## 官方仓库显式安装（分组列表，实际数量 80-95 视依赖版本而定）

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

## AI 安装命令

### 官方包

```bash
# Core/系统
sudo pacman -S --needed base grub efibootmgr os-prober
sudo pacman -S --needed networkmanager dhcpcd
sudo pacman -S --needed snapper grub-btrfs snap-pac btrfs-assistant btrfs-progs
sudo pacman -S --needed pacman-contrib
sudo pacman -S --needed power-profiles-daemon
sudo pacman -S --needed pipewire pipewire-pulse pipewire-alsa pipewire-jack wireplumber
sudo pacman -S --needed ufw
sudo pacman -S --needed zram-generator
sudo pacman -S --needed linux-firmware
sudo pacman -S --needed linux-zen-headers linux-lts-headers
sudo pacman -S --needed intel-ucode intel-media-driver sof-firmware alsa-firmware alsa-ucm-conf
sudo pacman -S --needed bluez

# GNOME 桌面
sudo pacman -S --needed gnome-desktop gnome-shell gdm gnome-control-center gnome-software
sudo pacman -S --needed gnome-tweaks gnome-text-editor gnome-calculator gnome-clocks
sudo pacman -S --needed gnome-disk-utility gnome-keyring
sudo pacman -S --needed baobab loupe showtime snapshot file-roller
sudo pacman -S --needed ghostty

# 应用
sudo pacman -S --needed chromium
sudo pacman -S --needed mission-center
sudo pacman -S --needed foliate fragments
sudo pacman -S --needed nautilus-python
sudo pacman -S --needed neovim github-cli
sudo pacman -S --needed fastfetch yazi
sudo pacman -S --needed flatpak
sudo pacman -S --needed exfat-utils

# 启用 multilib 仓库（若已启用则跳过，幂等）
grep -q '^\[multilib\]' /etc/pacman.conf || echo -e '\n[multilib]\nInclude = /etc/pacman.d/mirrorlist' | sudo tee -a /etc/pacman.conf
sudo pacman -Sy

# 图形驱动
sudo pacman -S --needed vulkan-intel vulkan-icd-loader vulkan-tools
sudo pacman -S --needed lib32-vulkan-intel lib32-vulkan-icd-loader

# 字体
sudo pacman -S --needed noto-fonts noto-fonts-emoji noto-fonts-cjk
sudo pacman -S --needed ttf-jetbrains-mono terminus-font
sudo pacman -S --needed adobe-source-han-sans-cn-fonts

# 输入法
sudo pacman -S --needed fcitx5 fcitx5-rime fcitx5-gtk fcitx5-qt fcitx5-configtool

# Shell
sudo pacman -S --needed zsh zsh-autosuggestions zsh-completions zsh-syntax-highlighting
sudo pacman -S --needed zsh-theme-powerlevel10k-git

# 注：yay 和 archlinuxcn-keyring 已在 bootstrap 中安装，此处不重复

# 开发
sudo pacman -S --needed base-devel inotify-tools

# 硬件调优
sudo pacman -S --needed stress-ng intel-undervolt
```

### AUR 包

```bash
# clash-verge-rev-bin 已在 bootstrap 中安装（含 clash-verge-service 守护进程 + clash-verge GUI）
yay -S --needed visual-studio-code-bin
# opencode-bin 已在 bootstrap 中安装（首次安装需要），此处可跳过
# yay -S --needed opencode-bin
yay -S --needed moekoemusic-bin
yay -S --needed wechat-bin
yay -S --needed thinkfan
yay -S --needed catppuccin-gtk-theme-macchiato
yay -S --needed rime-ice-git
```

### Flatpak

```bash
sudo flatpak install -y flathub \
  com.mattjakeman.ExtensionManager \
  io.github.fabrialberio.pinapp \
  org.freedesktop.Platform.GL.default \
  org.freedesktop.Platform.VAAPI.Intel \
  org.freedesktop.Platform.codecs-extra
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

## Flatpak（system 级别）

| 名称 | Flatpak ID |
|------|-----------|
| Extension Manager | `com.mattjakeman.ExtensionManager` |
| Pins | `io.github.fabrialberio.pinapp` |
| Mesa (2 refs) | `org.freedesktop.Platform.GL.default` |
| Intel VAAPI driver | `org.freedesktop.Platform.VAAPI.Intel` |
| Codecs Extra | `org.freedesktop.Platform.codecs-extra` |

`org.gnome.Platform` 运行时由上述包自动依赖安装，无需显式安装。

## 孤儿包

当前无孤儿包（已清理）。
