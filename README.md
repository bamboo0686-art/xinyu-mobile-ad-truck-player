# 心禹國際 2.1 噸 LED 行動廣告車虛擬播放器

可直接部署於 GitHub Pages 的靜態 3D 播放器。使用者可在電腦或手機瀏覽器上傳本機影片／圖片，預覽素材顯示在行動廣告車 LED 螢幕上的效果。

## 已完成規格

- 左側主螢幕與左側 90° 轉角螢幕皆為滿版無框。
- 左側兩面螢幕共用同一條幾何邊線，轉角間距 0 mm。
- 左側 L 型畫面使用同一支素材連續分割，不重複播放完整畫面。
- 右側平面螢幕上下與四周滿版無框。
- 車尾右側保留唯一一道車廂出入口門。
- 支援影片、圖片、播放／暫停、靜音、視角切換、自動旋轉、全螢幕及擷取畫面。
- 上傳素材僅在使用者瀏覽器本機處理，不會儲存至網站或伺服器。

## 專案結構

```text
xinyu-mobile-ad-truck-player/
├─ index.html
├─ .nojekyll
├─ README.md
├─ assets/
│  ├─ models/
│  │  └─ Xinyu_2.1t_LED_Mobile_Ad_Truck_V2.glb
│  └─ config/
│     └─ screen_mapping.json
└─ robots.txt
```

## 模型顯示面

| 顯示面 | GLB Mesh | 實體尺寸 |
|---|---|---:|
| 左側主螢幕 | `LED_LEFT_MAIN` | 3.69 × 1.44 m |
| 左側 90° 轉角螢幕 | `LED_LEFT_REAR` | 1.12 × 1.44 m |
| 右側平面螢幕 | `LED_RIGHT_MAIN` | 2.52 × 1.44 m |
| 車頭上方螢幕 | `LED_FRONT_HEADER` | 1.68 × 0.64 m |
| 車尾右側門 | `REAR_RIGHT_ACCESS_DOOR` | 已保留 |

左側 L 型總展開尺寸為 4.81 × 1.44 m，建議素材比例約 3.34:1，例如 1920×575。

## GitHub Pages

儲存庫：`bamboo0686-art/xinyu-mobile-ad-truck-player`

預定網址：

```text
https://bamboo0686-art.github.io/xinyu-mobile-ad-truck-player/
```

若網站尚未發布，請到儲存庫的 `Settings` → `Pages`，選擇 `Deploy from a branch`，Branch 選 `main`、資料夾選 `/(root)`，再按 `Save`。

## 技術說明

- 模型格式：glTF Binary（GLB），單位為公尺，Y 軸向上。
- 播放器：Three.js ES Module。
- Three.js 固定使用 0.165.0 版本，由 jsDelivr CDN 載入。
- 部署：純靜態 GitHub Pages，不需要 Node.js、npm、資料庫或後端。
