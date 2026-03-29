# とり覚え（鳥記憶アプリ）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 鳥の写真を見て名前を覚える記憶術PWA Webアプリを、身近な鳥20種で構築する

**Architecture:** フレームワークなしのHTML+CSS+JS構成。SPA的に画面をJSで切り替える。進捗データはIndexedDB、設定はlocalStorage。PWA対応でiPhoneホーム画面追加可能。

**Tech Stack:** HTML5, CSS3, Vanilla JavaScript, IndexedDB, Service Worker

---

## File Structure

```
basyo_hou_app/
├── index.html          # メインHTML（全画面の骨格、SPA）
├── style.css           # 全スタイル（ダークモード固定）
├── app.js              # 画面遷移・UI制御・メインエントリ
├── db.js               # IndexedDB操作（進捗の読み書き）
├── quiz.js             # 出題ロジック・回答判定・採点
├── settings.js         # 設定の読み書き（localStorage）
├── data.js             # 鳥データ定義（20種のJSON配列）
├── manifest.json       # PWAマニフェスト
├── sw.js               # Service Worker（オフライン対応）
├── icon-192.png        # PWAアイコン
├── icon-512.png        # PWAアイコン（大）
├── images/             # 鳥写真（Wikimedia Commonsから取得）
│   ├── suzume.jpg
│   ├── hashibutogarasu.jpg
│   ├── hashibosogarasu.jpg
│   ├── kijibato.jpg
│   ├── hiyodori.jpg
│   ├── mejiro.jpg
│   ├── shijuukara.jpg
│   ├── tsubame.jpg
│   ├── mukudori.jpg
│   ├── hakusekirei.jpg
│   ├── karugamo.jpg
│   ├── kosagi.jpg
│   ├── aosagi.jpg
│   ├── tobi.jpg
│   ├── mozu.jpg
│   ├── uguisu.jpg
│   ├── kawasemi.jpg
│   ├── joubitaki.jpg
│   ├── enaga.jpg
│   └── kawarahiwa.jpg
└── docs/
```

各ファイルの責務:
- `data.js`: 鳥データの配列をexport。他ファイルから参照される唯一のデータソース
- `db.js`: IndexedDBの初期化、進捗レコードのCRUD。他ファイルはdb.jsの関数経由でのみDBにアクセス
- `settings.js`: localStorageの読み書き。デフォルト値の管理
- `quiz.js`: 出題候補の選定、ランダム抽出、回答判定（カタカナ正規化）、mastered判定
- `app.js`: 画面の表示切り替え、UIイベント、各モジュールの組み合わせ
- `style.css`: ダークモード固定、レスポンシブ、全画面のスタイル
- `index.html`: 全画面のHTML骨格（非表示で全画面を持ち、JSで表示切り替え）

---

### Task 1: プロジェクト初期化とgit

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: gitリポジトリを初期化**

Run:
```bash
cd C:/Users/goren/Desktop/Claude_Code/basyo_hou_app
git init
```

- [ ] **Step 2: .gitignoreを作成**

```
.superpowers/
node_modules/
.DS_Store
Thumbs.db
```

- [ ] **Step 3: 初期コミット**

```bash
git add .gitignore docs/ shiryou/
git commit -m "init: プロジェクト初期化、設計仕様書と参考画像を追加"
```

---

### Task 2: 鳥データ定義（data.js）

**Files:**
- Create: `data.js`

- [ ] **Step 1: data.jsを作成**

20種の鳥データを定義する。各鳥は`id`, `name`, `category`, `image`, `tags`を持つ。

```javascript
// data.js — 鳥データ定義
const BIRD_DATA = [
  { id: "suzume", name: "スズメ", category: "鳥", image: "images/suzume.jpg", tags: [] },
  { id: "hashibutogarasu", name: "ハシブトガラス", category: "鳥", image: "images/hashibutogarasu.jpg", tags: [] },
  { id: "hashibosogarasu", name: "ハシボソガラス", category: "鳥", image: "images/hashibosogarasu.jpg", tags: [] },
  { id: "kijibato", name: "キジバト", category: "鳥", image: "images/kijibato.jpg", tags: [] },
  { id: "hiyodori", name: "ヒヨドリ", category: "鳥", image: "images/hiyodori.jpg", tags: [] },
  { id: "mejiro", name: "メジロ", category: "鳥", image: "images/mejiro.jpg", tags: [] },
  { id: "shijuukara", name: "シジュウカラ", category: "鳥", image: "images/shijuukara.jpg", tags: [] },
  { id: "tsubame", name: "ツバメ", category: "鳥", image: "images/tsubame.jpg", tags: [] },
  { id: "mukudori", name: "ムクドリ", category: "鳥", image: "images/mukudori.jpg", tags: [] },
  { id: "hakusekirei", name: "ハクセキレイ", category: "鳥", image: "images/hakusekirei.jpg", tags: [] },
  { id: "karugamo", name: "カルガモ", category: "鳥", image: "images/karugamo.jpg", tags: [] },
  { id: "kosagi", name: "コサギ", category: "鳥", image: "images/kosagi.jpg", tags: [] },
  { id: "aosagi", name: "アオサギ", category: "鳥", image: "images/aosagi.jpg", tags: [] },
  { id: "tobi", name: "トビ", category: "鳥", image: "images/tobi.jpg", tags: [] },
  { id: "mozu", name: "モズ", category: "鳥", image: "images/mozu.jpg", tags: [] },
  { id: "uguisu", name: "ウグイス", category: "鳥", image: "images/uguisu.jpg", tags: [] },
  { id: "kawasemi", name: "カワセミ", category: "鳥", image: "images/kawasemi.jpg", tags: [] },
  { id: "joubitaki", name: "ジョウビタキ", category: "鳥", image: "images/joubitaki.jpg", tags: [] },
  { id: "enaga", name: "エナガ", category: "鳥", image: "images/enaga.jpg", tags: [] },
  { id: "kawarahiwa", name: "カワラヒワ", category: "鳥", image: "images/kawarahiwa.jpg", tags: [] },
];
```

