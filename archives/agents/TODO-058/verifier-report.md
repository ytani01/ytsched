# TODO-058 verifier 報告

依頼書（`request-verifier.md`）、implementer 報告、`TODO.md` の
TODO-058 節を読んだうえで確認した。

## 決まった手順

- `mise run fmt` ○（`ruff format` 25 files left unchanged / `ruff check` All checks passed）
- `mise run typecheck` ○（basedpyright 0 errors / mypy Success, 22 source files）
- `mise run lint` ○（上と同じ）
- `mise run test` ○（439 件成功）

## アプリの起動（ポート 18058、`--datadir` は一時ディレクトリ）

```
uv run ytsched webapp --datadir <tmp> --port 18058
curl http://localhost:18058/  → 200
```

- HTML に `{{` `{%` の生残りなし
- `#week_bar` の中に `.my-gage-bar`（`my-gage-axis` / `my-gage-base` /
  `svg#gage_r` / `my-gage-label` × 8）が入っていることを確認。
  `padding-left:22px` は無い
- playwright（`env -u DISPLAY`、`/usr/bin/chromium`）で確認
  - forward ボタン（`#forward_button` の `mousedown`）を押すと、
    `#gage_r` の `getBoundingClientRect().left` が 200 → 225.8 → 233.0 →
    239.6 → 241.4（以降変化なし）と、約 0.15〜0.2 秒かけて右へ動いた
  - home ボタン 1 回押しで `today`（2026-08-26）へ戻り、`left` も
    272.97 → 200（中央）に戻った
  - 検索モード（`?search_str=test`）では `#week_bar` も `#gage_r` も
    DOM に存在しない（count 0）。console error / pageerror は無し
    （`onloadHdr` のログのみ）
  - 通常モードでの console も error / warning なし
- **注意点（依頼書どおりの既知の挙動）**: `search_str` は `conf.json` に
  残るため、検索モードを試したあとに `?date=` だけで確認しようとすると
  検索モードのままになり `#gage_r` が見えず `bounding_box()` がタイムアウト
  した。`?search_str=` で解除してから確認し直して解決（コードの不具合ではない）

## キャプチャ

`tools/screenshot.py`（`env -u DISPLAY`）で撮影。保存先:
`/tmp/claude-649/.../scratchpad/shots/todo058_closed_{360,412,800}.png`
（セッション固有のスクラッチパスなので、このセッション終了後は残らない）

- 360px: 目盛りラベル 8 個（`-30y -1y -1m -1w  +1w +1m +1y +30y`）が
  重ならず等間隔に出ている。360px 拡大クロップでも余白あり
- 412px・800px: 同様に問題なし。針は中央、いちばん上の日付ブロック
  （2026/08/24 Mon）も隠れていない

## 見つかった不具合

なし。依頼に書かれた確認項目はすべて期待どおりだった。

## 判断が要る点

なし。
