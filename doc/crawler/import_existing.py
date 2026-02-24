#!/usr/bin/env python3
"""将已有的本地素材导入 SQLite 数据库"""
import sqlite3
import json
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "media_library.db"
MEDIA_LIB_JSON = Path("/root/dreamX/doc/media_library.json")

def import_existing():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    with open(MEDIA_LIB_JSON) as f:
        lib = json.load(f)

    # 导入角色
    for char_id, info in lib.get("characterRegistry", {}).items():
        c.execute("""
            INSERT OR IGNORE INTO characters (id, name, ip, description, search_keywords)
            VALUES (?, ?, ?, ?, ?)
        """, (char_id, char_id, info.get("ip"), info.get("desc"), info.get("searchKeywords")))
    print(f"✅ 导入 {len(lib.get('characterRegistry', {}))} 个角色")

    # 导入表情包
    memes = lib.get("memes", {}).get("library", [])
    for m in memes:
        if not os.path.exists(m["file"]):
            print(f"  ⚠️ 文件不存在: {m['file']}")
            continue
        file_size = os.path.getsize(m["file"])
        c.execute("""
            INSERT OR IGNORE INTO memes (id, file_path, source, meme_name, meme_desc, format, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (m["id"], m["file"], m.get("source", "local"), m.get("memeName"), m.get("memeDesc"), m.get("format", "gif"), file_size))
        for mood in m.get("mood", []):
            c.execute("INSERT OR IGNORE INTO tags (resource_type, resource_id, tag_type, tag_value) VALUES ('meme', ?, 'mood', ?)", (m["id"], mood))
        for tag in m.get("tags", []):
            c.execute("INSERT OR IGNORE INTO tags (resource_type, resource_id, tag_type, tag_value) VALUES ('meme', ?, 'theme', ?)", (m["id"], tag))
    print(f"✅ 导入 {len(memes)} 个表情包")

    # 导入 BGM
    bgms = lib.get("bgm", {}).get("library", [])
    for b in bgms:
        if not os.path.exists(b["file"]):
            print(f"  ⚠️ 文件不存在: {b['file']}")
            continue
        waveform = b.get("waveform", {})
        c.execute("""
            INSERT OR IGNORE INTO bgms (id, file_path, source, source_id, title, artist, duration, genre, avg_rms, bpm, climax_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (b["id"], b["file"], b.get("source"), str(b.get("sourceId", "")), b.get("title"), b.get("artist"),
              b.get("duration"), b.get("genre"), waveform.get("avgRms"), waveform.get("bpm"),
              json.dumps(waveform.get("climaxRanges", []))))
        for mood in b.get("mood", []):
            c.execute("INSERT OR IGNORE INTO tags (resource_type, resource_id, tag_type, tag_value) VALUES ('bgm', ?, 'mood', ?)", (b["id"], mood))
        for tag in b.get("tags", []):
            c.execute("INSERT OR IGNORE INTO tags (resource_type, resource_id, tag_type, tag_value) VALUES ('bgm', ?, 'theme', ?)", (b["id"], tag))
        # 角色-BGM 关联
        for char_name in b.get("memeMatch", []):
            c.execute("INSERT OR IGNORE INTO character_bgm_match (character_id, bgm_id) VALUES (?, ?)", (char_name, b["id"]))
    print(f"✅ 导入 {len(bgms)} 首 BGM")

    conn.commit()
    conn.close()
    print("✅ 导入完成!")

if __name__ == "__main__":
    import_existing()
