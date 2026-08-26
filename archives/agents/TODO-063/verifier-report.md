# TODO-063 verifier 報告

## 1. 差分の確認

`git diff -- src/ytsched/webroot/static/js/my.js` は依頼書
（`archives/agents/TODO-063/request.md`）の内容と一致していた
（`moveToMonday()` の `days` の計算だけを変更）。

## 2. `mise run lint` / `mise run test`

```
mise run lint
mise run test
```

- `ruff format`: 25 files left unchanged
- `ruff check`: All checks passed!
- `basedpyright`: 0 errors, 0 warnings, 0 notes
- `mypy`: Success: no issues found in 22 source files
- `pytest`: 439 passed in 3.66s

いずれも OK。`mise run upgradeproject` は走らせていない。

## 3. ブラウザでの確認

`--datadir /tmp/todo063-datadir`（一時ディレクトリ）、ポート 18063 で
`uv run ytsched webapp` を起動し、`uv run --with playwright` で
`/usr/bin/chromium`（headless）を操作。今日（2026-08-26、水曜）扱いで
確認した。

- HTTP 200（`/ytsched/`）
- ホームボタン → `#cur_day`・`date=` とも `2026-08-26`
- 左の矢印（`#back_button`、◀）→ `#cur_day`・`date=` とも
  `2026-08-17`（前の週の月曜）。console ログでも
  `moveToMonday:days=-9` → `d1_str=2026-08-17` を確認
- そこから右の矢印（`#forward_button`、▶）→ `2026-08-24`
  （元の週の月曜、`days=7`）
- もう一度右の矢印 → `2026-08-31`（次の週、`days=7`）
- 月曜（`2026-08-17`・`2026-08-24`）を表示している状態からの前後
  矢印も、上の手順の中で実際に確かめた（いずれも問題なし）
- URL の `date=` と `#cur_day`（画面側の状態）は毎回一致していた
  （TODO-049 のような、URL だけ変わって画面が変わらない退行は無し）
- サーバのログ（`/tmp/todo063-webapp.log`）に例外・トレースバックは
  無し。ブラウザの console にも error は出ていない

### 変更前のコードで再現すること

リポジトリのファイルは変更せず、Playwright の `page.route()` で
`my.js` のレスポンス本文だけを変更前の `moveToMonday()` の分岐に
置き換えて確認した。同じ手順（ホーム → 左の矢印）で、
`moveToMonday:days=-2` → `d1_str=2026-08-24`（表示していた週と
同じ月曜のまま）となり、依頼書の症状が実際に再現することを確認した。

## 使ったコマンド

```
mise run lint
mise run test
mkdir -p /tmp/todo063-datadir
uv run ytsched webapp --port 18063 --datadir /tmp/todo063-datadir
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18063/ytsched/
uv run --with playwright python /tmp/todo063-test.py       # 変更後の確認
uv run --with playwright python /tmp/todo063-test-old3.py  # 変更前の再現
```

（`/tmp/todo063-test*.py` はリポジトリ外の一時ファイル。動作確認用の
スクリプトなので報告には残さず、必要なら再現手順の説明で足りると判断した）

## 判断が要る点

特になし。動作・テストとも依頼どおりだった。
