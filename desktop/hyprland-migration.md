# GNOME → Hyprland 迁移方案

> **状态：未执行 / 备选方案**
>
> **生成日期：** 2026-06-27  
> **系统：** ThinkPad · linux-zen 7.0.13 · Intel Panther Lake · GNOME 50 · Wayland  
> **显示器：** eDP-1, 1920×1200 @ 60Hz, 125% 缩放 · 单屏笔记本

---

## 一、安装

### 1.1 官方包

```
pkexec pacman -S \
  hyprland waybar hyprpaper hyprlock hypridle \
  wofi dunst wl-clipboard cliphist grim slurp \
  polkit-kde-agent brightnessctl network-manager-applet playerctl blueman \
  libappindicator-gtk3 \
  xdg-desktop-portal-hyprland \
  qt5-wayland qt6-wayland nwg-look wlsunset pavucontrol
```

### 1.2 AUR

```
paru -S wlogout
```

---

## 二、配置文件清单

| 文件 | 用途 |
|------|------|
| `~/.config/hypr/hyprland.conf` | 显示器、环境变量、快捷键、窗口规则、启动链 |
| `~/.config/hypr/hyprpaper.conf` | 壁纸（复用当前 GNOME 壁纸） |
| `~/.config/hypr/hyprlock.conf` | 锁屏界面 |
| `~/.config/hypr/hypridle.conf` | 空闲管理（熄屏/锁屏/休眠） |
| `~/.config/waybar/config.jsonc` | 状态栏模块 |
| `~/.config/waybar/style.css` | 状态栏样式 |
| `~/.config/wofi/config` | 应用启动器 |
| `~/.config/dunst/dunstrc` | 通知系统 |

---

## 三、hyprland.conf 核心内容

### 3.1 显示器

```ini
monitor = eDP-1,1920x1200@60,auto,1.25
```

### 3.2 环境变量

```ini
env = XDG_CURRENT_DESKTOP,Hyprland
env = XDG_SESSION_TYPE,wayland
env = XCURSOR_THEME,Adwaita
env = XCURSOR_SIZE,32
env = GTK_IM_MODULE,fcitx
env = QT_IM_MODULE,fcitx
env = XMODIFIERS,@im=fcitx
env = SDL_IM_MODULE,fcitx
env = QT_QPA_PLATFORM,wayland;xcb
env = ELECTRON_OZONE_PLATFORM_HINT,auto
```

### 3.3 输入设备

```ini
input {
    kb_layout = us
    follow_mouse = 1
    touchpad {
        natural_scroll = true
        tap-to-click = true
        disable_while_typing = true
    }
}

gestures {
    workspace_swipe = true
    workspace_swipe_fingers = 3
}
```

### 3.4 全局配置

```ini
general {
    gaps_in = 5
    gaps_out = 10
    border_size = 2
    col.active_border = rgb(c6a0f6) rgb(f5c2e7) 45deg
    col.inactive_border = rgb(45475a)
    resize_on_border = true
}

misc {
    disable_hyprland_logo = true
    mouse_move_enables_dpms = true
    key_press_enables_dpms = true
}

xwayland {
    force_zero_scaling = true
}
```

### 3.5 装饰与模糊

```ini
decoration {
    rounding = 8
    blur {
        enabled = yes
        size = 8
        passes = 3
        new_optimizations = on
    }
}
```

### 3.6 快捷键 — 窗口管理

```ini
bind = SUPER, Q, killactive
bind = SUPER, F, fullscreen
bind = SUPER, Escape, exec, hyprctl reload

bind = SUPER, 1, workspace, 1
bind = SUPER, 2, workspace, 2
bind = SUPER, 3, workspace, 3
bind = SUPER, 4, workspace, 4

bind = SUPER SHIFT, 1, movetoworkspace, 1
bind = SUPER SHIFT, 2, movetoworkspace, 2
bind = SUPER SHIFT, 3, movetoworkspace, 3
bind = SUPER SHIFT, 4, movetoworkspace, 4

bind = SUPER, mouse_down, workspace, e+1
bind = SUPER, mouse_up,   workspace, e-1
```

### 3.7 快捷键 — 应用

```ini
bind = SUPER, T,       exec, ghostty
bind = SUPER, B,       exec, chromium --ozone-platform-hint=auto
bind = SUPER, Space,   exec, wofi --show drun
bind = CTRL ALT, S,    exec, missioncenter
bind = SUPER, E,       exec, nautilus
```

