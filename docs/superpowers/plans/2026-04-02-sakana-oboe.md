# さかなおぼえモード Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 琵琶湖の淡水魚（外来種含む80〜100種）の写真フラッシュカード暗記モード「さかなおぼえ」を既存アプリに追加する。

**Architecture:** 既存の「とり覚え」モードと同一パターン。`fish_data.js`に魚データ配列、`images/fish/`に横向き全身写真、`fish_credits.js`にクレジット。app.jsのモード分岐に`fish`を追加。

**Tech Stack:** Vanilla JS（既存アプリと同じ）、Python（画像ダウンロードスクリプト）、Wikimedia Commons API

---

## File Structure

| ファイル | 操作 | 責務 |
|---------|------|------|
| `fish_data.js` | 新規作成 | `FISH_DATA` 配列（80〜100種） |
| `fish_credits.js` | 新規作成 | `FISH_CREDITS` オブジェクト |
| `fish_credits.json` | 新規作成 | クレジットJSON（スクリプト出力） |
| `download_fish.py` | 新規作成 | Wikimedia Commons画像ダウンロード |
| `images/fish/` | 新規ディレクトリ | 魚の横向き全身写真 |
| `index.html` | 変更 | モードボタン追加、script読み込み追加 |
| `app.js` | 変更 | fish モード分岐追加 |
| `sw.js` | 変更 | キャッシュ対象にfish関連追加 |

---

### Task 1: fish_data.js — 琵琶湖淡水魚データ作成

**Files:**
- Create: `fish_data.js`

- [ ] **Step 1: 琵琶湖淡水魚のリストを調査・作成**

琵琶湖に生息する淡水魚（固有種・在来種・外来種）を網羅的にリストアップする。以下のカテゴリで整理：

固有種（ビワマス、ニゴロブナ、ゲンゴロウブナ、ホンモロコ、ビワヒガイ、ビワコオオナマズ、イサザ、ビワヨシノボリなど）、在来種（アユ、コイ、フナ類、オイカワ、カワムツ、ヌマムツ、ウグイ、タモロコ、モツゴ、ハス、ワタカ、ゼゼラ、カマツカ、ナマズ、ドジョウ類、ヨシノボリ類、カジカ、ウナギ、メダカ、ドンコなど）、外来種（オオクチバス、コクチバス、ブルーギル、チャネルキャットフィッシュ、タイリクバラタナゴなど）。

各種について英語版Wikipediaの記事タイトルを調べ、ローマ字IDを決定する。

- [ ] **Step 2: fish_data.js を作成**

`data.js`（BIRD_DATA）と同じ形式で作成。例：

```js
const FISH_DATA = [
  // ===== 固有種 - サケ科 =====
  { id: "biwamasu", name: "ビワマス", category: "魚類", image: "images/fish/biwamasu.jpg", tags: ["サケ科", "固有種"] },
  // ===== 固有種 - コイ科 =====
  { id: "nigorobuna", name: "ニゴロブナ", category: "魚類", image: "images/fish/nigorobuna.jpg", tags: ["コイ科", "固有種"] },
  { id: "gengoroubuuna", name: "ゲンゴロウブナ", category: "魚類", image: "images/fish/gengoroubuna.jpg", tags: ["コイ科", "固有種"] },
  { id: "honmoroko", name: "ホンモロコ", category: "魚類", image: "images/fish/honmoroko.jpg", tags: ["コイ科", "固有種"] },
  // ... 80〜100種
];
```

tags には科名と、固有種の場合は `"固有種"`、外来種の場合は `"外来種"` を付与。

- [ ] **Step 3: コミット**

```bash
git add fish_data.js
git commit -m "feat: add fish_data.js with Lake Biwa freshwater fish data (~90 species)"
```

---

### Task 2: download_fish.py — 画像ダウンロードスクリプト作成

**Files:**
- Create: `download_fish.py`
- Reference: `download_birds.py`（既存パターンをベースにする）

- [ ] **Step 1: download_fish.py を作成**

`download_birds.py` をベースに、以下を変更：
- `IMAGES_DIR` を `"images/fish"` に
- `CREDITS_FILE` を `"fish_credits.json"` に
- `BIRDS_TO_ADD` を `FISH_TO_ADD` に変更し、fish_data.js の全種を `(romaji_id, 日本語名, Wikipedia英語版記事タイトル)` のタプルで列挙
- User-Agent を `"FishMemoryApp/1.0"` に
- リサイズは長辺500pxのまま（既存と同じ）
- 画像の検索で横向き全身写真を優先するため、Wikipedia記事のメイン画像（Taxobox画像）を使用

