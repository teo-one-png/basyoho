"""
GBIF API 経由で xeno-canto の鳥の鳴き声をダウンロードするスクリプト。
音源は CC BY-NC 4.0 ライセンスです。

使い方: python download_nakigoe.py
"""

import json
import os
import time
import urllib.request
import urllib.parse
import subprocess
import shutil

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ffmpeg があれば mp3 に変換
FFMPEG = shutil.which("ffmpeg")

# xeno-canto dataset key in GBIF
XC_DATASET_KEY = "b1047888-ae52-4179-9dd5-5448ea342a24"

BIRDS = [
    {"id": "uguisu", "name": "ウグイス", "scientific": "Horornis diphone"},
    {"id": "shijuukara", "name": "シジュウカラ", "scientific": "Parus minor"},
    {"id": "yamagara", "name": "ヤマガラ", "scientific": "Sittiparus varius"},
    {"id": "mejiro", "name": "メジロ", "scientific": "Zosterops japonicus"},
    {"id": "hoojiro", "name": "ホオジロ", "scientific": "Emberiza cioides"},
    {"id": "kawarahiwa", "name": "カワラヒワ", "scientific": "Chloris sinica"},
    {"id": "mozu", "name": "モズ", "scientific": "Lanius bucephalus"},
    {"id": "hiyodori", "name": "ヒヨドリ", "scientific": "Hypsipetes amaurotis"},
    {"id": "isohiyodori", "name": "イソヒヨドリ", "scientific": "Monticola solitarius"},
    {"id": "suzume", "name": "スズメ", "scientific": "Passer montanus"},
    {"id": "tsubame", "name": "ツバメ", "scientific": "Hirundo rustica"},
    {"id": "segurosekirei", "name": "セグロセキレイ", "scientific": "Motacilla grandis"},
    {"id": "hakusekirei", "name": "ハクセキレイ", "scientific": "Motacilla alba lugens"},
    {"id": "kibitaki", "name": "キビタキ", "scientific": "Ficedula narcissina"},
    {"id": "ooruri", "name": "オオルリ", "scientific": "Cyanoptila cyanomelana"},
    {"id": "sankouchou", "name": "サンコウチョウ", "scientific": "Terpsiphone atrocaudata"},
    {"id": "ooyoshikiri", "name": "オオヨシキリ", "scientific": "Acrocephalus orientalis"},
    {"id": "joubitaki", "name": "ジョウビタキ", "scientific": "Phoenicurus auroreus"},
    {"id": "enaga", "name": "エナガ", "scientific": "Aegithalos caudatus"},
    {"id": "mukudori", "name": "ムクドリ", "scientific": "Spodiopsar cineraceus"},
    {"id": "hototogisu", "name": "ホトトギス", "scientific": "Cuculus poliocephalus"},
    {"id": "kakkou", "name": "カッコウ", "scientific": "Cuculus canorus"},
    {"id": "kijibato", "name": "キジバト", "scientific": "Streptopelia orientalis"},
    {"id": "kojukei", "name": "コジュケイ", "scientific": "Bambusicola thoracicus"},
    {"id": "kogera", "name": "コゲラ", "scientific": "Yungipicus kizuki"},
    {"id": "tobi", "name": "トビ", "scientific": "Milvus migrans"},
    {"id": "keri", "name": "ケリ", "scientific": "Vanellus cinereus"},
    {"id": "kaitsuburi", "name": "カイツブリ", "scientific": "Tachybaptus ruficollis"},
    {"id": "kiji", "name": "キジ", "scientific": "Phasianus versicolor"},
]

CALL_TYPES = [
    {"suffix": "saezuri", "label": "さえずり", "keywords": ["song", "SONG"]},
    {"suffix": "jinaki", "label": "地鳴き", "keywords": ["call", "CALL", "alarm"]},
]

CREDITS = {}


def search_gbif_xc(scientific_name, limit=50):
    """GBIF API 経由で xeno-canto の録音を検索"""
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
    """結果から指定タイプの最適な録音を選択"""
    candidates = []

    for r in results:
        media_list = r.get("media", [])
        for m in media_list:
            if m.get("type") != "Sound":
                continue
            url = m.get("identifier", "")
            if not url:
                continue

            # ファイル名や説明からタイプを判定
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
                # mp3 を優先
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

    # 日本の録音を優先、次にmp3を優先
    candidates.sort(key=lambda c: (
        0 if c["country"] == "Japan" else 1,
        0 if c["is_mp3"] else 1,
    ))

    return candidates[0] if candidates else None


