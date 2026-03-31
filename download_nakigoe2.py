"""
GBIF API 経由で追加の鳥の鳴き声をダウンロードするスクリプト（第2弾）。
滋賀県で声が聞ける鳥のうち、まだ収録していない種を追加。
"""

import json
import os
import time
import urllib.request
import urllib.parse

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

XC_DATASET_KEY = "b1047888-ae52-4179-9dd5-5448ea342a24"

# 追加する鳥（滋賀県で声が聞ける鳥）
BIRDS = [
    # === 留鳥・漂鳥（年中聞ける） ===
    {"id": "kawarahiwa", "name": "カワラヒワ", "scientific": "Chloris sinica"},
    {"id": "hashibutogarasu", "name": "ハシブトガラス", "scientific": "Corvus macrorhynchos"},
    {"id": "hashibosogarasu", "name": "ハシボソガラス", "scientific": "Corvus corone"},
    {"id": "kawasemi", "name": "カワセミ", "scientific": "Alcedo atthis"},
    {"id": "hibari", "name": "ヒバリ", "scientific": "Alauda arvensis"},
    {"id": "misosazai", "name": "ミソサザイ", "scientific": "Troglodytes troglodytes"},
    {"id": "aogera", "name": "アオゲラ", "scientific": "Picus awokera"},
    {"id": "akagera", "name": "アカゲラ", "scientific": "Dendrocopos major"},
    {"id": "kakesu", "name": "カケス", "scientific": "Garrulus glandarius"},
    {"id": "ikaru", "name": "イカル", "scientific": "Eophona personata"},
    {"id": "gojuukara", "name": "ゴジュウカラ", "scientific": "Sitta europaea"},
    {"id": "higara", "name": "ヒガラ", "scientific": "Periparus ater"},
    {"id": "kogara", "name": "コガラ", "scientific": "Poecile montanus"},
    {"id": "kisekirei", "name": "キセキレイ", "scientific": "Motacilla cinerea"},
    {"id": "kawagarasu", "name": "カワガラス", "scientific": "Cinclus pallasii"},
    {"id": "fukurou", "name": "フクロウ", "scientific": "Strix uralensis"},
    {"id": "karugamo", "name": "カルガモ", "scientific": "Anas zonorhyncha"},
    {"id": "ooban", "name": "オオバン", "scientific": "Fulica atra"},
    {"id": "ban", "name": "バン", "scientific": "Gallinula chloropus"},
    {"id": "aosagi", "name": "アオサギ", "scientific": "Ardea cinerea"},
    {"id": "chougenbou", "name": "チョウゲンボウ", "scientific": "Falco tinnunculus"},
    # === 夏鳥（春〜夏に声が聞ける） ===
    {"id": "sendaimushikui", "name": "センダイムシクイ", "scientific": "Phylloscopus coronatus"},
    {"id": "yabusame", "name": "ヤブサメ", "scientific": "Urosphena squameiceps"},
    {"id": "kurotsugumi", "name": "クロツグミ", "scientific": "Turdus cardis"},
    {"id": "akashoubin", "name": "アカショウビン", "scientific": "Halcyon coromanda"},
    {"id": "komadori", "name": "コマドリ", "scientific": "Larvivora akahige"},
    {"id": "koruri", "name": "コルリ", "scientific": "Larvivora cyane"},
    {"id": "aobazuku", "name": "アオバズク", "scientific": "Ninox japonica"},
    {"id": "tsutsudori", "name": "ツツドリ", "scientific": "Cuculus optatus"},
    {"id": "juuichi", "name": "ジュウイチ", "scientific": "Hierococcyx hyperythrus"},
    # === 冬鳥（秋〜冬に声が聞ける） ===
    {"id": "tsugumi", "name": "ツグミ", "scientific": "Turdus naumanni"},
    {"id": "shirohara", "name": "シロハラ", "scientific": "Turdus pallidus"},
    {"id": "ruribitaki", "name": "ルリビタキ", "scientific": "Tarsiger cyanurus"},
    {"id": "aoji", "name": "アオジ", "scientific": "Emberiza spodocephala"},
    {"id": "uso", "name": "ウソ", "scientific": "Pyrrhula pyrrhula"},
    {"id": "benimasiko", "name": "ベニマシコ", "scientific": "Uragus sibiricus"},
    {"id": "kashiradaka", "name": "カシラダカ", "scientific": "Emberiza rustica"},
    {"id": "miyamahoojiro", "name": "ミヤマホオジロ", "scientific": "Emberiza elegans"},
]

CALL_TYPES = [
    {"suffix": "saezuri", "label": "さえずり", "keywords": ["song", "SONG"]},
    {"suffix": "jinaki", "label": "地鳴き", "keywords": ["call", "CALL", "alarm"]},
]


