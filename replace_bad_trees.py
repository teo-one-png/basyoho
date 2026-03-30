"""
不適切な樹木画像を葉の写真に差し替えるスクリプト
- Commons APIで学名+leaf/leavesで検索
- ファイル名に leaf/leaves/foliage/Blatt を含む画像を優先
- 日本語Wikipedia fallback
"""

import requests, json, time, re, os
from PIL import Image
from io import BytesIO
from urllib.parse import unquote

IMAGES_DIR = "images/trees"
CREDITS_FILE = "credits.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "TreeMemoryApp/1.0 (https://github.com/goren; educational) Python-requests/2.32",
})

# 差し替え対象: (romaji_id, 日本語名, 学名)
BAD_IMAGES = [
    # Batch 1
    ("abemaki", "アベマキ", "Quercus variabilis"),
    ("aburachan", "アブラチャン", "Lindera praecox"),
    ("akashide", "アカシデ", "Carpinus laxiflora"),
    ("akinire", "アキニレ", "Ulmus parvifolia"),
    ("aodamo", "アオダモ", "Fraxinus lanuginosa"),
    ("aogiri", "アオギリ", "Firmiana simplex"),
    ("aohada", "アオハダ", "Ilex macropoda"),
    ("asunaro", "アスナロ", "Thujopsis dolabrata"),
    ("awabuki", "アワブキ", "Meliosma myriantha"),
    ("azukinashi", "アズキナシ", "Sorbus alnifolia"),
    ("bodaiju", "ボダイジュ", "Tilia miqueliana"),
    ("buna", "ブナ", "Fagus crenata"),
    ("ezomatsu", "エゾマツ", "Picea jezoensis"),
    ("gamazumi", "ガマズミ", "Viburnum dilatatum"),
    ("gekkeiju", "ゲッケイジュ", "Laurus nobilis"),
    ("gonzui", "ゴンズイ", "Euscaphis japonica"),
    ("goyoumatsu", "ゴヨウマツ", "Pinus parviflora"),
    ("goyoutsutsuji", "ゴヨウツツジ", "Rhododendron quinquefolium"),
    ("hainoki", "ハイノキ", "Symplocos myrtacea"),
    ("hakoneutsugi", "ハコネウツギ", "Weigela coraeensis"),
    ("hakusanshakunage", "ハクサンシャクナゲ", "Rhododendron brachycarpum"),
    ("hananoki", "ハナノキ", "Acer pycnanthum"),
    ("hannoki", "ハンノキ", "Alnus japonica"),
    ("harienju", "ハリエンジュ", "Robinia pseudoacacia"),
    ("harunire", "ハルニレ", "Ulmus davidiana"),
    # Batch 2
    ("himeshara", "ヒメシャラ", "Stewartia monadelpha"),
    ("hinoki", "ヒノキ", "Chamaecyparis obtusa"),
    ("hisakaki", "ヒサカキ", "Eurya japonica"),
    ("hitotsubatago", "ヒトツバタゴ", "Chionanthus retusus"),
    ("horutonoki", "ホルトノキ", "Elaeocarpus sylvestris"),
    ("ibotanoki", "イボタノキ", "Ligustrum obtusifolium"),
    ("ichou", "イチョウ", "Ginkgo biloba"),
    ("inubiwa", "イヌビワ", "Ficus erecta"),
    ("inubuna", "イヌブナ", "Fagus japonica"),
    ("inumaki", "イヌマキ", "Podocarpus macrophyllus"),
    ("irohamomiji", "イロハモミジ", "Acer palmatum"),
    ("isunoki", "イスノキ", "Distylium racemosum"),
    ("kajinoki", "カジノキ", "Broussonetia papyrifera"),
    ("kagonoki", "カゴノキ", "Litsea coreana"),
    ("kanamemochi", "カナメモチ", "Photinia glabra"),
    ("kamatsuka", "カマツカ", "Pourthiaea villosa"),
    ("karatachi", "カラタチ", "Citrus trifoliata"),
    ("kashiwa", "カシワ", "Quercus dentata"),
    ("kasumizakura", "カスミザクラ", "Prunus verecunda"),
    ("kibushi", "キブシ", "Stachyurus praecox"),
    ("kihada", "キハダ", "Phellodendron amurense"),
    ("kizuta", "キヅタ", "Hedera rhombea"),
    # Batch 3
    ("kuchinashi", "クチナシ", "Gardenia jasminoides"),
    ("kurobe", "クロベ", "Thuja standishii"),
    ("kuromoji", "クロモジ", "Lindera umbellata"),
    ("kuri", "クリ", "Castanea crenata"),
    ("marubachishanoki", "マルバチシャノキ", "Ehretia dicksonii"),
    ("matatabi", "マタタビ", "Actinidia polygama"),
    ("matebashii", "マテバシイ", "Lithocarpus edulis"),
    ("megi", "メギ", "Berberis thunbergii"),
    ("megusurinoki", "メグスリノキ", "Acer nikoense"),
    ("mizuki", "ミズキ", "Cornus controversa"),
    ("mizume", "ミズメ", "Betula grossa"),
    ("mube", "ムベ", "Stauntonia hexaphylla"),
    ("mukuroji", "ムクロジ", "Sapindus mukorossi"),
    ("murasaki_shikibu", "ムラサキシキブ", "Callicarpa japonica"),
    ("nagi", "ナギ", "Nageia nagi"),
    ("nanakamado", "ナナカマド", "Sorbus commixta"),
    ("nawashirogumi", "ナワシログミ", "Elaeagnus pungens"),
    ("nekoyanagi", "ネコヤナギ", "Salix gracilistyla"),
    ("nejiki", "ネジキ", "Lyonia ovalifolia"),
    ("nezumimochi", "ネズミモチ", "Ligustrum japonicum"),
    ("nezumisashi", "ネズミサシ", "Juniperus rigida"),
    ("mokuren", "モクレン", "Magnolia liliiflora"),
    ("natsugumi", "ナツグミ", "Elaeagnus multiflora"),
    ("niwatoko", "ニワトコ", "Sambucus racemosa"),
    # Batch 4
    ("oobayashabushi", "オオバヤシャブシ", "Alnus sieboldiana"),
    ("ooshimazakura", "オオシマザクラ", "Cerasus speciosa"),
    ("ooyamarenge", "オオヤマレンゲ", "Magnolia sieboldii"),
    ("ooyamazakura", "オオヤマザクラ", "Prunus sargentii"),
    ("rinboku", "リンボク", "Prunus spinulosa"),
    ("saikachi", "サイカチ", "Gleditsia japonica"),
    ("sakaki", "サカキ", "Cleyera japonica"),
    ("sanshou", "サンショウ", "Zanthoxylum piperitum"),
    ("sarusuberi", "サルスベリ", "Lagerstroemia indica"),
    ("sarutoriibara", "サルトリイバラ", "Smilax china"),
    ("satsuki", "サツキ", "Rhododendron indicum"),
    ("sawafutagi", "サワフタギ", "Symplocos sawafutagi"),
    ("sawashiba", "サワシバ", "Carpinus cordata"),
    ("shirakaba", "シラカバ", "Betula platyphylla"),
    ("shidareyanagi", "シダレヤナギ", "Salix babylonica"),
    ("shimotsuke", "シモツケ", "Spiraea japonica"),
    ("shiroyanagi", "シロヤナギ", "Salix jessoensis"),
    ("sudajii", "スダジイ", "Castanopsis sieboldii"),
    ("suikazura", "スイカズラ", "Lonicera japonica"),
    ("suzukakenoki", "スズカケノキ", "Platanus orientalis"),
    ("tabunoki", "タブノキ", "Machilus thunbergii"),
    ("taisanboku", "タイサンボク", "Magnolia grandiflora"),
    ("taniutsugi", "タニウツギ", "Weigela hortensis"),
    ("tobera", "トベラ", "Pittosporum tobira"),
    ("todomatsu", "トドマツ", "Abies sachalinensis"),
    # Batch 5
    ("toneriko", "トネリコ", "Fraxinus japonica"),
    ("tsuga", "ツガ", "Tsuga sieboldii"),
    ("tsukubaneutsugi", "ツクバネウツギ", "Abelia spathulata"),
    ("tsuta", "ツタ", "Parthenocissus tricuspidata"),
    ("ume", "ウメ", "Prunus mume"),
    ("urajirogashi", "ウラジロガシ", "Quercus salicina"),
    ("urihadakaede", "ウリハダカエデ", "Acer rufinerve"),
    ("yamaajisai", "ヤマアジサイ", "Hydrangea serrata"),
    ("yamabuki", "ヤマブキ", "Kerria japonica"),
    ("yamahagi", "ヤマハギ", "Lespedeza bicolor"),
    ("yamahaze", "ヤマハゼ", "Toxicodendron sylvestre"),
    ("yamamomo", "ヤマモモ", "Morella rubra"),
    ("yamatsutsuji", "ヤマツツジ", "Rhododendron kaempferi"),
    ("yamaurushi", "ヤマウルシ", "Toxicodendron trichocarpum"),
    ("yamazakura", "ヤマザクラ", "Cerasus jamasakura"),
    ("yatsude", "ヤツデ", "Fatsia japonica"),
    ("yukitsubaki", "ユキツバキ", "Camellia rusticana"),
    ("zakuro", "ザクロ", "Punica granatum"),
    ("zumi", "ズミ", "Malus toringo"),
    ("inuzakura", "イヌザクラ", "Prunus buergeriana"),
    ("tsuribana", "ツリバナ", "Euonymus oxyphyllus"),
]


