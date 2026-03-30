"""
Wikipedia + Wikimedia Commonsから鳥の画像をダウンロードするスクリプト
- Wikipedia英語版の記事メイン画像を取得（pageimages API）
- 長辺500pxにリサイズ
- CommonsからライセンスInfo取得
- クレジット情報をJSONに保存
"""

import requests
import json
import os
import time
import re
from PIL import Image
from io import BytesIO
from urllib.parse import unquote

IMAGES_DIR = "images"
CREDITS_FILE = "credits.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "BirdMemoryApp/1.0 (https://github.com/goren; educational project) Python-requests/2.32",
})

# 追加する鳥: (romaji_id, 日本語名, Wikipedia英語版の記事タイトル)
BIRDS_TO_ADD = [
    # キジ目
    ("raichou", "ライチョウ", "Rock ptarmigan"),
    ("kojukei", "コジュケイ", "Chinese bamboo partridge"),
    ("yamadori", "ヤマドリ", "Copper pheasant"),
    ("kiji", "キジ", "Green pheasant"),
    # カモ目
    ("magan", "マガン", "Greater white-fronted goose"),
    ("kobuhakuchou", "コブハクチョウ", "Mute swan"),
    ("oohakuchou", "オオハクチョウ", "Whooper swan"),
    ("oshidori", "オシドリ", "Mandarin duck"),
    ("hidorigamo", "ヒドリガモ", "Eurasian wigeon"),
    ("magamo", "マガモ", "Mallard"),
    ("hashibirogamo", "ハシビロガモ", "Northern shoveler"),
    ("onagagamo", "オナガガモ", "Northern pintail"),
    ("kogamo", "コガモ", "Eurasian teal"),
    ("hoshihajiro", "ホシハジロ", "Common pochard"),
    ("kinkurohajiro", "キンクロハジロ", "Tufted duck"),
    ("mikoaisa", "ミコアイサ", "Smew"),
    # カイツブリ目
    ("kaitsuburi", "カイツブリ", "Little grebe"),
    ("kanmurikaitsuburi", "カンムリカイツブリ", "Great crested grebe"),
    # ハト目
    ("kawarabato", "カワラバト", "Rock dove"),
    ("aobato", "アオバト", "White-bellied green pigeon"),
    # コウノトリ目
    ("kounotori", "コウノトリ", "Oriental stork"),
    # ペリカン目・サギ科
    ("goisagi", "ゴイサギ", "Black-crowned night heron"),
    ("sasagoi", "ササゴイ", "Striated heron"),
    ("amasagi", "アマサギ", "Cattle egret"),
    ("daisagi", "ダイサギ", "Great egret"),
    ("chuusagi", "チュウサギ", "Intermediate egret"),
    # トキ科
    ("toki", "トキ", "Crested ibis"),
    # ツル目
    ("tanchou", "タンチョウ", "Red-crowned crane"),
    ("nabeduru", "ナベヅル", "Hooded crane"),
    ("ban", "バン", "Common moorhen"),
    ("ooban", "オオバン", "Eurasian coot"),
    # カッコウ目
    ("kakkou", "カッコウ", "Common cuckoo"),
    ("hototogisu", "ホトトギス", "Lesser cuckoo"),
    ("tsutsudori", "ツツドリ", "Oriental cuckoo"),
    # チドリ目
    ("tageri", "タゲリ", "Northern lapwing"),
    ("keri", "ケリ", "Grey-headed lapwing"),
    ("kochidori", "コチドリ", "Little ringed plover"),
    ("isoshigi", "イソシギ", "Common sandpiper"),
    ("yurikamome", "ユリカモメ", "Black-headed gull"),
    ("umineko", "ウミネコ", "Black-tailed gull"),
    ("segurokamome", "セグロカモメ", "Herring gull"),
    # タカ目
    ("misago", "ミサゴ", "Osprey"),
    ("chuuhi", "チュウヒ", "Eastern marsh harrier"),
    ("inuwashi", "イヌワシ", "Golden eagle"),
    ("kanmuriwashi", "カンムリワシ", "Crested serpent eagle"),
    # フクロウ目
    ("fukurou", "フクロウ", "Ural owl"),
    ("aobazuku", "アオバズク", "Brown hawk-owl"),
    ("konohazuku", "コノハズク", "Eurasian scops owl"),
    ("komimizuku", "コミミズク", "Short-eared owl"),
    ("shimafukurou", "シマフクロウ", "Blakiston's fish owl"),
    # ブッポウソウ目
    ("akashoubin", "アカショウビン", "Ruddy kingfisher"),
    ("yamasemi", "ヤマセミ", "Crested kingfisher"),
    ("buppousou", "ブッポウソウ", "Oriental dollarbird"),
    # キツツキ目
    ("kogera", "コゲラ", "Japanese pygmy woodpecker"),
    ("akagera", "アカゲラ", "Great spotted woodpecker"),
    ("aogera", "アオゲラ", "Japanese green woodpecker"),
    ("kumagera", "クマゲラ", "Black woodpecker"),
    ("arisui", "アリスイ", "Eurasian wryneck"),
    # ハヤブサ目
    ("chougenbou", "チョウゲンボウ", "Common kestrel"),
    # スズメ目
    ("sankouchou", "サンコウチョウ", "Japanese paradise flycatcher"),
    ("kakesu", "カケス", "Eurasian jay"),
    ("onaga", "オナガ", "Azure-winged magpie"),
    ("kasasagi", "カササギ", "Eurasian magpie"),
    ("hoshigarasu", "ホシガラス", "Spotted nutcracker"),
    ("kikuitadaki", "キクイタダキ", "Goldcrest"),
    ("kogara", "コガラ", "Willow tit"),
    ("higara", "ヒガラ", "Coal tit"),
    ("yamagara", "ヤマガラ", "Varied tit"),
    ("hibari", "ヒバリ", "Eurasian skylark"),
    ("koshiakatsubame", "コシアカツバメ", "Red-rumped swallow"),
    ("iwatsubame", "イワツバメ", "Asian house martin"),
    ("yabusame", "ヤブサメ", "Asian stubtail"),
    ("sendaimushikui", "センダイムシクイ", "Eastern crowned warbler"),
    ("gabichou", "ガビチョウ", "Chinese hwamei"),
    ("soushichou", "ソウシチョウ", "Red-billed leiothrix"),
    ("ooyoshikiri", "オオヨシキリ", "Oriental reed warbler"),
    ("sekka", "セッカ", "Zitting cisticola"),
    ("kirenjaku", "キレンジャク", "Bohemian waxwing"),
    ("hirenjaku", "ヒレンジャク", "Japanese waxwing"),
    ("gojuukara", "ゴジュウカラ", "Eurasian nuthatch"),
    ("misosazai", "ミソサザイ", "Eurasian wren"),
    ("komukudori", "コムクドリ", "Chestnut-cheeked starling"),
    ("kawagarasu", "カワガラス", "Brown dipper"),
    ("toratsugumi", "トラツグミ", "Scaly thrush"),
    ("kurotsugumi", "クロツグミ", "Japanese thrush"),
    ("shirohara", "シロハラ", "Pale thrush"),
    ("akahara", "アカハラ", "Brown-headed thrush"),
    ("komadori", "コマドリ", "Japanese robin"),
    ("ruribitaki", "ルリビタキ", "Red-flanked bluetail"),
    ("nobitaki", "ノビタキ", "Stonechat"),
    ("isohiyodori", "イソヒヨドリ", "Blue rock thrush"),
    ("kibitaki", "キビタキ", "Narcissus flycatcher"),
    ("ooruri", "オオルリ", "Blue-and-white flycatcher"),
    ("iwahibari", "イワヒバリ", "Alpine accentor"),
    ("kisekirei", "キセキレイ", "Grey wagtail"),
    ("segurosekirei", "セグロセキレイ", "Japanese wagtail"),
    ("binzui", "ビンズイ", "Olive-backed pipit"),
    ("atori", "アトリ", "Brambling"),
    ("mahiwa", "マヒワ", "Eurasian siskin"),
    ("benimashiko", "ベニマシコ", "Long-tailed rosefinch"),
    ("uso", "ウソ", "Eurasian bullfinch"),
    ("shime", "シメ", "Hawfinch"),
    ("ikaru", "イカル", "Japanese grosbeak"),
    ("hoojiro", "ホオジロ", "Meadow bunting"),
    ("kashiradaka", "カシラダカ", "Rustic bunting"),
    ("aoji", "アオジ", "Black-faced bunting"),
    ("oojurin", "オオジュリン", "Common reed bunting"),
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

    for i, (romaji, jp_name, en_title) in enumerate(BIRDS_TO_ADD):
        print(f"[{i+1}/{len(BIRDS_TO_ADD)}] {jp_name} ({en_title})...", flush=True)
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

        time.sleep(1)  # rate limit

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

    # Generate data.js entries
    print("\n=== data.js追加用エントリ ===")
    for romaji, jp_name in results:
        print(f'  {{ id: "{romaji}", name: "{jp_name}", category: "鳥", image: "images/{romaji}.jpg", tags: [] }},')


if __name__ == "__main__":
    main()
