# TODO-067. フッターの入力欄とアイコンの縦位置を揃える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier + wording |
| 実施 | Opus 5 / effort high | main + verifier + wording |
| 消費 | output 39,334 / cache_creation 242,943 / 概算 $6.0 |
|      | main 91% + verifier 6% + wording 3%（料金の割合） |

分担の理由と各担当の報告は
[archives/agents/TODO-067/](../agents/TODO-067/README.md) にある。

## きっかけ

2026-08-26 に、利用者から挙がった。フッターの入力欄とアイコンの縦位置が
揃っていない。幅 412px で測った、直す前のずれ（数字は要素の上下の中心）。

| 要素 | 直す前 | 直したあと |
|------|--------|------------|
| 上段 date 入力欄 | 834.3 | 840.0 |
| 上段 list アイコン | 830.3 | 840.0 |
| 上段 select | 834.1 | 840.0 |
| 上段 filter アイコン | 833.3 | 840.0 |
| 上段 filter 入力欄 | 841.2 | 840.0 |
| 下段 bars | 872.0 | 877.0 |
| 下段 chevron | 873.0 | 877.0 |
| 下段 home | 873.2 | 877.0 |
| 下段 search アイコン | 872.0 | 877.0 |
| 下段 search 入力欄 | 875.8 | 877.0 |

原因は 3 つあり、3 つとも直した。

## やったこと

### 1. `align-middle` が SVG アイコンに効いていなかった

`my.css` の `.align-middle`（`vertical-align: middle`）と `.my-icon`
（`vertical-align: -0.125em`）は詳細度が同じで、後ろにある `.my-icon` が
勝っていた。テンプレートは `class="my-icon my-icon-lg align-middle"` と
書いているのに、computed 値は `-2px` だった。

**`.align-middle` と `.align-bottom` を、ユーティリティの節から
`.my-icon*` の後ろへ移した。** 詳細度をいじる（`svg.align-middle` に
するなど）より、順番で解決するほうがこのファイルの書き方に合っている
（ユーティリティの節の先頭にも「この中でも順番に意味がある」と書いてある）。
移した理由はその場にコメントで残した。

`align-middle` / `align-bottom` はフッター以外でも使っているので、
そちらも撮って確かめた（下記「テスト」）。

### 2. アイコンの大きさと、親の文字の大きさがバラバラだった

フッターのアイコンを、全部 `my-icon-lg`（1.25em）に揃えた。

- chevron-left / chevron-right … `my-icon`（1em、16px）→ `my-icon-lg`
- filter … `my-icon-2x`（2em）→ `my-icon-lg`

filter の列は親の div が `my-fs-small`（13px）で、search の列
（`my-fs-medium`、16px）と違っていた。**filter の列を `my-fs-medium` に
して、入力欄のほうに `my-fs-small` を付けた**（search の列と同じ形）。
これでフッターのアイコンは全部 20px になった。

### 3. 縦の揃えを `vertical-align` に頼っていた

`.row` は Grid で、列は `align-self: stretch` で行の高さいっぱいになる。
その中身をインラインのまま `vertical-align` で揃えると、高さの違う要素
（入力欄 25.5px・select 21px・アイコン 20px）は中心で揃わない。

`.my-row-middle` を足して、付けた行の列を
`display: flex; align-items: center` にした。フッターの 2 つの行
（メニューバーと、date・todo_days・filter の行）に付けている。

- 入力欄とアイコンは `form` の中にあり、列から見ると孫なので、
  **列だけでなく `form` にも同じ指定が要る**。bars を包む `label` も同じ
- flex にすると要素の間の空白が消えるので、`gap: 0.25em` で戻した
- `text-end` の列は `justify-content: flex-end` にする

`Version …` / `(c) 2020 …` の行には付けていない。文字だけの行で揃える
ものが無く、flex にすると `Version` と `({{ cache_size }})` の間の空白が
消えてしまう。

## やらなかったこと

**横位置の不揃い**（列の幅と `text-center` の組み合わせで、列ごとに中身の
寄り方が違う）は、立てたときから「この項目では扱わない」としていた。
今回も触っていない。

## テスト

- 幅 412px で、要素の上下の中心を playwright で測って確かめた
  （上の表）。**上段は 12 要素すべて 840.0、下段はすべて 877.0 で揃った**
- `mise run shot -- --width 412 --toggle '#menu-sw' --open` で、
  メニューを開いた状態と閉じた状態を撮って見比べた
- `mise run lint` / `mise run test`（444 件）はすべて通る

## フッター以外への影響

`align-middle` / `align-bottom` を効くようにしたので、**フッター以外の
見た目も変わった**。

| 画面 | 要素 | ずれ |
|------|------|------|
| 検索結果（`main.html` の検索期間の行） | search・circle-up-fill | 2.77px 下 |
| 編集画面（`edit.html`） | circle-up・dot-circle・circle-down | 4.5px 下 |

**どちらもそのままにした。** 編集画面の 3 つは、同じ行の日付入力欄との
縦位置が近くなっていて、むしろ見やすくなっている。検索結果のほうは
2.77px で、並びの意味は変わらない。

**main は最初、この 2 つを撮り比べて「見た目は変わっていない」と判断
したが、これは誤りだった。** 数 px のずれは、画面を並べて目で見ても
気づけない。verifier が変更前のコードを別ポートで起動して
`getBoundingClientRect()` と画素差分で比べ、実際にはずれていることを
見つけた（[verifier-report.md](../agents/TODO-067/verifier-report.md)）。
**見た目の確認は、撮って見るだけでなく数字で比べること。**

## 文書の確認 (wording)

前例の無い語は 2 語（`justify-content`・`my-row-middle`）。前者は CSS の
プロパティ名、後者は今回足したクラス名で、どちらも言い回しの造語では
ない。**書き直したところは無い。**
