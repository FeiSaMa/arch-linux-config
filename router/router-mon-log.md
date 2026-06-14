# T14 Gen1 路由监控面板 开发日志

## 概述

为 T14 Gen1 软路由开发了一个全屏 TTY 监控面板，显示在 tty2（Alt+F2 切换）。左半边：实时路由流量 + 连接列表，右半边：fastfetch 系统信息 + Arch ASCII 标志。

## 最终文件

| 文件 | 路径 | 用途 |
|------|------|------|
| 监控脚本 | `/usr/local/bin/router-mon.py` | curses 全屏 TUI 主程序 |
| systemd 服务 | `/etc/systemd/system/router-mon.service` | 开机在 tty2 自启 |
| 控制台字体 | `/etc/vconsole.conf` | ter-132b（16×32px，120 列 × 33 行） |

## 关键依赖

```bash
pacman -S python-rich terminus-font fastfetch
```

Rich 最终未使用（curses 替代了它），保留以备将来。

## 架构

```
tty2 (1920×1080, ter-132b 字体 → 120 列 × 33 行)
  └─ systemd router-mon.service
       ├─ ExecStartPre: setfont ter-132b
       └─ ExecStart: router-mon.py (curses)
            ├─ 左面板 (60 列): 速率、连接、代理节点
            ├─ 右面板 (60 列): Arch logo + fastfetch
            └─ 数据源: Mihomo REST API (127.0.0.1:9097)
```

## 遇到的问题和修复

### 1. 字体太小 / 不匹配
- **第一次尝试**: ter-132n（16×32px 普通）→ 120 列 × 33 行，字体太小
- **第二次尝试**: ter-228b → 实际是 14×28px，更小
- **最终**: ter-132b（16×32px 加粗）→ 120 列 × 33 行，合适

### 2. 显示全是大括号标记 [bold cyan]
- Rich 的 Text.append("[bold cyan]UP[/]") 在 TTY 上不解析 markup
- 改用 curses 库，显式 `Text("str", style=...)` 也不行
- **最终**: 放弃 Rich，用 curses 标准库重写，所有颜色用 `curses.color_pair()`

### 3. fps 刷新率混乱
- 最初 1fps：`time.sleep(FPS)` = sleep(1) ✓
- 改 60fps: `time.sleep(60)` = sleep(60) ✗ 睡了 60 秒
- 改 10fps: `time.sleep(10)` = sleep(10) ✗ 睡了 10 秒
- **最终**: `time.sleep(1/FPS)` + 默认 FPS=1

### 4. 底部白线截断
- 每行 `60+空格+60 = 121 字符`，120 列终端换行
- **修复**: 去空格，60+60=120
- **再次出现**: `clrtoeol()` 清掉了竖线
- **最终**: 竖线在所有内容之后画

### 5. 所有连接都显示 P (Proxy)
- 用 `c.get("rule")` 判断，但 Mihomo 返回的是 "Match"/"GeoSite"
- **修复**: 改用 `c.get("chains")[0]` 判断实际路由（DIRECT/PROXY/REJECT）

### 6. TTY 不支持中文
- Linux 控制台 PSF 字体无 CJK 字符
- **修复**: `sanitize()` 函数——台湾→TW、硅谷→SV 等映射 + 正则删除所有 CJK/Emoji

### 7. Node 显示 "DIRECT ?"
- get_proxies() 取了 Selector 类型组（当前选 DIRECT）
- **修复**: 取 URLTest 组（自动选最快节点）+ 单独查节点延迟

### 8. 速度峰值第一条把条撑满
- 首页 `pu=0` 但 `ul=API累计值`，第一帧算出差速极大 → peak 虚假
- **修复**: `pu=pd=None`，第一帧跳过速度计算

### 9. 内存/磁盘占用条不显示
- `fill = int(5/100*12) = 0` → 低百分比时 0 个 #
- **修复**: `fill = max(1, int(...)) if pct > 0 else 0`

## 配色参考（快照）

- UP/DN 标题：白色加粗
- PROXY 连接：紫色 (5)
- DIRECT 连接：绿色 (2)
- REJECT 连接：红色 (1)
- Arch logo：青色 (6) 加粗
- 提示符：白色加粗
