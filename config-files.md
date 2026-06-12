# 修改的系统配置文件

## /etc/pacman.conf

```ini
[options]
Color
ParallelDownloads = 5
[multilib]
Include = /etc/pacman.d/mirrorlist
[archlinuxcn]
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch
```

## /etc/default/grub

```ini
GRUB_DEFAULT=saved
GRUB_CMDLINE_LINUX_DEFAULT="loglevel=5 zswap.enabled=0 nmi_watchdog=0"
```

## /etc/fstab

```ini
# /dev/nvme0n1p6 (btrfs)
UUID=5ab890af-...  /     btrfs  rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=/@  0 0
UUID=5ab890af-...  /home btrfs  rw,relatime,compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=/@home  0 0
# /dev/nvme0n1p5 (vfat → /efi)
UUID=9485-0A61     /efi  vfat   rw,...  0 2
```

## /etc/systemd/journald.conf（Pacman hook 自动注入）

```ini
[Journal]
SystemMaxUse=500M
```

## /etc/mkinitcpio.conf（Pacman hook 自动维护）

```ini
MODULES=(thinkpad_acpi)
HOOKS=(base systemd autodetect microcode modconf kms keyboard sd-vconsole block filesystems fsck)
```

## /etc/environment

```ini
EDITOR=nvim
XIM=fcitx
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
```

## /etc/modprobe.d/99-thinkfan.conf

```ini
options thinkpad_acpi fan_control=1
```

## /etc/NetworkManager/conf.d/20-connectivity.conf

```ini
[connectivity]
enabled=false
```

## /etc/sysctl.d/99-swappiness.conf

```ini
vm.swappiness=1
```

## /etc/systemd/zram-generator.conf

```ini
[zram0]
zram-size = ram
compression-algorithm = zstd
```

## /etc/locale.conf

```ini
LANG=zh_CN.UTF-8
```

## /etc/hostname

```
ThinkPad
```

## /etc/adjtime

```
0.000000 1781050430 0.000000
1781050430
UTC
```

## /etc/pacman.d/mirrorlist

安装时由 reflector 在中国镜像中生成：
```
reflector -a 12 -c cn -f 10 --sort score
```

## /etc/pacman.d/hooks/（2 个自定义 hook）

### 00-journald-size.hook
```
[Trigger]
Operation = Upgrade
Type = Package
Target = systemd

[Action]
Description = Merging SystemMaxUse=500M into /etc/systemd/journald.conf...
When = PostTransaction
Exec = /bin/sh -c 'grep -q "^SystemMaxUse=500M" /etc/systemd/journald.conf || echo "SystemMaxUse=500M" >> /etc/systemd/journald.conf'
```

### 01-mkinitcpio-thinkpad.hook
```
[Trigger]
Operation = Upgrade
Type = Package
Target = mkinitcpio

[Action]
Description = Ensuring MODULES=(thinkpad_acpi) in /etc/mkinitcpio.conf...
When = PostTransaction
Exec = /bin/sh -c 'grep -q "^MODULES=(thinkpad_acpi)" /etc/mkinitcpio.conf || sed -i "s/^MODULES=()/MODULES=(thinkpad_acpi)/" /etc/mkinitcpio.conf'
```
