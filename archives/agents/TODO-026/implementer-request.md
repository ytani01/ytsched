# implementer への依頼（TODO-026）

`~/work/ytsched/TODO.md` の TODO-026 と、
`archives/todo/TODO-025. 文書の確認を分ける仕組みを決める.md` の
「決めたこと」を**先に読むこと**。作るものはそこで決まっている。

作るのは次の 3 つ。**文書（CLAUDE.md・TODO.md・archives）は main が書く
ので触らない。**

---

## 1. `.claude/agents/wording.md`

新しい担当の定義。frontmatter は既存 5 個（`implementer.md` など）に
揃える。

```yaml
name: wording
description: コミットに入る .md から、このリポジトリに前例の無い語を挙げる。文書は直さない。main（管理者）から名指しで依頼されたときだけ使う。自動では起動しない。
tools: Read, Write, Bash, Grep, Glob
model: sonnet
effort: medium
color: magenta
```

本文に書くこと（TODO-025 の「決めたこと」がそのまま元になる）。

- **役割** — そのコミットに入る `.md` に出てくる呼び名を拾い、
  `git grep` で前例の有無を見て、**前例の無い語を全部挙げる**
- **対象は、そのコミットに入る `.md` 全部。** 依頼書・archives・
  `CLAUDE.md`・README に加えて、**担当の報告ファイルも含める**
  （TODO-021 で「足場」が入っていたのが報告ファイルだったので、
  外すと今回の例を見逃す）
- **文書は直さない。** 挙げるだけ。直すかどうかは main が判断する。
  書き込んでよいのは自分の報告ファイルだけ（`reviewer` と同じ形）
- **既知語リストは持たない。** 一度指摘された語しか止まらず、次の
  造語が素通りするため
- **語を拾うのは自分（LLM）が読んでやる。** `git grep` は前例の有無を
  答えるだけに使う。正規表現で語を切ると「件追記」「全部通」のような
  切れ端が混ざることが TODO-025 で実測されている
- **前例なし ＝ 造語ではない。** 一般に通用する専門用語でも、この
  リポジトリでは初出になる（TODO-025 の時点で「ゴールデンマスター」も
  前例 1 件しかなかった）。**一般に通用しそうかの見立ては添えるが、
  決めるのは main**
- **ゼロは狙わない。** 前例の無い語を挙げるところまでが仕事で、
  見落としは残る
- **目安** — TODO-025 の実測では、造語が入った文書で前例なしが 15 語、
  造語を作っていない文書では 1〜3 語だった。**語数そのものが目印になる**
- 報告の書き方 — 語ごとに、その語・出てくるファイルと箇所・`git grep`
  の件数・見立て（一般に通用しそうか）
- 決まりごとの節は既存の定義（`reviewer.md` の末尾）に揃える。
  報告は `archives/agents/TODO-NNN/wording-report.md`、返事は 5 行以内

**前例を見るコマンドの形も定義に書いておくこと。** 基準は「その文書が
入る前」なので、`git grep -c <語> HEAD` の形になる（作業ツリーではなく
`HEAD`。まだコミットされていない文書自身を数えてしまわないため）。
実際に何度か叩いて、意図どおり動く形になっているか確かめてから書く。

---

## 2. `.claude/hooks/check-md-commit.sh`

`git commit` を捕まえて、`.md` が入っていれば促すだけの hook。
**判断させない**（`.md` が入っているかどうかだけを見る）。

仕様:

- stdin に JSON が来る。`.tool_input.command` にコマンド文字列が入る
- `git commit` でなければ何も出さずに `exit 0`
- ステージされた `.md` を `git diff --cached --name-only` で拾う。
  **`-a` / `--all` が付いているときは `git diff --name-only HEAD` も
  見る**（`-a` だとステージしていない変更も入るため）
- `.md` が 1 つも無ければ何も出さずに `exit 0`
- `.md` があるときだけ、**exit 0 で** 次の形の JSON を stdout に出す。
  **`permissionDecision` は返さない**（返すとコミットが止まる）

```json
{
  "systemMessage": "…画面に出る文言…",
  "additionalContext": "…Claude に届く文言…"
}
```

`systemMessage` にはファイル名の一覧と「確認の担当（wording）を
立てたか」を入れる。`additionalContext` も同じ趣旨でよい。

hook の出力仕様（2026-08-21 に
`https://code.claude.com/docs/en/hooks` で確認した）:

- exit 0 で stdout が `{` で始まれば JSON として読まれる
- `systemMessage` は transcript にシステムメッセージとして出る
- `additionalContext` は Claude の文脈に足される
- `permissionDecision` が `"ask"` なら確認ダイアログで止まる、
  `"deny"` と exit 2 はブロックする。**どれも使わない**
- 素の stdout / stderr は debug log にしか出ない。**必ず JSON で出す**

書き方の注意:

- `jq` は入っている（`/usr/bin/jq`、1.8.2）。使ってよい
- **JSON の組み立ては `jq -n --arg` を使う。** 文字列を自分で連結すると
  ファイル名に引用符や改行が入ったときに壊れる
- **どんな場合も `exit 0` で終わる。** `git` が失敗しても、リポジトリの
  外で呼ばれても、hook のせいでコミットが止まらないようにする
  （`set -e` を使うならその点に気をつける）
- 実行権限を付ける（`chmod +x`）
- リポジトリのルートは `$CLAUDE_PROJECT_DIR` を使う

---

## 3. `.claude/settings.json`（新規）

hook の設定を置く。**`.claude/settings.local.json` は git 管理外なので
触らない。**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git commit *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-md-commit.sh"
          }
        ]
      }
    ]
  }
}
```

`if` が効くかどうかは確信が持てない。**効かない場合に備えて、
スクリプト側でも `git commit` かどうかを見ること**（上の仕様に入れてある）。

---

## 自分で確かめること

- スクリプトに JSON を食わせて、`.md` あり／なしの両方で出力を見る。
  **一時ディレクトリに使い捨てのリポジトリを作って試す。本物のコミットは
  作らない**
- `jq . ` に通して、出た JSON が壊れていないこと
- 最終的な確認は `verifier` が別に行うが、自分で確かめたことも報告に書く

## 気をつけること

- **`.claude/settings.local.json` を書き換えない**
- **`TODO.md`・`CLAUDE.md`・`archives/todo/` を書き換えない**（main が書く）
- **git commit / git tag はしない**
- 報告は `archives/agents/TODO-026/implementer-report.md`
