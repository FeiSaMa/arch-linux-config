# AI 恢复手册

> 在刚装好的 Arch Linux 上通过 opencode 一键恢复系统。
>
> **前提：** Arch base 已安装、已联网、已有普通用户、已安装 `git` + `yay` + `opencode-bin`
>
> **注意：** 本配置针对 ThinkPad T14 Gen 7 (Intel Core Ultra 7 356H)。如果目标机器硬件不同，\n\
> Phase 5（硬件调优）中的 thinkfan、RAPL 功率限制、GPU min_freq 等参数需要重新适配。

## 使用方式

```bash
# 1. 一键安装 yay + opencode（依托 archlinuxcn 源）
echo -e "\n[archlinuxcn]\nServer = https://mirrors.ustc.edu.cn/archlinuxcn/\$arch" | sudo tee -a /etc/pacman.conf
sudo pacman -Sy archlinuxcn-keyring yay git base-devel
yay -S opencode-bin

# 2. 克隆本仓库
git clone https://github.com/FeiSaMa/arch-linux-config ~/refs/arch-linux-config

# 3. 启动 opencode，告诉他：
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
- 重启 opencode 使新配置生效

---

## Phase 1: 安装包

目标：安装本机的全部 75 个官方包 + 7 个 AUR 包 + 7 个 Flatpak。

参考文档：`system/packages.md`

### AI 执行

**官方包：**

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

# 注：lib32 包需要 multilib 仓库已启用
# 如果尚未启用，先恢复 pacman.conf（见 Phase 2）或手动取消注释 /etc/pacman.conf 中的 [multilib]

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
yay -S --needed clash-verge-rev-bin
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
  io.github.fabrialberio.pinapp \
  org.freedesktop.Platform.GL.default \
  org.freedesktop.Platform.GL32.default \
  org.freedesktop.Platform.VAAPI.Intel \
  org.gnome.Platform.Codecs
# 注：Extension Manager 通过 gnome-extensions 安装，不是 Flatpak 方式
```

### 验证

```bash
pacman -Q --explicit | wc -l     # 应接近 75（因依赖版本可能有差异）
yay -Q --aur | wc -l             # 应 ≈ 8 (含 rime-ice-git)
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

# 复制配置文件（AI 逐个读取 ~/refs/arch-linux-config/files/etc/ 下的文件并写入）
# 以下是 AI 需要复制到对应路径的文件清单：
```

AI 从 `files/etc/environment` 读取内容并写入 `/etc/environment`
AI 从 `files/etc/sysctl.d/99-swappiness.conf` 读取内容并写入 `/etc/sysctl.d/99-swappiness.conf`
AI 从 `files/etc/systemd/zram-generator.conf` 读取内容并写入 `/etc/systemd/zram-generator.conf`
AI 从 `files/etc/modprobe.d/99-thinkfan.conf` 读取内容并写入 `/etc/modprobe.d/99-thinkfan.conf`
AI 从 `files/etc/NetworkManager/conf.d/20-connectivity.conf` 读取内容并写入 `/etc/NetworkManager/conf.d/20-connectivity.conf`
AI 从 `files/etc/pacman.d/hooks/merge-journald-conf.hook` 读取内容并写入 `/etc/pacman.d/hooks/merge-journald-conf.hook`
AI 从 `files/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook` 读取内容并写入 `/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook`
AI 从 `files/etc/thinkfan.conf` 读取内容并写入 `/etc/thinkfan.conf`
AI 从 `files/etc/pacman.conf` 读取内容并写入 `/etc/pacman.conf`
AI 从 `files/etc/locale.conf` 读取内容并写入 `/etc/locale.conf`
AI 从 `files/etc/hostname` 读取内容并写入 `/etc/hostname`
AI 从 `files/etc/adjtime` 读取内容并写入 `/etc/adjtime`
（注：adjtime 含旧机器的时间戳，AI 也可选择不复制，改用 `hwclock --systohc --utc` 生成新值）

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

