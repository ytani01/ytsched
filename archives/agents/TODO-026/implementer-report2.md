# implementer の報告 その 2（TODO-026・reviewer の指摘 1・2・3 を直した）

依頼書 `archives/agents/TODO-026/implementer-request2.md` のとおり、
指摘 1・2・3 を直した。**指摘 4 は直していない**（見送りの指示どおり）。

触ったのは指示された 3 ファイルだけ。`TODO.md`・`CLAUDE.md`・
`archives/todo/`・`.claude/settings.local.json` は触っていない。
`git status --short` で確認済み（`.claude/agents/wording.md`、
`.claude/hooks/`、`.claude/settings.json`、`archives/agents/TODO-026/` の
4 つが untracked のまま。新しく増えたファイルは無い）。

## 1. `settings.json` から `if` を外した

`"if": "Bash(git commit *)"` の行を消して `matcher: "Bash"` だけにした。
`jq -e .` で valid を確認。`git commit` の判定はスクリプト側だけが持つ形に
なった。

## 2. `wording.md` の `git diff` に `-z` を付けた

対象ファイル収集の節を、hook 側と同じ形に揃えた。

```sh
git diff --cached --name-only -z -- '*.md' | tr '\0' '\n'
git diff --name-only -z HEAD -- '*.md' | tr '\0' '\n'
```

**書く前に、clone した ytsched で 2 つとも実際に叩いて確かめた。**

| コマンド | 出力（末尾 1 行） |
| --- | --- |
| `git diff --cached --name-only -- '*.md'` | `"archives/todo/TODO-021. \343\203\252\343\203\225...md"` |
| `git diff --cached --name-only -z -- '*.md' \| tr '\0' '\n'` | `archives/todo/TODO-021. リファクタリング（挙動は変えない）.md` |
| `git diff --name-only HEAD -- '*.md'` | `"archives/todo/TODO-021. \343\203\252\343\203\225...md"` |
| `git diff --name-only -z HEAD -- '*.md' \| tr '\0' '\n'` | `archives/todo/TODO-021. リファクタリング（挙動は変えない）.md` |

あわせて、**なぜ `-z` が要るか**（八進エスケープされたパスは Read できない、
`core.quotePath=false` では空白・引用符入りの名前が残るので足りない）を
定義に書いた。`git grep` 側にだけ `core.quotePath=false` の注意がある
非対称は、これで解消した。

コメント行の `# -a でコミットするとき` は、pathspec でも使う経路に
なったので `# -a でコミットするとき、pathspec を付けるとき` に直した。

## 3. pathspec 付きの `git commit` を拾えるようにした

main が決めた条件をそのまま実装した。

```sh
look_worktree=""
if <cmd に -a / --all がある>; then
	look_worktree="yes"
elif [ -z "$(git -C "$root" diff --cached --name-only 2>/dev/null)" ]; then
	look_worktree="yes"
fi
```

`-a` の判定を残したまま、`elif` で「ステージが空なら作業ツリーも見る」を
足した形。**pathspec を正規表現で切り出してはいない**（依頼書のとおり）。
なぜこの条件で足りるのかの理由も、コメントとして本文に書いた。

## 3 の直しで気づいて、その場で直した副作用

最初は emptiness の判定にも `-z` を付けて書いた。すると **bash が
stderr に警告を出した**。

```
check-md-commit.sh: 行 54: 警告: コマンド代入: 入力のヌルバイトを無視しました
```

コマンド置換は NUL を扱えないため。stderr なので debug log にしか出ず
コミットは止まらないが、reviewer が「stdout に JSON 以外が混じる経路が
見当たらない」と確認した状態を汚すので直した。

**この 1 行だけ `-z` を付けない**（中身が空かどうかを見るだけで、
ファイル名を使わないため）。理由をコメントに書いた。
直したあと、主要な 4 経路で **stderr が空であることを確認済み**。

## 自分で確かめたこと

すべて scratchpad の使い捨てリポジトリと clone で試した。
**本物のコミットは作っていない。** `~/ytsched/data` は触っていない。
出た JSON はすべて `jq -e .` に通して valid を確認した。

`bash -n` OK。`shellcheck` 指摘なし。`jq -e . .claude/settings.json` valid。

### 新しい経路（指摘 3）

