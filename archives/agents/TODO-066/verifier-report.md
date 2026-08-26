# TODO-066 verifier 報告

## 確認したこと

1. `uv run pytest`
   - コマンド: `uv run pytest -q`
   - 結果: ○ 444 passed（`tests/test_browser.py` 含む）

2. `mise run lint`
   - コマンド: `mise run lint`
   - 結果: ○ ruff format 26 files left unchanged / ruff check All checks passed

3. `mise run typecheck`
   - コマンド: `mise run typecheck`
   - 結果: ○ basedpyright 0 errors, 0 warnings, 0 notes / mypy Success: no issues found in 23 source files

4. アプリの起動・画面
   - コマンド:
     `uv run ytsched webapp --datadir /tmp/ytsched-verify-XXXX --port 10086`
   - `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:10086/` → 200
   - 週バーの期間表示（`2026/08/24 – 08/30` 相当）が HTML から消えていることを確認
     （`grep -n "gage_r\|week_bar\|plusmn\|&ndash;"` で本文中に日付範囲なし）
   - サーバ側の初期描画（テンプレート `week_diff`）:
     - 今週 (`/`) → `&plusmn;0`
     - `?date=` で 3 週先 → `+3w`
     - `?date=` で 1 週前 → `-1w`
   - `tools/screenshot.py --width 412` で 3 パターン撮影し目視。
     `±0` / `+3w` / `-1w` がいずれも針の真上に出て、針とラベルの中心が
     そろっている。目盛りラベル（`-30y` 〜 `+30y`）との重なりも無い
   - 幅 360px、針が `-3y` 付近（`-157w`）のケースも撮影し目視。崩れなし
   - 検索モード: `curl -s -X POST http://localhost:10086/
     --data-urlencode "search_str=test"` の本文に `id="week_bar"` が
     0 件（週バーが出ない）
   - サーバログ（`server.log`）に例外・トレースバックなし
   - 確認後、プロセスは kill 済み、一時ディレクトリは削除済み

5. 週送りボタンで針とラベルが一緒に動くか
   - `tests/test_browser.py` の新規テスト
     `test_gage_label_moves_with_the_needle` /
     `test_gage_label_is_plus_minus_zero_in_this_week` で確認済み
     （ラベルの中心と針（`.my-gage-r-needle`）の中心のずれが 2px 未満）。
     これは `uv run pytest` に含まれ、上記の 444 件に入っている
   - `#forward_button` / `#back_button` を押した動き自体は、既存の
     `test_forward_button_moves_a_week` / `test_back_button_moves_a_week`
     が別途確認しており、今回の変更でラベルが針の入れ物
     （`#gage_r`）の中にまとめられているため、位置がずれる余地は無い

## 見つかったこと

なし。実装は依頼どおり動作している。

## 判断が要る点

なし。