- [ ] **Step 2: コミット**

```bash
git add data.js
git commit -m "feat: 鳥20種のデータ定義を追加"
```

---

### Task 3: 設定モジュール（settings.js）

**Files:**
- Create: `settings.js`

- [ ] **Step 1: settings.jsを作成**

localStorageから設定を読み書きする。デフォルト値を持ち、未設定の項目はデフォルトで埋める。

```javascript
// settings.js — 設定の読み書き
const DEFAULT_SETTINGS = {
  questionCount: 10,
  displayMode: "grid",       // "grid" | "single"
  masteryThreshold: 3,
  includeMastered: false,
  prioritizeWrong: true,
};

function loadSettings() {
  try {
    const saved = JSON.parse(localStorage.getItem("torioboe_settings"));
    return { ...DEFAULT_SETTINGS, ...saved };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

function saveSettings(settings) {
  localStorage.setItem("torioboe_settings", JSON.stringify(settings));
}
```

- [ ] **Step 2: コミット**

```bash
git add settings.js
git commit -m "feat: 設定の読み書きモジュールを追加"
```

---

### Task 4: IndexedDBモジュール（db.js）

**Files:**
- Create: `db.js`

- [ ] **Step 1: db.jsを作成**

IndexedDBを使い、進捗データのCRUDを行う。DBを開く関数、進捗を取得する関数、進捗を保存する関数、全進捗を取得する関数、全削除する関数、エクスポート/インポート関数を提供する。

```javascript
// db.js — IndexedDB操作
const DB_NAME = "torioboe";
const DB_VERSION = 1;
const STORE_NAME = "progress";

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror = (e) => reject(e.target.error);
  });
}

async function getProgress(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const req = store.get(id);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = (e) => reject(e.target.error);
  });
}

async function saveProgress(record) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    store.put(record);
    tx.oncomplete = () => resolve();
    tx.onerror = (e) => reject(e.target.error);
  });
}

async function getAllProgress() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const req = store.getAll();
    req.onsuccess = () => resolve(req.result);
    req.onerror = (e) => reject(e.target.error);
  });
}

async function clearAllProgress() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    store.clear();
    tx.oncomplete = () => resolve();
    tx.onerror = (e) => reject(e.target.error);
  });
}

async function exportData() {
  const progress = await getAllProgress();
  const settings = loadSettings();
  return JSON.stringify({ progress, settings }, null, 2);
}

async function importData(jsonString) {
  const data = JSON.parse(jsonString);
  if (data.progress) {
    for (const record of data.progress) {
      await saveProgress(record);
    }
  }
  if (data.settings) {
    saveSettings(data.settings);
  }
}
```

- [ ] **Step 2: コミット**

```bash
git add db.js
git commit -m "feat: IndexedDB進捗管理モジュールを追加"
```

---

### Task 5: 出題・採点ロジック（quiz.js）

**Files:**
- Create: `quiz.js`

- [ ] **Step 1: quiz.jsを作成**

出題候補の絞り込み、ランダム選択、回答判定、mastered判定を行う。

