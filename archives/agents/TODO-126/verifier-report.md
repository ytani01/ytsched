# TODO-126 verifier-report

## 1. mise run lint

○ 通った。ruff format / ruff check / basedpyright（0 errors）/ mypy
（Success: no issues found in 35 source files）/ eslint すべて通過。

## 2. uv run pytest tests

○ 543 passed in 126.37s（`tests/test_holiday.py` は 7 件通過）。

## 3. --help / 年なしエラー

```
uv run ytsched holiday --help
```
○ ヘルプが出力される。`--datadir`, `--dry-run`, `--url`, `-d` などのオプションが表示される。

```
uv run ytsched holiday --datadir <一時ディレクトリ>
```
○ `Error: Missing argument 'YEARS...'.` で exit code 2（0 で終わらない）。

## 4. file:// CSV での動作確認

`--url file://$(pwd)/tests/data/syukujitsu-sample.csv` を使用。

- `--dry-run 2026`: ○ `足した予定: 3 / 飛ばした予定: 0` と出て、
  `find <datadir> -type f` は空（ファイルが 1 つも作られない）
- 通常実行 `2026`: ○ `2026/01/01.jsonl` `2026/05/03.jsonl` `2026/05/06.jsonl`
  が作成された。`01/01.jsonl` の中身:
  `{"date": "2026-01-01", "time_start": null, "time_end": null,
  "type": "休日", "title": "元日", "place": "", "detail": ""}`
  （type=休日、title=CSV のまま「元日」、time_start/time_end が null、期待通り）
- 同じコマンドを再実行: ○ `足した予定: 0 / 飛ばした予定: 3`。
  3 ファイルとも before/after で行数 1 のまま変化なし（二重登録なし）
- `2026 2030`（2030 は CSV に無い）: ○
  ```
  WARNING holiday.py:167 register()> 2030: no data in CSV .. skipped
  足した予定: 0 / 飛ばした予定: 3 / データが無い年: 2030
  ```
  2030 は「データが無い」と報告され、2026 の処理（飛ばした 3 件）は継続した。
  exit code 0。

## 5. 本物のネットからの取得（--dry-run のみ）

```
uv run ytsched holiday --datadir <一時ディレクトリ> --dry-run 2026
```
○ 実行できた。`足した予定: 18 / 飛ばした予定: 0`。例外・トレースバックなし。

## 見つかった問題

なし。依頼書に書かれた確認はすべて期待通りの結果だった。
