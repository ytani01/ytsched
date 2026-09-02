# TODO-161. フッターの左右三角とホームボタンの調整

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ |
| 実施 | Sonnet 5 / effort medium | main のみ |

## きっかけ

フッターの前週・次週ボタン（`back_button` / `forward_button`）が隣接して
いて押し間違えやすいのと、ホームボタンが行の中央に来ていなかったので、
調整してほしいという要望があった。

## やったこと

`main.html` のメニュー行を、ハンバーガー・前週・次週ボタンをまとめる
`my-menu-nav-left` と、検索欄の `my-menu-search-col` の 2 つを両側に置き、
間にホームボタンを挟む構成に組み替えた。`my.css` の `.my-menu-nav-row` を
12 列グリッドから flex レイアウトに変更し、両側の要素に `flex: 1 1 0` を
与えることで、左右の幅が異なっていてもホームボタンが常に行の中央に
来るようにした。

前週・次週ボタンの間には、`forward_button` に `my-menu-nav-col-gap`
（`margin-left: 0.5em`）を足して間隔を空けた。

## テスト

- `mise run lint` / `mise run test`（607 passed）: 通過
- `--datadir` に一時ディレクトリを指定してアプリを起動し、
  `mise run shot` でフッター部分をスクリーンショットで確認。
  三角の間に間隔ができ、ホームボタンが中央に揃っていることを目視で確認