```javascript
// quiz.js — 出題ロジックと回答判定

// カタカナ正規化（半角→全角）
function normalizeKatakana(str) {
  return str.replace(/[\uFF65-\uFF9F]/g, (ch) => {
    const code = ch.charCodeAt(0);
    // 半角カタカナ→全角カタカナ変換
    const map = {
      0xFF66: "ヲ", 0xFF67: "ァ", 0xFF68: "ィ", 0xFF69: "ゥ", 0xFF6A: "ェ",
      0xFF6B: "ォ", 0xFF6C: "ャ", 0xFF6D: "ュ", 0xFF6E: "ョ", 0xFF6F: "ッ",
      0xFF70: "ー", 0xFF71: "ア", 0xFF72: "イ", 0xFF73: "ウ", 0xFF74: "エ",
      0xFF75: "オ", 0xFF76: "カ", 0xFF77: "キ", 0xFF78: "ク", 0xFF79: "ケ",
      0xFF7A: "コ", 0xFF7B: "サ", 0xFF7C: "シ", 0xFF7D: "ス", 0xFF7E: "セ",
      0xFF7F: "ソ", 0xFF80: "タ", 0xFF81: "チ", 0xFF82: "ツ", 0xFF83: "テ",
      0xFF84: "ト", 0xFF85: "ナ", 0xFF86: "ニ", 0xFF87: "ヌ", 0xFF88: "ネ",
      0xFF89: "ノ", 0xFF8A: "ハ", 0xFF8B: "ヒ", 0xFF8C: "フ", 0xFF8D: "ヘ",
      0xFF8E: "ホ", 0xFF8F: "マ", 0xFF90: "ミ", 0xFF91: "ム", 0xFF92: "メ",
      0xFF93: "モ", 0xFF94: "ヤ", 0xFF95: "ユ", 0xFF96: "ヨ", 0xFF97: "ラ",
      0xFF98: "リ", 0xFF99: "ル", 0xFF9A: "レ", 0xFF9B: "ロ", 0xFF9C: "ワ",
      0xFF9D: "ン", 0xFF9E: "゛", 0xFF9F: "゜", 0xFF65: "・",
    };
    return map[code] || ch;
  }).trim();
}

// 回答を判定する（カタカナ完全一致）
function checkAnswer(input, correctName) {
  const normalizedInput = normalizeKatakana(input);
  const normalizedCorrect = normalizeKatakana(correctName);
  return normalizedInput === normalizedCorrect;
}

// 出題候補を選定する
async function selectQuestions(birdData, settings) {
  const allProgress = await getAllProgress();
  const progressMap = {};
  for (const p of allProgress) {
    progressMap[p.id] = p;
  }

  // 候補を絞る
  let candidates = birdData.filter((bird) => {
    if (!settings.includeMastered) {
      const prog = progressMap[bird.id];
      if (prog && prog.mastered) return false;
    }
    return true;
  });

  // 間違えた鳥を優先
  if (settings.prioritizeWrong) {
    candidates.sort((a, b) => {
      const pa = progressMap[a.id];
      const pb = progressMap[b.id];
      const rateA = pa && pa.totalAttempts > 0
        ? pa.totalCorrect / pa.totalAttempts : 1;
      const rateB = pb && pb.totalAttempts > 0
        ? pb.totalCorrect / pb.totalAttempts : 1;
      return rateA - rateB; // 正答率が低い順
    });
  }

  // 出題数分を選択
  const count = Math.min(settings.questionCount, candidates.length);

  if (settings.prioritizeWrong && candidates.length > count) {
    // 正答率が低い方から優先的に取り、残りからランダムに埋める
    const priorityCount = Math.ceil(count * 0.6);
    const priority = candidates.slice(0, priorityCount);
    const rest = candidates.slice(priorityCount);
    shuffleArray(rest);
    const selected = [...priority, ...rest.slice(0, count - priorityCount)];
    shuffleArray(selected);
    return selected;
  }

  shuffleArray(candidates);
  return candidates.slice(0, count);
}

// 回答後に進捗を更新する
async function updateProgress(birdId, isCorrect, masteryThreshold) {
  let prog = await getProgress(birdId);
  if (!prog) {
    prog = {
      id: birdId,
      correctStreak: 0,
      totalCorrect: 0,
      totalAttempts: 0,
      mastered: false,
      lastAttempt: null,
    };
  }

  prog.totalAttempts += 1;
  prog.lastAttempt = new Date().toISOString();

  if (isCorrect) {
    prog.correctStreak += 1;
    prog.totalCorrect += 1;
    if (prog.correctStreak >= masteryThreshold) {
      prog.mastered = true;
    }
  } else {
    prog.correctStreak = 0;
  }

  await saveProgress(prog);
  return prog;
}

// Fisher-Yatesシャッフル
function shuffleArray(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
```

- [ ] **Step 2: コミット**

```bash
git add quiz.js
git commit -m "feat: 出題ロジックと回答判定モジュールを追加"
```

---

### Task 6: HTMLとCSS（index.html, style.css）

**Files:**
- Create: `index.html`
- Create: `style.css`

- [ ] **Step 1: index.htmlを作成**

全画面の骨格を含むSPA構造。画面ごとに`<section>`を持ち、`display:none`で非表示にしてJSで切り替える。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="theme-color" content="#1a1a2e">
  <title>とり覚え</title>
  <link rel="stylesheet" href="style.css">
  <link rel="manifest" href="manifest.json">
  <link rel="apple-touch-icon" href="icon-192.png">
