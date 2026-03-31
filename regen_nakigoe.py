"""Regenerate nakigoe_data.js and nakigoe_credits.js from audio files."""
import os, json

AUDIO_DIR = "audio"
files = sorted(os.listdir(AUDIO_DIR))

birds = {}
for f in files:
    if not any(f.endswith(e) for e in ['.mp3', '.wav', '.ogg']):
        continue
    name_no_ext = f.rsplit('.', 1)[0]
    ext = f.rsplit('.', 1)[1]
    parts = name_no_ext.rsplit('_', 1)
    if len(parts) != 2:
        continue
    bird_id, call_type = parts
    if bird_id not in birds:
        birds[bird_id] = {}
    birds[bird_id][call_type] = ext

# Load credits
with open('nakigoe_credits.json', 'r', encoding='utf-8') as f:
    credits = json.load(f)

# Build name map from credits
NAMES = {}
for key, val in credits.items():
    bird_id = key.rsplit('_', 1)[0]
    if bird_id not in NAMES and 'bird_name' in val:
        NAMES[bird_id] = val['bird_name']

# Hardcoded fallback names
FALLBACK = {
    'akashoubin': 'アカショウビン', 'aobazuku': 'アオバズク', 'aoji': 'アオジ',
    'fukurou': 'フクロウ', 'gojuukara': 'ゴジュウカラ', 'hashibutogarasu': 'ハシブトガラス',
    'hibari': 'ヒバリ', 'higara': 'ヒガラ', 'juuichi': 'ジュウイチ',
    'kashiradaka': 'カシラダカ', 'kawagarasu': 'カワガラス', 'kisekirei': 'キセキレイ',
    'kogara': 'コガラ', 'komadori': 'コマドリ', 'koruri': 'コルリ',
    'kurotsugumi': 'クロツグミ', 'sendaimushikui': 'センダイムシクイ', 'shirohara': 'シロハラ',
    'tsutsudori': 'ツツドリ', 'yabusame': 'ヤブサメ', 'misosazai': 'ミソサザイ',
    'aogera': 'アオゲラ', 'akagera': 'アカゲラ', 'ikaru': 'イカル',
    'ruribitaki': 'ルリビタキ', 'benimasiko': 'ベニマシコ', 'miyamahoojiro': 'ミヤマホオジロ',
    'kawasemi': 'カワセミ', 'chougenbou': 'チョウゲンボウ',
}
NAMES.update(FALLBACK)

for bird_id in birds:
    if bird_id not in NAMES:
        NAMES[bird_id] = bird_id
        print(f"WARNING: no name for {bird_id}")

# Generate data JS
entries = []
for bird_id in sorted(birds.keys()):
    name = NAMES.get(bird_id, bird_id)
    types = birds[bird_id]
    if 'jinaki' in types:
        ext = types['jinaki']
        entries.append(f'  {{ id: "{bird_id}_jinaki", name: "{name}", callType: "\u5730\u9cf4\u304d", audio: "audio/{bird_id}_jinaki.{ext}" }}')
    if 'saezuri' in types:
        ext = types['saezuri']
        entries.append(f'  {{ id: "{bird_id}_saezuri", name: "{name}", callType: "\u3055\u3048\u305a\u308a", audio: "audio/{bird_id}_saezuri.{ext}" }}')

js = f"""// nakigoe_data.js - {len(birds)}\u7a2e {len(entries)}\u554f
// \u97f3\u6e90: xeno-canto (CC BY-NC 4.0) via GBIF

const NAKIGOE_DATA = [
{chr(44)+chr(10).join(entries)}
];
"""

with open('nakigoe_data.js', 'w', encoding='utf-8') as f:
    f.write(js)

# Generate credits JS
js_credits = {}
for key, val in credits.items():
    js_credits[key] = {
        'recorder': val.get('recorder', 'Unknown'),
        'license': 'CC BY-NC 4.0',
        'xc_id': val.get('xc_id', ''),
    }
with open('nakigoe_credits.js', 'w', encoding='utf-8') as f:
    f.write('const NAKIGOE_CREDITS = ' + json.dumps(js_credits, ensure_ascii=False, indent=2) + ';\n')

# Stats
total_size = sum(os.path.getsize(os.path.join(AUDIO_DIR, f)) for f in files if f.endswith(('.mp3', '.wav', '.ogg')))
wav_count = sum(1 for f in files if f.endswith('.wav'))
print(f"鳥の種数: {len(birds)}")
print(f"問題数: {len(entries)}")
print(f"合計サイズ: {total_size / 1024 / 1024:.1f} MB")
print(f"クレジット: {len(js_credits)}件")
print(f"残りwav: {wav_count}")