def search_gbif_xc(scientific_name, limit=50):
    params = urllib.parse.urlencode({
        "datasetKey": XC_DATASET_KEY,
        "scientificName": scientific_name,
        "mediaType": "Sound",
        "limit": limit,
    })
    url = f"https://api.gbif.org/v1/occurrence/search?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BirdCallApp/1.0 (educational)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("results", [])
    except Exception as e:
        print(f"  GBIF検索エラー: {e}")
        return []


def find_best_recording(results, call_type_keywords):
    candidates = []
    for r in results:
        media_list = r.get("media", [])
        for m in media_list:
            if m.get("type") != "Sound":
                continue
            url = m.get("identifier", "")
            if not url:
                continue
            url_upper = url.upper()
            desc = (m.get("description", "") or "").upper()
            remarks = (r.get("occurrenceRemarks", "") or "").upper()
            matched = False
            for kw in call_type_keywords:
                kw_upper = kw.upper()
                if kw_upper in url_upper or kw_upper in desc or kw_upper in remarks:
                    matched = True
                    break
            if matched:
                is_mp3 = url.lower().endswith(".mp3")
                candidates.append({
                    "url": url,
                    "format": m.get("format", ""),
                    "is_mp3": is_mp3,
                    "recorder": r.get("recordedBy", "Unknown"),
                    "xc_id": url.split("XC")[-1].split("-")[0].split(".")[0] if "XC" in url else "",
                    "license": r.get("license", "CC BY-NC 4.0"),
                    "country": r.get("country", ""),
                })
    candidates.sort(key=lambda c: (
        0 if c["country"] == "Japan" else 1,
        0 if c["is_mp3"] else 1,
    ))
    return candidates[0] if candidates else None


def download_file(url, output_path):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            with open(output_path, "wb") as f:
                f.write(content)
        return True
    except Exception as e:
        print(f"  ダウンロードエラー: {e}")
        return False


def main():
    total = len(BIRDS) * len(CALL_TYPES)
    done = 0
    failed = []
    credits = {}

    # 既存のクレジット読み込み
    credits_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nakigoe_credits.json")
    if os.path.exists(credits_path):
        with open(credits_path, "r", encoding="utf-8") as f:
            credits = json.load(f)

    for bird in BIRDS:
        print(f"\n=== {bird['name']} ({bird['scientific']}) ===")
        results = search_gbif_xc(bird["scientific"])
        print(f"  GBIF結果: {len(results)}件")

        if not results:
            genus = bird["scientific"].split()[0]
            print(f"  属名 {genus} で再検索...")
            results = search_gbif_xc(genus)
            print(f"  再検索結果: {len(results)}件")

        for ct in CALL_TYPES:
            done += 1
            filename_mp3 = f"{bird['id']}_{ct['suffix']}.mp3"
            output_path_mp3 = os.path.join(AUDIO_DIR, filename_mp3)

            # 既にダウンロード済みならスキップ（mp3 or wavチェック）
            existing = None
            for ext in [".mp3", ".wav", ".ogg"]:
                p = os.path.join(AUDIO_DIR, f"{bird['id']}_{ct['suffix']}{ext}")
                if os.path.exists(p) and os.path.getsize(p) > 1000:
                    existing = p
                    break

            if existing:
                print(f"  [{done}/{total}] スキップ（既存）: {bird['name']} {ct['label']}")
                continue

            print(f"  [{done}/{total}] {bird['name']} {ct['label']}を検索中...")

            rec = find_best_recording(results, ct["keywords"])

            if not rec:
                print(f"    *** 見つかりませんでした")
                failed.append(f"{bird['name']} {ct['label']}")
                continue

            url = rec["url"]
            print(f"    ダウンロード中...")

            ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
            if ext not in ("mp3", "wav", "ogg", "flac"):
                ext = "mp3"

            output_path = os.path.join(AUDIO_DIR, f"{bird['id']}_{ct['suffix']}.{ext}")
            success = download_file(url, output_path)

            if success:
                actual_filename = f"{bird['id']}_{ct['suffix']}.{ext}"
                print(f"    保存完了: {actual_filename}")
                credits[f"{bird['id']}_{ct['suffix']}"] = {
                    "xc_id": rec.get("xc_id", ""),
                    "recorder": rec["recorder"],
                    "license": rec["license"],
                    "url": url,
                    "bird_name": bird["name"],
                    "call_type": ct["label"],
                }
            else:
                failed.append(f"{bird['name']} {ct['label']}")

            time.sleep(0.5)

    # クレジット情報を保存
    with open(credits_path, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)
    print(f"\nクレジット情報を更新: {credits_path}")

    if failed:
        print(f"\n--- 失敗した項目 ({len(failed)}件) ---")
        for f_item in failed:
            print(f"  - {f_item}")

    print(f"\n成功: {total - len(failed)}/{total}")


if __name__ == "__main__":
    main()
