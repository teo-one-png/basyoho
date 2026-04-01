# しょくそう覚え Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 既存「とり覚え」アプリに「しょくそう覚え」モード（昆虫⇔食草クイズ）を追加する

**Architecture:** 既存のモード切替（bird/tree/nakigoe）に `shokusou` モードを追加。しょくそう覚えモード内にさらに「むし→しょくそう」「しょくそう→むし」のサブモード切替を設ける。クイズは1画像に対して複数回答欄（名前＋関連種）を動的生成する。データはPDF「昆虫と食草ハンドブック」から全種を網羅。

**Tech Stack:** HTML/CSS/JS（既存PWAに追加）、IndexedDB（既存db.js流用）、Wikimedia Commons画像

---

## File Structure

| ファイル | 役割 |
|---|---|
| `shokusou_data.js` (新規) | 昆虫データ・植物データ・昆虫⇔食草マッピング |
| `index.html` (変更) | モードボタン追加、サブモード切替UI追加 |
| `app.js` (変更) | しょくそう覚えモードのロジック（getActiveData拡張、サブモード切替、複数回答UI生成、採点ロジック） |
| `style.css` (変更) | サブモード切替ボタン、複数回答欄のスタイル |
| `images/shokusou/` (新規) | 昆虫・植物画像（Wikimedia Commonsからダウンロード） |
| `download_shokusou.py` (新規) | 画像ダウンロードスクリプト |

---

### Task 1: shokusou_data.js — 全種データ作成

**Files:**
- Create: `shokusou_data.js`

PDFから抽出した全昆虫種（約95種）と全植物種（約85種）のデータ。各昆虫にfoodPlants配列、各植物にinsects配列を持たせる。

- [ ] **Step 1: shokusou_data.js を作成**

昆虫データ（INSECT_DATA）と植物データ（PLANT_DATA）を定義。PDFの「主な掲載種一覧」と各解説ページから全種を網羅。

