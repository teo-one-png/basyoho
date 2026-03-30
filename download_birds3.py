"""
残り全種をダウンロードするスクリプト（第3弾）
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

# 残りの種: (romaji_id, 日本語名, Wikipedia英語版記事タイトル)
BIRDS_BATCH3 = [
    # ペリカン目 — サギ科（残り）
    ("sankanogoi", "サンカノゴイ", "Eurasian bittern"),
    ("yoshigoi", "ヨシゴイ", "Yellow bittern"),
    ("ooyoshigoi", "オオヨシゴイ", "Schrenck's bittern"),
    ("ryuukyuuyoshigoi", "リュウキュウヨシゴイ", "Cinnamon bittern"),
    ("mizogoi", "ミゾゴイ", "Japanese night heron"),
    ("zuguromizogoi", "ズグロミゾゴイ", "Malayan night heron"),
    ("akagashirasagi", "アカガシラサギ", "Chinese pond heron"),
    # ツル目（残り）
    ("shiroharakuina", "シロハラクイナ", "White-breasted waterhen"),
    # カッコウ目（残り）
    ("segurokakkou", "セグロカッコウ", "Indian cuckoo"),
    # アマツバメ目（残り）
    ("harioamatsubame", "ハリオアマツバメ", "White-throated needletail"),
    ("himeamatsubame", "ヒメアマツバメ", "House swift"),
    # チドリ目（残り — シギ・カモメ等）
    ("sorihashiseitakashigi", "ソリハシセイタカシギ", "Pied avocet"),
    ("amamiyamashigi", "アマミヤマシギ", "Amami woodcock"),
    ("aoshigi", "アオシギ", "Solitary snipe"),
    ("oohashishigi", "オオハシシギ", "Long-billed dowitcher"),
    ("daishakushigi", "ダイシャクシギ", "Eurasian curlew"),
    ("tsurushigi", "ツルシギ", "Spotted redshank"),
    ("akaashishigi", "アカアシシギ", "Common redshank"),
    ("koaoashishigi", "コアオアシシギ", "Marsh sandpiper"),
    ("kusashigi", "クサシギ", "Green sandpiper"),
    ("takabushigi", "タカブシギ", "Wood sandpiper"),
    ("sorihashishigi", "ソリハシシギ", "Terek sandpiper"),
    ("obashigi", "オバシギ", "Great knot"),
    ("miyubishigi", "ミユビシギ", "Sanderling"),
    ("ojirotounen", "オジロトウネン", "Temminck's stint"),
    ("hibarishigi", "ヒバリシギ", "Long-toed stint"),
    ("uzurashigi", "ウズラシギ", "Sharp-tailed sandpiper"),
    ("saruhamashigi", "サルハマシギ", "Curlew sandpiper"),
    ("herashigi", "ヘラシギ", "Spoon-billed sandpiper"),
    ("erimakishigi", "エリマキシギ", "Ruff"),
    ("akaerihireashishigi", "アカエリヒレアシシギ", "Red-necked phalarope"),
    ("renkaku", "レンカク", "Pheasant-tailed jacana"),
    ("tamashigi", "タマシギ", "Greater painted-snipe"),
    ("mifuuzura", "ミフウズラ", "Barred buttonquail"),
    ("tsubamechidori", "ツバメチドリ", "Oriental pratincole"),
    ("kuroajisashi", "クロアジサシ", "Brown noddy"),
    ("mitsuyubikamome", "ミツユビカモメ", "Black-legged kittiwake"),
    ("zugurokamome", "ズグロカモメ", "Saunders's gull"),
    ("kamome", "カモメ", "Common gull"),
    ("washikamome", "ワシカモメ", "Glaucous-winged gull"),
    ("shirokamome", "シロカモメ", "Glaucous gull"),
    ("beniajisashi", "ベニアジサシ", "Roseate tern"),
    ("eriguroajisashi", "エリグロアジサシ", "Black-naped tern"),
    ("touzokukamome", "トウゾクカモメ", "Pomarine jaeger"),
    ("umigarasu", "ウミガラス", "Common murre"),
    ("keimafuri", "ケイマフリ", "Spectacled guillemot"),
    ("umisuzume", "ウミスズメ", "Ancient murrelet"),
    ("kanmuriUmisuzume", "カンムリウミスズメ", "Japanese murrelet"),
    ("utou", "ウトウ", "Rhinoceros auklet"),
    ("etopirika", "エトピリカ", "Tufted puffin"),
    # ウミツバメ科
    ("himekuroumitsubame", "ヒメクロウミツバメ", "Swinhoe's storm petrel"),
    # チシマウガラス
    ("chishimaugarasu", "チシマウガラス", "Red-faced cormorant"),
    # フクロウ目（残り）
    ("ryuukyuukonohazuku", "リュウキュウコノハズク", "Ryukyu scops owl"),
    # オウム目
    ("honseiinko", "ホンセイインコ", "Rose-ringed parakeet"),
    # スズメ目（残り）
    ("yaIrochou", "ヤイロチョウ", "Fairy pitta"),
    ("ryuukyuusanshoukui", "リュウキュウサンショウクイ", "Ryukyu minivet"),
    ("kouraiuguisu", "コウライウグイス", "Black-naped oriole"),
    ("ouchuu", "オウチュウ", "Black drongo"),
    ("oriigara", "オリイガラ", "Owston's tit"),
    ("tsurisugara", "ツリスガラ", "Penduline tit"),
    ("kimayumushikui", "キマユムシクイ", "Yellow-browed warbler"),
    ("mebosomushikui", "メボソムシクイ", "Japanese leaf warbler"),
    ("ezomushikui", "エゾムシクイ", "Sakhalin leaf warbler"),
    ("iijimamushikui", "イイジマムシクイ", "Ijima's leaf warbler"),
    ("makinosennyu", "マキノセンニュウ", "Middendorff's grasshopper warbler"),
    ("shimasennyu", "シマセンニュウ", "Pleske's grasshopper warbler"),
    ("uchiyamasennyu", "ウチヤマセンニュウ", "Styan's grasshopper warbler"),
    ("ezosennyu", "エゾセンニュウ", "Gray's grasshopper warbler"),
    ("koyoshikiri", "コヨシキリ", "Black-browed reed warbler"),
    ("kibashiri", "キバシリ", "Eurasian treecreeper"),
    ("mamijiro", "マミジロ", "Siberian thrush"),
    ("minamitoratsugumi", "ミナミトラツグミ", "White's thrush"),
    ("karaakahara", "カラアカハラ", "Grey-backed thrush"),
    ("mamichajinai", "マミチャジナイ", "Eyebrowed thrush"),
    ("akahige", "アカヒゲ", "Ryukyu robin"),
    ("nogoma", "ノゴマ", "Siberian rubythroat"),
    ("koruri", "コルリ", "Siberian blue robin"),
    ("shimagoma", "シマゴマ", "Rufous-tailed robin"),
    ("ezobitaki", "エゾビタキ", "Grey-streaked flycatcher"),
    ("samebitaki", "サメビタキ", "Dark-sided flycatcher"),
    ("kosamebitaki", "コサメビタキ", "Asian brown flycatcher"),
    ("mugimaki", "ムギマキ", "Mugimaki flycatcher"),
    ("nishiojiRobitaki", "ニシオジロビタキ", "Red-breasted flycatcher"),
    ("kayakuguri", "カヤクグリ", "Japanese accentor"),
    ("nyuunaIsuzume", "ニュウナイスズメ", "Russet sparrow"),
    ("shimakinpara", "シマキンパラ", "Scaly-breasted munia"),
    ("tsumenagasekirei", "ツメナガセキレイ", "Western yellow wagtail"),
    ("mamijirotahibari", "マミジロタヒバリ", "Richard's pipit"),
    ("muneakatahibari", "ムネアカタヒバリ", "Red-throated pipit"),
    ("tahibari", "タヒバリ", "Water pipit"),
    ("benihiwa", "ベニヒワ", "Common redpoll"),
    ("hagimashiko", "ハギマシコ", "Asian rosy finch"),
    ("akamashiko", "アカマシコ", "Common rosefinch"),
    ("oomashiko", "オオマシコ", "Pallas's rosefinch"),
    ("ginzanmashiko", "ギンザンマシコ", "Pine grosbeak"),
    ("isuka", "イスカ", "Red crossbill"),
    ("koikaru", "コイカル", "Chinese grosbeak"),
    ("tsumenagahoojiro", "ツメナガホオジロ", "Lapland longspur"),
    ("yukihoojiro", "ユキホオジロ", "Snow bunting"),
    ("hooaka", "ホオアカ", "Chestnut-eared bunting"),
    ("kohooaka", "コホオアカ", "Little bunting"),
    ("kimayuhoojiro", "キマユホオジロ", "Yellow-browed bunting"),
    ("miyamahoojiro", "ミヤマホオジロ", "Yellow-throated bunting"),
    ("shimaaoji", "シマアオジ", "Yellow-breasted bunting"),
    ("nojiko", "ノジコ", "Japanese yellow bunting"),
    ("kuroji", "クロジ", "Grey bunting"),
    ("kojurin", "コジュリン", "Japanese reed bunting"),
    # hontouakahige is subspecies, skip
]


def get_wikipedia_image(article_title):
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
        print(f"  API error: {e}")
        return None, None
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        thumb = page.get("thumbnail", {})
        original = page.get("original", {})
        return thumb.get("source"), original.get("source")
    return None, None


def get_wikipedia_image_ja(article_title):
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

    for i, (romaji, jp_name, en_title) in enumerate(BIRDS_BATCH3):
        print(f"[{i+1}/{len(BIRDS_BATCH3)}] {jp_name} ({en_title})...", flush=True)
        filepath = os.path.join(IMAGES_DIR, f"{romaji}.jpg")

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  Already exists, skipping")
            results.append((romaji, jp_name))
            continue

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
