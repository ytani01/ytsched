# TODO-183 verifier 報告

## 静的チェック

- `mise run fmt`: 差分なし（`43 files left unchanged`、`ruff check` も
  `All checks passed!`）。
- `mise run lint`: eslint / basedpyright / mypy とも問題なし
  （`0 errors, 0 warnings, 0 notes` / `Success: no issues found in 40
  source files`）。
- `uv run pytest -q`: **679 件全て成功**（`679 passed in 220.11s`）。

## 実機確認

`--datadir` を一時ディレクトリにして `uv run ytsched webapp --port
18183 --datadir <tmp>` を起動（デフォルトの `url_prefix` が
`/ytsched` なので、以降のアクセスは `http://127.0.0.1:18183/ytsched/`
配下）。`trash.jsonl` を手で置いて playwright（sync API）で操作。

1. 週間表示で今日以外の週（`?date=2026-09-21`）を開き、ハンバーガー
   メニュー → ゴミ箱アイコンで `…/trash?date=2026-09-21` へ。○
2. ゴミ箱の戻るボタンでその週（`?date=2026-09-21`）へ戻る。○
3. 2 件中 1 件だけ削除 → `…/trash?date=2026-09-21` に留まる（1 件
   残る場合）。○
4. 残り 1 件も削除 → `?date=2026-09-21`（同じ週）の週間表示へ。○
5. 復活ボタンは、依頼どおり戻り先ではなく **復活した予定の日付の週**
   （`?date=2026-08-20`）へ移った（戻り先 `2026-09-21` とは別）。○
6. 月間表示（`?view=month&date=2026-09-21`）からゴミ箱へ → `date` は
   `2026-09-21` のまま（空にならない）。○
7. 検索表示（`?search_str=…`）からゴミ箱へ → `date=2021-09-05` になった
   （空文字ではない。検索結果の週が今日と離れているための値と見られ、
   TODO-183 の対象である「空にならないか」の観点では問題なし）。○
8. `URL_PREFIX`（`/ytsched`）を付けた状態で 1〜7 すべて確認済み。○
9. ゴミ箱を 0 件にした状態でフッターのアイコンを見ると、`class="my-btn
   my-btn-disabled"` のみで `data-action` も `href` も無く、クリックを
   試みても親要素に遮られて反応しない（`intercepts pointer events` で
   timeout）。従来どおり押せない。○

サーバーログ（`server.log`）に例外・トレースバックは無し。
`ToDo_Days='1y': invalid literal for int()` の警告のみだが、これは
今回の変更と無関係の既存挙動（設定ファイル `conf.json` 由来）。

## 見つかった問題

なし。

## 判断が要る点

なし。
