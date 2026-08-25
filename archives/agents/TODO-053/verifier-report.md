# TODO-053 verifier 報告

## 確認内容と結果

1. アプリ起動（`--datadir` に一時ディレクトリ、`--port 10085`）
   - ○ 起動できた。`curl` で `/ytsched/` `/ytsched/edit/` は 200、
     `/edit/`（前置き無し）は 404 だった

2. 200 の URL で撮れること
   - コマンド: `uv run --with playwright python tools/screenshot.py
     http://localhost:10085/ytsched/ --outdir <一時dir> -p ok`
   - ○ `exit=0`。`ok_closed_412.png`（46K）・`ok_closed_800.png`（49K）が
     できた

3. 404 の URL で PNG ができないこと
   - コマンド: `uv run --with playwright python tools/screenshot.py
     http://localhost:10085/edit/ --outdir <一時dir> -p 404test`
   - ○ 撮る前に同名の古いファイルが無いことを確認済み。実行後も
     `404test_*.png` は作られなかった

4. 404 のときの標準エラーと終了コード
   - ○ 標準エラー:
     ```
     404: http://localhost:10085/edit/
     URL を確かめる。
     ```
   - ○ `exit=1`

5. `uv run pytest tests`
   - ○ 427 件 全て pass（`427 passed in 2.91s`）

6. lint / 型チェック
   - ○ `uv run ruff format --line-length 78 --check tools/screenshot.py`
     → `1 file already formatted`
   - ○ `uv run ruff check --extend-select I tools/screenshot.py`
     → `All checks passed!`
   - ○ `uv run basedpyright tools/screenshot.py`
     → `0 errors, 0 warnings, 0 notes`

## その他

- webapp のログファイルに例外・トレースバックは出ていなかった
  （`grep -i -E "error|exception|traceback"` で該当なし）
- webapp プロセスは確認後に kill 済み。`curl` で接続不可（000）を確認

## 見つかった不具合

なし。依頼書に書かれた確認はすべて期待どおりだった。

## main の判断が要る点

特になし。
