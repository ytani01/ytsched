# TODO-061 wording 報告

`~/work/ytsched/TODO.md` の TODO-061 の節（この時点では既に完了済みへ
移されている）を読んでから始めた。

## 対象にしたファイル

- `TODO.md`（TODO-061 の節を消し、目次に足した差分のみ）
- `archives/todo/TODO-061. スマホの幅で、ヘッダとフッタの表示が崩れるのを直す.md`（新規）
- `archives/agents/TODO-061/README.md`（新規）
- `archives/agents/TODO-061/verifier-request.md`（新規）
- `archives/agents/TODO-061/verifier-report.md`（新規）

前例の有無は `git grep -cF <語> HEAD -- '*.md'` で数えた（作業ツリーではなく
`HEAD`）。

## 前例の無い語・少ない語

### 1. 心配なところ（前例なし）

- 出てくる場所: `verifier-request.md` の
  「`overflow-x: clip` で隣の週まで切れていないかが**心配なところ**。」
- `git grep -cF` の件数: 0 件
- 見立て: 「心配」も「ところ」もありふれた語で、組み合わせ自体は
  不自然ではない。ただしこのリポジトリでは初出。造語というより、
  普通の日本語の範囲に見えるが、判断は main に委ねる

### 2. 追従中（前例なし）

- 出てくる場所:
  - `archives/todo/TODO-061. …md`
    「**追従中**に隣の週まで切れてしまう。」
    「隣の週が、**追従中**に下で切れて見える。」
    「`hidden` だと**追従中**に下が切れる」
  - `verifier-request.md`
    「左右のスワイプで週を送れること、**追従中**に隣の週が見えること」
- `git grep -cF` の件数: 0 件（「追従」単体は 56 件あるが、「中」を
  付けた形はここが初出）
- 見立て: 「追従」＋「中」は一般的な複合の作り方で、不自然な言い回し
  には見えない。判断できないなら判断できないと書く、の原則どおり
  そのまま挙げる

### 3. 切り取る位置（前例なし）

- 出てくる場所: `README.md` の
  「分岐も挙動も変わらず、CSS の値と**切り取る位置**だけの変更のため
  （TODO-017 の基準）」
- `git grep -cF` の件数: 0 件
- 見立て: `overflow-x: clip` が「（要素を）切り取る」ことを指しての
  言い回しで、普通の日本語に見える。このリポジトリだけの言い換えとは
  断定できない

### 4. 隣週（前例 1 件）

- 出てくる場所:
  - `archives/todo/TODO-061. …md`
    「隣の週まで切れて」「隣の週が」など、この文書自体は基本的に
    「隣の週」と書いている
  - `verifier-request.md` の
    「`overflow-x: clip` で**隣週**まで切れていないかが心配なところ。」
- `git grep -cF` の件数: 1 件（`archives/agents/TODO-057/verifier-report.md`
  の「縦スクロール中のスワイプで**隣週**が上下にずれない」）
- 参考: 「隣の週」（省略しない形）は 48 件
- 見立て: 「隣の週」がこのリポジトリの通常の書き方で、「隣週」は
  TODO-057 の verifier 報告で 1 回だけ出た表記。今回の
  `verifier-request.md` がそれを踏襲した形になっている。表記ゆれに
  近く、統一するかどうかは main の判断

## 前例が既にあった語（参考、挙げるほどではない）

- 「詰まって」「間引く」: `archives/todo/TODO-061. …md` と `TODO.md` の
  両方に出るが、`TODO.md` 側の文面はこの節がまだ削除されていない時点
  （＝この差分より前）に既に入っていた文章の移設で、新規の言い回しでは
  ない
- 「生残り」（`verifier-report.md` の「`{{` `{%` の生残りなし」）は
  TODO-003 以来くり返し使われている定着語（24 件）

## 読んだファイル

- `TODO.md`（差分のみ）
- `archives/todo/TODO-061. スマホの幅で、ヘッダとフッタの表示が崩れるのを直す.md`
- `archives/agents/TODO-061/README.md`
- `archives/agents/TODO-061/verifier-request.md`
- `archives/agents/TODO-061/verifier-report.md`

## 前例なしの語数

3 語（「心配なところ」「追従中」「切り取る位置」）。前例が薄い語として
「隣週」（1 件）も併記した。
