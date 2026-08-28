# TODO-097. `.js` の呼び出し関係をファイル先頭のコメントに書く

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | implementer + verifier |
| 消費 | output 37,873 / cache_creation 447,935 / 概算 $3.1 |
|      | main 57% + implementer 27% + verifier 10% + wording 6%（料金の割合） |

基本設計のレビュー（2026-08-27）の O。分担の理由と各担当の報告は
[archives/agents/TODO-097/](../agents/TODO-097/) にある。挙動は変えていない
（コメントの追加だけ）。

## きっかけ

`static/js/` は ES モジュールにしない方針（TODO-083）なので `import` が
書けず、`base.html` の `<script>` の並び順（state → spinner → gauge →
nav → week → keyboard → swipe）がそのまま暗黙の仕様になっている。順番を
入れ替えても読み込み時には何も起きず、ボタンを押したときに初めて壊れる。
どのファイルが何を外へ出し、何を他ファイル・テンプレートから使っているかを、
各ファイルの先頭にコメントで書いて分かるようにする。

## やったこと

対象 9 ファイル（`state.js` / `spinner.js` / `gauge.js` / `nav.js` /
`week.js` / `keyboard.js` / `swipe.js` / `main-page.js` / `edit-page.js`）の
先頭、既存の `/** (c) ... */` と `// 〜 (TODO-0xx)` の 1 行説明の直後に、
「外へ出すもの」「外から使うもの」を並べた `//` コメントを足した。

- 依存は `static/js/` 全体と `templates/` を grep して洗い出した。実際の
  関数呼び出しと、HTML 属性のイベントハンドラ（`onmousedown=` など）だけを
  採り、コメント内の言及は除いた。
- 「外へ出すもの」には、他 `.js` から呼ばれる関数と、HTML テンプレート
  （`main.html` / `edit.html` / `sde.html`）の `on*` 属性から呼ばれる関数を
  挙げた。どちらからも参照が無いものは「このファイル内だけで使う」とまとめた。
- 「外から使うもの」に挙げたのは、他 `.js` のトップレベル名と、`base.html` /
  `main.html` の `<script>` 内の定数（`url_prefix` / `search_str0` /
  `today_str` / `auto_turn_msec`）だけ。DOM 要素の id は全ファイルが多数
  触るので挙げていない。
- `gauge.js` / `nav.js` / `week.js` は `base.html` であとに読み込まれる
  ファイルの関数を呼ぶ。実行時にしか呼ばれず前方参照でよい、という 1 行を
  この 3 ファイルのコメントに添えた。
- `keyboard.js` の `keyHdr` 内の `today_str` は関数ローカルの変数で、
  `main.html` の `today_str` とは別物。紛らわしいので 1 行注記した。

### TODO.md の表になかった依存（想定と違ったもの）

TODO.md の表は代表例だけだった。grep で次が追加で見つかった。

- `gauge.js` → `nav.js` の `scrollToDate()`（`gaugeBarClickHdr` 内）。
- `week.js` → `nav.js` の `getLocaltimeDateString` / `getLocaltimeString` /
  `shiftDays` / `pushDateInUrl` / `doGet`。
- `swipe.js` → `week.js` の `hasAdjacentWeek()`、`state.js` の `ytState`。

### main が着手後に直したこと

verifier が挙げた、まとめすぎで実態より広く読める箇所 4 点を main が
直した（コメントのみ）。

- `nav.js`: `shiftDays` / `getLocaltimeString` / `getLocaltimeDateString` /
  `calcDays` を利用元ごとに分けた。`doGet` は 3 テンプレート + `week.js` +
  `main-page.js`、`doPost` は `main.html` + `main-page.js`、`doSubmit` /
  `doGetDate` は `main.html` だけ、と関数ごとに分けた。
- `gauge.js`: 「外から使うもの（すべて nav.js …）」の見出しが `ytState`
  の行と食い違っていたので、見出しを直し各行に定義元のファイルを付けた。
- `edit-page.js`: `changeDetailHeight()` は自身を `load` に登録して
  いないので、「別の load ハンドラから呼ぶ」に直した。

## テスト

- `mise run fmt` 通過（ruff format: 31 files unchanged / ruff check: All
  checks passed）。
- `mise run lint` 通過（ESLint 指摘なし、basedpyright 0 errors、mypy
  Success）。
- `mise run test`。`tests/test_browser.py::test_tap_again_stops_auto_page_turn`
  が断続的に落ちる（`AssertionError: assert '2026-09-21' == '2026-09-14'`）。
  verifier が `git stash` でコメント追加前のクリーンな作業ツリーに戻して
  検証したところ、単体・全体とも通り、`git stash pop` 後の再実行では
  481 passed。自動ページ送り（TODO-084）のタイミング依存の flaky で、
  コメントのみの本変更とは無関係。`test_browser.py` はこの項目で触って
  いない。
- `git diff` は 122 行の追加のみ・削除ゼロ。追加行はすべて `//` コメントで、
  コードには手が入っていない（main の修正後は追加行がやや減る）。