```js
// shokusou_data.js

const INSECT_DATA = [
  // === チョウ目（チョウ類）===
  // アゲハチョウ科
  { id: "ageha", name: "アゲハ", altName: "ナミアゲハ", category: "チョウ類", image: "images/shokusou/ageha.jpg", foodPlants: ["ミカン類", "サンショウ", "カラタチ", "カラスザンショウ"] },
  { id: "kuroageha", name: "クロアゲハ", category: "チョウ類", image: "images/shokusou/kuroageha.jpg", foodPlants: ["ミカン類", "カラスザンショウ", "コクサギ", "キハダ"] },
  { id: "karasuageha", name: "カラスアゲハ", category: "チョウ類", image: "images/shokusou/karasuageha.jpg", foodPlants: ["コクサギ", "キハダ", "カラスザンショウ"] },
  { id: "nagasakiageha", name: "ナガサキアゲハ", category: "チョウ類", image: "images/shokusou/nagasakiageha.jpg", foodPlants: ["ミカン類", "ユズ", "カラタチ"] },
  { id: "kiageha", name: "キアゲハ", category: "チョウ類", image: "images/shokusou/kiageha.jpg", foodPlants: ["セリ", "ニンジン", "ミツバ"] },
  { id: "aosujiageha", name: "アオスジアゲハ", category: "チョウ類", image: "images/shokusou/aosujiageha.jpg", foodPlants: ["クスノキ", "タブノキ"] },
  { id: "jakouageha", name: "ジャコウアゲハ", category: "チョウ類", image: "images/shokusou/jakouageha.jpg", foodPlants: ["ウマノスズクサ類"] },
  { id: "gifuchou", name: "ギフチョウ", category: "チョウ類", image: "images/shokusou/gifuchou.jpg", foodPlants: ["カンアオイ類"] },
  // シロチョウ科
  { id: "monshirochou", name: "モンシロチョウ", category: "チョウ類", image: "images/shokusou/monshirochou.jpg", foodPlants: ["キャベツ", "アブラナ類", "イヌガラシ"] },
  { id: "monkichou", name: "モンキチョウ", category: "チョウ類", image: "images/shokusou/monkichou.jpg", foodPlants: ["シロツメクサ"] },
  { id: "kitakichou", name: "キタキチョウ", category: "チョウ類", image: "images/shokusou/kitakichou.jpg", foodPlants: ["ハギ類", "ネムノキ", "メドハギ"] },
  // タテハチョウ科
  { id: "akatateha", name: "アカタテハ", category: "チョウ類", image: "images/shokusou/akatateha.jpg", foodPlants: ["カラムシ", "アカソ類"] },
  { id: "ruritateha", name: "ルリタテハ", category: "チョウ類", image: "images/shokusou/ruritateha.jpg", foodPlants: ["サルトリイバラ", "ホトトギス類"] },
  { id: "kitatetaha", name: "キタテハ", category: "チョウ類", image: "images/shokusou/kitatetaha.jpg", foodPlants: ["カナムグラ"] },
  { id: "tsumagurohyoumon", name: "ツマグロヒョウモン", category: "チョウ類", image: "images/shokusou/tsumagurohyoumon.jpg", foodPlants: ["スミレ類"] },
  { id: "ichimonjichou", name: "イチモンジチョウ", category: "チョウ類", image: "images/shokusou/ichimonjichou.jpg", foodPlants: ["スイカズラ"] },
  { id: "oomurasaki", name: "オオムラサキ", category: "チョウ類", image: "images/shokusou/oomurasaki.jpg", foodPlants: ["エノキ"] },
  { id: "gomadarachou", name: "ゴマダラチョウ", category: "チョウ類", image: "images/shokusou/gomadarachou.jpg", foodPlants: ["エノキ"] },
  { id: "komurasaki", name: "コムラサキ", category: "チョウ類", image: "images/shokusou/komurasaki.jpg", foodPlants: ["ヤナギ類"] },
  { id: "ishigakechou", name: "イシガケチョウ", category: "チョウ類", image: "images/shokusou/ishigakechou.jpg", foodPlants: ["イヌビワ"] },
  { id: "kurokonomachou", name: "クロコノマチョウ", category: "チョウ類", image: "images/shokusou/kurokonomachou.jpg", foodPlants: ["ジュズダマ", "ススキ"] },
  { id: "asagimadara", name: "アサギマダラ", category: "チョウ類", image: "images/shokusou/asagimadara.jpg", foodPlants: ["キジョラン", "イケマ"] },
  { id: "komisuji", name: "コミスジ", category: "チョウ類", image: "images/shokusou/komisuji.jpg", foodPlants: ["クズ", "フジ"] },
  { id: "uraginshijimi", name: "ウラギンシジミ", category: "チョウ類", image: "images/shokusou/uraginshijimi.jpg", foodPlants: ["フジ", "クズ"] },
  // シジミチョウ科
  { id: "murasakitsubame", name: "ムラサキツバメ", category: "チョウ類", image: "images/shokusou/murasakitsubame.jpg", foodPlants: ["マテバシイ"] },
  { id: "murasakishijimi", name: "ムラサキシジミ", category: "チョウ類", image: "images/shokusou/murasakishijimi.jpg", foodPlants: ["アラカシ", "シラカシ"] },
  { id: "midorishijimi", name: "ミドリシジミ", category: "チョウ類", image: "images/shokusou/midorishijimi.jpg", foodPlants: ["ハンノキ", "ヤマハンノキ"] },
  { id: "yamatoshijimi", name: "ヤマトシジミ", category: "チョウ類", image: "images/shokusou/yamatoshijimi.jpg", foodPlants: ["カタバミ"] },
  { id: "benishijimi", name: "ベニシジミ", category: "チョウ類", image: "images/shokusou/benishijimi.jpg", foodPlants: ["ギシギシ類", "スイバ"] },
  // セセリチョウ科
  { id: "aobaseseri", name: "アオバセセリ", category: "チョウ類", image: "images/shokusou/aobaseseri.jpg", foodPlants: ["アワブキ"] },
  { id: "suminagashi", name: "スミナガシ", category: "チョウ類", image: "images/shokusou/suminagashi.jpg", foodPlants: ["アワブキ"] },
  { id: "daimyouseseri", name: "ダイミョウセセリ", category: "チョウ類", image: "images/shokusou/daimyouseseri.jpg", foodPlants: ["ヤマノイモ", "オニドコロ"] },
  { id: "ichimonjiseseri", name: "イチモンジセセリ", category: "チョウ類", image: "images/shokusou/ichimonjiseseri.jpg", foodPlants: ["ススキ", "イネ"] },

  // === チョウ目（ガ類）===
  { id: "hotaruga", name: "ホタルガ", category: "ガ類", image: "images/shokusou/hotaruga.jpg", foodPlants: ["ヒサカキ", "サカキ"] },
  { id: "okinawarurichirashi", name: "オキナワルリチラシ", category: "ガ類", image: "images/shokusou/okinawarurichirashi.jpg", foodPlants: ["ヒサカキ", "サカキ", "ヤブツバキ"] },
  { id: "minousuba", name: "ミノウスバ", category: "ガ類", image: "images/shokusou/minousuba.jpg", foodPlants: ["マサキ", "ニシキギ", "マユミ"] },
  { id: "ibotaga", name: "イボタガ", category: "ガ類", image: "images/shokusou/ibotaga.jpg", foodPlants: ["イボタノキ", "ネズミモチ"] },
  { id: "kiedashaku", name: "キエダシャク", category: "ガ類", image: "images/shokusou/kiedashaku.jpg", foodPlants: ["ノイバラ"] },
  { id: "ooayashaku", name: "オオアヤシャク", category: "ガ類", image: "images/shokusou/ooayashaku.jpg", foodPlants: ["コブシ", "ホオノキ"] },
  { id: "ooskashiba", name: "オオスカシバ", category: "ガ類", image: "images/shokusou/ooskashiba.jpg", foodPlants: ["クチナシ"] },
  { id: "hoshihoujaku", name: "ホシホウジャク", category: "ガ類", image: "images/shokusou/hoshihoujaku.jpg", foodPlants: ["ヘクソカズラ"] },
  { id: "kosuzume", name: "コスズメ", category: "ガ類", image: "images/shokusou/kosuzume.jpg", foodPlants: ["ヤブガラシ"] },
  { id: "kuwaedashaku", name: "クワエダシャク", category: "ガ類", image: "images/shokusou/kuwaedashaku.jpg", foodPlants: ["クワ類"] },
  { id: "monhosobasuzume", name: "モンホソバスズメ", category: "ガ類", image: "images/shokusou/monhosobasuzume.jpg", foodPlants: ["オニグルミ"] },
  { id: "murasakishachihoko", name: "ムラサキシャチホコ", category: "ガ類", image: "images/shokusou/murasakishachihoko.jpg", foodPlants: ["オニグルミ"] },
  { id: "ashibenikagiba", name: "アシベニカギバ", category: "ガ類", image: "images/shokusou/ashibenikagiba.jpg", foodPlants: ["ガマズミ", "サンゴジュ"] },
  { id: "shinjusan", name: "シンジュサン", category: "ガ類", image: "images/shokusou/shinjusan.jpg", foodPlants: ["クロガネモチ", "クスノキ", "クヌギ"] },
  { id: "ustabiga", name: "ウスタビガ", category: "ガ類", image: "images/shokusou/ustabiga.jpg", foodPlants: ["コナラ", "クヌギ", "サクラ類"] },
  { id: "yamamayu", name: "ヤママユ", altName: "ヤママユガ", category: "ガ類", image: "images/shokusou/yamamayu.jpg", foodPlants: ["クヌギ", "コナラ", "クリ"] },
  { id: "takekareha", name: "タケカレハ", category: "ガ類", image: "images/shokusou/takekareha.jpg", foodPlants: ["タケ類", "ササ類"] },
  { id: "takenohosokiroba", name: "タケノホソクロバ", category: "ガ類", image: "images/shokusou/takenohosokiroba.jpg", foodPlants: ["タケ類", "ササ類"] },
  { id: "matsukareha", name: "マツカレハ", category: "ガ類", image: "images/shokusou/matsukareha.jpg", foodPlants: ["マツ類"] },
  { id: "chadokuga", name: "チャドクガ", category: "ガ類", image: "images/shokusou/chadokuga.jpg", foodPlants: ["ツバキ類", "サザンカ"] },
  { id: "kinokawaga", name: "キノカワガ", category: "ガ類", image: "images/shokusou/kinokawaga.jpg", foodPlants: ["カキノキ"] },
  { id: "oogomadaraedashaku", name: "オオゴマダラエダシャク", category: "ガ類", image: "images/shokusou/oogomadaraedashaku.jpg", foodPlants: ["カキノキ"] },
  { id: "iraga", name: "イラガ", category: "ガ類", image: "images/shokusou/iraga.jpg", foodPlants: ["カキノキ", "サクラ類", "クリ"] },
  { id: "akebikonoha", name: "アケビコノハ", category: "ガ類", image: "images/shokusou/akebikonoha.jpg", foodPlants: ["アケビ", "ミツバアケビ"] },
  { id: "oomizuao", name: "オオミズアオ", category: "ガ類", image: "images/shokusou/oomizuao.jpg", foodPlants: ["サクラ類", "クリ", "ハナミズキ"] },
  { id: "kususan", name: "クスサン", category: "ガ類", image: "images/shokusou/kususan.jpg", foodPlants: ["クリ", "サクラ類", "クスノキ", "ケヤキ"] },
  { id: "maimaiga", name: "マイマイガ", category: "ガ類", image: "images/shokusou/maimaiga.jpg", foodPlants: ["サクラ類", "クヌギ", "ケヤキ"] },

  // === 甲虫目 ===
  { id: "gomadarakamikiri", name: "ゴマダラカミキリ", category: "甲虫類", image: "images/shokusou/gomadarakamikiri.jpg", foodPlants: ["ヤナギ類", "ミカン類", "スズカケノキ類"] },
  { id: "kuwakamikiri", name: "クワカミキリ", category: "甲虫類", image: "images/shokusou/kuwakamikiri.jpg", foodPlants: ["イチジク", "クワ類", "ケヤキ"] },
  { id: "nijuuyahoshitentou", name: "ニジュウヤホシテントウ", category: "甲虫類", image: "images/shokusou/nijuuyahoshitentou.jpg", foodPlants: ["イヌホオズキ類"] },
  { id: "tohoshitentou", name: "トホシテントウ", category: "甲虫類", image: "images/shokusou/tohoshitentou.jpg", foodPlants: ["カラスウリ"] },
  { id: "jingasahamushi", name: "ジンガサハムシ", category: "甲虫類", image: "images/shokusou/jingasahamushi.jpg", foodPlants: ["ヒルガオ"] },
  { id: "ichimonjikamenokohamushi", name: "イチモンジカメノコハムシ", category: "甲虫類", image: "images/shokusou/ichimonjikamenokohamushi.jpg", foodPlants: ["ムラサキシキブ"] },
  { id: "tohoshikubibosohamushi", name: "トホシクビボソハムシ", category: "甲虫類", image: "images/shokusou/tohoshikubibosohamushi.jpg", foodPlants: ["クコ"] },
  { id: "nirehamushi", name: "ニレハムシ", category: "甲虫類", image: "images/shokusou/nirehamushi.jpg", foodPlants: ["ケヤキ", "アキニレ"] },
  { id: "tsutsujikobuhamushi", name: "ツツジコブハムシ", category: "甲虫類", image: "images/shokusou/tsutsujikobuhamushi.jpg", foodPlants: ["ツツジ類"] },
  { id: "akaganesaruhamushi", name: "アカガネサルハムシ", category: "甲虫類", image: "images/shokusou/akaganesaruhamushi.jpg", foodPlants: ["エビヅル", "ノブドウ"] },
  { id: "herigurotentouminohamushi", name: "ヘリグロテントウノミハムシ", category: "甲虫類", image: "images/shokusou/herigurotentouminohamushi.jpg", foodPlants: ["ヒイラギモクセイ", "ヒイラギ"] },
  { id: "dorohamakichokkiri", name: "ドロハマキチョッキリ", category: "甲虫類", image: "images/shokusou/dorohamakichokkiri.jpg", foodPlants: ["イタドリ"] },
  { id: "higenagaotoshibumi", name: "ヒゲナガオトシブミ", category: "甲虫類", image: "images/shokusou/higenagaotoshibumi.jpg", foodPlants: ["アブラチャン", "クロモジ"] },
  { id: "otoshibumi", name: "オトシブミ", altName: "ナミオトシブミ", category: "甲虫類", image: "images/shokusou/otoshibumi.jpg", foodPlants: ["クリ", "コナラ", "ハンノキ"] },
  { id: "shirosujikamikiri", name: "シロスジカミキリ", category: "甲虫類", image: "images/shokusou/shirosujikamikiri.jpg", foodPlants: ["クリ", "コナラ", "クヌギ"] },
  { id: "egohigenagazoumushi", name: "エゴヒゲナガゾウムシ", category: "甲虫類", image: "images/shokusou/egohigenagazoumushi.jpg", foodPlants: ["エゴノキ"] },
  { id: "egotsurukubiotoshibumi", name: "エゴツルクビオトシブミ", category: "甲虫類", image: "images/shokusou/egotsurukubiotoshibumi.jpg", foodPlants: ["エゴノキ"] },

  // === カメムシ目 ===
  { id: "akasujikamemushi", name: "アカスジカメムシ", category: "カメムシ類", image: "images/shokusou/akasujikamemushi.jpg", foodPlants: ["ヤブジラミ", "ニンジン"] },
  { id: "kibaraherikamemushi", name: "キバラヘリカメムシ", category: "カメムシ類", image: "images/shokusou/kibaraherikamemushi.jpg", foodPlants: ["マユミ", "ニシキギ"] },
  { id: "esakimonkitsunokamemushi", name: "エサキモンキツノカメムシ", category: "カメムシ類", image: "images/shokusou/esakimonkitsunokamemushi.jpg", foodPlants: ["ミズキ", "ハンノキ"] },
  { id: "akasujikinkamemushi", name: "アカスジキンカメムシ", category: "カメムシ類", image: "images/shokusou/akasujikinkamemushi.jpg", foodPlants: ["ミズキ", "コブシ"] },
  { id: "ookinkamemushi", name: "オオキンカメムシ", category: "カメムシ類", image: "images/shokusou/ookinkamemushi.jpg", foodPlants: ["アブラギリ"] },
  { id: "akagikamemushi", name: "アカギカメムシ", category: "カメムシ類", image: "images/shokusou/akagikamemushi.jpg", foodPlants: ["アカメガシワ"] },

  // === 沖縄のチョウ ===
  { id: "shiroobi_ageha", name: "シロオビアゲハ", category: "沖縄チョウ", image: "images/shokusou/shiroobi_ageha.jpg", foodPlants: ["シークワーサー"] },
  { id: "tsumabenichou", name: "ツマベニチョウ", category: "沖縄チョウ", image: "images/shokusou/tsumabenichou.jpg", foodPlants: ["ギョボク"] },
  { id: "namieshirochou", name: "ナミエシロチョウ", category: "沖縄チョウ", image: "images/shokusou/namieshirochou.jpg", foodPlants: ["ツゲモドキ"] },
  { id: "oogomadarachou", name: "オオゴマダラ", category: "沖縄チョウ", image: "images/shokusou/oogomadarachou.jpg", foodPlants: ["ホウライカガミ"] },
  { id: "kabamadara", name: "カバマダラ", category: "沖縄チョウ", image: "images/shokusou/kabamadara.jpg", foodPlants: ["トウワタ"] },
  { id: "tsumamurasakimadara", name: "ツマムラサキマダラ", category: "沖縄チョウ", image: "images/shokusou/tsumamurasakimadara.jpg", foodPlants: ["オキナワテイカカズラ"] },
  { id: "ryuukyuuasagimadara", name: "リュウキュウアサギマダラ", category: "沖縄チョウ", image: "images/shokusou/ryuukyuuasagimadara.jpg", foodPlants: ["ツルモウリンカ"] },
  { id: "konohachou", name: "コノハチョウ", category: "沖縄チョウ", image: "images/shokusou/konohachou.jpg", foodPlants: ["オキナワスズムシソウ"] },
  { id: "aotatehamodoki", name: "アオタテハモドキ", category: "沖縄チョウ", image: "images/shokusou/aotatehamodoki.jpg", foodPlants: ["イワダレソウ"] },
  { id: "iwakawashijimi", name: "イワカワシジミ", category: "沖縄チョウ", image: "images/shokusou/iwakawashijimi.jpg", foodPlants: ["クチナシ"] },
  { id: "bananaseseri", name: "バナナセセリ", category: "沖縄チョウ", image: "images/shokusou/bananaseseri.jpg", foodPlants: ["バナナ"] },
];

const PLANT_DATA = [
  // === ミカン科 ===
  { id: "mikanrui", name: "ミカン類", category: "樹木", image: "images/shokusou/mikanrui.jpg", insects: ["アゲハ", "クロアゲハ", "ナガサキアゲハ"] },
  { id: "sanshou", name: "サンショウ", category: "樹木", image: "images/shokusou/sanshou.jpg", insects: ["アゲハ"] },
  { id: "karatachi", name: "カラタチ", category: "樹木", image: "images/shokusou/karatachi.jpg", insects: ["アゲハ", "ナガサキアゲハ"] },
  { id: "karasuzanshou", name: "カラスザンショウ", category: "樹木", image: "images/shokusou/karasuzanshou.jpg", insects: ["アゲハ", "クロアゲハ", "カラスアゲハ"] },
  { id: "kokusagi", name: "コクサギ", category: "樹木", image: "images/shokusou/kokusagi.jpg", insects: ["クロアゲハ", "カラスアゲハ"] },
  { id: "kihada", name: "キハダ", category: "樹木", image: "images/shokusou/kihada.jpg", insects: ["クロアゲハ", "カラスアゲハ"] },
  { id: "yuzu", name: "ユズ", category: "樹木", image: "images/shokusou/yuzu.jpg", insects: ["ナガサキアゲハ"] },
  // === セリ科 ===
  { id: "seri", name: "セリ", category: "草本", image: "images/shokusou/seri.jpg", insects: ["キアゲハ"] },
  { id: "ninjin", name: "ニンジン", category: "草本", image: "images/shokusou/ninjin.jpg", insects: ["キアゲハ", "アカスジカメムシ"] },
  { id: "mitsuba", name: "ミツバ", category: "草本", image: "images/shokusou/mitsuba.jpg", insects: ["キアゲハ"] },
  // === クスノキ科 ===
  { id: "kusunoki", name: "クスノキ", category: "樹木", image: "images/shokusou/kusunoki.jpg", insects: ["アオスジアゲハ", "シンジュサン", "クスサン"] },
  { id: "tabunoki", name: "タブノキ", category: "樹木", image: "images/shokusou/tabunoki.jpg", insects: ["アオスジアゲハ"] },
  // === ウマノスズクサ科 ===
  { id: "umanosuzkusarui", name: "ウマノスズクサ類", category: "草本", image: "images/shokusou/umanosuzkusarui.jpg", insects: ["ジャコウアゲハ"] },
  { id: "kanaoi_rui", name: "カンアオイ類", category: "草本", image: "images/shokusou/kanaoi_rui.jpg", insects: ["ギフチョウ"] },
  // === アブラナ科 ===
  { id: "kyabetsu", name: "キャベツ", category: "草本", image: "images/shokusou/kyabetsu.jpg", insects: ["モンシロチョウ"] },
  { id: "aburana_rui", name: "アブラナ類", category: "草本", image: "images/shokusou/aburana_rui.jpg", insects: ["モンシロチョウ"] },
  { id: "inugarashi", name: "イヌガラシ", category: "草本", image: "images/shokusou/inugarashi.jpg", insects: ["モンシロチョウ"] },
  // === マメ科 ===
  { id: "shirotsumekusa", name: "シロツメクサ", category: "草本", image: "images/shokusou/shirotsumekusa.jpg", insects: ["モンキチョウ"] },
  { id: "hagirui", name: "ハギ類", category: "樹木", image: "images/shokusou/hagirui.jpg", insects: ["キタキチョウ"] },
  { id: "nemunoki", name: "ネムノキ", category: "樹木", image: "images/shokusou/nemunoki.jpg", insects: ["キタキチョウ"] },
  { id: "kuzu", name: "クズ", category: "草本", image: "images/shokusou/kuzu.jpg", insects: ["コミスジ", "ウラギンシジミ"] },
  { id: "fuji", name: "フジ", category: "樹木", image: "images/shokusou/fuji.jpg", insects: ["コミスジ", "ウラギンシジミ"] },
  // === イラクサ科 ===
  { id: "karamushi", name: "カラムシ", category: "草本", image: "images/shokusou/karamushi.jpg", insects: ["アカタテハ"] },
  { id: "akaso_rui", name: "アカソ類", category: "草本", image: "images/shokusou/akaso_rui.jpg", insects: ["アカタテハ"] },
  // === サルトリイバラ科・ユリ科 ===
  { id: "sarutoriibara", name: "サルトリイバラ", category: "樹木", image: "images/shokusou/sarutoriibara.jpg", insects: ["ルリタテハ"] },
  { id: "hototogisu_rui", name: "ホトトギス類", category: "草本", image: "images/shokusou/hototogisu_rui.jpg", insects: ["ルリタテハ"] },
  // === アサ科 ===
  { id: "kanamugura", name: "カナムグラ", category: "草本", image: "images/shokusou/kanamugura.jpg", insects: ["キタテハ"] },
  { id: "enoki", name: "エノキ", category: "樹木", image: "images/shokusou/enoki.jpg", insects: ["オオムラサキ", "ゴマダラチョウ"] },
  // === スミレ科 ===
  { id: "sumire_rui", name: "スミレ類", category: "草本", image: "images/shokusou/sumire_rui.jpg", insects: ["ツマグロヒョウモン"] },
  // === スイカズラ科 ===
  { id: "suikazura", name: "スイカズラ", category: "樹木", image: "images/shokusou/suikazura.jpg", insects: ["イチモンジチョウ"] },
  // === ヤナギ科 ===
  { id: "yanagi_rui", name: "ヤナギ類", category: "樹木", image: "images/shokusou/yanagi_rui.jpg", insects: ["コムラサキ", "ゴマダラカミキリ"] },
  // === クワ科 ===
  { id: "inubiwa", name: "イヌビワ", category: "樹木", image: "images/shokusou/inubiwa.jpg", insects: ["イシガケチョウ"] },
  { id: "kuwa_rui", name: "クワ類", category: "樹木", image: "images/shokusou/kuwa_rui.jpg", insects: ["クワエダシャク", "クワカミキリ"] },
  { id: "ichijiku", name: "イチジク", category: "樹木", image: "images/shokusou/ichijiku.jpg", insects: ["クワカミキリ"] },
  // === イネ科 ===
  { id: "suzudama", name: "ジュズダマ", category: "草本", image: "images/shokusou/suzudama.jpg", insects: ["クロコノマチョウ"] },
  { id: "susuki", name: "ススキ", category: "草本", image: "images/shokusou/susuki.jpg", insects: ["クロコノマチョウ", "イチモンジセセリ"] },
  { id: "ine", name: "イネ", category: "草本", image: "images/shokusou/ine.jpg", insects: ["イチモンジセセリ"] },
  { id: "take_rui", name: "タケ類", category: "樹木", image: "images/shokusou/take_rui.jpg", insects: ["タケカレハ", "タケノホソクロバ"] },
  { id: "sasa_rui", name: "ササ類", category: "草本", image: "images/shokusou/sasa_rui.jpg", insects: ["タケカレハ", "タケノホソクロバ"] },
  // === キョウチクトウ科 ===
  { id: "kijoran", name: "キジョラン", category: "草本", image: "images/shokusou/kijoran.jpg", insects: ["アサギマダラ"] },
  { id: "ikema", name: "イケマ", category: "草本", image: "images/shokusou/ikema.jpg", insects: ["アサギマダラ"] },
  // === ブナ科 ===
  { id: "matebashii", name: "マテバシイ", category: "樹木", image: "images/shokusou/matebashii.jpg", insects: ["ムラサキツバメ"] },
  { id: "arakashi", name: "アラカシ", category: "樹木", image: "images/shokusou/arakashi.jpg", insects: ["ムラサキシジミ"] },
  { id: "shirakashi", name: "シラカシ", category: "樹木", image: "images/shokusou/shirakashi.jpg", insects: ["ムラサキシジミ"] },
  { id: "konara", name: "コナラ", category: "樹木", image: "images/shokusou/konara.jpg", insects: ["ウスタビガ", "ヤママユ", "シロスジカミキリ", "オトシブミ"] },
  { id: "kunugi", name: "クヌギ", category: "樹木", image: "images/shokusou/kunugi.jpg", insects: ["ウスタビガ", "ヤママユ", "シンジュサン", "マイマイガ", "シロスジカミキリ"] },
  { id: "kuri", name: "クリ", category: "樹木", image: "images/shokusou/kuri.jpg", insects: ["ヤママユ", "イラガ", "オオミズアオ", "クスサン", "オトシブミ", "シロスジカミキリ"] },
  // === カバノキ科 ===
  { id: "hannoki", name: "ハンノキ", category: "樹木", image: "images/shokusou/hannoki.jpg", insects: ["ミドリシジミ", "エサキモンキツノカメムシ", "オトシブミ"] },
  { id: "yamahannoki", name: "ヤマハンノキ", category: "樹木", image: "images/shokusou/yamahannoki.jpg", insects: ["ミドリシジミ"] },
  // === カタバミ科 ===
  { id: "katabami", name: "カタバミ", category: "草本", image: "images/shokusou/katabami.jpg", insects: ["ヤマトシジミ"] },
  // === タデ科 ===
  { id: "gishigishi_rui", name: "ギシギシ類", category: "草本", image: "images/shokusou/gishigishi_rui.jpg", insects: ["ベニシジミ"] },
  { id: "suiba", name: "スイバ", category: "草本", image: "images/shokusou/suiba.jpg", insects: ["ベニシジミ"] },
  // === アワブキ科 ===
  { id: "awabuki", name: "アワブキ", category: "樹木", image: "images/shokusou/awabuki.jpg", insects: ["アオバセセリ", "スミナガシ"] },
  // === ヤマノイモ科 ===
  { id: "yamanoimo", name: "ヤマノイモ", category: "草本", image: "images/shokusou/yamanoimo.jpg", insects: ["ダイミョウセセリ"] },
  { id: "onidokoro", name: "オニドコロ", category: "草本", image: "images/shokusou/onidokoro.jpg", insects: ["ダイミョウセセリ"] },
  // === サカキ科 ===
  { id: "hisakaki", name: "ヒサカキ", category: "樹木", image: "images/shokusou/hisakaki.jpg", insects: ["ホタルガ", "オキナワルリチラシ"] },
  { id: "sakaki", name: "サカキ", category: "樹木", image: "images/shokusou/sakaki.jpg", insects: ["ホタルガ", "オキナワルリチラシ"] },
  // === ニシキギ科 ===
  { id: "masaki", name: "マサキ", category: "樹木", image: "images/shokusou/masaki.jpg", insects: ["ミノウスバ"] },
  { id: "nishikigi", name: "ニシキギ", category: "樹木", image: "images/shokusou/nishikigi.jpg", insects: ["ミノウスバ", "キバラヘリカメムシ"] },
  { id: "mayumi", name: "マユミ", category: "樹木", image: "images/shokusou/mayumi.jpg", insects: ["ミノウスバ", "キバラヘリカメムシ"] },
  // === モクセイ科 ===
  { id: "ibotanoki", name: "イボタノキ", category: "樹木", image: "images/shokusou/ibotanoki.jpg", insects: ["イボタガ"] },
  { id: "nezumimochi", name: "ネズミモチ", category: "樹木", image: "images/shokusou/nezumimochi.jpg", insects: ["イボタガ"] },
  // === バラ科 ===
  { id: "noibara", name: "ノイバラ", category: "樹木", image: "images/shokusou/noibara.jpg", insects: ["キエダシャク"] },
  { id: "sakura_rui", name: "サクラ類", category: "樹木", image: "images/shokusou/sakura_rui.jpg", insects: ["ウスタビガ", "イラガ", "オオミズアオ", "クスサン", "マイマイガ"] },
  // === モクレン科 ===
  { id: "kobushi", name: "コブシ", category: "樹木", image: "images/shokusou/kobushi.jpg", insects: ["オオアヤシャク", "アカスジキンカメムシ"] },
  { id: "hoonoki", name: "ホオノキ", category: "樹木", image: "images/shokusou/hoonoki.jpg", insects: ["オオアヤシャク"] },
  // === アカネ科 ===
  { id: "kuchinashi", name: "クチナシ", category: "樹木", image: "images/shokusou/kuchinashi.jpg", insects: ["オオスカシバ", "イワカワシジミ"] },
  { id: "hekusokazura", name: "ヘクソカズラ", category: "草本", image: "images/shokusou/hekusokazura.jpg", insects: ["ホシホウジャク"] },
  // === ブドウ科 ===
  { id: "yabugarashi", name: "ヤブガラシ", category: "草本", image: "images/shokusou/yabugarashi.jpg", insects: ["コスズメ"] },
  { id: "ebidzuru", name: "エビヅル", category: "草本", image: "images/shokusou/ebidzuru.jpg", insects: ["アカガネサルハムシ"] },
  // === クルミ科 ===
  { id: "onigurumi", name: "オニグルミ", category: "樹木", image: "images/shokusou/onigurumi.jpg", insects: ["モンホソバスズメ", "ムラサキシャチホコ"] },
  // === ガマズミ科 ===
  { id: "gamazumi", name: "ガマズミ", category: "樹木", image: "images/shokusou/gamazumi.jpg", insects: ["アシベニカギバ"] },
  { id: "sangoju", name: "サンゴジュ", category: "樹木", image: "images/shokusou/sangoju.jpg", insects: ["アシベニカギバ"] },
  // === モチノキ科 ===
  { id: "kuroganemochi", name: "クロガネモチ", category: "樹木", image: "images/shokusou/kuroganemochi.jpg", insects: ["シンジュサン"] },
  // === マツ科 ===
  { id: "matsu_rui", name: "マツ類", category: "樹木", image: "images/shokusou/matsu_rui.jpg", insects: ["マツカレハ"] },
  // === ツバキ科 ===
  { id: "tsubaki_rui", name: "ツバキ類", category: "樹木", image: "images/shokusou/tsubaki_rui.jpg", insects: ["チャドクガ"] },
  { id: "sazanka", name: "サザンカ", category: "樹木", image: "images/shokusou/sazanka.jpg", insects: ["チャドクガ"] },
  // === カキノキ科 ===
  { id: "kakinoki", name: "カキノキ", category: "樹木", image: "images/shokusou/kakinoki.jpg", insects: ["キノカワガ", "オオゴマダラエダシャク", "イラガ"] },
  // === アケビ科 ===
  { id: "akebi", name: "アケビ", category: "樹木", image: "images/shokusou/akebi.jpg", insects: ["アケビコノハ"] },
  { id: "mitsubaakebi", name: "ミツバアケビ", category: "樹木", image: "images/shokusou/mitsubaakebi.jpg", insects: ["アケビコノハ"] },
  // === ミズキ科 ===
  { id: "mizuki", name: "ミズキ", category: "樹木", image: "images/shokusou/mizuki.jpg", insects: ["エサキモンキツノカメムシ", "アカスジキンカメムシ"] },
  { id: "hanamizuki", name: "ハナミズキ", category: "樹木", image: "images/shokusou/hanamizuki.jpg", insects: ["オオミズアオ"] },
  // === ニレ科 ===
  { id: "keyaki", name: "ケヤキ", category: "樹木", image: "images/shokusou/keyaki.jpg", insects: ["ニレハムシ", "クワカミキリ", "クスサン", "マイマイガ"] },
  { id: "akinire", name: "アキニレ", category: "樹木", image: "images/shokusou/akinire.jpg", insects: ["ニレハムシ"] },
  // === ナス科 ===
  { id: "inuhoozuki_rui", name: "イヌホオズキ類", category: "草本", image: "images/shokusou/inuhoozuki_rui.jpg", insects: ["ニジュウヤホシテントウ"] },
  { id: "kuko", name: "クコ", category: "樹木", image: "images/shokusou/kuko.jpg", insects: ["トホシクビボソハムシ"] },
  // === ウリ科 ===
  { id: "karasuuri", name: "カラスウリ", category: "草本", image: "images/shokusou/karasuuri.jpg", insects: ["トホシテントウ"] },
  // === ヒルガオ科 ===
  { id: "hirugao", name: "ヒルガオ", category: "草本", image: "images/shokusou/hirugao.jpg", insects: ["ジンガサハムシ"] },
  // === シソ科 ===
  { id: "murasakishikibu", name: "ムラサキシキブ", category: "樹木", image: "images/shokusou/murasakishikibu.jpg", insects: ["イチモンジカメノコハムシ"] },
  // === ツツジ科 ===
  { id: "tsutsuji_rui", name: "ツツジ類", category: "樹木", image: "images/shokusou/tsutsuji_rui.jpg", insects: ["ツツジコブハムシ"] },
  // === モクセイ科（ヒイラギ系）===
  { id: "hiiragimokkusei", name: "ヒイラギモクセイ", category: "樹木", image: "images/shokusou/hiiragimokkusei.jpg", insects: ["ヘリグロテントウノミハムシ"] },
  { id: "hiiragi", name: "ヒイラギ", category: "樹木", image: "images/shokusou/hiiragi.jpg", insects: ["ヘリグロテントウノミハムシ"] },
  // === タデ科 ===
  { id: "itadori", name: "イタドリ", category: "草本", image: "images/shokusou/itadori.jpg", insects: ["ドロハマキチョッキリ"] },
  // === クスノキ科（クロモジ属）===
  { id: "aburachan", name: "アブラチャン", category: "樹木", image: "images/shokusou/aburachan.jpg", insects: ["ヒゲナガオトシブミ"] },
  { id: "kuromoji", name: "クロモジ", category: "樹木", image: "images/shokusou/kuromoji.jpg", insects: ["ヒゲナガオトシブミ"] },
  // === エゴノキ科 ===
  { id: "egonoki", name: "エゴノキ", category: "樹木", image: "images/shokusou/egonoki.jpg", insects: ["エゴヒゲナガゾウムシ", "エゴツルクビオトシブミ"] },
  // === セリ科 ===
  { id: "yabujirami", name: "ヤブジラミ", category: "草本", image: "images/shokusou/yabujirami.jpg", insects: ["アカスジカメムシ"] },
  // === トウダイグサ科 ===
  { id: "aburagiri", name: "アブラギリ", category: "樹木", image: "images/shokusou/aburagiri.jpg", insects: ["オオキンカメムシ"] },
  { id: "akamegashiwa", name: "アカメガシワ", category: "樹木", image: "images/shokusou/akamegashiwa.jpg", insects: ["アカギカメムシ"] },
  // === スズカケノキ科 ===
  { id: "suzukakenoki_rui", name: "スズカケノキ類", category: "樹木", image: "images/shokusou/suzukakenoki_rui.jpg", insects: ["ゴマダラカミキリ"] },
  // === 沖縄系 ===
  { id: "shiikuwaasaa", name: "シークワーサー", category: "樹木", image: "images/shokusou/shiikuwaasaa.jpg", insects: ["シロオビアゲハ"] },
  { id: "gyoboku", name: "ギョボク", category: "樹木", image: "images/shokusou/gyoboku.jpg", insects: ["ツマベニチョウ"] },
  { id: "tsugemodoki", name: "ツゲモドキ", category: "樹木", image: "images/shokusou/tsugemodoki.jpg", insects: ["ナミエシロチョウ"] },
  { id: "houraikagami", name: "ホウライカガミ", category: "樹木", image: "images/shokusou/houraikagami.jpg", insects: ["オオゴマダラ"] },
  { id: "touwata", name: "トウワタ", category: "草本", image: "images/shokusou/touwata.jpg", insects: ["カバマダラ"] },
  { id: "okinawateikakazura", name: "オキナワテイカカズラ", category: "樹木", image: "images/shokusou/okinawateikakazura.jpg", insects: ["ツマムラサキマダラ"] },
  { id: "tsurumourinka", name: "ツルモウリンカ", category: "草本", image: "images/shokusou/tsurumourinka.jpg", insects: ["リュウキュウアサギマダラ"] },
  { id: "okinawasuzumushisou", name: "オキナワスズムシソウ", category: "草本", image: "images/shokusou/okinawasuzumushisou.jpg", insects: ["コノハチョウ"] },
  { id: "iwadaresou", name: "イワダレソウ", category: "草本", image: "images/shokusou/iwadaresou.jpg", insects: ["アオタテハモドキ"] },
  { id: "banana", name: "バナナ", category: "草本", image: "images/shokusou/banana.jpg", insects: ["バナナセセリ"] },
  { id: "medohagi", name: "メドハギ", category: "草本", image: "images/shokusou/medohagi.jpg", insects: ["キタキチョウ"] },
  { id: "nobudou", name: "ノブドウ", category: "草本", image: "images/shokusou/nobudou.jpg", insects: ["アカガネサルハムシ"] },
];
```

