# reviewer の報告（TODO-026）

見たもの: `.claude/agents/wording.md`、`.claude/hooks/check-md-commit.sh`、
`.claude/settings.json`（いずれも untracked なので直接読んだ）。
`implementer-request.md`・`implementer-report.md`・TODO-025 の「決めたこと」と
突き合わせた。

正規表現と `git` の挙動は、使い捨てのリポジトリ（scratchpad）と、
ytsched の履歴（`95895c1`）で実際に確かめた。**本物のコミットは作っていない。
ファイルは 1 つも直していない。**

---

## 確信度の高い指摘

### 1. `settings.json` の `if` が、効いた場合にいちばん多い形の `git commit` を弾く

`.claude/settings.json:9`

```json
"if": "Bash(git commit *)"
```

`if` の値は permission rule の書き方だと implementer が確認している。
permission rule の Bash マッチは**コマンド文字列の前方一致**で、しかも
`&&` などのシェル演算子を意識して、**前置きが付いた形は同じ rule に
当てはめない**という決まりになっている。すると:

| コマンド | スクリプト側の判定 | `if` が効いた場合 |
| --- | --- | --- |
| `git commit -m "x"` | 拾う | たぶん通る |
| `git add -A && git commit -m "x"` | 拾う | **通らない** |
| `cd /tmp && git commit` | 拾う | **通らない** |

**このリポジトリで実際に使われているのは 2 番目の形**（`git add` してから
`git commit`）。スクリプト側は `(^|[;&|(]|&&)` で `&&` を丁寧に扱っている
のに、その手前の `if` で落ちると、**hook は黙って発火しない**。
依頼書が reviewer に見てほしいと書いた経路そのもの。

さらに、permission rule の前方一致の書き方は `Bash(git commit:*)`
（コロン）で、`Bash(git commit *)`（空白＋`*`）は文書にある 2 形式
（完全一致・`:*` の前方一致）のどちらでもない。完全一致として扱われると
**どんなコマンドでも通らない**（＝ hook が一度も発火しない）。

`if` が単に未知フィールドとして無視されるなら実害は無いが、その場合は
書いてある意味も無い。**スクリプトが自前で `git commit` を判定している
ので `if` は冗長**であり、外すのがいちばん安全。

implementer が確かめたのは「設定として無効ではない」ところまでで、
**`if` を通って実際に発火するかは誰も試していない**。verifier に試させる
なら、`git add -A && git commit --dry-run` のような形を必ず入れること。
外すかどうかは main の判断。

### 2. `wording.md` の対象ファイル収集コマンドに `-z` が無い（hook 側と非対称）

`.claude/agents/wording.md:37-40`

```sh
git diff --cached --name-only -- '*.md'   # ステージ済み
git diff --name-only HEAD -- '*.md'       # -a でコミットするとき
```

implementer は hook 側で「`-z` が無いと日本語ファイル名が化ける。必須」と
判断して直したのに、**同じ問題が定義ファイル側に残っている**。実測:

```
$ git diff --name-only 95895c1^ 95895c1 -- '*.md' | tail -1
"archives/todo/TODO-021. \343\203\252\343\203\225\343\202\241...md"
```

`archives/todo/` のファイル名は全部日本語なので、`wording` はこの形の
パスを受け取る。担当（LLM）はそのまま Read しようとして失敗するか、
八進エスケープを自分で復元することになる。**読むファイルを取り違えたり
落としたりする経路**で、しかも静かに起きる。

同じ定義の 73 行では `git grep` にだけ `core.quotePath=false` を書いていて、
非対称になっている。`git grep` に要ると気づいた注意が `git diff` に
付いていない。

### 3. `git commit <パス>` でコミットすると、`.md` が入っていても黙って通る

`.claude/hooks/check-md-commit.sh:35-44`

pathspec を付けた `git commit` は、**ステージの有無に関わらず**指定した
パスをコミットする。実測（使い捨てリポジトリ）:

```
a.md を変更（ステージしない）
入力: {"tool_input":{"command":"git commit -m x a.md"}}
→ 出力なし、exit 0
```

`git commit` 自体は正しく拾えているのに、`--cached` にも（`-a` が無いので）
`git diff HEAD` にも当たらず、`.md` が 0 個と判定される。
`git commit -m "docs(todo): …" TODO.md` は main が使いうる形。

止めない hook なので害は「促されない」だけだが、**促すのが唯一の仕事**の
hook なので、見落とす側の穴になる。

### 4. 前置きの付いた `git commit` を拾わない

同 `:26` の正規表現は `(^|[;&|(]|&&)[[:space:]]*git` で、区切りの直後が
`git` でないと当たらない。実測で miss になったもの:

```
sudo git commit / env FOO=1 git commit / timeout 60 git commit
command git commit / /usr/bin/git commit -m x
```

このリポジトリでどれも使っていないので優先度は低い。**3 と合わせて、
「見落とす経路がここまで」と分かっていれば十分**という性格の指摘。

---

## 仕様との突き合わせ（逸脱は無し）

