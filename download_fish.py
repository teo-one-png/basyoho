"""
Wikipedia + Wikimedia Commonsから魚の画像をダウンロードするスクリプト
- Wikipedia英語版の記事メイン画像を取得（pageimages API）
- 長辺500pxにリサイズ
- CommonsからライセンスInfo取得
- クレジット情報をJSONに保存
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
from urllib.parse import unquote

IMAGES_DIR = "images/fish"
CREDITS_FILE = "fish_credits.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "FishMemoryApp/1.0 (educational project) Python-requests/2.32",
})

# 追加する魚: (romaji_id, 日本語名, Wikipedia英語版の記事タイトル)
FISH_TO_ADD = [
    # ========== 固有種（琵琶湖固有種・琵琶湖固有亜種） ==========
    ("biwamasu", "ビワマス", "Biwa trout"),
    ("nigorobuna", "ニゴロブナ", "Carassius buergeri"),
    ("gengoroubuna", "ゲンゴロウブナ", "Carassius cuvieri"),
    ("honmoroko", "ホンモロコ", "Gnathopogon caerulescens"),
    ("biwahigai", "ビワヒガイ", "Sarcocheilichthys biwaensis"),
    ("aburahigai", "アブラヒガイ", "Sarcocheilichthys biwaensis"),
    ("wataka", "ワタカ", "Ischikauia steenackeri"),
    ("sugomoroko", "スゴモロコ", "Squalidus chankaensis"),
    ("dememoroko", "デメモロコ", "Squalidus japonicus"),
    ("isaza", "イサザ", "Gymnogobius isaza"),
    ("biwayoshinobori", "ビワヨシノボリ", "Rhinogobius biwaensis"),
    ("biwakooonamazu", "ビワコオオナマズ", "Lake Biwa catfish"),
    ("utsusemikajika", "ウツセミカジカ", "Cottus reinii"),
    ("iwatoko_namazu", "イワトコナマズ", "Silurus lithophilus"),
    ("biwakoogatasu_jishimadojou", "ビワコガタスジシマドジョウ", "Cobitis minamorii"),
    ("oogarasugomoroko", "オオガタスゴモロコ", "Squalidus chankaensis"),

    # ========== 在来種 — コイ科 ==========
    ("koi", "コイ", "Common carp"),
    ("ginbuna", "ギンブナ", "Carassius auratus"),
    ("oikawa", "オイカワ", "Opsariichthys platypus"),
    ("kawamutsu", "カワムツ", "Candidia temminckii"),
    ("numamutsu", "ヌマムツ", "Candidia sieboldii"),
    ("ugui", "ウグイ", "Tribolodon hakonensis"),
    ("tamoroko", "タモロコ", "Gnathopogon elongatus"),
    ("motsugo", "モツゴ", "Stone moroko"),
    ("hasu", "ハス", "Opsariichthys uncirostris"),
    ("kamatsuka", "カマツカ", "Pseudogobio esocinus"),
    ("tsuchifuki", "ツチフキ", "Abbottina rivularis"),
    ("zezera", "ゼゼラ", "Biwia zezera"),
    ("mugitsuku", "ムギツク", "Pungtungia herzi"),
    ("higai", "ヒガイ", "Sarcocheilichthys variegatus"),
    ("itomoroko", "イトモロコ", "Squalidus gracilis"),
    ("nagabuna", "ナガブナ", "Carassius buergeri"),

    # ========== 在来種 — タナゴ類（コイ科） ==========
    ("tanago", "タナゴ", "Acheilognathus melanogaster"),
    ("kanehira", "カネヒラ", "Acheilognathus rhombeus"),
    ("ichimonjitanago", "イチモンジタナゴ", "Acheilognathus cyanostigma"),
    ("yaritanago", "ヤリタナゴ", "Tanakia lanceolata"),
    ("shirotanago", "シロヒレタビラ", "Acheilognathus tabira"),

    # ========== 在来種 — アユ科 ==========
    ("ayu", "アユ", "Ayu"),

    # ========== 在来種 — ナマズ科 ==========
    ("namazu", "ナマズ", "Amur catfish"),
    ("gigi", "ギギ", "Tachysurus nudiceps"),
    ("akaza", "アカザ", "Liobagrus reini"),

    # ========== 在来種 — ドジョウ科 ==========
    ("dojou", "ドジョウ", "Pond loach"),
    ("shimadojou", "シマドジョウ", "Cobitis biwae"),
    ("ajimedojou", "アジメドジョウ", "Niwaella delicata"),
    ("hotokodojou", "ホトケドジョウ", "Lefua echigonia"),
    ("nagashimadojou", "ナガシマドジョウ", "Cobitis striata"),

    # ========== 在来種 — ハゼ科 ==========
    ("yoshinobori", "ヨシノボリ", "Rhinogobius"),
    ("kawayoshinobori", "カワヨシノボリ", "Rhinogobius flumineus"),
    ("touyoshinobori", "トウヨシノボリ", "Rhinogobius kurodai"),
    ("ukigori", "ウキゴリ", "Gymnogobius urotaenia"),
    ("sumiukigori", "スミウキゴリ", "Gymnogobius petschiliensis"),
    ("donko", "ドンコ", "Odontobutis obscura"),
    ("numachichibu", "ヌマチチブ", "Tridentiger brevispinis"),

    # ========== 在来種 — その他 ==========
    ("kajika", "カジカ", "Cottus pollux"),
    ("unagi", "ニホンウナギ", "Japanese eel"),
    ("medaka", "メダカ", "Japanese rice fish"),
    ("amago", "アマゴ", "Oncorhynchus masou ishikawae"),
    ("iwana", "イワナ", "Japanese char"),
    ("ooyamato_shimadojou", "オオヤマトシマドジョウ", "Cobitis magnostriata"),
    ("sunayatsume", "スナヤツメ", "Lethenteron reissneri"),
    ("kawayatsume", "カワヤツメ", "Arctic lamprey"),
    ("tomiyo", "トミヨ", "Pungitius pungitius"),
    ("itoyo", "イトヨ", "Three-spined stickleback"),
    ("hariyo", "ハリヨ", "Gasterosteus microcephalus"),
    ("sayori", "サヨリ", "Japanese halfbeak"),
    ("wakasagi", "ワカサギ", "Hypomesus nipponensis"),
    ("hiuo", "ヒウオ", "Plecoglossus altivelis"),
    ("shirauo", "シラウオ", "Japanese icefish"),
    ("yoshinobori_ruisenbo", "ルリヨシノボリ", "Rhinogobius mizunoi"),
    ("bora", "ボラ", "Flathead grey mullet"),

    # ========== 外来種 ==========
    ("ookuchibasu", "オオクチバス", "Largemouth bass"),
    ("kokuchibasu", "コクチバス", "Smallmouth bass"),
    ("buruugiru", "ブルーギル", "Bluegill"),
    ("channerukyattofisshu", "チャネルキャットフィッシュ", "Channel catfish"),
    ("tairikubaratanago", "タイリクバラタナゴ", "Rhodeus ocellatus"),
    ("kamuruchii", "カムルチー", "Northern snakehead"),
    ("nijimasu", "ニジマス", "Rainbow trout"),
    ("ootanago", "オオタナゴ", "Acheilognathus macropterus"),
    ("sougyou", "ソウギョ", "Grass carp"),
    ("rengyou", "レンギョ", "Silver carp"),
    ("hakuren", "ハクレン", "Silver carp"),
    ("kokuren", "コクレン", "Bighead carp"),
    ("taiwandojou", "タイワンドジョウ", "Blotched snakehead"),
    ("numagarei", "ヌマガレイ", "Starry flounder"),
    ("peherey", "ペヘレイ", "Odontesthes bonariensis"),
]


def get_wikipedia_image(article_title):
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
        print(f"  Wikipedia API error: {e}")
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
    # /wikipedia/commons/thumb/a/ab/Filename.jpg/500px-Filename.jpg
    # or /wikipedia/commons/a/ab/Filename.jpg
    parts = url.split("/wikipedia/commons/")
    if len(parts) < 2:
        return None
    path = parts[1]
    # thumb path: thumb/a/ab/File.jpg/500px-File.jpg
    if path.startswith("thumb/"):
        segments = path.split("/")
        if len(segments) >= 4:
            return unquote(segments[3])
    else:
        # direct: a/ab/File.jpg
        segments = path.split("/")
        if len(segments) >= 3:
            return unquote(segments[2])
    return None


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    credits = {}
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, "r", encoding="utf-8") as f:
            credits = json.load(f)

    results = []
    failed = []

    for i, (romaji, jp_name, en_title) in enumerate(FISH_TO_ADD):
        print(f"[{i+1}/{len(FISH_TO_ADD)}] {jp_name} ({en_title})...", flush=True)
        filepath = os.path.join(IMAGES_DIR, f"{romaji}.jpg")

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  Already exists, skipping")
            results.append((romaji, jp_name))
            continue

        thumb_url, orig_url = get_wikipedia_image(en_title)
        if not thumb_url:
            print(f"  [FAIL] No image found on Wikipedia")
            failed.append((romaji, jp_name, en_title))
            time.sleep(1)
            continue

        success = download_and_resize(thumb_url, filepath)
        if not success:
            # Retry with original if thumb fails
            if orig_url:
                time.sleep(1)
                success = download_and_resize(orig_url, filepath)

        if success:
            # ライセンス情報を取得
            commons_filename = extract_filename_from_url(orig_url or thumb_url)
            if commons_filename:
                time.sleep(0.3)
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
                "original_url": orig_url or thumb_url,
            }
        else:
            print(f"  [FAIL] Download failed")
            failed.append((romaji, jp_name, en_title))

        time.sleep(2)  # rate limit

    # Save credits
    with open(CREDITS_FILE, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    print(f"\n=== 結果 ===")
    print(f"成功: {len(results)}種")
    print(f"失敗: {len(failed)}種")
    if failed:
        print("\n失敗リスト:")
        for r, jp, en in failed:
            print(f"  {jp} ({en}) - {r}")

    # Generate fish_data.js entries
    print("\n=== fish_data.js追加用エントリ ===")
    for romaji, jp_name in results:
        print(f'  {{ id: "{romaji}", name: "{jp_name}", category: "魚類", image: "images/fish/{romaji}.jpg", tags: [] }},')


if __name__ == "__main__":
    main()
