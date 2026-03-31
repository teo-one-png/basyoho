"""
滋賀県全鳥類リストの鳴き声をGBIF経由でダウンロード。
既にダウンロード済みのものはスキップ。
"""

import json
import os
import time
import urllib.request
import urllib.parse

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
XC_DATASET_KEY = "b1047888-ae52-4179-9dd5-5448ea342a24"

# 滋賀県全鳥類リスト（学名マッピング）
ALL_BIRDS = [
    # === カモ目 ===
    {"id": "hakugan", "name": "ハクガン", "scientific": "Anser caerulescens"},
    {"id": "haiirogan", "name": "ハイイロガン", "scientific": "Anser anser"},
    {"id": "sakatsuragen", "name": "サカツラガン", "scientific": "Anser cygnoid"},
    {"id": "magan", "name": "マガン", "scientific": "Anser albifrons"},
    {"id": "karigane", "name": "カリガネ", "scientific": "Anser erythropus"},
    {"id": "oohishikui", "name": "オオヒシクイ", "scientific": "Anser fabalis middendorffii"},
    {"id": "hishikui", "name": "ヒシクイ", "scientific": "Anser fabalis"},
    {"id": "kokugan", "name": "コクガン", "scientific": "Branta bernicla"},
    {"id": "shijuukaraganmo", "name": "シジュウカラガン", "scientific": "Branta hutchinsii"},
    {"id": "kobuhakuchou", "name": "コブハクチョウ", "scientific": "Cygnus olor"},
    {"id": "kohakuchou", "name": "コハクチョウ", "scientific": "Cygnus columbianus"},
    {"id": "oohakuchou", "name": "オオハクチョウ", "scientific": "Cygnus cygnus"},
    {"id": "akatsukushigamo", "name": "アカツクシガモ", "scientific": "Tadorna ferruginea"},
    {"id": "tsukushigamo", "name": "ツクシガモ", "scientific": "Tadorna tadorna"},
    {"id": "oshidori", "name": "オシドリ", "scientific": "Aix galericulata"},
    {"id": "tomoegamo", "name": "トモエガモ", "scientific": "Sibirionetta formosa"},
    {"id": "shimaji", "name": "シマアジ", "scientific": "Spatula querquedula"},
    {"id": "hashibirogamo", "name": "ハシビロガモ", "scientific": "Spatula clypeata"},
    {"id": "okayoshigamo", "name": "オカヨシガモ", "scientific": "Mareca strepera"},
    {"id": "yoshigamo", "name": "ヨシガモ", "scientific": "Mareca falcata"},
    {"id": "hidorigamo", "name": "ヒドリガモ", "scientific": "Mareca penelope"},
    {"id": "amerikahidori", "name": "アメリカヒドリ", "scientific": "Mareca americana"},
    # karugamo already exists
    {"id": "magamo", "name": "マガモ", "scientific": "Anas platyrhynchos"},
    {"id": "onagagamo", "name": "オナガガモ", "scientific": "Anas acuta"},
    {"id": "kogamo", "name": "コガモ", "scientific": "Anas crecca"},
    {"id": "akahashihajiro", "name": "アカハシハジロ", "scientific": "Netta rufina"},
    {"id": "oohoshihajiro", "name": "オオホシハジロ", "scientific": "Aythya ferina"},
    {"id": "hoshihajiro", "name": "ホシハジロ", "scientific": "Aythya ferina"},
    {"id": "kubiwakinkuro", "name": "クビワキンクロ", "scientific": "Aythya collaris"},
    {"id": "mejirogamo", "name": "メジロガモ", "scientific": "Aythya nyroca"},
    {"id": "akahajiro", "name": "アカハジロ", "scientific": "Aythya baeri"},
    {"id": "kinkurohajiro", "name": "キンクロハジロ", "scientific": "Aythya fuligula"},
    {"id": "suzugamo", "name": "スズガモ", "scientific": "Aythya marila"},
    {"id": "kosuzugamo", "name": "コスズガモ", "scientific": "Aythya affinis"},
    {"id": "shinorigamo", "name": "シノリガモ", "scientific": "Histrionicus histrionicus"},
    {"id": "biroodokinkuro", "name": "ビロードキンクロ", "scientific": "Melanitta fusca"},
    {"id": "kurogamo", "name": "クロガモ", "scientific": "Melanitta americana"},
    {"id": "koorigamo", "name": "コオリガモ", "scientific": "Clangula hyemalis"},
    {"id": "hoojirogamo", "name": "ホオジロガモ", "scientific": "Bucephala clangula"},
    {"id": "mikoaisa", "name": "ミコアイサ", "scientific": "Mergellus albellus"},
    {"id": "kawaaisa", "name": "カワアイサ", "scientific": "Mergus merganser"},
    {"id": "umiaisa", "name": "ウミアイサ", "scientific": "Mergus serrator"},
    {"id": "kouraiaisa", "name": "コウライアイサ", "scientific": "Mergus squamatus"},
    # === キジ目 ===
    {"id": "ezoraichou", "name": "エゾライチョウ", "scientific": "Tetrastes bonasia"},
    {"id": "raichou", "name": "ライチョウ", "scientific": "Lagopus muta"},
    {"id": "yamadori", "name": "ヤマドリ", "scientific": "Syrmaticus soemmerringii"},
    # kiji, kojukei already exist
    {"id": "uzura", "name": "ウズラ", "scientific": "Coturnix japonica"},
    # === ハト目 ===
    {"id": "kawarabato", "name": "カワラバト", "scientific": "Columba livia"},
    # kijibato already exists
    {"id": "aobato", "name": "アオバト", "scientific": "Treron sieboldii"},
    # === サケイ目 ===
    {"id": "sakei", "name": "サケイ", "scientific": "Syrrhaptes paradoxus"},
    # === カッコウ目 ===
    # juuichi, kakkou, tsutsudori already exist
    {"id": "segurokaxtukoo", "name": "セグロカッコウ", "scientific": "Cuculus micropterus"},
    # === ヨタカ目 ===
    {"id": "yotaka", "name": "ヨタカ", "scientific": "Caprimulgus indicus"},
    # === アマツバメ目 ===
    {"id": "harioamatsubame", "name": "ハリオアマツバメ", "scientific": "Hirundapus caudacutus"},
    {"id": "amatsubame", "name": "アマツバメ", "scientific": "Apus pacificus"},
    {"id": "himeatsubame", "name": "ヒメアマツバメ", "scientific": "Apus nipalensis"},
    # === ツル目 ===
    {"id": "kuina", "name": "クイナ", "scientific": "Rallus indicus"},
    # ban, ooban already exist
    {"id": "tsurukuina", "name": "ツルクイナ", "scientific": "Gallicrex cinerea"},
    {"id": "shiroharakuina", "name": "シロハラクイナ", "scientific": "Amaurornis phoenicurus"},
    {"id": "hikuina", "name": "ヒクイナ", "scientific": "Zapornia fusca"},
    {"id": "himekuina", "name": "ヒメクイナ", "scientific": "Zapornia pusilla"},
    {"id": "shimakuina", "name": "シマクイナ", "scientific": "Coturnicops exquisitus"},
    {"id": "kanadaduru", "name": "カナダヅル", "scientific": "Antigone canadensis"},
    {"id": "manaduru", "name": "マナヅル", "scientific": "Grus vipio"},
    {"id": "kuroduru", "name": "クロヅル", "scientific": "Grus grus"},
    {"id": "nabeduru", "name": "ナベヅル", "scientific": "Grus monacha"},
    # === チドリ目 ===
    {"id": "seitakashigi", "name": "セイタカシギ", "scientific": "Himantopus himantopus"},
    {"id": "sorihashiseitakashigi", "name": "ソリハシセイタカシギ", "scientific": "Recurvirostra avosetta"},
    {"id": "miyakodori", "name": "ミヤコドリ", "scientific": "Haematopus ostralegus"},
    {"id": "daizen", "name": "ダイゼン", "scientific": "Pluvialis squatarola"},
    {"id": "munaguro", "name": "ムナグロ", "scientific": "Pluvialis fulva"},
    {"id": "kochidori", "name": "コチドリ", "scientific": "Charadrius dubius"},
    {"id": "ikaruchidori", "name": "イカルチドリ", "scientific": "Charadrius placidus"},
    {"id": "tageri", "name": "タゲリ", "scientific": "Vanellus vanellus"},
    # keri already exists
    {"id": "medaichidori", "name": "メダイチドリ", "scientific": "Charadrius mongolus"},
    {"id": "shirochidori", "name": "シロチドリ", "scientific": "Charadrius alexandrinus"},
    {"id": "tamashigi", "name": "タマシギ", "scientific": "Rostratula benghalensis"},
    {"id": "renkaku", "name": "レンカク", "scientific": "Hydrophasianus chirurgus"},
    {"id": "chuushakushigi", "name": "チュウシャクシギ", "scientific": "Numenius phaeopus"},
    {"id": "koshakushigi", "name": "コシャクシギ", "scientific": "Numenius minutus"},
    {"id": "daishakushigi", "name": "ダイシャクシギ", "scientific": "Numenius arquata"},
    {"id": "hourokushigi", "name": "ホウロクシギ", "scientific": "Numenius madagascariensis"},
    {"id": "oosorihashishigi", "name": "オオソリハシシギ", "scientific": "Limosa lapponica"},
    {"id": "oguroshigi", "name": "オグロシギ", "scientific": "Limosa limosa"},
    {"id": "oohashishigi", "name": "オオハシシギ", "scientific": "Limnodromus scolopaceus"},
    {"id": "yamashigi", "name": "ヤマシギ", "scientific": "Scolopax rusticola"},
    {"id": "aoshigi", "name": "アオシギ", "scientific": "Gallinago solitaria"},
    {"id": "oojishigi", "name": "オオジシギ", "scientific": "Gallinago hardwickii"},
    {"id": "tashigi", "name": "タシギ", "scientific": "Gallinago gallinago"},
    {"id": "akaerihireashishigi", "name": "アカエリヒレアシシギ", "scientific": "Phalaropus lobatus"},
    {"id": "isoshigi", "name": "イソシギ", "scientific": "Actitis hypoleucos"},
    {"id": "kusashigi", "name": "クサシギ", "scientific": "Tringa ochropus"},
    {"id": "kiashishigi", "name": "キアシシギ", "scientific": "Tringa brevipes"},
    {"id": "koaoashishigi", "name": "コアオアシシギ", "scientific": "Tringa stagnatilis"},
    {"id": "akaashishigi", "name": "アカアシシギ", "scientific": "Tringa totanus"},
    {"id": "tsurushigi", "name": "ツルシギ", "scientific": "Tringa erythropus"},
    {"id": "aoashishigi", "name": "アオアシシギ", "scientific": "Tringa nebularia"},
    {"id": "kyoujoushigi", "name": "キョウジョシギ", "scientific": "Arenaria interpres"},
    {"id": "obashigi", "name": "オバシギ", "scientific": "Calidris tenuirostris"},
    {"id": "koobashigi", "name": "コオバシギ", "scientific": "Calidris canutus"},
    {"id": "erimakishigi", "name": "エリマキシギ", "scientific": "Calidris pugnax"},
    {"id": "kiriai", "name": "キリアイ", "scientific": "Calidris falcinellus"},
    {"id": "uzurashigi", "name": "ウズラシギ", "scientific": "Calidris acuminata"},
    {"id": "saruhamashigi", "name": "サルハマシギ", "scientific": "Calidris ferruginea"},
    {"id": "ojirotounen", "name": "オジロトウネン", "scientific": "Calidris temminckii"},
    {"id": "hibarishigi", "name": "ヒバリシギ", "scientific": "Calidris subminuta"},
    {"id": "tounen", "name": "トウネン", "scientific": "Calidris ruficollis"},
    {"id": "herashigi", "name": "ヘラシギ", "scientific": "Calidris pygmaea"},
    {"id": "miyubishigi", "name": "ミユビシギ", "scientific": "Calidris alba"},
    {"id": "hamashigi", "name": "ハマシギ", "scientific": "Calidris alpina"},
    {"id": "tsubamechidori", "name": "ツバメチドリ", "scientific": "Glareola maldivarum"},
    {"id": "yurikamome", "name": "ユリカモメ", "scientific": "Chroicocephalus ridibundus"},
    {"id": "umineko", "name": "ウミネコ", "scientific": "Larus crassirostris"},
    {"id": "kamome", "name": "カモメ", "scientific": "Larus canus"},
    {"id": "segurokamome", "name": "セグロカモメ", "scientific": "Larus argentatus"},
    {"id": "oosegurokamome", "name": "オオセグロカモメ", "scientific": "Larus schistisagus"},
    {"id": "koajisashi", "name": "コアジサシ", "scientific": "Sternula albifrons"},
    {"id": "kuroharaajisashi", "name": "クロハラアジサシ", "scientific": "Chlidonias hybrida"},
    {"id": "ajisashi", "name": "アジサシ", "scientific": "Sterna hirundo"},
    # === カイツブリ目 ===
    # kaitsuburi already exists
    {"id": "hajirokaitsiburi", "name": "ハジロカイツブリ", "scientific": "Podiceps nigricollis"},
    {"id": "akaerikaitsiburi", "name": "アカエリカイツブリ", "scientific": "Podiceps grisegena"},
    {"id": "kanmurikaitsiburi", "name": "カンムリカイツブリ", "scientific": "Podiceps cristatus"},
    {"id": "mimikaitsiburi", "name": "ミミカイツブリ", "scientific": "Podiceps auritus"},
    # === アビ目 ===
    {"id": "abi", "name": "アビ", "scientific": "Gavia stellata"},
    {"id": "ooham", "name": "オオハム", "scientific": "Gavia arctica"},
    # === ミズナギドリ目 ===
    {"id": "oomizunagidori", "name": "オオミズナギドリ", "scientific": "Calonectris leucomelas"},
    # === コウノトリ目 ===
    {"id": "kounotori", "name": "コウノトリ", "scientific": "Ciconia boyciana"},
    # === カツオドリ目 ===
    {"id": "himeu", "name": "ヒメウ", "scientific": "Urile pelagicus"},
    {"id": "kawau", "name": "カワウ", "scientific": "Phalacrocorax carbo"},
    {"id": "umiu", "name": "ウミウ", "scientific": "Phalacrocorax capillatus"},
    # === ペリカン目 ===
    {"id": "herasagi", "name": "ヘラサギ", "scientific": "Platalea leucorodia"},
    {"id": "kurotsurahersagi", "name": "クロツラヘラサギ", "scientific": "Platalea minor"},
    {"id": "sankanogoi", "name": "サンカノゴイ", "scientific": "Botaurus stellaris"},
    {"id": "ooyoshigoi", "name": "オオヨシゴイ", "scientific": "Ixobrychus eurhythmus"},
    {"id": "yoshigoi", "name": "ヨシゴイ", "scientific": "Ixobrychus sinensis"},
    {"id": "goisagi", "name": "ゴイサギ", "scientific": "Nycticorax nycticorax"},
    {"id": "sasagoi", "name": "ササゴイ", "scientific": "Butorides striata"},
    # aosagi already exists
    {"id": "daisagi", "name": "ダイサギ", "scientific": "Ardea alba"},
    {"id": "chuusagi", "name": "チュウサギ", "scientific": "Ardea intermedia"},
    {"id": "kosagi", "name": "コサギ", "scientific": "Egretta garzetta"},
    {"id": "kurosagi", "name": "クロサギ", "scientific": "Egretta sacra"},
    {"id": "akagashirasagi", "name": "アカガシラサギ", "scientific": "Ardeola bacchus"},
    {"id": "amasagi", "name": "アマサギ", "scientific": "Bubulcus ibis"},
    {"id": "murasakisagi", "name": "ムラサキサギ", "scientific": "Ardea purpurea"},
    # === タカ目 ===
    {"id": "misago", "name": "ミサゴ", "scientific": "Pandion haliaetus"},
    # hachikuma, kumataka already in bird data
    {"id": "inuwashi", "name": "イヌワシ", "scientific": "Aquila chrysaetos"},
    {"id": "tsumi", "name": "ツミ", "scientific": "Accipiter gularis"},
    {"id": "akaharadaka", "name": "アカハラダカ", "scientific": "Accipiter soloensis"},
    {"id": "haitaka", "name": "ハイタカ", "scientific": "Accipiter nisus"},
    {"id": "ootaka", "name": "オオタカ", "scientific": "Accipiter gentilis"},
    {"id": "chuuhi", "name": "チュウヒ", "scientific": "Circus spilonotus"},
    {"id": "haiirochuuhi", "name": "ハイイロチュウヒ", "scientific": "Circus cyaneus"},
    # tobi already exists
    {"id": "ojirowashi", "name": "オジロワシ", "scientific": "Haliaeetus albicilla"},
    {"id": "oowashi", "name": "オオワシ", "scientific": "Haliaeetus pelagicus"},
    {"id": "sashiba", "name": "サシバ", "scientific": "Butastur indicus"},
    {"id": "keashinosuri", "name": "ケアシノスリ", "scientific": "Buteo lagopus"},
    {"id": "nosuri", "name": "ノスリ", "scientific": "Buteo japonicus"},
    # === フクロウ目 ===
    {"id": "ookonohazuku", "name": "オオコノハズク", "scientific": "Otus lempiji"},
    {"id": "konohazuku", "name": "コノハズク", "scientific": "Otus scops"},
    # fukurou already exists
    {"id": "torafuzuku", "name": "トラフズク", "scientific": "Asio otus"},
    {"id": "komimizuku", "name": "コミミズク", "scientific": "Asio flammeus"},
    # aobazuku already exists
    # === ブッポウソウ目 ===
    {"id": "yatsugashira", "name": "ヤツガシラ", "scientific": "Upupa epops"},
    # kawasemi, akashoubin already exist
    {"id": "yamashoubin", "name": "ヤマショウビン", "scientific": "Halcyon pileata"},
    {"id": "yamasemi", "name": "ヤマセミ", "scientific": "Megaceryle lugubris"},
    {"id": "buppousou", "name": "ブッポウソウ", "scientific": "Eurystomus orientalis"},
    # === キツツキ目 ===
    {"id": "arisui", "name": "アリスイ", "scientific": "Jynx torquilla"},
    # kogera, akagera, aogera already exist
    {"id": "ooakagera", "name": "オオアカゲラ", "scientific": "Dendrocopos leucotos"},
    {"id": "koakagera", "name": "コアカゲラ", "scientific": "Dryobates minor"},
    {"id": "kumagera", "name": "クマゲラ", "scientific": "Dryocopus martius"},
    # === ハヤブサ目 ===
    # chougenbou already exists
    {"id": "kochougenbou", "name": "コチョウゲンボウ", "scientific": "Falco columbarius"},
    {"id": "chigohayabusa", "name": "チゴハヤブサ", "scientific": "Falco subbuteo"},
    {"id": "hayabusa", "name": "ハヤブサ", "scientific": "Falco peregrinus"},
    # === スズメ目（前半） ===
    {"id": "yairochou", "name": "ヤイロチョウ", "scientific": "Pitta nympha"},
    {"id": "sanshoukui", "name": "サンショウクイ", "scientific": "Pericrocotus divaricatus"},
    {"id": "kouraiuguisu", "name": "コウライウグイス", "scientific": "Oriolus chinensis"},
    {"id": "ouchuu", "name": "オウチュウ", "scientific": "Dicrurus macrocercus"},
    # sankouchou already exists
    {"id": "chigomozu", "name": "チゴモズ", "scientific": "Lanius tigrinus"},
    # mozu already exists
    {"id": "akamozu", "name": "アカモズ", "scientific": "Lanius cristatus"},
    {"id": "oomozu", "name": "オオモズ", "scientific": "Lanius excubitor"},
    # kakesu already exists
    {"id": "onaga", "name": "オナガ", "scientific": "Cyanopica cyanus"},
    {"id": "kasasagi", "name": "カササギ", "scientific": "Pica pica"},
    {"id": "hoshigarasu", "name": "ホシガラス", "scientific": "Nucifraga caryocatactes"},
    {"id": "kokumarugarasu", "name": "コクマルガラス", "scientific": "Corvus dauuricus"},
    {"id": "miyamagarasu", "name": "ミヤマガラス", "scientific": "Corvus frugilegus"},
    # hashibosogarasu, hashibutogarasu already exist
    # higara, yamagara, kogara, shijuukara already exist
    {"id": "tsurisugara", "name": "ツリスガラ", "scientific": "Remiz pendulinus"},
    # hibari already exists
    {"id": "kohibari", "name": "コヒバリ", "scientific": "Calandrella brachydactyla"},
    {"id": "sekka", "name": "セッカ", "scientific": "Cisticola juncidis"},
    {"id": "koyoshikiri", "name": "コヨシキリ", "scientific": "Acrocephalus bistrigiceps"},
    # ooyoshikiri already exists
    {"id": "ezosennyu", "name": "エゾセンニュウ", "scientific": "Helopsaltes fasciolatus"},
    {"id": "oosekka", "name": "オオセッカ", "scientific": "Locustella pryeri"},
    {"id": "shimasennyu", "name": "シマセンニュウ", "scientific": "Locustella ochotensis"},
    {"id": "makinosennyu", "name": "マキノセンニュウ", "scientific": "Locustella lanceolata"},
    {"id": "shoudoutsubame", "name": "ショウドウツバメ", "scientific": "Riparia riparia"},
    # tsubame already exists
    {"id": "iwatsubame", "name": "イワツバメ", "scientific": "Delichon dasypus"},
    {"id": "koshiakatsubame", "name": "コシアカツバメ", "scientific": "Cecropis daurica"},
    # hiyodori already exists
    {"id": "kimayumushikui", "name": "キマユムシクイ", "scientific": "Phylloscopus inornatus"},
    {"id": "mujisekka", "name": "ムジセッカ", "scientific": "Phylloscopus fuscatus"},
    # sendaimushikui already exists
    {"id": "ezomushikui", "name": "エゾムシクイ", "scientific": "Phylloscopus borealoides"},
    {"id": "mebosomushikui", "name": "メボソムシクイ", "scientific": "Phylloscopus xanthodryas"},
    {"id": "oomushikui", "name": "オオムシクイ", "scientific": "Phylloscopus examinandus"},
    # yabusame already exists
    # uguisu already exists
    # enaga already exists
    # mejiro already exists
    {"id": "soushichou", "name": "ソウシチョウ", "scientific": "Leiothrix lutea"},
    {"id": "gabichou", "name": "ガビチョウ", "scientific": "Garrulax canorus"},
    {"id": "kikuitadaki", "name": "キクイタダキ", "scientific": "Regulus regulus"},
    # gojuukara already exists
    {"id": "kibashiri", "name": "キバシリ", "scientific": "Certhia familiaris"},
    # misosazai, kawagarasu already exist
    # === スズメ目（後半） ===
    {"id": "hoshimukudori", "name": "ホシムクドリ", "scientific": "Sturnus vulgaris"},
    {"id": "komukudori", "name": "コムクドリ", "scientific": "Agropsar philippensis"},
    # mukudori already exists
    {"id": "toratsugumi", "name": "トラツグミ", "scientific": "Zoothera dauma"},
    {"id": "mamijiro", "name": "マミジロ", "scientific": "Turdus sibiricus"},
    # kurotsugumi already exists
    # shirohara already exists
    {"id": "mamichajinaishirohara", "name": "マミチャジナイ", "scientific": "Turdus obscurus"},
    {"id": "akahara", "name": "アカハラ", "scientific": "Turdus chrysolaus"},
    # tsugumi already exists
    {"id": "ezobitaki", "name": "エゾビタキ", "scientific": "Muscicapa griseisticta"},
    {"id": "samebitaki", "name": "サメビタキ", "scientific": "Muscicapa sibirica"},
    {"id": "kosamebitaki", "name": "コサメビタキ", "scientific": "Muscicapa dauurica"},
    # ooruri already exists
    # komadori, koruri already exist
    {"id": "nogoma", "name": "ノゴマ", "scientific": "Calliope calliope"},
    # ruribitaki already exists
    # kibitaki already exists
    {"id": "mugimaki", "name": "ムギマキ", "scientific": "Ficedula mugimaki"},
    # joubitaki already exists
    # isohiyodori already exists
    {"id": "nobitaki", "name": "ノビタキ", "scientific": "Saxicola torquatus"},
    {"id": "kirenjaku", "name": "キレンジャク", "scientific": "Bombycilla garrulus"},
    {"id": "hirenjaku", "name": "ヒレンジャク", "scientific": "Bombycilla japonica"},
    {"id": "iwabibari", "name": "イワヒバリ", "scientific": "Prunella collaris"},
    {"id": "kayakuguri", "name": "カヤクグリ", "scientific": "Prunella rubida"},
    {"id": "nyuunaisuzume", "name": "ニュウナイスズメ", "scientific": "Passer rutilans"},
    # suzume already exists
    # kisekirei, segurosekirei, hakusekirei already exist
    {"id": "tsumesekirei", "name": "ツメナガセキレイ", "scientific": "Motacilla flava"},
    {"id": "binzui", "name": "ビンズイ", "scientific": "Anthus hodgsoni"},
    {"id": "tahibari", "name": "タヒバリ", "scientific": "Anthus spinoletta"},
    {"id": "atori", "name": "アトリ", "scientific": "Fringilla montifringilla"},
    {"id": "shime", "name": "シメ", "scientific": "Coccothraustes coccothraustes"},
    {"id": "koikaru", "name": "コイカル", "scientific": "Eophona migratoria"},
    # ikaru already exists
    # benimasiko already exists
    {"id": "oomasiko", "name": "オオマシコ", "scientific": "Carpodacus roseus"},
    # uso already exists
    {"id": "hagimasiko", "name": "ハギマシコ", "scientific": "Leucosticte arctoa"},
    {"id": "kawarahiwa", "name": "カワラヒワ", "scientific": "Chloris sinica"},
    {"id": "benihiwa", "name": "ベニヒワ", "scientific": "Acanthis flammea"},
    {"id": "isuka", "name": "イスカ", "scientific": "Loxia curvirostra"},
    {"id": "mahiwa", "name": "マヒワ", "scientific": "Spinus spinus"},
    {"id": "hooaka", "name": "ホオアカ", "scientific": "Emberiza fucata"},
    # hoojiro already exists
    # miyamahoojiro already exists
    {"id": "kojurin", "name": "コジュリン", "scientific": "Emberiza yessoensis"},
    {"id": "oojurin", "name": "オオジュリン", "scientific": "Emberiza schoeniclus"},
    # kashiradaka already exists
    {"id": "nojiko", "name": "ノジコ", "scientific": "Emberiza sulphurata"},
    # aoji already exists
    {"id": "kuroji", "name": "クロジ", "scientific": "Emberiza variabilis"},
]

