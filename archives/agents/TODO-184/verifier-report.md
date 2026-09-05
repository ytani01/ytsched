# TODO-184 確認報告（verifier）

## 実行したコマンド

```
mise run fmt
mise run lint
mise run typecheck
mise run test
```

## 結果

- `mise run fmt` — ○（ruff format 43 files left unchanged / ruff check All checks passed!）
- `mise run lint` — ○（prettier 全ファイル unchanged、eslint 通過、typecheck 0 errors、mypy Success: no issues found in 40 source files）
- `mise run typecheck` — ○（`mise run lint` に含まれる形で実行、上記と同じ）
- `mise run test` — ○（679 passed in 218.59s）

## アプリの起動確認

```
uv run ytsched webapp --datadir /tmp/ytsched-verify-184
curl -s -o /tmp/ytsched-verify-184.html -w "HTTP %{http_code}\n" http://127.0.0.1:10085/ytsched/
```

- HTTP 200
- 取得した HTML に `{{` `{%` の生残りなし（grep -c で 0 件）
- サーバログに例外・トレースバックなし。1 件だけ既存の警告
  `ToDo_Days='1y': invalid literal for int() with base 10: '1y' .. ignored`
  が出たが、これはテストデータ由来で TODO-184 の変更とは無関係
- 確認後、起動したプロセスは kill 済み

## diff の内容確認（依頼の 1〜5）

`git diff -- src/ytsched/webroot/static/js/main-page.js src/ytsched/webroot/static/js/week.js` を読んだ。

1. `fillMainHeight()`（main-page.js）は測る前に
   `ytsched.ytState.elMain.style.minHeight = "";` を実行してから
   `body_h` / `win_h` を測っている。○
2. `week.js` の `setActiveWeek()` では、`ytsched.scrollToId(...)` の直後
  （次の行）に `ytsched.fillMainHeight();` を呼んでいる。○
   （呼び出し順は scrollToId → fillMainHeight）
3. `window.addEventListener("resize", ytsched.fillMainHeight);` と
   `window.addEventListener("orientationchange", ytsched.fillMainHeight);`
   がファイル末尾の IIFE 内に追加されている。○
4. `onloadHdr()` の分岐は、`body_h < win_h` のときに
   `fillMainHeight()` → `visibility = "visible"` → `dispGauge()` → `return`、
   そうでないときは以降の `scrollToDate(...)` まで進む形のまま変わっていない
   （main-page.js 371〜381 行目付近）。○

## 見つかったこと

特に不具合は見つからなかった。ブラウザでの見た目の確認（実際に
リサイズ・週送りで白が残らないか）は依頼どおり行っていない。
