# TODO-098 wording 報告

このコミットに入る `.md` を読み、リポジトリに前例の無い語を挙げた。
文書は直していない。件数は `git grep -cF <語> HEAD -- '*.md'` の合計。
判断は main。

## 読んだファイル

- `docs/Developer.md`（HEAD からの差分。追加行が主対象）
- `TODO.md`（TODO-098 の節を削除する差分）
- `archives/agents/TODO-098/README.md`
- `archives/agents/TODO-098/implementer-task.md`
- `archives/agents/TODO-098/implementer-report.md`
- `archives/agents/TODO-098/verifier-task.md`
- `archives/agents/TODO-098/verifier-report.md`
- `archives/agents/TODO-098/wording-task.md`
- `archives/todo/TODO-098. JavaScript のリンター（ESLint）を導入する.md`

`Developer.md` の追加行と `TODO.md` の差分には、前例の無い語は無かった
（`ESLint` / `Node.js` / `npm` / `npm ci` / `npx` は一般語。`実行環境` は
HEAD で 5 件、同じ表の Python 3.14 の行でも使われている）。

## 前例の無い語（件数の少ない順）

### 1. 自動ページめくり／ページめくり — 前例なし

- `archives/agents/TODO-098/verifier-report.md:43`
  「自動ページめくりのタイミング依存テストのフレークで」
- `git grep`: `ページめくり` 0 件、`めくり` 0 件
- 見立て: **このリポジトリだけの言い換え。** 同じ機能を既存の文書は
  `自動ページ送り` と呼んでいる（`自動ページ` は HEAD で 39 件、
  README・TODO-084 ほか）。造語というより既存語との不一致。

### 2. 層を重ねる — 前例なし

- `archives/todo/TODO-098. ….md:46`
  「`files` を … に限定し、`no-undef` / `no-unused-vars` を `off` に
  した層を重ねる」
- `git grep`: `層を重ね` 0 件（`層` 単体は 5 件だが別の意味）
- 見立て: ESLint flat config の配列要素を「層」と呼ぶ言い回し。
  一般的な用語ではなく、このリポジトリでも初出。判断は main。

### 3. 依存グラフ — 前例なし

- `archives/agents/TODO-098/verifier-task.md:25`
  「タスクの依存グラフが変わったので 1 回だけ通す」
- `git grep`: 0 件
- 見立て: 一般に通用する用語（dependency graph）。ただしこのリポジトリの
  他の文書は mise タスクの依存を `depends` や「依存する」と素の語で
  書いており、初出。

### 4. 依存の連鎖 — 前例なし

- `archives/agents/TODO-098/verifier-task.md:23`
  「`lint` → `test` の依存の連鎖が `lintjs` 追加後も通ること」
- `git grep`: 0 件
- 見立て: 「依存」は多数の前例あり。「連鎖」を付けた言い回しが初出。
  意味は通るが、素の「依存」で足りるところ。判断は main。

### 5. グローバル共有 — 前例なし

- `archives/agents/TODO-098/implementer-task.md:60`（`eslint.config.js`
  に入れるコメント案）「ファイルをまたぐグローバル共有は今の作り」
- `git grep`: 0 件（`グローバル` 単体は 21 件）
- 見立て: 「グローバル変数／関数をファイルをまたいで共有する」を
  名詞句に縮めたもの。造語寄り。なお実際にコミットされる
  `eslint.config.js` のコメント文面は wording の対象外（`.js`）だが、
  依頼書に候補として残っている。

### 6. グローバル関数 — 前例なし

- `archives/agents/TODO-098/implementer-report.md:17`、
  `implementer-task.md:15`、`archives/todo/TODO-098. ….md:25`
- `git grep`: 0 件（`グローバル` は 21 件）
- 見立て: 素直な複合語（global function）で一般に通じる。初出ではあるが
  問題は無いと思う。

### 7. 最小構成 — 前例なし

- `archives/agents/TODO-098/README.md:28`、`implementer-task.md:18`、
  `archives/todo/TODO-098. ….md:30`
- `git grep`: 0 件（`最小限` は 6 件）
- 見立て: 一般に通用する言い方（minimal configuration）。造語ではないと
  思うが、`最小限` で書いている前例はある。

### 8. 今の構成／構成そのもの — 前例なし（「今の構成」名義）

- `archives/agents/TODO-098/implementer-report.md:17`、
  `wording-task.md:22`、`archives/todo/TODO-098. ….md:27`
  （「今の構成そのもの」）
- `git grep`: `今の構成` 0 件。`今の作り` は 3 件、`構成そのもの` は 1 件
- 見立て: 一般語。ただし同じ意味で `今の作り` という前例があり、揺れて
  いる。判断は main。

### 9. tooling — 前例なし

- `archives/agents/TODO-098/implementer-task.md:27`、
  `archives/todo/TODO-098. ….md:39`（「tooling 専用」）
- `git grep`: 0 件
- 見立て: 英語をそのまま使った語。このリポジトリの他の文書は「ツール」と
  カタカナで書いている。和訳の要否は main。

### 10. キャレット指定／キャレット — 前例なし

- `archives/agents/TODO-098/implementer-task.md:32`
  「いずれも最新のキャレット指定でよい」
- `git grep`: 0 件
- 見立て: npm のバージョン指定子 `^` を「キャレット」と呼ぶ言い方。
  npm を知っていれば通じるが、このリポジトリでは初出。判断できないので
  そのまま挙げる。

### 11. 追跡変更 — 前例なし

- `archives/agents/TODO-098/verifier-report.md:39, 42`
  「追跡変更（`.gitignore` / … / `mise.toml`）を stash した」
- `git grep`: 0 件（`追跡対象` は 2 件）
- 見立て: git の tracked changes を名詞句に縮めたもの。`追跡対象` の
  前例に近いが、この形は初出。判断は main。

### 12. 顕在化 — 前例なし

- `archives/agents/TODO-098/verifier-report.md:44`
  「本項目の作業中に顕在化したので報告する」
- `git grep`: 0 件
- 見立て: 一般的な日本語。造語ではない。

## まとめ

- 前例の無い語: **12 語**（1〜12）。
- うち、既存文書との不一致がはっきりしているのは **1.（自動ページめくり
  ／ページめくり）**。既存は `自動ページ送り`。
- 言い回しとして造語寄りなのは 2.（層を重ねる）、5.（グローバル共有）、
  4.（依存の連鎖）、11.（追跡変更）あたり。
- 6.・7.・12. は一般語で、問題は無いと思う。
- 語数の多い文書は `verifier-report.md`（1・3・4 相当の元 … 実際は
  1・11・12＝3 語）と `implementer-task.md`（5・6・9・10＝4 語）。
  いずれも 10 語未満で、TODO-025 の「造語の入った報告 15 語」の水準では
  ない。
- 判断が要る点: 1. を `自動ページ送り` に揃えるか、2.〜11. の言い回しを
  素の語に直すか。直すかどうかは main。