### 3.8 快捷键 — 锁屏与休眠

```ini
bind = SUPER, L,            exec, hyprlock
bind = SUPER SHIFT, L,      exec, systemctl suspend
bind = , XF86Sleep,         exec, systemctl suspend
bind = , XF86Suspend,       exec, systemctl suspend
```

### 3.9 快捷键 — PPD 功率档

```ini
bind = SUPER, F9,  exec, powerprofilesctl set low-power
bind = SUPER, F10, exec, powerprofilesctl set balanced
bind = SUPER, F11, exec, powerprofilesctl set performance
```

> 注：首次切换会弹出 polkit 密码对话框（`polkit-kde-agent` 处理），之后缓存。

### 3.10 快捷键 — 截图

```ini
bind = , Print,       exec, grim - | wl-copy
bind = SHIFT, Print,  exec, grim -g "$(slurp)" - | wl-copy
```

### 3.11 快捷键 — 剪贴板历史

```ini
bind = SUPER, V, exec, cliphist list | wofi -dmenu -p "Clipboard" | cliphist decode | wl-copy
```

### 3.12 快捷键 — ThinkPad 硬件键

```ini
# 亮度
bindel = , XF86MonBrightnessUp,   exec, brightnessctl s +5%
bindel = , XF86MonBrightnessDown, exec, brightnessctl s 5%-

# 音量
bindel = , XF86AudioRaiseVolume, exec, pactl set-sink-volume @DEFAULT_SINK@ +5%
bindel = , XF86AudioLowerVolume, exec, pactl set-sink-volume @DEFAULT_SINK@ -5%
bindl  = , XF86AudioMute,        exec, pactl set-sink-mute @DEFAULT_SINK@ toggle

# 麦克风
bindl = , XF86AudioMicMute, exec, pactl set-source-mute @DEFAULT_SOURCE@ toggle

# 媒体控制
bindl = , XF86AudioPlay, exec, playerctl play-pause
bindl = , XF86AudioNext, exec, playerctl next
bindl = , XF86AudioPrev, exec, playerctl previous
```

### 3.13 快捷键 — 快速设置替代

```ini
bind = SUPER CTRL, W, exec, nmcli radio wifi toggle
bind = SUPER CTRL, B, exec, bluetoothctl power toggle
bind = SUPER CTRL, D, exec, dunstctl set-paused toggle
```

### 3.14 窗口规则

```ini
windowrulev2 = float, class:^(fcitx5-.*)$
windowrulev2 = nofocus, class:^(fcitx5-.*)$
windowrulev2 = noinitialfocus, class:^(fcitx5-.*)$

windowrulev2 = float,  class:^(io.missioncenter.MissionCenter)$
windowrulev2 = center, class:^(io.missioncenter.MissionCenter)$

windowrulev2 = float,  class:^(clash-verge)$
windowrulev2 = float,  class:^(nwg-look)$
windowrulev2 = center, class:^(nwg-look)$

windowrulev2 = float,  class:^(wlogout)$
windowrulev2 = noanim, class:^(wlogout)$

windowrulev2 = float,  class:^(pavucontrol)$
windowrulev2 = center, class:^(pavucontrol)$
```

### 3.15 exec-once 启动链

```ini
exec-once = hyprpaper
exec-once = waybar
exec-once = dunst
exec-once = fcitx5 -d
exec-once = /usr/lib/polkit-kde-authentication-agent-1
exec-once = hyprctl setcursor Adwaita 32
exec-once = nm-applet
exec-once = blueman-applet
exec-once = clash-verge
exec-once = hypridle
exec-once = wl-paste --watch cliphist store
```

---

## 四、配套配置文件

### 4.1 hyprpaper.conf

```ini
preload = /home/feisama/Pictures/wallpaper.jpg
wallpaper = eDP-1,/home/feisama/Pictures/wallpaper.jpg
```

> 壁纸文件从 `~/refs/arch-linux-config/gnome/wallpaper.jpg` 复制到 `~/Pictures/`。

### 4.2 hyprlock.conf

```ini
background {
    monitor = eDP-1
    path = /home/feisama/Pictures/wallpaper.jpg
    blur_passes = 3
    blur_size = 8
}

input-field {
    monitor = eDP-1
    size = 300, 50
    outline_thickness = 2
    outer_color = rgb(c6a0f6)
    inner_color = rgb(1e1e2e)
    font_color = rgb(cad3f5)
    fade_on_empty = false
    placeholder_text = Password...
    position = 0, -80
    halign = center
    valign = center
}
```

