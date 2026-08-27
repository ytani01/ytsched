# TODO-083 wording 報告

対象は依頼にあった 13 ファイル（`runner-report.md` は存在したので含めた）。
候補は前例の件数が少ない順。

## 前例なし

### 1. `global lexical scope`
- `archives/todo/TODO-083. my.js と main.html の JavaScript を分ける.md`
  「素の `<script>` 同士は global lexical scope を共有するので」
- `git grep -cF "global lexical scope" HEAD -- '*.md'` → 前例なし
- 見立て: JavaScript の一般的な専門用語で、英語のまま書くのは
  `CLAUDE.md` の「専門用語は無理に和訳しない」に沿う。造語ではなく、
  このリポジトリでの初出と見る

### 2. `ES モジュール`
- 同上ファイル「ES モジュールにはしない」の節見出し、implementer-request
  にも同語
- `git grep -cF "ES モジュール" HEAD -- '*.md'` → 前例なし
- 見立て: `type="module"` の一般名。専門用語として妥当、造語ではない

### 3. 名前空間オブジェクト
- 同上ファイル「選ばれたのは名前空間オブジェクト」
- `git grep -cF "名前空間オブジェクト" HEAD -- '*.md'` → 前例なし
- 見立て: 3 案（要素はその都度取る／名前空間オブジェクト／最小変更）の
  1 つの呼び名。一般的な設計用語で、このリポジトリでは初出

### 4. `ytState`
- 複数ファイルに頻出（識別子そのもの）
- `git grep -cF "ytState" HEAD -- '*.md'` → 前例なし
- 見立て: 造語ではなくコード上の変数名。用語というより固有名なので、
  「前例の無い語」に数えるべきか判断できない。念のため挙げる

### 5. `ブラウザ側のスクリプト`
- `src/README.md` の新しい節見出し
- `git grep -cF "ブラウザ側のスクリプト" HEAD -- '*.md'` → 前例なし
  （近い言い回し「ブラウザ側の」は TODO-049 に 1 件あり）
- 見立て: 普通の言い方で、造語には見えない

### 6. 静かに壊れる
- `archives/agents/TODO-083/README.md`
  「どれか 1 本でも 404 なら静かに壊れる」、
  `archives/todo/TODO-083. ....md` の「分かったこと」にも同じ言い回し
- `git grep -cF "静かに壊れる" HEAD -- '*.md'` → 前例なし
- 見立て: "fail silently" の意訳。比喩だが自然な日本語で、
  このリポジトリだけの言い換えというほどではないと思う

### 7. 宣言一覧
- `verifier-report.md`「宣言一覧（`function`/`const`/`let`）の差分は」
- `git grep -cF "宣言一覧" HEAD -- '*.md'` → 前例なし
- 見立て: 普通の複合語。造語というより単なる言い回し

### 8. 誤ったコメント
- `implementer-report.md`「削除したファイルを指す誤ったコメントを
  残すのは避けた」
- `git grep -cF "誤ったコメント" HEAD -- '*.md'` → 前例なし
- 見立て: ごく普通の表現。問題なさそう

### 9. 退行の受け皿になった
- `archives/todo/TODO-083. ....md`「TODO-056 で入れたブラウザのテストが、
  そのまま退行の受け皿になった」
- `git grep -cF "退行の受け皿になった" HEAD -- '*.md'` → 前例なし
  （構成要素の「退行」は前例多数、「受け皿」は前例 2 件、
  組み合わせでの完全一致は無し）
- 見立て: 比喩としては分かりやすいが、「退行の受け皿」という組み合わせは
  このリポジトリで初出。造語というほどではないが、比喩表現なので
  一応挙げる

### 10. 一望
- `archives/todo/TODO-083. ....md`「どこから書き換えられるかを
  `ytState` で grep すれば一望できる」
- `git grep -cF "一望" HEAD -- '*.md'` → 前例なし
- 見立て: 普通の日本語。問題なさそう

## 前例が少数だけあったもの（参考。造語ではなさそうだが目に付いた）

- **受け皿**（2 件: TODO-020 reviewer-report、TODO-038 タイトル）
  — TODO-083 archive の「退行の受け皿になった」の一部
- **線引き**（5 件） — README.md「`ytState` に入れるものの線引き」など、
  既存の使い方の延長で問題なさそうに見える

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-083. my.js と main.html の JavaScript を分ける.md`
- `archives/agents/TODO-083/README.md`
- `archives/agents/TODO-083/implementer-request.md`
- `archives/agents/TODO-083/implementer-report.md`
- `archives/agents/TODO-083/verifier-request.md`
- `archives/agents/TODO-083/verifier-report.md`
- `archives/agents/TODO-083/reviewer-request.md`
- `archives/agents/TODO-083/reviewer-report.md`
- `archives/agents/TODO-083/runner-report.md`
- `src/README.md`（差分のみ）
- `docs/Developer.md`（差分のみ）
- `tests/README.md`（差分のみ）

前例なしの語数: **10 語**（このほか、既存語の組み合わせとして
1 語「退行の受け皿」を注記）。
