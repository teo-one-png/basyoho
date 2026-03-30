# とり覚え — 開発メモ

## 概要
鳥の写真を見て名前を覚える記憶術Webアプリ（PWA）。
iPhone Safariのホーム画面追加でアプリっぽく使える。

## 2026-03-29〜30 の作業内容

### ブレスト・設計
- GPT5.4との会話ログをベースに、WebアプリかiOSネイティブかを検討 → Webアプリに決定
- ブレストスキルで仕様を詰めた（Visual Companionでモックアップも表示）
- 設計仕様書: `docs/superpowers/specs/2026-03-29-bird-memory-app-design.md`
- 実装計画書: `docs/superpowers/plans/2026-03-29-bird-memory-app.md`

### 実装（全11タスク完了）
1. git初期化
2. 鳥データ定義（data.js）— 最初20種、後にタカ類10種追加で計30種
3. 設定モジュール（settings.js）— localStorage
4. IndexedDBモジュール（db.js）— 進捗保存
5. 出題・採点ロジック（quiz.js）— カタカナ正規化、連続正解でmastered判定
6. HTML + CSS — ダークモード固定、iPhone最適化
7. メインアプリロジック（app.js）— 画面遷移、記憶/テスト/結果/設定
8. 鳥画像取得 — Wikimedia Commonsから30種ダウンロード
9. PWA設定 — manifest.json、Service Worker、アイコン
10. ローカル動作確認
11. iPhone Safari確認（手順案内済み）

### 修正・追加
- 提出ボタンが見えない問題を修正（sticky + 背景 + z-index）
- ウグイスとカワラヒワの画像が卵だったので差し替え
- タカ類10種を追加（オオタカ、ハイタカ、ツミ、ノスリ、クマタカ、サシバ、ハチクマ、オオワシ、オジロワシ、ハヤブサ）
- 起動時の簡易ロック画面を追加（ID:1, Pass:1）
- 出題数の上限を999に変更（手入力対応）
- 鳥350図鑑から3回に分けて314種を追加（合計344種）— Wikipedia/Wikimedia Commons APIで画像自動取得
  - 第1弾: 107種、第2弾: 100種、第3弾: 107種（全弾失敗ゼロ）
- 全画像のライセンス情報をcredits.json/credits.jsに記録（CC BY/CC BY-SA/Public domain等）
- 設定画面に「写真クレジット」ページを追加（CC BY-SA帰属表示要件対応）
- Service Workerキャッシュをv6に更新（442枚対応）
- 「じゅもく覚え」モードを追加 — 樹木の葉っぱ写真252種（葉っぱで見分ける樹木図鑑より全種）
  - tree_data.js: 252種の樹木データ
  - images/trees/: 葉の写真252枚（Wikimedia Commons、フリーライセンス）
  - ホーム画面に「とり覚え / じゅもく覚え」切替ボタンを設置
  - 進捗データは鳥・樹木それぞれ独立してIndexedDBに保存（モード別統計表示対応）

### デプロイ
- GitHub Pagesへのデプロイ手順を案内済み（未実施）
- Privateリポジトリ + GitHub Pages推奨

## 技術構成
- HTML + CSS + JavaScript（フレームワークなし）
- IndexedDB: 進捗データ保存
- localStorage: 設定保存
- PWA: manifest.json + Service Worker
- ダークモード固定（#1a1a2e系）

## 今後の拡張予定
- 鳥350全種への拡大（gakusyu_shien_systemのHTMLからデータ抽出可能）
- 花・昆虫カテゴリの追加
- 回答欄の複数化（名前＋季節＋生息地など）
- カテゴリ別の出題フィルタ

## ローカルサーバー起動方法
```bash
cd C:/Users/goren/Desktop/Claude_Code/basyo_hou_app
python -m http.server 8080
```
ブラウザで http://localhost:8080 を開く
