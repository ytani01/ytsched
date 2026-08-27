# TODO-081 wording 報告

対象は次の 8 ファイル（新規 `TODO-081.` の archives ファイルを含む）。

- `TODO.md`
- `src/README.md`
- `tests/README.md`
- `archives/todo/TODO-081. ハンドラの役割と、依存の渡し方を整理する.md`
- `archives/agents/TODO-081/README.md`
- `archives/agents/TODO-081/implementer-task.md`
- `archives/agents/TODO-081/implementer-report.md`
- `archives/agents/TODO-081/verifier-report.md`
- `archives/agents/TODO-081/reviewer-report.md`

前例の件数が少ない順に並べる。基準は `HEAD`（このコミット前）。

## 契約

- 出てくる箇所: `reviewer-report.md`「`make_app()` が `(app, sd)` を
  返す案も、`WebTestBase.get_app()`（`tests/test_web.py:147`）が
  `tornado.testing` の**契約上** `Application` 単体を返す必要があるため」
  「`tornado.testing` の**制約により**機能しないことを確認できた」
  （「制約」は前例が多いが「契約」は 1 か所）
- `git grep`: `契約` は `HEAD` に 1 件あるが、その 1 件は
  `archives/agents/TODO-030/wording-request.md` に載っている
  「終了コード契約」という**禁止語の例そのもの**（`~/.claude/CLAUDE.md`
  が名指しで禁止している造語の実例）。実質的な用例としては初出
- 見立て: `~/.claude/CLAUDE.md` に「造語を使わない。『回帰基準』
  『全緑』『終了コード契約』『鳴動』『契約』のように…作らない」と
  名指しで挙げられている語そのもの。**最も直したほうがよいと思う語。**
  「tornado.testing の決まり」「tornado.testing の仕様」で足りる場面

## 静的型

- 出てくる箇所: `README.md`「`self._app` の**静的型**が
  `tornado.web.Application` のまま」、`implementer-report.md` 同旨、
  `reviewer-report.md` 同旨（複数箇所で使われている）
- `git grep`: 0 件（前例なし）
- 見立て: 型チェッカ関連の一般的な専門用語（動的型と対になる語）。
  このリポジトリでの初出ではあるが、一般に通用しそうで問題は薄い

## 動的属性

- 出てくる箇所: `implementer-report.md`「`app.sd = sd` で素朴に
  **生やす**つもりだった」、`reviewer-report.md`「`app.sd = sd` と
  **動的属性**を生やす案」
- `git grep`: `動的属性` 0 件（前例なし）。「生やす」は既存の言い回しか
  未確認（下記参照）
- 見立て: Python でよく使う一般的な言い方（インスタンスへの動的な
  属性追加）。リポジトリ初出だが専門用語として通用しそう

## 素通しの関数

- 出てくる箇所: `implementer-report.md`「`app_sd(app)` という
  **素通しの関数**にした」
- `git grep`: `素通しの関数` 0 件。「素通し」単体は 18 件あるが
  （`docs/data-format.md` などで「壊れた行を素通しする」の意味で
  多用）、**「〜する関数」を指す名詞的な使い方は初出**
- 見立て: 「中身を加工せず取り次ぐだけの関数」という意味は文脈から
  読み取れるが、このリポジトリでの「素通し」はこれまで動詞的
  （「素通しする」）にしか使っておらず、名詞化した言い方は独自寄り。
  判断できない

## 対象名

- 出てくる箇所: `implementer-task.md`「ファイル名は既存の並び…に
  釣り合うものにする」、`README.md` / `implementer-report.md`
  「**対象名** + `_util(s)`」（`click_utils.py` との並びを説明する語）
- `git grep`: 0 件（前例なし）
- 見立て: 「モジュールが扱う対象の名前」という意味で読めば普通の日本語。
  一般に通用しそうで、造語というより素朴な言い換え

## 差分レビュー

- 出てくる箇所: `verifier-report.md`「内容は目視で軽く見ただけで、
  詳細な**差分レビュー**はしていない（依頼の範囲を超えるため）」
- `git grep`: 0 件（前例なし）
- 見立て: 「diff review」の直訳的表現だが、IT の現場で普通に使われる
  言い方。一般に通用しそうで問題は薄い

## 短い寿命

- 出てくる箇所: `reviewer-report.md`「テストプロセスの**短い寿命**を
  考えると、素の `dict` でも実質的な違いは無い」
- `git grep`: 0 件（前例なし）
- 見立て: 「プロセスの寿命（lifetime）」は一般的な言い方。リポジトリ
  初出だが問題は薄い

## 不親切

- 出てくる箇所: `reviewer-report.md`「エラーメッセージが…デバッグ時に
  やや**不親切**かもしれない」
- `git grep`: 0 件（前例なし）
- 見立て: ごく普通の日本語（「羽目」「事柄」に近い）。問題なし

## デバッグ時

- 出てくる箇所: `reviewer-report.md`（上と同じ文）
- `git grep`: 0 件（前例なし）
- 見立て: 一般的な複合語。問題なし

## 転送用（のメソッド）

- 出てくる箇所: `implementer-task.md`「`HandlerBase` に**転送用の
  メソッド**を残さない」、`README.md` 同旨
- `git grep`: `転送用` 0 件（`転送` 単体は 13 件あり、`super().__init__()`
  へ「転送する」という動詞の用例は既にある）
- 見立て: 「委譲するためだけのメソッド」の意味で、既存の「転送する」の
  名詞化。素直な言い換えに見え、問題は薄い

## GC 追随

- 出てくる箇所: `reviewer-report.md`「`weakref` を使っているので
  エントリは `app` の GC に**追随**して消え」
- `git grep`: `追随` 単体は 47 件あり定着済み（TODO-080 の
  「キャッシュが…追随しない」など）。「GC」との組み合わせは初出だが、
  意味は文脈から自明
- 見立て: 一般的な言い方の組み合わせ。問題は薄い

---

## 前例が複数あり、既に定着していると見立てた語（参考）

`確信度の高い指摘` / `確信度の低い指摘`（`.claude/agents/reviewer.md` の
定義由来、112 件）、`純粋な関数`（6 件）、`型チェッカ`（7 件）、
`妥当`（100 件）、`決まり`（99 件）、`並び`（64 件）、`素通し`（動詞、
18 件）、`実害`（63 件）、`判断が要る点`（128 件）は、いずれも前例が
複数あり定着した言い回しと見立て、候補から外した。

---

## 読んだファイル

- `TODO.md`
- `src/README.md`
- `tests/README.md`
- `archives/todo/TODO-081. ハンドラの役割と、依存の渡し方を整理する.md`
- `archives/agents/TODO-081/README.md`
- `archives/agents/TODO-081/implementer-task.md`
- `archives/agents/TODO-081/implementer-report.md`
- `archives/agents/TODO-081/verifier-report.md`
- `archives/agents/TODO-081/reviewer-report.md`

前例なしの語数: 10 語（`静的型` / `動的属性` / `素通しの関数` /
`対象名` / `差分レビュー` / `短い寿命` / `不親切` / `デバッグ時` /
`転送用` / `GC 追随`）＋実質初出扱いの `契約`（1 件だが禁止語の例示
のみ）を合わせて 11 語。
