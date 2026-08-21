# verifier への依頼（TODO-026）

`~/work/ytsched/TODO.md` の TODO-026 と、
`archives/agents/TODO-026/implementer-request.md`（仕様）、
`archives/agents/TODO-026/implementer-report.md`（実装の報告）を
**先に読むこと**。

implementer が作ったのは次の 3 つ。

- `.claude/agents/wording.md` — 新しい担当の定義
- `.claude/hooks/check-md-commit.sh` — `git commit` を捕まえる hook
- `.claude/settings.json` — hook の設定

**hook は動くもの。「同梱したのだから動くだろう」で済ませず、実際に叩く。**

---

## 確かめること

### A. hook が発火するか（いちばん大事）

**一時ディレクトリに使い捨ての git リポジトリを作って試す。
`~/work/ytsched` で本物のコミットを作らないこと。** `mktemp -d` を使い、
終わったら消す。

スクリプトに stdin から JSON を食わせる形で叩く。JSON の形は

```json
{"tool_input": {"command": "git commit -m \"...\""}}
```

（実際のキーの位置は `implementer-request.md` と implementer の報告で
確かめること）

次の場合を全部試して、**実際に得られた stdout と終了ステータスを
そのまま報告する**。

1. `.md` をステージしてある状態で `git commit -m "..."` → JSON が出て、
   ファイル名が入っていること
2. `.md` を含まない（`.py` だけなど）状態 → **何も出さずに exit 0**
3. 何もステージしていない状態 → 何も出さずに exit 0
4. `git commit -am "..."` で `.md` を**ステージせずに**変更した状態 →
   JSON が出ること（`-a` の経路）
5. `git status` や `git log` など、`git commit` でないコマンド →
   何も出さずに exit 0
6. **git リポジトリの外**で呼ばれた場合 → exit 0 で止まらないこと
7. 空白や引用符を含むファイル名の `.md`（例 `a b".md` が作れるなら）→
   出た JSON が `jq .` に通ること

**出た JSON は毎回 `jq .` に通して、壊れていないことを確かめる。**

**終了ステータスが 0 以外になる経路が 1 つでもあれば、それは報告する。**
hook が 0 以外を返すと Claude Code の挙動が変わる。

### B. 設定の形

`.claude/settings.json` が JSON として読めるか（`jq . .claude/settings.json`）。
`command` に書かれたパスに、実行権限の付いたファイルが実在するか
（`ls -l`）。`${CLAUDE_PROJECT_DIR}` を実際のパスに置き換えたときに
そのファイルへ届くか。

**`.claude/settings.local.json` が書き換えられていないこと**も見る
（`git status` で確認）。

### C. `wording` が実際に「足場」を挙げるか

TODO-025 で調べたとおり、「足場」という造語がリポジトリに入ったのは
コミット `95895c1` の 1 つだけで、入っているファイルは
`archives/agents/TODO-021/implementer1-report.md` と
`archives/agents/TODO-021/reviewer-report.md` の 2 つ。

`.claude/agents/wording.md` に書かれた手順を**自分で（担当を起動せずに）
なぞって**、次を確かめる。

- 定義に書かれている `git grep` のコマンドを、`95895c1^` を基準にして
  実際に叩く。**「足場」の前例が 0 件と出るか**
- 定義のコマンドが `HEAD` を基準にしているなら、試すときは `95895c1^`
  に読み替えてよい（作業ツリーを切り替えないこと。`git grep -c 足場
  95895c1^` の形で基準を指定できる）
- 定義に書かれた手順で、**その 2 ファイルから「足場」を拾えるか**
  （文書を読んで語を拾う部分は自分でやってよい）

拾えなければ、定義のどこが足りないかを報告する。**定義は直さない。**

---

## 決まりごと

- **コードも定義も直さない。** 見つけたことは報告するだけ
- **書き込んでよいのは自分の報告ファイルだけ**
- **git commit / git tag はしない**
- **`TODO.md` は編集しない**
- 報告は `archives/agents/TODO-026/verifier-report.md`。
  返事は 5 行以内
