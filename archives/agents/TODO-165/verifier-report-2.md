# TODO-165 verifier 報告（2回目）

reviewer の指摘を受けた修正後の確認。

## 1. `uv run pytest`（全件）

```
uv run pytest -q
```

結果: **1 failed, 615 passed**（184.01s）

```
FAILED tests/test_browser.py::test_home_button_double_tap_by_touch_returns_to_the_top_screen[300]
AssertionError: 1 回目の読み直しに 360 ミリ秒かかり、300 ミリ秒後の 2 回目をダブルタップにできない
assert 359.85328909009695 < 300
```

## 2. lint / 型チェック

- `uv run ruff check` → All checks passed!
- `uv run ruff format --check src tests` → 37 files already formatted（○）
  - `uv run ruff format --check`（全体）は archives 配下の既存 `.md`
    3件（TODO-002・TODO-088・TODO-165/reviewer-report.md）で
    unformatted と出るが、いずれも今回の diff に含まれない既存物。
    src/tests は問題なし
- `uv run basedpyright` → 0 errors, 0 warnings, 0 notes（○）

## 3. `tests/test_browser.py -k home_button -rs` を5回連続

```
uv run pytest tests/test_browser.py -k home_button -rs -q
```

| 回 | 結果 |
|----|------|
| 1  | **1 failed**, 8 passed |
| 2  | 9 passed |
| 3  | 9 passed |
| 4  | **1 failed**, 8 passed |
| 5  | 9 passed |

skip は5回とも0件（`-rs` の出力に skipped 行なし）。

失敗はいずれも同じ箇所
`test_home_button_double_tap_by_touch_returns_to_the_top_screen[300]` の
`_double_tap_home_in_search()` の assert。

- 回1: `1 回目の読み直しに 329 ミリ秒かかり、300 ミリ秒後の 2 回目をダブルタップにできない`
  （`assert 329.233804019168 < 300`）
- 回4: `1 回目の読み直しに 357 ミリ秒かかり、300 ミリ秒後の 2 回目をダブルタップにできない`
  （`assert 357.3608009610325 < 300`）

（全件実行の1で挙げたものも同種、360ms）

5回中2回、さらに全件実行でも1回、計3回/6回 失敗。skip をやめて assert にした
結果、想定通り「読み直しが間に合わない回」がテスト失敗として顕在化している。
これは実装のバグというより、CI/実行環境の速度に左右されるテストの安定性の
問題（`interval_msec=300` の境界が環境によっては超えやすい）。

## 4. アプリの起動確認

```
uv run ytsched webapp --datadir <一時ディレクトリ>
curl -s -o top.html -w "HTTP:%{http_code}\n" http://127.0.0.1:10085/
```

- HTTP:200（○）
- `top.html` に `{{` `{%` の残存なし（grep で0件）
- `webapp.log` に例外・トレースバックなし
  （`start server: run forever ..` の INFO ログのみ）
- 確認後、pgrep で PID を確認して kill 済み

## 判断が要る点

- 依頼のステップ3で懸念されていた通り、`_double_tap_home_in_search()` の
  assert が **6回中3回失敗する**。300ミリ秒の境界に対し実測が
  329〜360ミリ秒でばらつく。このままだと `pytest` 全件実行が
  不安定（flaky）になる。境界値（`HOME_DOUBLE_TAP_MSEC` または
  `interval_msec=300` のパラメータ）を見直すか、実行環境の速度差を
  吸収する仕組みが要るかは main の判断が必要