```python
"""
Wikipedia + Wikimedia Commonsから魚の画像をダウンロードするスクリプト
- Wikipedia英語版の記事メイン画像を取得（pageimages API）
- 長辺500pxにリサイズ
- CommonsからライセンスInfo取得
- クレジット情報をJSONに保存
"""

import requests
import json
import os
import time
import re
from PIL import Image
from io import BytesIO
from urllib.parse import unquote

IMAGES_DIR = "images/fish"
CREDITS_FILE = "fish_credits.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "FishMemoryApp/1.0 (educational project) Python-requests/2.32",
})

FISH_TO_ADD = [
    # 固有種 - サケ科
    ("biwamasu", "ビワマス", "Biwa trout"),
    # 固有種 - コイ科
    ("nigorobuna", "ニゴロブナ", "Carassius buergeri grandoculis"),
    ("gengoroubuna", "ゲンゴロウブナ", "Carassius cuvieri"),
    ("honmoroko", "ホンモロコ", "Gnathopogon caerulescens"),
    # ... fish_data.js の全種を列挙
    # （実際のスクリプトでは80〜100種すべてのタプルを記載）
]
```

残りのロジック（ダウンロード・リサイズ・クレジット取得）は `download_birds.py` と同一。

- [ ] **Step 2: コミット**

```bash
git add download_fish.py
git commit -m "feat: add download_fish.py for Lake Biwa fish images"
```

---

### Task 3: 画像ダウンロード実行

**Files:**
- Create: `images/fish/*.jpg`（80〜100枚）
- Create: `fish_credits.json`

- [ ] **Step 1: images/fish ディレクトリ作成**

```bash
mkdir -p images/fish
```

- [ ] **Step 2: ダウンロードスクリプト実行**

```bash
python download_fish.py
```

実行後、`images/fish/` に画像ファイル、`fish_credits.json` にクレジットJSONが生成される。

- [ ] **Step 3: ダウンロード結果を確認**

```bash
ls images/fish/ | wc -l
```

80〜100枚程度あることを確認。不足があれば手動でURLを指定して再取得。

- [ ] **Step 4: fish_credits.js を生成**

`fish_credits.json` から `fish_credits.js` を生成。形式は `credits.js`（BIRD_CREDITS）と同じ：

```js
const FISH_CREDITS = {
  "biwamasu": { artist: "...", license: "CC BY-SA 4.0" },
  "nigorobuna": { artist: "...", license: "CC BY-SA 3.0" },
  // ...
};
```

既存の `fix_credits_js.py` を参考にスクリプトで生成するか、手動で変換。

- [ ] **Step 5: コミット**

```bash
git add images/fish/ fish_credits.json fish_credits.js
git commit -m "feat: add Lake Biwa fish images and credits (~90 species)"
```

---

### Task 4: index.html — モードボタンとscript読み込み追加

**Files:**
- Modify: `index.html`

- [ ] **Step 1: モード切替ボタンに「さかなおぼえ」追加**

`index.html` の `.mode-switcher` 内（line 40、しょくそう覚えボタンの後）に追加：

```html
<button class="mode-btn" id="mode-fish" data-mode="fish">さかなおぼえ</button>
```

- [ ] **Step 2: script読み込み追加**

`index.html` の `</body>` 前のscriptタグ群（line 265-274付近）に、`shokusou_data.js` の後に追加：

```html
<script src="fish_data.js"></script>
<script src="fish_credits.js"></script>
```

- [ ] **Step 3: コミット**

```bash
git add index.html
git commit -m "feat: add sakana-oboe mode button and script tags to index.html"
```

---

### Task 5: app.js — fish モードの分岐追加

**Files:**
- Modify: `app.js`

- [ ] **Step 1: getActiveData() に fish 分岐追加**

`app.js` line 20-28 の `getActiveData()` に追加：

```js
function getActiveData() {
  if (currentMode === 'tree') return TREE_DATA;
  if (currentMode === 'nakigoe') return NAKIGOE_DATA;
  if (currentMode === 'shokusou') {
    return currentSubMode === 'plant' ? PLANT_DATA : INSECT_DATA;
  }
  if (currentMode === 'fish') return FISH_DATA;
  return BIRD_DATA;
}
```

