# TODO-178 verifier 報告

## 1. lint

```
uv run ruff format --check
```
→ `72 files already formatted`（○）

```
uv run ruff check
```
→ `All checks passed!`（○）

## 2. tests/test_browser.py

```
uv run pytest tests/test_browser.py -q
```
→ `67 passed in 208.36s`（○）。TODO-178 で足された 4 件
（`test_gauge_drag_does_not_move_screen_while_dragging` /
`test_gauge_drag_follows_after_1_second_stop` /
`test_gauge_drag_follow_does_not_push_history` /
`test_gauge_tap_moves_to_the_tapped_week`）を含め全部通った。

## 3. pytest 全体

```
uv run pytest -q
```
→ `670 passed in 206.56s`（○）

## 4. アプリを起動して実機で確認

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18765` を
バックグラウンドで起動し（`curl` で 200 を確認）、playwright を直に書いて
`tests/test_browser.py` の既存パターン
（`window.ytsched.days2xPercent()` で座標を計算 → `page.mouse` で
down/move/up）を使って以下を確認した。自動テストで既にカバーされている
項目（ドラッグ中に画面が動かない・1 秒後に先読み済みの週へ追従・履歴が
1 つしか積まれない・タップで移る）はテスト結果の○で確認済みとし、
自動テストに含まれていない項目だけ手で追加確認した。

- ○ 先読みの範囲より遠い位置（+3y 相当）で 1 秒止めても URL は変わらず
  （`?date=2026-08-31` のまま）、針のラベルは `+3.0y` まで動いた
- ○ 月間表示（`?view=month`）でもゲージ帯があり、1 秒止めると
  `?view=month&date=2026-08-31` → `?view=month&date=2026-09-07` へ追従した
  （ページの読み直しではなく URL 変化のみ）
- ○ 検索モード（検索語を入れて送信）では `#week_bar` も `.my-gauge-bar`
  も DOM から消え、console エラーは 0 件
- ○ 週間表示・月間表示のどちらでも console エラーは 0 件
- 帯の上でドラッグしたときに週送りスワイプが二重に効かないかは、
  横に大きく動かして確認したところ、ゲージ側の移動だけが起き
  （`?date=1975-10-27&sde_align=top` のように大きく離れた日付に単発で
  移った）、スワイプの追加移動は見られなかった。ただしこの確認方法は
  「ゲージ自体の移動」と「スワイプの二重発火」を厳密には区別できて
  いないので、参考程度に留める

## 5. 帯の高さ・padding-top

- ○ `.my-gauge-bar` の高さは 44px（`getBoundingClientRect().height` で実測）
- ○ `#week_bar` の高さは 52px、`body` の `padding-top` も 52px で一致
  （`onloadHdr()` が測って入れている）

## 見つかったこと

なし。依頼の確認項目はすべて期待どおりだった。

## 使ったコマンド

```
uv run ruff format --check
uv run ruff check
uv run pytest tests/test_browser.py -q
uv run pytest -q
uv run ytsched webapp --datadir <tmp> --port 18765 &
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18765/
# 以降は playwright を直に書いたスクリプトで確認（本報告に手順を記載）
```

---

## 今回（直し 1〜5 のあとの再確認）

### 1. lint

```
mise run lint
```
→ `fmt`（ruff format/check）・`typecheck`（basedpyright/mypy）・`fmtjs`（prettier）・
`lintjs`（eslint）すべて通った（○）。`upgradeproject` は走らせていない。

### 2. pytest 全体

```
uv run pytest -q
```
→ `670 passed in 207.51s`（○）

### 3. `my.css` の下詰め（`--my-gauge-shift: 12px`）の見た目

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18766` を
バックグラウンドで起動し、playwright で実測・スクリーンショット確認した。

- ○ `.my-gauge-bar` の高さは 44px のまま（`getBoundingClientRect()` で実測）
- ○ `#week_bar` の高さ・`body` の `padding-top` は共に 52px で一致
- ○ 軸・今週のしるし・針・週差ラベル・目盛りラベルは、帯（0〜44px）の
  範囲内に収まっていた（目盛りラベルの下端がちょうど 44px、他はそれより
  上）。スクリーンショットでも重なり・はみ出しは見えなかった
- ○ 月間表示（`?view=month`）でも帯の高さは同じく 44px
- ○ 別の週（`?date=2026-10-05`）を開いても針の縦位置（`top`）は変わらず
  （どちらも 16px）

### 4. 直し 1（`blockPanelOf()` 切り出し・`pointerId` の見分け・左ボタン限定）で挙動が変わっていないか

playwright で実際にドラッグ・追従・タップを再現した。

- ○ 先読み範囲の外（+1.1m 相当）へドラッグしている間は URL は変わらず、
  1.5 秒待っても追従しない。指を離すと `?date=2026-10-05&sde_align=top`
  へ移った（範囲外は指を離したときに移る、の仕様どおり）
- ○ 先読み範囲内（+8px 相当）へドラッグし 1.3 秒待つと
  `?date=2026-08-31` へ追従した
- ○ `history.length` は、ドラッグ開始前 2 → 1 秒待ちを 2 回はさんで
  指を離したあと 3。1 回しか積まれていない
  （`test_gauge_drag_pushes_history_only_once` に対応する動きを実機でも確認）
- ○ タップ（ドラッグ無しでクリック）でも `?date=2027-07-12&sde_align=top`
  のように狙った週へ飛んだ
- ○ 検索モードでは `.my-gauge-bar` が DOM から消え、console エラーは
  0 件（全操作を通して console エラーなし）

### 5. `tests/test_browser.py` のテスト名変更・`main.html` のコメント

- ○ `test_gauge_drag_pushes_history_only_once` という名前の関数が存在する
- ○ `main.html` の `.my-gauge-bar` 上のコメントは TODO-178 の内容
  （ドラッグ・1 秒後の追従・範囲外は指を離したときに移る）に書き直されていた

## 見つかったこと

なし。依頼の確認項目はすべて期待どおりだった。

## 使ったコマンド

```
mise run lint
uv run pytest -q
uv run ytsched webapp --datadir <tmp> --port 18766 &
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18766/
# 以降は playwright を直に書いたスクリプトで確認（本報告に手順を記載）
```
