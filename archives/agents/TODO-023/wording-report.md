# wording 報告（TODO-023）

## 前例の無い語・少ない語

### 連鎖

- 出てくる箇所:
  - `archives/todo/TODO-023. mise.toml の見直し.md` 15行目
    「`upgrademise` → `upgradeuv` の連鎖ごと動かない」
  - `archives/agents/TODO-023/verifier-report.md` 51行目
    「`lint` → `test` → `build` と連鎖し」、86行目
    「fmt/typecheck/lint も連鎖して走る」
- `git grep -cF 連鎖 HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: タスクの依存関係を指す一般語で、造語ではないと思う。
  ただしこのリポジトリでは初出で、`depends` の依存関係を指すのに
  「依存」ではなく「連鎖」を使っており、文書内でも両方（「依存」と
  「連鎖」）が混在している。統一するかどうかは main の判断次第

### どこからも依存されていない／どこからも依存されない

- 出てくる箇所:
  - `archives/todo/TODO-023. mise.toml の見直し.md` 37行目
    「**どこからも依存されない** タスクにした」
  - `archives/agents/TODO-023/verifier-request.md` 27行目
    「`upgradeproject` が**どこからも依存されていない**こと」
  - `archives/agents/TODO-023/verifier-report.md` 81行目（見出し）
    「upgradeproject がどこからも依存されていないこと」
- `git grep -cF` （両方の言い回しとも）: 前例なし（0 件）
- 見立て: 名詞化した用語ではなく、状態を説明する普通の文なので
  造語ではないと思う。判断できない部分は無い

### ホーム側

- 出てくる箇所:
  - `archives/todo/TODO-023. mise.toml の見直し.md` 31行目
    「同じ名前のタスクが `~/mise.toml`（ホーム側）にもあるので」
  - `archives/agents/TODO-023/verifier-request.md` 20行目
  - `archives/agents/TODO-023/verifier-report.md` 40行目
- `git grep -cF ホーム側 HEAD -- '*.md'`: 前例なし（0 件）
- 見立て: `~/mise.toml`（ユーザ側の設定）とプロジェクトの
  `mise.toml` を区別するための言い回し。一般に通用するかは
  判断できない。プロジェクト側の `mise.toml` を指す対語
  （「プロジェクト側」）は今回の文書には出てこず、`~/mise.toml` と
  書き分けている

### 空きポート

- 出てくる箇所: `archives/agents/TODO-023/verifier-request.md` 30行目
  「`--port <空きポート>` で」
- `git grep -cF 空きポート HEAD -- '*.md'`: 1 件
  （`archives/agents/TODO-021/verifier-request.md`）
- 見立て: 一般的な IT 用語（使用されていないポート番号）で、
  このリポジトリでも TODO-021 で前例がある。造語ではない

## 前例が十分にある語（参考、造語ではない）

`叩く`（10 件）・`分担`（63 件）・`見込み`（54 件）・`実施`（33 件）・
`退避`（21 件）・`見立て`（37 件）・`一時ディレクトリ`（72 件）・
`整形`（複数）・`検証`（複数）・`実測`（複数）・`書き戻す`（複数）は
いずれも前例があり、問題ないと判断した。

## 読んだファイル

- `TODO.md`（差分のみ）
- `CLAUDE.md`（差分のみ）
- `archives/todo/TODO-023. mise.toml の見直し.md`
- `archives/agents/TODO-023/README.md`
- `archives/agents/TODO-023/verifier-request.md`
- `archives/agents/TODO-023/verifier-report.md`

## 前例の無い語の数

4 語（連鎖／どこからも依存されていない（ていない・ない 2 形）／
ホーム側／空きポートは前例 1 件なので厳密には「前例が少ない語」）。
前例が完全にゼロなのは 3 語（連鎖・どこからも依存されない系・
ホーム側）。