- [ ] **Step 2: getModeLabels() に fish 分岐追加**

`app.js` の `getModeLabels()` 関数（line 162付近）に追加。`shokusou` ブロックの後、`return` の前に：

```js
if (mode === 'fish') {
  return {
    title: 'さかなおぼえ',
    subtitle: '琵琶湖淡水魚フラッシュカード',
    resultWrongTitle: '間違えた項目',
    catalogTitle: '魚一覧'
  };
}
```

- [ ] **Step 3: セッション履歴キーに fish 追加**

`app.js` line 17-18 の `lastSessionIdsByMode` と `recentSessionHistoryByMode` に `fish` キー追加：

```js
var lastSessionIdsByMode = { bird: [], tree: [], fish: [], shokusou_insect: [], shokusou_plant: [] };
var recentSessionHistoryByMode = { bird: [], tree: [], fish: [], shokusou_insect: [], shokusou_plant: [] };
```

- [ ] **Step 4: クレジット画面で fish モードの表示対応**

app.js 内のクレジット表示ロジックを確認し、`FISH_CREDITS` を参照するよう対応が必要なら追加。既存コードで `credits.js` の読み込みパターンを確認して同様に統合する。

具体的には、クレジット表示関数で currentMode に応じて `BIRD_CREDITS`/`TREE_CREDITS`/`NAKIGOE_CREDITS`/`FISH_CREDITS` を切り替える処理を確認・追加する。クレジットイントロテキストは「魚の写真はすべてWikimedia Commonsのフリーライセンス画像を使用しています。」に。

- [ ] **Step 5: コミット**

```bash
git add app.js
git commit -m "feat: add fish mode logic to app.js (getActiveData, getModeLabels, session keys, credits)"
```

---

### Task 6: sw.js — キャッシュ対象にfish関連ファイル追加

**Files:**
- Modify: `sw.js`

- [ ] **Step 1: CACHE_NAME のバージョンを上げる**

```js
const CACHE_NAME = "torioboe-v9";
```

- [ ] **Step 2: ASSETS 配列に fish_data.js と fish_credits.js を追加**

```js
const ASSETS = [
  // ... 既存のもの
  "./fish_data.js",
  "./fish_credits.js",
];
```

- [ ] **Step 3: FISH_IMAGES 配列を追加**

`BIRD_IMAGES` 配列の後に、ダウンロードされた全魚画像のパスを列挙：

```js
const FISH_IMAGES = [
  "./images/fish/biwamasu.jpg",
  "./images/fish/nigorobuna.jpg",
  "./images/fish/gengoroubuna.jpg",
  "./images/fish/honmoroko.jpg",
  // ... 全種のパス
];
```

- [ ] **Step 4: ALL_ASSETS に FISH_IMAGES を統合**

```js
const ALL_ASSETS = [...ASSETS, ...BIRD_IMAGES, ...FISH_IMAGES];
```

- [ ] **Step 5: コミット**

```bash
git add sw.js
git commit -m "feat: add fish assets to service worker cache (sw.js v9)"
```

---

### Task 7: 動作確認

- [ ] **Step 1: ローカルサーバーで起動確認**

```bash
cd C:/Users/goren/Desktop/Claude_Code/basyo_hou_app
python -m http.server 8000
```

ブラウザで `http://localhost:8000` を開く。

- [ ] **Step 2: 確認項目**

1. ホーム画面に「さかなおぼえ」モードボタンが表示される
2. 「さかなおぼえ」をタップするとタイトルが「さかなおぼえ」「琵琶湖淡水魚フラッシュカード」に変わる
3. 種類数・習得済み・挑戦回数が正しく表示される
4. 「開始」で暗記画面に魚画像が表示される
5. 「回答開始」→テスト画面でカタカナ入力→答え合わせが機能する
6. 結果画面のスコア・間違えた項目が正しく表示される
7. 種類一覧で魚リストが表示される
8. 設定画面のクレジットに魚の写真クレジットが表示される

- [ ] **Step 3: 最終コミット（必要な修正があれば）**

```bash
git add -A
git commit -m "fix: adjustments after sakana-oboe integration testing"
```
