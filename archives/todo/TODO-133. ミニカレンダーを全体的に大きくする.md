# TODO-133. ミニカレンダーを全体的に大きくする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ実装 + verifier |
| 実施 | Opus 5 / effort medium | main のみ実装 + verifier |
| 消費 | output 7,864 / cache_creation 45,756 / 概算 $0.6 |
|      | verifier 61% + main 39%（料金の割合） |

## きっかけ

ミニカレンダーが小さく、フォント・予定のドット・ToDo の四角をまとめて
大きくしたかった。ただし日セルは 24px 固定で、2 ヶ月ぶんの合計が約
348px あり、幅の狭い端末では px を増やすとはみ出す恐れがあった。

## やったこと

`src/ytsched/webroot/static/css/my.css` の `.my-mini-cal*` だけを変更した。
テンプレートと Python コードは触っていない。

- `.my-mini-cal`: `flex: 1 1 0` / `table-layout: fixed` / `max-width: 200px`
  を足し、`font-size` を x-small → small。日セルの固定幅をやめ、2 つの表で
  使える幅を分け合う形にした（広い画面で間延びしないよう上限を付けた）
- `.my-mini-cal-day`: `width: 24px` を削除、`height` 24px → 30px
- `.my-mini-cal-caption`: `font-size` small → medium
- `.my-mini-cal-daynum`: `line-height` 14px → 16px
- `.my-mini-cal-dot` / `.my-mini-cal-sq`: 6px → 8px
- `.my-mini-cal-row`: `gap` 10px → 6px

## テスト

verifier が確認した（報告は
[archives/agents/TODO-133/verifier-report.md](../agents/TODO-133/verifier-report.md)）。

- `mise run lint` / `mise run test`（556 passed）が通った
- 一時ディレクトリを `--datadir` に指定してアプリを起動し、週表示が
  HTTP 200 で返り、`my-mini-cal` のマークアップが従来どおり出ることを確認
- 幅は Playwright で実測し、360px 幅で横スクロールが出ないことを確認
- セルの中身は約 25px で、30px の高さに収まる

なお、立てたときの本文には「`container` の左右パディング 12px」と書いたが、
実際の `main.html` は `container-fluid p-0` で `.p-0` が勝ち、パディングは
0 だった（幅は 360px まるごと使える）。はみ出さない結論は変わらない。
