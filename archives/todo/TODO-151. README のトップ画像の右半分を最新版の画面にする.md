# TODO-151. README のトップ画像の右半分を最新版の画面にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier |
| 消費 | output 26,926 / cache_creation 92,818 / 概算 $3.9 |
|      | main 95% + verifier 5%（料金の割合） |

依頼と報告は `archives/agents/TODO-151/` にある。

## きっかけ

`docs/fig1.png`（README の先頭に貼っている図）は、左半分がシステム手帳の
リフィルの写真、右半分がアプリの画面という作り。右半分が 2021 年当時の
Android のキャプチャのままで、そのあとに入ったもの（月間ミニカレンダー、
横向きのゲージ、月の境目の年月の見出し、フッターの作り）が写っていなかった。

## やったこと

### 撮り直し

一時ディレクトリにサンプルデータを置き、`--datadir` を指定してアプリを
起動して撮った。予定は旧画像と同じ内容（[面会] 佐藤さん、★事業戦略会議、
ToDo の会議資料など）を、今日（2026-09-01 火）の週へ移して並べ直した。
月曜が 08/31 になるので、月の境目の見出しも写る。

```sh
uv run python tools/screenshot.py -w 412 --height 853 --scale 2 -p today
```

**高さの 853 は、幅 412 のときの `document.body.scrollHeight` に合わせた。**
これより低いと月間ミニカレンダーが下で切れ、これより高いと
`main-page.js` の `body_h < win_h` の分岐に入って、画面の作りが変わる。

### 合成

左半分は `docs/refill1.jpg` の左ページの切り出しで、旧画像と同じものを
そのまま使った。切り出す位置と、写真の下を埋める灰色
（`rgb(128,128,128)`）は、旧 `docs/fig1.png` から測って合わせた。

```sh
convert <shot>.png -resize 550x1139! right.png
convert docs/refill1.jpg -crop 623x997+0+0 +repage left.png
convert -size 1173x1139 xc:'rgb(128,128,128)' \
  left.png  -geometry +0+0   -composite \
  right.png -geometry +623+0 -composite \
  docs/fig1.png
```

大きさは 1264x1139 から 1173x1139 になった。画面の縦横比が変わった
（旧キャプチャは 1080x1934、今回は 412x853）ぶん、右半分が少し細くなる。

合成は数行で済むので、スクリプトは置かず、手順をここに残した。

### `tools/screenshot.py` の `--scale`

デバイスピクセル比を渡せるようにした。レイアウトは `-w` の幅のままで、
画像だけが指定の倍率になる。旧キャプチャ（1080 幅）と並べても粗く
見えないように、2 倍で撮ってから縮小した。既定は 1 なので、これまでの
呼び方では大きさは変わらない。

`docs/Developer.md` の「画面を撮る」に説明を足した。

### `docs/sample1.png`

合成の材料（右半分の元のキャプチャ）。新しく撮ったものに差し替えた
（1080x1934 → 824x1706）。README からは参照していない。

## テスト

verifier に確認させた（`archives/agents/TODO-151/verifier-report.md`）。

- `mise run lint`（ruff format / ruff check / basedpyright / mypy）… 問題なし
- `uv run pytest` … 597 件通過
- `docs/fig1.png` `docs/sample1.png` が PNG として壊れていないこと
- `README.md` からの参照が切れていないこと
- `docs/fig1.png` の右半分に、ゲージ・日付入力欄・月の境目の見出し・
  月間ミニカレンダー 2 か月分・フッターが、切れずに写っていること
- 左半分が `docs/refill1.jpg` の左ページと一致すること
- `--scale` を付けないときの画像の大きさが、これまでと同じであること。
  `--scale 2` で縦横とも 2 倍になり、レイアウトは変わらないこと
- 実データ（`~/ytsched/data`）に触れていないこと
