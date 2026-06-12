# 内核与引导

## 内核

| 内核 | 状态 | 类型 |
|------|------|------|
| linux-zen 7.0.11.zen1-1 | 默认 | 自定义/抢占式桌面内核 |
| linux-lts 6.18.35-1 | 备用 | 长期支持内核 |

两者均安装了对应的头文件（`linux-zen-headers`、`linux-lts-headers`）。

## GRUB 引导

- GRUB 2.14
- UEFI 模式 (`/efi`)
- GRUB 配置：`/etc/default/grub`
- 内核命令行：`loglevel=5 zswap.enabled=0 nmi_watchdog=0 rootflags=subvol=@`
- 默认启动项：`saved`（记住上次选择）

## mkinitcpio

```ini
MODULES=(thinkpad_acpi)
HOOKS=(base systemd autodetect microcode modconf kms keyboard sd-vconsole block filesystems fsck)
```

- `microcode` hook 加载 Intel 微码更新
- `MODULES=(thinkpad_acpi)` 由 pacman hook 维护

## initramfs

```
/boot/
├── vmlinuz-linux-zen        # 默认内核
├── initramfs-linux-zen.img
├── vmlinuz-linux-lts        # LTS 备用内核
├── initramfs-linux-lts.img
└── intel-ucode.img          # Intel 微码
```

## 系统启动目标

`graphical.target`（GNOME 显示管理器 `gdm.service` 拉入）

## Btrfs 快照启动

`grub-btrfsd` 将 snapper 快照自动添加到 GRUB 菜单，支持直接从快照启动。
