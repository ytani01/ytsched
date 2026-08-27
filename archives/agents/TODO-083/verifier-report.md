# TODO-083 verifier 報告

## テスト・静的解析

- `uv run pytest tests -q` — 475 passed（skip なし）
- `uv run pytest tests/test_browser.py -q` — 19 passed（skip なし。chromium あり）
- `mise run lint` — ruff format 28 files unchanged / ruff check All checks
  passed
- `mise run typecheck` — basedpyright 0 errors / mypy Success（25 files）
- `mise run fmt --check` は `--check` が mise 側のタスク定義に無く
  ruff のエラーになった（`fmt` 自体は上の lint 実行で確認済み。
  依頼書の「相当」の扱いとして許容範囲と判断）

## アプリ起動確認

`--datadir` に一時ディレクトリを指定して起動（port 18765）。

- `/ytsched/static/js/{state,spinner,gauge,nav,week,keyboard,swipe,main-page}.js`
  — 8 本すべて 200
- Playwright でトップページ (`/ytsched/`) と `edit/` を開き、console/pageerror
  を収集 — どちらも 0 件（`console.log` の通常ログのみ）
- トップページで `#main` が visible = True
- 起動ログに例外・トレースバックなし

## コード突き合わせ

- `git show HEAD:...my.js` と新 8 本を突き合わせ。宣言一覧
  （`function`/`const`/`let`）の差分は、`ytState` への集約対象 5 つ
  （`elLoadingSpinner` / `elMain` / `elGaugeR0` / `elWeekWrap` /
  `activeWeekOffset`）が消えて `const ytState` が増えただけ。他の欠落・
  追加なし
- コメント・空行を除いた本文を、`ytState.` を取り除いて正規化し diff。
  差分は上記 5 つの宣言行が無くなっただけで、それ以外は 1 文字も違わない
- `main.html` / `main-page.js` / `edit.html` / `base.html` の diff を確認。
  `search_str0` / `today_str` / `url_prefix` の置き換え、
  `cur_day.value` → `document.getElementById("cur_day").value`、
  `ytState.elLoadingSpinner` の書き換えは依頼どおり
- レンダリング後の HTML に `{{` `{%` の生残りなし。`search_str0` /
  `today_str` の値も正しく埋まっていた（`today_str = '2026-08-27'`）

## 判断が要る点

とくになし。挙動を変えずに分割できていることを確認した。
