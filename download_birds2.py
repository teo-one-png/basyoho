"""
次の100種をダウンロードするスクリプト（第2弾）
Wikipedia pageimages APIで画像取得 → リサイズ → ライセンス収集
"""

import requests, json, time, re, os
from PIL import Image
from io import BytesIO
from urllib.parse import unquote

IMAGES_DIR = "images"
CREDITS_FILE = "credits.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "BirdMemoryApp/1.0 (https://github.com/goren; educational project) Python-requests/2.32",
})

# 次の100種: (romaji_id, 日本語名, Wikipedia英語版記事タイトル)
BIRDS_BATCH2 = [
    # キジ目（残り）
    ("ezoraichou", "エゾライチョウ", "Hazel grouse"),
    ("uzura", "ウズラ", "Japanese quail"),
    ("tairikukiji", "タイリクキジ", "Common pheasant"),
    # カモ目（残り）
    ("hishikui", "ヒシクイ", "Bean goose"),
    ("karigane", "カリガネ", "Lesser white-fronted goose"),
    ("hakugan", "ハクガン", "Snow goose"),
    ("shijuukaragaN", "シジュウカラガン", "Cackling goose"),
    ("kokugan", "コクガン", "Brant"),
    ("kohakuchou", "コハクチョウ", "Tundra swan"),
    ("tsukushigamo", "ツクシガモ", "Common shelduck"),
    ("okayoshigamo", "オカヨシガモ", "Gadwall"),
    ("yoshigamo", "ヨシガモ", "Falcated duck"),
    ("amerikahidori", "アメリカヒドリ", "American wigeon"),
    ("shimaaji", "シマアジ", "Garganey"),
    ("tomoegamo", "トモエガモ", "Baikal teal"),
    ("suzugamo", "スズガモ", "Greater scaup"),
    ("shinorigamo", "シノリガモ", "Harlequin duck"),
    ("kurogamo", "クロガモ", "Black scoter"),
    ("koorigamo", "コオリガモ", "Long-tailed duck"),
    ("hoojirogamo", "ホオジロガモ", "Common goldeneye"),
    ("kawaaisa", "カワアイサ", "Common merganser"),
    ("umiaisa", "ウミアイサ", "Red-breasted merganser"),
    # カイツブリ目（残り）
    ("akaerikaitsuburi", "アカエリカイツブリ", "Red-necked grebe"),
    ("mimikaitsuburi", "ミミカイツブリ", "Horned grebe"),
    ("hajirokaitsuburi", "ハジロカイツブリ", "Black-necked grebe"),
    # ハト目（残り）
    ("karasubato", "カラスバト", "Japanese wood pigeon"),
    ("shirakobato", "シラコバト", "Eurasian collared dove"),
    ("kinbato", "キンバト", "Common emerald dove"),
    ("zuakaaobato", "ズアカアオバト", "Whistling green pigeon"),
    # アビ目
    ("abi", "アビ", "Red-throated loon"),
    ("oohamu", "オオハム", "Arctic loon"),
    ("shiroerioohamu", "シロエリオオハム", "Pacific loon"),
    # ミズナギドリ目
    ("ahoudori", "アホウドリ", "Short-tailed albatross"),
    ("koahoudori", "コアホウドリ", "Laysan albatross"),
    ("kuroashiahoudori", "クロアシアホウドリ", "Black-footed albatross"),
    ("oomizunagidori", "オオミズナギドリ", "Streaked shearwater"),
    # カツオドリ目
    ("katsuodori", "カツオドリ", "Brown booby"),
    ("himeu", "ヒメウ", "Pelagic cormorant"),
    ("kawau", "カワウ", "Great cormorant"),
    ("umiu", "ウミウ", "Japanese cormorant"),
    # ペリカン目（残り）
    ("murasakisagi", "ムラサキサギ", "Purple heron"),
    ("kurosagi", "クロサギ", "Pacific reef heron"),
    ("herasagi", "ヘラサギ", "Eurasian spoonbill"),
    ("kurotsuraherasagi", "クロツラヘラサギ", "Black-faced spoonbill"),
    # ツル目（残り）
    ("kanadaduru", "カナダヅル", "Sandhill crane"),
    ("manaduru", "マナヅル", "White-naped crane"),
    ("kuroduru", "クロヅル", "Common crane"),
    ("yanbarukuina", "ヤンバルクイナ", "Okinawa rail"),
    ("kuina", "クイナ", "Water rail"),
    ("hikuina", "ヒクイナ", "Band-bellied crake"),
    # カッコウ目（残り）
    ("juuichi", "ジュウイチ", "Hodgson's hawk-cuckoo"),
    # ヨタカ目
    ("yotaka", "ヨタカ", "Grey nightjar"),
    # アマツバメ目
    ("amatsubame", "アマツバメ", "Pacific swift"),
    # チドリ目（残り）
    ("munaguro", "ムナグロ", "Pacific golden plover"),
    ("daizen", "ダイゼン", "Grey plover"),
    ("ikaruchidori", "イカルチドリ", "Long-billed plover"),
    ("shirochidori", "シロチドリ", "Kentish plover"),
    ("medaichidori", "メダイチドリ", "Lesser sand plover"),
    ("miyakodori", "ミヤコドリ", "Eurasian oystercatcher"),
    ("seitakashigi", "セイタカシギ", "Black-winged stilt"),
    ("yamashigi", "ヤマシギ", "Eurasian woodcock"),
    ("oojishigi", "オオジシギ", "Latham's snipe"),
    ("tashigi", "タシギ", "Common snipe"),
    ("oguroshigi", "オグロシギ", "Black-tailed godwit"),
    ("oosorihashishigi", "オオソリハシシギ", "Bar-tailed godwit"),
    ("chuushakushigi", "チュウシャクシギ", "Whimbrel"),
    ("hourokushigi", "ホウロクシギ", "Far Eastern curlew"),
    ("aoashishigi", "アオアシシギ", "Common greenshank"),
    ("kiashishigi", "キアシシギ", "Grey-tailed tattler"),
    ("kyoujoshigi", "キョウジョシギ", "Ruddy turnstone"),
    ("tounen", "トウネン", "Red-necked stint"),
    ("hamashigi", "ハマシギ", "Dunlin"),
    ("koajisashi", "コアジサシ", "Little tern"),
    ("ajisashi", "アジサシ", "Common tern"),
    ("oosegurokamome", "オオセグロカモメ", "Slaty-backed gull"),
    # タカ目（残り）
    ("haiirochUhi", "ハイイロチュウヒ", "Hen harrier"),
    ("keashinosuri", "ケアシノスリ", "Rough-legged buzzard"),
    # フクロウ目（残り）
    ("ookonohazuku", "オオコノハズク", "Japanese scops owl"),
    ("torafuzuku", "トラフズク", "Long-eared owl"),
    # サイチョウ目
    ("yatsugashira", "ヤツガシラ", "Eurasian hoopoe"),
    # キツツキ目（残り）
    ("ooakagera", "オオアカゲラ", "White-backed woodpecker"),
    ("yamagera", "ヤマゲラ", "Grey-headed woodpecker"),
    ("noguchigera", "ノグチゲラ", "Okinawa woodpecker"),
    # ハヤブサ目（残り）
    ("chigohayabusa", "チゴハヤブサ", "Eurasian hobby"),
    # スズメ目（残り）
    ("sanshokui", "サンショウクイ", "Ashy minivet"),
    ("chigomozu", "チゴモズ", "Brown shrike"),
    ("akamozu", "アカモズ", "Bull-headed shrike"),
    ("oomozu", "オオモズ", "Great grey shrike"),
    ("rurikakesu", "ルリカケス", "Lidth's jay"),
    ("kokumarugarasu", "コクマルガラス", "Daurian jackdaw"),
    ("miyamagarasu", "ミヤマガラス", "Rook"),
    ("watarigarasu", "ワタリガラス", "Common raven"),
    ("hashibutogara", "ハシブトガラ", "Marsh tit"),
    ("shoudoutsubame", "ショウドウツバメ", "Bank swallow"),
    ("shirogashira", "シロガシラ", "Chinese bulbul"),
    ("meguro", "メグロ", "Bonin white-eye"),
    ("oosekka", "オオセッカ", "Japanese marsh warbler"),
    ("hakkachou", "ハッカチョウ", "Crested myna"),
    ("ginmukudori", "ギンムクドリ", "Red-cheeked starling"),
    ("hoshimukudori", "ホシムクドリ", "Common starling"),
]


