"""
不足している鳥の鳴き声を、キーワードマッチを緩めて再取得する。
見つからなかった鳥は、タイプ不問で1つだけでもダウンロードする。
"""

import json
import os
import time
import urllib.request
import urllib.parse

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
XC_DATASET_KEY = "b1047888-ae52-4179-9dd5-5448ea342a24"

# 不足している鳥
BIRDS = [
    {"id": "kawarahiwa", "name": "カワラヒワ", "scientific": "Chloris sinica"},
    {"id": "akagera", "name": "アカゲラ", "scientific": "Dendrocopos major"},
    {"id": "ikaru", "name": "イカル", "scientific": "Eophona personata"},
    {"id": "ruribitaki", "name": "ルリビタキ", "scientific": "Tarsiger cyanurus"},
    {"id": "aoji", "name": "アオジ", "scientific": "Emberiza spodocephala"},
    {"id": "uso", "name": "ウソ", "scientific": "Pyrrhula pyrrhula"},
    {"id": "benimasiko", "name": "ベニマシコ", "scientific": "Uragus sibiricus"},
    {"id": "kashiradaka", "name": "カシラダカ", "scientific": "Emberiza rustica"},
    {"id": "miyamahoojiro", "name": "ミヤマホオジロ", "scientific": "Emberiza elegans"},
    # 片方だけ不足
    {"id": "hashibosogarasu", "name": "ハシボソガラス", "scientific": "Corvus corone"},
    {"id": "kawasemi", "name": "カワセミ", "scientific": "Alcedo atthis"},
    {"id": "misosazai", "name": "ミソサザイ", "scientific": "Troglodytes troglodytes"},
    {"id": "aogera", "name": "アオゲラ", "scientific": "Picus awokera"},
    {"id": "kakesu", "name": "カケス", "scientific": "Garrulus glandarius"},
    {"id": "karugamo", "name": "カルガモ", "scientific": "Anas zonorhyncha"},
    {"id": "ooban", "name": "オオバン", "scientific": "Fulica atra"},
    {"id": "ban", "name": "バン", "scientific": "Gallinula chloropus"},
    {"id": "aosagi", "name": "アオサギ", "scientific": "Ardea cinerea"},
    {"id": "chougenbou", "name": "チョウゲンボウ", "scientific": "Falco tinnunculus"},
    {"id": "tsugumi", "name": "ツグミ", "scientific": "Turdus naumanni"},
]

CALL_TYPES = [
    {"suffix": "saezuri", "label": "さえずり", "keywords": ["song", "SONG", "sing"]},
    {"suffix": "jinaki", "label": "地鳴き", "keywords": ["call", "CALL", "alarm", "contact"]},
]


def search_gbif(scientific_name, limit=80):
    # Try both xeno-canto and general search
    results = []
    for dataset_key in [XC_DATASET_KEY, None]:
        params = {
            "scientificName": scientific_name,
            "mediaType": "Sound",
            "limit": limit,
        }
        if dataset_key:
            params["datasetKey"] = dataset_key
        url = f"https://api.gbif.org/v1/occurrence/search?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BirdCallApp/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results.extend(data.get("results", []))
        except Exception as e:
            print(f"  検索エラー: {e}")
        if results:
            break
    return results


def find_recording(results, keywords, fallback=False):
    candidates = []
    for r in results:
        for m in r.get("media", []):
            if m.get("type") != "Sound":
                continue
            url = m.get("identifier", "")
            if not url:
                continue

            url_upper = url.upper()
            desc = (m.get("description", "") or "").upper()
            remarks = (r.get("occurrenceRemarks", "") or "").upper()

            matched = fallback  # fallback=True means accept any
            if not fallback:
                for kw in keywords:
                    if kw.upper() in url_upper or kw.upper() in desc or kw.upper() in remarks:
                        matched = True
                        break

            if matched:
                is_mp3 = url.lower().endswith(".mp3")
                candidates.append({
                    "url": url,
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
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  ダウンロードエラー: {e}")
        return False


def main():
    credits_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nakigoe_credits.json")
    credits = {}
    if os.path.exists(credits_path):
        with open(credits_path, "r", encoding="utf-8") as f:
            credits = json.load(f)

    failed = []
    downloaded = 0

    for bird in BIRDS:
        print(f"\n=== {bird['name']} ({bird['scientific']}) ===")
        results = search_gbif(bird["scientific"])
        print(f"  検索結果: {len(results)}件")

        for ct in CALL_TYPES:
            key = f"{bird['id']}_{ct['suffix']}"

            # 既にファイルがあればスキップ
            existing = False
            for ext in [".mp3", ".wav", ".ogg"]:
                p = os.path.join(AUDIO_DIR, f"{key}{ext}")
                if os.path.exists(p) and os.path.getsize(p) > 1000:
                    existing = True
                    break
            if existing:
                continue

            print(f"  {ct['label']}を検索中...")

            # まずキーワードマッチ
            rec = find_recording(results, ct["keywords"])

            # 見つからなければフォールバック（タイプ不問）
            if not rec:
                print(f"    キーワードなし、タイプ不問で検索...")
                rec = find_recording(results, [], fallback=True)

            if not rec:
                print(f"    *** 見つかりませんでした")
                failed.append(f"{bird['name']} {ct['label']}")
                continue

            url = rec["url"]
            ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
            if ext not in ("mp3", "wav", "ogg"):
                ext = "mp3"

            output_path = os.path.join(AUDIO_DIR, f"{key}.{ext}")
            print(f"    ダウンロード中...")

            if download_file(url, output_path):
                print(f"    保存完了: {key}.{ext}")
                credits[key] = {
                    "xc_id": rec.get("xc_id", ""),
                    "recorder": rec["recorder"],
                    "license": rec["license"],
                    "url": url,
                    "bird_name": bird["name"],
                    "call_type": ct["label"],
                }
                downloaded += 1
            else:
                failed.append(f"{bird['name']} {ct['label']}")

            time.sleep(0.5)

    with open(credits_path, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    print(f"\n追加ダウンロード: {downloaded}件")
    if failed:
        print(f"失敗: {len(failed)}件")
        for f_item in failed:
            print(f"  - {f_item}")


if __name__ == "__main__":
    main()
