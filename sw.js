/* 讀日文小工程 service worker：重複造訪秒開、離線也能讀 */
var PREFIX = "drw-";
var CACHE = PREFIX + "f5c0ea33";
var CORE = [
  "./",
  "assets/fonts/mplus-400.woff2?v=3ac0254f95",
  "assets/fonts/mplus-700.woff2?v=822258bb3a",
  "assets/fonts/mplus-800.woff2?v=2456896b0d",
  "assets/fonts/mplus-900.woff2?v=3361fc3fc9",
  "assets/fonts/notosanstc.woff2?v=111ba6dc3a",
  "assets/mascot.webp",
  "assets/mascot-128.webp"
];
var SCOPE = new URL("./", self.location).pathname;   // e.g. /japanese-reading/

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) {
    // cache: "reload" skips the browser's HTTP cache, so a new version never stores an old file
    return Promise.all(CORE.map(function (u) {
      return fetch(new Request(u, { cache: "reload" })).then(function (res) {
        if (res.ok) return c.put(u, res);
      }).catch(function () {});
    }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  // only remove this site's own old versions, never caches of other projects on the same domain
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf(PREFIX) === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

function isAppPage(url) {
  var p = new URL(url).pathname;
  return p === SCOPE || p === SCOPE + "index.html";
}

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;

  // 頁面：先拿最新版，沒網路才用快取。只把成功的首頁存成離線版本
  if (req.mode === "navigate") {
    if (!isAppPage(req.url)) return;
    e.respondWith(fetch(req).then(function (res) {
      if (res.ok) {
        var copy = res.clone();
        e.waitUntil(caches.open(CACHE).then(function (c) { return c.put("./", copy); }));
      }
      return res;
    }).catch(function () { return caches.match("./"); }));
    return;
  }

  // 圖片、字型：先用快取，背景再更新（字型網址帶版本號，換版時一定會抓新檔）
  e.respondWith(caches.open(CACHE).then(function (c) {
    return c.match(req).then(function (hit) {
      var net = fetch(req).then(function (res) {
        if (res.ok) c.put(req, res.clone());
        return res;
      });
      if (hit) { e.waitUntil(net.catch(function () {})); return hit; }
      return net;
    });
  }));
});
