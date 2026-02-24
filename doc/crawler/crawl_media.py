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
    # --- 原有分类 ---
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
    # --- 国际梗 ---
    ("pepe frog meme", "pepe_frog", ["搞笑", "吐槽"], 1),
    ("doge meme shiba", "doge", ["搞笑", "可爱"], 1),
    ("wojak meme", "wojak", ["吐槽", "委屈"], 1),
    ("nyan cat meme", "nyan_cat", ["搞笑", "欢快"], 2),
    ("grumpy cat meme", "grumpy_cat", ["吐槽", "无语"], 1),
    ("surprised pikachu meme", "surprised_pikachu", ["震惊", "搞笑"], 1),
    ("drake meme approve disapprove", "drake", ["搞笑", "吐槽"], 1),
    ("distracted boyfriend meme", "distracted_boyfriend", ["搞笑", "离谱"], 2),
    ("this is fine dog fire", "this_is_fine", ["无语", "离谱"], 1),
    ("stonks meme", "stonks", ["搞笑", "离谱"], 2),
    ("galaxy brain meme", "galaxy_brain", ["搞笑", "离谱"], 2),
    ("expanding brain meme", "expanding_brain", ["搞笑", "离谱"], 2),
    ("spongebob meme", "spongebob", ["搞笑", "吐槽"], 1),
    ("patrick star meme", "patrick_star", ["搞笑", "可爱"], 2),
    ("shrek meme", "shrek", ["搞笑", "离谱"], 2),
    ("thanos meme snap", "thanos", ["震惊", "离谱"], 2),
    ("baby yoda grogu meme", "baby_yoda", ["可爱", "搞笑"], 1),
    ("rickroll meme", "rickroll", ["搞笑", "离谱"], 2),
    ("trollface meme", "trollface", ["搞笑", "吐槽"], 2),
    ("rage comics meme", "rage_comics", ["愤怒", "搞笑"], 3),
    # --- 猫系 ---
    ("orange cat meme", "orange_cat", ["搞笑", "可爱"], 1),
    ("black cat meme", "black_cat", ["搞笑", "可爱"], 2),
    ("white cat meme", "white_cat", ["可爱", "无语"], 2),
    ("tuxedo cat meme", "tuxedo_cat", ["搞笑", "可爱"], 3),
    ("persian cat meme", "persian_cat", ["可爱", "无语"], 3),
    ("siamese cat meme", "siamese_cat", ["可爱", "吐槽"], 3),
    ("cat loaf meme", "cat_loaf", ["可爱", "搞笑"], 2),
    ("cat box meme", "cat_box", ["搞笑", "可爱"], 2),
    ("cat vs cucumber scared", "cat_cucumber", ["震惊", "搞笑"], 2),
    ("cat zoomies running", "cat_zoomies", ["搞笑", "欢快"], 2),
    ("cat slap meme", "cat_slap", ["搞笑", "愤怒"], 1),
    ("cat stare meme", "cat_stare", ["无语", "吐槽"], 1),
    ("cat judging meme", "cat_judge", ["吐槽", "无语"], 1),
    ("cat vibing meme", "cat_vibing", ["欢快", "搞笑"], 1),
    ("keyboard cat meme", "keyboard_cat", ["搞笑", "欢快"], 2),
    ("ceiling cat meme", "ceiling_cat", ["搞笑", "离谱"], 3),
    ("longcat meme", "longcat", ["搞笑", "离谱"], 3),
    ("business cat meme", "business_cat", ["搞笑", "吐槽"], 3),
    ("chemistry cat meme", "chemistry_cat", ["搞笑", "吐槽"], 3),
    ("lawyer cat meme", "lawyer_cat", ["搞笑", "吐槽"], 3),
    # --- 狗系 ---
    ("shiba inu meme", "shiba_inu", ["搞笑", "可爱"], 1),
    ("golden retriever meme", "golden_retriever", ["可爱", "欢快"], 2),
    ("husky meme dramatic", "husky", ["搞笑", "离谱"], 2),
    ("corgi meme cute", "corgi", ["可爱", "搞笑"], 2),
    ("pug meme", "pug", ["搞笑", "可爱"], 2),
    ("dog side eye meme", "dog_side_eye", ["吐槽", "无语"], 1),
    ("dog confused meme", "dog_confused", ["震惊", "搞笑"], 2),
    ("dog happy excited meme", "dog_happy", ["欢快", "可爱"], 2),
    ("dog disappointed meme", "dog_disappointed", ["委屈", "无语"], 2),
    # --- 表情反应 ---
    ("mind blown meme", "mind_blown", ["震惊", "离谱"], 1),
    ("eye roll meme", "eye_roll", ["无语", "吐槽"], 1),
    ("slow clap meme", "slow_clap", ["吐槽", "搞笑"], 2),
    ("mic drop meme", "mic_drop", ["搞笑", "离谱"], 2),
    ("deal with it meme sunglasses", "deal_with_it", ["搞笑", "离谱"], 1),
    ("nope meme", "nope", ["无语", "吐槽"], 2),
    ("bruh moment meme", "bruh_moment", ["无语", "离谱"], 1),
    ("oof meme", "oof", ["委屈", "搞笑"], 2),
    ("yikes meme", "yikes", ["震惊", "无语"], 2),
    ("cringe meme", "cringe", ["无语", "吐槽"], 2),
    ("sus meme among us", "sus", ["搞笑", "吐槽"], 2),
    ("based meme", "based", ["搞笑", "离谱"], 3),
    ("cope meme", "cope", ["吐槽", "委屈"], 3),
    ("seethe meme angry", "seethe", ["愤怒", "吐槽"], 3),
    # --- 职场 ---
    ("office meme work", "office", ["搞笑", "吐槽"], 1),
    ("meeting meme boring", "meeting", ["无语", "吐槽"], 2),
    ("deadline meme panic", "deadline", ["震惊", "委屈"], 1),
    ("monday meme hate", "monday", ["委屈", "无语"], 1),
    ("friday meme happy", "friday", ["欢快", "搞笑"], 2),
    ("boss meme work", "boss", ["吐槽", "无语"], 2),
    ("salary meme money", "salary", ["委屈", "吐槽"], 2),
    ("overtime meme tired", "overtime", ["委屈", "愤怒"], 2),
    ("work from home meme", "wfh", ["搞笑", "吐槽"], 2),
    ("corporate meme", "corporate", ["吐槽", "无语"], 3),
    # --- 情绪 ---
    ("panic meme freaking out", "panic", ["震惊", "搞笑"], 1),
    ("anxiety meme nervous", "anxiety", ["委屈", "搞笑"], 2),
    ("depression meme sad", "depression", ["委屈", "吐槽"], 2),
    ("existential crisis meme", "existential", ["离谱", "吐槽"], 2),
    ("inner peace meme calm", "inner_peace", ["欢快", "搞笑"], 2),
    ("rage quit meme angry", "rage_quit", ["愤怒", "搞笑"], 1),
    ("celebration meme party", "celebration", ["欢快", "搞笑"], 1),
    ("victory meme win", "victory", ["欢快", "搞笑"], 2),
    ("defeat meme lose", "defeat", ["委屈", "吐槽"], 2),
    ("confusion meme confused", "confusion", ["震惊", "搞笑"], 1),
]

