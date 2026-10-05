# TODO-223. docs/User.md のファイル名を UsersGuide.md に変える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 30 | 7,998 | 19,188 | 1,584,163 | 88% |
| verifier | Sonnet 5.5 | medium | 16 | 109 | 50,567 | 167,402 | 12% |
| 合計 |  |  | 46 | 8,107 | 69,755 | 1,751,565 | 計 1,829,473 |

- TODO-222 と並行したので、範囲が TODO-222 と重なっている。main の分には
  TODO-222 の決着の作業も入っている
- ファイル名は、見出しの `/` をパスに使えないので `／` にした

## きっかけ

利用者向けの文書のファイル名を `User.md` から `UsersGuide.md` に変えたい。

## やったこと

- `git mv docs/User.md docs/UsersGuide.md`
- 参照を直した: README.md、docs/Install.md、docs/Developer.md、main.html の
  GitHub へのリンク、my.css のコメント、mise.toml の description、
  tools/annotate.py の docstring
- 直さなかったもの: `archives/` の中（当時の記録）、docs/Developer.md から
  archives の TODO-152 のファイルへ張ったリンク（そのファイル名のまま）、
  図のファイル名（`docs/user-*.png`、`tools/user-figs.json`）
- TODO-222 の未コミットの変更が `docs/User.md` にあったので、worktree
  （ブランチ `todo-223`）で作業し、TODO-222 のコミット後に develop へ
  取り込んだ。改名と TODO-222 の書き足しは衝突なく合わさった

## 確かめたこと

verifier が、参照の取り残しが TODO-152 へのリンク 1 件だけであること、
変えた相対リンクの行き先が実在すること、main.html のリンクの文字列、
`archives/` と図のファイル名が変わっていないことを確かめた
（[verifier-report.md](../agents/TODO-223/verifier-report.md)）。
取り込んだあとに main も、develop で取り残しが同じ 1 件だけで、
`docs/UsersGuide.md` に TODO-222 の書き足しが入っていることを見た。

## 残ること

- main.html のリンクは GitHub の `HEAD` を指すので、push するまでは
  新しい名前が 404 になる

## 分担の振り返り

- verifier は食い違いを見つけなかった。置き換えで漏れやすい
  archives へのリンクは、main が実装中に自分で戻していた
- 見込みと実施は一致した
- 次に同じ規模の改名をするなら、置き換えを `sed` で一括にせず、
  `archives/` を指すリンクを除いた `rg` の結果から置き換える。一括で
  置き換えて戻す手間が出た。main が叩いた `rg` を、パス無しで
  標準入力が空でないシェルから呼んで固まらせたので、
  `rg … . < /dev/null` の形で渡す
