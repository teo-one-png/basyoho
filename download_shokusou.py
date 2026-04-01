"""
shokusou quiz image downloader
Downloads images from Wikipedia/Wikimedia Commons for insects and plants.
"""
import os
import time
import requests

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images", "shokusou")

# shokusou_data.js から抽出した全種の id → name マッピング
SPECIES = {
    # ===== INSECT_DATA =====
    # チョウ類 - アゲハチョウ科
    "ageha": "アゲハ（ナミアゲハ）",
    "kuroageha": "クロアゲハ",
    "karasuageha": "カラスアゲハ",
    "nagasakiageha": "ナガサキアゲハ",
    "kiageha": "キアゲハ",
    "aosujiageha": "アオスジアゲハ",
    "jakouageha": "ジャコウアゲハ",
    "gifuchou": "ギフチョウ",
    # チョウ類 - シロチョウ科
    "monshirochou": "モンシロチョウ",
    "monkichou": "モンキチョウ",
    "kitakichou": "キタキチョウ",
    # チョウ類 - タテハチョウ科
    "akatateha": "アカタテハ",
    "ruritateha": "ルリタテハ",
    "kitateha": "キタテハ",
    "tsumagurohyoumon": "ツマグロヒョウモン",
    "ichimonjichou": "イチモンジチョウ",
    "oomurasaki": "オオムラサキ",
    "gomadarachou": "ゴマダラチョウ",
    "komurasaki": "コムラサキ",
    "ishigakechou": "イシガケチョウ",
    "kurokonomachou": "クロコノマチョウ",
    "asagimadara": "アサギマダラ",
    # チョウ類 - シジミチョウ科
    "komisuji": "コミスジ",
    "uraginshijimi": "ウラギンシジミ",
    "murasakitsubame": "ムラサキツバメ",
    "murasakishijimi": "ムラサキシジミ",
    "midorishijimi": "ミドリシジミ",
    "yamatoshijimi": "ヤマトシジミ",
    "benishijimi": "ベニシジミ",
    # チョウ類 - セセリチョウ科
    "aobaseseri": "アオバセセリ",
    "suminagashi": "スミナガシ",
    "daimyouseseri": "ダイミョウセセリ",
    "ichimonjiseseri": "イチモンジセセリ",
    # ガ類
    "hotaruga": "ホタルガ",
    "okinawaruri_chirashi": "オキナワルリチラシ",
    "minousuba": "ミノウスバ",
    "ibotaga": "イボタガ",
    "kiedashaku": "キエダシャク",
    "ooayashaku": "オオアヤシャク",
    "oosukashiba": "オオスカシバ",
    "hoshihoujaku": "ホシホウジャク",
    "kosuzume": "コスズメ",
    "kuwaedashaku": "クワエダシャク",
    "monhosobasuzume": "モンホソバスズメ",
    "murasakishachihoko": "ムラサキシャチホコ",
    "ashibenikagiba": "アシベニカギバ",
    "shinjusan": "シンジュサン",
    "usutabiga": "ウスタビガ",
    "yamamayu": "ヤママユ（ヤママユガ）",
    "takekareha": "タケカレハ",
    "takenohosokuroba": "タケノホソクロバ",
    "matsukareha": "マツカレハ",
    "chadokuga": "チャドクガ",
    "kinokawaga": "キノカワガ",
    "oogomadara_edashaku": "オオゴマダラエダシャク",
    "iraga": "イラガ",
    "akebikonoha": "アケビコノハ",
    "oomizuao": "オオミズアオ",
    "kususan": "クスサン",
    "maimaiga": "マイマイガ",
    # 甲虫類
    "gomadarakamikiri": "ゴマダラカミキリ",
    "kuwakamikiri": "クワカミキリ",
    "nijuuyahoshi_tentou": "ニジュウヤホシテントウ",
    "tohoshi_tentou": "トホシテントウ",
    "jingasahamushi": "ジンガサハムシ",
    "ichimonji_kamenokohamushi": "イチモンジカメノコハムシ",
    "tohoshi_kubibosohamushi": "トホシクビボソハムシ",
    "nirehamushi": "ニレハムシ",
    "tsutsuji_kobuhamushi": "ツツジコブハムシ",
    "akagane_saruhamushi": "アカガネサルハムシ",
    "heriguro_tentouno_mihamushi": "ヘリグロテントウノミハムシ",
    "drohamaki_chokkiri": "ドロハマキチョッキリ",
    "higenaga_otoshibumi": "ヒゲナガオトシブミ",
    "otoshibumi": "オトシブミ（ナミオトシブミ）",
    "shirosuji_kamikiri": "シロスジカミキリ",
    "ego_higenaga_zoumushi": "エゴヒゲナガゾウムシ",
    "ego_tsurukubi_otoshibumi": "エゴツルクビオトシブミ",
    # カメムシ類
    "akasuji_kamemushi": "アカスジカメムシ",
    "kibara_herikamemushi": "キバラヘリカメムシ",
    "esaki_monki_tsunokamemushi": "エサキモンキツノカメムシ",
    "akasuji_kinkamemushi": "アカスジキンカメムシ",
    "ookin_kamemushi": "オオキンカメムシ",
    "akagi_kamemushi": "アカギカメムシ",
    # 沖縄チョウ
    "shiroobi_ageha": "シロオビアゲハ",
    "tsumabeni_chou": "ツマベニチョウ",
    "namie_shirochou": "ナミエシロチョウ",
    "oogomadara": "オオゴマダラ",
    "kabamadara": "カバマダラ",
    "tsumamurasakimadara": "ツマムラサキマダラ",
    "ryuukyuu_asagimadara": "リュウキュウアサギマダラ",
    "konohachou": "コノハチョウ",
    "aotateha_modoki": "アオタテハモドキ",
    "iwakawa_shijimi": "イワカワシジミ",
    "banana_seseri": "バナナセセリ",

    # ===== PLANT_DATA =====
    # 樹木
    "mikan_rui": "ミカン類",
    "sanshou": "サンショウ",
    "karatachi": "カラタチ",
    "karasuzanshou": "カラスザンショウ",
    "kokusagi": "コクサギ",
    "kihada": "キハダ",
    "yuzu": "ユズ",
    "kusunoki": "クスノキ",
    "tabunoki": "タブノキ",
    "hagi_rui": "ハギ類",
    "nemunoki": "ネムノキ",
    "sarutoriibara": "サルトリイバラ",
    "suikazura": "スイカズラ",
    "enoki": "エノキ",
    "yanagi_rui": "ヤナギ類",
    "inubiwa": "イヌビワ",
    "fuji": "フジ",
    "matebashii": "マテバシイ",
    "arakashi": "アラカシ",
    "shirakashi": "シラカシ",
    "hannoki": "ハンノキ",
    "yamahannoki": "ヤマハンノキ",
    "awabuki": "アワブキ",
    "hisakaki": "ヒサカキ",
    "sakaki": "サカキ",
    "yabutsubaki": "ヤブツバキ",
    "masaki": "マサキ",
    "nishikigi": "ニシキギ",
    "mayumi": "マユミ",
    "ibotanoki": "イボタノキ",
    "nezumimochi": "ネズミモチ",
    "noibara": "ノイバラ",
    "kobushi": "コブシ",
    "hoonoki": "ホオノキ",
    "kuchinashi": "クチナシ",
    "kuwa_rui": "クワ類",
    "onigurumi": "オニグルミ",
    "gamazumi": "ガマズミ",
    "sangoju": "サンゴジュ",
    "kuroganemochi": "クロガネモチ",
    "konara": "コナラ",
    "kunugi": "クヌギ",
    "kuri": "クリ",
    "sakura_rui": "サクラ類",
    "take_rui": "タケ類",
    "matsu_rui": "マツ類",
    "tsubaki_rui": "ツバキ類",
    "sazanka": "サザンカ",
    "kakinoki": "カキノキ",
    "akebi": "アケビ",
    "mitsubaakebi": "ミツバアケビ",
    "hanamizuki": "ハナミズキ",
    "keyaki": "ケヤキ",
    "akinire": "アキニレ",
    "ichijiku": "イチジク",
    "suzukakenoki_rui": "スズカケノキ類",
    "murasakishikibu": "ムラサキシキブ",
    "kuko": "クコ",
    "tsutsuji_rui": "ツツジ類",
    "hiiragi_mokusei": "ヒイラギモクセイ",
    "hiiragi": "ヒイラギ",
    "aburachan": "アブラチャン",
    "kuromoji": "クロモジ",
    "egonoki": "エゴノキ",
    "mizuki": "ミズキ",
    "aburagiri": "アブラギリ",
    "akamegashiwa": "アカメガシワ",
    "shiikuwaasaa": "シークワーサー",
    "gyoboku": "ギョボク",
    "tsugemodoki": "ツゲモドキ",
    "hourai_kagami": "ホウライカガミ",
    "okinawa_teikakazura": "オキナワテイカカズラ",
    # 草本
    "seri": "セリ",
    "ninjin": "ニンジン",
    "mitsuba": "ミツバ",
    "umanosuzukusa_rui": "ウマノスズクサ類",
    "kanaoi_rui": "カンアオイ類",
    "kyabetsu": "キャベツ",
    "aburana_rui": "アブラナ類",
    "inugarashi": "イヌガラシ",
    "shirotsumekusa": "シロツメクサ",
    "medohagi": "メドハギ",
    "karamushi": "カラムシ",
    "akaso_rui": "アカソ類",
    "hototogisu_rui": "ホトトギス類",
    "kanamugura": "カナムグラ",
    "sumire_rui": "スミレ類",
    "juzudama": "ジュズダマ",
    "susuki": "ススキ",
    "kijoran": "キジョラン",
    "ikema": "イケマ",
    "kuzu": "クズ",
    "katabami": "カタバミ",
    "gishigishi_rui": "ギシギシ類",
    "suiba": "スイバ",
    "yamanoimo": "ヤマノイモ",
    "onidokoro": "オニドコロ",
    "ine": "イネ",
    "sasa_rui": "ササ類",
    "hekusokazura": "ヘクソカズラ",
    "yabugarashi": "ヤブガラシ",
    "inuhoozuki_rui": "イヌホオズキ類",
    "karasuuri": "カラスウリ",
    "hirugao": "ヒルガオ",
    "ebizuru": "エビヅル",
    "nobudou": "ノブドウ",
    "itadori": "イタドリ",
    "yabujirami": "ヤブジラミ",
    "touwata": "トウワタ",
    "tsurumourinka": "ツルモウリンカ",
    "okinawa_suzumushisou": "オキナワスズムシソウ",
    "iwadaresou": "イワダレソウ",
    "banana": "バナナ",
}