- [ ] **Step 2: index.html に script タグ追加**

`index.html` の既存 `<script src="tree_data.js">` の後に追加:
```html
<script src="shokusou_data.js"></script>
```

- [ ] **Step 3: Commit**
```bash
git add shokusou_data.js index.html
git commit -m "feat: add shokusou_data.js with all insect/plant data from PDF"
```

---

### Task 2: index.html — モードボタン＋サブモード切替UI追加

**Files:**
- Modify: `index.html`

- [ ] **Step 1: モード切替ボタンに「しょくそう覚え」を追加**

`index.html` のモードスイッチャー部分（`.mode-switcher`内）に追加:
```html
<button class="mode-btn" id="mode-shokusou" data-mode="shokusou">しょくそう覚え</button>
```

- [ ] **Step 2: サブモード切替UIを追加**

ホーム画面のモードスイッチャーの直後に追加:
```html
<div class="submode-switcher" id="submode-switcher" style="display:none">
  <button class="submode-btn active" data-submode="insect">むし→しょくそう</button>
  <button class="submode-btn" data-submode="plant">しょくそう→むし</button>
</div>
```

- [ ] **Step 3: Commit**
```bash
git add index.html
git commit -m "feat: add shokusou mode button and submode switcher to HTML"
```

---

### Task 3: style.css — サブモード切替・複数回答欄スタイル

