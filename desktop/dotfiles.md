# 用户配置文件变更

所有文件的实际内容见 `home/` 目录。

## 文件清单

| 目标路径 | 仓库路径 |
|----------|---------|
| `~/.zshrc` | `home/.zshrc` |
| `~/.p10k.zsh` | `home/.p10k.zsh` |
| `~/.config/ghostty/config` | `home/.config/ghostty/config` |
| `~/.config/fcitx5/config` | `home/.config/fcitx5/config` |
| `~/.config/gtk-3.0/settings.ini` | `home/.config/gtk-3.0/settings.ini` |
| `~/.config/mimeapps.list` | `home/.config/mimeapps.list` |
| `~/.config/autostart/Clash Verge.desktop` | `home/.config/autostart/Clash Verge.desktop` |
| `~/.local/share/fcitx5/rime/default.custom.yaml` | `home/.local/share/fcitx5/rime/default.custom.yaml` |

## 额外说明

### ~/.zshrc

- Oh My Zsh + Powerlevel10k 主题
- 历史设置：`HISTSIZE=1000`、`SAVEHIST=1000`、`SHARE_HISTORY`、`EXTENDED_HISTORY`
- `HIST_IGNORE_DUPS`、`HIST_IGNORE_SPACE`
- 插件：`zsh-autosuggestions`、`zsh-syntax-highlighting`、`compinit`
- 自定义函数：`fan()` — 读取 ThinkPad 风扇 RPM

### ~/.p10k.zsh

Powerlevel10k 主题配置（199 行）。

### ~/.config/ghostty/config

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

### ~/.config/nvim/

LazyVim starter 模板：`git clone https://github.com/LazyVim/starter ~/.config/nvim`

### ~/.config/mimeapps.list

```ini
x-scheme-handler/clash=clash-verge.desktop;
```

## AI 恢复命令

```bash
mkdir -p ~/.config/ghostty ~/.config/fcitx5 ~/.config/gtk-3.0 ~/.config/autostart ~/.local/share/fcitx5/rime

# AI 逐文件读取 home/ 目录并写入对应路径
# AI 读取 home/.zshrc → tee ~/.zshrc
# AI 读取 home/.config/ghostty/config → tee ~/.config/ghostty/config
# ...

# Oh My Zsh（.zshrc 依赖此框架）
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Neovim
git clone https://github.com/LazyVim/starter ~/.config/nvim

# 切换 shell
sudo chsh -s /usr/bin/zsh "$USER"
```
