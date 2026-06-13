#!/usr/bin/env bash
# GNOME Shell 扩展安装脚本
# 来源：https://github.com/FeiSaMa/arch-linux-config/tree/main/gnome
# 使用方式：bash gnome/extensions.sh

set -euo pipefail

echo "=== 安装 GNOME Shell 扩展 ==="

# 通过 GNOME Extensions CLI 安装 (需要 gnome-browser-connector 或 Extension Manager)
# 备用：从 GitHub Releases 下载 .shell-extension.zip

install_extension() {
    local uuid="$1"
    local url="$2"
    local zip_file="/tmp/${uuid}.shell-extension.zip"

    if gnome-extensions info "$uuid" &>/dev/null; then
        echo "  ✅ $uuid 已安装"
        return 0
    fi

    echo "  📦 安装 $uuid ..."
    if curl -sL "$url" -o "$zip_file" && [ -s "$zip_file" ]; then
        gnome-extensions install --force "$zip_file" 2>/dev/null || true
        echo "  ✅ $uuid 安装完成"
    else
        echo "  ⚠️  $uuid 下载失败，请手动安装"
    fi
    rm -f "$zip_file"
}

# 扩展列表 (UUID → EGO/Release 下载链接)
# 注: .shell-extension.zip 下载链接从 extensions.gnome.org 获取
# 格式: install_extension "UUID" "下载URL"

install_extension "appindicatorsupport@rgcjonas.gmail.com" "https://extensions.gnome.org/extension-data/appindicatorsupportrgcjonas.gmail.com.v63.shell-extension.zip"
install_extension "auto-power-profile@dmy3k.github.io" "https://extensions.gnome.org/extension-data/auto-power-profiledmy3k.github.io.v4.shell-extension.zip"
install_extension "blur-my-shell@aunetx" "https://extensions.gnome.org/extension-data/blur-my-shellaunetx.v72.shell-extension.zip"
install_extension "burn-my-windows@schneegans.github.com" "https://extensions.gnome.org/extension-data/burn-my-windowsschneegans.github.com.v50.shell-extension.zip"
install_extension "caffeine@patapon.info" "https://extensions.gnome.org/extension-data/caffeinepatapon.info.v62.shell-extension.zip"
install_extension "clipboard-indicator@tudmotu.com" "https://extensions.gnome.org/extension-data/clipboard-indicatortudmotu.com.v77.shell-extension.zip"
install_extension "gnome-fuzzy-app-search@gnome-shell-extensions.Czarlie.gitlab.com" "https://extensions.gnome.org/extension-data/gnome-fuzzy-app-searchgnome-shell-extensions.Czarlie.gitlab.com.v7.shell-extension.zip"
install_extension "hidetopbar@mathieu.bidon.ca" "https://extensions.gnome.org/extension-data/hidetopbarmathieu.bidon.ca.v95.shell-extension.zip"
install_extension "kimpanel@kde.org" "https://extensions.gnome.org/extension-data/kimpanelkde.org.v56.shell-extension.zip"
install_extension "lockkeys@vaina.lt" "https://extensions.gnome.org/extension-data/lockkeysvaina.lt.v54.shell-extension.zip"
install_extension "logomenu@aryan_k" "https://extensions.gnome.org/extension-data/logomenuaryan_k.v46.shell-extension.zip"
install_extension "steal-my-focus-window@steal-my-focus-window" "https://extensions.gnome.org/extension-data/steal-my-focus-windowsteal-my-focus-window.v12.shell-extension.zip"
install_extension "tilingshell@ferrarodomenico.com" "https://extensions.gnome.org/extension-data/tilingshellferrarodomenico.com.v22.shell-extension.zip"
install_extension "unlockDialogBackground@sun.wxg@gmail.com" "https://extensions.gnome.org/extension-data/unlockDialogBackgroundsun.wxg@gmail.com.v19.shell-extension.zip"
install_extension "Vitals@CoreCoding.com" "https://extensions.gnome.org/extension-data/VitalsCoreCoding.com.v72.shell-extension.zip"

# 内置扩展
echo "  📦 启用内置扩展..."
gnome-extensions enable user-theme@gnome-shell-extensions.gcampax.github.com 2>/dev/null || true
gnome-extensions enable workspace-indicator@gnome-shell-extensions.gcampax.github.com 2>/dev/null || true

echo ""
echo "=== 安装完成 ==="
echo "请重启 GNOME Shell (Alt+F2 → r) 或重新登录"
