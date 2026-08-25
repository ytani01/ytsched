# TODO-047 verifier 報告

## 1. lint

`mise run lint` → ruff format 24 files left unchanged / ruff check All checks
passed / basedpyright 0 errors,0 warnings,0 notes / mypy Success（21 files）。

## 2. pytest

`uv run pytest tests` → **418 passed**（実装者の報告と同数）。

## 3. アプリの起動

```
echo '{}' > <一時ディレクトリ>/conf.json   # search_str のリセット
uv run ytsched webapp --datadir <一時ディレクトリ> --port 10089
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:10089/ytsched/
```

→ `200`。

## 4. HTML

- `grep -n bootstrap index.html` → 0 件（`<link>` が消えている）
- Font Awesome の `<link>`（`vendor/fontawesome/css/all.css`）は残っている
- `{{ }}` `{%` の生残り → 0 件
- `GET /ytsched/static/css/my.css` → `200`
- `GET /ytsched/static/vendor/bootstrap/bootstrap.min.css` → `404`

## 5. サーバのログ

`server.log` に traceback / exception の行 → 0 件（ログ自体 2 行のみ）。

## 6. キャプチャの見比べ

`git stash` は使わず、作業ツリーはそのまま。既存の `todo047-before-*` /
`todo047-cmpbefore-*` はそのまま使い、変更後だけ自分で撮り直した
（`env -u DISPLAY uv run --with playwright python tools/screenshot.py`、
撮る前に毎回 `conf.json` を `{}` に戻す）。`todo047-verify-{main,open,
menu,edit,search}_*` として `~/tmp/playwright-mcp/` に保存（幅 412px・
800px、既存ファイルは削除していない）。

`compare -metric AE` で画素差を出し、ずれた箇所は拡大して目で確認した。

| 比較 | 画素差(AE) | 見た目 |
|------|-----------|--------|
| before-main_closed vs verify-main_closed（800） | 17141 | 今日の日付ブロックの赤・下段時計の blink 位相差のみ。レイアウト差なし |
| before-main_open vs verify-open_open（800） | 19776 | 同上 |
| cmpbefore-menu_open vs verify-menu_open（800） | 18376 | 同上。メニュー展開後のフッタ（バージョン表示など）も一致 |
| cmpbefore-menu_closed vs verify-menu_closed（800） | 17133 | 同上 |
| cmpbefore-edit_closed vs verify-edit_closed（800） | **27** | `(Tue)` の文字ふちのアンチエイリアスのみ。実装者の報告と同じ 27 画素 |
| before-search_closed vs verify-search_closed（800） | 1082 | 日付ブロックの blink 位相差と、`(キャンセル)` の取り消し線まわりのみ。レイアウト差なし |

いずれも 412px 幅でも同様の傾向。**レイアウト・配置が変わったと見える
箇所は無かった。** 実装者の報告（意図した差は 3 つのみ）と矛盾しない
結果。

## 気づいたこと（判断は main へ）

- `todo047-before-alert_*` と `todo047-verify-search_*` を比べると画素差が
  56 万を超えるが、これは「alert」状態が検索とは別のキャプチャ（検索
  結果 0 件時の `alert-danger` 表示）であるためで、依頼書の 5 通りには
  含まれない。今回の確認対象ではないので実施していない