</head>
<body>

  <!-- ホーム画面 -->
  <section id="screen-home" class="screen active">
    <div class="app-header">
      <div class="app-icon">🐦</div>
      <h1>とり覚え</h1>
      <p class="app-subtitle">野鳥記憶トレーニング</p>
    </div>
    <div class="home-buttons">
      <button id="btn-memorize" class="home-btn memorize-btn">
        <span class="btn-icon">📖</span>
        <span class="btn-label">記憶モード</span>
        <span class="btn-desc">写真と名前を覚える</span>
      </button>
      <button id="btn-test" class="home-btn test-btn">
        <span class="btn-icon">✏️</span>
        <span class="btn-label">テストモード</span>
        <span class="btn-desc">名前を入力して回答</span>
      </button>
    </div>
    <div id="home-stats" class="stats-box">
      <div class="stats-row">
        <span>登録: <b id="stat-total">0</b>種</span>
        <span>覚えた: <b id="stat-mastered">0</b>種</span>
        <span>正答率: <b id="stat-rate">0</b>%</span>
      </div>
      <div class="progress-bar">
        <div id="stat-bar" class="progress-fill" style="width:0%"></div>
      </div>
    </div>
    <button id="btn-settings" class="link-btn">⚙️ 設定</button>
  </section>

  <!-- 記憶モード -->
  <section id="screen-memorize" class="screen">
    <div class="screen-header">
      <button class="back-btn" data-target="home">← 戻る</button>
      <h2>記憶モード</h2>
      <button id="btn-start-test" class="action-btn purple">想起 →</button>
    </div>
    <div id="memorize-grid" class="bird-grid"></div>
    <!-- 拡大表示オーバーレイ -->
    <div id="memorize-overlay" class="overlay hidden">
      <div class="overlay-content">
        <img id="overlay-img" src="" alt="">
        <p id="overlay-name" class="overlay-name"></p>
        <button id="overlay-close" class="overlay-close-btn">✕</button>
      </div>
    </div>
  </section>

  <!-- テストモード（グリッド） -->
  <section id="screen-test-grid" class="screen">
    <div class="screen-header">
      <button class="back-btn" data-target="home">← 戻る</button>
      <h2>テスト（グリッド）</h2>
    </div>
    <div id="test-grid" class="bird-grid"></div>
    <button id="btn-submit-grid" class="action-btn green full-width">提出する</button>
  </section>

  <!-- テストモード（1枚ずつ） -->
  <section id="screen-test-single" class="screen">
    <div class="screen-header">
      <button class="back-btn" data-target="home">← 戻る</button>
      <h2>テスト</h2>
      <span id="single-progress" class="progress-text">1/10</span>
    </div>
    <div class="single-card">
      <img id="single-img" src="" alt="" class="single-img">
      <input id="single-input" type="text" class="answer-input" placeholder="名前を入力（カタカナ）">
      <div id="single-feedback" class="feedback hidden"></div>
    </div>
    <div class="single-nav">
      <button id="btn-prev" class="nav-btn">← 前</button>
      <button id="btn-answer" class="action-btn purple">回答</button>
      <button id="btn-next" class="nav-btn">次 →</button>
    </div>
  </section>

  <!-- 採点結果 -->
  <section id="screen-result" class="screen">
    <div class="screen-header">
      <h2>結果</h2>
    </div>
    <div class="result-summary">
      <p class="result-score"><span id="result-correct">0</span> / <span id="result-total">0</span></p>
      <p class="result-rate">正答率: <span id="result-rate">0</span>%</p>
    </div>
    <div id="result-wrong" class="result-wrong-list"></div>
    <div class="result-actions">
      <button id="btn-retry" class="action-btn purple">もう一度</button>
      <button id="btn-result-home" class="action-btn gray">ホームへ</button>
    </div>
  </section>

  <!-- 設定 -->
  <section id="screen-settings" class="screen">
    <div class="screen-header">
      <button class="back-btn" data-target="home">← 戻る</button>
      <h2>設定</h2>
    </div>
    <div class="settings-list">
      <div class="setting-item">
        <label for="set-count">出題数</label>
        <input id="set-count" type="number" min="1" max="999" class="setting-input">
      </div>
      <div class="setting-item">
        <label>表示形式</label>
        <div class="toggle-group">
          <button class="toggle-btn" data-mode="grid" id="set-mode-grid">グリッド</button>
          <button class="toggle-btn" data-mode="single" id="set-mode-single">1枚ずつ</button>
        </div>
      </div>
      <div class="setting-item">
        <label>覚えた判定（連続正解回数）</label>
        <div class="toggle-group">
          <button class="toggle-btn" data-threshold="1">1</button>
          <button class="toggle-btn" data-threshold="2">2</button>
          <button class="toggle-btn" data-threshold="3">3</button>
          <button class="toggle-btn" data-threshold="5">5</button>
        </div>
      </div>
      <div class="setting-item">
        <label for="set-include-mastered">覚えた鳥も出題する</label>
        <input id="set-include-mastered" type="checkbox" class="toggle-check">
      </div>
      <div class="setting-item">
        <label for="set-prioritize-wrong">間違えた鳥を優先出題</label>
        <input id="set-prioritize-wrong" type="checkbox" class="toggle-check">
      </div>
      <div class="setting-divider"></div>
      <div class="setting-item">
        <label>データ管理</label>
        <div class="data-buttons">
          <button id="btn-export" class="data-btn">📤 エクスポート</button>
          <button id="btn-import" class="data-btn">📥 インポート</button>
          <input id="import-file" type="file" accept=".json" class="hidden">
        </div>
      </div>
      <div class="setting-divider"></div>
      <button id="btn-reset" class="danger-btn">🗑️ 全データリセット</button>
    </div>
  </section>

  <script src="data.js"></script>
  <script src="settings.js"></script>
  <script src="db.js"></script>
  <script src="quiz.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: style.cssを作成**

ダークモード固定、iPhone縦画面最適化のスタイル。

