# 修改的系统配置文件

所有文件的实际内容见 `files/etc/` 目录。

## 文件清单

| 目标路径 | 仓库路径 |
|----------|---------|
| `/etc/environment` | `files/etc/environment` |
| `/etc/sysctl.d/99-swappiness.conf` | `files/etc/sysctl.d/99-swappiness.conf` |
| `/etc/systemd/zram-generator.conf` | `files/etc/systemd/zram-generator.conf` |
| `/etc/modprobe.d/99-thinkfan.conf` | `files/etc/modprobe.d/99-thinkfan.conf` |
| `/etc/NetworkManager/conf.d/20-connectivity.conf` | `files/etc/NetworkManager/conf.d/20-connectivity.conf` |
| `/etc/pacman.d/hooks/merge-journald-conf.hook` | `files/etc/pacman.d/hooks/merge-journald-conf.hook` |
| `/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook` | `files/etc/pacman.d/hooks/merge-mkinitcpio-conf.hook` |
| `/etc/thinkfan.conf` | `files/etc/thinkfan.conf` |
| `/etc/pacman.conf` | `files/etc/pacman.conf` |
| `/etc/locale.conf` | `files/etc/locale.conf` |
| `/etc/hostname` | `files/etc/hostname` |
| `/etc/adjtime` | `files/etc/adjtime` |

## 额外说明

### /etc/default/grub

```ini
GRUB_DEFAULT=saved
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=5 zswap.enabled=0 nmi_watchdog=0 mitigations=off rootflags=subvol=@"
```

注：`rootflags=subvol=@` 是 Btrfs 子卷参数，新机器需根据实际分区调整 UUID 和子卷名。

### /etc/fstab

```ini
# /dev/nvme0n1p6 (btrfs)
UUID=...  /     btrfs  rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=/@  0 0
UUID=...  /home btrfs  rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=/@home  0 0
# /dev/nvme0n1p5 (vfat → /efi)
UUID=...  /efi  vfat   rw,...  0 2
```

### /etc/systemd/journald.conf

Pacman hook 自动追加 `SystemMaxUse=500M`。

### /etc/mkinitcpio.conf

```ini
MODULES=(thinkpad_acpi)
HOOKS=(base systemd autodetect microcode modconf kms keyboard sd-vconsole block filesystems fsck)
```

Pacman hook 自动维护 `MODULES=(thinkpad_acpi)`。

### /etc/pacman.d/mirrorlist

由 reflector 在中国镜像中生成：
```
reflector -a 12 -c cn -f 10 --sort score
```

## AI 恢复命令

```bash
# 读取 files/etc/ 下每个文件并写入对应系统路径
# AI 先读取文件内容，然后用 sudo tee 写入

# 示例（AI 逐文件执行）：
# AI 读取 files/etc/environment → sudo tee /etc/environment
# AI 读取 files/etc/hostname → sudo tee /etc/hostname
# ...
```
