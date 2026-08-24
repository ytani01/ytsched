# TODO-041 の分担

追加読み込みのたびに画面が下から上へ流れるのを直す。

| 担当 | 何を任せたか | 依頼書 / 報告 |
|---|---|---|
| main | 症状の再現、原因の特定、`main.html` の 1 行の修正 | — |
| verifier | 直ったことの確認（lint・テストと、追加読み込み直後のスクロール位置） | [依頼](verifier-request.md) / [報告](verifier-report.md) |
| wording | コミットに入る `.md` から前例の無い語を挙げる | [依頼](wording-request.md) / [報告](wording-report.md) |

## この分担にした理由

### main が原因を突き止めた

利用者からは「スクロールで追加読み込みが起きると、必ず下から上へ自動
スクロールする。実機で確認できないので確かめてほしい」という形で来た。
症状の再現と原因の切り分けが最初の仕事で、それが済めば直す量は 1 行と
分かっていた。

再現には Playwright（headless）を使った。**headless の Chromium は smooth
スクロールを実行しない**ので、`scrollTo()` が smooth 扱いになっていれば
スクロールが起きずに止まる。これがそのまま切り分けの手がかりになった。

```
CSS が smooth のまま scrollTo({top:2500, behavior:'auto'}) → 1000 のまま動かない
scroll-behavior を auto に戻して同じ呼び出し               → 2500 へ即座に移動
```

`"auto"` が CSS の `scroll-behavior` に従っていることが、これで確かめられた。

### implementer を分けなかった

直す量が `main.html` の `"auto"` → `"instant"` の 1 か所だけで、
`~/.claude/CLAUDE.md` の目安（複数のファイルにまたがる、実装とテストと文書が
まとまって要る）のどれにも当たらない。

### reviewer を入れなかった

`~/.claude/CLAUDE.md` では「挙動や分岐が変わる項目には入れる」となっている。
今回はスクロールの見え方が変わるが、**変えたのは `scrollTo()` に渡す引数
1 つで、分岐も呼び出しの順序も増えていない**。設計上の判断がある変更では
ないので入れなかった。

### verifier には判定の値まで渡した

修正前に main が測った 2 つの値（追加読み込み直後の `scrollY` が `0`、
`scrollToId` が狙った位置が `2611`）を依頼書に書き、「`0` でなく狙った位置に
一致すれば直っている」という形にした。headless で `scroll` イベント経由では
`scrollHdr` が発火しなかったことも書き添えて、`scrollHdr` を直接呼ぶ手順を
渡している。
