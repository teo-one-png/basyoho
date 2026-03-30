"""
樹木の葉画像をWikimedia Commonsからダウンロードするスクリプト
葉の写真を優先的に取得するため、Commons APIで "leaves" "leaf" で検索
"""

import requests, json, time, re, os
from PIL import Image
from io import BytesIO
from urllib.parse import unquote

IMAGES_DIR = "images/trees"
CREDITS_FILE = "credits.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "TreeMemoryApp/1.0 (https://github.com/goren; educational project) Python-requests/2.32",
})

# 主要100種: (romaji_id, 日本語名, Commons検索キーワード（学名 + leaf）)
TREES = [
    # ブナ科
    ("konara", "コナラ", "Quercus serrata leaves"),
    ("kunugi", "クヌギ", "Quercus acutissima leaves"),
    ("kashiwa", "カシワ", "Quercus dentata leaves"),
    ("mizunara", "ミズナラ", "Quercus crispula leaves"),
    ("ubamegashi", "ウバメガシ", "Quercus phillyraeoides leaves"),
    ("arakashi", "アラカシ", "Quercus glauca leaves"),
    ("shirakashi", "シラカシ", "Quercus myrsinifolia leaves"),
    ("buna", "ブナ", "Fagus crenata leaves"),
    ("kuri", "クリ", "Castanea crenata leaves"),
    ("sudajii", "スダジイ", "Castanopsis sieboldii leaves"),
    ("matebashii", "マテバシイ", "Lithocarpus edulis leaves"),
    # ニレ科
    ("keyaki", "ケヤキ", "Zelkova serrata leaves"),
    ("enoki", "エノキ", "Celtis sinensis leaves"),
    ("mukunoki", "ムクノキ", "Aphananthe aspera leaves"),
    # カバノキ科
    ("shirakaba", "シラカバ", "Betula platyphylla leaves"),
    ("hannoki", "ハンノキ", "Alnus japonica leaves"),
    # カエデ科
    ("irohamomiji", "イロハモミジ", "Acer palmatum leaves"),
    ("oomomiji", "オオモミジ", "Acer amoenum leaves"),
    ("hauchiwakaede", "ハウチワカエデ", "Acer japonicum leaves"),
    ("itayakaede", "イタヤカエデ", "Acer pictum leaves"),
    ("toukaede", "トウカエデ", "Acer buergerianum leaves"),
    # モクレン科
    ("hoonoki", "ホオノキ", "Magnolia obovata leaves"),
    ("kobushi", "コブシ", "Magnolia kobus leaves"),
    ("mokuren", "モクレン", "Magnolia liliiflora leaves"),
    ("taisanboku", "タイサンボク", "Magnolia grandiflora leaves"),
    ("yurinoki", "ユリノキ", "Liriodendron tulipifera leaves"),
    # クスノキ科
    ("kusunoki", "クスノキ", "Cinnamomum camphora leaves"),
    ("tabunoki", "タブノキ", "Machilus thunbergii leaves"),
    ("kuromoji", "クロモジ", "Lindera umbellata leaves"),
    ("gekkeiju", "ゲッケイジュ", "Laurus nobilis leaves"),
    # バラ科
    ("yamazakura", "ヤマザクラ", "Cerasus jamasakura leaves"),
    ("ooshimazakura", "オオシマザクラ", "Cerasus speciosa leaves"),
    ("ume", "ウメ", "Prunus mume leaves"),
    ("yamabuki", "ヤマブキ", "Kerria japonica leaves"),
    ("nanakamado", "ナナカマド", "Sorbus commixta leaves"),
    # マメ科
    ("nemunoki", "ネムノキ", "Albizia julibrissin leaves"),
    ("fuji", "フジ", "Wisteria floribunda leaves"),
    ("harienju", "ハリエンジュ", "Robinia pseudoacacia leaves"),
    # ツバキ科
    ("yabutsubaki", "ヤブツバキ", "Camellia japonica leaves"),
    ("natsutsubaki", "ナツツバキ", "Stewartia pseudocamellia leaves"),
    ("sakaki", "サカキ", "Cleyera japonica leaves"),
    # カツラ科
    ("katsura", "カツラ", "Cercidiphyllum japonicum leaves"),
    # ミズキ科
    ("mizuki", "ミズキ", "Cornus controversa leaves"),
    ("yamaboushi", "ヤマボウシ", "Cornus kousa leaves"),
    ("hanamizuki", "ハナミズキ", "Cornus florida leaves"),
    ("aoki", "アオキ", "Aucuba japonica leaves"),
    # ウルシ科
    ("hazenoki", "ハゼノキ", "Toxicodendron succedaneum leaves"),
    ("nurude", "ヌルデ", "Rhus javanica leaves"),
    # ウコギ科
    ("yatsude", "ヤツデ", "Fatsia japonica leaves"),
    ("kakuremino", "カクレミノ", "Dendropanax trifidus leaves"),
    ("kizuta", "キヅタ", "Hedera rhombea leaves"),
    # ツツジ科
    ("yamatsutsuji", "ヤマツツジ", "Rhododendron kaempferi leaves"),
    ("asebi", "アセビ", "Pieris japonica leaves"),
    # モクセイ科
    ("kinmokusei", "キンモクセイ", "Osmanthus fragrans leaves"),
    ("hiiragi", "ヒイラギ", "Osmanthus heterophyllus leaves"),
    ("egonoki", "エゴノキ", "Styrax japonicus leaves"),
    # カキノキ科
    ("kakinoki", "カキノキ", "Diospyros kaki leaves"),
    # スイカズラ科
    ("gamazumi", "ガマズミ", "Viburnum dilatatum leaves"),
    # その他広葉樹
    ("yamamomo", "ヤマモモ", "Morella rubra leaves"),
    ("onigurumi", "オニグルミ", "Juglans mandshurica leaves"),
    ("tobera", "トベラ", "Pittosporum tobira leaves"),
    ("kiri", "キリ", "Paulownia tomentosa leaves"),
    ("sendan", "センダン", "Melia azedarach leaves"),
    ("tochinoki", "トチノキ", "Aesculus turbinata leaves"),
    ("sanshou", "サンショウ", "Zanthoxylum piperitum leaves"),
    ("nanten", "ナンテン", "Nandina domestica leaves"),
    ("sarusuberi", "サルスベリ", "Lagerstroemia indica leaves"),
    ("ichou", "イチョウ", "Ginkgo biloba leaves"),
    ("shinanoki", "シナノキ", "Tilia japonica leaves"),
    ("mube", "ムベ", "Stauntonia hexaphylla leaves"),
    ("akebi", "アケビ", "Akebia quinata leaves"),
    ("suzukakenoki", "スズカケノキ", "Platanus orientalis leaves"),
    ("zakuro", "ザクロ", "Punica granatum leaves"),
    # マンサク科
    ("mansaku", "マンサク", "Hamamelis japonica leaves"),
    # ニシキギ科
    ("nishikigi", "ニシキギ", "Euonymus alatus leaves"),
    ("mayumi", "マユミ", "Euonymus sieboldianus leaves"),
    # モチノキ科
    ("mochinoki", "モチノキ", "Ilex integra leaves"),
    # トベラ科 — already have tobera
    # グミ科
    ("natsugumi", "ナツグミ", "Elaeagnus multiflora leaves"),
    # スギ科・マツ科（針葉樹）
    ("sugi", "スギ", "Cryptomeria japonica leaves"),
    ("hinoki", "ヒノキ", "Chamaecyparis obtusa leaves"),
    ("akamatsu", "アカマツ", "Pinus densiflora leaves"),
    ("kuromatsu", "クロマツ", "Pinus thunbergii leaves"),
    ("momi", "モミ", "Abies firma leaves"),
    ("karamatsu", "カラマツ", "Larix kaempferi leaves"),
    ("metasekoia", "メタセコイア", "Metasequoia glyptostroboides leaves"),
    ("tsuga", "ツガ", "Tsuga sieboldii leaves"),
    # その他
    ("kusagi", "クサギ", "Clerodendrum trichotomum leaves"),
    ("megusurinoki", "メグスリノキ", "Acer nikoense leaves"),
    ("ryoubu", "リョウブ", "Clethra barbinervis leaves"),
    ("niwatoko", "ニワトコ", "Sambucus racemosa leaves"),
    ("murasaki_shikibu", "ムラサキシキブ", "Callicarpa japonica leaves"),
    ("iigiri", "イイギリ", "Idesia polycarpa leaves"),
    ("akamegashiwa", "アカメガシワ", "Mallotus japonicus leaves"),
    ("yuzuriha", "ユズリハ", "Daphniphyllum macropodum leaves"),
    ("taranoki", "タラノキ", "Aralia elata leaves"),
    ("harigiri", "ハリギリ", "Kalopanax septemlobus leaves"),
    ("shirodamo", "シロダモ", "Neolitsea sericea leaves"),
    ("matatabi", "マタタビ", "Actinidia polygama leaves"),
]


