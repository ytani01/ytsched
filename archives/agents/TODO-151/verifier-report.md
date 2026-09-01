# TODO-151 verifier 報告

## 1. lint / pytest

- `mise run lint` — 通った（ruff format / ruff check / basedpyright / mypy / eslint / prettier いずれも問題なし）
- `uv run pytest` — 597 passed（157.24s）

## 2. PNG の健全性

```
identify docs/fig1.png docs/sample1.png docs/refill1.jpg
docs/fig1.png     PNG  1173x1139
docs/sample1.png  PNG  824x1706
docs/refill1.jpg  JPEG 1264x997
```
壊れずに読める。サイズは依頼記載の値と一致。

## 3. 参照切れ

- `README.md:3` の `![](docs/fig1.png)` — 健在
- `docs/sample1.png` `docs/refill1.jpg` を参照している箇所は
  リポジトリ内に無かった（`TODO.md` 中の記述は TODO-151 自体の
  タスク説明であり、画像参照ではない）

## 4. fig1.png 右半分の内容（画像を目視）

以下すべて確認できた。
- 上部の横向きゲージ（`-30y … ±0 … +30y`）
- ヘッダーの日付入力欄（`2026/09/01`）
- 月の境目の見出し（`2026/08` `2026/09`）
- 月間ミニカレンダー 2 か月分、切れずに表示
- フッター（メニュー・◀▶・ホーム・検索欄）

## 5. fig1.png 左半分と refill1.jpg

画像を並べて目視。`refill1.jpg` の左ページ（8/2〜8/8）と一致している。

## 6. `tools/screenshot.py --scale`

- `--help` に `--scale SCALE  デバイスピクセル比...(既定: 1.0)` と出る
- `-w 412 --height 900`（`--scale` 無し）→ 412x900（期待通り）
- `-w 412 --height 900 --scale 2` → 824x1800（期待通り）
- `scale2` 画像を 412x900 へ縮小して `noscale` と比較。
  `compare -metric AE` で差分 107262px（全 370800px 中）出たが、
  差分画像・両画像を目視した結果、レイアウトは同一で文字のアンチエイリアス
  由来の差と判断（構造的なズレなし）

## 7. 実データ

`--datadir` に一時ディレクトリ
（`/tmp/claude-649/.../scratchpad/ytsched-data`）を指定して起動。
`~/ytsched/data` には触れていない。起動したプロセスはすべて kill 済み。

## 気づいた点（既知でなければ報告）

用意したサンプルデータの JSON Lines が実際のスキーマ（`date` フィールド等）
と合っておらず、`load_line()` で「invalid .. ignored」の警告が出た
（依頼の確認項目には含まれないため、そのまま進めた）。画像の内容確認
（4・5）自体はリポジトリの `docs/fig1.png` を直接読んで行ったので、
このサンプルデータの不備は結果に影響していない。
