# TODO-048. Font Awesome をやめて、自作の SVG アイコンにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier（2 回）+ wording（2 回） |
| 消費 | output 130,507 / cache_creation 580,585 / 概算 $16.4 |
|      | main 87% + implementer 6% + verifier 5% + wording 2%（料金の割合） |

消費は `mise run tokens -- TODO-048 --since '2026-08-25 16:42:16'` で
数えた。**`--since` が要る。** 立てたのは 06:39 で、着手までの間に
TODO-050・052・053 を挟んでいるため、指定しないとその分（reviewer を
含む）まで数に入る（$73.5 になった）。

依頼と報告は `archives/agents/TODO-048/` にある。

## きっかけ

`static/vendor/fontawesome/` は 288KB（`all.css` 130KB、
`fa-solid-900.woff2` 119KB、`fa-regular-400.woff2` 20KB）あったが、
使っていたアイコンは 23 か所・22 種類だけだった。読み込んでいたのは
`base.html` の 1 行で、Python・JavaScript・CSS からは参照していない。

- **アイコンフォントは、フォント側の既定値が変わると位置がずれる。**
  ゲージの針と基準線がずれた件（TODO-042）がそれで、TODO-043 で SVG に
  描き直して直した。今回は残りのアイコンに同じことをした
- フォントの読み込みが終わるまでアイコンが出ない
- **自作にすればライセンスの扱いが要らなくなる。** Font Awesome Free は
  フォントが SIL OFL 1.1、アイコン（SVG）は CC BY 4.0 で、SVG を持つ形に
  すると帰属表示が要る

TODO-047（Bootstrap をやめる）で同梱していた外部ライブラリは、これで
無くなった。

## やったこと

### 22 個すべてを自分で描いた

Font Awesome の SVG は使わず、図案も写していない。家・虫めがね・
ゴミ箱といったありふれた図案そのものは構わないが、パスをなぞると
派生物になるので、円と直線の組み合わせとして引き直した。

- `viewBox="0 0 24 24"` に、太さ 2 の線で描く。`stroke: currentColor` /
  `fill: none` なので、`<i>` のときと同じく親の文字色に従う
- **solid と regular を使い分けている 2 組**（`square` と
  `check-square`、`arrow-alt-circle-up` の solid と regular）は、
  外形を同じにして、輪郭だけ描くか中を塗るかで分けた

`<symbol>` は 23 個ある。`arrow-alt-circle-up` が solid と regular で
字形が違い、`#circle-up-fill`（検索バー）と `#circle-up`（編集画面）の
2 つに分かれるため。

**`sync`（更新）と `spinner`（読み込み中）は、まとめずに別のままにした。**
自作なら 1 つの図案にできると見込んでいたが、一覧を作る段階で見て、
用途が違うものを同じ絵にする利点が無いと判断した。

### 先に確認用ページを作って、図案の承認を取った

**字形が別物になるので、変更の前後のキャプチャが一致するかは見られない。**
そこで、テンプレートを差し替える前に、23 個の一覧・大きさ（`lg` / `2x` /
`9x`）・メニューバーに置いた様子を 1 枚にまとめたページを作り、
キャプチャを見せて承認を取った。描き直しが安く済む。

ページは `tools/icons_preview.py` で作り直せる。キャプチャは
[images/TODO-048-icons_800.png](images/TODO-048-icons_800.png)
（スマホ幅は `_412.png`）。

**外部ファイルを `<use href="icons.svg#...">` で参照する形が Chromium で
効くことも、このページで確かめた。** スプライトを `base.html` へ埋め込む
必要は無かった。

### 大きさと回転は `my.css` のクラスに移した

`fa-lg`（1.25em）・`fa-2x`（2em）・`fa-9x`（9em）・`fa-spin`（2 秒・
linear・無限）の代わりに、`my-icon` / `my-icon-lg` / `my-icon-2x` /
`my-icon-9x` / `my-icon-spin` を `.my-spinner` の隣に置いた。
**`my-icon-9x` だけは線が太くなりすぎるので `stroke-width: 1` に下げて
いる。** 既存の `align-middle` / `align-bottom` はそのまま使える。

`my-icon` の `width` / `height` は `1em` なので、`.my-sde-check` の
`font-size: small` のような指定は `<i>` のときと同じに効く。

### 詳細のある行が 44.00px → 50.25px に太っていた（直した）

原因は開閉スイッチ（`sde.html` の `.my-sde-detail-sw` の中の
`<label class="m-1">`）。**Font Awesome の `.fa-lg` は
`line-height: .05em` を持っていて、`<i>` 自体の高さがほぼ 0 になっていた**
（実測で 0.81px）。字面はその枠からはみ出して描かれるので、行の高さには
響かない。SVG は 16.25px の場所をそのまま取るので、`label` の余白
`m-1`（4px）が効いてしまった。

`m-1` を外して `my.css` に `.my-sde-detail-sw label { margin: 1px; }` を
足し、44.25px に戻した。詳細の無い行は 26.00px で変わっていない。

### 消したもの・残したもの

- `static/vendor/fontawesome/`（`LICENSE.txt` / `css/all.css` /
  `webfonts/*.woff2`）を削除し、`base.html` の `<link>` も外した。
  「`my.css` は `all.css` より後に読むこと」のコメント（TODO-047）も
  一緒に消えた
- `README.md` の「同梱しているライブラリ」を「外部のライブラリ」に
  書き直した。同梱するものが無くなったため
- `main.html` と `my.css` に残る `fa-caret-right` / `fa-grip-lines` の
  コメントは、ゲージの図形の由来（TODO-043）を書いたものなので残した
- `edit.html` のコメントアウトされた戻るボタンの中の `fa-reply` も、
  消し残しの `grep` に引っかからないよう `<svg><use>` に揃えた

## テスト

### 目で見比べるだけでは足りなかった

**キャプチャを目で見比べただけでは、行の高さの崩れに気づけなかった。**
verifier は 1 回目に「崩れなし」と報告してきていて、上の 50.25px は
`getBoundingClientRect()` で数えて初めて出てきた。

直したあとの確認（verifier 2 回目）では、HEAD の webroot を
`git archive` で取り出して旧・新のサーバを別々に立て、同じデータを
入れて `.my-sde` の高さを突き合わせている。

| 行 | 旧（HEAD） | 新 |
|---|---|---|
| 詳細ありの予定 | 44.00px | 44.25px |
| 詳細なしの予定 | 26.00px | 26.00px |

**見た目を変えない類いの確認では、目で見比べる前に、DOM の値を
数えて突き合わせる。**

### そのほか

- `mise run lint`・`uv run pytest tests`（427 件）とも通過。
  ゴールデンマスターテストで落ちるものは無かった。
  `tests/test_handler.py` のそれは `app.settings` から読む 8 つの値に
  ついてで、テンプレートの HTML を比較するテストではない
- `GET /ytsched/static/icons/icons.svg` が 200 を返し、`<symbol>` が
  23 個あること
- 一覧・メニューを開いた状態・編集画面（既存・新規）・検索バーを
  `tools/screenshot.py`（TODO-046）で 412px と 800px で撮り、
  アイコンがどこも空白になっていないこと、大きさ・縦位置・行の詰まり
  具合が崩れていないことを確認した
- 読み込み中のしるしはキャプチャに写らないので、`page.evaluate()` で
  `#loadingSpinner` を強制表示して別に撮った
- `mise run build` で作った wheel に `static/icons/icons.svg` が入り、
  `vendor/` が入っていないこと
- 起動の確認は、どちらの担当も `--datadir` を一時ディレクトリに向けて
  行った。実データには触っていない
