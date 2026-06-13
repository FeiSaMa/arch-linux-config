# 系统提权规则

## 权限提升
当需要 root 权限时，始终使用 `pkexec` 而非 `sudo`。

- 原因：本机的 `pam_faillock` 配置在 sudo 失败 3 次后锁定账户 10 分钟
- `pkexec` 会弹出 GNOME 图形化授权对话框，体验更好
- 示例：`pkexec cp file /etc/somewhere`

## GRUB 配置
GRUB 配置文件位于 `/etc/default/grub`，修改后需运行：
```
pkexec grub-mkconfig -o /boot/grub/grub.cfg
```

## 配置同步规则

### 系统配置参考
涉及系统配置文件（如 `/etc/` 下的文件）的修改，先参考 `~/refs/arch-linux-config/` 中的已有文档。

### 硬件配置参考
涉及硬件相关修改（如 ThinkPad 电源管理、内核参数、CPU/GPU 调优等），先参考 `~/refs/arch-linux-config/hardware/` 中的已有文档。

### 同步到 Git
对系统或硬件做出任何更改后，需同步到仓库并推送到 GitHub：

更新 `~/refs/arch-linux-config/` 中的文件（含 `hardware-tuning/` 子目录），然后：
```
git -C ~/refs/arch-linux-config add -A
git -C ~/refs/arch-linux-config commit -m "描述更改内容"
git -C ~/refs/arch-linux-config push
```
