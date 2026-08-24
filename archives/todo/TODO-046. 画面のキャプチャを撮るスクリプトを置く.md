# TODO-046. 画面のキャプチャを撮るスクリプトを置く

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Opus 5 | main + verifier |
| 消費 | output 9,275 / cache_creation 52,191 / 概算 $1.3 |
|      | main 83% + verifier 17%（料金の割合） |

依頼と報告は `archives/agents/TODO-046/` にある。

## きっかけ

見た目を変える項目では、テストだけでは確かめられず、画面を見るしかない
（TODO-042・TODO-043・TODO-045）。そのたびに playwright を動かす短い
コードを書き直していたので、まとめた。

TODO-045 で、`~/.cache/ms-playwright` にあるビルドが起動しないことも
分かった。その回避もスクリプト側に持たせる。

## やったこと

### `tools/screenshot.py`

引数は URL・幅・出力先。ファイル名は
`{prefix}_{closed|open}_{幅}.png`。

- 幅は既定で 412px（スマホ）と 800px の 2 つ。`-w` を複数回渡して変える
- `--open` を付けると、開閉するものを開いた状態も撮る。開くものは
  `--toggle`（既定は詳細の開閉スイッチ `input.longtext-sw`）
- 保存先の既定は `~/tmp/playwright-mcp/`。利用者に画像を見せるときの
  置き場所に合わせた
- 失敗したときは終了ステータス 1 で、何を確かめればよいかを出す。
  アプリが動いていないとき、ブラウザが見つからないときの 2 つ

### ブラウザの選び方

`executable_path` にシステムの `/usr/bin/chromium` を渡す。

`~/.cache/ms-playwright` にあるのは `chromium-1200`（約 900MB）で、
playwright-mcp が入れたものと思われる。`uv run --with playwright` は
そのつど最新の playwright を取ってくるので、要求するビルドがずれて
起動しない（TODO-045 で実際に起きた）。

`playwright install` で入れ直す案もあったが、さらに 900MB を使ううえ、
playwright が上がればまたずれる。版を固定する案は playwright-mcp 側の
更新に引きずられる。追加のダウンロードが要らず、ずれが再発しないので、
システムの chromium を使うことにした。このアプリを実際に見るブラウザも
同じ chromium なので、見た目の確認としてはむしろ実態に近い。

### 依存とタスク

playwright は dev 依存に入れず、`uv run --with playwright` でそのつど
用意する。`mise run upgradeproject` が触る依存を増やさないため。
`mise.toml` に `shot` タスクを足した。

mypy には `ignore_missing_imports` の対象として `playwright` を足した。
basedpyright は `reportMissingImports = "none"` なので設定は要らない。

使い方は `docs/Developer.md` の「画面を撮る」に書いた。タスクの一覧に
`tokens` が抜けていたので、それも足した。

## テスト

verifier に確認させた（`archives/agents/TODO-046/verifier-report.md`）。

- `mise run lint`（ruff format / ruff check / basedpyright / mypy）… 問題なし
- `uv run pytest` … 418 件通過
- `--help` が出ること
- 一時ディレクトリにデータを置いてアプリを起動し、`--open` で 4 枚
  （幅 2 つ × 閉・開）が保存されること。`file` で PNG として壊れて
  いないこと、閉じたときは詳細が 1 行、開いたときは 3 行になっていること
- `mise run shot` 経由でも同じに動くこと
- 失敗時の振る舞い。アプリが動いていない URL と、存在しない
  `--chromium` の 2 つで、終了ステータス 1 と意味の分かるメッセージ
- `docs/Developer.md` の手順をそのままなぞれること
