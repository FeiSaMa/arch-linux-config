# GNOME 桌面配置

所有 GNOME 设置的备份见 `gnome/` 目录。

## 备份文件

| 文件 | 说明 |
|------|------|
| `gnome/dconf.conf` | dconf dump / 完整备份（含快捷键、主题、扩展配置等） |
| `gnome/extensions.sh` | 17 个扩展安装脚本 |
| `gnome/wallpaper.jpg` | 桌面/锁屏壁纸 |

## 关键设置摘要

### 外观

| 设置 | 值 |
|------|-----|
| 配色方案 | `prefer-dark`（深色模式） |
| 强调色 | `purple`（紫色） |
| GTK 主题 | `Adwaita` |
| WM 主题 | `catppuccin-macchiato-mauve-standard+default` |
| 图标主题 | `Adwaita` |
| 缩放 | 125%（1920×1200） |

### 快捷键

| 快捷键 | 操作 |
|--------|------|
| Super+1~4 | 切换工作区 |
| Shift+Super+1~4 | 移动窗口到工作区 |
| Super+Q | 关闭窗口 |
| Super+F | 最大化 |
| Super+B | chromium |
| Super+T | ghostty |
| Ctrl+Alt+S | missioncenter |

### 已安装扩展（17 个）

参见 `gnome/extensions.sh` 中的完整 UUID 列表。

## AI 恢复命令

```bash
# 恢复 dconf 设置
dconf load / < ~/refs/arch-linux-config/gnome/dconf.conf

# 安装扩展
bash ~/refs/arch-linux-config/gnome/extensions.sh

# 恢复壁纸
mkdir -p ~/.local/share/backgrounds
cp ~/refs/arch-linux-config/gnome/wallpaper.jpg ~/.local/share/backgrounds/
gsettings set org.gnome.desktop.background picture-uri \
  "file://$HOME/.local/share/backgrounds/wallpaper.jpg"
gsettings set org.gnome.desktop.screensaver picture-uri \
  "file://$HOME/.local/share/backgrounds/wallpaper.jpg"
```