```css
/* style.css — ダークモード固定、iPhone縦画面最適化 */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", sans-serif;
  background: #1a1a2e;
  color: #e0e0e0;
  min-height: 100vh;
  min-height: 100dvh;
  overflow-x: hidden;
  -webkit-tap-highlight-color: transparent;
}

/* 画面切り替え */
.screen {
  display: none;
  padding: 16px;
  padding-top: env(safe-area-inset-top, 16px);
  padding-bottom: calc(env(safe-area-inset-bottom, 16px) + 16px);
  min-height: 100vh;
  min-height: 100dvh;
}
.screen.active { display: block; }

/* ヘッダー */
.screen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 8px;
}
.screen-header h2 {
  font-size: 18px;
  color: #fff;
  flex: 1;
  text-align: center;
}

/* ホーム画面 */
.app-header {
  text-align: center;
  padding: 32px 0 24px;
}
.app-icon { font-size: 48px; margin-bottom: 8px; }
.app-header h1 { font-size: 24px; color: #fff; }
.app-subtitle { font-size: 13px; color: #888; margin-top: 4px; }

.home-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}
.home-btn {
  background: #2d2d44;
  border: 2px solid #444;
  border-radius: 14px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  color: #fff;
  font-size: 16px;
}
.home-btn:active { transform: scale(0.98); }
.memorize-btn { border-color: #6c3eb6; }
.test-btn { border-color: #22c55e; }
.btn-icon { font-size: 20px; margin-right: 6px; }
.btn-label { font-weight: bold; }
.btn-desc { display: block; font-size: 12px; color: #aaa; margin-top: 4px; }

/* 統計 */
.stats-box {
  background: #2d2d44;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 16px;
}
.stats-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}
.stats-row b { color: #fff; }
.progress-bar {
  background: #333;
  border-radius: 4px;
  height: 6px;
  overflow: hidden;
}
.progress-fill {
  background: linear-gradient(90deg, #4ade80, #22c55e);
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

/* 鳥グリッド */
.bird-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}
.bird-card {
  text-align: center;
}
.bird-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 10px;
  background: #2d2d44;
}
.bird-card .bird-name {
  font-size: 12px;
  margin-top: 4px;
  color: #e0e0e0;
  word-break: keep-all;
}
.bird-card .answer-input {
  width: 100%;
  margin-top: 4px;
}

/* 入力欄 */
.answer-input {
  background: #2d2d44;
  border: 1px solid #555;
  border-radius: 8px;
  padding: 8px;
  color: #fff;
  font-size: 14px;
  width: 100%;
  text-align: center;
}
.answer-input:focus {
  outline: none;
  border-color: #6c3eb6;
}
.answer-input.correct { border-color: #4ade80; color: #4ade80; }
.answer-input.wrong { border-color: #f87171; color: #f87171; }

/* 1枚ずつモード */
.single-card {
  text-align: center;
  padding: 16px 0;
}
.single-img {
  width: 80%;
  max-width: 300px;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 16px;
  background: #2d2d44;
  margin-bottom: 16px;
}
.single-card .answer-input {
  max-width: 260px;
  margin: 0 auto;
}
.single-nav {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}
.progress-text { font-size: 14px; color: #888; }

/* フィードバック */
.feedback {
  margin-top: 12px;
  font-size: 16px;
  font-weight: bold;
  min-height: 24px;
}
.feedback.correct { color: #4ade80; }
.feedback.wrong { color: #f87171; }

/* ボタン */
.action-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 20px;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  color: #fff;
}
.action-btn:active { opacity: 0.85; }
.action-btn.purple { background: #6c3eb6; }
.action-btn.green { background: #22c55e; }
.action-btn.gray { background: #444; }
.full-width { display: block; width: 100%; margin-top: 12px; }

.nav-btn {
  background: #333;
  border: none;
  color: #fff;
  padding: 8px 18px;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
}

.back-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 14px;
  cursor: pointer;
}
.link-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 13px;
  cursor: pointer;
  display: block;
  text-align: center;
}

/* 結果画面 */
.result-summary {
  text-align: center;
  padding: 24px 0;
}
.result-score {
  font-size: 48px;
  font-weight: bold;
  color: #fff;
}
.result-rate {
  font-size: 18px;
  color: #aaa;
  margin-top: 8px;
}
.result-wrong-list {
  margin: 16px 0;
}
.result-wrong-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #2d2d44;
  border-radius: 10px;
  padding: 10px;
  margin-bottom: 8px;
}
.result-wrong-item img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 8px;
}
.result-wrong-item .wrong-answer { color: #f87171; font-size: 13px; }
.result-wrong-item .correct-answer { color: #4ade80; font-size: 13px; }
.result-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

/* オーバーレイ */
.overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.overlay.hidden { display: none; }
.overlay-content { text-align: center; }
.overlay-content img {
  width: 80vw;
  max-width: 350px;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 16px;
}
.overlay-name {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  margin-top: 12px;
}
.overlay-close-btn {
  position: absolute;
  top: 40px; right: 20px;
  background: none;
  border: none;
  color: #fff;
  font-size: 28px;
  cursor: pointer;
}

/* 設定 */
.settings-list { padding: 8px 0; }
.setting-item {
  margin-bottom: 18px;
}
.setting-item label {
  display: block;
  font-size: 13px;
  color: #888;
  margin-bottom: 6px;
}
.setting-input {
  background: #2d2d44;
  border: 1px solid #555;
  border-radius: 8px;
  padding: 8px 12px;
  color: #fff;
  font-size: 16px;
  width: 80px;
  text-align: center;
}
.toggle-group {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.toggle-btn {
  background: #333;
  border: none;
  color: #aaa;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
.toggle-btn.active {
  background: #6c3eb6;
  color: #fff;
}
.toggle-check {
  width: 20px;
  height: 20px;
  accent-color: #6c3eb6;
}
.setting-divider {
  border-top: 1px solid #333;
  margin: 16px 0;
}
.data-buttons {
  display: flex;
  gap: 8px;
}
.data-btn {
  background: #2d2d44;
  border: none;
  color: #aaa;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}
.danger-btn {
  background: #7f1d1d;
  border: none;
  color: #f87171;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  width: 100%;
}

.hidden { display: none !important; }
```

- [ ] **Step 3: コミット**

```bash
git add index.html style.css
git commit -m "feat: HTMLとCSSの画面構造を追加"
```

---

### Task 7: メインアプリロジック（app.js）

**Files:**
- Create: `app.js`

- [ ] **Step 1: app.jsを作成**

画面遷移、各モードのUI構築、イベントハンドリング、設定画面の制御を行うメインファイル。

