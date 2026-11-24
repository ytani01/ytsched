# TODO

**残っている項目: TODO-238、TODO-239。** これまでに 237 件を完了させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-240` から。**

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

## TODO-238. テストの説明文書の一覧に、載っていない 3 つのテストを足す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（文書）+ reviewer（Sonnet 5.5 / medium）+ verifier（Haiku 5.5 / low） |

- [ ] `tests/README.md` の一覧に `test_fix_id.py`・`test_notify.py`・`test_trash.py` を足し、
  それぞれが何を見ているかを書く

**無駄を省く工夫:** 文書だけの変更なので、verifier は一覧と `tests/` のファイルが一致するかだけを見る。

TODO-237 の作業中に implementer が見つけた（`archives/agents/TODO-237/implementer-report.md`）。

## TODO-239. 添付ファイルを外して同じ名前で付け直したとき、古い画像が表示され続けないかを確かめる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | verifier（Sonnet 5.5 / medium）→ 直すなら implementer（Sonnet 5.5 / medium）+ reviewer（Sonnet 5.5 / medium） |

- [ ] 添付を返す処理が `Cache-Control` を付けないため、ブラウザが古い画像を使い続けるかを確かめる
- [ ] 起きるなら、キャッシュさせない形に直す

**無駄を省く工夫:** 確かめるのは画像 1 つだけ。ブラウザは Playwright の Chromium だけで済ませる。

TODO-237 の reviewer の指摘 5（`archives/agents/TODO-237/reviewer-report.md`）。実害は確かめていない。
直すかどうかは、確かめた結果を見て利用者と決める。

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
