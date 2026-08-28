# TODO-094 wording report

前例の有無は `git grep -cF <語> HEAD -- '*.md'` で数えた（HEAD 基準）。
**文書は直していない。** 挙げるだけ。決めるのは main。

## 前例の無い語（件数の少ない順）

### 1. `SEARCH_ENOUGH_DAYS`

- 箇所: `archives/todo/TODO-094. 細かいもの.md`「`SchedLoader.SEARCH_MODE_DAYS` → `SEARCH_ENOUGH_DAYS`」、
  `README.md` / `verifier-request.md` / `verifier-report.md` にも同じ改名の記述。
- 件数: 前例なし（0 件）。
- 見立て: コード上の新しい定数名。archive 本文に「コードの挙動を正として、
  名前を利用者に選んでもらった（2026-08-28）」とあり、main が選定した命名。
  語の造語というより識別子の新設。判断は main。

### 2. `SEARCH_HARD_LIMIT_DAYS`

- 箇所: 同上（`handler_util.SEARCH_MODE_MAX_DAYS` → `SEARCH_HARD_LIMIT_DAYS`）。
- 件数: 前例なし（0 件）。
- 見立て: 1 と同じく main が選んだ新しい定数名。「hard limit」は一般的な
  用語で、識別子としては素直。判断は main。

### 3. 二重照合

- 箇所: `archives/todo/TODO-094. 細かいもの.md`「**`mk_todo_by_date()` の二重照合を除去**」、
  `verifier-request.md`「二重 `search_match()` 除去」、
  `verifier-report.md`「二重照合除去」「中の照合ループ」。
- 件数: 前例なし（0 件）。「二重」「照合」は個別には前例多数。
- 見立て: 「同じ照合処理を 2 回かけている」ことを指す説明語。構成する語が
  どちらも一般的で、意味も素直に通る。造語性は低いと見るが、決めるのは main。

### 4. さかのぼり（名詞）

- 箇所: `archives/todo/TODO-094. 細かいもの.md`「1825 はさかのぼりの絶対の上限」、
  `verifier-request.md`「`SEARCH_HARD_LIMIT_DAYS`（1825）はさかのぼりの絶対の上限」。
- 件数: 前例なし（0 件）。動詞「さかのぼる」は前例多数。
- 見立て: 動詞の名詞化だけで、一般に通用する。問題は無いと見る。

### 5. 宛先名

- 箇所: `archives/todo/TODO-094. 細かいもの.md`「短縮形 `-l` と click の宛先名 `size_limit`、`WebServer` への引数はそのまま」。
- 件数: 前例なし（0 件）。「宛先」は TODO-034 で既出。
- 見立て: click の `dest`（パーサが値を格納する属性名）を指す言い換え。
  click まわりの一般的な呼び名ではなく、この文書での説明語に見える。判断は main。

### 6. 短縮形

- 箇所: `archives/todo/TODO-094. 細かいもの.md`「短縮形 `-l` と click の宛先名…」、
  `verifier-request.md` / `verifier-report.md`「`-l` は据え置き」の文脈。
- 件数: 前例なし（0 件）。
- 見立て: コマンドラインの短いオプション（short option）の通常の呼び方。
  一般に通用する。問題は無いと見る。

### 7. 絶対の上限

- 箇所: `archives/todo/TODO-094. 細かいもの.md`「1825 はさかのぼりの絶対の上限」、
  `verifier-request.md` / `verifier-report.md`「さかのぼりの絶対の上限」。
- 件数: HEAD では `TODO.md` に 1 件だが、これは**今回のコミットで削除される
  TODO-094 の項目本文**（同じ書き手）。その外に前例なし。
- 見立て: 「hard limit」を日本語で言い換えたもの。ふつうの日本語の範囲で、
  造語というほどではないと見る。

### 8. 諦める日数

- 箇所: `archives/todo/TODO-094. 細かいもの.md`「旧『1 件も当たらないときに
  諦める日数（元 MainHandler.…）』」（旧コメントの引用）。
- 件数: HEAD では `TODO.md`（削除される TODO-094 本文）と
  `archives/agents/TODO-087/wording-report.md` / `TODO-088/implementer-request.md` に既出。
- 見立て: 旧コメント文言の引用として出てくるもので、この文書での新しい
  言い換えではない。改める対象は旧コメント側であり、archive はそれを
  「食い違っていた」と説明しているだけ。問題は無いと見る。

## 読んだファイル

- `archives/todo/TODO-094. 細かいもの.md`
- `archives/agents/TODO-094/README.md`
- `archives/agents/TODO-094/verifier-request.md`
- `archives/agents/TODO-094/verifier-report.md`
- `archives/agents/TODO-094/wording-request.md`
- `TODO.md` の差分（TODO-094 を完了済みへ移す変更）

## 前例なしの語数

8 語（うち 2 語はコード上の定数名、残りは一般的な日本語か旧文言の引用）。
10 語の目安は超えていない。造語らしい造語は見当たらないが、
**3（二重照合）と 5（宛先名）**は「このリポジトリだけの言い換え」に
見える度合いがやや高い。決めるのは main。