```javascript
// app.js — メインアプリロジック

// 画面遷移
function showScreen(id) {
  document.querySelectorAll(".screen").forEach((s) => s.classList.remove("active"));
  document.getElementById("screen-" + id).classList.add("active");
}

// ホーム画面の統計を更新
async function updateHomeStats() {
  const total = BIRD_DATA.length;
  const allProgress = await getAllProgress();
  const mastered = allProgress.filter((p) => p.mastered).length;
  const totalAttempts = allProgress.reduce((s, p) => s + p.totalAttempts, 0);
  const totalCorrect = allProgress.reduce((s, p) => s + p.totalCorrect, 0);
  const rate = totalAttempts > 0 ? Math.round((totalCorrect / totalAttempts) * 100) : 0;

  document.getElementById("stat-total").textContent = total;
  document.getElementById("stat-mastered").textContent = mastered;
  document.getElementById("stat-rate").textContent = rate;
  document.getElementById("stat-bar").style.width = (total > 0 ? (mastered / total) * 100 : 0) + "%";
}

// ==================== 記憶モード ====================

function renderMemorizeGrid() {
  const grid = document.getElementById("memorize-grid");
  grid.innerHTML = "";
  for (const bird of BIRD_DATA) {
    const card = document.createElement("div");
    card.className = "bird-card";
    card.innerHTML = `
      <img src="${bird.image}" alt="${bird.name}" loading="lazy">
      <div class="bird-name">${bird.name}</div>
    `;
    card.addEventListener("click", () => {
      document.getElementById("overlay-img").src = bird.image;
      document.getElementById("overlay-name").textContent = bird.name;
      document.getElementById("memorize-overlay").classList.remove("hidden");
    });
    grid.appendChild(card);
  }
}

// ==================== テストモード共通 ====================

let currentQuestions = [];
let currentIndex = 0;
let testAnswers = []; // { bird, userAnswer, isCorrect }

async function startTest() {
  const settings = loadSettings();
  currentQuestions = await selectQuestions(BIRD_DATA, settings);
  currentIndex = 0;
  testAnswers = currentQuestions.map((bird) => ({
    bird,
    userAnswer: "",
    isCorrect: null,
  }));

  if (currentQuestions.length === 0) {
    alert("出題できる鳥がありません。設定を確認してください。");
    return;
  }

  if (settings.displayMode === "grid") {
    renderTestGrid();
    showScreen("test-grid");
  } else {
    renderTestSingle();
    showScreen("test-single");
  }
}

// ==================== グリッドテスト ====================

function renderTestGrid() {
  const grid = document.getElementById("test-grid");
  grid.innerHTML = "";
  for (let i = 0; i < currentQuestions.length; i++) {
    const bird = currentQuestions[i];
    const card = document.createElement("div");
    card.className = "bird-card";
    card.innerHTML = `
      <img src="${bird.image}" alt="?" loading="lazy">
      <input type="text" class="answer-input" data-index="${i}"
             placeholder="名前" autocomplete="off">
    `;
    grid.appendChild(card);
  }
}

async function submitGridTest() {
  const inputs = document.querySelectorAll("#test-grid .answer-input");
  const settings = loadSettings();
  let correctCount = 0;

  for (const input of inputs) {
    const idx = parseInt(input.dataset.index);
    const answer = input.value;
    const bird = currentQuestions[idx];
    const isCorrect = checkAnswer(answer, bird.name);

    testAnswers[idx].userAnswer = answer;
    testAnswers[idx].isCorrect = isCorrect;

    input.classList.add(isCorrect ? "correct" : "wrong");
    input.disabled = true;

    if (!isCorrect) {
      const nameDiv = document.createElement("div");
      nameDiv.className = "bird-name";
      nameDiv.style.color = "#4ade80";
      nameDiv.textContent = bird.name;
      input.parentElement.appendChild(nameDiv);
    }

    if (isCorrect) correctCount++;
    await updateProgress(bird.id, isCorrect, settings.masteryThreshold);
  }

  // 2秒後に結果画面へ
  setTimeout(() => showResult(correctCount, currentQuestions.length), 2000);
}

// ==================== 1枚ずつテスト ====================

function renderTestSingle() {
  updateSingleDisplay();
}

function updateSingleDisplay() {
  const bird = currentQuestions[currentIndex];
  document.getElementById("single-img").src = bird.image;
  document.getElementById("single-input").value = testAnswers[currentIndex].userAnswer || "";
  document.getElementById("single-input").disabled = testAnswers[currentIndex].isCorrect !== null;
  document.getElementById("single-progress").textContent =
    `${currentIndex + 1}/${currentQuestions.length}`;

  const feedback = document.getElementById("single-feedback");
  if (testAnswers[currentIndex].isCorrect === true) {
    feedback.textContent = "⭕ 正解！";
    feedback.className = "feedback correct";
  } else if (testAnswers[currentIndex].isCorrect === false) {
    feedback.textContent = `✕ 正解: ${bird.name}`;
    feedback.className = "feedback wrong";
  } else {
    feedback.textContent = "";
    feedback.className = "feedback hidden";
  }

  // 回答ボタンの状態
  document.getElementById("btn-answer").disabled = testAnswers[currentIndex].isCorrect !== null;
}

async function submitSingleAnswer() {
  const input = document.getElementById("single-input");
  const answer = input.value;
  const bird = currentQuestions[currentIndex];
  const settings = loadSettings();
  const isCorrect = checkAnswer(answer, bird.name);

  testAnswers[currentIndex].userAnswer = answer;
  testAnswers[currentIndex].isCorrect = isCorrect;

  await updateProgress(bird.id, isCorrect, settings.masteryThreshold);
  updateSingleDisplay();

  // 全問回答済みかチェック
  const allDone = testAnswers.every((a) => a.isCorrect !== null);
  if (allDone) {
    const correctCount = testAnswers.filter((a) => a.isCorrect).length;
    setTimeout(() => showResult(correctCount, currentQuestions.length), 1500);
  }
}

// ==================== 結果画面 ====================

function showResult(correct, total) {
  document.getElementById("result-correct").textContent = correct;
  document.getElementById("result-total").textContent = total;
  document.getElementById("result-rate").textContent =
    total > 0 ? Math.round((correct / total) * 100) : 0;

  const wrongList = document.getElementById("result-wrong");
  wrongList.innerHTML = "";
  for (const item of testAnswers) {
    if (!item.isCorrect) {
      const div = document.createElement("div");
      div.className = "result-wrong-item";
      div.innerHTML = `
        <img src="${item.bird.image}" alt="">
        <div>
          <div class="wrong-answer">あなたの回答: ${item.userAnswer || "（未回答）"}</div>
          <div class="correct-answer">正解: ${item.bird.name}</div>
        </div>
      `;
      wrongList.appendChild(div);
    }
  }

  showScreen("result");
}

// ==================== 設定画面 ====================

function renderSettings() {
  const s = loadSettings();
  document.getElementById("set-count").value = s.questionCount;
  document.getElementById("set-include-mastered").checked = s.includeMastered;
  document.getElementById("set-prioritize-wrong").checked = s.prioritizeWrong;

  // 表示形式
  document.querySelectorAll("[data-mode]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === s.displayMode);
  });

  // 覚えた判定
  document.querySelectorAll("[data-threshold]").forEach((btn) => {
    btn.classList.toggle("active", parseInt(btn.dataset.threshold) === s.masteryThreshold);
  });
}

function setupSettingsEvents() {
  // 出題数
  document.getElementById("set-count").addEventListener("change", (e) => {
    const s = loadSettings();
    s.questionCount = Math.max(1, parseInt(e.target.value) || 10);
    saveSettings(s);
  });

  // 表示形式
  document.querySelectorAll("[data-mode]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const s = loadSettings();
      s.displayMode = btn.dataset.mode;
      saveSettings(s);
      renderSettings();
    });
  });

  // 覚えた判定
  document.querySelectorAll("[data-threshold]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const s = loadSettings();
      s.masteryThreshold = parseInt(btn.dataset.threshold);
      saveSettings(s);
      renderSettings();
    });
  });

  // トグル
  document.getElementById("set-include-mastered").addEventListener("change", (e) => {
    const s = loadSettings();
    s.includeMastered = e.target.checked;
    saveSettings(s);
  });
  document.getElementById("set-prioritize-wrong").addEventListener("change", (e) => {
    const s = loadSettings();
    s.prioritizeWrong = e.target.checked;
    saveSettings(s);
  });

  // エクスポート
  document.getElementById("btn-export").addEventListener("click", async () => {
    const json = await exportData();
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "torioboe_backup.json";
    a.click();
    URL.revokeObjectURL(url);
  });

  // インポート
  document.getElementById("btn-import").addEventListener("click", () => {
    document.getElementById("import-file").click();
  });
  document.getElementById("import-file").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const text = await file.text();
    try {
      await importData(text);
      alert("インポートしました");
      renderSettings();
      updateHomeStats();
    } catch (err) {
      alert("インポートに失敗しました: " + err.message);
    }
    e.target.value = "";
  });

  // リセット
  document.getElementById("btn-reset").addEventListener("click", async () => {
    if (confirm("全ての進捗データをリセットしますか？この操作は元に戻せません。")) {
      await clearAllProgress();
      alert("リセットしました");
      updateHomeStats();
    }
  });
}

// ==================== イベント設定・初期化 ====================

function setupEvents() {
  // ホーム画面
  document.getElementById("btn-memorize").addEventListener("click", () => {
    renderMemorizeGrid();
    showScreen("memorize");
  });
  document.getElementById("btn-test").addEventListener("click", startTest);
  document.getElementById("btn-settings").addEventListener("click", () => {
    renderSettings();
    showScreen("settings");
  });

  // 戻るボタン
  document.querySelectorAll(".back-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      updateHomeStats();
      showScreen(btn.dataset.target);
    });
  });

  // 記憶モード
  document.getElementById("btn-start-test").addEventListener("click", startTest);
  document.getElementById("overlay-close").addEventListener("click", () => {
    document.getElementById("memorize-overlay").classList.add("hidden");
  });

  // グリッドテスト
  document.getElementById("btn-submit-grid").addEventListener("click", submitGridTest);

  // 1枚ずつテスト
  document.getElementById("btn-answer").addEventListener("click", submitSingleAnswer);
  document.getElementById("btn-prev").addEventListener("click", () => {
    if (currentIndex > 0) { currentIndex--; updateSingleDisplay(); }
  });
  document.getElementById("btn-next").addEventListener("click", () => {
    if (currentIndex < currentQuestions.length - 1) { currentIndex++; updateSingleDisplay(); }
  });

  // 結果画面
  document.getElementById("btn-retry").addEventListener("click", startTest);
  document.getElementById("btn-result-home").addEventListener("click", () => {
    updateHomeStats();
    showScreen("home");
  });

  // 設定
  setupSettingsEvents();
}

// 初期化
document.addEventListener("DOMContentLoaded", async () => {
  setupEvents();
  await updateHomeStats();
});
```