# Wikipedia記事タイトルが種名と異なる場合のマッピング
TITLE_OVERRIDES = {
    "アゲハ（ナミアゲハ）": "アゲハチョウ",
    "ヤママユ（ヤママユガ）": "ヤママユガ",
    "オトシブミ（ナミオトシブミ）": "オトシブミ",
    "ミカン類": "ウンシュウミカン",
    "クワ類": "クワ",
    "ヤナギ類": "シダレヤナギ",
    "マツ類": "アカマツ",
    "ツバキ類": "ツバキ",
    "ツツジ類": "ツツジ",
    "ハギ類": "ヤマハギ",
    "アカソ類": "アカソ",
    "ホトトギス類": "ホトトギス (植物)",
    "ウマノスズクサ類": "ウマノスズクサ",
    "カンアオイ類": "カンアオイ",
    "アブラナ類": "アブラナ",
    "スミレ類": "スミレ",
    "ギシギシ類": "ギシギシ",
    "タケ類": "モウソウチク",
    "ササ類": "アズマネザサ",
    "サクラ類": "ソメイヨシノ",
    "イヌホオズキ類": "イヌホオズキ",
    "スズカケノキ類": "モミジバスズカケノキ",
    # Additional fallback titles for species with no pageimage
    "アゲハ（ナミアゲハ）": "ナミアゲハ",
    "キタキチョウ": "キチョウ",
    "ヤマトシジミ": "ヤマトシジミ (蝶)",
    "コムラサキ": "コムラサキ (蝶)",
    "ムラサキツバメ": "ムラサキツバメ (蝶)",
    "ヤママユ（ヤママユガ）": "ヤママユ",
    "コスズメ": "コスズメ (蛾)",
    "シークワーサー": "シークヮーサー",
    "ヤブツバキ": "ツバキ",
    "ササ類": "ササ",
}