**Files:**
- Modify: `style.css`

- [ ] **Step 1: モードボタン4つ対応＋サブモード切替のCSS追加**

`style.css` の末尾に追加:
```css
/* ===========================
   Shokusou mode
   =========================== */

/* 4-button mode switcher: smaller text */
.mode-switcher {
  flex-wrap: wrap;
}

.mode-switcher .mode-btn {
  font-size: 0.72rem;
  padding: 6px 8px;
}

/* Submode switcher */
.submode-switcher {
  display: flex;
  gap: 6px;
  margin: 8px 0 12px 0;
  justify-content: center;
}

.submode-btn {
  background: var(--bg2);
  color: var(--text-muted);
  border: 1px solid var(--border);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
}

.submode-btn.active {
  background: var(--bg3);
  color: var(--text);
  border-color: var(--purple-lt);
}

/* Multi-answer card: show full image without cropping */
.bird-card.shokusou-card img {
  max-height: min(42vh, 300px);
  object-fit: contain;
  width: 100%;
}

/* Multiple input fields within a card */
.shokusou-answer-group {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 100%;
}

.shokusou-answer-group .answer-label {
  font-size: 0.55rem;
  color: var(--text-muted);
  padding-left: 4px;
}

.shokusou-answer-group input {
  width: 100%;
  background: var(--input-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 4px 6px;
  font-size: 0.7rem;
  color: var(--text);
  outline: none;
}

.shokusou-answer-group input:focus {
  border-color: var(--purple-lt);
}

.shokusou-answer-group input.correct {
  border-color: var(--green-lt);
  color: var(--green-lt);
}

.shokusou-answer-group input.wrong {
  border-color: var(--red);
  color: var(--red);
}

/* Grid layout for shokusou: 2 columns for more space */
.bird-grid.shokusou-grid {
  grid-template-columns: repeat(2, 1fr);
}
```