# Mixkit 分类页面 → 直接解析 preview MP3 链接
MIXKIT_CATEGORIES = [
    # --- 原有 ---
    ("funny", "/free-stock-music/funny/", "funny", ["搞笑", "离谱", "吐槽"], 1),
    ("happy", "/free-stock-music/happy/", "happy", ["欢快", "可爱"], 1),
    ("jazz", "/free-stock-music/jazz/", "jazz", ["吐槽", "震惊"], 2),
    ("dramatic", "/free-stock-music/dramatic/", "dramatic", ["震惊", "愤怒"], 2),
    ("sad", "/free-stock-music/sad/", "sad", ["委屈"], 3),
    ("children", "/free-stock-music/children/", "children", ["搞笑", "可爱"], 3),
    # --- 新增 ---
    ("epic", "/free-stock-music/epic/", "epic", ["震惊", "欢快"], 1),
    ("suspense", "/free-stock-music/suspense/", "suspense", ["震惊", "愤怒"], 1),
    ("chill", "/free-stock-music/chill-out/", "chill", ["欢快", "可爱"], 1),
    ("lo-fi", "/free-stock-music/lo-fi/", "lofi", ["欢快", "委屈"], 1),
    ("rock", "/free-stock-music/rock/", "rock", ["愤怒", "欢快"], 2),
    ("pop", "/free-stock-music/pop/", "pop", ["欢快", "搞笑"], 2),
    ("electronic", "/free-stock-music/electronic/", "electronic", ["欢快", "震惊"], 2),
    ("ambient", "/free-stock-music/ambient/", "ambient", ["欢快", "可爱"], 2),
    ("cinematic", "/free-stock-music/cinematic/", "cinematic", ["震惊", "欢快"], 1),
    ("comedy", "/free-stock-music/comedy/", "comedy", ["搞笑", "离谱"], 1),
    ("upbeat", "/free-stock-music/upbeat/", "upbeat", ["欢快", "搞笑"], 1),
    ("motivational", "/free-stock-music/motivational/", "motivational", ["欢快", "震惊"], 2),
    ("romantic", "/free-stock-music/romantic/", "romantic", ["害羞", "欢快"], 2),
    ("horror", "/free-stock-music/horror/", "horror", ["震惊", "愤怒"], 2),
    ("action", "/free-stock-music/action/", "action", ["震惊", "愤怒"], 2),
    ("adventure", "/free-stock-music/adventure/", "adventure", ["欢快", "震惊"], 2),
    ("corporate", "/free-stock-music/corporate/", "corporate", ["欢快", "无语"], 3),
    ("technology", "/free-stock-music/technology/", "technology", ["欢快", "震惊"], 3),
    ("nature", "/free-stock-music/nature/", "nature", ["欢快", "可爱"], 3),
    ("holiday", "/free-stock-music/holiday/", "holiday", ["欢快", "搞笑"], 3),
]


