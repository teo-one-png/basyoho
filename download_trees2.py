"""
樹木の残り約154種をダウンロードするスクリプト
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

# 残り154種
TREES_BATCH2 = [
    # カバノキ科（残り）
    ("keyamahannoki", "ケヤマハンノキ", "Alnus hirsuta leaves"),
    ("yashabushi", "ヤシャブシ", "Alnus firma leaves"),
    ("oobayashabushi", "オオバヤシャブシ", "Alnus sieboldiana leaves"),
    ("udaikamba", "ウダイカンバ", "Betula maximowicziana leaves"),
    ("dakekamba", "ダケカンバ", "Betula ermanii leaves"),
    ("mizume", "ミズメ", "Betula grossa leaves"),
    ("hashibami", "ハシバミ", "Corylus heterophylla leaves"),
    ("tsunohashibami", "ツノハシバミ", "Corylus sieboldiana leaves"),
    ("asada", "アサダ", "Ostrya japonica leaves"),
    ("sawashiba", "サワシバ", "Carpinus cordata leaves"),
    ("kumashide", "クマシデ", "Carpinus japonica leaves"),
    ("akashide", "アカシデ", "Carpinus laxiflora leaves"),
    ("inushide", "イヌシデ", "Carpinus tschonoskii leaves"),
    # ブナ科（残り）
    ("inubuna", "イヌブナ", "Fagus japonica leaves"),
    ("abemaki", "アベマキ", "Quercus variabilis leaves"),
    ("akagashi", "アカガシ", "Quercus acuta leaves"),
    ("ichiigashi", "イチイガシ", "Quercus gilva leaves"),
    ("urajirogashi", "ウラジロガシ", "Quercus salicina leaves"),
    # ニレ科（残り）
    ("harunire", "ハルニレ", "Ulmus davidiana leaves"),
    ("ohyou", "オヒョウ", "Ulmus laciniata leaves"),
    ("akinire", "アキニレ", "Ulmus parvifolia leaves"),
    # クワ科（残り）
    ("maguwa", "マグワ", "Morus alba leaves"),
    ("yamaguwa", "ヤマグワ", "Morus australis leaves"),
    ("kajinoki", "カジノキ", "Broussonetia papyrifera leaves"),
    ("himekouzo", "ヒメコウゾ", "Broussonetia kazinoki leaves"),
    ("inubiwa", "イヌビワ", "Ficus erecta leaves"),
    # モクレン科（残り）
    ("ogatamanoki", "オガタマノキ", "Michelia compressa leaves"),
    ("ooyamarenge", "オオヤマレンゲ", "Magnolia sieboldii leaves"),
    ("tamushiba", "タムシバ", "Magnolia salicifolia leaves"),
    # シキミ科
    ("shikimi", "シキミ", "Illicium anisatum leaves"),
    # クスノキ科（残り）
    ("yabunikkei", "ヤブニッケイ", "Cinnamomum yabunikkei leaves"),
    ("aburachan", "アブラチャン", "Lindera praecox leaves"),
    ("dankoubai", "ダンコウバイ", "Lindera obtusiloba leaves"),
    ("kagonoki", "カゴノキ", "Litsea coreana leaves"),
    # メギ科（残り）
    ("megi", "メギ", "Berberis thunbergii leaves"),
    # アケビ科（残り）
    ("mitsubaakebi", "ミツバアケビ", "Akebia trifoliata leaves"),
    # ツバキ科（残り）
    ("yukitsubaki", "ユキツバキ", "Camellia rusticana leaves"),
    ("himeshara", "ヒメシャラ", "Stewartia monadelpha leaves"),
    ("mokkoku", "モッコク", "Ternstroemia gymnanthera leaves"),
    ("hisakaki", "ヒサカキ", "Eurya japonica leaves"),
    # マンサク科（残り）
    ("marubanoki", "マルバノキ", "Disanthus cercidifolius leaves"),
    ("isunoki", "イスノキ", "Distylium racemosum leaves"),
    # ユキノシタ科
    ("noriutsugi", "ノリウツギ", "Hydrangea paniculata leaves"),
    ("gakuajisai", "ガクアジサイ", "Hydrangea macrophylla leaves"),
    ("yamaajisai", "ヤマアジサイ", "Hydrangea serrata leaves"),
    ("utsugi", "ウツギ", "Deutzia crenata leaves"),
    # バラ科（残り）
    ("shimotsuke", "シモツケ", "Spiraea japonica leaves"),
    ("inuzakura", "イヌザクラ", "Prunus buergeriana leaves"),
    ("uwamizuzakura", "ウワミズザクラ", "Prunus grayana leaves"),
    ("rinboku", "リンボク", "Prunus spinulosa leaves"),
    ("kanhizakura", "カンヒザクラ", "Prunus campanulata leaves"),
    ("edohigan", "エドヒガン", "Prunus itosakura leaves"),
    ("ooyamazakura", "オオヤマザクラ", "Prunus sargentii leaves"),
    ("kasumizakura", "カスミザクラ", "Prunus verecunda leaves"),
    ("noibara", "ノイバラ", "Rosa multiflora leaves"),
    ("hamanasu", "ハマナス", "Rosa rugosa leaves"),
    ("momijiichigo", "モミジイチゴ", "Rubus palmatus leaves"),
    ("azukinashi", "アズキナシ", "Sorbus alnifolia leaves"),
    ("sharinbai", "シャリンバイ", "Rhaphiolepis umbellata leaves"),
    ("kanamemochi", "カナメモチ", "Photinia glabra leaves"),
    ("kamatsuka", "カマツカ", "Pourthiaea villosa leaves"),
    ("zumi", "ズミ", "Malus toringo leaves"),
    # マメ科（残り）
    ("saikachi", "サイカチ", "Gleditsia japonica leaves"),
    ("enju", "エンジュ", "Styphnolobium japonicum leaves"),
    ("yamahagi", "ヤマハギ", "Lespedeza bicolor leaves"),
    ("marubahagi", "マルバハギ", "Lespedeza cyrtobotrya leaves"),
    # トウダイグサ科（残り）
    ("shiraki", "シラキ", "Neoshirakia japonica leaves"),
    # ミカン科（残り）
    ("kokusagi", "コクサギ", "Orixa japonica leaves"),
    ("kihada", "キハダ", "Phellodendron amurense leaves"),
    ("karatachi", "カラタチ", "Citrus trifoliata leaves"),
    # ウルシ科（残り）
    ("tsutaurushi", "ツタウルシ", "Toxicodendron orientale leaves"),
    ("yamaurushi", "ヤマウルシ", "Toxicodendron trichocarpum leaves"),
    ("yamahaze", "ヤマハゼ", "Toxicodendron sylvestre leaves"),
    # カエデ科（残り）
    ("hananoki", "ハナノキ", "Acer pycnanthum leaves"),
    ("yamamomiji", "ヤマモミジ", "Acer amoenum var. matsumurae leaves"),
    ("kohauchiwakaede", "コハウチワカエデ", "Acer sieboldianum leaves"),
    ("urihadakaede", "ウリハダカエデ", "Acer rufinerve leaves"),
    ("ooitayameigetsu", "オオイタヤメイゲツ", "Acer shirasawanum leaves"),
    ("hitotsubakaede", "ヒトツバカエデ", "Acer distylum leaves"),
    ("chidorinoki", "チドリノキ", "Acer carpinifolium leaves"),
    ("mitsudekaede", "ミツデカエデ", "Acer cissifolium leaves"),
    # ムクロジ科
    ("mukuroji", "ムクロジ", "Sapindus mukorossi leaves"),
    # アワブキ科
    ("awabuki", "アワブキ", "Meliosma myriantha leaves"),
    # モチノキ科（残り）
    ("inutsuge", "イヌツゲ", "Ilex crenata leaves"),
    ("tarayou", "タラヨウ", "Ilex latifolia leaves"),
    ("aohada", "アオハダ", "Ilex macropoda leaves"),
    ("umemodoki", "ウメモドキ", "Ilex serrata leaves"),
    # ニシキギ科（残り）
    ("masaki", "マサキ", "Euonymus japonicus leaves"),
    ("tsuribana", "ツリバナ", "Euonymus oxyphyllus leaves"),
    ("tsuruumemodoki", "ツルウメモドキ", "Celastrus orbiculatus leaves"),
    # ミツバウツギ科
    ("gonzui", "ゴンズイ", "Euscaphis japonica leaves"),
    # ツゲ科
    ("tsuge", "ツゲ", "Buxus microphylla leaves"),
    # ブドウ科
    ("yamabudou", "ヤマブドウ", "Vitis coignetiae leaves"),
    ("nobudou", "ノブドウ", "Ampelopsis glandulosa leaves"),
    ("tsuta", "ツタ", "Parthenocissus tricuspidata leaves"),
    # ホルトノキ科
    ("horutonoki", "ホルトノキ", "Elaeocarpus sylvestris leaves"),
    # シナノキ科（残り）
    ("bodaiju", "ボダイジュ", "Tilia miqueliana leaves"),
    # アオギリ科
    ("aogiri", "アオギリ", "Firmiana simplex leaves"),
    # グミ科（残り）
    ("nawashirogumi", "ナワシログミ", "Elaeagnus pungens leaves"),
    # キブシ科
    ("kibushi", "キブシ", "Stachyurus praecox leaves"),
    # ミズキ科（残り）
    ("hanaikada", "ハナイカダ", "Helwingia japonica leaves"),
    ("kumanomizuki", "クマノミズキ", "Cornus macrophylla leaves"),
    ("sanshuyu", "サンシュユ", "Cornus officinalis leaves"),
    # ウコギ科（残り）
    ("yamaukogi", "ヤマウコギ", "Eleutherococcus spinosus leaves"),
    ("koshiabura", "コシアブラ", "Chengiopanax sciadophylloides leaves"),
    # ツツジ科（残り）
    ("satsuki", "サツキ", "Rhododendron indicum leaves"),
    ("mitsubatsutsuji", "ミツバツツジ", "Rhododendron dilatatum leaves"),
    ("goyoutsutsuji", "ゴヨウツツジ", "Rhododendron quinquefolium leaves"),
    ("hakusanshakunage", "ハクサンシャクナゲ", "Rhododendron brachycarpum leaves"),
    ("azumashakunage", "アズマシャクナゲ", "Rhododendron degronianum leaves"),
    ("nejiki", "ネジキ", "Lyonia ovalifolia leaves"),
    # エゴノキ科
    ("hakuunboku", "ハクウンボク", "Styrax obassia leaves"),
    # ハイノキ科
    ("sawafutagi", "サワフタギ", "Symplocos sawafutagi leaves"),
    ("hainoki", "ハイノキ", "Symplocos myrtacea leaves"),
    # モクセイ科（残り）
    ("aodamo", "アオダモ", "Fraxinus lanuginosa leaves"),
    ("yachidamo", "ヤチダモ", "Fraxinus mandshurica leaves"),
    ("toneriko", "トネリコ", "Fraxinus japonica leaves"),
    ("hashidoi", "ハシドイ", "Syringa reticulata leaves"),
    ("hitotsubatago", "ヒトツバタゴ", "Chionanthus retusus leaves"),
    ("nezumimochi", "ネズミモチ", "Ligustrum japonicum leaves"),
    ("ibotanoki", "イボタノキ", "Ligustrum obtusifolium leaves"),
    # キョウチクトウ科
    ("teikakazura", "テイカカズラ", "Trachelospermum asiaticum leaves"),
    # アカネ科
    ("kuchinashi", "クチナシ", "Gardenia jasminoides leaves"),
    # ムラサキ科
    ("marubachishanoki", "マルバチシャノキ", "Ehretia dicksonii leaves"),
    # スイカズラ科（残り）
    ("kanboku", "カンボク", "Viburnum opulus leaves"),
    ("sangoju", "サンゴジュ", "Viburnum odoratissimum leaves"),
    ("ookamenoki", "オオカメノキ", "Viburnum furcatum leaves"),
    ("yabudemari", "ヤブデマリ", "Viburnum plicatum leaves"),
    ("otokoyouzome", "オトコヨウゾメ", "Viburnum phlebotrichum leaves"),
    ("tsukubaneutsugi", "ツクバネウツギ", "Abelia spathulata leaves"),
    ("hakoneutsugi", "ハコネウツギ", "Weigela coraeensis leaves"),
    ("taniutsugi", "タニウツギ", "Weigela hortensis leaves"),
    ("suikazura", "スイカズラ", "Lonicera japonica leaves"),
    ("uguisukagura", "ウグイスカグラ", "Lonicera gracilipes leaves"),
    # ユリ科
    ("sarutoriibara", "サルトリイバラ", "Smilax china leaves"),
    # 針葉樹（残り）
    ("goyoumatsu", "ゴヨウマツ", "Pinus parviflora leaves"),
    ("todomatsu", "トドマツ", "Abies sachalinensis leaves"),
    ("shirabiso", "シラビソ", "Abies veitchii leaves"),
    ("ezomatsu", "エゾマツ", "Picea jezoensis leaves"),
    ("himarayasugi", "ヒマラヤスギ", "Cedrus deodara leaves"),
    ("kouyamaki", "コウヤマキ", "Sciadopitys verticillata leaves"),
    ("nezumisashi", "ネズミサシ", "Juniperus rigida leaves"),
    ("sawara", "サワラ", "Chamaecyparis pisifera leaves"),
    ("kurobe", "クロベ", "Thuja standishii leaves"),
    ("asunaro", "アスナロ", "Thujopsis dolabrata leaves"),
    ("inumaki", "イヌマキ", "Podocarpus macrophyllus leaves"),
    ("nagi", "ナギ", "Nageia nagi leaves"),
    ("ichii", "イチイ", "Taxus cuspidata leaves"),
    ("kaya", "カヤ", "Torreya nucifera leaves"),
    # ヤナギ科（残り）
    ("doronoki", "ドロノキ", "Populus maximowiczii leaves"),
    ("shiroyanagi", "シロヤナギ", "Salix jessoensis leaves"),
    ("bakkoyanagi", "バッコヤナギ", "Salix caprea leaves"),
    ("shidareyanagi", "シダレヤナギ", "Salix babylonica leaves"),
    ("nekoyanagi", "ネコヤナギ", "Salix gracilistyla leaves"),
]


def search_commons_leaf(query):
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
    except Exception:
        return None

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None

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

        return {
            "thumb_url": thumb_url,
            "original_url": original_url,
            "license": license_short,
            "license_url": license_url,
            "artist": artist,
            "title": page.get("title", ""),
        }
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

    for i, (romaji, jp_name, query) in enumerate(TREES_BATCH2):
        print(f"[{i+1}/{len(TREES_BATCH2)}] {jp_name} ({query.split(' leaves')[0]})...", flush=True)
        filepath = os.path.join(IMAGES_DIR, f"{romaji}.jpg")

        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print("  Already exists, skipping")
            results.append((romaji, jp_name))
            continue

        info = search_commons_leaf(query)
        if not info:
            time.sleep(0.5)
            info = search_commons_leaf(query.replace(" leaves", " leaf"))
        if not info:
            time.sleep(0.5)
            info = search_commons_leaf(query.replace(" leaves", ""))

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
            print(f"  {jp} ({q.split(' leaves')[0]}) - {r}")


if __name__ == "__main__":
    main()
