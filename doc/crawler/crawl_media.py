#!/usr/bin/env python3
"""
DreamX 素材库爬取 v3
- 表情包: agent-browser + Giphy（绕过国内网络限制）
- BGM: Mixkit preview MP3（直接 curl 下载）
- 结果写入 SQLite
"""
import asyncio
import aiosqlite
import subprocess
import json
import os
import sys
import re
import time
import base64
import hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/root/dreamX/doc")
MEME_DIR = BASE_DIR / "memes"
BGM_DIR = BASE_DIR / "bgm"
DB_PATH = Path(__file__).parent / "media_library.db"

# === 优先级配置 ===
MEME_PRIORITIES = [
    ("cat meme funny", "cat_funny", ["搞笑", "离谱"], 1),
    ("shocked cat surprised", "cat_shocked", ["震惊", "离谱"], 1),
    ("crying cat sad meme", "cat_crying", ["委屈"], 1),
    ("angry cat furious meme", "cat_angry", ["愤怒", "吐槽"], 1),
    ("tom and jerry meme", "tom_jerry", ["搞笑", "离谱"], 1),
    ("tired exhausted work meme", "tired", ["委屈", "吐槽"], 2),
    ("facepalm speechless meme", "facepalm", ["无语", "吐槽"], 2),
    ("cheems doge meme", "cheems", ["搞笑", "离谱"], 2),
    ("unbelievable wtf meme", "wtf", ["离谱", "震惊"], 2),
    ("happy excited celebration", "happy", ["欢快"], 2),
    ("cute cat kawaii", "cute", ["可爱", "害羞"], 3),
    ("funny reaction laugh", "funny_reaction", ["搞笑"], 3),
]

# Mixkit 分类页面 → 直接解析 preview MP3 链接
MIXKIT_CATEGORIES = [
    ("funny", "/free-stock-music/funny/", "funny", ["搞笑", "离谱", "吐槽"], 1),
    ("happy", "/free-stock-music/happy/", "happy", ["欢快", "可爱"], 1),
    ("jazz", "/free-stock-music/jazz/", "jazz", ["吐槽", "震惊"], 2),
    ("dramatic", "/free-stock-music/dramatic/", "dramatic", ["震惊", "愤怒"], 2),
    ("sad", "/free-stock-music/sad/", "sad", ["委屈"], 3),
    ("children", "/free-stock-music/children/", "children", ["搞笑", "可爱"], 3),
]


