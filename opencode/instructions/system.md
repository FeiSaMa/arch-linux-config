# 系统提权规则

## 权限提升
- 当前机器（pam_faillock 已配置）：使用 `pkexec`，sudo 失败 3 次会锁定 10 分钟
- 新安装的机器（pam_faillock 未配置）：使用 `sudo`，pkexec 在 TTY 下需要 polkit 代理

AI 检测规则：`pkexec --version` 成功 → 用 pkexec；否则用 sudo。

示例：
```bash
# 新机器（推荐）
sudo cp file /etc/somewhere

# 当前机器（pam_faillock 已配置）
pkexec cp file /etc/somewhere
```

## GRUB 配置
GRUB 配置文件位于 `/etc/default/grub`，修改后需运行：
```bash
pkexec grub-mkconfig -o /boot/grub/grub.cfg     # 当前机器
sudo grub-mkconfig -o /boot/grub/grub.cfg        # 新机器
```

## 配置同步规则

### 系统配置参考
涉及系统配置文件（如 `/etc/` 下的文件）的修改，先参考 `~/refs/arch-linux-config/` 中的已有文档。

### 硬件配置参考
涉及硬件相关修改（如 ThinkPad 电源管理、内核参数、CPU/GPU 调优等），先参考 `~/refs/arch-linux-config/hardware/` 中的已有文档。

### 同步到 Git
对系统或硬件做出任何更改后，需同步到仓库并推送到 GitHub：

更新 `~/refs/arch-linux-config/` 中的文件（含 `hardware/` 子目录），然后：
```
git -C ~/refs/arch-linux-config add -A
git -C ~/refs/arch-linux-config commit -m "描述更改内容"
git -C ~/refs/arch-linux-config push
```