- [ ] **Step 2: コミット**

```bash
git add app.js
git commit -m "feat: メインアプリロジック（画面遷移・記憶・テスト・設定）を追加"
```

---

### Task 8: 鳥画像の取得

**Files:**
- Create: `images/` 内の20枚のjpg

- [ ] **Step 1: imagesフォルダを作成**

```bash
mkdir -p images
```

- [ ] **Step 2: Wikimedia Commonsから20種の写真をダウンロード**

各鳥について、Wikimedia Commonsからフリーライセンス（CC BY-SA等）の写真を1枚ずつ取得する。
長辺500px程度のjpgファイルとして保存する。

以下のファイル名で保存:
- `images/suzume.jpg` — スズメ
- `images/hashibutogarasu.jpg` — ハシブトガラス
- `images/hashibosogarasu.jpg` — ハシボソガラス
- `images/kijibato.jpg` — キジバト
- `images/hiyodori.jpg` — ヒヨドリ
- `images/mejiro.jpg` — メジロ
- `images/shijuukara.jpg` — シジュウカラ
- `images/tsubame.jpg` — ツバメ
- `images/mukudori.jpg` — ムクドリ
- `images/hakusekirei.jpg` — ハクセキレイ
- `images/karugamo.jpg` — カルガモ
- `images/kosagi.jpg` — コサギ
- `images/aosagi.jpg` — アオサギ
- `images/tobi.jpg` — トビ
- `images/mozu.jpg` — モズ
- `images/uguisu.jpg` — ウグイス
- `images/kawasemi.jpg` — カワセミ
- `images/joubitaki.jpg` — ジョウビタキ
- `images/enaga.jpg` — エナガ
- `images/kawarahiwa.jpg` — カワラヒワ

