# verifier 報告 (TODO-213)

作業ツリーは依頼どおり（TODO.md, src/README.md, main_handler.py, my.css, main-page.js, test_browser.py, test_web.py の変更と archives/agents/TODO-213/）。コードは直していない。

1. ○ `mise run lint` exit 0（ruff・fmtjs・eslint・basedpyright 0 errors・mypy 39 files no issues）
   ○ `mise run test` exit 0、`718 passed in 168.38s`（test_browser を含む）
2. 実機（`/tmp/claude-649/v.py`、chromium 412x1600、`--datadir` は一時ディレクトリ）
   - a ○ 追加後 URL=`/?date=2026-10-03&sde_align=top`（flash_* 無し）。`.my-flash` は `my-date-col my-wday-5` と `my-sde my-sde-normal` の 2 個だけ
     - 注: 新規画面には add ボタンが無い（new_flag）ので、新規の保存は `data-cmd="fix"` で行った。`cmd=add` は新規画面からは押せないため未実測（既存予定の画面の複製ボタン）。
   - b ○ 10-05 → 10-07 に日付変更。URL に flash_* 無し。移動先 `#date-2026-10-07 .my-date-col.my-flash` = 1、移動元 10-05 = 0。`.my-sde.my-flash` は 1
   - c ○ 削除。`.my-flash` は `my-date-col` の 1 個のみ、`.my-sde.my-flash` = 0
   - d ○ update 後 URL=`/edit/?date=2026-10-07&sde_id=...&todo_flag=false`（flash_* 無し）
   - e ○ 読み込み 500ms 後は class あり。→ で 1 週移動後も class はまだ付いたまま（要素は visibility:hidden, x=-410, 同じ点滅の途中）。2 週目で `.my-flash` は 0 個。← 2 回で戻ったあとも 0 個、`animation` 無し。3.5 秒待っても 0 個
   - f ○ a の点滅終了後に reload: `.my-flash` 0 個、getAnimations 0 個、URL に flash_* 無し
   - g ○ `archives/agents/TODO-213/flash.png`。日付の欄(03 Sat)と予定の行(新規追加)が黄色。他の行・ミニカレンダーに黄色は無く、余計なものは映っていない

## 判断が要る点
- e の 1 週目: 1 週移った直後（隣の週へ隠れた状態）は class が残る。2 週移ると外れる。実害は未確認（隣の週へ戻ると点滅の続きが見える可能性あり。未測定）。
