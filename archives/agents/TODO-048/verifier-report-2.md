# TODO-048 verifier 追加確認（行の高さの直し）報告

## 環境

- `--datadir` は自分で用意した一時ディレクトリ
  （`/tmp/claude-649/.../scratchpad/datadir-old` と `datadir-new`）を使用
- HEAD の webroot は `git archive HEAD src/ytsched/webroot` で
  `/tmp/.../scratchpad/oldroot` に取り出し
- 旧: port 10093（`--webroot oldroot`）、新: port 10094（作業ツリーそのまま）
- 両方に同じ日付（2026-08-25）へ、詳細ありの予定 1 件・詳細なしの予定 1 件を
  jsonl で直接投入（テストデータ）
- 測定・クリック確認には `~/work/next-ai-draw-io/node_modules/playwright`
  （version 1.57.0）を使った（本リポジトリには playwright が無いため）

## 1. `getBoundingClientRect()` による高さの突き合わせ

`.my-sde` の `getBoundingClientRect().height` を旧・新で比較。

| 行 | 旧（HEAD） | 新（作業ツリー） |
|---|---|---|
| 詳細ありの予定 | 44.00px | **44.25px** |
| 詳細なしの予定 | 26.00px | 26.00px（変化なし） |

○ 44.00px → 44.25px。依頼書に書かれた「44.25px になり、変更前の
44.00px とほぼ同じに戻った」と一致。50.25px への崩れは再現しない。
詳細なしの行は旧・新で完全に一致（26.00px）。

## 2. 開閉スイッチの操作

`.my-sde-detail-sw label` をクリックして `.my-sde-detail` の高さを確認。

- クリック前: 18.25px（折りたたみ、プレビュー表示分）
- クリック後: 47px（展開）

○ 押せて詳細が開くことを確認。`label` の余白を削っても、クリック領域は
`.my-btn`（親の `.col-1`）が担っているため支障なし。

## 3. lint・テスト

- ○ `mise run lint`（fmt/check/basedpyright/mypy）: 全て通過
- ○ `uv run pytest tests`: **427 passed**

## 4. キャプチャ

- ○ `env -u DISPLAY uv run --with playwright python tools/screenshot.py
  'http://localhost:10094/ytsched/' -p todo048-verify2` で
  `todo048-verify2_closed_412.png` / `_800.png` を撮り直した
  （`~/tmp/playwright-mcp/`）。目視でも崩れなし、`{{ }}` / `{% %}` の
  生残りなし

## 結論

依頼された 4 項目とも問題なし。行の高さの直しは数値でも確認でき、
50.25px への崩れは解消している。main の判断が要る点は特に無し。
