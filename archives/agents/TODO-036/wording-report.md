# TODO-036 wording 報告

対象は次の 2 ファイル（どちらも未コミット）。

- `TODO.md`（`git diff TODO.md` の差分部分のみ、「## TODO-036. …」の節）
- `archives/agents/TODO-036/implementer-request.md`

基準は `HEAD`（この 2 ファイルはまだコミットされていないので作業ツリーの
まま `git grep ... HEAD -- '*.md'` で数えた）。

## 前例の無い語（0 件）

### 疑問

- 出てくる箇所: `implementer-request.md` 5 行目
  「疑問があれば実装を止めて報告する。」
- `git grep -cF 疑問 HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: 一般的な日本語で、造語ではない。ただの見落としと見る

### 呼び出し可能

- 出てくる箇所: `implementer-request.md` 12 行目
  「`func` はデコレータが受け取る任意の呼び出し可能オブジェクトなので」
- `git grep -cF 呼び出し可能 HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: Python の `Callable` を指す一般的な訳語（「呼び出し可能オブジェクト」
  は Python 公式ドキュメントの定訳）。このリポジトリでの初出だが、
  リポジトリ外で広く通用する語

### デコレータ

- 出てくる箇所: `implementer-request.md` 12 行目（同上の文の一部）
- `git grep -cF デコレータ HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: Python の一般的な用語（decorator のカタカナ表記）。造語ではない

### 導入する

- 出てくる箇所: `TODO.md` 見出し「## TODO-036. click_utils.py を導入する」
- `git grep -cF 導入する HEAD -- '*.md'`: 前例なし（0 件）
  （「導入」単体では既存文書にも出ている可能性があるが、「導入する」の
  活用形としては前例なし）
- 見立て: ごく普通の日本語。造語ではない

## 前例が少ない語（参考、件数 6 件以下）

- **手書き**（`implementer-request.md` 21 行目「手書きの `--debug` / `-d`
  オプション 3 箇所を消す」）: 6 件。一般的な語
- **未使用**（`implementer-request.md` 39 行目「未使用にならないか確認し、
  未使用になったものだけ消す」）: 6 件。一般的な語（IT 用語としても定着）

## それ以外に見た語（前例あり、参考）

- 衝突: 10 件（`TODO.md` 差分 34 行目「衝突するところと、決めたこと」）
- 寄せる: 7 件（`TODO.md` 差分「`version_option` に寄せ」）
- 二重: 24 件（`implementer-request.md` 26 行目「二重に付くため」）
- 型ヒント: 16 件（`TODO.md` 差分、`implementer-request.md` 双方に複数箇所）
- フラグ: 3 件

## まとめ

- 読んだファイル: `TODO.md`（差分部分）、
  `archives/agents/TODO-036/implementer-request.md`
- 前例の無い語（0 件）: **4 語**（疑問、呼び出し可能、デコレータ、導入する）
  - いずれも一般的な日本語・Python 用語で、このリポジトリだけの言い換えに
    見えるものは無いという見立て。決めるのは main

---

## 追記: 実装コミットぶんの確認（TODO-036 決着時）

前回（このファイル冒頭）は「立てる」コミットの `TODO.md` と
`implementer-request.md` だけを見た。今回は残り全部を対象にした。
前回挙げた 4 語（疑問・呼び出し可能・デコレータ・導入する）は main が
「一般的な語なのでそのまま」と決めたので再掲しない。

### 対象にしたファイル

- `TODO.md`（`git diff TODO.md`。TODO-036 の節を消して完了済みの目次に
  足した差分）
- `src/README.md`（`git diff src/README.md`。モジュール一覧に
  `click_utils.py` を足し、共通オプションの説明を書いた差分）
- `archives/todo/TODO-036. click_utils.py を導入する.md`（新規）
- `archives/agents/TODO-036/README.md`（新規）
- `archives/agents/TODO-036/` の
  implementer-request.md / implementer-report.md / verifier-request.md /
  verifier-report.md / reviewer-request.md / reviewer-report.md
- `src/ytsched/mylog.py` の `loggerInit()` の docstring（`.md` ではないが、
  依頼により文書として一緒に見た）

基準は `HEAD`（対象はすべて未コミット）。

### 前例の無い語（0 件）

#### メタデコレータ

- 出てくる箇所: `archives/todo/TODO-036. click_utils.py を導入する.md`
  10 行目「他のプロジェクト（`~/work/tmr`）と共通の、click の共通
  オプションをまとめたメタデコレータ `click_common_opts()`」
- `git grep -cF メタデコレータ HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: 「デコレータを返すデコレータ」を指しているようだが、一般には
  「decorator factory（デコレータファクトリ）」と呼ばれることが多く、
  「メタデコレータ」は一般に定着した訳語とは言えない。このリポジトリ
  だけの言い換えに見える度合いがやや高い

#### 束縛

- 出てくる箇所: `archives/agents/TODO-036/reviewer-report.md`
  「`Command | Callable[..., Any]` 束縛の TypeVar」
  「`Callable[..., Any]` に束縛される」
- `git grep -cF 束縛 HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: 型理論・Python の `typing` まわりで「型変数を束縛する」は
  一般的な言い方。このリポジトリでは初出だが、外部で広く通用する語

#### 肩代わり

- 出てくる箇所: `archives/todo/TODO-036. click_utils.py を導入する.md`
  「`CONTEXT_SETTINGS` は `help_option` が肩代わりするので消せる」
- `git grep -cF 肩代わり HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: 普通の日本語の慣用表現。造語ではない

#### 評価順

- 出てくる箇所: `archives/agents/TODO-036/reviewer-request.md`
  「eager オプションの評価順」、
  `reviewer-report.md`「評価順は問題なし。`iter_params_for_processing()`
  が eager …」
- `git grep -cF 評価順 HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: 「オプションが処理される順序」を指す造語気味の圧縮表現。
  一般に流通しているとまでは言い切れない。判断できない

### 参考: 前例はあるが確認した語

- 追随漏れ: 2 件（TODO-027・TODO-033 の archives に既出）。新語ではない
- 潰れる: 2 件（TODO-018・`docs/data-format.md` に既出、いずれも「タブが
  潰れる」の文脈）。`reviewer-report.md` の「シグネチャが…に潰れる」は
  比喩の使い方が違うが、語自体は前例あり
- 水準: 11 件（既出）。`mylog.py` の docstring 変更部分にも使われているが
  新語ではない
- 差し引く: 0 件だが一般的な動詞なので割愛（造語性は無いと判断）
- 揃え直す: 0 件だが「揃える」の一般的な活用として割愛

### まとめ（追記分）

- 読んだファイル: 上記「対象にしたファイル」一覧のとおり
- 前例の無い語（0 件）: **4 語**（メタデコレータ、束縛、肩代わり、評価順）
  - 「束縛」「肩代わり」は一般に通用する語という見立て
  - 「メタデコレータ」「評価順」はこのリポジトリ（または書き手）独自の
    圧縮・言い換えに見える度合いがやや高いという見立て。決めるのは main
