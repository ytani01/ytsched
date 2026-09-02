# TODO-159. フッターの ＜ ＞（chevron-left/right）を塗りつぶし三角形にする

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ |
| 実施 | Sonnet 5 / effort medium | main + verifier |

## きっかけ

フッターの前週・次週ボタン（`back_button` / `forward_button`）が線画の
山かっこ（`chevron-left` / `chevron-right`）で、三角形にしたいという
要望があった。

## やったこと

`icons.svg` の `chevron-left` / `chevron-right` の `<symbol>` を削除し、
代わりに `triangle-left` / `triangle-right`（`circle-up-fill` などと
同じ `fill="currentColor" stroke="none"` の塗りつぶし）を追加した。
`main.html` の該当箇所の `<use>` を差し替えた。

`tools/icons_preview.py` にも `chevron-left` / `chevron-right` の参照が
残っていたため（verifier の確認で判明）、`triangle-left` /
`triangle-right` へ書き換えた。

## テスト

verifier に依頼（`archives/agents/TODO-159/verifier-report.md`）。

- `mise run lint` / `mise run test`（607 passed）: 通過
- `chevron-left` / `chevron-right` の参照が、修正後は
  リポジトリ内に残っていないことを確認
- `--datadir` に一時ディレクトリを指定してアプリを起動し、フッターの
  HTML に `#triangle-left` / `#triangle-right` への参照が出ていることを
  確認
