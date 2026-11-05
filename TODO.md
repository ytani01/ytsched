# TODO

**残っている項目: TODO-228、TODO-229、TODO-230。** これまでに 227 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-231` から。**

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

## TODO-228. 詳細欄を広げる基準の高さが、フォーカス中の変化を取りこぼす

TODO-227 の残り。基準の高さは入力欄にフォーカスが無いときだけ更新するので、次の場面で詳細欄が広がらない、または余計に広がる。どれも入力内容は失われない。実害は未確認のものを含む。

- [ ] 直すか（対応しない）とするかを利用者に聞く

対象の場面: フォーカスしたまま横向きから縦向きへ回す / PC で入力欄にフォーカスしたままウィンドウを低くする / 詳細欄を離れたあとに低い高さの `resize` が来る / 広げている間の `resize` でページが元の位置へ戻る / 高さ 407px 未満の画面。報告は `archives/agents/TODO-227/reviewer-report.md`。

| | main | 担当 |
|---|---|---|
| 見込み | Opus 5.5 / effort medium | main のみ（決めるだけ。直すなら implementer + reviewer + verifier を立て直す） |

**無駄を省く工夫:** 実機で困ってから直す選択肢を先に聞く。直す場合も `TODO-227` のテストの範囲で確かめる。

## TODO-229. `main-page.js` の `scroll-behavior` のコメントを実態に合わせる

`main-page.js` の 436 行と 501 行のコメントは Bootstrap の `scroll-behavior` を理由に挙げているが、CSS にその指定が無い（TODO-227 のレビューで判明）。指定の有無を確かめ、コメントと `behavior` の指定を直すかを決める。

- [ ] 読み込んでいる CSS に `scroll-behavior` が無いことを確かめる
- [ ] コメントを直す。指定を外すと滑らかに動く恐れが無ければ、指定も外す

| | main | 担当 |
|---|---|---|
| 見込み | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium） |

**無駄を省く工夫:** 数行の項目なので main が書く。確認は週送りとホームボタンの動きの代表 1 つずつに絞る。

## TODO-230. 編集後の hook で ESLint が動かない

`.claude/hooks/fmt-one.sh` が `.js` の編集後に ESLint を呼ぶが、`eslint@10.14.0` が入っておらず `npx canceled due to missing packages` で止まる（TODO-227 で発生。node を上げた `e1c47b2` との関係は未確認）。

- [ ] 原因を確かめて、hook が ESLint を走らせられるようにする

| | main | 担当 |
|---|---|---|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ verifier（Sonnet 5.5 / medium） |

**無駄を省く工夫:** 確認は `.js` を 1 つ編集して hook の出力を見るだけにする。ESLint の全件実行は頼まない。

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
