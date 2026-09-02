# TODO-158. バージョン表示をクリックすると GitHub 上の User.md を開くようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ |
| 実施 | Sonnet 5 / effort low | main + verifier |

## きっかけ

フッターのバージョン表示（`ytsched {{ version }}`）が、ただのテキストに
なっていた。押すと使い方（`docs/User.md`）が読めると分かりやすい。

## やったこと

`main.html` の `ytsched {{ version }}` を `<a>` タグにし、
`https://github.com/ytani01/ytsched/blob/HEAD/docs/User.md` へのリンクに
した。ブランチ名を `develop` のように固定すると、将来デフォルト
ブランチが変わったときにリンク切れになる。GitHub は `HEAD` を
デフォルトブランチへのエイリアスとして解決してくれるので、それを使った。

## テスト

verifier に依頼。

- `mise run lint`: 通過（ruff format / ruff check / basedpyright / mypy）
- `mise run test`: 607 passed
- `--datadir` に一時ディレクトリを指定してアプリを起動し、`curl` で
  取得した HTML のフッターに、リンクが正しく展開されていることを確認
  （`{{ }}` / `{%` の未展開タグは 0 件）。サーバログに例外なし
