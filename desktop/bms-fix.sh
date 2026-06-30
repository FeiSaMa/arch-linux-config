#!/bin/bash
# 修复 Blur My Shell 面板模糊分配竞态导致的日志刷屏
# 每次扩展更新后运行此脚本重新打补丁
# 用法: bash bms-fix.sh

EXT_DIR="$HOME/.local/share/gnome-shell/extensions/blur-my-shell@aunetx"
PANEL_JS="$EXT_DIR/components/panel.js"

if [ ! -f "$PANEL_JS" ]; then
    echo "Blur My Shell extension not found at $EXT_DIR"
    exit 1
fi

if grep -q 'this\.update_size(actors);' "$PANEL_JS"; then
    python3 -c "
import re
with open('$PANEL_JS', 'r') as f:
    content = f.read()
# remove the immediate update_size call that precedes queue_update_size
content = re.sub(
    r\"(// update the size of the actor\n)\s*this\.update_size\(actors\);\n\s*(this\.queue_update_size\(actors\);\n)\",
    r'\1        \2',
    content
)
with open('$PANEL_JS', 'w') as f:
    f.write(content)
"
    echo "Patched. Restart Shell: busctl --user call org.gnome.Shell /org/gnome/Shell org.gnome.Shell Eval s 'Meta.restart(\"Restarting…\")'"
else
    echo "Already patched."
fi
