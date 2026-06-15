# T14 Gen1 路由监控面板 开发日志

## 概述

为 T14 Gen1 软路由开发了一个全屏 TTY 监控面板，显示在 tty2（Alt+F2 切换）。左半边：实时路由流量 + 连接列表，右半边：fastfetch 系统信息 + Arch ASCII 标志。

## 最终文件

| 文件 | 路径 | 用途 |
|------|------|------|
| 监控脚本 | `/usr/local/bin/router-mon.py` | curses 全屏 TUI 主程序 |
| systemd 服务 | `/etc/systemd/system/router-mon.service` | 开机在 tty2 自启 |
| 控制台字体 | `/etc/vconsole.conf` | ter-132b（16×32px，120 列 × 33 行） |
| WiFi IP 服务 | `/etc/systemd/system/wifi-lan-ip.service` | 分配 192.168.2.1/24 给 wlp0s20f3 |
| nftables 防火墙 | `/etc/nftables.conf` | NAT + DNS redirect + Meta 转发 |
| dnsmasq DHCP | `/etc/dnsmasq.conf` | LAN DHCP 192.168.2.50-200 |
| hostapd WiFi | `/etc/hostapd/hostapd.conf` | WiFi AP 配置 |
| Mihomo 代理 | `/etc/mihomo/config.yaml` | TUN 透明代理 + fake-ip DNS |
| IP 转发 | `/etc/sysctl.d/99-ip-forward.conf` | net.ipv4.ip_forward=1 |
| 合盖不休眠 | `/etc/systemd/logind.conf` | HandleLidSwitch=ignore |
| 屏幕不熄灭 | `/etc/default/grub` | consoleblank=0 |
| sudo 免密 | `/etc/sudoers.d/feisama` | feisama NOPASSWD: ALL |
| NM unmanaged WiFi | `/etc/NetworkManager/conf.d/90-unmanaged-wifi.conf` | NM 不管 wlp0s20f3 |

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

## 重启后追加的问题

### 10. 合盖会导致路由器休眠
- systemd-logind 默认 `HandleLidSwitch=suspend`
- **修复**: `/etc/systemd/logind.conf` 设为 `HandleLidSwitch=ignore`

### 11. 屏幕自动熄灭
- Linux 控制台默认 10 分钟无输入后关屏
- **修复**: GRUB 加 `consoleblank=0` 内核参数

### 12. vconsole.conf 字体写错
- 写了 `FONT=ter-228b`（14×28px），应为 `ter-132b`（16×32px）
- **修复**: 更正为 `FONT=ter-132b`
- **验证**: 重启后 `stty -F /dev/tty2 size` → `33 120` ✓

### 重启验证结果

```
mihomo          enabled=active     ✅
nftables        enabled=inactive   ✅ (oneshot, rules loaded)
dnsmasq         enabled=active     ✅
hostapd         enabled=active     ✅
router-mon      enabled=active     ✅
wifi-lan-ip     enabled=active     ✅
WAN IP:         192.168.1.195      ✅
WiFi IP:        192.168.2.1        ✅
net.ipv4.ip_forward = 1           ✅
Font:           120×33 (ter-132b)  ✅
```

---

## 2026-06-15 NAS 配置 + 5GHz 尝试期间引发的问题

### 13. router-mon 报错 TypeError: 'NoneType' object is not iterable

- **现象**: 监控面板顶部条报错，左右面板空白
- **位置**: `router-mon.py` line 129 `for c in conns:`
- **根因**: Mihomo API `/connections` 偶尔返回 `{"connections": null}`。`d.get("connections", [])` 在 key 存在但值为 `null` 时返回 `None` 而非默认值 `[]`
- **修复**: `d.get("connections", [])` → `d.get("connections") or []`

### 14. nftables 规则 ifindex 过期 — LAN 全断

- **现象**: iPad 连上 WiFi（WPA 握手成功）但拿不到 IP，反复连上→断开
- **根因**: 5GHz 解锁过程多次 `modprobe -r`→`modprobe` 重载 WiFi 模块，`wlp0s20f3` 接口被销毁并重新创建，ifindex 从 3 变为 13。nftables 规则缓存的是旧 ifindex（`iif 3`），导致 `chain input iif 3 accept` 不匹配新接口，所有 LAN 入站流量（含 DHCP）被 `policy drop` 丢弃
- **附带故障**: `wifi-lan-ip.service` 在模块卸载期间尝试 `ip addr del`，但此时 `wlp0s20f3` 不存在，报错 `Cannot find device`，服务进入 failed 状态，IP 未重新分配
- **修复**:
  ```bash
  sudo nft -f /etc/nftables.conf           # 按名称重新加载，不再用数字 ifindex
  sudo ip addr replace 192.168.2.1/24 dev wlp0s20f3  # 手动恢复 IP
  sudo systemctl reset-failed wifi-lan-ip  # 清除失败状态
  sudo systemctl restart wifi-lan-ip dnsmasq
  ```
- **教训**: nftables 配置文件中接口应始终用名称（`wlp0s20f3`）而非数字索引（`3`）。当前 `/etc/nftables.conf` 已使用名称，问题出在运行时缓存的旧规则。未来若需重载模块，务必同时 `nft -f /etc/nftables.conf`。

### 15. 5GHz AP 模式解锁失败 — Intel CNVi 固件硬限制

- **尝试过的手段**:
  - `cfg80211.ieee80211_regdom=CN` 内核参数（通过 `/etc/kernel/cmdline` + UKI 重建）
  - `iw reg set CN`
  - 安装 `wireless-regdb`（提供 `regulatory.db`）
  - 移除 `ieee80211d=1 country_code=CN`（避免触发 COUNTRY_UPDATE 重检）
  - 换信道 36/149/各种组合
- **结果**: 全部失败。`iw list` 显示通用信道无 `(no IR)`，但 hostapd 通过 nl80211 查询 AP 模式信道时，iwlwifi 固件对所有 5GHz 信道统一返回 `NO_IR`
- **根因**: Intel CNVi WiFi (8086:02f0, iwlwifi 自管 regulatory 模式) 的固件层面硬编码 5GHz AP 禁止。不由 kernel regdomain 或 hostapd 配置控制的
- **结论**: T14 Gen1 内置 WiFi 仅支持 2.4GHz 802.11n 20MHz AP 模式（130 Mbps 上限）。需外接 USB 5GHz 网卡（推荐 MT7612U 芯片）才能解锁 5GHz
- **Samba 速度影响**: 2.4GHz 130 Mbps → 实际 SMB 4-6 MB/s。5GHz 867 Mbps → 预期 80+ MB/s
