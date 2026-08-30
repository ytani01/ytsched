# TODO-115. implementer の effort を medium に下げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main のみ |
| 実施 | Opus 5 / effort high | main のみ |
| 消費 | output 3,353 / cache_creation 32,907 / 概算 $0.4 |
|      | main 100%（料金の割合） |

消費は `effort` を変えるところまでの集計。あとに続いた観察（TODO-116・
TODO-117 の報告を読んで判断した分）は、終点のコミットより後なので
入っていない。

## きっかけ

サブエージェントのモデルを下げてトークン消費を減らせないか、という相談から。
implementer と runner を Haiku にする案が出たが、runner は既に
`model: haiku` / `effort: low` になっている。implementer を Haiku に
するのは見送った。理由は次の 3 つ。

- `~/.claude/CLAUDE.md` の基準では、判断の要らない担当が Sonnet 以下。
  implementer は「最小限の変更にとどめる」「ついでの整理に手を出さない」と、
  変更の範囲を自分で線引きする担当で、ここに当たらない
- ytsched のコードは `HandlerBase` / `MainHandler` / `EditHandler` の関係や
  `SchedData` 周りなど、既存の書き方に揃える判断が要る
- 雑な変更を verifier / reviewer が拾い、main が指示し直すと、やり直し 1 回で
  Sonnet と Haiku の差額はほぼ消える

モデルは sonnet のまま、`effort` だけ下げて様子を見ることにした。

担当を `main のみ` にしたのは、変えるのが frontmatter の 1 行で、
確かめられることがこの項目の中に無いため。効果の判定は、次に implementer を
立てる項目での観察になる。

## やったこと

- `.claude/agents/implementer.md` の `effort` を `high` から `medium` に
  変えた（2026-08-30）。`.claude/agents/*.md` は Claude Code の起動時に
  しか読まれないので、利用者が再起動した
- 変更後に implementer を立てた TODO-116・TODO-117 の 2 件を観察し、
  **`medium` のままにすると決めた**

## 観察の結果

|                        | TODO-116 | TODO-117 |
|------------------------|----------|----------|
| 担当                   | implementer + verifier | implementer + verifier |
| verifier の不具合指摘  | なし | なし |
| lint / typecheck / test | 通過（512 件） | 通過（518 件） |
| 追加テストの有効性     | 分岐を潰すと 3 件とも FAIL | 分岐を潰すと該当 8 件・2 件が FAIL |
| 料金                   | $2.5（implementer 34%） | $3.5（implementer 49%） |

2 件とも verifier の指摘がゼロで、main が指示し直したやり直しも無かった。
追加したテストが実装を壊したときに実際に落ちるかまで確かめさせていて、
そこも通っている。

TODO-117 の途中で「検索モードでは PC のマウスドラッグが `swipeFinish()` に
届かない」ことが後から分かり、追加で直した。ただしこれは implementer が
自分で見つけて申告したもので、項目を立てた段階で見えていなかった仕様の穴。
`effort` を下げたことによる雑さではないと判断した。

`high` へは戻さない。

## テスト

- `.claude/agents/implementer.md` の frontmatter が
  `model: sonnet` / `effort: medium` になっていることを確認
- TODO-116・TODO-117 の verifier 報告
  （[TODO-116](../agents/TODO-116/verifier-report.md)・
  [TODO-117](../agents/TODO-117/verifier-report.md)）を読み、
  どちらも不具合の指摘が無いことを確認
