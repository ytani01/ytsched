# TODO-064 verifier 報告

## 1. lint / typecheck / test

- `mise run lint` — ○ ruff format 25 files unchanged、ruff check All checks passed
- `mise run typecheck` — ○ basedpyright 0 errors、mypy Success (22 files)
- `mise run test` — ○ 439 passed

## 2. `node --check`

```
node --check src/ytsched/webroot/static/js/my.js
```
○ 構文エラー無し

## 3. アプリ起動・ブラウザ操作（playwright, chromium 1.62.1 を一時的に npx で導入）

`uv run ytsched webapp --datadir <mktemp -d> --port 18765` を起動（HTTP 200 確認）。
playwright の `page.mouse` / CDP `Input.dispatchTouchEvent` で操作。

- ○ 日付セルを左へ 200px ドラッグ → 次週へ（`date=2026-08-31`）
- ○ 右へ 200px ドラッグ → 前週へ（`date=2026-08-24`）
- ○ 動かさずにクリック → `/ytsched/edit/?date=...&sde_id=` へ遷移（最重要項目）
- ○ 3px だけ動かして離す → クリック扱いのまま編集画面へ遷移
- ○ 「スケジュール追加」ボタン（`.my-add-btn`）クリック → 編集画面へ
- ○ メニューバーの次週ボタン（`#forward_button`）／前週ボタン（`#back_button`）クリック
  → それぞれ週送り
- ○ 検索欄（`#search_str`）にフォーカスして文字入力できる
- ○ タッチイベント合成（CDP `Input.dispatchTouchEvent`）での左ドラッグ → 次週へ
  （タッチの週送りは維持されている）
- コンソールエラー・例外・サーバログのトレースバック無し

編集画面（`/ytsched/edit/`）の確認:
- ○ 日付の ±1 ボタン（`changeElDate(-1)`）が効く（フィールドの値が変わる）
- ○ 更新ボタン（`submitCmd('update')`）クリック → 正常に保存され URL に `sde_id` が付く
- 「キャンセル」ボタン（`onmousedown="history.back();"`）はテンプレート上
  コメントアウトされており存在しない（今回の変更と無関係、既存のまま）

## テスト中に見つけた注意点（実装のバグではない）

自作の playwright スクリプトで、DOM 上に週パネルが 3 つ（前週・当該週・次週）
同時に存在するため、セレクタを `.my-week-cur` で絞らずに `.my-add-btn` などを
取ると、画面外（`x: -1171px` など）にある前週パネルの要素を掴んでしまい、
誤って「効かない」ように見えることがあった。これはテストスクリプト側の
セレクタの問題であり、実装側の不具合ではない（`.my-week-cur` で絞ったところ
正しく動作した）。

## 後片付け

`kill` でサーバプロセスを終了、`ss -ltnp` でポート 18765 が空いていることを確認。