def file_hash(filepath: str, block_size: int = 8192) -> str:
    """计算文件内容 MD5 hash，用于去重"""
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


async def get_existing_hashes(db) -> set:
    """从数据库加载所有已有文件的 hash"""
    hashes = set()
    # 从 memes 表
    async with db.execute("SELECT file_path FROM memes") as cursor:
        async for row in cursor:
            fp = row[0]
            if os.path.exists(fp):
                try:
                    hashes.add(file_hash(fp))
                except:
                    pass
    # 从 bgms 表
    async with db.execute("SELECT file_path FROM bgms") as cursor:
        async for row in cursor:
            fp = row[0]
            if os.path.exists(fp):
                try:
                    hashes.add(file_hash(fp))
                except:
                    pass
    return hashes


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


async def crawl_giphy_memes(db, keyword: str, save_dir: str, moods: list, max_count: int = 10, known_hashes: set = None):
    """用 agent-browser 从 Giphy 搜索并下载表情包（含内容去重）"""
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

        # 内容去重：检查文件 hash
        fh = file_hash(str(filepath))
        if known_hashes is not None and fh in known_hashes:
            filepath.unlink(missing_ok=True)
            print(f"    🔁 跳过重复: {filename}")
            continue
        if known_hashes is not None:
            known_hashes.add(fh)

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


async def crawl_mixkit_bgm(db, name: str, url_path: str, save_dir: str, moods: list, max_count: int = 5, known_hashes: set = None):
    """从 Mixkit 下载 BGM（preview MP3，含内容去重）"""
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

        # 内容去重：检查文件 hash
        fh = file_hash(str(filepath))
        if known_hashes is not None and fh in known_hashes:
            filepath.unlink(missing_ok=True)
            print(f"    🔁 跳过重复BGM: {filename}")
            continue
        if known_hashes is not None:
            known_hashes.add(fh)

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
    print(f"   🔒 内容去重: MD5 hash")
    print()

    # 加载已有文件 hash 用于去重
    print("📦 加载已有文件 hash...")
    known_hashes = await get_existing_hashes(db)
    print(f"   已有 {len(known_hashes)} 个唯一文件")
    print()

    total_memes = 0
    total_bgms = 0

    if mode in ("all", "memes"):
        sorted_memes = sorted(MEME_PRIORITIES, key=lambda x: x[3])
        for keyword, save_dir, moods, priority in sorted_memes:
            print(f"🔍 [P{priority}] 表情包: {keyword} → {save_dir}/")
            n = await crawl_giphy_memes(db, keyword, save_dir, moods, max_count=max_memes, known_hashes=known_hashes)
            total_memes += n
            await asyncio.sleep(2)

    if mode in ("all", "bgm"):
        sorted_bgms = sorted(MIXKIT_CATEGORIES, key=lambda x: x[4])
        for name, url_path, save_dir, moods, priority in sorted_bgms:
            print(f"🎵 [P{priority}] BGM: {name} → {save_dir}/")
            n = await crawl_mixkit_bgm(db, name, url_path, save_dir, moods, max_count=max_bgms, known_hashes=known_hashes)
            total_bgms += n

    elapsed = time.time() - start
    print()
    print(f"📊 爬取完成 ({elapsed:.1f}s)")
    print(f"   表情包: +{total_memes}")
    print(f"   BGM: +{total_bgms}")

    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
