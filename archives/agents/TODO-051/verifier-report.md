# TODO-051 verifier 報告

対象: `tools/screenshot.py` の `DEF_URL` 変更、`docs/Developer.md`・`TODO.md` の記述。
アプリは port 10085 で起動済み（`curl http://localhost:10085/ytsched/` → 200）。

## 1. 引数なし `mise run shot` （DISPLAY あり）

```
mise run shot -- -o <scratchpad>/shots/with-display
```

○ 通った。`shot_closed_412.png`（46k）・`shot_closed_800.png`（49k）を保存。既定 URL が
`/ytsched/` になったので、一覧がそのまま撮れることを確認。

## 2. 編集画面

```
mise run shot -- http://localhost:10085/ytsched/edit/ -o <scratchpad>/shots/edit-new
mise run shot -- http://localhost:10085/edit/         -o <scratchpad>/shots/edit-old
```

○ 新既定（`/ytsched/edit/`）は撮れた（15k）。
- `curl -s -o /dev/null -w '%{http_code}' http://localhost:10085/ytsched/edit/` → **200**
- `curl -s -o /dev/null -w '%{http_code}' http://localhost:10085/edit/` → **404**（旧既定だと 404 になることを実際に確認）

△ 気づいた点（範囲外・報告のみ）: `tools/screenshot.py` は HTTP ステータスを見ずに
撮ってしまうらしく、404 のページでも `exit=0` で PNG（4.6k・5.8k、404 ページの内容）を
保存した。今回の依頼（`DEF_URL` の変更確認）とは別の話なので直さず報告のみ。

## 3. DISPLAY あり／なし

- あり（`localhost:11.0`）: 1・2 とも通った（上記）
- なし（`env -u DISPLAY`）: 一覧・編集画面ともに通った。
  `shot_closed_412.png`（no-display: 46k / no-display-edit: 15k）等を保存。

TODO-051 本文の症状（`DISPLAY` があるとタイムアウトする）は、今回の環境では
再現しなかった（本文の「保留にした理由」と一致）。

## 4. PNG が壊れていないか

`file` コマンドで全て `PNG image data` と確認。サイズもゼロでない。

- with-display: 412x900 46k / 800x900 49k
- edit-new: 412x900 15k / 800x900 15k
- edit-old（404 ページ）: 412x900 4.6k / 800x900 5.8k
- no-display: 412x900 46k / 800x900 49k
- no-display-edit: 412x900 15k / 800x900 15k

壊れているものは無い。

## 5. lint / 型チェック

`mise.toml` の `fmt`・`lint`・`typecheck` は `src tests tools` を対象にしており、
`tools/screenshot.py` も対象。

- `uv run ruff format --check --line-length 78 tools/screenshot.py` → ○（"1 file already formatted"）
- `uv run ruff check --extend-select I tools/screenshot.py` → ○（"All checks passed!"）
- `uv run basedpyright tools/screenshot.py` → ○（"0 errors, 0 warnings, 0 notes"）
- `uv run mypy tools/screenshot.py` 単体指定 → mylog に py.typed が無い旨の
  `import-untyped` エラーが 1 件出た。ただし `uv run mypy src tests tools`（実際の
  タスクの叩き方）では **"Success: no issues found in 21 source files"**。
  単体指定したときだけ出る差分で、実害ではないと考えられる（念のため報告）。

## 6. `mise run test`

○ 通った。`ruff check` → All checks passed / `basedpyright` → 0 errors /
`mypy` → Success / `pytest tests` → **418 passed**（2.67 秒）。

## 判断が要る点

- 4-2 で触れた「編集画面が 404 でも `tools/screenshot.py` が黙って（404 ページの）
  スクリーンショットを撮ってしまう」件。今回の依頼の範囲（`DEF_URL` の確認）では
  ないため直していないが、気になれば別項目にするか検討を。
