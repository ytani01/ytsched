# TODO-021 の分担

項目そのものは
[`archives/todo/TODO-021. リファクタリング（挙動は変えない）.md`](../../todo/TODO-021.%20リファクタリング（挙動は変えない）.md)。

## 誰に何を担当させたか

| 担当 | 依頼 | 報告 | 何を任せたか |
| --- | --- | --- | --- |
| implementer(1) | [request](implementer1-request.md) | [report](implementer1-report.md) | 現状の挙動を押さえるテスト（`src/` は触らせない） |
| implementer(2) | [request](implementer2-request.md) | [report](implementer2-report.md) | リファクタリング本体（A〜E） |
| verifier | [request](verifier-request.md) | [report](verifier-report.md) | 「変える前と同じに動くか」の確認 |
| reviewer | [request](reviewer-request.md) | [report](reviewer-report.md) | 条件式のずれ（テストでは捕まらないもの） |
| runner | （依頼は口頭） | [report](runner-report.md) | 最終確認の 5 コマンド |

## その分担にした理由

### implementer を 2 人に分けた

TODO の `見込み:` では implementer は 1 人だった。**着手時に 2 人へ
分けた。**

「分割の前に、現状の挙動を押さえるテストを足す」のがこの項目の前提
だが、同じ担当が両方をやると、**これから変えるつもりの形に合わせた
テスト**になりかねない。テストとリファクタリングは、片方がもう片方の
検算になっていないと意味が無い。

分けた結果、implementer(2) は**テストを 1 行も書き換えずに**終えている。

implementer(1) には `src/` を触らせず、実際に
`git status --porcelain src` が空であることを main でも確認した。

### verifier と reviewer は両方入れた

TODO-017 の基準どおり。**分岐や条件式が動く**項目なので reviewer が要る。

実際、reviewer だけが `is_todo()` の委譲で debug ログが 0 行から
毎回 1 行に増えることを見つけた。テストは通るし、アプリも動くので、
verifier では捕まらない種類の指摘。

### runner を最終確認に使った

TODO-022 で作った定義の試用。verifier が終わったあと、reviewer の指摘を
main が直したので、**もう一度 5 コマンドを流すだけ**の仕事が発生した。
切り分けの要らない仕事なので runner に回した。

## 実測（TODO-022 の判定材料）

| 担当 | モデル | 所要 | トークン | ツール呼び出し |
| --- | --- | --- | --- | --- |
| implementer(1) | opus | 12 分 | 121k | 34 |
| implementer(2) | opus | 10 分 | 115k | 60 |
| verifier | sonnet | 4 分 26 秒 | 64k | 49 |
| reviewer | opus | 4 分 41 秒 | 85k | 19 |
| runner | haiku | **34 秒** | **18k** | 7 |

**runner は使える。** 決まった 5 コマンドを流して結果を写すだけなら、
verifier の 1/8 のトークン・1/8 の時間で済む。切り分けをしない線引きも
守られていて、「すべて成功」以上のことを書いてこなかった。

ただし**verifier の代わりにはならない**。verifier はアプリを起動して
不正な正規表現や ToDo 完了の経路を叩き、`pgrep -f "ytsched webapp"` が
自分自身を拾う問題まで自力で回避している。runner にそれは無理だし、
定義でもさせないことにしている。**「決まった手順を流すだけ」を runner、
「実際に叩いて確かめる」を verifier** という切り分けで足りる。

## main が判断したこと

- **reviewer の C-1（debug ログの増加）を直した。** `type_is_todo()` 側の
  debug を落とす形。理由は TODO の archives 側に書いてある
- **reviewer の L-1（`"%H:%M"` → `TIME_FORMAT`）は残した**
- **`cmd_add()` の引数の並びを変えない**と決めて implementer(2) へ伝えた。
  implementer(1) は「並びを変えるならテストを直してよい」と報告して
  いたが、`cmd_add()` は A〜E の範囲外だし、「テストは 1 行も
  書き換えない」を崩したくなかった
- **verifier が「`TODO.md` に差分があるが implementer(2) は触っていない」
  と挙げてきた件**は、利用者が別途 TODO-023 を追記したもので、
  この項目とは無関係。報告を鵜呑みにせず食い違いとして挙げたのは正しい
