# implementer の報告（TODO-026）

依頼書 `archives/agents/TODO-026/implementer-request.md` の「作るもの 3 つ」
を作った。文書（`CLAUDE.md`・`TODO.md`・`archives/todo/`）は触っていない。

## 作ったファイル

| パス | 要点 |
| --- | --- |
| `.claude/agents/wording.md` | 新しい担当の定義。frontmatter は依頼書のとおり（`sonnet` / `medium` / `magenta`）。本文は「対象は `.md` 全部（報告ファイルを含む）」「語を拾うのは LLM、`git grep` は前例の有無だけ」「既知語リストを持たない」「文書は直さない」「前例なし ＝ 造語ではない」「ゼロは狙わない」「語数が目印（15 語 対 1〜3 語）」。決まりごとの節は `reviewer.md` の末尾に揃えた |
| `.claude/hooks/check-md-commit.sh` | `git commit` に `.md` が入っていれば促すだけの hook。実行権限あり（`755`）。判断はしない。どんな場合も `exit 0` |
| `.claude/settings.json` | hook の設定（新規）。依頼書の内容そのまま。`settings.local.json` は触っていない |

`archives/agents/TODO-026/implementer-report.md`（このファイル）以外に、
既存ファイルの変更・削除は無い。`git status --short` で確認済み。

## hook の作りで、依頼書に無いことを決めた点

### 1. `git diff` に `-z` を付けた（**これは必須だった**）

依頼書は `git diff --cached --name-only` と書いてあるが、そのままだと
**このリポジトリの日本語ファイル名が化ける**。実測:

```
$ git diff --cached --name-only -- '*.md'
"archives/todo/TODO-025. \346\226\207\346\233\270\343\201\256\347\242\272...md"

$ git diff --cached --name-only -z -- '*.md' | tr '\0' '\n'
archives/todo/TODO-025. 文書の確認を分ける仕組みを決める.md
```

`archives/todo/` のファイル名はすべて日本語なので、`-z` が無いと促す
メッセージがほぼ読めなくなる。`-z` にして `tr '\0' '\n'` で改行区切りへ
戻している（`core.quotePath=false` では、引用符や空白を含む名前は
やはりエスケープされるので `-z` を採った）。

**副作用**: ファイル名に改行が入っていると行として崩れる。実害は
「メッセージの見た目が乱れる」だけで、止めることはない。このリポジトリに
そんな名前は無いので、そこまでは対処していない。

### 2. 一覧は 20 件で打ち切る（`MAX_LIST=20`）

`systemMessage` は 10,000 字までという上限がある（下記の文書で確認）。
文書だけのコミットで `.md` が数十個入ることは普通にあるので
（`95895c1` で 12 個）、20 件を超えたら `（ほか N 件）` と出すようにした。
促すのが目的で、全件を読ませる必要は無いと判断した。

### 3. `git commit` かどうかの見分け方

```
grep -Eq '(^|[;&|(]|&&)[[:space:]]*git[^;&|]*[[:space:]]commit([[:space:]]|$)'
```

同じコマンド区切りの中で `git` のあとに `commit` が来る形だけを見る。

- 拾う: `git commit -m "x"` / `git -C /path commit` / `cd /tmp && git commit`
- 拾わない: `git status` / `ls -l` / `git log --oneline | grep commit`
  / `git log --grep=commit`
- **拾ってしまう**: `git log --grep commit`（`=` ではなく空白で書いた形）

最後のものは誤検出になるが、**hook は止めないので実害はメッセージが
1 回余分に出るだけ**。逆に見落とすと促せない。止めない hook なので
「拾いすぎる側」に倒した。

### 4. `-a` / `--all` の見分け方

```
grep -Eq '(^|[[:space:]])(--all|-[[:alnum:]]*a[[:alnum:]]*)([[:space:]]|$)'
```

`-a` / `-am` / `--all` を拾い、`--amend` は拾わない（実測で確認済み）。
コミットメッセージの中に ` -a ` のような文字列があると誤検出するが、
そのときは「ステージしていない `.md` も一覧に混ざる」だけで止まらない。

### 5. `jq` が無ければ何もしない

依頼書に「JSON の組み立ては `jq -n --arg` を使う」とあるので、
`jq` が無い環境では文字列を自分で連結せず、そのまま `exit 0` にした。

## hook の出力仕様を確認し直した

`https://code.claude.com/docs/en/hooks` を 2026-08-21 に読んだ。依頼書と
違っていた点が 1 つある。

- **`if` は正しいフィールドだった。** `hooks[]` の中に書ける任意フィールドで、
  値は permission rule の書き方（`"Bash(rm *)"` など）。依頼書は「効くか
  確信が持てない」としていたが、少なくとも**設定として無効ではない**ので、
  `settings.json` ごと弾かれる心配は無い。実際に絞り込めているかは
  `verifier` に見てもらう必要がある（スクリプト側でも `git commit` かを
  見ているので、`if` が効かなくても動く）
- **`permissionDecision` の値は `"allow"` / `"deny"` / `"escalate"`** で、
  依頼書にある `"ask"` は現在の文書には無い。**どれも使っていない**ので
  実装には影響しない