CALL_TYPES = [
    {"suffix": "saezuri", "label": "さえずり", "keywords": ["song", "SONG", "sing"]},
    {"suffix": "jinaki", "label": "地鳴き", "keywords": ["call", "CALL", "alarm", "contact"]},
]


def search_gbif(scientific_name, limit=50):
    results = []
    for dataset_key in [XC_DATASET_KEY, None]:
        params = {"scientificName": scientific_name, "mediaType": "Sound", "limit": limit}
        if dataset_key:
            params["datasetKey"] = dataset_key
        url = f"https://api.gbif.org/v1/occurrence/search?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BirdCallApp/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results.extend(data.get("results", []))
        except Exception as e:
            pass
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
            matched = fallback
            if not fallback:
                for kw in keywords:
                    if kw.upper() in url_upper or kw.upper() in desc or kw.upper() in remarks:
                        matched = True
                        break
            if matched:
                is_mp3 = url.lower().endswith(".mp3")
                candidates.append({
                    "url": url, "is_mp3": is_mp3,
                    "recorder": r.get("recordedBy", "Unknown"),
                    "xc_id": url.split("XC")[-1].split("-")[0].split(".")[0] if "XC" in url else "",
                    "license": r.get("license", "CC BY-NC 4.0"),
                    "country": r.get("country", ""),
                })
    candidates.sort(key=lambda c: (0 if c["country"] == "Japan" else 1, 0 if c["is_mp3"] else 1))
    return candidates[0] if candidates else None


