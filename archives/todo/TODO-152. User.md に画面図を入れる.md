# TODO-152. docs/User.md に画面図を入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier |
| 消費 | output 89,698 / cache_creation 292,393 / 概算 $11.5 |
|      | main 96% + verifier 4%（料金の割合） |

依頼と報告は `archives/agents/TODO-152/` にある。

## きっかけ

`docs/User.md` は文章だけで、画面を見たことがない人には何がどこにあるのか
伝わらなかった。検索結果のバーだけはコードブロックで擬似図を書いてあったが、
実物とは形が違っていた。

## やったこと

### 6 枚の画面図

`docs/user-week.png` `docs/user-month.png` `docs/user-menu.png`
`docs/user-search.png` `docs/user-trash.png` `docs/user-edit.png` を作り、
`docs/User.md` の各節の頭に貼った。スマホで使う前提なので、幅 412px・
デバイスピクセル比 2 で撮っている。

### `tools/annotate.py`

キャプチャに引き出し線と吹き出しを重ねる道具。キャプチャを HTML に貼り、
吹き出しを絶対位置で並べ、引き出し線を SVG で引いて、chromium で撮り直す。
注釈の位置は `tools/user-figs.json` に書く。`mise run figs` で流せる。

- **引き出し線はブラウザ側で引く。** 吹き出しの大きさは文字を流し込むまで
  決まらないので、`getBoundingClientRect()` で測ってから、吹き出しの中心と
  指し示す点の位置関係で「どの辺から線を出すか」を決める
- **画像は data: URI で埋め込む。** `page.set_content()` で開いたページは
  about:blank 扱いになり、`file:` の画像を読めない
- `crop` で画面の一部だけを図にできる（メニューの図は下端だけを使った）

ImageMagick の `-draw` で 6 枚ぶん書くやり方は採らなかった。撮り直しの
たびに座標を書き直すことになり、6 枚では手に負えない。

### 撮り直しの手順

サンプルデータ、URL、それぞれの高さ、撮る順番は
[../agents/TODO-152/verifier-request.md](../agents/TODO-152/verifier-request.md)
に書いてある。要点は 2 つ。

- **検索は最後に撮る。** `search_str` は `conf.json` に保存され、検索中は
  月間表示にならない（検索モードが優先）
- **検索の解除は `?search_str=%20`（空白 1 文字）。** `?search_str=` では
  解除できない。tornado が空の引数を渡さないので「指定が無かった」と
  同じ扱いになる

高さは画面ごとに変えた（週 853 / 月 815 / メニュー 853 / ゴミ箱 370 /
編集 545 / 検索 500）。週の 853 は TODO-151 と同じ理由で、これより低いと
ミニカレンダーが切れ、高いと `main-page.js` の分岐が変わる。他は中身が
入りきる高さに合わせて、余白が空きすぎないようにした。

### `docs/User.md` の整理

- 「週の表示」を先頭に持ってきた。最初に出る画面なので、そこから読むほうが
  分かりやすい
- **「編集画面」の節を新しく足した。** それまでどこにも説明が無く、
  5 つのボタン（戻る・更新・完了・複製・削除）の違いも書いていなかった
- 検索結果のバーの擬似図（コードブロック）を、実画面の図に差し替えた。
  左右の日付・目標件数・さかのぼった日数の説明は、図の吹き出しへ移した

## テスト

verifier に確認させた（`archives/agents/TODO-152/verifier-report.md`）。

- `mise run lint` … 問題なし
- `uv run pytest` … 597 件通過
- `docs/user-*.png` 6 枚が PNG として壊れていないこと
- `docs/User.md` からの参照が切れていないこと
- **図を実際に開いて、吹き出しのはみ出し・引き出し線のずれ・文字切れが
  無いこと**
- 編集画面のボタンの説明が、`edit.html` の `data-cmd` と
  `MainHandler.exec_cmd()` の挙動に合っていること
- `tools/annotate.py` の `--only` が、1 枚だけ作れること・無い名前では
  エラーで終わること
- 実データ（`~/ytsched/data`）に触れていないこと

`docs/user-search.png` の左側の引き出し線が交差しているという指摘を受けて、
吹き出しの上下を入れ替えた。
