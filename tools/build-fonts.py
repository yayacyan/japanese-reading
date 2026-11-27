#!/usr/bin/env python3
"""把網站用到的字裁切成小字型檔（assets/fonts/*.woff2）。

改了 index.html 的文字（新增文章、改介面字串）之後跑一次：
    pip install fonttools brotli
    python3 tools/build-fonts.py

它會：
  1. 重新產生 assets/fonts/ 裡的字型子集
  2. 把 index.html 和 sw.js 裡的字型網址換成新的版本號（?v=...），
     並更新 sw.js 的快取名稱，讓舊訪客一定拿到新字型

只檢查、不改檔（給 GitHub Actions 用）：
    python3 tools/build-fonts.py --check
有字不在字型裡、或網址版本號跟字型檔對不上，就會失敗。

原始字型（OFL 授權）固定從 google/fonts 的某個版本下載到 tools/.font-cache/（不進 git）。
"""
import hashlib, os, re, sys, urllib.request
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", ".font-cache")
OUT = os.path.join(ROOT, "assets", "fonts")
HTML = os.path.join(ROOT, "index.html")
SW = os.path.join(ROOT, "sw.js")
GF_COMMIT = "5026800714d07231937d92eb4cceabf06e05d74e"   # google/fonts, pinned so builds are reproducible
GF = "https://raw.githubusercontent.com/google/fonts/%s/ofl/" % GF_COMMIT
MPLUS = {"400": "Regular", "700": "Bold", "800": "ExtraBold", "900": "Black"}
TC = "NotoSansTC[wght].ttf"
FONT_FILES = ["mplus-%s.woff2" % w for w in MPLUS] + ["notosanstc.woff2"]
# characters that are deliberately left to the system (emoji)
IGNORE = set("☕")


def fetch(rel):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, os.path.basename(rel))
    if not os.path.exists(path):
        print("download", rel)
        tmp = path + ".part"
        urllib.request.urlretrieve(GF + rel.replace("[", "%5B").replace("]", "%5D"), tmp)
        os.replace(tmp, path)   # only a complete download ever gets the real name
    return path


def site_text():
    html = open(HTML, encoding="utf-8").read()
    chars = {c for c in html if ord(c) >= 32} | {chr(i) for i in range(32, 127)}
    return "".join(sorted(chars - IGNORE))


def make(src, text, dst):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    font = subset.load_font(src, opts)
    s = subset.Subsetter(opts)
    s.populate(text=text)
    s.subset(font)
    subset.save_font(font, os.path.join(OUT, dst), opts)
    print(dst, os.path.getsize(os.path.join(OUT, dst)), "bytes")


def versions():
    v = {}
    for f in FONT_FILES:
        v[f] = hashlib.sha256(open(os.path.join(OUT, f), "rb").read()).hexdigest()[:10]
    return v


def stamp(path, v):
    """Rewrite assets/fonts/NAME.woff2[?v=...] to the current version; returns the new text."""
    text = open(path, encoding="utf-8").read()
    for f, h in v.items():
        text = re.sub(r"assets/fonts/%s(\?v=[0-9a-f]+)?" % re.escape(f), "assets/fonts/%s?v=%s" % (f, h), text)
    if path == SW:
        combo = hashlib.sha256("".join(v[f] for f in FONT_FILES).encode()).hexdigest()[:8]
        text = re.sub(r'var CACHE = PREFIX \+ "[^"]*";', 'var CACHE = PREFIX + "%s";' % combo, text)
    return text


def check():
    text = site_text()
    covered = set()
    for f in FONT_FILES:
        covered |= set(chr(c) for c in TTFont(os.path.join(OUT, f)).getBestCmap())
    missing = sorted(c for c in text if c not in covered and not c.isspace())
    ok = True
    if missing:
        ok = False
        print("字型裡缺這些字，請跑 python3 tools/build-fonts.py：", "".join(missing))
    v = versions()
    for path in (HTML, SW):
        if stamp(path, v) != open(path, encoding="utf-8").read():
            ok = False
            print("%s 的字型版本號沒更新，請跑 python3 tools/build-fonts.py" % os.path.basename(path))
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    if "--check" in sys.argv:
        return check()
    text = site_text()
    os.makedirs(OUT, exist_ok=True)

    regular = fetch("mplusrounded1c/MPLUSRounded1c-Regular.ttf")
    for w, name in MPLUS.items():
        make(fetch("mplusrounded1c/MPLUSRounded1c-%s.ttf" % name), text, "mplus-%s.woff2" % w)

    # M PLUS Rounded 1c 沒有的繁中字，改用 Noto Sans TC（可變字重，一個檔涵蓋全部粗細）
    cmap = TTFont(regular).getBestCmap()
    missing = "".join(c for c in text if ord(c) not in cmap)
    make(fetch("notosanstc/" + TC), missing, "notosanstc.woff2")

    v = versions()
    for path in (HTML, SW):
        new = stamp(path, v)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
    print("updated font versions in index.html and sw.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
