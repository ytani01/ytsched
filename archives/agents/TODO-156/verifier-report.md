# TODO-156 verifier 報告

## 静的チェック

- `uv run ruff format --check .` → src/ tests/ は問題なし。
  archives 配下の 2 件の .md（TODO-156 とは無関係の既存ファイル、
  git log で TODO-088・TODO-002 のコミット由来と確認済み）のみ
  reformat 対象。実害なし
- `uv run ruff check .` → All checks passed!
- `uv run basedpyright` → 0 errors, 0 warnings, 0 notes
- `uv run pytest` → 607 passed in 163.11s（test_notify.py の 10 件含む）

## 実動作確認

一時ディレクトリ（scratchpad 配下）に Python で以下を仕込んだ:
- 2026-09-02 09:00-10:00 会議A
- 2026-09-03 14:00- 会議B
- ToDo（期限 2026-09-04）請求書を出す

`ytsched notify --datadir <tmp> --date 2026-09-02 --days 3`:

```
2026-09-02 (水)
  09:00-10:00 会議A

2026-09-03 (木)
  14:00-      会議B

2026-09-04 (金)
  予定なし

期限が近い ToDo
  09-04 請求書を出す
```

○ 3 日分の節が連続して出て、ToDo の節は最後に 1 回だけ。

`ytsched notify --datadir <tmp> --date 2026-09-02 --memo 'テストメモ'`:

```
テストメモ

2026-09-02 (水)
  09:00-10:00 会議A

期限が近い ToDo
  09-04 請求書を出す
```

○ メモが先頭に出る。

`ytsched notify --datadir <tmp> --date 2026-09-02`（`--days` 省略、既定 1）:

```
2026-09-02 (水)
  09:00-10:00 会議A

期限が近い ToDo
  09-04 請求書を出す
```

○ `--memo` 無し版と同じ形（1 日分＋ ToDo）で、これまでの挙動と一致。

## 結論

不具合なし。すべて期待通り。main の判断が要る点は無し。
