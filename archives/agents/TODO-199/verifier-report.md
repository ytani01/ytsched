# TODO-199 verifier 報告

対象: `src/ytsched/webroot/static/js/main-page.js` / `nav.js` の差分（`sde_align="home"`）。
コードは直していない（2 回目の確認 2 で行った一時的な書き換えは、確認後に元に戻した）。

## 1. mise run lint / typecheck / test（2 回目の確認）

| 確認 | 結果 |
|---|---|
| `mise run lint`（ruff format/check） | ○ `All checks passed!`（`tests/test_browser.py` の CHROMIUM 一時差し替え中、ruff format が長い行を折り返した。CHROMIUM を戻した際に一緒に消え、`git diff` には残っていない） |
| `mise run lint` の `fmtjs`（prettier） | × 実行不可。`npm error npx canceled due to missing packages`（`node_modules` が無い。環境の制約で、この変更とは無関係） |
| `mise run typecheck`（basedpyright / mypy） | ○ `0 errors, 0 warnings, 0 notes` / `Success: no issues found in 39 source files` |
| `uv run pytest -q`（CHROMIUM を一時的に `/home/ytani/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome` に差し替え、ブラウザテスト込み） | ○ 698 passed（189.69s） |
| CHROMIUM を `/usr/bin/chromium` に戻したことの確認 | ○ `git diff tests/test_browser.py` に CHROMIUM 行は出ない |

JS の lint/format はこの環境に `node_modules` が無く、今回も実行できない（TODO-199 の変更が原因ではない、既知）。

## 2. テストが壊すと落ちるか

`nav.js` の `document.getElementById("footer_gauge_bar") || el_menu_bar` を、
一時的に `el_menu_bar` だけに書き換えてから
`test_home_button_keeps_today_in_view` / `test_home_reload_keeps_today_in_view`
を実行した。

```
uv run pytest -q tests/test_browser.py -k "test_home_button_keeps_today_in_view or test_home_reload_keeps_today_in_view"
```

結果: **○ 2 件とも落ちた**（`playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 5000ms exceeded`）。
今日の欄がメニューバーの上端には収まるがゲージには隠れたままになり、
`_wait_today_above_footer`（ゲージの上端を基準に待つ）がタイムアウトした。
テストはゲージへの回帰を検知できる。

書き換え後、`\cp` で退避しておいたファイルから元に戻し、
`git diff src/ytsched/webroot/static/js/nav.js` で
`document.getElementById("footer_gauge_bar") || el_menu_bar` が
戻っていることを確認した。

## 3. 実測（Playwright、画面サイズ・PC/スマホ。ゲージを基準にした版）

サーバは今日を `datetime.date.today()` で決めており、上書きの仕組みは無い。
実行時のシステム日付が 2026-09-27（日）と一致したため、`today_str` の
書き換えなしでそのまま条件 a を再現できた（b は `today_str` を evaluate で上書き）。

データは前回と同じ一時ディレクトリを再利用（2026-09-21〜27 の各日に 6 件ずつ）。
スクリプトは前回と同じ 1 本を直して使った
（`archives/agents/TODO-199/verifier-todo199_check.py`。measure() に
`#footer_gauge_bar` の `top` を追加しただけ）。

### a: 今日＝日曜のまま、前週を開いてホーム1回 / c: ダブルタップ

| 条件 | today_bottom | gauge_top | 差(≈30目標) | menu_top(参考) | scrollY | URL date |
|---|---|---|---|---|---|---|
| pc1920 a | 939.5 | 970 | 30.5 | 1038.4 | 1049 | 2026-09-21 ○ |
| pc1920 c | 939.5 | 970 | 30.5 | 1038.4 | 1049 | 2026-09-21 ○（&sde_align=home 付き） |
| pc1366 a | 627.5 | 658 | 30.5 | 726.4 | 1361 | 2026-09-21 ○ |
| pc1366 c | 627.5 | 658 | 30.5 | 726.4 | 1361 | 2026-09-21 ○ |
| mobile390 a | 703.5 | 734 | 30.5 | 802.4 | 1915 | 2026-09-21 ○ |
| mobile390 c | 703.5 | 734 | 30.5 | 802.4 | 1915 | 2026-09-21 ○ |