- [ ] **Step 2: Commit**
```bash
git add style.css
git commit -m "feat: add CSS for shokusou submode switcher and multi-answer cards"
```

---

### Task 4: app.js — しょくそう覚えモードロジック

**Files:**
- Modify: `app.js`

これが最大のタスク。既存ロジックを拡張してしょくそう覚えモードを動作させる。

- [ ] **Step 1: State変数とgetActiveData拡張**

`app.js` 先頭のState部分に追加:
```js
var currentSubMode = 'insect'; // 'insect' | 'plant'  (shokusou mode only)
```

`getActiveData()` を変更:
```js
function getActiveData() {
  if (currentMode === 'tree') return TREE_DATA;
  if (currentMode === 'nakigoe') return NAKIGOE_DATA;
  if (currentMode === 'shokusou') {
    return currentSubMode === 'plant' ? PLANT_DATA : INSECT_DATA;
  }
  return BIRD_DATA;
}
```

`isNakigoeMode()` の後に追加:
```js
function isShokusouMode() {
  return currentMode === 'shokusou';
}
```

- [ ] **Step 2: getModeLabels にしょくそう覚え追加**

```js
if (mode === 'shokusou') {
  return {
    title: 'しょくそう覚え',
    subtitle: currentSubMode === 'plant' ? 'しょくそう→むし' : 'むし→しょくそう',
    resultWrongTitle: '間違えた項目',
    catalogTitle: currentSubMode === 'plant' ? '植物一覧' : '昆虫一覧'
  };
}
```