def download_file(url, output_path):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"    DL error: {e}")
        return False


def main():
    credits_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nakigoe_credits.json")
    credits = {}
    if os.path.exists(credits_path):
        with open(credits_path, "r", encoding="utf-8") as f:
            credits = json.load(f)

    FFMPEG = r"C:\Users\goren\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"

    failed = []
    downloaded = 0
    skipped = 0

    for bird in ALL_BIRDS:
        # Check if both already exist
        has_all = True
        for ct in CALL_TYPES:
            key = f"{bird['id']}_{ct['suffix']}"
            existing = any(
                os.path.exists(os.path.join(AUDIO_DIR, f"{key}{ext}")) and os.path.getsize(os.path.join(AUDIO_DIR, f"{key}{ext}")) > 1000
                for ext in [".mp3", ".wav", ".ogg"]
            )
            if not existing:
                has_all = False
                break
        if has_all:
            skipped += 1
            continue

        print(f"{bird['name']} ({bird['scientific']})")
        results = search_gbif(bird["scientific"])

        for ct in CALL_TYPES:
            key = f"{bird['id']}_{ct['suffix']}"
            existing = any(
                os.path.exists(os.path.join(AUDIO_DIR, f"{key}{ext}")) and os.path.getsize(os.path.join(AUDIO_DIR, f"{key}{ext}")) > 1000
                for ext in [".mp3", ".wav", ".ogg"]
            )
            if existing:
                continue

            rec = find_recording(results, ct["keywords"])
            if not rec:
                rec = find_recording(results, [], fallback=True)
            if not rec:
                failed.append(f"{bird['name']} {ct['label']}")
                continue

            url = rec["url"]
            ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
            if ext not in ("mp3", "wav", "ogg"):
                ext = "mp3"

            output_path = os.path.join(AUDIO_DIR, f"{key}.{ext}")
            if download_file(url, output_path):
                # Convert wav to mp3
                if ext != "mp3" and os.path.exists(FFMPEG):
                    mp3_path = os.path.join(AUDIO_DIR, f"{key}.mp3")
                    import subprocess
                    subprocess.run([FFMPEG, "-y", "-i", output_path, "-acodec", "libmp3lame", "-q:a", "4", mp3_path],
                                   capture_output=True, timeout=30)
                    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 100:
                        os.remove(output_path)
                        ext = "mp3"

                credits[key] = {
                    "xc_id": rec.get("xc_id", ""),
                    "recorder": rec["recorder"],
                    "license": rec["license"],
                    "url": url,
                    "bird_name": bird["name"],
                    "call_type": ct["label"],
                }
                downloaded += 1
                print(f"  {ct['label']}: OK")
            else:
                failed.append(f"{bird['name']} {ct['label']}")

            time.sleep(0.3)

    with open(credits_path, "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    print(f"\nスキップ(既存): {skipped}")
    print(f"追加DL: {downloaded}")
    print(f"失敗: {len(failed)}")
    if failed:
        for f_item in failed:
            print(f"  - {f_item}")


if __name__ == "__main__":
    main()
