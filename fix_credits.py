"""credits.jsonの不足分を補完するスクリプト"""
import requests, json, time, re, os
from urllib.parse import unquote

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "BirdMemoryApp/1.0 (educational) Python-requests/2.32"})

with open("credits.json", "r", encoding="utf-8") as f:
    credits = json.load(f)

birds = [
    ("raichou", "ライチョウ", "Rock ptarmigan"),
    ("kojukei", "コジュケイ", "Chinese bamboo partridge"),
    ("yamadori", "ヤマドリ", "Copper pheasant"),
    ("kiji", "キジ", "Green pheasant"),
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
    ("kaitsuburi", "カイツブリ", "Little grebe"),
    ("kanmurikaitsuburi", "カンムリカイツブリ", "Great crested grebe"),
    ("kawarabato", "カワラバト", "Rock dove"),
    ("aobato", "アオバト", "White-bellied green pigeon"),
    ("kounotori", "コウノトリ", "Oriental stork"),
    ("goisagi", "ゴイサギ", "Black-crowned night heron"),
    ("sasagoi", "ササゴイ", "Striated heron"),
    ("amasagi", "アマサギ", "Cattle egret"),
    ("daisagi", "ダイサギ", "Great egret"),
    ("toki", "トキ", "Crested ibis"),
    ("tanchou", "タンチョウ", "Red-crowned crane"),
    ("nabeduru", "ナベヅル", "Hooded crane"),
    ("ban", "バン", "Common moorhen"),
    ("ooban", "オオバン", "Eurasian coot"),
    ("kakkou", "カッコウ", "Common cuckoo"),
    ("hototogisu", "ホトトギス", "Lesser cuckoo"),
    ("tsutsudori", "ツツドリ", "Oriental cuckoo"),
    ("tageri", "タゲリ", "Northern lapwing"),
    ("keri", "ケリ", "Grey-headed lapwing"),
    ("kochidori", "コチドリ", "Little ringed plover"),
    ("isoshigi", "イソシギ", "Common sandpiper"),
    ("yurikamome", "ユリカモメ", "Black-headed gull"),
    ("umineko", "ウミネコ", "Black-tailed gull"),
    ("misago", "ミサゴ", "Osprey"),
    ("chuuhi", "チュウヒ", "Eastern marsh harrier"),
    ("inuwashi", "イヌワシ", "Golden eagle"),
    ("kanmuriwashi", "カンムリワシ", "Crested serpent eagle"),
    ("fukurou", "フクロウ", "Ural owl"),
    ("konohazuku", "コノハズク", "Eurasian scops owl"),
    ("komimizuku", "コミミズク", "Short-eared owl"),
    ("shimafukurou", "シマフクロウ", "Blakiston's fish owl"),
    ("akashoubin", "アカショウビン", "Ruddy kingfisher"),
    ("yamasemi", "ヤマセミ", "Crested kingfisher"),
    ("buppousou", "ブッポウソウ", "Oriental dollarbird"),
    ("kogera", "コゲラ", "Japanese pygmy woodpecker"),
    ("akagera", "アカゲラ", "Great spotted woodpecker"),
    ("aogera", "アオゲラ", "Japanese green woodpecker"),
    ("kumagera", "クマゲラ", "Black woodpecker"),
    ("arisui", "アリスイ", "Eurasian wryneck"),
    ("chougenbou", "チョウゲンボウ", "Common kestrel"),
    ("kakesu", "カケス", "Eurasian jay"),
    ("onaga", "オナガ", "Azure-winged magpie"),
    ("kasasagi", "カササギ", "Eurasian magpie"),
    ("kikuitadaki", "キクイタダキ", "Goldcrest"),
    ("kogara", "コガラ", "Willow tit"),
    ("higara", "ヒガラ", "Coal tit"),
    ("yamagara", "ヤマガラ", "Varied tit"),
    ("hibari", "ヒバリ", "Eurasian skylark"),
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
    ("isohiyodori", "イソヒヨドリ", "Blue rock thrush"),
    ("kibitaki", "キビタキ", "Narcissus flycatcher"),
    ("ooruri", "オオルリ", "Blue-and-white flycatcher"),
    ("iwahibari", "イワヒバリ", "Alpine accentor"),
]

missing = [(r, jp, en) for r, jp, en in birds if r not in credits]
print(f"Missing credits: {len(missing)}")

for i, (romaji, jp, en) in enumerate(missing):
    print(f"[{i+1}/{len(missing)}] {jp}...", end=" ", flush=True)

    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query", "titles": en, "prop": "pageimages",
            "piprop": "original", "format": "json",
        }
        r = SESSION.get(url, params=params, timeout=15)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        orig_url = None
        for pid, page in pages.items():
            orig_url = page.get("original", {}).get("source")

        if not orig_url:
            print("no URL")
            credits[romaji] = {"name_jp": jp, "artist": "Unknown", "license": "Wikimedia Commons", "license_url": "", "source": "", "original_url": ""}
            time.sleep(0.5)
            continue

        parts = orig_url.split("/wikipedia/commons/")
        filename = None
        if len(parts) >= 2:
            segs = parts[1].split("/")
            if len(segs) >= 3:
                filename = unquote(segs[2])

        if not filename:
            print("no filename")
            credits[romaji] = {"name_jp": jp, "artist": "Unknown", "license": "Wikimedia Commons", "license_url": "", "source": "", "original_url": orig_url}
            time.sleep(0.5)
            continue

        time.sleep(0.5)
        params2 = {
            "action": "query", "titles": f"File:{filename}",
            "prop": "imageinfo", "iiprop": "extmetadata", "format": "json",
        }
        r2 = SESSION.get("https://commons.wikimedia.org/w/api.php", params=params2, timeout=15)
        d2 = r2.json()
        for pid2, p2 in d2.get("query", {}).get("pages", {}).items():
            meta = p2.get("imageinfo", [{}])[0].get("extmetadata", {})
            a = meta.get("Artist", {}).get("value", "Unknown")
            a = re.sub(r"<[^>]+>", "", a).strip()
            lic = meta.get("LicenseShortName", {}).get("value", "Unknown")
            lic_url = meta.get("LicenseUrl", {}).get("value", "")
            credits[romaji] = {
                "name_jp": jp, "artist": a, "license": lic, "license_url": lic_url,
                "source": f"https://commons.wikimedia.org/wiki/File:{filename}",
                "original_url": orig_url,
            }
            print(f"{lic} by {a[:30]}")
    except Exception as e:
        print(f"error: {e}")
        credits[romaji] = {"name_jp": jp, "artist": "Unknown", "license": "Unknown", "license_url": "", "source": "", "original_url": ""}

    time.sleep(0.8)

with open("credits.json", "w", encoding="utf-8") as f:
    json.dump(credits, f, ensure_ascii=False, indent=2)
print(f"\nTotal credits now: {len(credits)}")
