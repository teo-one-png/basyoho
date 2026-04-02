const CACHE_NAME = "torioboe-v10";
const DATA_SCRIPTS = [
  "./data.js",
  "./tree_data.js",
  "./nakigoe_data.js",
  "./shokusou_data.js",
  "./fish_data.js",
];

importScripts.apply(null, DATA_SCRIPTS);

const CORE_ASSETS = [
  "./index.html",
  "./style.css",
  "./app.js",
  "./credits.js",
  "./nakigoe_credits.js",
  "./fish_credits.js",
  "./db.js",
  "./quiz.js",
  "./settings.js",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
].concat(DATA_SCRIPTS);

function normalizeAssetPath(assetPath) {
  if (!assetPath || typeof assetPath !== "string") return null;
  if (assetPath.indexOf("./") === 0) return assetPath;
  return "./" + assetPath.replace(/^\/+/, "");
}

function collectMediaAssets(items) {
  return (items || []).reduce(function (assets, item) {
    var imagePath = normalizeAssetPath(item.image);
    var audioPath = normalizeAssetPath(item.audio);

    if (imagePath) assets.push(imagePath);
    if (audioPath) assets.push(audioPath);

    return assets;
  }, []);
}

const CONTENT_ASSETS = []
  .concat(collectMediaAssets(typeof BIRD_DATA !== "undefined" ? BIRD_DATA : []))
  .concat(collectMediaAssets(typeof TREE_DATA !== "undefined" ? TREE_DATA : []))
  .concat(collectMediaAssets(typeof NAKIGOE_DATA !== "undefined" ? NAKIGOE_DATA : []))
  .concat(collectMediaAssets(typeof INSECT_DATA !== "undefined" ? INSECT_DATA : []))
  .concat(collectMediaAssets(typeof PLANT_DATA !== "undefined" ? PLANT_DATA : []))
  .concat(collectMediaAssets(typeof FISH_DATA !== "undefined" ? FISH_DATA : []));

const ALL_ASSETS = Array.from(new Set(CORE_ASSETS.concat(CONTENT_ASSETS)));

self.addEventListener("install", function (event) {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(ALL_ASSETS);
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    Promise.all([
      caches.keys().then(function (keys) {
        return Promise.all(
          keys
            .filter(function (key) { return key !== CACHE_NAME; })
            .map(function (key) { return caches.delete(key); })
        );
      }),
      self.clients.claim(),
    ])
  );
});

self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then(function (cachedResponse) {
      if (cachedResponse) return cachedResponse;

      return fetch(event.request).then(function (networkResponse) {
        if (
          networkResponse &&
          networkResponse.ok &&
          new URL(event.request.url).origin === self.location.origin
        ) {
          var responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(event.request, responseClone);
          });
        }

        return networkResponse;
      });
    })
  );
});