- `systemMessage` / `additionalContext` はどちらもトップレベルのフィールドで、
  上限は 10,000 字。`permissionDecision` のほうは `hookSpecificOutput` の
  中に入れる。今回はトップレベルの 2 つだけを出しているので、
  **コミットが止まる経路は無い**

## 自分で確かめたこと

一時ディレクトリ（scratchpad）に使い捨てのリポジトリを作って試した。
**本物のコミットは作っていない。** `~/ytsched/data` は触っていない。

### 使い捨てリポジトリでの単体の確認

| 入力 | 結果 |
| --- | --- |
| `git commit -m "docs"`、`.md` 2 個ステージ済み | JSON 出力、`exit 0`。一覧に 2 個 |
| `.md` なし（`a.py` だけ） | 出力なし、`exit 0` |
| `git status` / `ls -l` | 出力なし、`exit 0` |
| `git log --oneline \| grep commit` | 出力なし、`exit 0` |
| `git log --grep=commit` | 出力なし、`exit 0` |
| 追跡済み `.md` を未ステージで変更＋`git commit -m` | 出力なし（正しい） |
| 同上＋`git commit -a -m` / `-am` / `--all` | 拾う（正しい） |
| `git commit --amend --no-edit`（ステージ無し） | 出力なし（`-a` と誤認しない） |
| 空の stdin / `not json` / `{}` | 出力なし、`exit 0` |
| リポジトリの外（`CLAUDE_PROJECT_DIR` が非リポジトリ、未設定＋cwd も外） | 出力なし、`exit 0` |
| `.md` 27 個 | 20 個＋`（ほか 7 件）` |
| ファイル名 `a "b" c.md`（引用符・空白入り） | そのまま正しく出る |
| 日本語ファイル名 | そのまま正しく出る |

**出た JSON はすべて `jq -e .` に通した（valid）。**
`bash -n` OK。`shellcheck` も指摘なし。
`.claude/settings.json` も `jq -e .` で valid を確認。

### 実物に近い形での確認（`95895c1` の再現）

ytsched を scratchpad へ clone し、`95895c1^` の上に `95895c1` の `.md`
12 個をステージした状態を作って hook にかけた。**12 個すべてが一覧に
出た**（`archives/todo/TODO-021. リファクタリング（挙動は変えない）.md`
の日本語名も正しく表示。「足場」が入っていた
`implementer1-report.md` と `reviewer-report.md` も入っている）。

### `wording.md` に書いた `git grep` の形

定義に書く前に実際に叩いて確かめた。

```sh
$ git grep -cF 足場 HEAD -- '*.md'
HEAD:TODO.md:2
HEAD:archives/agents/TODO-021/implementer1-report.md:3
...
$ git grep -cF 足場 95895c1^ -- '*.md'   # 終了ステータス 1、出力なし＝前例なし
```

- 一致なしは「出力なし＋終了ステータス 1」。`set -e` の下では `|| true` が
  要るので、その注意を定義に書いた
- `-F` を足した（依頼書には無い）。語に `.` などが入ったとき、正規表現と
  して解釈されて誤って一致するのを防ぐため
- 合計件数は `| awk -F: '{s+=$NF} END{print s+0}'` で取れることも確認して
  定義に書いた

**注意（`verifier` 向け）**: 「足場」は TODO-021・TODO-025 の archive が
既にコミットされているので、**いま `HEAD` を基準にすると前例 14 件で
挙がらない**。効き目を試すときは `95895c1^` を基準にすること
（そこでは 0 件になるのを確認済み）。

## 単独で決めた判断のまとめ

1. `git diff` に `-z` を付けた（日本語ファイル名が化けるため。必須）
2. 一覧を 20 件で打ち切る（`systemMessage` の 10,000 字制限のため）
3. `git commit` の判定は「拾いすぎる側」に倒す（止めない hook なので、
   見落とすほうが困る）
4. `jq` が無ければ何もしない（手で JSON を組み立てない）
5. `wording.md` の `git grep` に `-F` を足した

## 気づいたが直さずに残したもの

- **TODO-026 の「既存 5 個の定義を整理して、増えたぶんを吸収できるか見る」
  （`runner` を `verifier` に畳めるか）には手を付けていない。** 依頼書の
  「作るもの 3 つ」に入っていないため。定義は 6 個になっている。
  畳むかどうかは main の判断
- **TODO-026 の「『足場』が入ったコミットで、実際に挙がるか試す」も
  やっていない。** hook が `95895c1` の `.md` 12 個を拾うところまでは
  確かめたが、`wording` 担当を実際に立てて 15 語が挙がるかは試していない
  （担当を起動するのは main の役目）
- `.claude/RESUME.md` と `.claude/settings.local.json` は触っていない
- `wording.md` の `description` 行が 78 字を超えている（92 字）。既存 5 個の
  定義も同じなので揃えたまま。frontmatter は折り返せない

## うまくいかなかったところ

- 最初 `git diff --cached --name-only`（`-z` なし）で書いてしまい、
  日本語ファイル名が `\346\226\207...` に化けた。テストで気づいて `-z` に
  直した
- `if` フィールドが実際に絞り込みとして働くかは、hook を起動させて
  みないと分からない。文書上は有効なフィールドだと確認できたが、
  **実際の発火は `verifier` に確かめてもらう必要がある**
  （Claude Code は起動時にしか設定を読まないので、`settings.json` を
  効かせるには**利用者による再起動**が要る）
