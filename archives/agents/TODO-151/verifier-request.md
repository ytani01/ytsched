# TODO-151 verifier への依頼

## 目的

README のトップ画像 `docs/fig1.png` の右半分を、最新版の画面に差し替えた。
その結果が壊れていないかを確かめる。

## 変更したもの

- `docs/fig1.png` — 作り直した（1264x1139 → 1173x1139）
- `docs/sample1.png` — 合成の材料。新しい画面キャプチャに差し替えた
  （1080x1934 → 824x1706）
- `tools/screenshot.py` — `--scale`（デバイスピクセル比）を足した
- `docs/Developer.md` — `--scale` の説明を足した

`docs/refill1.jpg`（リフィルの写真）は変えていない。

## 作った手順

1. 一時ディレクトリにサンプルデータを置く（下記）
2. `uv run ytsched webapp --datadir <一時ディレクトリ> --port 10085`
3. `uv run python tools/screenshot.py -w 412 --height 853 --scale 2 -p today -o <出力先>`
4. 合成（`convert`）

```sh
convert <shot>.png -resize 550x1139! right.png
convert docs/refill1.jpg -crop 623x997+0+0 +repage left.png
convert -size 1173x1139 xc:'rgb(128,128,128)' \
  left.png  -geometry +0+0   -composite \
  right.png -geometry +623+0 -composite \
  docs/fig1.png
```

高さ 853 は、幅 412 のときの `document.body.scrollHeight` に合わせた値。
これより低いと月間ミニカレンダーが切れ、これより高いと
`main-page.js` の `body_h < win_h` の分岐に入る。

サンプルデータ（旧 `docs/sample1.png` の内容を今日 2026-09-01 の週へ移したもの）:

```
2026/08/31.jsonl : 07:00-11:00 [朝活] (欠)バックギャモン @泰生ポーチ / 寝坊(^^;)
2026/09/01.jsonl : 10:00-11:30 [面会] 佐藤さん @1Fロビー / 新技術に関する提案
                   15:00-17:00 資料作成 @オフィス / ・データのまとめ
                   19:00       [会食] 田中さん @渋谷
2026/09/02.jsonl : 13:00-15:00 [会議] ★事業戦略会議 @会議室1
2026/09/04.jsonl : 18:00-20:00 [パーティー] 親睦会 @六本木
ToDo.jsonl       : 2026-09-02 □ToDo 会議資料
```

## 確かめること

1. `mise run lint`（ruff format / ruff check / basedpyright / mypy）と
   `uv run pytest` が通ること
2. `docs/fig1.png` `docs/sample1.png` が PNG として壊れていないこと
   （`identify` / `convert ... info:` が通る）
3. `README.md` からの参照（`![](docs/fig1.png)`）が切れていないこと。
   リポジトリ内から `docs/sample1.png` `docs/refill1.jpg` を参照している
   箇所があれば、それも切れていないこと
4. `docs/fig1.png` の右半分に、旧画像に無かった今の要素が写っていること。
   画像を読んで確かめる:
   - 上部の横向きゲージ（`-30y … ±0 … +30y`）
   - ヘッダーの日付入力欄（`2026/09/01`）
   - 月の境目の年月の見出し行（`2026/08` と `2026/09`）
   - 月間ミニカレンダーが 2 か月分、切れずに入っていること
   - フッター（メニュー・◀▶・ホーム・検索欄）
5. 左半分がリフィルの写真のままで、`docs/refill1.jpg` の左ページと
   一致すること（`compare` などで見てよい）
6. `tools/screenshot.py` の `--scale`:
   - `--help` に出ること
   - `--scale` を付けないときの画像の大きさが、これまでと同じ
     （`-w 412 --height 900` なら 412x900）
   - `--scale 2` で 824x1800 になり、レイアウトは変わらないこと
     （縮小して並べれば、ほぼ同じに見えるはず）
7. 実データ（`~/ytsched/data`）に触れていないこと。
   **アプリを起動するときは `--datadir` に必ず一時ディレクトリを指定する。**

## 報告

`archives/agents/TODO-151/verifier-report.md` に書く。
**コードや画像は直さないこと。** 見つけたことは報告だけする。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。