- GRUB 安装需确认 EFI 分区路径（可能是 `/boot` 或 `/efi`）
- `mkinitcpio -P` 失败：检查 `/etc/mkinitcpio.conf` 是否存在
- `hwclock` 失败：跳过，不影响系统功能
- **建议此时重启一次**，确保 GRUB 参数和 initramfs 生效后再继续 Phase 3-7

---

## Phase 3: 部署 dotfiles

目标：恢复用户目录下的配置文件。

参考文档：`desktop/dotfiles.md`

### AI 执行

AI 从 `home/` 目录读取每个文件并写入对应用户路径：

```bash
# 创建必要目录
mkdir -p ~/.config/ghostty ~/.config/fcitx5 ~/.config/gtk-3.0 \
  ~/.config/autostart ~/.local/share/fcitx5/rime
```

AI 从 `home/.zshrc` 读取内容并写入 `~/.zshrc`
AI 从 `home/.p10k.zsh` 读取内容并写入 `~/.p10k.zsh`
AI 从 `home/.config/ghostty/config` 读取内容并写入 `~/.config/ghostty/config`
AI 从 `home/.config/fcitx5/config` 读取内容并写入 `~/.config/fcitx5/config`
AI 从 `home/.config/gtk-3.0/settings.ini` 写入 `~/.config/gtk-3.0/settings.ini`
AI 从 `home/.config/mimeapps.list` 写入 `~/.config/mimeapps.list`
AI 从 `home/.config/autostart/"Clash Verge.desktop"` 写入 `~/.config/autostart/"Clash Verge.desktop"`
AI 从 `home/.local/share/fcitx5/rime/default.custom.yaml` 写入 `~/.local/share/fcitx5/rime/default.custom.yaml`

```bash
# Oh My Zsh（.zshrc 依赖此框架）
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Neovim (LazyVim starter)
git clone https://github.com/LazyVim/starter ~/.config/nvim

# 切换默认 shell 到 zsh
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

参考文档：`desktop/gnome-settings.md`

### AI 执行

```bash
# 恢复 dconf 设置（含快捷键、主题、扩展配置等所有 GNOME 设置）
# 注：dconf load 需要 GNOME 会话环境，如果在 TTY 下执行会失败
# 可暂缓此步，登录 GNOME 后再运行
#
# 替换 dconf 中硬编码的旧用户名 /home/feisama/ → /home/$USER/
sed "s|/home/feisama/|/home/$USER/|g" ~/refs/arch-linux-config/gnome/dconf.conf | \
  dconf load / 2>/dev/null || echo "dconf 未执行（无 GNOME 会话），登录后再运行 dconf load"

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
# 以下命令需要 GNOME 会话，在 TTY 下跳过
if pgrep -x gnome-shell >/dev/null 2>&1; then
  gsettings get org.gnome.desktop.interface.color-scheme  # → 'prefer-dark'
  gsettings get org.gnome.desktop.interface.accent-color   # → 'purple'
  gnome-extensions list --enabled | wc -l                   # → ≈ 17
else
  echo "GNOME 未运行，登录后手动验证"
fi
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
# 设置 GRUB 内核参数（mitigations=off 等）
# 追加参数到 GRUB_CMDLINE_LINUX_DEFAULT（若变量不存在则创建）
if grep -q '^GRUB_CMDLINE_LINUX_DEFAULT' /etc/default/grub; then
  sudo sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& mitigations=off zswap.enabled=0 nmi_watchdog=0/' /etc/default/grub
else
  echo 'GRUB_CMDLINE_LINUX_DEFAULT="mitigations=off zswap.enabled=0 nmi_watchdog=0"' | sudo tee -a /etc/default/grub
fi
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

```bash
# 重启进入 GNOME
sudo reboot
```

登录后验证：
- 切换 PPD 模式检查硬件联动
- Fcitx5 输入法 (Super+Space)
- Ghostty 终端 (Catppuccin 主题)
- 各扩展功能
