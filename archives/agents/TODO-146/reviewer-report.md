# TODO-146 reviewer 報告

## 確認した内容

- `main.html` / `edit.html` / `trash.html` / `sde.html` の全ての折りたたみ箇所を、
  変更前の `class="..."` を 1 プロパティずつ手で展開し、`.row > *` の
  `min-width: 0` とガター由来パディングの上書き有無（`p-0`/`p-1`/`p-2`/`m-0`/`m-1`
  の有無による違い、特に `p-*` が無い列でガターパディングが残るケース）まで
  含めて、新しい役割クラスの計算値と突き合わせた。すべて一致した
  （`.my-week-bar` `.my-menu-bar`〔z-index 200 で fixed-bottom の 1030 を
  正しく打ち消す〕`.my-trash-header-row`〔m-0/m-1 が無く負のガター margin が
  残る点〕`.my-version-info`〔p-0 が無くガターpaddingのまま〕
  `.my-edit-time-col`〔同じく〕`.my-trash-back-col`/`.my-trash-title-col` など）
- `.my-row-middle > .text-end` → `.my-row-end` の畳み込みは 3 箇所
  （検索欄の列、ゴミ箱ヘッダーの選択列・削除列）とも、親が `.my-row-middle`
  を保持したままで、対象の div にだけ `my-row-end` が付いており一致
- `.my-longtext` の `min-width: 0` は自身のクラスへ直接持たせる形になり、
  「`.row` の直接の子であること」への依存は無くなっている（グリッドの子
  であることへの依存は残るが、これは折りたたみ前と同じ制約）
- `!important` を使っていた `.d-none` は `.my-menu-sw-hidden` /
  `.my-longtext-sw` に分かれ、どちらも単独セレクタで他と競合しないことを
  確認した。`#menu-sw:checked ~ .my-bar-content` や
  `.my-longtext-sw:checked ~ .my-longtext` は詳細度で単純な役割クラスに
  勝つ構造なので、ソース順に依存しない（これは以前から）
- 命名は既存の `my-sde-*` `my-date-*` `my-menu-*` の付け方と揃っており、
  `my-footer-*` `my-trash-entry-summary` など新設の名前も役割を表している。
  残した修飾クラス（`my-align-middle` / `my-fw-bold` / `my-row-end`）の
  理由も妥当
- 使われていない定義・定義の無いクラスは見当たらなかった
  （`my-mini-cal-wdays` は対象外の `mini_cal.html` にある既存の問題で、
  今回の変更とは無関係）
- `base.html` / `mini_cal.html` / `month.html` は無変更であることを確認した
- JS ファイルは旧クラス名（`container-fluid` `d-none` `longtext-sw` など）を
  参照していないことを確認した

## 指摘

### 1. ライセンス表記の値の列挙に漏れがある（確信度高）

`src/ytsched/webroot/static/css/my.css` 先頭コメント（1〜28 行目）。

`.my-sde`（939 行目）に `border: 1px solid #dee2e6;` が残っている。これは
旧 `.border` ユーティリティの値で、TODO-146 の本文が挙げた「写した値」の
一覧にも `border の #dee2e6` と明記されている。ところが書き直した後の
先頭コメントは、`.my-error-box` の配色・`border-radius: .375rem`・
`z-index: 1030`・ガター `1.5rem` は挙げているが、この `#dee2e6` には
触れていない。値そのものは残っているのに、列挙から抜け落ちている。
依頼の見てほしいこと 8「写した値の列挙に漏れが無いか」に直接あたる。

## 確信度が低い指摘

### 2. 実装者報告と実際の差分が食い違っている

`archives/agents/TODO-146/implementer-report.md` の「残る懸念」は
`tools/screenshot.py` の `DEF_TOGGLE = "input.longtext-sw"` を
「直していない」としているが、実際の作業ツリーでは
`input.my-longtext-sw` に直されており（`docs/Developer.md` の該当箇所も
`input.my-longtext-sw` に書き換わっている）、内容自体は正しい。
報告が実際の変更を反映していないだけなので、コードの問題ではないが、
念のため記す。

### 3. `my.css` に古いコメントの消し残りがある

`.my-sde`（930〜931 行目）・`.my-sde-time`（980〜981 行目）・
`.my-sde-detail-sw`（1023〜1024 行目）で、書き直す前のコメント行と
書き直した後のコメント行が両方残っている（例: 「予定 1 件分の枠。
font-size: 0 は…」の直後に「予定 1 件分の枠 (旧 container-fluid p-0
border)。…」が続く）。見た目には影響しないが、読みにくい。
