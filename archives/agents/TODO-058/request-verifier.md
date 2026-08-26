# TODO-058 verifier への依頼

## 何をした項目か

**左端の縦ゲージをやめて、週バーの下に横向きのゲージの帯を 1 行出す
ようにした。**

- 帯は `#week_bar`（`fixed-top`）の中の 2 行目。**中央 (50%) が今週、
  両端が ±30y**。目盛りのラベルは 8 個（`-30y` `-1y` `-1m` `-1w`
  `+1w` `+1m` `+1y` `+30y`）
- 位置は px ではなく**割合 (%)**で持つ。Python 側
  （`main_handler.py` の `days2x_percent()`。`days2y_offset()` を
  置き換えた）と JavaScript 側（`my.js` の `days2xPercent()`）で
  同じ式にしてある
- **ゲージのクリックで移動する機能は無い**（表示だけ）
- **検索モードでは週バーごと出ないので、横ゲージも出ない**
- 縦ゲージ用に空けていた `main` の `padding-left:22px` を詰めた

変えたファイル: `src/ytsched/main_handler.py`、
`src/ytsched/webroot/templates/main.html`、
`src/ytsched/webroot/static/css/my.css`、
`src/ytsched/webroot/static/js/my.js`、`tests/test_handler.py`、
`tests/README.md`。実装の詳細は
[implementer-report.md](implementer-report.md) を読むこと。

## 確かめてほしいこと

1. 決まった手順（`mise run fmt` / `typecheck` / `lint` / `test`）。
   **`mise run upgradeproject` は走らせない**
2. **実際にアプリを動かして、次を確かめる**（`--datadir` は必ず一時
   ディレクトリ。`~/ytsched/data` を汚さないこと）
   - 週バーの下に帯が出ていること。左端に縦ゲージの残りが**無い**こと
   - **週を送る（← → ボタン、左右のスワイプ）と針が動くこと。**
     0.3 秒かけて動くところまで見る。TODO-054 の verifier が
     `getBoundingClientRect()` で追う手を使っている
     （[TODO-054 の報告](../TODO-054/verifier-report.md)）。
     今回は縦ではなく**横**なので `.left` を見ること
   - 針の位置が週に合っていること。**今週で中央、+1w で `+1w` の
     ラベルのあたり、離れた週（数年先など）で端に寄る**
   - **30 年より先の日付でも、針が帯からはみ出さないこと**（頭打ち）
   - **検索モードでは帯が出ないこと。** そのとき JavaScript の
     エラーが出ないこと（`gage_r` が無い状態で `dispGage()` が
     呼ばれる）
   - 帯のぶん週バーが高くなるが、**一番上の日付ブロックが隠れて
     いないこと**（`padding-top` は `offsetHeight` から入る）
   - ホームボタン（1 回押し・2 回押し）、日付欄、週送りが今までどおり
     効くこと
   - console に error / warning が出ていないこと
3. **キャプチャを撮る**（`tools/screenshot.py`、`env -u DISPLAY` を
   付ける）。幅は **412px と 800px、それに 360px**。
   **360px でラベルが重なっていないか**を必ず見ること
   （重なるようなら `±1m` を落として 6 個に減らすと決めてある）

**検索語は `conf.json` に残る。** 確認のあいだにデータディレクトリを
分けるか、検索を解除してから次を見ること。

## 報告

`archives/agents/TODO-058/verifier-report.md` に書く。返事は 5 行以内で、
終わったか・報告ファイルのパス・判断が要る点だけ。**コードは直さない。**
撮ったキャプチャのパスは報告ファイルに書いておくこと。
