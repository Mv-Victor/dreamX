#!/usr/bin/env python3
"""查询素材库状态"""
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "media_library.db"

def status():
    if not DB_PATH.exists():
        print("❌ 数据库不存在，请先运行 init_db.py")
        return

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 表情包统计
    meme_count = c.execute("SELECT COUNT(*) FROM memes").fetchone()[0]
    meme_size = c.execute("SELECT COALESCE(SUM(file_size), 0) FROM memes").fetchone()[0]

    # BGM 统计
    bgm_count = c.execute("SELECT COUNT(*) FROM bgms").fetchone()[0]
    bgm_duration = c.execute("SELECT COALESCE(SUM(duration), 0) FROM bgms").fetchone()[0]

    # 角色统计
    char_count = c.execute("SELECT COUNT(*) FROM characters").fetchone()[0]

    # 标签统计
    tag_count = c.execute("SELECT COUNT(DISTINCT tag_value) FROM tags").fetchone()[0]

    # 按情绪分布
    print("=" * 50)
    print("📊 DreamX 素材库状态")
    print("=" * 50)
    print(f"\n🎭 表情包: {meme_count} 个 ({meme_size / 1024 / 1024:.1f} MB)")
    print(f"🎵 BGM: {bgm_count} 首 (总时长 {bgm_duration / 60:.1f} 分钟)")
    print(f"👤 角色: {char_count} 个")
    print(f"🏷️ 标签: {tag_count} 种")

    # 表情包按目录分布
    print("\n--- 表情包分布 ---")
    rows = c.execute("""
        SELECT 
            REPLACE(REPLACE(file_path, '/root/dreamX/doc/memes/', ''), '/' || SUBSTR(file_path, INSTR(file_path, '/') + 1), '') as dir,
            COUNT(*),
            SUM(file_size) / 1024
        FROM memes 
        GROUP BY dir
        ORDER BY COUNT(*) DESC
    """).fetchall()
    if rows:
        for dir_name, count, size_kb in rows:
            # 简化目录名
            parts = dir_name.split("/")
            short = parts[-1] if parts else dir_name
            print(f"  {short}: {count} 个 ({size_kb:.0f} KB)")
    else:
        print("  (空)")

    # BGM 按目录分布
    print("\n--- BGM 分布 ---")
    rows = c.execute("""
        SELECT 
            REPLACE(file_path, '/root/dreamX/doc/bgm/', '') as path,
            title, duration
        FROM bgms
        ORDER BY duration DESC
    """).fetchall()
    if rows:
        for path, title, dur in rows:
            print(f"  {title or path}: {dur:.0f}s")
    else:
        print("  (空)")

    # 情绪标签分布
    print("\n--- 情绪标签分布 ---")
    rows = c.execute("""
        SELECT tag_value, resource_type, COUNT(*) 
        FROM tags WHERE tag_type='mood'
        GROUP BY tag_value, resource_type
        ORDER BY COUNT(*) DESC
    """).fetchall()
    if rows:
        for tag, rtype, count in rows:
            icon = "🎭" if rtype == "meme" else "🎵"
            print(f"  {icon} {tag}: {count}")
    else:
        print("  (空)")

    # 最近爬取任务
    print("\n--- 最近爬取任务 ---")
    rows = c.execute("""
        SELECT source, keyword, category, status, total_found, total_downloaded, started_at
        FROM crawl_tasks
        ORDER BY id DESC LIMIT 10
    """).fetchall()
    if rows:
        for source, kw, cat, status, found, dl, started in rows:
            icon = "✅" if status == "done" else "❌" if status == "failed" else "🔄"
            print(f"  {icon} [{source}] {kw} → {cat}: {dl}/{found} ({started})")
    else:
        print("  (无)")

    # 磁盘实际文件统计
    print("\n--- 磁盘文件统计 ---")
    meme_dir = Path("/root/dreamX/doc/memes")
    bgm_dir = Path("/root/dreamX/doc/bgm")
    
    meme_files = list(meme_dir.rglob("*.gif")) + list(meme_dir.rglob("*.webp")) + list(meme_dir.rglob("*.jpg")) + list(meme_dir.rglob("*.png"))
    bgm_files = list(bgm_dir.rglob("*.mp3"))
    
    print(f"  表情包文件: {len(meme_files)} 个")
    print(f"  BGM 文件: {len(bgm_files)} 个")

    conn.close()

if __name__ == "__main__":
    status()
