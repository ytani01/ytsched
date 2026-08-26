# TODO-055 verifier 報告

## 決まった手順

- `mise run fmt` ○ ruff format 25 files unchanged / ruff check All checks passed
- `mise run typecheck` ○ basedpyright 0 errors, mypy Success (22 files)
- `mise run test` ○ `uv run pytest tests` 437 passed

## アプリを動かしての確認

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18765` で起動（HTTP 200）。
`--datadir` は `/tmp/.../scratchpad/ytsched-data` を使用、実データは触っていない。

- 今週の帯: `2026/08/24 – 08/30`、週の差の欄は空（`+Nw` を出さない）○
- `?date=2026-09-14` （3 週先）: 帯に `+3w` を表示 ○
- 検索モード（POST で `search_str` を設定）: `week_bar` が出力に含まれない（count 0）○
- 帯の高さぶん `body.style.paddingTop` が入る: 今週で `28px` ○。一番上の日付ブロック
  （08/24）はキャプチャ上も帯に隠れていない ○
- 検索モードでは `paddingTop` が空文字のまま（未設定＝0 相当）で余計な空きは無い ○
  （スクリーンショットでも隙間なし）
- 日付欄クリック（通常時）: `edit/?date=2026-08-24&sde_id=` へ遷移 ○
- 週送り（`moveToMonday(1, ...)`）を 3 回 → `?date=2026-09-14`、帯に `+3w` ○。
  そこでホームボタンをクリック → `?date=2026-08-26`（今週）に戻る。
  TODO-049 の退行（画面が前の週のまま）は再現しなかった ○
- スワイプ（CDP `Input.dispatchTouchEvent` で左方向）→ `?date=2026-08-31`
  （翌週の月曜）に遷移、効いている ○
- キャプチャ: `todo055-today2_closed_{412,800}.png`、`search_mode.png` を
  `/tmp/.../scratchpad/shots/` に保存（一時領域。archives には入れていない）

検索を試したあとは `search_str=""` で POST し直し、`conf.json` の
`SearchStr` が空であることを確認した。サーバは kill 済み。

## 追加確認（検索モードで日付欄を押したとき）

playwright で実際にブラウザを動かして確かめた（実データは触らず、一時
`--datadir` に自分で作った予定 1 件を使用）。

1. `2026-08-25` に予定（`SEARCHME2`）を追加
2. 今週（`2026-08-26`）の画面で `SEARCHME2` を検索 → 検索結果に `2026-08-25`
   の行が出て、`week_bar` は無い（検索モードどおり）
3. その行の日付欄（左端の列）をクリック
   - URL: `?date=2026-08-25`（その日を含む週へ移動）○
   - `week_bar` が出力に含まれるようになる（`2026/08/24 – 08/30`）○
   - `conf.json` の `SearchStr` が `"searchme2"` → `""` になる（検索解除）○

依頼の (1)(2) とも確認でき、不具合は無かった。確認後は `conf.json` の
`SearchStr` が空であることを確認済み。サーバは kill 済み
（PID 確認 → `ps -fp` で消えたことも確認）。

## 判断が要る点

無し。見つけた不具合も無し。
