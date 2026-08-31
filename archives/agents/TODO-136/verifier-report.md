# TODO-136 verifier 報告

## 実行したコマンド

```
mise run lint
uv run pytest tests
uv run ytsched webapp --port 18136 --datadir /tmp/ytsched-verify-136-data
```

## 結果

- `mise run lint`（fmt/typecheck/lintjs 含む） -- ○ すべて通過
  （ruff format 38 files unchanged、ruff check All checks passed、
  eslint エラー無し、basedpyright 0 errors、mypy Success: no issues found
  in 35 source files）
- `uv run pytest tests` -- ○ 560 passed in 137.43s
- アプリ起動 -- ○ `curl http://127.0.0.1:18136/` で HTTP 200。
  ログ（`/tmp/ytsched-verify-136.log`）に例外・トレースバックなし
  （起動メッセージ 1 行のみ）

## ブラウザでの確認（playwright + `/usr/bin/chromium`、viewport 412x1600）

`/tmp/ytsched-verify-136-data` を `--datadir` にして起動したサーバへ、
`tests/test_browser.py` の新規テストと同じ操作を自作スクリプトで再現し、
依頼の 4 項目を確認した。

1. ミニカレンダー領域でのマウスドラッグ（左へ 250px）
   -- ○ `2026-03-02` → `2026-04-06`（4 月の最初の月曜、曜日は月曜）。
   スクリーンショットでも週一覧・ミニカレンダーの選択枠が
   `2026/04/06` に揃っていることを目視確認（添付画像参照）
2. ミニカレンダー以外の領域（週見出し）でのドラッグ
   -- ○ `2026-03-02` → `2026-03-09`（1 週間だけ進む、月送りへ退行していない）
3. ミニカレンダーのセルをしきい値未満の動きでクリック
   -- ○ 押したセルの日付（`monday` の 1 週間後）へ直接移動、月送りと
   誤認しない
4. 検索モードでのスワイプ（TODO-117、基準日を ±7 日）への影響
   -- ○ 検索モードでは `.my-mini-cal` が 0 件（表自体が出ない）。
   その状態で左スワイプすると `date` パラメータが `today + 7日` へ
   変わり、TODO-136 の変更後も従来どおり動く

いずれも `tests/test_browser.py` に足された新規ブラウザテスト 4 件
（`test_touch_swipe_in_mini_cal_moves_by_a_month` など）と同じ結果。
新規テストも含めた `pytest tests` のフル実行（560 件）はすでに通過済み。

## TODO-136 のチェック項目

- 「ミニカレンダーの領域での左右スワイプ・ドラッグで 1 ヶ月単位に
  移動する」-- 満たされている（上記 1）
- 「移動先の曜日は月曜にする」-- 満たされている（上記 1、
  `moveActiveMonth()` が `mondayDaysInMonth()` で求めた月曜へ移す）

## 見つかった不具合

無し。

## 判断が要る点

無し。