a と c は全条件で一致。差はどの条件も 30.5px（期待値 30px。丸めの誤差程度）で、
今日の欄の下端がゲージにもメニューバーにも隠れず、想定どおりの余白で収まっている。
URL の `date` はいずれも月曜のまま。

### b: today_str を水曜(2026-09-23)に書き換えてホーム1回

| 条件 | scrollY | 月曜 top 合わせの scrollY | gauge_top - today_bottom |
|---|---|---|---|
| pc1920 b | 0 | 0 | 131.5（収まるので月曜合わせのまま） |
| pc1366 b | 279 | 0 | 30.5（クランプが効いた） |
| mobile390 b | 473 | 0 | 30.5（クランプが効いた） |

前回と同じく `Math.max(月曜top, 今日下端クランプ)` の式どおりで、
比べる相手をゲージに変えても挙動は一貫している。不具合ではない。

### 画面の高さを 1080→600（PC 1920 幅）

| today_bottom | gauge_top | 差 | scrollY |
|---|---|---|---|
| 459.5 | 490 | 30.5 | 1529 |

高さを変えたあとでもホームボタンで再度クランプが効き、今日の欄がゲージに隠れない。

### スクリーンショット（目視確認、撮り直し）

`~/tmp/playwright-mcp/TODO-199-pc1920.png` / `-pc1366.png` / `-mobile390.png` /
`-pc1920-h600.png` の 4 枚を確認。すべてで 27日(Sun)の最後の予定（18:00）が
ゲージにもメニューバーにも隠れず見えている。欠けや余計な表示も無い。

### サーバのログ

例外・トレースバックは無し（`rg -ic "traceback|exception"` → 0 件）。

## 見つかった不具合

無し。

## 境界線上の判断（報告のみ、原因の切り分けはしていない）

前回同様、シングルタップ直後に scrollY が少し遅れて変化する挙動を観測した
（既存の週の先読み・レイアウト由来と見られる）。今回は「スクロールが 300ms
変化しなくなるまで」待ってから測ったため、最終的な安定値は a/c で一致しており、
TODO-199 の実装自体に起因する不具合ではないと考えられるが、断定はしない。

---

## 前回（ゲージを見ていない版、#menu_bar とだけ比較）

（今日の欄の下端が `#footer_gauge_bar` に隠れていたのを見逃していた版。
記録として残す。上の「3. 実測」が現在の判定）

### a: 今日＝日曜のまま、前週を開いてホーム1回 / c: ダブルタップ

| 条件 | today_bottom | menu_top | 差(≈30目標) | scrollY | URL date |
|---|---|---|---|---|---|
| pc1920 a | 1007.5 | 1038.4 | 30.9 | 981 | 2026-09-21 ○ |
| pc1920 c | 1007.5 | 1038.4 | 30.9 | 981 | 2026-09-21 ○（&sde_align=home 付き） |
| pc1366 a | 695.5 | 726.4 | 30.9 | 1293 | 2026-09-21 ○ |
| pc1366 c | 695.5 | 726.4 | 30.9 | 1293 | 2026-09-21 ○ |
| mobile390 a | 771.5 | 802.4 | 30.9 | 1847 | 2026-09-21 ○ |
| mobile390 c | 771.5 | 802.4 | 30.9 | 1847 | 2026-09-21 ○ |

### b: today_str を水曜(2026-09-23)に書き換えてホーム1回

| 条件 | scrollY | 月曜 top 合わせの scrollY | 一致 |
|---|---|---|---|
| pc1920 b | 0 | 0 | ○（水曜が画面に収まり、月曜合わせのまま） |
| pc1366 b | 211 | 0 | 不一致だが妥当（クランプが効いた） |
| mobile390 b | 405 | 0 | 同上 |

### 画面の高さを 1080→600（PC 1920 幅）

| today_bottom | menu_top | 差 | scrollY |
|---|---|---|---|
| 527.5 | 558.4 | 30.9 | 1461 |

### 1 回目の lint/typecheck/test

| 確認 | 結果 |
|---|---|
| `mise run lint`（ruff format/check） | ○ `All checks passed!` |
| `mise run typecheck`（basedpyright / mypy） | ○ `0 errors, 0 warnings, 0 notes` / `Success: no issues found in 39 source files` |
| `uv run pytest -q -k "not browser"` | ○ 611 passed |
| `uv run pytest -q tests/test_browser.py` | ○ 87 passed（185.89s） |
