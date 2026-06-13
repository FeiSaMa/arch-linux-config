# AI 恢复手册

> 在已安装 GNOME 桌面的 Arch Linux 上通过 opencode 一键恢复全部配置。
>
> **完整流程：**
>
> | 步骤 | 内容 |
> |------|------|
> | 1 | [Shorin ArchLinux → 手动安装](https://github.com/SHORiN-KiWATA/Shorin-ArchLinux-Guide/wiki/%E5%AE%89%E8%A3%85ArchLinux#%E6%89%8B%E5%8A%A8%E5%AE%89%E8%A3%85) |
> | 2 | 安装 GNOME 桌面（手动，pacman 走国内镜像） |
> | 3 | 创建 snapshot（如 "after GNOME"） |
> | 4 | **从这里开始 — 以下用 opencode 恢复** |
>
> **起始状态：**
> - ✅ Arch base + Btrfs + GRUB + NetworkManager + zram + locale/时区/用户
> - ✅ GNOME 桌面 + gdm（已登录 GNOME）
> - ❌ 未安装 yay / opencode / Clash
> - ❌ 无 dotfiles / 硬件调优 / 其他配置

## 使用方式

```bash
# 1. 添加 archlinuxcn 源 + 安装 yay 和 opencode
echo -e "\n[archlinuxcn]\nServer = https://mirrors.ustc.edu.cn/archlinuxcn/\$arch" | sudo tee -a /etc/pacman.conf
sudo pacman -Sy archlinuxcn-keyring yay git base-devel
yay -S opencode-bin

# 2. 安装 Clash Verge + 启动代理（配置订阅后生效）
yay -S clash-verge-rev-bin
# 订阅链接：https://feed.iggv5.com/c/714a8058-614e-4068-965a-682d2263d5b2/platform/clash/iGG-iGuge
# 打开 Clash Verge GUI → 订阅 → 添加上述 URL → 切换到可用节点
# 配置完成后启动服务（代理立即可用）：
sudo systemctl enable --now clash-verge-service.service

# 3. 克隆仓库（走代理，GitHub 可访问）
git clone https://github.com/FeiSaMa/arch-linux-config ~/refs/arch-linux-config

# 4. 启动 opencode，告诉他：
#    "根据 ~/refs/arch-linux-config/RESTORE.md 恢复我的系统"
opencode
```

---

# 恢复流程

## Phase 0: 自举

目标：安装基础工具，恢复 opencode 自身配置。

### AI 执行

```bash
# 安装基础开发工具
# 注：若代理已生效，GitHub 下载（rustup、docker 等）走代理，否则使用国内镜像
sudo pacman -S --needed curl cmake docker docker-compose go rustup \
  nodejs npm python-pip openssh ripgrep fd fzf jq unzip tmux

# 启用 Docker
sudo systemctl enable docker.service
sudo usermod -aG docker "$USER"
```

```bash
# 恢复 opencode 配置
# 从仓库复制到 ~/.config/opencode/
mkdir -p ~/.config/opencode/instructions
cp ~/refs/arch-linux-config/opencode/opencode.jsonc ~/.config/opencode/
cp ~/refs/arch-linux-config/opencode/instructions/system.md ~/.config/opencode/instructions/
cp ~/refs/arch-linux-config/opencode/tui.json ~/.config/opencode/
```

### 验证

```bash
ls ~/.config/opencode/opencode.jsonc ~/.config/opencode/instructions/system.md
```

### 失败处理

- `pacman` 失败：检查网络连接和镜像源
- opencode 配置已复制到 ~/.config/opencode/，下次启动自动生效。当前会话不受影响，AI 已可直接读取仓库文件
- 检测到 GitHub 访问失败时，检查 `clash-verge-service.service` 是否已启动且订阅已配置

---

## Phase 1: 安装包

目标：安装本机的全部 75 个官方包 + 7 个 AUR 包 + 7 个 Flatpak。

参考文档：`system/packages.md`

### AI 执行

**官方包（注意：GNOME 包已由用户在步骤 2 手动安装，`--needed` 会自动跳过）：**

```bash
# Core/系统
sudo pacman -S --needed base grub efibootmgr os-prober
sudo pacman -S --needed networkmanager dhcpcd
# 注：snapper/grub-btrfs/snap-pac 需要 Btrfs 文件系统，非 Btrfs 环境跳过
sudo pacman -S --needed btrfs-progs
if mount | grep -q 'on / type btrfs'; then
  sudo pacman -S --needed snapper grub-btrfs snap-pac btrfs-assistant
else
  echo "非 Btrfs 根文件系统，跳过 snapper/grub-btrfs"
fi
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

# 启用 multilib 仓库（lib32 包需要，若已启用则跳过）
grep -q '^\[multilib\]' /etc/pacman.conf || echo -e '\n[multilib]\nInclude = /etc/pacman.d/mirrorlist' | sudo tee -a /etc/pacman.conf
sudo pacman -Sy

# 图形驱动 (Intel)
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

# 注：yay 和 archlinuxcn-keyring 已在 bootstrap 中安装

# 开发
sudo pacman -S --needed base-devel inotify-tools

# 硬件调优
sudo pacman -S --needed stress-ng intel-undervolt
```

**AUR 包：**

```bash
# clash-verge-rev-bin 已在 bootstrap 中安装（含 CLI 守护进程，无需桌面）
yay -S --needed visual-studio-code-bin
# opencode-bin 已在 bootstrap 中安装，此处不重复
yay -S --needed moekoemusic-bin
yay -S --needed wechat-bin
yay -S --needed thinkfan
yay -S --needed catppuccin-gtk-theme-macchiato
yay -S --needed rime-ice-git
```

**Flatpak：**

```bash
sudo flatpak install -y flathub \
  com.mattjakeman.ExtensionManager \
  io.github.fabrialberio.pinapp \
  org.freedesktop.Platform.GL.default \
  org.freedesktop.Platform.VAAPI.Intel \
  org.freedesktop.Platform.codecs-extra
# 注：org.gnome.Platform 运行时由上述包自动依赖安装
```

### 验证

```bash
pacman -Q --explicit | wc -l     # 应接近 80-95（因依赖和 GNOME 版本差异）
# AUR 包逐个验证：
for pkg in clash-verge-rev-bin visual-studio-code-bin opencode-bin \
  moekoemusic-bin wechat-bin thinkfan catppuccin-gtk-theme-macchiato \
  rime-ice-git; do
  pacman -Q "$pkg" &>/dev/null && echo "  ✅ $pkg" || echo "  ❌ $pkg"
done
flatpak list --system | wc -l    # 应 ≈ 7
```

### 失败处理

- 单个包安装失败：跳过，继续下一个
- AUR 包编译失败：检查 `base-devel` 是否已安装
- Flatpak 需先安装 `flatpak` 并添加 flathub 仓库

---

## Phase 2: 配置系统

目标：复制所有系统配置文件到 /etc/，配置引导和内核。

参考文档：`system/config-files.md`、`system/kernel-boot.md`

### AI 执行

```bash
# 创建必要目录
sudo mkdir -p /etc/sysctl.d /etc/modprobe.d /etc/NetworkManager/conf.d \
  /etc/pacman.d/hooks /efi

# 系统配置文件恢复原则：
# - 纯参数文件（sysctl、modprobe、NetworkManager、zram-generator、thinkfan）→ 直接写入
# - 含旧路径/机器信息的（adjtime）→ 理解后适配
# - 包管理的（pacman.conf、hooks）→ 校验后写入
#
# AI 逐个读取 files/etc/ 下的参考文件，理解后写入对应路径：
```

AI 读取 `files/etc/environment` 理解环境变量设置 → 写入 `/etc/environment`
AI 读取 `files/etc/sysctl.d/99-swappiness.conf` → 写入 `/etc/sysctl.d/99-swappiness.conf`
AI 读取 `files/etc/systemd/zram-generator.conf` → 写入 `/etc/systemd/zram-generator.conf`
AI 读取 `files/etc/modprobe.d/99-thinkfan.conf` → 写入 `/etc/modprobe.d/99-thinkfan.conf`
AI 读取 `files/etc/NetworkManager/conf.d/20-connectivity.conf` → 写入 `/etc/NetworkManager/conf.d/20-connectivity.conf`
AI 读取 `files/etc/pacman.d/hooks/merge-journald-conf.hook` → 写入 `/etc/pacman.d/hooks/merge-journald-conf.hook`
AI 读取 `files/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook` → 写入 `/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook`
AI 读取 `files/etc/thinkfan.conf` → 写入 `/etc/thinkfan.conf`（非 ThinkPad 跳过）
AI 读取 `files/etc/pacman.conf` → 写入 `/etc/pacman.conf`
AI 读取 `files/etc/locale.conf` → 写入 `/etc/locale.conf`
AI 读取 `files/etc/hostname` → 写入 `/etc/hostname`
AI 读取 `files/etc/systemd/system/ppd-profile-monitor.service` → 写入 `/etc/systemd/system/ppd-profile-monitor.service`
AI 读取 `files/etc/systemd/system/clash-verge-service.service` → 写入 `/etc/systemd/system/clash-verge-service.service`
AI 读取 `files/etc/adjtime` 了解格式 → 不复制旧时间戳，改用 `hwclock --systohc --utc` 生成

```bash
# 生成 locale（zh_CN.UTF-8 需在 /etc/locale.gen 中启用）
if ! grep -q '^zh_CN.UTF-8' /etc/locale.gen; then
  sudo sed -i 's/#zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen 2>/dev/null || echo 'zh_CN.UTF-8 UTF-8' | sudo tee -a /etc/locale.gen
fi
sudo locale-gen

# 区域设置
sudo localectl set-locale LANG=zh_CN.UTF-8
sudo hostnamectl hostname ThinkPad
sudo timedatectl set-timezone Asia/Shanghai
sudo timedatectl set-ntp true
sudo hwclock --systohc --utc

# GRUB 引导（检测 UEFI 或 BIOS）
if [ -d /sys/firmware/efi ]; then
  echo "检测到 UEFI 模式"
  # 查找 ESP 挂载点
  EFI_DIR=$(mount | grep 'vfat.*/boot\|vfat.*/efi' | awk '{print $3}' | head -1)
  [ -z "$EFI_DIR" ] && EFI_DIR="/efi"
  sudo grub-install --target=x86_64-efi --efi-directory="$EFI_DIR"
else
  echo "检测到 BIOS/Legacy 模式"
  sudo grub-install --target=i386-pc
fi
sudo grub-mkconfig -o /boot/grub/grub.cfg

# initramfs（thinkpad_acpi 风扇控制）
sudo mkinitcpio -P
```

### 验证

```bash
cat /etc/hostname    # → ThinkPad
cat /etc/locale.conf # → LANG=zh_CN.UTF-8
timedatectl show --property NTPSynchronized --value  # → yes
cat /proc/sys/vm/swappiness  # → 1
```

### 失败处理

- GRUB 已安装时 `grub-install` 会安全覆盖，不会损坏现有引导
- `mkinitcpio -P` 失败：检查 `/etc/mkinitcpio.conf` 是否存在
- `hwclock` 失败：跳过，不影响系统功能

---

## Phase 3: 部署 dotfiles

目标：在新机器上生成适配的 dotfiles。

**原则：** 不盲目复制旧文件。AI 读取 `home/` 中的参考文件，理解每个配置项的意图，然后为新机器生成适配版本。

参考文档：`desktop/dotfiles.md`

### AI 理解参考文件

```bash
# 创建必要目录
mkdir -p ~/.config/ghostty ~/.config/fcitx5 ~/.config/gtk-3.0 \
  ~/.config/autostart ~/.local/share/fcitx5/rime
```

**AI 需要为每个 dotfile 做的事情：**

1. 读取参考文件 → 理解配置意图
2. 检查新机器上对应工具是否已安装
3. 剔除依赖旧机器特有工具的配置（如 `fan()` 函数需要 ThinkPad hwmon）
4. 写入适配后的版本

### ~/.zshrc

参考：`home/.zshrc`（148 行，Oh My Zsh + Powerlevel10k）

```bash
# Oh My Zsh 框架（必需，.zshrc 依赖）
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Powerlevel10k 主题
# 已通过 pacman 安装 zsh-theme-powerlevel10k-git
```

**AI 需注意：**
- `source $ZSH/oh-my-zsh.sh`（第 82 行）依赖 Oh My Zsh，已安装
- `plugins=(git)`（第 80 行）是 Oh My Zsh 内置插件，无需额外安装
- `zsh-autosuggestions`（第 138 行）和 `zsh-syntax-highlighting`（第 142 行）从 `/usr/share/` 加载，已通过 pacman 安装
- `fan()` 函数（第 148 行）是 ThinkPad 专用，非 ThinkPad 机器应移除
- `p10k.zsh`（第 114 行）已备份，见下方

### ~/.p10k.zsh

参考：`home/.p10k.zsh`（199 行）

```bash
# 直接写入（纯外观配置，无机器相关路径）
```

### ~/.config/ghostty/config

参考：`home/.config/ghostty/config`

**AI 需注意：**
- 主题文件 `catppuccin-macchiato.conf` 来自 ghostty 包内置主题，确认已安装
- 如 ghostty 未安装，跳过此文件

### ~/.config/fcitx5/config

参考：`home/.config/fcitx5/config`

```bash
# 直接写入（输入法配置，无机器相关路径）
```

### ~/.config/gtk-3.0/settings.ini

参考：`home/.config/gtk-3.0/settings.ini`

```bash
# 直接写入
```

### ~/.config/mimeapps.list

参考：`home/.config/mimeapps.list`

```bash
# 直接写入（文件关联配置）
```

### ~/.config/autostart/Clash Verge.desktop

参考：`home/.config/autostart/"Clash Verge.desktop"`

**AI 需注意：**
- 文件路径含空格，写入时需用引号
- 确认 `clash-verge-rev-bin` 已安装（Phase 1 AUR 包）

### Neovim

```bash
git clone https://github.com/LazyVim/starter ~/.config/nvim
```

### Rime 输入法

```bash
# custom.yaml 直接写入（rime-ice-git 包安装后会自动配置词库）
```

### 切换默认 shell

```bash
sudo chsh -s /usr/bin/zsh "$USER"
```

### 验证

```bash
ls -la ~/.zshrc ~/.p10k.zsh
echo $SHELL  # → /usr/bin/zsh
```

### 失败处理

- `chsh` 失败：手动运行 `chsh -s /usr/bin/zsh`
- LazyVim clone 失败：检查网络，可稍后手动 clone

---

## Phase 4: 恢复 GNOME

目标：恢复 GNOME 桌面设置、扩展、壁纸。

**时机：** GNOME 已在运行（用户步骤 2 手动安装并登录），此阶段可以直接执行。

参考文档：`desktop/gnome-settings.md`

### AI 执行

```bash
# 恢复 dconf 设置（含快捷键、主题、扩展配置等所有 GNOME 设置）
# 替换 dconf 中硬编码的旧用户名 /home/feisama/ → /home/$USER/
sed "s|/home/feisama/|/home/$USER/|g" ~/refs/arch-linux-config/gnome/dconf.conf | \
  dconf load / 2>/dev/null || echo "部分 dconf 键导入失败（可能是扩展未安装导致的 schema 缺失）"

# 安装 GNOME Shell 扩展
bash ~/refs/arch-linux-config/gnome/extensions.sh

# 复制壁纸
mkdir -p ~/.local/share/backgrounds
cp ~/refs/arch-linux-config/gnome/wallpaper.jpg ~/.local/share/backgrounds/
gsettings set org.gnome.desktop.background picture-uri \
  "file://$HOME/.local/share/backgrounds/wallpaper.jpg"
gsettings set org.gnome.desktop.screensaver picture-uri \
  "file://$HOME/.local/share/backgrounds/wallpaper.jpg"

# Fcitx5 Rime 输入法配置（复制 Rime 雾凇词库）
# 注：rime-ice-git 包安装后会自动配置，custom.yaml 已部署
```

### 验证

```bash
gsettings get org.gnome.desktop.interface.color-scheme  # → 'prefer-dark'
gsettings get org.gnome.desktop.interface.accent-color   # → 'purple'
gnome-extensions list --enabled | wc -l                   # → ≈ 17
```

### 失败处理

- `dconf load` 某些键可能因缺少 schema 而报 warning，忽略
- 扩展安装可能因 EGO 版本号变化失败，检查 `gnome/extensions.sh` 中的版本号
- 壁纸路径需替换为实际 home 路径

---

## Phase 5: 硬件调优

目标：部署 PPD 功率联动脚本、thinkfan 配置、GRUB 内核参数。

参考文档：`hardware/performance-unlock.md`、`hardware/mitigations-off.md`

### AI 执行

```bash
# 部署 PPD 功率调优脚本（Intel CPU + ThinkPad 专用，其他硬件跳过）
if [ -d /sys/class/powercap/intel-rapl ]; then
  sudo cp ~/refs/arch-linux-config/files/usr/local/bin/ppd-power-tune.sh \
    /usr/local/bin/
  sudo chmod +x /usr/local/bin/ppd-power-tune.sh

  # 设置 CAFFEINE_USER 供 Caffeine 联动使用（注入到 service 环境）
  sudo mkdir -p /etc/systemd/system/ppd-profile-monitor.service.d
  echo "[Service]" | sudo tee /etc/systemd/system/ppd-profile-monitor.service.d/caffeine-user.conf
  echo "Environment=CAFFEINE_USER=$USER" | sudo tee -a /etc/systemd/system/ppd-profile-monitor.service.d/caffeine-user.conf

  # 重载 systemd
  sudo systemctl daemon-reload

  # 启动 ppd-monitor 服务
  sudo systemctl start ppd-profile-monitor.service 2>/dev/null || echo "服务文件未就绪，Phase 6 将处理"
else
  echo "非 Intel RAPL 硬件，跳过 PPD 功率调优"
fi

# ThinkPad 风扇控制（非 ThinkPad 跳过）
if [ -d /sys/class/hwmon ] && grep -l ^thinkpad /sys/class/hwmon/hwmon*/name &>/dev/null; then
  # 重载 thinkpad_acpi 模块使 fan_control=1 在当前会话生效
  sudo modprobe -r thinkpad_acpi 2>/dev/null || true
  sudo modprobe thinkpad_acpi

  # 启动 thinkfan
  sudo systemctl start thinkfan 2>/dev/null || echo "thinkfan 未就绪，Phase 6 将处理"

  # 确认 fan_control 生效
  cat /sys/module/thinkpad_acpi/parameters/fan_control  # 应为 Y
else
  echo "非 ThinkPad 硬件，跳过 thinkfan"
fi
```

```bash
# 确保 /boot/grub → /efi/grub symlink 存在（Shorin 指南的配置）
sudo ln -sf /efi/grub /boot/grub 2>/dev/null || true

# 设置 GRUB 内核参数（仅添加不存在的参数，避免重复）
CURRENT=$(grep -oP '^GRUB_CMDLINE_LINUX_DEFAULT="\K[^"]*' /etc/default/grub 2>/dev/null)
for param in mitigations=off zswap.enabled=0 nmi_watchdog=0; do
  echo "$CURRENT" | grep -qw "$param" || CURRENT="$CURRENT $param"
done
sudo sed -i "s/^GRUB_CMDLINE_LINUX_DEFAULT=\".*\"/GRUB_CMDLINE_LINUX_DEFAULT=\"$CURRENT\"/" /etc/default/grub 2>/dev/null \
  || echo "GRUB_CMDLINE_LINUX_DEFAULT=\"$CURRENT\"" | sudo tee -a /etc/default/grub
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

### 验证

```bash
systemctl is-active thinkfan ppd-profile-monitor.service  # → active active
cat /sys/module/thinkpad_acpi/parameters/fan_control       # → Y
```

### 失败处理

- `fan_control=Y` 不生效：检查 `thinkpad_acpi` 模块加载时机（需在 initramfs 中加载）
- `ppd-power-tune.sh` 依赖 `power-profiles-daemon`，需确认已安装

---

## Phase 6: 启用服务

目标：启用所有系统服务和用户服务。

参考文档：`system/services.md`

### AI 执行

```bash
# 系统服务（关键服务使用 enable --now 立即启动）
sudo systemctl enable --now NetworkManager.service
sudo systemctl enable --now bluetooth.service
sudo systemctl enable --now power-profiles-daemon.service
sudo systemctl enable NetworkManager-wait-online.service
sudo systemctl enable NetworkManager-dispatcher.service
sudo systemctl enable gdm.service
sudo systemctl enable ufw.service
sudo systemctl enable thinkfan.service thinkfan-sleep.service thinkfan-wakeup.service
sudo systemctl enable grub-btrfsd.service
sudo systemctl enable ppd-profile-monitor.service
sudo systemctl enable clash-verge-service.service

# 用户服务（AI 已以普通用户身份运行，直接执行即可）
systemctl --user enable pipewire.service
systemctl --user enable pipewire-pulse.service
systemctl --user enable wireplumber.service
systemctl --user enable xdg-user-dirs.service
systemctl --user enable gnome-keyring-daemon.socket
systemctl --user enable p11-kit-server.socket
systemctl --user enable pipewire-pulse.socket
systemctl --user enable pipewire.socket

# ufw 防火墙规则
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### 验证

```bash
systemctl --failed                   # → 0 loaded units listed
systemctl is-active NetworkManager   # → active
sudo ufw status verbose              # → Status: active
```

### 失败处理

- 自定义服务（`clash-verge-service`、`ppd-profile-monitor`）不存在时禁用相应 enable 命令
- 用户服务需在用户会话下执行，确保 `systemctl --user` 正常工作

---

## Phase 7: 验证

目标：运行完整检查清单，确认所有参数正确。

参考文档：`hardware/improving-loop.md`

### AI 执行

```bash
echo "=== 1. 服务状态 ==="
systemctl --failed
systemctl is-active ppd-profile-monitor.service thinkfan NetworkManager

echo "=== 2. 风扇控制 ==="
cat /sys/module/thinkpad_acpi/parameters/fan_control

echo "=== 3. RAPL 功率限制 ==="
grep . /sys/class/powercap/intel-rapl*/intel-rapl:0/constraint_0_power_limit_uw
grep . /sys/class/powercap/intel-rapl-mmio*/intel-rapl-mmio:0/constraint_0_power_limit_uw

echo "=== 4. PPD 联动 ==="
powerprofilesctl get
cat /sys/class/drm/card0/device/tile0/gt0/freq0/min_freq
cat /sys/module/nvme_core/parameters/default_ps_max_latency_us
cat /sys/module/pcie_aspm/parameters/policy
cat /proc/sys/vm/dirty_ratio

echo "=== 5. 系统参数 ==="
cat /proc/sys/vm/swappiness
cat /sys/block/nvme0n1/queue/scheduler
grep SystemMaxUse /etc/systemd/journald.conf

echo "=== 6. NTP / 时区 ==="
timedatectl show --property NTPSynchronized --value
cat /etc/timezone 2>/dev/null || timedatectl show --property Timezone --value

echo "=== 7. 无 pacnew 残留 ==="
find /etc -name "*.pacnew" 2>/dev/null

echo "=== 8. Caffeine 联动 ==="
sudo -u "$USER" GSETTINGS_BACKEND=memory dbus-launch gsettings get org.gnome.shell.extensions.caffeine cli-toggle 2>/dev/null || echo "需登录 GNOME 后验证"
```

### 验证通过标准

| 检查项 | 期望值 |
|--------|--------|
| `systemctl --failed` | 0 loaded units |
| fan_control | Y |
| MSR PL1 | 75000000 |
| MMIO PL1 | 75000000 |
| GT0 min_freq (performance) | 700 |
| NVMe latency (performance) | 0 |
| ASPM (performance) | `[performance]` |
| dirty_ratio (performance) | 10 |
| swappiness | 1 |
| I/O scheduler | `[none]` |
| journald limit | 500M |
| NTP | yes |
| pacnew | 无 |

### 失败处理

- 验证不通过时，AI 应定位具体哪个配置未生效，对照对应文档重新执行
- 硬件调优参数（RAPL、GPU min_freq）需在 GNOME 登录后切换 PPD profile 才能生效

---

## 恢复后的收尾

### 验证清单

```bash
# 如果 Phase 7 验证都通过，重启确认所有服务正常运行
sudo reboot
```

登录后验证：
- 切换 PPD 模式检查硬件联动
- Fcitx5 输入法 (Super+Space)
- Ghostty 终端 (Catppuccin 主题)
- 各扩展功能