### 4.3 hypridle.conf

```ini
general {
    lock_cmd = pidof hyprlock || hyprlock
    before_sleep_cmd = loginctl lock-session
    after_sleep_cmd = hyprctl dispatch dpms on
}

listener {
    timeout = 300
    on-timeout = brightnessctl -s intel_backlight s 10%
    on-resume = brightnessctl -s intel_backlight s 100%
}

listener {
    timeout = 600
    on-timeout = loginctl lock-session
}

listener {
    timeout = 900
    on-timeout = systemctl suspend
}
```

### 4.4 wofi/config

```
width=480
height=320
location=center
matching=fuzzy
show=drun
allow_images=true
```

### 4.5 GTK 主题应用

首次登录 Hyprland 后，运行 `nwg-look` 图形界面设置：
- GTK 主题：`catppuccin-macchiato-mauve-standard+default`
- 图标主题：`Adwaita`
- 字体：`Adwaita Sans 11`
- 配色方案：`prefer-dark`

或通过命令行：
```bash
gsettings set org.gnome.desktop.interface gtk-theme "catppuccin-macchiato-mauve-standard+default"
gsettings set org.gnome.desktop.interface color-scheme prefer-dark
gsettings set org.gnome.desktop.interface font-name "Adwaita Sans 11"
```

---

## 五、GNOME 配置迁移对照

### 5.1 完全保留（不受影响）

| 路径 | 说明 |
|------|------|
| `~/.zshrc` / `~/.p10k.zsh` | Zsh 配置 |
| `~/.config/ghostty/config` | 终端（需 Hyprland blur 开启才显示透明效果） |
| `~/.config/fcitx5/config` + Rime | 输入法（/etc/environment 已有 env 变量） |
| `~/.config/gtk-3.0/settings.ini` | GTK3 主题 |
| `~/.config/mimeapps.list` | 默认应用 |
| `/usr/local/bin/ppd-power-tune.sh` | PPD 调优脚本（纯 sysfs，零 GNOME 依赖） |
| `ppd-profile-monitor.service` | 自定义服务（不受影响） |
| `clash-verge-service.service` | 代理守护（不受影响） |
| 全部 `hardware/` 配置 | 风扇/RAPL/CPU/ASPM — 均 DE 无关 |
| 全部 `system/` 配置 | 内核/Btrfs/ZRAM/UFW — 均不变 |

### 5.2 17 个 GNOME 扩展替代

| GNOME 扩展 | Hyprland 方案 |
|------------|--------------|
| Tiling Shell | 原生 Dwindle/Master 瓦片布局 |
| Blur My Shell | `decoration:blur` |
| Burn My Windows | 内置窗口动画 |
| Vitals | Waybar 模块（CPU/内存/温度/频率） |
| clipboard-indicator | `cliphist` + Waybar 模块 |
| Caffeine（防息屏） | `hypridle` — 监听全屏/视频自动抑制 |
| hidetopbar | Hyprland 无顶栏 |
| appindicatorsupport | Waybar `tray` 模块 + `libappindicator-gtk3` |
| lockkeys（大小写） | Waybar `keyboard-state` |
| logoutmenu | `wlogout`（AUR） |
| gnome-fuzzy-app-search | `wofi` 模糊搜索 |
| kimpanel（输入法状态） | fcitx5 原生窗口 |
| steal-my-focus | `windowrulev2` |
| unlockDialogBackground | `hyprlock` 背景模糊 |
| auto-power-profile | 已有 `ppd-profile-monitor.service` |
| logomenu | 无需求 |
| user-theme / workspace-indicator | Waybar 工作区模块 |

### 5.3 快捷键迁移对照

| GNOME | Hyprland |
|-------|----------|
| Super+Q — 关闭窗口 | `SUPER, Q, killactive` |
| Super+F — 最大化 | `SUPER, F, fullscreen` |
| Super+T — Ghostty | `SUPER, T, exec, ghostty` |
| Super+B — Chromium | `SUPER, B, exec, chromium --ozone-platform-hint=auto` |
| Super+1~4 — 切换工作区 | `SUPER, 1../4, workspace, 1../4` |
| Shift+Super+1~4 — 移动窗口 | `SUPER SHIFT, 1../4, movetoworkspace, 1../4` |
| Ctrl+Alt+S — Mission Center | `CTRL ALT, S, exec, missioncenter` |