def get_wikipedia_image(article_title):
    """Wikipedia英語版の記事からメイン画像のURLを取得"""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query", "titles": article_title,
        "prop": "pageimages", "piprop": "original|thumbnail",
        "pithumbsize": 500, "format": "json",
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
        return thumb.get("source"), original.get("source")
    return None, None


def get_wikipedia_image_ja(article_title):
    """日本語Wikipedia fallback"""
    url = "https://ja.wikipedia.org/w/api.php"
    params = {
        "action": "query", "titles": article_title,
        "prop": "pageimages", "piprop": "original|thumbnail",
        "pithumbsize": 500, "format": "json",
    }
    try:
        resp = SESSION.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception:
        return None, None
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        thumb = page.get("thumbnail", {})
        original = page.get("original", {})
        return thumb.get("source"), original.get("source")
    return None, None


def get_commons_license(filename):
    """Wikimedia Commonsからライセンス情報を取得"""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "titles": f"File:{filename}",
        "prop": "imageinfo", "iiprop": "extmetadata", "format": "json",
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
        artist = re.sub(r"<[^>]+>", "", artist).strip()
        return {
            "license": meta.get("LicenseShortName", {}).get("value", "Unknown"),
            "artist": artist,
            "license_url": meta.get("LicenseUrl", {}).get("value", ""),
        }
    return {"license": "Unknown", "artist": "Unknown", "license_url": ""}


