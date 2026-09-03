# TODO-170 verifier 報告

## 1. mise run fmt / typecheck / lint / test

- `mise run fmt` — ○（43 files left unchanged, ruff check All checks passed!）
- `mise run typecheck` — ○（basedpyright 0 errors/0 warnings/0 notes、mypy Success: no issues found in 40 source files）
- `mise run lint` — ○（typecheck・fmtjs・lintjs すべて通過）
- `mise run test` — ○ **633 件パス**（`tests/test_fix_id.py` 13 件含む）

`mise run upgradeproject` は走らせていない。

## 2. 実データのコピーで確認

`\cp -a ~/ytsched/data <tmp>/data` でコピー。`diff -rq ~/ytsched/data <tmp>/data`
は差分なし（コピー直後）。元の `~/ytsched/data` には書き込んでいない
（作業後も `diff -rq` で元データが手つかずであることを確認済み）。

### 事前カウント（main の見込みとの比較）

依頼書記載の見込み: UUID 6 件 / 非UUID 13418 件 / 非UUIDを含むファイル 6555 個 /
`.jsonl` 6739 ファイル・13429 行。

実測（`SchedDataFile.split_lines()` で正しく分割してカウント）:

- `.jsonl` ファイル総数: 6739（`find -name "*.jsonl"`。`trash.jsonl` 1・
  `ToDo.jsonl` 1・日次 6737 の内訳）
- fix-id が走査する対象（日次 6737 + `ToDo.jsonl` 1）: **6738 ファイル**
- 総行数: **13424 行**（見込みの 13429 と 5 行ずれる。差の原因は未調査。
  `str.splitlines()` で数えると Unicode 行区切り文字の混入で行数が
  ずれることがあるため、見込み側の数え方の違いの可能性がある）
- 非 UUID: **13418 行**（見込みと一致）、UUID: 6 行（見込みと一致）、
  非UUIDを含むファイル: 6555 個（見込みと一致）

（注）自分の最初の検証スクリプトは Python 標準の `str.splitlines()` を
使ったため、`detail` に長い文字列を含む 1 行を誤って複数行に見せてしまい、
一時的に「読めない行がある」ように見えた。`docs`/コードのコメント通り、
`SchedDataFile.split_lines()`（`\n` のみで分割）で数え直したところ矛盾は
解消した。fix-id 自体の不具合ではない。

### dry-run

```
uv run ytsched fix-id --datadir <tmp>/data --dry-run
```

出力:
```
===== dry run: 書き出していません =====
走査したファイル: 6738
書き換えたファイル: 6555
書き換えた行    : 13418
元から UUID の行: 6
読めなかった行  : 0
```

`diff -rq ~/ytsched/data <tmp>/data` — dry-run 後も差分なし（1 バイトも
変わっていない）。

### 本番実行

同じコマンドを `--dry-run` 無しで実行。件数は dry-run と完全一致
（走査 6738 / 書換ファイル 6555 / 書換行 13418 / 元UUID 6 / 読めない行 0）。

以下を `SchedDataFile.split_lines()` ベースで検証（`json.loads` して
`sde_id` を除いた残りのキー・値・並び順を比較）:

- 全 6738 ファイル・13424 行で **`sde_id` 以外の不一致 0 件**
- ファイルごとの行数不一致 **0 件**
- 実行後、非 UUID の `sde_id` が残っている行 **0 件**
- `sde_id` の一意性: 総 13424 件がすべて相異なる UUID（重複 0）
- `trash.jsonl` は `diff` で不変を確認

### 2 回目の実行

```
uv run ytsched fix-id --datadir <tmp>/data
```
```
走査したファイル: 6738
書き換えたファイル: 0
書き換えた行    : 0
元から UUID の行: 13424
読めなかった行  : 0
```
1 件も書き換わらないことを確認。

## 3. 書き換え後データで Web アプリ

`uv run ytsched webapp --datadir <tmp>/data -p 18765` を起動（`--datadir`
に実データは指定していない）。

- `GET /ytsched/` → 200、`GET /ytsched/edit?date=...&sde_id=<UUID>` → 200、
  `GET /ytsched/trash` → 200。いずれも取得した HTML に生の `{{ }}` / `{%` は
  残っていない
- （`GET /search`・`/edit`・`/trash`（`/ytsched` プレフィックス無し）は
  404。これは `url_prefix` の既定値 `/ytsched` によるもので、fix-id とは
  無関係）
- 実データの 1 件（`2021-03-19` の `fee7eb92-...`）を編集画面と同じ形の
  `POST /ytsched`（`cmd=update`）で書き換え、`detail` が
  `"verifier-test-edit"` に変わったことをファイルで確認。302 で編集画面へ
  リダイレクトされ、`sde_id` は保存前後で不変（UUID が保たれている）
- サーバログ（`webapp.log`）に例外・トレースバックは出ていない
  （404 のアクセスログのみ）
- 確認後、プロセスを `pgrep -fa` で確認して `kill` で停止済み

## まとめ

不具合は見つからなかった。上記「事前カウント」の行数の 5 行のずれ
（13424 vs 見込み 13429）だけ、原因未特定のまま報告する
（fix-id の書き換え結果自体には矛盾が無く、実害は確認できていない）。
