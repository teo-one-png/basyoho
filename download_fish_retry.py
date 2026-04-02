"""
失敗した35種の魚画像をリトライダウンロードするスクリプト
- 日本語Wikipedia → 英語Wikipedia（学名） → Wikimedia Commons検索
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json
import os
import time
import re
from PIL import Image
from io import BytesIO
from urllib.parse import unquote, quote

IMAGES_DIR = "images/fish"
CREDITS_FILE = "fish_credits.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "FishMemoryApp/1.0 (educational project) Python-requests/2.32",
})

# (romaji_id, 日本語名, 学名, 日本語Wikipedia記事タイトル)
RETRY_FISH = [
    ("gengoroubuna", "ゲンゴロウブナ", "Carassius cuvieri", "ゲンゴロウブナ"),
    ("wataka", "ワタカ", "Ischikauia steenackeri", "ワタカ"),
    ("sugomoroko", "スゴモロコ", "Squalidus chankaensis biwae", "スゴモロコ"),
    ("isaza", "イサザ", "Gymnogobius isaza", "イサザ"),
    ("biwayoshinobori", "ビワヨシノボリ", "Rhinogobius biwaensis", "ビワヨシノボリ"),
    ("biwakooonamazu", "ビワコオオナマズ", "Silurus biwaensis", "ビワコオオナマズ"),
    ("biwakoogatasu_jishimadojou", "ビワコガタスジシマドジョウ", "Cobitis minamorii", "ビワコガタスジシマドジョウ"),
    ("oogarasugomoroko", "オオガタスゴモロコ", "Squalidus chankaensis", "オオガタスゴモロコ"),
    ("ginbuna", "ギンブナ", "Carassius auratus langsdorfii", "ギンブナ"),
    ("oikawa", "オイカワ", "Opsariichthys platypus", "オイカワ"),
    ("kawamutsu", "カワムツ", "Candidia temminckii", "カワムツ"),
    ("numamutsu", "ヌマムツ", "Candidia sieboldii", "ヌマムツ"),
    ("ugui", "ウグイ", "Tribolodon hakonensis", "ウグイ"),
    ("nagabuna", "ナガブナ", "Carassius buergeri", "ナガブナ"),
    ("ichimonjitanago", "イチモンジタナゴ", "Acheilognathus cyanostigma", "イチモンジタナゴ"),
    ("ayu", "アユ", "Plecoglossus altivelis", "アユ"),
    ("gigi", "ギギ", "Tachysurus nudiceps", "ギギ"),
    ("akaza", "アカザ", "Liobagrus reini", "アカザ"),
    ("ajimedojou", "アジメドジョウ", "Niwaella delicata", "アジメドジョウ"),
    ("hotokodojou", "ホトケドジョウ", "Lefua echigonia", "ホトケドジョウ"),
    ("nagashimadojou", "ナガシマドジョウ", "Cobitis striata", "ナガシマドジョウ"),
    ("touyoshinobori", "トウヨシノボリ", "Rhinogobius kurodai", "トウヨシノボリ"),
    ("ukigori", "ウキゴリ", "Gymnogobius urotaenia", "ウキゴリ"),
    ("sumiukigori", "スミウキゴリ", "Gymnogobius petschiliensis", "スミウキゴリ"),
    ("donko", "ドンコ", "Odontobutis obscura", "ドンコ"),
    ("kajika", "カジカ", "Cottus pollux", "カジカ (魚)"),
    ("amago", "アマゴ", "Oncorhynchus masou ishikawae", "アマゴ"),
    ("iwana", "イワナ", "Salvelinus leucomaenis", "イワナ"),
    ("ooyamato_shimadojou", "オオヤマトシマドジョウ", "Cobitis magnostriata", "オオヤマトシマドジョウ"),
    ("tomiyo", "トミヨ", "Pungitius pungitius", "トミヨ"),
    ("hariyo", "ハリヨ", "Gasterosteus microcephalus", "ハリヨ"),
    ("sayori", "サヨリ", "Hyporhamphus sajori", "サヨリ"),
    ("hiuo", "ヒウオ", "Plecoglossus altivelis", "ヒウオ"),
    ("shirauo", "シラウオ", "Salangichthys microdon", "シラウオ"),
    ("tairikubaratanago", "タイリクバラタナゴ", "Rhodeus ocellatus", "タイリクバラタナゴ"),
]


def get_ja_wikipedia_image(ja_title):
    """日本語Wikipediaの記事からメイン画像のURLを取得"""
    url = "https://ja.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": ja_title,
        "prop": "pageimages",
        "piprop": "original|thumbnail",
        "pithumbsize": 500,
        "format": "json",
    }
    try:
        resp = SESSION.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception as e:
        print(f"  ja.Wikipedia API error: {e}")
        return None, None

    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        thumb = page.get("thumbnail", {})
        original = page.get("original", {})
        thumb_url = thumb.get("source")
        orig_url = original.get("source")
        if thumb_url:
            return thumb_url, orig_url
    return None, None


def get_en_wikipedia_image(article_title):
    """Wikipedia英語版の記事からメイン画像のURLを取得"""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": article_title,
        "prop": "pageimages",
        "piprop": "original|thumbnail",
        "pithumbsize": 500,
        "format": "json",
    }
    try:
        resp = SESSION.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception as e:
        print(f"  en.Wikipedia API error: {e}")
        return None, None

    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        thumb = page.get("thumbnail", {})
        original = page.get("original", {})
        thumb_url = thumb.get("source")
        orig_url = original.get("source")
        if thumb_url:
            return thumb_url, orig_url
    return None, None


def search_commons_image(search_term):
    """Wikimedia Commonsで画像を検索"""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srnamespace": 6,  # File namespace
        "srsearch": search_term,
        "srinfo": "",
        "srlimit": 5,
        "format": "json",
    }
    try:
        resp = SESSION.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception as e:
        print(f"  Commons search error: {e}")
        return None, None

    results = data.get("query", {}).get("search", [])
    for result in results:
        title = result.get("title", "")
        # Filter for image files only
        if not any(title.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".tif", ".tiff"]):
            continue
        # Skip SVG files (not photos)
        if title.lower().endswith(".svg"):
            continue
        # Get the image URL from this file
        thumb_url, orig_url = get_commons_file_url(title)
        if thumb_url:
            return thumb_url, orig_url
    return None, None


def get_commons_file_url(file_title):
    """CommonsのファイルタイトルからURL取得"""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url|thumburl",
        "iiurlwidth": 500,
        "format": "json",
    }
    try:
        resp = SESSION.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception as e:
        print(f"  Commons file URL error: {e}")
        return None, None

    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        info_list = page.get("imageinfo", [])
        if info_list:
            info = info_list[0]
            thumb_url = info.get("thumburl")
            orig_url = info.get("url")
            if thumb_url:
                return thumb_url, orig_url
    return None, None


def get_commons_license(filename):
    """Wikimedia Commonsからライセンス情報を取得"""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "extmetadata",
        "format": "json",
    }
    try:
        resp = SESSION.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception:
        return {"license": "Unknown", "artist": "Unknown", "license_url": ""}

    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        info = page.get("imageinfo", [{}])[0]
        meta = info.get("extmetadata", {})
        artist = meta.get("Artist", {}).get("value", "Unknown")
        artist = re.sub(r'<[^>]+>', '', artist).strip()
        license_short = meta.get("LicenseShortName", {}).get("value", "Unknown")
        license_url = meta.get("LicenseUrl", {}).get("value", "")
        return {
            "license": license_short,
            "artist": artist,
            "license_url": license_url,
        }
    return {"license": "Unknown", "artist": "Unknown", "license_url": ""}


def download_and_resize(url, filepath, max_size=500):
    """画像をダウンロードして長辺500pxにリサイズ"""
    try:
        resp = SESSION.get(url, timeout=30)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))

        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        if max(w, h) > max_size:
            ratio = max_size / max(w, h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        img.save(filepath, "JPEG", quality=85)
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def extract_filename_from_url(url):
    """URLからCommonsのファイル名を抽出"""
    parts = url.split("/wikipedia/commons/")
    if len(parts) < 2:
        return None
    path = parts[1]
    if path.startswith("thumb/"):
        segments = path.split("/")
        if len(segments) >= 4:
            return unquote(segments[3])
    else:
        segments = path.split("/")
        if len(segments) >= 3:
            return unquote(segments[2])
    return None


def try_download(romaji, jp_name, sci_name, ja_title):
    """複数のソースを試して画像をダウンロード"""
    filepath = os.path.join(IMAGES_DIR, f"{romaji}.jpg")

    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f"  Already exists, skipping")
        return True, filepath, None, None

    # 1. 日本語Wikipedia
    print(f"  Trying ja.wikipedia ({ja_title})...")
    thumb_url, orig_url = get_ja_wikipedia_image(ja_title)
    if thumb_url:
        print(f"  Found on ja.wikipedia!")
        success = download_and_resize(thumb_url, filepath)
        if not success and orig_url:
            time.sleep(1)
            success = download_and_resize(orig_url, filepath)
        if success:
            return True, filepath, thumb_url, orig_url
    time.sleep(3)

    # 2. 英語Wikipedia（学名で検索）
    print(f"  Trying en.wikipedia ({sci_name})...")
    thumb_url, orig_url = get_en_wikipedia_image(sci_name)
    if thumb_url:
        print(f"  Found on en.wikipedia!")
        success = download_and_resize(thumb_url, filepath)
        if not success and orig_url:
            time.sleep(1)
            success = download_and_resize(orig_url, filepath)
        if success:
            return True, filepath, thumb_url, orig_url
    time.sleep(3)

    # 3. Wikimedia Commons検索（学名）
    print(f"  Trying Commons search ({sci_name})...")
    thumb_url, orig_url = search_commons_image(sci_name)
    if thumb_url:
        print(f"  Found on Commons (scientific name)!")
        success = download_and_resize(thumb_url, filepath)
        if not success and orig_url:
            time.sleep(1)
            success = download_and_resize(orig_url, filepath)
        if success:
            return True, filepath, thumb_url, orig_url
    time.sleep(3)

    # 4. Wikimedia Commons検索（日本語名）
    print(f"  Trying Commons search ({jp_name})...")
    thumb_url, orig_url = search_commons_image(jp_name)
    if thumb_url:
        print(f"  Found on Commons (Japanese name)!")
        success = download_and_resize(thumb_url, filepath)
        if not success and orig_url:
            time.sleep(1)
            success = download_and_resize(orig_url, filepath)
        if success:
            return True, filepath, thumb_url, orig_url

    return False, filepath, None, None


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    credits = {}
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, "r", encoding="utf-8") as f:
            credits = json.load(f)

    results = []
    failed = []

    for i, (romaji, jp_name, sci_name, ja_title) in enumerate(RETRY_FISH):
        print(f"\n[{i+1}/{len(RETRY_FISH)}] {jp_name} ({sci_name})...", flush=True)

        success, filepath, thumb_url, orig_url = try_download(romaji, jp_name, sci_name, ja_title)

        if success:
            # ライセンス情報を取得
            source_url = orig_url or thumb_url
            commons_filename = None
            if source_url:
                commons_filename = extract_filename_from_url(source_url)
            if not commons_filename and thumb_url:
                commons_filename = extract_filename_from_url(thumb_url)

            if commons_filename:
                time.sleep(0.5)
                lic_info = get_commons_license(commons_filename)
            else:
                lic_info = {"license": "Wikimedia Commons", "artist": "Unknown", "license_url": ""}

            print(f"  [OK] ({lic_info['license']}, by {lic_info['artist'][:40]})")
            results.append((romaji, jp_name))
            credits[romaji] = {
                "name_jp": jp_name,
                "artist": lic_info["artist"],
                "license": lic_info["license"],
                "license_url": lic_info["license_url"],
                "source": f"https://commons.wikimedia.org/wiki/File:{commons_filename}" if commons_filename else "",
                "original_url": orig_url or thumb_url or "",
            }
        else:
            print(f"  [FAIL] No image found from any source")
            failed.append((romaji, jp_name, sci_name))

        time.sleep(3)

    # Save credits
    with open(CREDITS_FILE, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    print(f"\n\n=== リトライ結果 ===")
    print(f"成功: {len(results)}種")
    print(f"失敗: {len(failed)}種")
    if failed:
        print("\n失敗リスト:")
        for r, jp, sci in failed:
            print(f"  {jp} ({sci}) - {r}")
    if results:
        print("\n成功リスト:")
        for r, jp in results:
            print(f"  {jp} - {r}")


if __name__ == "__main__":
    main()