def run_agent_browser(cmd: str, timeout: int = 20) -> str:
    """执行 agent-browser 命令"""
    try:
        result = subprocess.run(
            ["agent-browser"] + cmd.split() if isinstance(cmd, str) else ["agent-browser"] + cmd,
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return f"ERROR: {e}"


def run_agent_browser_eval(js: str, timeout: int = 30) -> str:
    """执行 agent-browser eval"""
    try:
        result = subprocess.run(
            ["agent-browser", "eval", js],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        return f"ERROR: {e}"


async def crawl_giphy_memes(db, keyword: str, save_dir: str, moods: list, max_count: int = 10):
    """用 agent-browser 从 Giphy 搜索并下载表情包"""
    dir_path = MEME_DIR / save_dir
    dir_path.mkdir(parents=True, exist_ok=True)

    print(f"  🌐 打开 Giphy 搜索: {keyword}")
    search_url = f"https://giphy.com/search/{keyword.replace(' ', '-')}"
    run_agent_browser(f"open {search_url} --timeout 15000")
    await asyncio.sleep(3)

    # 提取 GIF 链接
    js_extract = """
JSON.stringify(
  Array.from(document.querySelectorAll('img[src*="giphy.com/media"]'))
    .filter(i => i.src.endsWith('.gif') && i.alt)
    .slice(0, """ + str(max_count * 2) + """)
    .map(i => {
      const parts = i.src.split('/media/');
      let giphyId = '';
      if (parts.length > 1) {
        const seg = parts[1].split('/');
        // 跳过 v1.xxx 格式的 segment
        giphyId = seg.find(s => !s.startsWith('v1.') && s.length > 5 && s.length < 30) || seg[1] || '';
      }
      return {url: i.src, alt: i.alt, id: giphyId};
    })
)
"""
    raw = run_agent_browser_eval(js_extract)
    if not raw or raw.startswith("ERROR"):
        print(f"  ❌ 提取链接失败: {raw}")
        return 0

    try:
        # 去掉外层引号
        if raw.startswith('"') and raw.endswith('"'):
            raw = json.loads(raw)
        items = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ❌ JSON 解析失败")
        return 0

    print(f"  📋 找到 {len(items)} 个 GIF")

    downloaded = 0
    seen_ids = set()

    for item in items:
        if downloaded >= max_count:
            break

        gif_url = item.get("url", "")
        alt = item.get("alt", "")
        giphy_id = item.get("id", "")

        if not gif_url or not giphy_id or giphy_id in seen_ids:
            continue
        seen_ids.add(giphy_id)

        # 用 200.gif 版本（较小）
        small_url = gif_url.replace("/giphy.gif", "/200.gif").replace("/giphy.webp", "/200.gif")

        meme_id = f"giphy_{giphy_id}"

        # 检查是否已存在
        existing = await db.execute("SELECT id FROM memes WHERE id = ?", (meme_id,))
        if await existing.fetchone():
            continue

        safe_name = re.sub(r'[^\w\-]', '_', alt or giphy_id)[:50]
        filename = f"{safe_name}_{giphy_id}.gif"
        filepath = dir_path / filename

        if filepath.exists():
            continue

        # 在浏览器环境内 fetch → base64 → 写入本地
        js_download = f"""
(async () => {{
  try {{
    const resp = await fetch('{small_url}');
    if (!resp.ok) return JSON.stringify({{error: resp.status}});
    const buf = await resp.arrayBuffer();
    if (buf.byteLength < 1000 || buf.byteLength > 3000000) return JSON.stringify({{error: 'size', size: buf.byteLength}});
    const bytes = new Uint8Array(buf);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
    return JSON.stringify({{b64: btoa(binary), size: buf.byteLength}});
  }} catch(e) {{
    return JSON.stringify({{error: e.message}});
  }}
}})()
"""
        result_raw = run_agent_browser_eval(js_download, timeout=30)
        if not result_raw:
            continue

        try:
            if result_raw.startswith('"'):
                result_raw = json.loads(result_raw)
            result = json.loads(result_raw)
        except:
            continue

        if "error" in result:
            print(f"    ⚠️ {alt[:30]}: {result['error']}")
            continue

        b64_data = result.get("b64", "")
        file_size = result.get("size", 0)
        if not b64_data:
            continue

        # 写入文件
        try:
            filepath.write_bytes(base64.b64decode(b64_data))
        except:
            continue

        # 入库
        await db.execute("""
            INSERT OR IGNORE INTO memes (id, file_path, source, source_url, meme_name, meme_desc, format, file_size)
            VALUES (?, ?, 'giphy', ?, ?, ?, 'gif', ?)
        """, (meme_id, str(filepath), f"https://giphy.com/gifs/{giphy_id}", alt, alt, file_size))

        for mood in moods:
            await db.execute("""
                INSERT OR IGNORE INTO tags (resource_type, resource_id, tag_type, tag_value)
                VALUES ('meme', ?, 'mood', ?)
            """, (meme_id, mood))

        await db.commit()
        downloaded += 1
        print(f"    ⬇️ {filename} ({file_size // 1024}KB)")

    return downloaded


async def crawl_mixkit_bgm(db, name: str, url_path: str, save_dir: str, moods: list, max_count: int = 5):
    """从 Mixkit 下载 BGM（preview MP3）"""
    dir_path = BGM_DIR / save_dir
    dir_path.mkdir(parents=True, exist_ok=True)

    full_url = f"https://mixkit.co{url_path}"
    print(f"  🌐 Mixkit: {full_url}")

    try:
        result = subprocess.run(
            ["curl", "-sL", "--connect-timeout", "10",
             "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
             full_url],
            capture_output=True, text=True, timeout=20
        )
        html = result.stdout
    except:
        print(f"  ❌ 页面获取失败")
        return 0

    # 提取 preview MP3 链接和标题
    # data-audio-player-preview-url-value="https://assets.mixkit.co/music/466/466.mp3"
    pattern = r'data-audio-player-preview-url-value="(https://assets\.mixkit\.co/music/\d+/\d+\.mp3)"'
    mp3_urls = re.findall(pattern, html)

    # 提取标题（在附近的元素中）
    title_pattern = r'class="[^"]*item-grid-card__title[^"]*"[^>]*>([^<]+)<'
    titles = re.findall(title_pattern, html)

    print(f"  📋 找到 {len(mp3_urls)} 首 BGM")

    downloaded = 0
    for i, mp3_url in enumerate(mp3_urls[:max_count]):
        if downloaded >= max_count:
            break

        # 提取 ID
        match = re.search(r'/music/(\d+)/(\d+)\.mp3', mp3_url)
        if not match:
            continue
        mixkit_id = match.group(1)

        bgm_id = f"mixkit_{mixkit_id}"
        existing = await db.execute("SELECT id FROM bgms WHERE id = ?", (bgm_id,))
        if await existing.fetchone():
            continue

        title = titles[i].strip() if i < len(titles) else f"Mixkit Track {mixkit_id}"
        safe_title = re.sub(r'[^\w\-]', '_', title)[:50]
        filename = f"{safe_title}_{mixkit_id}.mp3"
        filepath = dir_path / filename

        if filepath.exists():
            continue

        # 下载
        try:
            dl_result = subprocess.run(
                ["curl", "-sL", "--connect-timeout", "15", "--max-time", "60",
                 "-H", "User-Agent: Mozilla/5.0",
                 "-H", "Referer: https://mixkit.co/",
                 "-o", str(filepath), mp3_url],
                capture_output=True, text=True, timeout=90
            )
        except:
            print(f"    ❌ 下载超时: {title}")
            continue

        if not filepath.exists() or filepath.stat().st_size < 10000:
            filepath.unlink(missing_ok=True)
            continue

        file_size = filepath.stat().st_size
        duration_est = file_size / (256 * 1024 / 8)  # Mixkit 是 256kbps

        await db.execute("""
            INSERT OR IGNORE INTO bgms (id, file_path, source, source_id, title, duration, genre)
            VALUES (?, ?, 'mixkit', ?, ?, ?, ?)
        """, (bgm_id, str(filepath), mixkit_id, title, duration_est, save_dir))

        for mood in moods:
            await db.execute("""
                INSERT OR IGNORE INTO tags (resource_type, resource_id, tag_type, tag_value)
                VALUES ('bgm', ?, 'mood', ?)
            """, (bgm_id, mood))

        await db.commit()
        downloaded += 1
        print(f"    ⬇️ {filename} ({file_size // 1024}KB, ~{duration_est:.0f}s)")

    return downloaded


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    max_memes = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    max_bgms = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    db = await aiosqlite.connect(str(DB_PATH))
    start = time.time()

    print(f"🚀 DreamX 素材爬取 v3 [{mode}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   表情包: agent-browser + Giphy")
    print(f"   BGM: Mixkit preview MP3")
    print()

    total_memes = 0
    total_bgms = 0

    if mode in ("all", "memes"):
        sorted_memes = sorted(MEME_PRIORITIES, key=lambda x: x[3])
        for keyword, save_dir, moods, priority in sorted_memes:
            print(f"🔍 [P{priority}] 表情包: {keyword} → {save_dir}/")
            n = await crawl_giphy_memes(db, keyword, save_dir, moods, max_count=max_memes)
            total_memes += n
            await asyncio.sleep(2)

    if mode in ("all", "bgm"):
        sorted_bgms = sorted(MIXKIT_CATEGORIES, key=lambda x: x[4])
        for name, url_path, save_dir, moods, priority in sorted_bgms:
            print(f"🎵 [P{priority}] BGM: {name} → {save_dir}/")
            n = await crawl_mixkit_bgm(db, name, url_path, save_dir, moods, max_count=max_bgms)
            total_bgms += n

    elapsed = time.time() - start
    print()
    print(f"📊 爬取完成 ({elapsed:.1f}s)")
    print(f"   表情包: +{total_memes}")
    print(f"   BGM: +{total_bgms}")

    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
