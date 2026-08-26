# TODO-065・TODO-068 verifier 報告

## 1. 決まった手順

```
mise run fmt
mise run typecheck
mise run lint
mise run test
```

- `ruff format`: 25 files left unchanged
- `ruff check`: All checks passed!
- `basedpyright`: 0 errors, 0 warnings, 0 notes
- `mypy`: Success: no issues found in 22 source files
- `pytest`: 439 passed in 3.43s

いずれも OK。`mise run upgradeproject` は走らせていない。

## 2. アプリの起動

`--datadir /tmp/todo065-data`（一時ディレクトリ）、ポート 18065 で起動。
`/ytsched/`・`/ytsched/edit/?date=2026-08-26` とも HTTP 200。テンプレートの `{{ }}` `{%`
が展開されずに残っている箇所は無し。サーバログ（`webapp.log`）に例外・トレースバックは
出ていない（起動ログのみ、1 行）。

playwright（`/tmp/todo065-scratch/venv` に別途インストール）＋
`/usr/bin/chromium`（`env -u DISPLAY` 付き）で操作した。

## 3. TODO-065（戻るボタン）

- **戻るボタンで、保存せずに週表示へ戻る**: 編集画面で `textarea` に
  値を入れてから戻るボタン（`onmousedown` を dispatch）を押すと、
  URL は `http://.../ytsched/?date=2026-08-26` になった。同じ日付で
  編集画面を開き直すと `textarea` は空のままで、保存されていないことを
  確認した
- **更新を 2 回押したあとに戻る**: `cmd=sync` の 2 回押しで URL は
  `edit/?date=2026-08-27&sde_id=...` のまま留まり（`history.back()`
  なら 2 回分戻ってしまうはずの経路）、続けて戻るボタンを押すと
  `http://.../ytsched/?date=2026-08-27`（週表示）へ遷移した。
  `history.back()` を使っていないことを確認できた
- **フッターの並び**: `col-2` が 6 個（合計 12）で崩れていない。
  既存項目（`sde_id` あり）・新規作成（`sde_id` なし、`new_flag=true`）
  の両方で `curl` により HTML を確認し、同じ 6 個の `col-2` になって
  いることを確認した
- console のエラー・警告は 0 件

## 4. TODO-068（スピナー）

- headless chromium（playwright、`go_back()`）で 週表示 → 編集画面 →
  ブラウザの戻る、を試した。**戻る操作のあいだに `my.js` / `my.css` /
  `icons.svg` 等の静的ファイルへの HTTP リクエストが再び発生しており、
  この環境では bfcache が効かず、通常の `load` として作り直されている**
  （`event.persisted` を確認しようとしたが、bfcache 復元でないため
  `pageshow` が bfcache から復元されたページで起きる状況を作れなかった）。
  そのため、**この確認では TODO-068 の不具合そのものを再現できなかった**
  （依頼にあるとおり、再現できない可能性は織り込み済み）
- 参考として、スピナーを `style.display = "block"` で強制的に出した
  状態でブラウザバックしたところ、（bfcache 復元ではなく通常の再読み込み
  だったため）`onloadHdr` の `load` ハンドラでスピナーは `none` に
  戻った。これは既存の `load` の経路であり、今回追加された `pageshow`
  の分岐（`event.persisted` が真のときだけ動く）を通ったかどうかは
  確認できていない
- コードは目視で確認した。`pageshow` リスナーは `event.persisted` が
  偽なら即 return するので、通常の `load` の動作へ影響しない作りに
  なっている

## 判断が要る点

- TODO-068 の修正が実際に効くかどうかは、この環境（headless chromium /
  playwright）では bfcache が働かず確認できなかった。実機のモバイル
  ブラウザ（Safari/Chrome）で確かめるか、確認できないまま良しとするかは
  main の判断が要る
