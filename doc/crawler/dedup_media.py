#!/usr/bin/env python3
"""清理素材库中的重复文件（基于 MD5 hash）"""
import hashlib
import os
from pathlib import Path
from collections import defaultdict

MEME_DIR = Path("/root/dreamX/doc/memes")
BGM_DIR = Path("/root/dreamX/doc/bgm")

def file_hash(filepath, block_size=8192):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def dedup_dir(base_dir, ext_filter=None):
    """扫描目录，找出重复文件，保留第一个，删除后续"""
    hash_map = defaultdict(list)
    
    for root, dirs, files in os.walk(base_dir):
        for f in sorted(files):
            if ext_filter and not any(f.endswith(e) for e in ext_filter):
                continue
            fp = os.path.join(root, f)
            try:
                fh = file_hash(fp)
                hash_map[fh].append(fp)
            except:
                pass
    
    removed = 0
    for fh, paths in hash_map.items():
        if len(paths) > 1:
            # 保留第一个（按路径排序），删除其余
            keep = paths[0]
            for dup in paths[1:]:
                size = os.path.getsize(dup)
                print(f"  🗑 删除重复: {dup} ({size//1024}KB) == {os.path.basename(keep)}")
                os.remove(dup)
                removed += 1
    return removed, len(hash_map)

print("=== 表情包去重 ===")
meme_removed, meme_unique = dedup_dir(MEME_DIR, ['.gif', '.png', '.jpg', '.webp'])
print(f"  唯一: {meme_unique}, 删除重复: {meme_removed}")

print("\n=== BGM 去重 ===")
bgm_removed, bgm_unique = dedup_dir(BGM_DIR, ['.mp3', '.wav', '.ogg'])
print(f"  唯一: {bgm_unique}, 删除重复: {bgm_removed}")

print(f"\n总计删除: {meme_removed + bgm_removed} 个重复文件")
