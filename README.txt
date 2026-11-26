讀日文小工程（精緻版）

・直接用瀏覽器打開 index.html 就能用（字型已自架在 assets/fonts/，不需連 Google Fonts）。
・也可以整個資料夾丟到任何靜態網站空間（GitHub Pages、Netlify、Cloudflare Pages 等）分享。
・單字本、進度、ふりがな 開關、語言設定都存在使用者自己瀏覽器的 localStorage，不需要帳號。
・assets/ 內：三張文章插圖（webp）、四種表情的飯糰吉祥物（透明 webp）、favicon／App 圖示、分享縮圖 og-image.png（1200×630）。
・分享縮圖在部分平台（LINE、Facebook、X）需要完整網址才會顯示；上線後可把 index.html 裡 og:image 改成完整網址。
・字型是「裁切版」，只含 index.html 裡用到的字。新增文章或改文字後，請跑一次：
    pip install fonttools brotli
    python3 tools/build-fonts.py
  然後把 sw.js 第一行附近的 CACHE 版本號（drw-v2）加一，讓舊訪客拿到新字型。
・文章插圖另有 -600.webp 小圖給清單卡片用；換插圖時兩種尺寸都要更新。
