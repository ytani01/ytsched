# TODO-045. 詳細（detail）の見え方を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Opus 5 | main + verifier |
| 消費 | output 11,539 / cache_creation 54,117 / 概算 $1.3 |
|      | main 85% + verifier 15%（料金の割合） |

依頼と報告は `archives/agents/TODO-045/` にある。

## きっかけ

一覧に並ぶ予定の詳細（detail）の見え方に、2 つ気になるところがあった。

- 閉じているとき、詳細が長いと開閉ラベル（`fa-angle-down`）のあとで
  折り返して 2 行になる
- 開いたとき、詳細の前後に空行が入る

## やったこと

### 閉じているときに 2 行になる

原因は `my.css` の `.longtext` にあった `width: auto`。Bootstrap の
`col-11` が付けている幅を打ち消すので、詳細が長いとその長さまで箱が伸び、
`row` に収まらなくなって折り返していた。`width: auto` をやめ、幅は
`col-11` に任せた。

代わりに `min-width: 0` を入れてある。flex の子は既定が
`min-width: auto` で中身より小さくならず、そのままだと
`text-overflow: ellipsis` が効かないため。開いたときの
`.longtext-sw:checked ~ .longtext` も同じに揃えた。

### 開いたときに前後へ空行が入る

`sde.html` で詳細を `{{ '\n' + detail + '\n' }}` と書いていた。開いた
ときの `.longtext` は `white-space: pre-wrap` なので、この前後の `\n` が
そのまま空行として見えていた。これは TODO-038 で「元からの見え方を保つ」
ために入れたものだったが、今回その見え方をやめると決めた。

`{{ detail }}` にして、開始タグ・終了タグに詰めて置いた。`pre-wrap` では
タグとの間の改行やインデントも見えてしまうので、行を分けられない。
その理由は `sde.html` のコメントに残してある。

## テスト

verifier に確認させた（`archives/agents/TODO-045/verifier-report.md`）。

- `uv run pytest` … 418 件通過
- `uv run ruff check` … 問題なし。`uv run basedpyright` … 0 errors
- `uv run ruff format --check` の指摘は `.py` のみが対象で、今回触った
  `my.css` / `sde.html` は含まれない。以前からの状態で、この項目とは無関係
- 一時ディレクトリにテストデータを置いてアプリを起動し、HTML を取得。
  詳細の div が `tabindex="0">…</div>` の形で、中身の前後に改行・空白が
  入っていないことを確認
- `.longtext` は `sde.html` 以外で使われていないので、他への影響は無い

見た目そのものは HTML では確かめきれないので、main が chromium
（playwright 経由、`executable_path` にシステムの `/usr/bin/chromium` を
指定）で画面を撮って目視で確認した。幅 412px と 800px で、閉じたときに
1 行へ収まって末尾が `…` で切れること、開いたときに前後の空行が無いこと、
複数行の詳細が行数どおりに出ることを確かめている。

- `~/tmp/playwright-mcp/todo045_closed_412.png`
- `~/tmp/playwright-mcp/todo045_open_412.png`
- `~/tmp/playwright-mcp/todo045_closed_800.png`
- `~/tmp/playwright-mcp/todo045_open_800.png`

なお、`~/.cache/ms-playwright` にあるブラウザは playwright の版と合わず
起動しなかった。`executable_path` にシステムの chromium を渡せば動く。
