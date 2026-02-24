#!/usr/bin/env python3
"""初始化素材库 SQLite 数据库"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "media_library.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    -- 角色表
    CREATE TABLE IF NOT EXISTS characters (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        ip TEXT,
        description TEXT,
        search_keywords TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 表情包表
    CREATE TABLE IF NOT EXISTS memes (
        id TEXT PRIMARY KEY,
        file_path TEXT NOT NULL,
        source TEXT,
        source_url TEXT,
        character_id TEXT REFERENCES characters(id),
        meme_name TEXT,
        meme_desc TEXT,
        text_content TEXT,
        format TEXT,
        file_size INTEGER,
        width INTEGER,
        height INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- BGM表
    CREATE TABLE IF NOT EXISTS bgms (
        id TEXT PRIMARY KEY,
        file_path TEXT NOT NULL,
        source TEXT,
        source_id TEXT,
        title TEXT,
        artist TEXT,
        duration REAL,
        genre TEXT,
        avg_rms REAL,
        bpm INTEGER,
        climax_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 标签表（表情包和BGM共用）
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_type TEXT,
        resource_id TEXT,
        tag_type TEXT,
        tag_value TEXT,
        UNIQUE(resource_type, resource_id, tag_type, tag_value)
    );

    -- 角色-BGM关联表
    CREATE TABLE IF NOT EXISTS character_bgm_match (
        character_id TEXT REFERENCES characters(id),
        bgm_id TEXT REFERENCES bgms(id),
        match_score REAL DEFAULT 0.5,
        PRIMARY KEY(character_id, bgm_id)
    );

    -- 使用记录表
    CREATE TABLE IF NOT EXISTS usage_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_type TEXT,
        resource_id TEXT,
        project_id TEXT,
        used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 爬取任务表（追踪进度）
    CREATE TABLE IF NOT EXISTS crawl_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        keyword TEXT,
        category TEXT,
        status TEXT DEFAULT 'pending',
        total_found INTEGER DEFAULT 0,
        total_downloaded INTEGER DEFAULT 0,
        last_error TEXT,
        started_at TIMESTAMP,
        finished_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")

if __name__ == "__main__":
    init_db()