- [ ] **Step 3: lastSessionIdsByMode / recentSessionHistoryByMode 拡張**

```js
var lastSessionIdsByMode = { bird: [], tree: [], shokusou_insect: [], shokusou_plant: [] };
var recentSessionHistoryByMode = { bird: [], tree: [], shokusou_insect: [], shokusou_plant: [] };
```

そして `currentMode` を使う部分で、shokusouの場合は `shokusou_insect` / `shokusou_plant` をキーとして使うようにする。

`rememberSessionQuestions` と `getRecentHistory` の呼び出し箇所で:
```js
function getSessionModeKey() {
  if (currentMode === 'shokusou') return 'shokusou_' + currentSubMode;
  return currentMode;
}
```

- [ ] **Step 4: renderMemorizeGrid をしょくそうモード対応に拡張**

暗記フェーズでは画像＋名前＋関連名（食草/昆虫）をすべて表示。回答フェーズでは画像＋入力欄を動的生成。

`renderMemorizeGrid` 内の else（画像モード）部分に、しょくそうモード用の分岐を追加:

```js
if (isShokusouMode() && !isAnswerPhase) {
  // 暗記フェーズ: 画像＋名前＋関連種をすべて表示
  var nameEl = document.createElement('p');
  nameEl.className = 'bird-card-name';
  nameEl.textContent = bird.name;
  card.appendChild(nameEl);

  var relatedNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
  if (relatedNames) {
    var relatedEl = document.createElement('p');
    relatedEl.className = 'bird-card-name';
    relatedEl.style.color = 'var(--purple-lt)';
    relatedEl.style.fontSize = '0.6rem';
    relatedEl.textContent = relatedNames.join('、');
    card.appendChild(relatedEl);
  }
}
```