def search_commons_leaf_strict(scientific_name):
    """Commons APIで葉の画像を検索。ファイル名にleaf/leavesを含むものを優先"""
    url = "https://commons.wikimedia.org/w/api.php"

    # Try multiple search queries
    queries = [
        f"File: {scientific_name} leaf",
        f"File: {scientific_name} leaves",
        f"File: {scientific_name} foliage",
        f"File: {scientific_name} Blatt",
    ]

    all_candidates = []

    for query in queries:
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 15,
            "gsrnamespace": 6,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size|mime",
            "iiurlwidth": 600,
            "format": "json",
        }
        try:
            resp = SESSION.get(url, params=params, timeout=15)
            data = resp.json()
        except Exception:
            continue

        pages = data.get("query", {}).get("pages", {})
        if not pages:
            continue

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

            title = page.get("title", "").lower()
            thumb_url = info.get("thumburl", info.get("url", ""))
            original_url = info.get("url", "")
            artist = meta.get("Artist", {}).get("value", "Unknown")
            artist = re.sub(r"<[^>]+>", "", artist).strip()
            license_url = meta.get("LicenseUrl", {}).get("value", "")

            # Score: prefer filenames with leaf-related words
            score = 0
            leaf_words = ["leaf", "leaves", "foliage", "blatt", "feuille", "folha"]
            for lw in leaf_words:
                if lw in title:
                    score += 10
            # Penalize flowers, fruit, bark, etc.
            bad_words = ["flower", "fruit", "bark", "seed", "cone", "blossom", "berry", "fleur", "habitus"]
            for bw in bad_words:
                if bw in title:
                    score -= 5

            all_candidates.append({
                "thumb_url": thumb_url,
                "original_url": original_url,
                "license": license_short,
                "license_url": license_url,
                "artist": artist,
                "title": page.get("title", ""),
                "score": score,
            })

        time.sleep(0.3)

    if all_candidates:
        all_candidates.sort(key=lambda c: c["score"], reverse=True)
        return all_candidates[0]
    return None


