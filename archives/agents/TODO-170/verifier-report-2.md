# TODO-170 verifier 報告（2 回目・修正後）

## 1. mise run fmt / typecheck / lint / test

- `mise run fmt` — ○（43 files left unchanged、ruff check All checks passed!）
- `mise run typecheck` — ○（basedpyright 0/0/0、mypy Success: no issues found in 40 source files）
- `mise run lint` — ○（fmtjs・lintjs・typecheck すべて通過）
- `mise run test` — ○ **637 件パス**（`tests/test_fix_id.py` 17 件。1 回目の 13 件から
  reviewer 対応で 4 件増）

`mise run upgradeproject` は走らせていない。

## 2. 実データのコピーで確認（1 回目と同じ結果か）

`\cp -a ~/ytsched/data <tmp>/data`。コピー直後・dry-run 後とも
`diff -rq ~/ytsched/data <tmp>/data` は差分なし（元データ未変更）。

### dry-run

```
走査したファイル: 6738
書き換えたファイル: 6555
書き換えた行    : 13418
元から UUID の行: 6
読めなかった行  : 0
```
1 回目と完全一致。

### 本番実行

同じ件数で実行。検証（`SchedDataFile.split_lines()` で行単位に分割し、
`json.loads` して `sde_id` を除いた残りのキー・値・並び順を比較する
スクリプトを実行）:

- files: 6738、total_lines: 13424（1 回目と一致）
- `sde_id` 以外の不一致（mismatch）: **0**
- ファイルごとの行数不一致: **0**
- 非 UUID が残っている行: **0**
- `sde_id` の一意性: 総 13424 件がすべて相異なる UUID（重複 0）
- `trash.jsonl` は `diff -q` で不変を確認

### 2 回目の実行

```
走査したファイル: 6738
書き換えたファイル: 0
書き換えた行    : 0
元から UUID の行: 13424
読めなかった行  : 0
```
1 件も書き換わらない。1 回目と同じ。

## 3. Web アプリの起動確認

依頼書の指示どおり省略した。

## まとめ

修正後のコードでも 1 回目の確認と完全に同じ結果になった。不具合は見つからなかった。