API_URL = "https://ja.wikipedia.org/w/api.php"
USER_AGENT = "ShokusouQuizApp/1.0 (Educational insect-plant quiz app; https://github.com/goren) requests/python"
MAX_RETRIES = 3
BASE_DELAY = 2  # seconds between requests

# Persistent session for connection reuse
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en;q=0.5",
})


def get_wiki_title(name):
    return TITLE_OVERRIDES.get(name, name)


def fetch_image_url(title):
    """Wikipedia API -> thumbnail URL (try pageimages first, then images fallback)"""
    # Method 1: pageimages (main article image)
    resp = SESSION.get(API_URL, params={
        "action": "query",
        "titles": title,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": 800,
        "pilicense": "any",
    }, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumb = page.get("thumbnail", {}).get("source")
        if thumb:
            return thumb

    # Method 2: get first image from article via images prop
    resp = SESSION.get(API_URL, params={
        "action": "query",
        "titles": title,
        "prop": "images",
        "format": "json",
        "imlimit": 10,
    }, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        images = page.get("images", [])
        for img in images:
            img_title = img.get("title", "")
            # Skip icons, logos, svg, commons category images
            lower = img_title.lower()
            if any(skip in lower for skip in [".svg", "icon", "logo", "commons", "flag", "map", "symbol", "status"]):
                continue
            if any(ext in lower for ext in [".jpg", ".jpeg", ".png"]):
                # Get the actual image URL via imageinfo
                resp2 = SESSION.get(API_URL, params={
                    "action": "query",
                    "titles": img_title,
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "iiurlwidth": 800,
                    "format": "json",
                }, timeout=15)
                resp2.raise_for_status()
                data2 = resp2.json()
                pages2 = data2.get("query", {}).get("pages", {})
                for p2 in pages2.values():
                    ii = p2.get("imageinfo", [{}])[0]
                    return ii.get("thumburl") or ii.get("url")
    return None


def download_image(image_url, dest_path):
    """Download image to file"""
    resp = SESSION.get(image_url, timeout=30)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)


def fetch_with_retry(wiki_title, dest):
    """Download with retry on 429"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            image_url = fetch_image_url(wiki_title)
            if not image_url:
                return "NO_IMAGE"
            download_image(image_url, dest)
            return "OK"
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429 and attempt < MAX_RETRIES:
                wait = BASE_DELAY * (2 ** attempt)
                print(f"  429 retry {attempt}/{MAX_RETRIES}, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
    return "FAIL"


def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)

    ok_count = 0
    skip_count = 0
    fail_count = 0
    total = len(SPECIES)

    for i, (species_id, name) in enumerate(SPECIES.items(), 1):
        dest = os.path.join(IMAGE_DIR, f"{species_id}.jpg")

        # 既にダウンロード済みならスキップ
        if os.path.exists(dest):
            print(f"[{i}/{total}] SKIP {species_id} ({name})")
            skip_count += 1
            continue

        wiki_title = get_wiki_title(name)
        try:
            result = fetch_with_retry(wiki_title, dest)
            if result == "NO_IMAGE":
                print(f"[{i}/{total}] FAIL {species_id} ({name}) - no image for '{wiki_title}'")
                fail_count += 1
            else:
                print(f"[{i}/{total}] OK   {species_id} ({name})")
                ok_count += 1
        except Exception as e:
            print(f"[{i}/{total}] FAIL {species_id} ({name}) - {e}")
            fail_count += 1

        time.sleep(BASE_DELAY)

    print(f"\n===== Done =====")
    print(f"OK: {ok_count}  SKIP: {skip_count}  FAIL: {fail_count}  TOTAL: {total}")


if __name__ == "__main__":
    main()
