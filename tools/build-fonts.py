#!/usr/bin/env python3
"""把網站用到的字裁切成小字型檔（assets/fonts/*.woff2）。

改了 index.html 的文字（新增文章、改介面字串）之後跑一次：
    pip install fonttools brotli
    python3 tools/build-fonts.py

原始字型（OFL 授權）會從 google/fonts 下載到 tools/.font-cache/（不進 git）。
"""
import os, sys, urllib.request
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", ".font-cache")
OUT = os.path.join(ROOT, "assets", "fonts")
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
MPLUS = {"400": "Regular", "700": "Bold", "800": "ExtraBold", "900": "Black"}
TC = "NotoSansTC[wght].ttf"


def fetch(rel):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, os.path.basename(rel))
    if not os.path.exists(path):
        print("download", rel)
        urllib.request.urlretrieve(GF + rel.replace("[", "%5B").replace("]", "%5D"), path)
    return path


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


def main():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    chars = {c for c in html if ord(c) >= 32} | {chr(i) for i in range(32, 127)}
    text = "".join(sorted(chars))
    os.makedirs(OUT, exist_ok=True)

    regular = fetch("mplusrounded1c/MPLUSRounded1c-Regular.ttf")
    for w, name in MPLUS.items():
        make(fetch("mplusrounded1c/MPLUSRounded1c-%s.ttf" % name), text, "mplus-%s.woff2" % w)

    # M PLUS Rounded 1c 沒有的繁中字，改用 Noto Sans TC（可變字重，一個檔涵蓋全部粗細）
    cmap = TTFont(regular).getBestCmap()
    missing = "".join(c for c in text if ord(c) not in cmap)
    make(fetch("notosanstc/" + TC), missing, "notosanstc.woff2")


if __name__ == "__main__":
    sys.exit(main())
