const FISH_DATA = [
  // ========== 固有種（琵琶湖固有種・琵琶湖固有亜種） ==========
  { id: "biwamasu", name: "ビワマス", category: "魚類", image: "images/fish/biwamasu.jpg", tags: ["サケ科", "固有種"] },
  { id: "nigorobuna", name: "ニゴロブナ", category: "魚類", image: "images/fish/nigorobuna.jpg", tags: ["コイ科", "固有種"] },
  { id: "gengoroubuna", name: "ゲンゴロウブナ", category: "魚類", image: "images/fish/gengoroubuna.jpg", tags: ["コイ科", "固有種"] },
  { id: "honmoroko", name: "ホンモロコ", category: "魚類", image: "images/fish/honmoroko.jpg", tags: ["コイ科", "固有種"] },
  { id: "biwahigai", name: "ビワヒガイ", category: "魚類", image: "images/fish/biwahigai.jpg", tags: ["コイ科", "固有種"] },
  { id: "aburahigai", name: "アブラヒガイ", category: "魚類", image: "images/fish/aburahigai.jpg", tags: ["コイ科", "固有種"] },
  { id: "wataka", name: "ワタカ", category: "魚類", image: "images/fish/wataka.jpg", tags: ["コイ科", "固有種"] },
  { id: "sugomoroko", name: "スゴモロコ", category: "魚類", image: "images/fish/sugomoroko.jpg", tags: ["コイ科", "固有種"] },
  { id: "dememoroko", name: "デメモロコ", category: "魚類", image: "images/fish/dememoroko.jpg", tags: ["コイ科", "固有種"] },
  { id: "isaza", name: "イサザ", category: "魚類", image: "images/fish/isaza.jpg", tags: ["ハゼ科", "固有種"] },
  { id: "biwayoshinobori", name: "ビワヨシノボリ", category: "魚類", image: "images/fish/biwayoshinobori.jpg", tags: ["ハゼ科", "固有種"] },
  { id: "biwakooonamazu", name: "ビワコオオナマズ", category: "魚類", image: "images/fish/biwakooonamazu.jpg", tags: ["ナマズ科", "固有種"] },
  { id: "utsusemikajika", name: "ウツセミカジカ", category: "魚類", image: "images/fish/utsusemikajika.jpg", tags: ["カジカ科", "固有種"] },
  { id: "iwatoko_namazu", name: "イワトコナマズ", category: "魚類", image: "images/fish/iwatoko_namazu.jpg", tags: ["ナマズ科", "固有種"] },
  { id: "biwakoogatasu_jishimadojou", name: "ビワコガタスジシマドジョウ", category: "魚類", image: "images/fish/biwakoogatasu_jishimadojou.jpg", tags: ["ドジョウ科", "固有種"] },
  { id: "oogarasugomoroko", name: "オオガタスゴモロコ", category: "魚類", image: "images/fish/oogarasugomoroko.jpg", tags: ["コイ科", "固有種"] },

  // ========== 在来種 — コイ科 ==========
  { id: "koi", name: "コイ", category: "魚類", image: "images/fish/koi.jpg", tags: ["コイ科"] },
  { id: "ginbuna", name: "ギンブナ", category: "魚類", image: "images/fish/ginbuna.jpg", tags: ["コイ科"] },
  { id: "oikawa", name: "オイカワ", category: "魚類", image: "images/fish/oikawa.jpg", tags: ["コイ科"] },
  { id: "kawamutsu", name: "カワムツ", category: "魚類", image: "images/fish/kawamutsu.jpg", tags: ["コイ科"] },
  { id: "numamutsu", name: "ヌマムツ", category: "魚類", image: "images/fish/numamutsu.jpg", tags: ["コイ科"] },
  { id: "ugui", name: "ウグイ", category: "魚類", image: "images/fish/ugui.jpg", tags: ["コイ科"] },
  { id: "tamoroko", name: "タモロコ", category: "魚類", image: "images/fish/tamoroko.jpg", tags: ["コイ科"] },
  { id: "motsugo", name: "モツゴ", category: "魚類", image: "images/fish/motsugo.jpg", tags: ["コイ科"] },
  { id: "hasu", name: "ハス", category: "魚類", image: "images/fish/hasu.jpg", tags: ["コイ科"] },
  { id: "kamatsuka", name: "カマツカ", category: "魚類", image: "images/fish/kamatsuka.jpg", tags: ["コイ科"] },
  { id: "tsuchifuki", name: "ツチフキ", category: "魚類", image: "images/fish/tsuchifuki.jpg", tags: ["コイ科"] },
  { id: "zezera", name: "ゼゼラ", category: "魚類", image: "images/fish/zezera.jpg", tags: ["コイ科"] },
  { id: "mugitsuku", name: "ムギツク", category: "魚類", image: "images/fish/mugitsuku.jpg", tags: ["コイ科"] },
  { id: "higai", name: "ヒガイ", category: "魚類", image: "images/fish/higai.jpg", tags: ["コイ科"] },
  { id: "itomoroko", name: "イトモロコ", category: "魚類", image: "images/fish/itomoroko.jpg", tags: ["コイ科"] },
  { id: "nagabuna", name: "ナガブナ", category: "魚類", image: "images/fish/nagabuna.jpg", tags: ["コイ科"] },

  // ========== 在来種 — タナゴ類（コイ科） ==========
  { id: "tanago", name: "タナゴ", category: "魚類", image: "images/fish/tanago.jpg", tags: ["コイ科", "タナゴ類"] },
  { id: "kanehira", name: "カネヒラ", category: "魚類", image: "images/fish/kanehira.jpg", tags: ["コイ科", "タナゴ類"] },
  { id: "ichimonjitanago", name: "イチモンジタナゴ", category: "魚類", image: "images/fish/ichimonjitanago.jpg", tags: ["コイ科", "タナゴ類"] },
  { id: "yaritanago", name: "ヤリタナゴ", category: "魚類", image: "images/fish/yaritanago.jpg", tags: ["コイ科", "タナゴ類"] },
  { id: "shirotanago", name: "シロヒレタビラ", category: "魚類", image: "images/fish/shirotanago.jpg", tags: ["コイ科", "タナゴ類"] },

  // ========== 在来種 — アユ科 ==========
  { id: "ayu", name: "アユ", category: "魚類", image: "images/fish/ayu.jpg", tags: ["キュウリウオ科"] },

  // ========== 在来種 — ナマズ科 ==========
  { id: "namazu", name: "ナマズ", category: "魚類", image: "images/fish/namazu.jpg", tags: ["ナマズ科"] },
  { id: "gigi", name: "ギギ", category: "魚類", image: "images/fish/gigi.jpg", tags: ["ギギ科"] },
  { id: "akaza", name: "アカザ", category: "魚類", image: "images/fish/akaza.jpg", tags: ["アカザ科"] },

  // ========== 在来種 — ドジョウ科 ==========
  { id: "dojou", name: "ドジョウ", category: "魚類", image: "images/fish/dojou.jpg", tags: ["ドジョウ科"] },
  { id: "shimadojou", name: "シマドジョウ", category: "魚類", image: "images/fish/shimadojou.jpg", tags: ["ドジョウ科"] },
  { id: "ajimedojou", name: "アジメドジョウ", category: "魚類", image: "images/fish/ajimedojou.jpg", tags: ["ドジョウ科"] },
  { id: "hotokodojou", name: "ホトケドジョウ", category: "魚類", image: "images/fish/hotokodojou.jpg", tags: ["ドジョウ科"] },
  { id: "nagashimadojou", name: "ナガシマドジョウ", category: "魚類", image: "images/fish/nagashimadojou.jpg", tags: ["ドジョウ科"] },

  // ========== 在来種 — ハゼ科 ==========
  { id: "yoshinobori", name: "ヨシノボリ", category: "魚類", image: "images/fish/yoshinobori.jpg", tags: ["ハゼ科"] },
  { id: "kawayoshinobori", name: "カワヨシノボリ", category: "魚類", image: "images/fish/kawayoshinobori.jpg", tags: ["ハゼ科"] },
  { id: "touyoshinobori", name: "トウヨシノボリ", category: "魚類", image: "images/fish/touyoshinobori.jpg", tags: ["ハゼ科"] },
  { id: "ukigori", name: "ウキゴリ", category: "魚類", image: "images/fish/ukigori.jpg", tags: ["ハゼ科"] },
  { id: "sumiukigori", name: "スミウキゴリ", category: "魚類", image: "images/fish/sumiukigori.jpg", tags: ["ハゼ科"] },
  { id: "donko", name: "ドンコ", category: "魚類", image: "images/fish/donko.jpg", tags: ["ドンコ科"] },
  { id: "numachichibu", name: "ヌマチチブ", category: "魚類", image: "images/fish/numachichibu.jpg", tags: ["ハゼ科"] },

  // ========== 在来種 — カジカ科 ==========
  { id: "kajika", name: "カジカ", category: "魚類", image: "images/fish/kajika.jpg", tags: ["カジカ科"] },

  // ========== 在来種 — ウナギ科 ==========
  { id: "unagi", name: "ニホンウナギ", category: "魚類", image: "images/fish/unagi.jpg", tags: ["ウナギ科"] },

  // ========== 在来種 — メダカ科 ==========
  { id: "medaka", name: "メダカ", category: "魚類", image: "images/fish/medaka.jpg", tags: ["メダカ科"] },

  // ========== 在来種 — サケ科 ==========
  { id: "amago", name: "アマゴ", category: "魚類", image: "images/fish/amago.jpg", tags: ["サケ科"] },
  { id: "iwana", name: "イワナ", category: "魚類", image: "images/fish/iwana.jpg", tags: ["サケ科"] },

  // ========== 在来種 — スズキ科・その他 ==========
  { id: "ooyamato_shimadojou", name: "オオヤマトシマドジョウ", category: "魚類", image: "images/fish/ooyamato_shimadojou.jpg", tags: ["ドジョウ科"] },
  { id: "sunayatsume", name: "スナヤツメ", category: "魚類", image: "images/fish/sunayatsume.jpg", tags: ["ヤツメウナギ科"] },
  { id: "kawayatsume", name: "カワヤツメ", category: "魚類", image: "images/fish/kawayatsume.jpg", tags: ["ヤツメウナギ科"] },
  { id: "tomiyo", name: "トミヨ", category: "魚類", image: "images/fish/tomiyo.jpg", tags: ["トゲウオ科"] },
  { id: "itoyo", name: "イトヨ", category: "魚類", image: "images/fish/itoyo.jpg", tags: ["トゲウオ科"] },
  { id: "hariyo", name: "ハリヨ", category: "魚類", image: "images/fish/hariyo.jpg", tags: ["トゲウオ科"] },
  { id: "sayori", name: "サヨリ", category: "魚類", image: "images/fish/sayori.jpg", tags: ["サヨリ科"] },
  { id: "wakasagi", name: "ワカサギ", category: "魚類", image: "images/fish/wakasagi.jpg", tags: ["キュウリウオ科"] },
  { id: "hiuo", name: "ヒウオ", category: "魚類", image: "images/fish/hiuo.jpg", tags: ["キュウリウオ科"] },
  { id: "shirauo", name: "シラウオ", category: "魚類", image: "images/fish/shirauo.jpg", tags: ["シラウオ科"] },
  { id: "yoshinobori_ruisenbo", name: "ルリヨシノボリ", category: "魚類", image: "images/fish/yoshinobori_ruisenbo.jpg", tags: ["ハゼ科"] },
  { id: "bora", name: "ボラ", category: "魚類", image: "images/fish/bora.jpg", tags: ["ボラ科"] },

  // ========== 外来種（琵琶湖に侵入・放流された種） ==========
  { id: "ookuchibasu", name: "オオクチバス", category: "魚類", image: "images/fish/ookuchibasu.jpg", tags: ["サンフィッシュ科", "外来種"] },
  { id: "kokuchibasu", name: "コクチバス", category: "魚類", image: "images/fish/kokuchibasu.jpg", tags: ["サンフィッシュ科", "外来種"] },
  { id: "buruugiru", name: "ブルーギル", category: "魚類", image: "images/fish/buruugiru.jpg", tags: ["サンフィッシュ科", "外来種"] },
  { id: "channerukyattofisshu", name: "チャネルキャットフィッシュ", category: "魚類", image: "images/fish/channerukyattofisshu.jpg", tags: ["アメリカナマズ科", "外来種"] },
  { id: "tairikubaratanago", name: "タイリクバラタナゴ", category: "魚類", image: "images/fish/tairikubaratanago.jpg", tags: ["コイ科", "外来種"] },
  { id: "kamuruchii", name: "カムルチー", category: "魚類", image: "images/fish/kamuruchii.jpg", tags: ["タイワンドジョウ科", "外来種"] },
  { id: "nijimasu", name: "ニジマス", category: "魚類", image: "images/fish/nijimasu.jpg", tags: ["サケ科", "外来種"] },
  { id: "ootanago", name: "オオタナゴ", category: "魚類", image: "images/fish/ootanago.jpg", tags: ["コイ科", "外来種"] },
  { id: "sougyou", name: "ソウギョ", category: "魚類", image: "images/fish/sougyou.jpg", tags: ["コイ科", "外来種"] },
  { id: "rengyou", name: "レンギョ", category: "魚類", image: "images/fish/rengyou.jpg", tags: ["コイ科", "外来種"] },
  { id: "hakuren", name: "ハクレン", category: "魚類", image: "images/fish/hakuren.jpg", tags: ["コイ科", "外来種"] },
  { id: "kokuren", name: "コクレン", category: "魚類", image: "images/fish/kokuren.jpg", tags: ["コイ科", "外来種"] },
  { id: "taiwandojou", name: "タイワンドジョウ", category: "魚類", image: "images/fish/taiwandojou.jpg", tags: ["タイワンドジョウ科", "外来種"] },
  { id: "numagarei", name: "ヌマガレイ", category: "魚類", image: "images/fish/numagarei.jpg", tags: ["カレイ科", "外来種"] },
  { id: "peherey", name: "ペヘレイ", category: "魚類", image: "images/fish/peherey.jpg", tags: ["アテリノプス科", "外来種"] },
];