回答フェーズでは複数入力欄を生成:
```js
if (isShokusouMode() && isAnswerPhase) {
  var answerGroup = document.createElement('div');
  answerGroup.className = 'shokusou-answer-group';

  // 名前の入力欄
  var nameLabel = document.createElement('span');
  nameLabel.className = 'answer-label';
  nameLabel.textContent = currentSubMode === 'insect' ? '昆虫名' : '植物名';
  answerGroup.appendChild(nameLabel);

  var nameInput = document.createElement('input');
  nameInput.type = 'text';
  nameInput.placeholder = 'カタカナ';
  nameInput.dataset.idx = idx;
  nameInput.dataset.field = 'name';
  answerGroup.appendChild(nameInput);

  // 関連種の入力欄
  var relatedNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
  relatedNames.forEach(function(rn, ri) {
    var label = document.createElement('span');
    label.className = 'answer-label';
    label.textContent = (currentSubMode === 'insect' ? '食草' : '昆虫') + (ri + 1);
    answerGroup.appendChild(label);

    var inp = document.createElement('input');
    inp.type = 'text';
    inp.placeholder = 'カタカナ';
    inp.dataset.idx = idx;
    inp.dataset.field = 'related_' + ri;
    answerGroup.appendChild(inp);
  });

  card.appendChild(answerGroup);
}
```