取得方法: Wikimedia Commons APIまたはWebで各鳥の学名・英名で検索し、適切なライセンスの写真をダウンロード。curlまたはWebFetchで取得。

- [ ] **Step 3: コミット**

```bash
git add images/
git commit -m "feat: 鳥20種の写真をWikimedia Commonsから追加"
```

---

### Task 9: PWA設定（manifest.json, sw.js, アイコン）

**Files:**
- Create: `manifest.json`
- Create: `sw.js`
- Create: `icon-192.png`
- Create: `icon-512.png`

- [ ] **Step 1: manifest.jsonを作成**

```json
{
  "name": "とり覚え",
  "short_name": "とり覚え",
  "description": "野鳥記憶トレーニング",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#1a1a2e",
  "theme_color": "#1a1a2e",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

- [ ] **Step 2: sw.jsを作成**

```javascript
// sw.js — Service Worker（オフライン対応）
const CACHE_NAME = "torioboe-v1";
const ASSETS = [
  "./index.html",
  "./style.css",
  "./app.js",
  "./data.js",
  "./db.js",
  "./quiz.js",
  "./settings.js",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
];

// 鳥画像もキャッシュ対象に追加
const BIRD_IMAGES = [
  "./images/suzume.jpg",
  "./images/hashibutogarasu.jpg",
  "./images/hashibosogarasu.jpg",
  "./images/kijibato.jpg",
  "./images/hiyodori.jpg",
  "./images/mejiro.jpg",
  "./images/shijuukara.jpg",
  "./images/tsubame.jpg",
  "./images/mukudori.jpg",
  "./images/hakusekirei.jpg",
  "./images/karugamo.jpg",
  "./images/kosagi.jpg",
  "./images/aosagi.jpg",
  "./images/tobi.jpg",
  "./images/mozu.jpg",
  "./images/uguisu.jpg",
  "./images/kawasemi.jpg",
  "./images/joubitaki.jpg",
  "./images/enaga.jpg",
  "./images/kawarahiwa.jpg",
];

const ALL_ASSETS = [...ASSETS, ...BIRD_IMAGES];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ALL_ASSETS))
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
```

- [ ] **Step 3: index.htmlにService Worker登録コードを追加**

`app.js`の初期化部分（DOMContentLoadedイベント内）の先頭に追加:

```javascript
// Service Worker登録
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js");
}
```

- [ ] **Step 4: アイコンを作成**

PWA用のアイコン画像を192x192と512x512のPNGで作成する。鳥のシンプルなアイコン。
Canvas APIやHTMLでシンプルなアイコンを生成してPNGとして保存する。

- [ ] **Step 5: コミット**

```bash
git add manifest.json sw.js icon-192.png icon-512.png app.js
git commit -m "feat: PWA対応（manifest, service worker, アイコン）を追加"
```

---

### Task 10: ローカルサーバーで動作確認

- [ ] **Step 1: ローカルHTTPサーバーで起動**

Service Workerはfile://では動作しないため、HTTPサーバーが必要。

```bash
cd C:/Users/goren/Desktop/Claude_Code/basyo_hou_app
python -m http.server 8080
```

ブラウザで `http://localhost:8080` を開く。

- [ ] **Step 2: 全画面の動作確認**

確認項目:
1. ホーム画面が表示される
2. 記憶モードで20種の写真＋名前がグリッド表示される
3. 写真タップで拡大オーバーレイが表示される
4. テストモード（グリッド）で入力→提出→採点が動く
5. テストモード（1枚ずつ）で入力→回答→正誤判定が動く
6. 結果画面が表示される
7. 設定画面の全項目が動作する
8. エクスポート/インポートが動く
9. 全データリセットが動く

- [ ] **Step 3: 問題があれば修正してコミット**

```bash
git add -A
git commit -m "fix: 動作確認で発見した問題を修正"
```

---

### Task 11: iPhone Safariでの確認

- [ ] **Step 1: 同じWi-Fiネットワークで確認**

PCのIPアドレスを確認し、iPhoneのSafariから `http://[PCのIP]:8080` でアクセス。

```bash
ipconfig | grep IPv4
```

- [ ] **Step 2: ホーム画面に追加**

iPhoneのSafariで:
1. 共有ボタン（□↑）をタップ
2. 「ホーム画面に追加」を選択
3. 「とり覚え」として追加

- [ ] **Step 3: ホーム画面から起動して動作確認**

ホーム画面のアイコンから起動し、フルスクリーンで動作することを確認。
スマホUIの表示崩れがないか確認。
入力欄のキーボード表示が正常か確認。

- [ ] **Step 4: 問題があれば修正してコミット**

```bash
git add -A
git commit -m "fix: iPhone Safari対応の修正"
```
