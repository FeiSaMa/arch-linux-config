# 文件系统布局

## 磁盘分区

```
nvme0n1 (953.9G)
├── nvme0n1p1  200M  vfat   (Windows 恢复)
├── nvme0n1p2   16M         (Microsoft 保留)
├── nvme0n1p3  700G  ntfs   (Windows C:)
├── nvme0n1p4  841M  ntfs   (Windows 恢复)
├── nvme0n1p5  477M  vfat   → /efi  (EFI 系统分区)
└── nvme0n1p6  252G  btrfs  → / + /home

zram0           31G  swap   ZRAM 压缩交换
```

## Btrfs 子卷布局

```
nvme0n1p6 (252G, btrfs)
├── @        → /          (根文件系统)
├── @home    → /home      (用户数据)
├── .snapshots            (snapper 快照存储)
```

## 挂载参数

```ini
/      → compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=/@
/home  → compress=zstd:3,ssd,discard=async,space_cache=v2,subvol=/@home
/efi   → vfat 默认参数
```

## Snapper 快照配置

- 根卷（root）和家卷（home）各有一套快照配置
- `snap-pac`：每次 pacman 事务前自动创建快照
- `grub-btrfsd`：快照自动出现在 GRUB 菜单，可引导