### 5.4 Autostart 迁移

| 原方法 | Hyprland |
|--------|----------|
| `~/.config/autostart/Clash Verge.desktop` (GDM) | `exec-once = clash-verge` |

---

## 六、执行步骤

### 第 1 步：安装包

```bash
pkexec pacman -S \
  hyprland waybar hyprpaper hyprlock hypridle \
  wofi dunst wl-clipboard cliphist grim slurp \
  polkit-kde-agent brightnessctl network-manager-applet playerctl blueman \
  libappindicator-gtk3 \
  xdg-desktop-portal-hyprland \
  qt5-wayland qt6-wayland nwg-look wlsunset pavucontrol

paru -S wlogout
```

### 第 2 步：创建目录和配置文件

```bash
mkdir -p ~/.config/hypr ~/.config/waybar ~/.config/wofi ~/.config/dunst ~/Pictures

cp ~/refs/arch-linux-config/gnome/wallpaper.jpg ~/Pictures/
```

### 第 3 步：写入配置文件

> 按上方第三节至第四节的完整内容写入对应文件。

### 第 4 步：验证安装

```bash
# 检查 hyprland.desktop 是否存在
ls /usr/share/wayland-sessions/hyprland.desktop

# 验证 polkit agent 二进制路径
find /usr/lib -name '*polkit*agent*' -type f 2>/dev/null
```

### 第 5 步：运行 GTK 主题应用

首次登录 Hyprland 后，终端运行：
```bash
nwg-look
```

设置 GTK 主题为 `catppuccin-macchiato-mauve-standard+default`，dark 模式。

### 第 6 步：切换登录

注销 GNOME → GDM 登录界面 → 齿轮图标 → 选择 **Hyprland** → 登录。

---

## 七、验证清单

登录 Hyprland 后逐项确认：

- [ ] Super+T → Ghostty 启动
- [ ] Super+B → Chromium 启动（Wayland 后端）
- [ ] Super+Space → wofi 应用启动器
- [ ] Super+1~4 → 工作区切换
- [ ] Super+Q → 关闭窗口
- [ ] Super+F → 全屏
- [ ] Super+L → 锁屏（hyprlock 显示）
- [ ] Super+V → 剪贴板历史
- [ ] Print → 全屏截图到剪贴板
- [ ] Shift+Print → 区域截图
- [ ] F9/F10/F11 → PPD 功率切换
- [ ] 亮度/音量/麦克风/媒体功能键可用
- [ ] Waybar 状态栏正常显示（电池/网络/音量/时间）
- [ ] 托盘图标可见（nm-applet, blueman-applet, clash-verge）
- [ ] Fcitx5 输入法可用（Super+Space 切换中英文）
- [ ] 空闲 5 分钟 → 屏幕变暗
- [ ] 空闲 10 分钟 → 锁屏
- [ ] Clash Verge 代理正常工作
- [ ] 剪贴板历史 `cliphist list` 正常

---

## 八、风险与回退

| 风险 | 处置 |
|------|------|
| Hyprland 起不来（黑屏/闪退） | `Ctrl+Alt+F2` 切 TTY → 修改 `hyprland.conf` → `hyprctl reload` 或重登录 |
| GDM 不显示 Hyprland 选项 | 确认 `/usr/share/wayland-sessions/hyprland.desktop` 存在；`systemctl restart gdm` |
| 亮度键不响应 | `pkexec usermod -aG video feisama` → 重登录 |
| Tray 图标不显示 | 确认 `libappindicator-gtk3` 已装 + 重启 waybar |
| Chromium/Electron 模糊 | 确认 `ELECTRON_OZONE_PLATFORM_HINT=auto` env 已设 |
| 全然不可用 → 回退 | GDM 登录界面齿轮切回 **GNOME**，零影响 |

---

## 九、扩展连接

- [Hyprland Wiki](https://wiki.hyprland.org/)
- [Hyprland Arch Wiki](https://wiki.archlinux.org/title/Hyprland)
- [Waybar Wiki](https://github.com/Alexays/Waybar/wiki)
- [Catppuccin Hyprland](https://github.com/catppuccin/hyprland)
- [本机 wallpapers](~/Pictures/wallpaper.jpg)
