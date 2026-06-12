# 用户配置文件变更

## ~/.zshrc

- Oh My Zsh + Powerlevel10k 主题
- 历史设置：`HISTSIZE=1000`、`SAVEHIST=1000`、`SHARE_HISTORY`、`EXTENDED_HISTORY`
- `HIST_IGNORE_DUPS`、`HIST_IGNORE_SPACE`
- 加载插件：
  - `zsh-autosuggestions`（策略：history → completion）
  - `zsh-syntax-highlighting`
  - `compinit`（菜单补全）
- 自定义函数：`fan()` → 读取 ThinkPad 风扇 RPM

## ~/.p10k.zsh（199 行）

Powerlevel10k 配置（首次运行 `p10k configure` 生成，包含 prompt 样式、图标、颜色等）

## ~/.config/ghostty/config

```ini
theme = catppuccin-macchiato.conf
window-decoration = none
background-opacity = 0.75
font-family = "Jetbrains Mono"
font-size = 13
window-padding-x = 10
window-padding-y = 10
cursor-style = block
cursor-style-blink = true
```

## ~/.config/nvim/（LazyVim 模板）

从 `https://github.com/LazyVim/starter` 克隆的标准配置：
- `init.lua` — 入口
- `lazy-lock.json` — 插件锁定
- `lazyvim.json` — LazyVim 设置
- `.neoconf.json` — Neovim 项目配置

## ~/.local/share/fcitx5/rime/default.custom.yaml

```yaml
patch:
  __include: rime_ice_suggestion:/
```

## ~/.config/gtk-3.0/settings.ini

```ini
[Settings]
gtk-application-prefer-dark-theme=0
```

## ~/.config/fcitx5/config

```ini
[Hotkey/TriggerKeys]
0=Super+space
[Hotkey/AltTriggerKeys]
0=Shift_L
[Hotkey/PrevPage]
0=Up
[Hotkey/NextPage]
0=Down
```

## ~/.config/mimeapps.list

```ini
x-scheme-handler/clash=clash-verge.desktop;
```

## ~/.config/monitors.xml

- ThinkPad 内置屏幕 eDP-1 (AUO B140UAX01.1)
- 1920×1200 @ 60Hz
- 125% 缩放
