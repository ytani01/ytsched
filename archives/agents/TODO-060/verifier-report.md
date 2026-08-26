# TODO-060 verifier 報告

## コードの確認

- `getBoundingClientRect()` への置き換えは `placeGageWithoutTransition()`
  内の 1 か所のみ（`my.js:131`）。○
- `dispGage()` 末尾は `placeGageWithoutTransition(monday_str)` に
  なっている（`my.js:174`）。○
- `offsetHeight` は `my.js:459`・`461` に残っており、置き換えは
  ゲージ以外に及んでいない。○（`main.html:47,55` `edit.html:87` は
  ファイルとして未確認だが、今回の変更は `my.js` のみで、そちらは触って
  いないことを diff の範囲（`my.js` の 2 か所）で確認済み）

## 環境の準備

- ポート 10099 に、事前に起動されていたアプリ（datadir はこのセッションの
  scratchpad）が既に立っていたのでそれを利用（`pgrep -af "ytsched webapp"`
  で確認、ポート 10085 は使っていない）
- `curl -s -o /dev/null -w '%{http_code}' http://localhost:10099/ytsched/?date=2027-08-25`
  → `200`

## probe.py の実測

```
env -u DISPLAY uv run --with playwright python archives/agents/TODO-060/probe.py
```

- ① 初回: `323ms style.left=75.8687% computed=288.297px`
  （中央 190px を経由せず、直接目的地へ）
- ② 同じ週をもう一度: `29ms style.left=(未設定) computed=190px`
  （ページ読み込み直後、JS 実行前の CSS 初期値。以後は動かない）
  → `41ms style.left=75.8687% computed=288.297px`
- ③ 隣の週へ: `37ms computed=288.297px`（前の週の位置）から
  `54ms〜202ms` にかけて `288.344px → 288.688px` へ滑らかに遷移
  （190px を経由していない）

依頼書に載っていた「直す前」の症状（60ms 時点で `computed=190px` の
まま反映されない → 85ms で中央から動き出す）は再現せず、直った。○

## mise / test

- `mise run fmt` → `ruff format`: 25 files left unchanged / `ruff check`:
  All checks passed
- `mise run typecheck` → basedpyright 0 errors, mypy 22 files success
- `mise run test` → `uv run pytest tests`: **439 passed**

## 検索モードでの例外

`gage_r` 無しの状態を作るため、`search_str` を POST するフォームを
`page.evaluate()` で実際に送信して検索モードへ遷移させ、`pageerror` を
監視した。

- 遷移後 `document.getElementById('gage_r')` → `False`（検索モードに
  入れていることを確認）
- `pageerror` イベント: 0 件
- サーバのログ（起動時の INFO のみ）にも例外なし

## 判断が要る点

特になし。すべて依頼どおりの結果。
