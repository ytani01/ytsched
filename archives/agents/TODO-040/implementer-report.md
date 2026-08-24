# TODO-040 implementer 報告

## 変更・作成・削除したファイル

- `src/ytsched/webroot/static/vendor/bootstrap/bootstrap.min.css` — 5.3.8 に差し替え
- `src/ytsched/webroot/static/vendor/bootstrap/LICENSE` — 5.3.8 のものに差し替え
- `src/ytsched/webroot/static/vendor/fontawesome/css/all.css` — 7.3.1 に差し替え
- `src/ytsched/webroot/static/vendor/fontawesome/webfonts/fa-solid-900.woff2` — 7.3.1 に差し替え
- `src/ytsched/webroot/static/vendor/fontawesome/webfonts/fa-regular-400.woff2` — 7.3.1 に差し替え
- `src/ytsched/webroot/static/vendor/fontawesome/webfonts/fa-solid-900.woff` — 削除（`git rm`）
- `src/ytsched/webroot/static/vendor/fontawesome/webfonts/fa-regular-400.woff` — 削除（`git rm`）
- `src/ytsched/webroot/static/vendor/fontawesome/LICENSE.txt` — 7.3.1 のものに差し替え
- `src/ytsched/webroot/templates/main.html` — クラス名置換（6 か所）
- `src/ytsched/webroot/templates/edit.html` — クラス名置換（2 か所）
- `src/ytsched/webroot/templates/sde.html` — クラス名置換（2 か所）
- `src/ytsched/webroot/static/css/my.css` — 先頭に `--bs-body-font-family` の固定を追加（依頼書の内容そのまま）
- `README.md` — 「同梱しているライブラリ」節の版数・woff 説明を書き直し

## 取得したファイルの照合結果（実測値）

- `bootstrap.min.css`
  - sha384 = `sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB` （一致）
  - sha256 = `d85327d99c7a3ee1f9b5d0500d1370acea3ad2db39c163c2f51f232baedbdede` （一致）
- Font Awesome
  - `css/all.css` sha384 = `7WvIYI4vLdL28Kb0e0uLmaY+AFg62zUFE8P4OgFsKy0m93wWgDxFmdtVTkKNTJi8` （一致）
  - `webfonts/fa-solid-900.woff2` sha384 = `TeBDWCQ2a4tojAZRcJzXsEgFI2EzW27W0GYt9HIpqXdUiPIauuYxz9RpAgJM1x9+` （一致）
  - `webfonts/fa-regular-400.woff2` sha384 = `78Wu/Ea/cmf/TbrN4bDVNmemhBWOSesv4mzA40dUVsj9Hb5E2CTaukY/7qGGVmBg` （一致）
- 4 つとも依頼書に書かれた値と 1 バイトも違わず一致。手を止める事態にはならなかった。

Bootstrap の展開後の構成が `dist/dist/css/...` ではなく `bootstrap-5.3.8-dist/css/...`
（`dist/` が 1 段だけ）だったので、そこは依頼書の記述と少し違ったが、
`bootstrap.min.css` 自体の場所とハッシュは一致しているので、そのまま使った。

## クラス名の置換

- `text-left` → `text-start`: `main.html` 2 か所、`edit.html` 1 か所、`sde.html` 1 か所（計 4）
- `text-right` → `text-end`: `main.html` 3 か所、`edit.html` 1 か所（計 4）
- `font-weight-bold` → `fw-bold`: `main.html` 1 か所、`sde.html` 1 か所（計 2）
- 依頼書に書かれた内訳・件数（4 / 4 / 2）と完全一致
- `grep -rn 'text-left\|text-right\|font-weight-bold' src/ytsched/` → **0 件**（確認済み）

## 自分で確かめたこと

- `mise run test` → **412 件全て pass**（fmt / typecheck / lint も通過）
- 一時ディレクトリ（`/tmp/.../scratchpad/todo040/datadir`）を `--datadir` に
  指定してアプリを起動し、`/ytsched/`（トップ）と `/ytsched/edit` が
  どちらも 200 で返ることを確認。`~/ytsched/data` は一切触っていない
- 同梱した 5 ファイルが `/ytsched/static/vendor/...` 配下で全て 200 で
  配信されることを確認
  （`bootstrap.min.css`, `fontawesome/css/all.css`,
  `fontawesome/webfonts/fa-solid-900.woff2`,
  `fontawesome/webfonts/fa-regular-400.woff2`,
  `fontawesome/LICENSE.txt`）
- 配信された `fa-solid-900.woff2` を curl で取得し、先頭 4 バイトが
  `wOF2` であることを Python で確認
- テスト用サーバーのプロセスは確認後に停止済み

## 単独で決めた判断

- 特に無し。依頼書と `TODO.md` の記述どおりに実施した。

## 気づいたが直さずに残したもの

- 特に無し（TODO-040 の範囲外に触れるものは見当たらなかった）。

## うまくいかなかったところ

- サーバー停止時、`kill` の対象 PID がタイミングによって既に無くなって
  いたことがあったが（zsh の `-i` エイリアスとは無関係）、最終的に
  `pgrep -af` で確認して、テストサーバーのプロセスが残っていないことを
  確かめた