- [ ] **Step 5: submitGridTest をしょくそうモード対応に拡張**

しょくそうモードでは名前＋関連種すべてを採点する。全フィールド正解で1問正解とする。

```js
// shokusou mode scoring
if (isShokusouMode()) {
  var answerInputs = card.querySelectorAll('.shokusou-answer-group input');
  var allFieldsCorrect = true;

  // first input = name
  var nameInput = answerInputs[0];
  var nameCorrect = nameInput && checkAnswer(nameInput.value, bird.name);
  if (nameInput) {
    nameInput.classList.add(nameCorrect ? 'correct' : 'wrong');
    if (!nameCorrect) {
      nameInput.value = nameInput.value + ' → ' + bird.name;
      allFieldsCorrect = false;
    }
  }

  // remaining inputs = related names
  var relatedNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
  for (var ri = 0; ri < relatedNames.length; ri++) {
    var relInput = answerInputs[ri + 1];
    if (relInput) {
      var relCorrect = checkAnswer(relInput.value, relatedNames[ri]);
      relInput.classList.add(relCorrect ? 'correct' : 'wrong');
      if (!relCorrect) {
        relInput.value = relInput.value + ' → ' + relatedNames[ri];
        allFieldsCorrect = false;
      }
      relInput.disabled = true;
    }
  }

  if (allFieldsCorrect) correctCount++;
  testAnswers[i].isCorrect = allFieldsCorrect;
  testAnswers[i].userInput = nameInput ? nameInput.value : '';
  if (nameInput) nameInput.disabled = true;
}
```

- [ ] **Step 6: モードボタン＋サブモードボタンのイベントリスナー追加**

DOMContentLoaded 内に追加:
```js
// Shokusou mode button
var modeShokusou = document.getElementById('mode-shokusou');
if (modeShokusou) {
  modeShokusou.addEventListener('click', function () {
    switchMode('shokusou');
  });
}

// Submode switcher
var submodeSwitcher = document.getElementById('submode-switcher');
if (submodeSwitcher) {
  submodeSwitcher.querySelectorAll('.submode-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      currentSubMode = btn.dataset.submode;
      submodeSwitcher.querySelectorAll('.submode-btn').forEach(function(b) {
        b.classList.toggle('active', b.dataset.submode === currentSubMode);
      });
      updateModeLabels();
      updateHomeStats();
    });
  });
}
```

`switchMode` 関数（もしくはモード切替時のロジック）でサブモードスイッチャーの表示切替:
```js
var submodeSwitcher = document.getElementById('submode-switcher');
if (submodeSwitcher) {
  submodeSwitcher.style.display = (currentMode === 'shokusou') ? '' : 'none';
}
```

- [ ] **Step 7: renderMemorizeGrid で shokusou-card / shokusou-grid クラスを付与**

gridに `.shokusou-grid` クラスを追加、各cardに `.shokusou-card` クラスを追加する分岐:
```js
if (isShokusouMode()) {
  grid.classList.add('shokusou-grid');
  card.classList.add('shokusou-card');
}
```

- [ ] **Step 8: Commit**
```bash
git add app.js
git commit -m "feat: integrate shokusou mode logic into app.js"
```

---

### Task 5: 画像ダウンロードスクリプト

**Files:**
- Create: `download_shokusou.py`

Wikimedia CommonsからWikipedia APIを使って昆虫・植物の画像を取得。

- [ ] **Step 1: download_shokusou.py を作成**

```python
import os, re, time, urllib.request, urllib.parse, json

OUT_DIR = os.path.join(os.path.dirname(__file__), "images", "shokusou")
os.makedirs(OUT_DIR, exist_ok=True)

# All species names mapped to their file IDs
SPECIES = {
    # -- insects --
    "ageha": "アゲハチョウ",
    "kuroageha": "クロアゲハ",
    "karasuageha": "カラスアゲハ",
    # ... (full list from INSECT_DATA + PLANT_DATA ids and search terms)
}

WIKI_API = "https://ja.wikipedia.org/w/api.php"

def get_image_url(title):
    params = {
        "action": "query", "titles": title,
        "prop": "pageimages", "format": "json",
        "pithumbsize": 800, "pilicense": "any"
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumb = page.get("thumbnail", {}).get("source")
        if thumb:
            return thumb
    return None

def download_all():
    for file_id, search_name in SPECIES.items():
        out_path = os.path.join(OUT_DIR, file_id + ".jpg")
        if os.path.exists(out_path):
            print(f"SKIP {file_id}")
            continue
        url = get_image_url(search_name)
        if url:
            urllib.request.urlretrieve(url, out_path)
            print(f"OK   {file_id} <- {search_name}")
        else:
            print(f"FAIL {file_id} ({search_name})")
        time.sleep(0.5)

if __name__ == "__main__":
    download_all()
```

注: SPECIESの完全リストはTask 1のINSECT_DATAとPLANT_DATAの全IDに対応する日本語Wikipedia記事タイトルを網羅する。

- [ ] **Step 2: 実行して画像をダウンロード**

```bash
cd C:/Users/goren/Desktop/Claude_Code/basyo_hou_app
python download_shokusou.py
```

- [ ] **Step 3: ダウンロード失敗した画像を手動確認・再取得**

- [ ] **Step 4: Commit**
```bash
git add download_shokusou.py images/shokusou/
git commit -m "feat: add shokusou image download script and images"
```

---

### Task 6: 動作確認・修正

- [ ] **Step 1: ブラウザでアプリを開いてしょくそう覚えモードを確認**

確認項目:
1. ホーム画面で「しょくそう覚え」ボタンが表示される
2. サブモード「むし→しょくそう」「しょくそう→むし」が切り替わる
3. 暗記フェーズで画像＋名前＋関連種が全て表示される
4. 画像が切り抜かれず全体が見える（object-fit: contain）
5. 回答フェーズで名前＋関連種分の入力欄が動的に表示される
6. 採点が正しく動作する
7. 結果画面で正解数が正しい

- [ ] **Step 2: 問題があれば修正**

- [ ] **Step 3: Commit**
```bash
git add -A
git commit -m "fix: polish shokusou mode integration"
```
