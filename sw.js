const CACHE_NAME = "torioboe-v2";
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
  "./images/ootaka.jpg",
  "./images/haitaka.jpg",
  "./images/tsumi.jpg",
  "./images/nosuri.jpg",
  "./images/kumataka.jpg",
  "./images/sashiba.jpg",
  "./images/hachikuma.jpg",
  "./images/ohwashi.jpg",
  "./images/ojirowanshi.jpg",
  "./images/hayabusa.jpg",
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