| 状態 | コマンド | 結果 |
| --- | --- | --- |
| ステージ空＋`a.md` を未ステージで変更 | `git commit -m x a.md` | **出力あり**（直った） |
| ステージ空＋日本語名の `.md` を変更 | `git commit -m "docs" "archives/todo/TODO-021. …md"` | **出力あり**。ファイル名も化けずに出る |
| ステージ空＋`.md` の変更なし | `git commit -m x a.md` | 出力なし、`exit 0` |
| ステージ空＋`.md` を変更 | `git commit -m x`（素） | 出力あり。**main が承知のうえで許容した「余計に促す」場面**（この状態で素の `git commit` を打つと git 自身がエラーで終わる） |

### リグレッション（前回すでに確かめてあった経路）

依頼書が名指しした `.py` だけの経路を含め、全部やり直した。

| # | 状態・コマンド | 結果 |
| --- | --- | --- |
| R-1 | **`.py` だけステージ**、`git commit -m "feat: code"` | **出力なし、`exit 0`**（壊れていない） |
| R-2 | `.py` ステージ＋`.md` 未ステージ、`-a` なし | 出力なし |
| R-3〜5 | 同上＋`-a` / `-am` / `--all` | 出力あり |
| R-6 | `git commit --amend --no-edit` | 出力なし（`-a` と誤認しない） |
| R-7 | `.md` ステージ済み | 出力あり |
| R-8〜9 | `git status` / `ls -l` | 出力なし |
| R-10 | `git log --oneline \| grep commit` | 出力なし |
| R-11 | `git log --grep=commit` | 出力なし |
| R-12 | **`git add -A && git commit -m "docs"`**（このリポジトリで使う形） | 出力あり |
| R-13 | `cd /tmp && git commit -m x` | 出力あり |
| R-14 | `git -C <path> commit -m x` | 出力あり |
| — | 空 stdin / `not json` / `{}` | 出力なし、`exit 0` |
| — | リポジトリ外（`CLAUDE_PROJECT_DIR` 未設定＋cwd も外／非リポジトリを指定） | 出力なし、`exit 0` |

R-1・R-2 が出力なしのままなのは、ステージが空でないので新しい条件
（`elif`）に入らないため。依頼書が確かめろと書いた点はそのとおりだった。

### 初回コミット前（`HEAD` が無い）リポジトリ

`git init` 直後でも `exit 0`。ステージ済みの `.md` があれば正しく拾う
（`git diff --cached --name-only` は `HEAD` が無くても動く）。

### `95895c1` の再現（clone で end-to-end）

- `git add -A && git commit -m "docs"` の形 → **`.md` 12 個すべてを一覧**。
  日本語名の `archives/todo/TODO-021. リファクタリング（挙動は変えない）.md`
  も化けずに出る
- ステージを解いて `git commit -m "docs(todo): x" TODO.md` → **`TODO.md` を
  拾う**（新しい経路が実際に効いている）

## 直さずに残したもの

- **reviewer の指摘 4**（`sudo git commit` / `env FOO=1 git commit` /
  `timeout 60 git commit` / `command git commit` / `/usr/bin/git commit`）。
  依頼書の指示どおり見送り
- **`a.py` をステージした状態で `git commit -m x TODO.md`** は、この直しでも
  拾えない（ステージが空でないため）。依頼書が承知のうえで見送ると
  書いている経路
- **`git diff --name-only HEAD` は untracked なファイルを見ない**ので、
  作業ツリー側を見る経路では「まだ一度も `git add` していない `.md`」を
  拾えない。ただし `git commit -m x <untracked>.md` は git 自身が
  `pathspec did not match any file(s) known to git` で失敗し、`-a` も
  untracked を含めないので、**git の動きと一致していて穴にはならない**
- TODO-026 のチェック項目「既存 5 個の定義を整理して…」（`runner` を
  `verifier` に畳めるか）は今回も手つかず。定義は 6 個のまま。main の判断
- reviewer の「確信度が低い」節の 4 点（`systemMessage` の文言が断定的、
  `wording.md` の「10 語を超えたら疑ってよい」、`git grep` を `.md` に
  限っていること、`matcher: "Bash"` の部分一致）は、依頼書に含まれて
  いないので触っていない

## うまくいかなかったところ

- 3 の直しを入れた最初の形で、bash の NUL 警告を stderr に出す状態を
  作ってしまった（上記）。テストの出力に混じっているのを見て気づき、
  その場で直した
- **`if` を外したので、hook が実際に発火するかは `matcher: "Bash"` だけに
  懸かっている。** これは動かしてみないと分からない。`settings.json` を
  効かせるには**利用者による Claude Code の再起動**が要る。
  `verifier` には、再起動後に `git add -A && git commit --dry-run` の形を
  必ず試してもらう必要がある（reviewer が指摘 1 の末尾で挙げていた形）
