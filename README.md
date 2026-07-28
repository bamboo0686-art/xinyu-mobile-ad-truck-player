# 心禹國際 2.1 噸 LED 行動廣告車虛擬播放器 V2

這是一個可直接部署到 **GitHub Pages** 的純靜態 3D 播放器，不需要 Node.js、npm、資料庫或後端伺服器。

## V2 修正重點

- 左側 L 型 LED 主螢幕、右側平面 LED 螢幕皆為滿版顯示，不建立上框、下框或四周裝飾框物件。
- 左側主螢幕與車尾左側轉角螢幕共用同一條 90° 幾何邊線，模型間距為 0 mm。
- 左側 L 型影片採一支素材連續分割到兩個螢幕，不會把同一畫面完整重複兩次。
- 車尾右側保留唯一一道車廂出入口門，其他可視側面不增加車門。
- 手機與電腦瀏覽器皆可使用，支援旋轉、縮放、視角切換、全螢幕與擷取畫面。

## 直接上傳 GitHub

1. 在 GitHub 建立新的 Repository。
2. 將本資料夾內的所有檔案與資料夾完整上傳到 Repository 根目錄。
3. 進入 Repository 的 `Settings` → `Pages`。
4. `Build and deployment` 選擇 `Deploy from a branch`。
5. Branch 選擇 `main`，資料夾選擇 `/(root)`，按下 `Save`。
6. 等待 GitHub Pages 完成部署後，開啟系統提供的網站網址。

> 請勿只上傳 `index.html`。`assets/models`、`assets/config` 與其他資料夾必須一起保留。

## 專案結構

```text
xinyu-mobile-ad-truck-player/
xinyu-mobile-ad-truck-player
├── index.html
├── README.md
├── LICENSE.txt
├── .nojekyll
├── assets
├── build_xinyu_truck.py
├── render_preview.py
└── validate_project.py
```

## LED 物件名稱

| 顯示面 | GLB Mesh 名稱 | 實體尺寸 |
|---|---|---:|
| 左側主螢幕 | `LED_LEFT_MAIN` | 3.69 × 1.44 m |
| 左側 90° 轉角螢幕 | `LED_LEFT_REAR` | 1.12 × 1.44 m |
| 右側平面螢幕 | `LED_RIGHT_MAIN` | 2.52 × 1.44 m |
| 車頭上方小螢幕 | `LED_FRONT_HEADER` | 1.68 × 0.64 m |
| 車尾右側出入口門 | `REAR_RIGHT_ACCESS_DOOR` | 保留 |

左側 L 型總展開尺寸約為 **4.81 × 1.44 m**，素材建議比例約 **3.34:1**，可使用 1920×575、2560×767 或其他等比例素材。

## 技術方式

- 模型：glTF Binary（GLB），單位為公尺，Y 軸向上。
- 播放器：Three.js ES Module。
- 部署：GitHub Pages 靜態網站。
- 媒體：瀏覽器本機 `Blob URL`，素材不會上傳至伺服器。
- L 型無縫內容：同一個影片元素產生兩張 VideoTexture，依 3.69 m 與 1.12 m 的展開寬度切割 UV。

## 本機測試

因瀏覽器安全限制，不建議直接雙擊 `index.html`。可在本資料夾執行：

```bash
python -m http.server 8000
```

然後在瀏覽器開啟：

```text
http://localhost:8000
```

## 注意事項

Three.js 程式庫由 CDN 載入，因此使用播放器時需要網路連線。正式 Logo 未由 AI 重新繪製；如需加入正式 Logo，請以心禹國際原始 Logo 檔進行後製貼圖。
