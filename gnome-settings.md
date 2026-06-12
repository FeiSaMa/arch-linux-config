# GNOME 桌面配置

## 外观

| 设置 | 值 |
|------|-----|
| 配色方案 | `prefer-dark`（深色模式） |
| 强调色 | `purple`（紫色） |
| GTK 主题 | `Adwaita` |
| WM 主题 | `catppuccin-macchiato-mauve-standard+default` |
| 图标主题 | `Adwaita` |
| 壁纸 | 自定义图片（WallpaperEngine） |
| 锁屏壁纸 | 同上 |
| 按钮布局 | `appmenu:`（仅应用菜单） |
| 缩放 | 125%（1920×1200） |

## 快捷键

| 快捷键 | 操作 |
|--------|------|
| Super+1~4 | 切换工作区 |
| Shift+Super+1~4 | 移动窗口到工作区 |
| Shift+Super+A/D | 工作区左/右移动 |
| Super+Q | 关闭窗口 |
| Super+F | 最大化 |
| Super+M | 显示桌面 |
| Shift+Alt+F | 全屏 |
| Alt+Tab | 应用切换 |
| Super+G | 应用概览 |
| Shift+Ctrl+S | 快速设置 |

### 自定义启动快捷键

| 快捷键 | 命令 | 说明 |
|--------|------|------|
| Super+B | chromium | 浏览器 |
| Super+T | ghostty | 终端 |
| Ctrl+Alt+S | missioncenter | 系统监视器 |
| Super+E | nautilus | 文件管理器 |

## GNOME Shell 扩展（19 个）

```
user-theme@gnome-shell-extensions       # Shell 主题
kimpanel@kde.org                        # Fcitx5 输入法面板
appindicatorsupport@rgcjonas.gmail.com  # 系统托盘
caffeine@patapon.info                   # 防息屏
lockkeys@vaina.lt                       # 大小写/数字锁定提示
clipboard-indicator@tudmotu.com         # 剪贴板历史（Super+V）
gnome-fuzzy-app-search                  # 模糊应用搜索
tilingshell@ferrarodomenico.com         # 窗口平铺（4 布局）
steal-my-focus-window                   # 新窗口自动获焦
Vitals@CoreCoding.com                   # 系统监视器
auto-power-profile@dmy3k.github.io     # 自动电源模式
workspace-indicator                     # 工作区指示器
unlockDialogBackground@sun.wxg@gmail.com # 自定义锁屏背景
blur-my-shell@aunetx                    # 毛玻璃效果
hidetopbar@mathieu.bidon.ca             # 自动隐藏顶栏
burn-my-windows@schneegans.github.com   # 窗口动画
Logo-menu@aryan_k                       # 开始菜单
user-theme@gnome-shell-extensions       # Shell 主题
```

## Tiling Shell 布局

4 套自定义平铺布局（左栏+主区域+右栏等比例），快捷键：
- `Super+W/A/S/D` 方向移动窗口
- `Alt+Super+W/A/S/D` 跨屏移动
- `Super+C` 取消平铺
- 内间距 8px

## Blur My Shell

- 面板/应用文件夹/Dash to Dock/窗口列表均启用模糊
- 亮度 0.6，sigma 30

## Vitals 传感器

内存使用、网络接收速率、风扇转速、最高温度、CPU 频率（1s 更新）

## Clipboard Indicator

`Super+V` 打开剪贴板历史

## Caffeine

一键防息屏，支持 CLI 切换

## Logo Menu

Arch 图标，绑定 missioncenter + ghostty

## Burn My Windows

glide 动画，100ms

## Unlock Dialog Background

自定义锁屏背景（同桌面壁纸）

## 收藏应用（Dock）

```
chromium.desktop
code.desktop
com.mitchellh.ghostty.desktop
moekoemusic.desktop
Clash Verge.desktop
org.prismlauncher.PrismLauncher.desktop
org.gnome.Nautilus.desktop
```

## 应用文件夹

- **System**（8 个）：设置、Extension Manager、软件中心、Tweaks、Refine 等
- **Tools**（13 个）：磁盘工具、归档管理器、Mission Center、时钟、Foliate、Fragments 等

## 其他

| 设置 | 值 |
|------|-----|
| 闲置超时 | 60 秒 |
| 触摸板 | 双指滚动 |
| 屏幕使用限制 | 8 小时/天 |
| 用眼提醒 | 开启 |
| 活动提醒 | 30 分钟/5 分钟 |
| 电源模式偏好 | performance |