TODO-025 の「決めたこと」3 点は、いずれも `wording.md` に入っている。

| 決めたこと | 場所 | 判定 |
| --- | --- | --- |
| 既知語リストは持たない | `:21-22` | OK |
| 文書は直さない（挙げるだけ） | `:19` | OK |
| 対象は報告ファイルを含む `.md` 全部 | `:28-33` | OK。TODO-021 の実例まで書いてある |

frontmatter は既存 5 個と揃っている（`name`/`description`/`tools`/`model`/
`effort`/`color` の順、`description` 末尾の「名指しで依頼されたときだけ／
自動では起動しない」も同じ）。`tools` に `Edit` が無いのは `reviewer` と
同じで、「直さない」担当として正しい。決まりごとの節も `reviewer.md` の
末尾と一致している。

**役割の線引きの衝突も無い。** `reviewer` はコード、`writer` は文書を
**書く**側、`wording` は文書の語彙を**見る**側で、重なっていない。
`writer.md` に既にある「造語を使わない」は書き手への指示で、TODO-025 が
「書いてあっても止まらなかった」と結論した相手そのものなので、
別の担当を立てる根拠と矛盾しない。

## 「誤って止める」経路（無し）

- 出力は `systemMessage` / `additionalContext` のトップレベル 2 つだけ。
  `permissionDecision` も `hookSpecificOutput` も出していない
- `exit 2` する経路が無い。`set -e` / `set -o pipefail` を使っていない
  （使わないと明記してある。この用途では正しい）
- 終了は全経路が `exit 0`。`[ "$count" -gt … ]` が失敗しても続行する
- stdout に JSON 以外が混じる経路が見当たらない。`command -v` は
  `>/dev/null`、`git` は全部コマンド置換か `2>/dev/null`、`jq -n` も
  `2>/dev/null`。`[` のエラーは stderr
- 出た JSON は `jq -e .` で valid。日本語も改行も `--arg` が正しく
  エスケープしている（`cat -A` で確認）

## implementer が単独で決めた 5 点（すべて妥当）

1. **`-z` を付けた** — 妥当というより必須。ただし上の指摘 2 のとおり、
   同じ直しが `wording.md` に入っていない
2. **`MAX_LIST=20`** — 妥当。促すのが目的で全件を読ませる必要は無い
3. **`git commit` の判定を「拾いすぎる側」に倒した** — 妥当。止めない
   hook なので、`git log --grep commit` を拾ってメッセージが 1 回余分に
   出るのと、コミットを促し損ねるのとでは、後者のほうが困る。同じ理由で
   `.md` を**削除するだけ**のコミットでも促す（実測）が、これも許容範囲
4. **`jq` が無ければ何もしない** — 妥当。手で JSON を組み立てるほうが
   はるかに危ない
5. **`git grep` に `-F` を足した** — 妥当。日本語の語でも、`.` や `*` を
   含む語（`ToDo.jsonl` など）を数えるときに効く

## 既にあるものの再実装（無し）

- `-z` ＋ `tr '\0' '\n'` は、`core.quotePath=false` では空白・引用符入りの
  名前がやはりクォートされるので、必要な処理。実測でも
  `a "b" c.md` が正しく出ている
- `sed '/^[[:space:]]*$/d' | sort -u` も素直
- `git commit` の判定をシェルで自前に書いている点は、指摘 1 のとおり
  `if` が信用できないので、**むしろ自前が正しい**

---

## 以下は確信度が低い

- **`systemMessage` の文言が断定的**（`:58`）。「このコミットには .md が
  N 個入っている」と言い切るが、`-a` の判定は誤検出しうる
  （`git commit -m "fix -a flag"` が HIT するのを実測）。そのとき N は
  実際にコミットされる数より多くなる。「入っている（見込み）」くらいに
  ゆるめる余地はあるが、促すだけの文なので実害は小さい
- **`wording.md:97` の「10 語を超えたら疑ってよい」** が、「前例の無い語を
  全部挙げる」と読み手の中で競合しないか。直後に「自信が無いという理由で
  語を落とさない」と念押しがあるので、たぶん大丈夫だと思う
- **`git grep -cF <語> HEAD -- '*.md'`（`:62`）が前例を `.md` に限っている。**
  `src/` のコメントや docstring にある語が「前例なし」として挙がる。
  挙げすぎる方向なので害は小さく、文書の語彙を見る担当としては妥当かも
  しれない
- **`matcher: "Bash"`** が部分一致だと `BashOutput` にも当たりうるが、
  当たっても `.tool_input.command` が無くて `exit 0` なので害は無い

## 範囲外だが気づいたこと（直していない）

- TODO-026 のチェック項目「既存 5 個の定義を整理して、増えたぶんを
  吸収できるか見る」（`runner` を `verifier` に畳めるか）は手つかずで、
  定義は 6 個になっている。implementer も報告済み。main の判断
- `.claude/settings.json` は `.gitignore` に当たっていない（`git check-ignore`
  で確認）。追跡されるべきファイルなので、これは意図どおり
