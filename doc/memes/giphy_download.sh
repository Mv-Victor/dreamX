#!/bin/bash
# Giphy 表情包批量下载脚本
# 用法: ./giphy_download.sh <搜索关键词> <保存目录> [数量]

KEYWORD="${1:-funny-reaction}"
SAVE_DIR="${2:-/root/dreamX/doc/memes/default}"
COUNT="${3:-6}"

mkdir -p "$SAVE_DIR"

echo "🔍 搜索: $KEYWORD, 保存到: $SAVE_DIR, 数量: $COUNT"

# 用 agent-browser 搜索 Giphy
agent-browser open "https://giphy.com/search/$KEYWORD" --timeout 15000 2>/dev/null
sleep 2

# 提取 GIF 链接
URLS=$(agent-browser eval "
JSON.stringify(
  Array.from(document.querySelectorAll('img[src*=\"giphy.com/media\"]'))
    .filter(i => i.src.endsWith('.gif'))
    .slice(0, $COUNT)
    .map(i => i.src)
)
" 2>/dev/null | tr -d '"[]' | tr ',' '\n')

# 下载
IDX=1
echo "$URLS" | while read -r url; do
  [ -z "$url" ] && continue
  FNAME="${KEYWORD}_${IDX}.gif"
  echo "⬇️  下载 #$IDX: $FNAME"
  curl -sL "$url" -o "$SAVE_DIR/$FNAME" --max-time 15
  IDX=$((IDX + 1))
done

echo "✅ 完成! 已下载到 $SAVE_DIR"
ls -lh "$SAVE_DIR"