def download_file(url, output_path):
    """ファイルをダウンロード"""
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


def convert_to_mp3(input_path, output_path):
    """ffmpeg で mp3 に変換"""
    if not FFMPEG:
        return False
    try:
        subprocess.run(
            [FFMPEG, "-y", "-i", input_path, "-acodec", "libmp3lame", "-q:a", "4",
             "-t", "15", output_path],
            capture_output=True, timeout=30
        )
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            os.remove(input_path)
            return True
    except Exception as e:
        print(f"  変換エラー: {e}")
    return False


def main():
    if FFMPEG:
        print(f"ffmpeg が見つかりました: {FFMPEG}")
    else:
        print("ffmpeg が見つかりません。wav/ogg ファイルはそのまま保存されます。")

    total = len(BIRDS) * len(CALL_TYPES)
    done = 0
    failed = []

    for bird in BIRDS:
        # GBIF から全録音を一括検索
        print(f"\n=== {bird['name']} ({bird['scientific']}) ===")
        results = search_gbif_xc(bird["scientific"])
        print(f"  GBIF結果: {len(results)}件")

        if not results:
            # 属名だけで再検索
            genus = bird["scientific"].split()[0]
            print(f"  属名 {genus} で再検索...")
            results = search_gbif_xc(genus)
            print(f"  再検索結果: {len(results)}件")

        for ct in CALL_TYPES:
            done += 1
            filename = f"{bird['id']}_{ct['suffix']}.mp3"
            output_path = os.path.join(AUDIO_DIR, filename)

            # 既にダウンロード済みならスキップ
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"  [{done}/{total}] スキップ（既存）: {ct['label']}")
                continue

            print(f"  [{done}/{total}] {ct['label']}を検索中...")

            rec = find_best_recording(results, ct["keywords"])

            if not rec:
                print(f"    *** 見つかりませんでした")
                failed.append(f"{bird['name']} {ct['label']}")
                continue

            url = rec["url"]
            print(f"    ダウンロード中: {url[:80]}...")

            # 拡張子に応じてダウンロード
            ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
            if ext in ("mp3",):
                tmp_path = output_path
            else:
                tmp_path = output_path.replace(".mp3", f".{ext}")

            success = download_file(url, tmp_path)
            if not success:
                failed.append(f"{bird['name']} {ct['label']}")
                continue

            # mp3 でなければ変換
            if tmp_path != output_path:
                if FFMPEG:
                    print(f"    mp3に変換中...")
                    if convert_to_mp3(tmp_path, output_path):
                        print(f"    変換完了")
                    else:
                        print(f"    変換失敗、元のファイルを使用")
                        os.rename(tmp_path, output_path.replace(".mp3", f".{ext}"))
                        # データファイルでは元の拡張子を使う
                        filename = f"{bird['id']}_{ct['suffix']}.{ext}"
                else:
                    os.rename(tmp_path, output_path.replace(".mp3", f".{ext}"))
                    filename = f"{bird['id']}_{ct['suffix']}.{ext}"

            print(f"    保存完了: {filename}")
            CREDITS[f"{bird['id']}_{ct['suffix']}"] = {
                "xc_id": rec.get("xc_id", ""),
                "recorder": rec["recorder"],
                "license": rec["license"],
                "url": url,
                "bird_name": bird["name"],
                "call_type": ct["label"],
            }

            time.sleep(0.5)

    # クレジット情報を保存
    credits_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nakigoe_credits.json")
    with open(credits_path, "w", encoding="utf-8") as f:
        json.dump(CREDITS, f, ensure_ascii=False, indent=2)
    print(f"\nクレジット情報を保存: {credits_path}")

    if failed:
        print(f"\n--- 失敗した項目 ({len(failed)}件) ---")
        for f_item in failed:
            print(f"  - {f_item}")
    else:
        print(f"\n全{total}件のダウンロードが完了しました！")

    print(f"\n成功: {total - len(failed)}/{total}")


if __name__ == "__main__":
    main()
