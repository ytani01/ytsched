# implementer への依頼 その 2（TODO-026・reviewer の指摘を直す）

`archives/agents/TODO-026/reviewer-report.md` の指摘 1・2・3 を直す。
**指摘 4 は見送る**（main の判断。理由は下記）。

## 1. `.claude/settings.json` から `if` を外す

`"if": "Bash(git commit *)"` の行を消す。`matcher: "Bash"` だけにする。

理由は reviewer の指摘 1。permission rule の前方一致は
`Bash(git commit:*)`（コロン）の形で、`Bash(git commit *)` は文書にある
2 形式のどちらでもない。効いた場合に
`git add -A && git commit …`（このリポジトリで実際に使う形）を弾いて、
**hook が黙って発火しなくなる**。スクリプトが自前で `git commit` を
判定しているので `if` は冗長。

## 2. `.claude/agents/wording.md` の `git diff` に `-z` を付ける

37〜40 行あたりの対象ファイル収集コマンド。hook 側で「必須」と判断した
のと同じ直しを、定義側にも入れる。`tr '\0' '\n'` で改行区切りへ戻す形も
hook と揃えること。

73 行の `git grep` に `core.quotePath=false` を書いてあるのに
`git diff` に無い、という非対称も解消する。

**実際に叩いて、日本語ファイル名が化けないことを確かめてから書くこと。**

## 3. pathspec 付きの `git commit` を拾えるようにする

`.claude/hooks/check-md-commit.sh`。実測（reviewer）:

```
a.md を変更（ステージしない）
入力: {"tool_input":{"command":"git commit -m x a.md"}}
→ 出力なし、exit 0
```

`git commit -m "docs(todo): …" TODO.md` は main が使う形なので塞ぐ。

**やり方は次のようにすること**（main が決めた）。

> **ステージされたファイルが 1 つも無ければ**（`.md` に限らず、
> `git diff --cached --name-only` が空なら）、`-a` の有無に関わらず
> 作業ツリー側（`git diff --name-only HEAD -- '*.md'`）も見る。

そう決めた理由: ステージが空のときに素の `git commit` を打っても、git
自身がエラーで終わる。つまり**ステージが空で `git commit` を打つのは
`-a` か pathspec のときしかない**ので、この条件なら余計に促す場面が
ほぼ増えない。

pathspec そのものを正規表現で切り出すやり方は採らない（`-m` の引数と
pathspec を見分けるのが難しく、壊れやすい）。

なお「`a.py` をステージした状態で `git commit -m x TODO.md`」は、
この直しでも拾えない。**それは承知のうえで見送る**（main の判断）。

## 見送るもの（直さない）

**reviewer の指摘 4**（`sudo git commit` / `env FOO=1 git commit` /
`timeout 60 git commit` / `command git commit` / `/usr/bin/git commit` を
拾わない）。このリポジトリでどれも使っていない。塞ぐと正規表現が
複雑になり、そのぶん壊れやすくなる。**直さないこと。**

## 確かめること

- 3 の直しで、既に確かめてある経路が壊れていないこと。特に
  **`.md` を含まないコミット（`.py` だけステージ）で、これまでどおり
  何も出さずに `exit 0` になること**。ステージが空でないので新しい条件に
  入らないはず
- 新しい経路: ステージ空＋`.md` を未ステージで変更＋`git commit -m x a.md`
  → JSON が出ること
- ステージ空＋`.md` の変更も無い → 出力なし、`exit 0`
- **一時ディレクトリの使い捨てリポジトリで試す。本物のコミットは作らない**
- 出た JSON は `jq -e .` に通す

## 気をつけること

- **触ってよいのは `.claude/settings.json`・`.claude/agents/wording.md`・
  `.claude/hooks/check-md-commit.sh` の 3 つだけ**
- `TODO.md`・`CLAUDE.md`・`archives/todo/` は触らない（main が書く）
- `.claude/settings.local.json` は触らない
- **git commit / git tag はしない**
- 報告は `archives/agents/TODO-026/implementer-report2.md`。返事は 5 行以内
