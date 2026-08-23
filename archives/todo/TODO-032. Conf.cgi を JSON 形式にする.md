# TODO-032. `Conf.cgi` を JSON 形式にする

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer + wording
実施: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer + runner + wording
消費: output 38,504 / cache_creation 397,739（main 32% + implementer 25% + reviewer 16% + wording 13% + verifier 9% + runner 4%）

## きっかけ

設定をデータディレクトリの `Conf.cgi` にタブ区切りで置き、自前で 1 行ずつ
分解して読み書きしていた（`ToDo_Days`・`FilterStr`・`SearchStr`・`SearchN`
の 4 つ）。標準ライブラリの `json` に置き換えれば、依存を増やさずに
自前のパーサを消せる。

TODO-011 で一度「対応しない」と決めた件。あのときの主題は TOML 化で、
書き込みに依存が増えることを理由に見送っていた。TODO-011 が挙げた
蒸し返しの条件（設定の値の型が文字列だけで収まらなくなる）は今も
満たしていないが、利用者の判断で進めた。

## やったこと

**`handler.py`（`HandlerBase`）**

- `CONF_FNAME` を `conf.json` へ。`.cgi` は Perl CGI 時代の名残で、
  中身とも合わない
- `load_conf()` を `json.load()` に、`save_conf()` を `json.dump()`
  （`ensure_ascii=False`・`indent=2`・末尾に改行）に置き換え、自前で
  1 行ずつ分解する処理を消した
- **読めない中身でも例外にしない。** 壊れた JSON、トップレベルが
  object でない、値が文字列でないキー、の 3 つは警告を 1 行出して
  無視する（不正な正規表現（TODO-012）・不正な引数（TODO-027）と
  同じ考え方。設定ファイルのせいで画面が出ないほうが困る）。
  ただし**ファイルそのものが読めない場合**（`PermissionError` など）は
  捕まえない。設定の中身の問題ではないため
- **後方互換は残さない。** 旧 `Conf.cgi` が残っていても読みに行かない

**`migrate.py`（`Migrator`）**

- `conv_conf()` / `migrate_conf()` を足し、`ytsched migrate` に載せた。
  JSON Lines への移行と入口を揃えた
- 読み方は予定データと揃えた。バイト列で読んで 1 行ずつデコードする
  （旧データが euc_jp のことがある）。**元の `Conf.cgi` は消さない**。
  `conf.json` が既にあれば警告して飛ばす。`--dry-run` では書かない
- タブの無い行は警告して飛ばす。**予定データと違い `--error-file` には
  出さない**（設定はアプリが書いたもので、行数も数行のため）
- `MigrateStat` に `conf_files` / `skipped_conf_files` を足し、
  `設定ファイル    : 変換 N, 飛ばした N` の 1 行を出力に足した
- `handler.py` は import しない。移行ツールに tornado への依存を
  持ち込まないため、ファイル名は `Migrator` 側に持つ

**変えなかったところ**

値は文字列のまま保存する。`main_handler.py` の `get_conf_arg()` /
`convert_value()` の変換をそのまま使い、形式の変更だけに範囲を絞った
（数値を `int` で持つと、不正な値を保存しない扱い（TODO-027）にも
手を入れることになる）。`main_handler.py` の差分はコメントと docstring
だけになっている。

## テスト

`pytest` 412 件（1 件増）。

- `tests/test_migrate.py` — 設定の移行を 6 件足した（変換、euc_jp の値、
  タブの無い行、`conf.json` が既にある、`Conf.cgi` が無い、`--dry-run`）。
  合成データ `tests/data/old_format/` には `Conf.cgi` を置かず、テストの
  中で一時ディレクトリへ書く。あちらは予定データの壊れ方を再現するもの
- `tests/test_handler.py` — タブ特有の 3 件（空行、タブの無い行、値に
  タブ）を JSON 版に差し替えた（壊れた JSON、object でない、値が文字列で
  ない、utf-8 で読めない）。値にタブや改行を含む往復のテストは残した
- `tests/test_main_handler.py` / `tests/test_web.py` — 設定ファイルを直に
  読み書きしているところを JSON にした。見ている中身は変えていない

`verifier` が実際に動かして確かめた（`archives/agents/TODO-032/verifier-report.md`）。
移行 → アプリ起動 → 画面から設定変更 → 壊れた `conf.json` の 4 系統で、
不具合は見つからなかった。euc_jp の `FilterStr` が画面に正しく出ることも
確認している。

## 担当

`implementer` が**セッションの上限に当たって途中で終わった**ため、main が
作業ツリーを引き継いだ。`reviewer` の指摘 10 件のうち 7 件を直し、
2 件は対応しないと判断、1 件は方針を変えずに明記した。分担の理由と
指摘の採否は [`archives/agents/TODO-032/README.md`](../agents/TODO-032/README.md)
にある。
