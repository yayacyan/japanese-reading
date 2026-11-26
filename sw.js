/* 讀日文小工程 service worker：重複造訪秒開、離線也能讀 */
var CACHE = "drw-v2";
var CORE = [
  "./",
  "assets/fonts/mplus-400.woff2",
  "assets/fonts/mplus-700.woff2",
  "assets/fonts/mplus-800.woff2",
  "assets/fonts/mplus-900.woff2",
  "assets/fonts/notosanstc.woff2",
  "assets/mascot.webp",
  "assets/mascot-128.webp"
];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;

  // 頁面：先拿最新版，沒網路才用快取
  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then(function (res) {
      var copy = res.clone();
      caches.open(CACHE).then(function (c) { c.put("./", copy); });
      return res;
    }).catch(function () { return caches.match("./"); }));
    return;
  }

  // 圖片、字型：先用快取，背景再更新
  e.respondWith(caches.open(CACHE).then(function (c) {
    return c.match(req).then(function (hit) {
      var net = fetch(req).then(function (res) {
        if (res.ok) c.put(req, res.clone());
        return res;
      });
      if (hit) { net.catch(function () {}); return hit; }
      return net;
    });
  }));
});
