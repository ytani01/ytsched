# TODO-190 verifier 報告

## 1. 公式ドキュメントの裏取り

`curl -A "Mozilla/5.0" https://platform.claude.com/docs/en/about-claude/pricing`
（HTTP 200）で本文を取得し確認した。

- 本文中に次の注記あり（`sonnet-5-introductory-pricing` の Aside）:
  > Sonnet 5, announced at launch as introductory pricing through August 31,
  > 2026, is now the standard price. The previously scheduled increase to
  > $3/$15 per million input/output tokens on September 1, 2026 will not occur.
- 価格表（Base input tokens / Output tokens）:
  - Claude Opus 5: $5 / MTok, $25 / MTok
  - Claude Sonnet 5: $2 / MTok, $10 / MTok
  - Claude Haiku 4.5: $1 / MTok, $5 / MTok

main の結論（$2/$10 のまま、値上げは行われなかった）と一致した。

## 2. `PRICING` との突き合わせ

`/home/ytani/.claude/bin/token-usage.py` の `PRICING`:
```
"claude-opus-5": (5.00, 25.00),
"claude-sonnet-5": (2.00, 10.00),
"claude-haiku-4-5": (1.00, 5.00),
```
3 モデルとも 1 で確認した公式単価と一致。○

## 3. 記述の食い違い確認

- `CLAUDE.md`（`git diff` で確認した差分）: 「2026-09-07 に公式のドキュメントで
  確認」と書かれている。事実関係は 1 の内容と整合する。
- `token-usage.py` の `PRICING` 直上のコメント: 「2026-09-06 に検算して誤りと
  分かった」と書かれている。**`CLAUDE.md`（2026-09-07 に確認）と
  `token-usage.py`（2026-09-06 に検算）で日付が 1 日ずれている。**
  「検算して誤りと分かった」と「公式ドキュメントで確認した」は文面上
  意味が異なる行為なので、日付が違うこと自体は矛盾ではなく、
  「いつ・どちらの方法で気づいたか」を書き分けているだけの可能性もある。
  ただし読み手には日付の食い違いに見えるので、main に確認してほしい点として挙げる。
- `TODO.md` の TODO-190 節（まだ未編集）:
  - 「単価は `claude-api` skill で確かめてから書き換える」とあるが、実際の
    確認方法は WebFetch で公式ドキュメントを直接引く形になっていた
    （少なくとも自分の確認はそう行った）。`claude-api` skill を使ったかどうかは
    main 側のログでないと分からない。記述と実施の方法が食い違っている可能性がある
  - 「`CLAUDE.md` の $3/$15 も書いた時点の見込みなので、実際と違うかもしれない」
    という記述は、結果的に「実際と違った（値上げ自体が起きなかった）」ことと
    整合しており、矛盾はない

## 4. `token-usage.py --list` の動作確認

```
~/.claude/bin/token-usage.py --list
```
エラーなく一覧が出力された（TODO-001〜189 相当の項目一覧、件数省略）。○

## 5. 古い「$3/$15 に書き換える」指示の残存確認

```
grep -rn '3/\$15\|\$3/\$15\|3.00, 15.00' /home/ytani/work/ytsched --include='*.md' --include='*.py' | grep -v archives/
```
`CLAUDE.md` の該当箇所は既に書き換え済み（1 参照）で「$3/$15 に書き換える」という
指示文は見当たらなかった。`archives/todo/` 配下（対象外）以外に現行の指示は
見つからなかった。○

## まとめ・main の判断が要る点

- 単価そのもの（$2/$10, $5/$25, $1/$5）は公式ドキュメントと一致。数値面は問題なし
- `CLAUDE.md`（2026-09-07 確認）と `token-usage.py` のコメント（2026-09-06 検算）の
  日付表記が 1 日ずれている。意図的な書き分けか単純な記載ミスか、main に確認してほしい
- `TODO.md` の TODO-190 節に「`claude-api` skill で確かめてから書き換える」と
  あるが、実際にその skill を使ったかは verifier からは確認できない
