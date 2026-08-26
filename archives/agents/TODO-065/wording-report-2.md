# TODO-065 完了コミット（9f2aa79）wording 報告 2

基準は `9f2aa79^`（= `ae5d22c`、TODO-065 が入る直前）。

## 前例の無い語

前例の件数が少ない順（0 件が並ぶものは、出てくる順）。

### bfcache
- 出てくる場所: `TODO.md:92,96`、`archives/todo/TODO-065. 編集画面に「戻る」ボタンを追加.md:78,83`、
  `archives/agents/TODO-065/verifier-report.md:53,54,59,71`
- `git grep` の件数: 0 件（前例なし）
- 見立て: ブラウザの back/forward cache を指す一般的な技術用語（略称）。
  この文書で複数回、注釈付きで説明されており、造語ではなさそう

### pageshow
- 出てくる場所: `TODO.md:93`、`archives/todo/....md:40,80`、`verifier-report.md:55,61,64`
- `git grep` の件数: 0 件（前例なし）
- 見立て: `window.pageshow` イベント名そのもの（標準 API）。一般に通用する

### event.persisted
- 出てくる場所: `TODO.md:94,98`、`archives/todo/....md:40,85`、`verifier-report.md:54,62,64`
- `git grep` の件数: 0 件（前例なし）
- 見立て: `PageTransitionEvent.persisted` という標準プロパティ名そのもの。
  一般に通用する

### 復元された文書
- 出てくる場所: `verifier-report.md:55`
  「`pageshow` が「復元された文書」に対して発火する状況を作れなかった」
- `git grep` の件数: 0 件（前例なし）
- 見立て: 判断できない。MDN 等の pageshow の説明（"document is retrieved
  from cache"）を意訳した言い回しに見えるが、このリポジトリだけの言い換え
  かどうかは分からない

### 織り込み済み
- 出てくる場所: `verifier-report.md:57`
  「再現できない可能性は織り込み済み」
- `git grep` の件数: 0 件（前例なし）
- 見立て: 一般的な日本語表現で、造語ではなさそう

### 桁の合計
- 出てくる場所: `archives/todo/....md:37`
  「空きの `col-4` を `col-2` に縮めて、桁の合計を 12 に保った」
- `git grep` の件数: 0 件（前例なし）
- 見立て: Bootstrap 由来の `col-*` グリッドの列幅の合計を指す。一般語の
  組み合わせで、このリポジトリ固有の言い換えには見えない

### 作り直されている
- 出てくる場所: `verifier-report.md:53`
  「通常の `load` として作り直されている」
- `git grep` の件数: 0 件（前例なし）
- 見立て: 普通の日本語の言い回し。造語ではなさそう

## 前例が少数ある語（参考）

- **唯一の参照**（`archives/todo/....md:44`）: 1 件
  （`HEAD:archives/todo/TODO-021. リファクタリング（挙動は変えない）.md`）
- **経路**（`verifier-report.md:39,61`）: 211 件、既に定着した語

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-065. 編集画面に「戻る」ボタンを追加.md`
- `archives/agents/TODO-065/verifier-report.md`

## 前例が無い語の数

7 語（`bfcache` / `pageshow` / `event.persisted` / `復元された文書` /
`織り込み済み` / `桁の合計` / `作り直されている`）。うち 3 語（`bfcache` /
`pageshow` / `event.persisted`）はブラウザの標準用語・API 名そのものなので、
このリポジトリ内の造語ではなく一般に通用する語と見てよい。残り 4 語は
判断できないもの・普通の日本語表現に見えるものが混じっている。