def extract_filename_from_url(url):
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


def download_and_resize(url, filepath, max_size=500):
    try:
        resp = SESSION.get(url, timeout=30)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        if img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size
        if max(w, h) > max_size:
            ratio = max_size / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        img.save(filepath, "JPEG", quality=85)
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    credits = {}
    if os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, "r", encoding="utf-8") as f:
            credits = json.load(f)

    results = []
    failed = []

    for i, (romaji, jp_name, en_title) in enumerate(BIRDS_BATCH2):
        print(f"[{i+1}/{len(BIRDS_BATCH2)}] {jp_name} ({en_title})...", flush=True)
        filepath = os.path.join(IMAGES_DIR, f"{romaji}.jpg")

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  Already exists, skipping")
            results.append((romaji, jp_name))
            continue

        # Try English Wikipedia first, then Japanese
        thumb_url, orig_url = get_wikipedia_image(en_title)
        if not thumb_url:
            time.sleep(0.5)
            thumb_url, orig_url = get_wikipedia_image_ja(jp_name)

        if not thumb_url:
            print(f"  [FAIL] No image found")
            failed.append((romaji, jp_name, en_title))
            time.sleep(1)
            continue

        success = download_and_resize(thumb_url, filepath)
        if not success and orig_url:
            time.sleep(1)
            success = download_and_resize(orig_url, filepath)

        if success:
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

        time.sleep(1)

    with open(CREDITS_FILE, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    print(f"\n=== Results ===")
    print(f"Success: {len(results)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("\nFailed list:")
        for r, jp, en in failed:
            print(f"  {jp} ({en}) - {r}")


if __name__ == "__main__":
    main()