def get_ja_wikipedia_image(jp_name):
    """日本語Wikipediaからメイン画像を取得"""
    url = "https://ja.wikipedia.org/w/api.php"
    params = {
        "action": "query", "titles": jp_name,
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
        thumb = page.get("thumbnail", {}).get("source")
        orig = page.get("original", {}).get("source")
        return thumb, orig
    return None, None


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
    with open(CREDITS_FILE, "r", encoding="utf-8") as f:
        credits = json.load(f)

    replaced = 0
    failed = []

    for i, (romaji, jp_name, sci_name) in enumerate(BAD_IMAGES):
        print(f"[{i+1}/{len(BAD_IMAGES)}] {jp_name} ({sci_name})...", flush=True)
        filepath = os.path.join(IMAGES_DIR, f"{romaji}.jpg")
        backup = filepath + ".bak"

        # Backup current bad image
        if os.path.exists(filepath) and not os.path.exists(backup):
            os.rename(filepath, backup)

        # Try Commons leaf-specific search
        info = search_commons_leaf_strict(sci_name)

        if info and info["score"] >= 5:
            dl_url = info["thumb_url"] or info["original_url"]
            success = download_and_resize(dl_url, filepath)
            if success:
                print(f"  [REPLACED] score={info['score']} ({info['license']})")
                credits[f"tree_{romaji}"] = {
                    "name_jp": jp_name,
                    "artist": info["artist"],
                    "license": info["license"],
                    "license_url": info["license_url"],
                    "source": info["title"],
                    "original_url": info["original_url"],
                }
                replaced += 1
                time.sleep(0.5)
                continue

        # Fallback: try Japanese Wikipedia
        time.sleep(0.5)
        thumb_url, orig_url = get_ja_wikipedia_image(jp_name)
        if thumb_url:
            success = download_and_resize(thumb_url, filepath)
            if success:
                print(f"  [REPLACED via ja.wiki]")
                # Get license info
                parts = (orig_url or thumb_url).split("/wikipedia/commons/")
                fn = None
                if len(parts) >= 2:
                    segs = parts[1].split("/")
                    if parts[1].startswith("thumb/") and len(segs) >= 4:
                        fn = unquote(segs[3])
                    elif len(segs) >= 3:
                        fn = unquote(segs[2])

                lic_info = {"license": "Wikimedia Commons", "artist": "Unknown", "license_url": ""}
                if fn:
                    time.sleep(0.3)
                    try:
                        r2 = SESSION.get("https://commons.wikimedia.org/w/api.php", params={
                            "action": "query", "titles": f"File:{fn}",
                            "prop": "imageinfo", "iiprop": "extmetadata", "format": "json",
                        }, timeout=15)
                        d2 = r2.json()
                        for p2 in d2.get("query", {}).get("pages", {}).values():
                            meta = p2.get("imageinfo", [{}])[0].get("extmetadata", {})
                            a = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "Unknown")).strip()
                            lic_info = {
                                "license": meta.get("LicenseShortName", {}).get("value", "Unknown"),
                                "artist": a,
                                "license_url": meta.get("LicenseUrl", {}).get("value", ""),
                            }
                    except Exception:
                        pass

                credits[f"tree_{romaji}"] = {
                    "name_jp": jp_name,
                    "artist": lic_info["artist"],
                    "license": lic_info["license"],
                    "license_url": lic_info["license_url"],
                    "source": f"https://commons.wikimedia.org/wiki/File:{fn}" if fn else "",
                    "original_url": orig_url or thumb_url,
                }
                replaced += 1
                time.sleep(0.5)
                continue

        # If Commons had any result (even low score), use it
        if info:
            dl_url = info["thumb_url"] or info["original_url"]
            success = download_and_resize(dl_url, filepath)
            if success:
                print(f"  [REPLACED] low-score={info['score']} ({info['license']})")
                credits[f"tree_{romaji}"] = {
                    "name_jp": jp_name,
                    "artist": info["artist"],
                    "license": info["license"],
                    "license_url": info["license_url"],
                    "source": info["title"],
                    "original_url": info["original_url"],
                }
                replaced += 1
                time.sleep(0.5)
                continue

        # Restore backup if all failed
        if os.path.exists(backup) and not os.path.exists(filepath):
            os.rename(backup, filepath)
        print(f"  [KEEP OLD] No better image found")
        failed.append((romaji, jp_name))
        time.sleep(0.5)

    with open(CREDITS_FILE, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    # Clean up backups of successfully replaced images
    for f_name in os.listdir(IMAGES_DIR):
        if f_name.endswith(".bak"):
            os.remove(os.path.join(IMAGES_DIR, f_name))

    print(f"\n=== Results ===")
    print(f"Replaced: {replaced}/{len(BAD_IMAGES)}")
    print(f"Kept old: {len(failed)}")
    if failed:
        print("\nKept old list:")
        for r, jp in failed:
            print(f"  {jp} - {r}")


if __name__ == "__main__":
    main()
