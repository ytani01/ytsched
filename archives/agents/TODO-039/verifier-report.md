# TODO-039 verifier 報告

## 1. いつもの一式

```
mise run test
```

- `ruff format` 23 files left unchanged
- `ruff check` All checks passed!
- `basedpyright` 0 errors, 0 warnings, 0 notes
- `mypy` Success: no issues found in 20 source files
- `pytest` **418 passed** in 2.70s（直前の 412 件から 6 件増えている。
  依頼書の実装報告どおり `test_web.py` / `test_webapp.py` にテストが
  足されている）

○ 問題なし。

## 2. `uv build` した wheel の中身

`mise run build` → `unzip -l dist/*.whl` で以下すべて確認。

```
ytsched/webroot/static/manifest.json
ytsched/webroot/static/favicon.ico
ytsched/webroot/static/icons/icon.svg
ytsched/webroot/static/icons/icon-192.png
ytsched/webroot/static/icons/icon-512.png
ytsched/webroot/static/icons/icon-maskable-512.png
ytsched/webroot/static/icons/apple-touch-icon.png
```

○ 7 ファイルすべて wheel に入っている。

## 3. 起動して、実際に引く

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18321` を
`run_in_background` で起動（`~/ytsched/data` は使っていない）。

- `/ytsched/` → 200、`/ytsched/edit` → 200
- `/ytsched/static/manifest.json` → 200。`python3 -m json.tool` に通り、
  中身は次のとおり（`start_url` / `scope` は `../`）。

  ```json
  {
    "name": "ytsched", "short_name": "ytsched", "lang": "ja",
    "start_url": "../", "scope": "../", "display": "standalone",
    "background_color": "#FFFFFF", "theme_color": "#4488CC",
    "icons": [...]
  }
  ```

- 7 ファイルすべて 200
- **`favicon.ico` は本物の ICO。** 先頭 4 バイト（`od -An -tx1 -N4`）は
  `00 00 01 00`。`file` コマンドは
  `MS Windows icon resource - 3 icons, 48x48, 32 bits/pixel, 32x32, 32
  bits/pixel` と返した。**直前まで PNG が入っていた問題は解消している。**
- PNG 4 つ（icon-192 / icon-512 / icon-maskable-512 / apple-touch-icon）は
  いずれも先頭 `89 50 4e 47`（`\x89PNG`）。`file` でも
  `PNG image data, 192x192` 等、期待どおりのサイズが出た
- `icon.svg` は `<?xml version="1.0" encoding="UTF-8"?>` で始まり、
  直後に `<svg` が続く
- 一覧 HTML（`/ytsched/`）に以下の行を確認。

  ```
  <meta name="theme-color" content="#4488CC">
  <link rel="icon" href="/ytsched/static/favicon.ico?v=…" sizes="32x32">
  <link rel="icon" type="image/svg+xml" ...
  <link rel="apple-touch-icon" ...
  <link rel="manifest" href="/ytsched/static/manifest.json?v=…">
  ```

- `grep -cE '\{\{|\{%'` で HTML 中の生の `{{` / `{%` は **0 件**

○ すべて期待どおり。

## 4. `--urlprefix` を変えても付いてくるか

同じサーバを止め、`--urlprefix /sched --port 18322` で起動し直した。

- `/sched/static/manifest.json` → 200
- `/sched/` → 200
- 一覧 HTML の `<link rel="manifest" href="…">` は
  `/sched/static/manifest.json?v=…` になっていて、`/ytsched/…` は
  残っていない
- manifest 自身の中身（`start_url` / `scope`）は `../` のまま
  （urlprefix を変えても manifest.json の中身自体は変わらない。
  依頼書のとおり、`../` の解決はブラウザの仕事なのでここまで）

○ 期待どおり。

## 5. ブラウザで見る（chromium）

`chromium --headless=new --remote-debugging-port=9333` を daemon として
起動し、CDP（`websocket-client` を `pip install --user` して自作した
簡易スクリプトで `Runtime.exceptionThrown` / `Log.entryAdded(level=error)`
を監視）で確認した。**申し送りどおり、呼び出しごとに
`--user-data-dir` を別ディレクトリにして進めた。**

- 一覧・編集の 2 画面 × 幅 412 / 740 の 4 通り＋
  `visualViewport` を `undefined` にした状態での一覧・編集
  （`Page.addScriptToEvaluateOnNewDocument` で
  `Object.defineProperty(window,'visualViewport',{value:undefined})`
  を注入）の計 6 通りすべてで、**JS の例外・console.error は 0 件**
- `git worktree` で `HEAD`（`e146a11`）を別ディレクトリに用意し、
  同じ 4 通り（412/740 × 一覧/編集）をスクリーンショットして
  Pillow で画素比較した。差分は次のとおりで、いずれも**下部バーの
  位置や見た目の変化ではなく、テストデータ（日付・ランダム UUID）の
  差**だった。

  | 画面 | bbox | 差分ピクセル数 |
  |---|---|---|
  | list 412 | (26,34)-(58,105) | 1923/370800 |
  | list 740 | (26,34)-(85,105) | 3796/666000 |
  | edit 412 | (306,736)-(408,744) | 631/370800 |
  | edit 740 | (634,736)-(736,744) | 678/666000 |

  該当範囲を切り出して目視したところ、list 側はカレンダーの日付
  セル内の文字（データディレクトリが別なので日付表示が違う）、
  edit 側は入力欄に入っているランダム UUID の文字列で、
  レイアウト自体は同一だった。**下部バーの位置・見た目に変化なし。**

○ 期待どおり（キーボードなし状態で `HEAD` と差がない、
`visualViewport` が無くても例外にならない）。

## その他

- サーバの起動ログ（`server1.log` / `server2.log`）に例外や
  トレースバックは出ていない（`start server: run forever ..` の
  INFO のみ）
- 作業後、起動したサーバ・chromium はすべて `pgrep`/`kill` で終了、
  `git worktree remove` で HEAD 用ワークツリーも削除し、
  `git status` はコミット前の状態に戻っている（実装済みの
  変更・未追跡ファイルのみ）

## 不具合

見つからなかった。