def search_commons_leaf(query, jp_name):
    """Commons APIで葉の画像を検索"""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"File: {query}",
        "gsrlimit": 10,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": 600,
        "format": "json",
    }
    try:
        resp = SESSION.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception as e:
        return None

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None

    candidates = []
    for page_id, page in pages.items():
        info = page.get("imageinfo", [{}])[0]
        mime = info.get("mime", "")
        if mime not in ("image/jpeg", "image/png"):
            continue
        w = info.get("width", 0)
        h = info.get("height", 0)
        if w < 200 or h < 200:
            continue

        meta = info.get("extmetadata", {})
        license_short = meta.get("LicenseShortName", {}).get("value", "")
        free_licenses = ["CC BY", "CC BY-SA", "CC0", "Public domain", "GFDL", "FAL"]
        is_free = any(fl.lower() in license_short.lower() for fl in free_licenses)
        if not is_free and license_short:
            continue

        thumb_url = info.get("thumburl", info.get("url", ""))
        original_url = info.get("url", "")
        artist = meta.get("Artist", {}).get("value", "Unknown")
        artist = re.sub(r"<[^>]+>", "", artist).strip()
        license_url = meta.get("LicenseUrl", {}).get("value", "")

        candidates.append({
            "thumb_url": thumb_url,
            "original_url": original_url,
            "license": license_short,
            "license_url": license_url,
            "artist": artist,
            "title": page.get("title", ""),
        })

    if candidates:
        return candidates[0]
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

    for i, (romaji, jp_name, query) in enumerate(TREES):
        print(f"[{i+1}/{len(TREES)}] {jp_name} ({query})...", flush=True)
        filepath = os.path.join(IMAGES_DIR, f"{romaji}.jpg")

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print("  Already exists, skipping")
            results.append((romaji, jp_name))
            continue

        info = search_commons_leaf(query, jp_name)

        # Fallback: try without "leaves"
        if not info:
            time.sleep(0.5)
            fallback_query = query.replace(" leaves", " leaf")
            info = search_commons_leaf(fallback_query, jp_name)

        if not info:
            time.sleep(0.5)
            # Try just scientific name
            sci_only = query.replace(" leaves", "")
            info = search_commons_leaf(sci_only, jp_name)

        if not info:
            print("  [FAIL] No image found")
            failed.append((romaji, jp_name, query))
            time.sleep(1)
            continue

        dl_url = info["thumb_url"] or info["original_url"]
        success = download_and_resize(dl_url, filepath)

        if success:
            print(f"  [OK] ({info['license']}, by {info['artist'][:40]})")
            results.append((romaji, jp_name))
            credits[f"tree_{romaji}"] = {
                "name_jp": jp_name,
                "artist": info["artist"],
                "license": info["license"],
                "license_url": info["license_url"],
                "source": info["title"],
                "original_url": info["original_url"],
            }
        else:
            print("  [FAIL] Download failed")
            failed.append((romaji, jp_name, query))

        time.sleep(1)

    with open(CREDITS_FILE, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    print(f"\n=== Results ===")
    print(f"Success: {len(results)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("\nFailed list:")
        for r, jp, q in failed:
            print(f"  {jp} ({q}) - {r}")


if __name__ == "__main__":
    main()
