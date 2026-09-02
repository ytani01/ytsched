# TODO-165 verifier 報告

## 1. `uv run pytest`（全件）

○ 614 passed in 181.46s

```
uv run pytest -q
```

## 2. lint・型チェック

- `uv run ruff check .` → ○ All checks passed!
- `uv run ruff format --check src tests` → ○ 37 files already formatted
  （`uv run ruff format --check .` だと archives/ 配下 9 ファイルが
  未整形と出るが、これは既存の対象外ファイル）
- `uv run basedpyright` → ○ 0 errors, 0 warnings, 0 notes

## 3. `tests/test_browser.py -k home_button` を 3 回連続

- 1 回目: `7 passed, 52 deselected in 21.04s`
- 2 回目: `7 passed, 52 deselected in 21.24s`
- 3 回目: `7 passed, 52 deselected in 20.77s`

○ 3 回とも 7 件全通過、skip なし。

```
uv run pytest tests/test_browser.py -k home_button -q
```
（3 回とも同じコマンド）

## 4. アプリの起動

```
uv run ytsched webapp --datadir <一時ディレクトリ> --port 18765
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18765/
```

○ `200`。サーバログ（`webapp.log`）に例外・トレースバックなし
（`start server: run forever ..` の INFO のみ）。
確認後 `pgrep -f` で PID を確かめて kill 済み。

## 判断が要る点

なし。4 項目すべて問題なし。
