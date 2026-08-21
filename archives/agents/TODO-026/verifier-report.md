# verifier の報告（TODO-026）

依頼書 `verifier-request.md` の項目 A・B・C をすべて実際に叩いて確認した。
`~/work/ytsched` では本物のコミットを作っていない。使い捨てリポジトリは
scratchpad に作り、確認後に削除した。

## A. hook が発火するか

`.claude/hooks/check-md-commit.sh` に対して stdin から JSON を渡す形で、
使い捨てリポジトリ（`/tmp/.../scratchpad/hooktest`）を使って全 7 ケースを
確認した。**すべて期待どおりの結果で、終了ステータスは全ケース `exit=0`。**

| ケース | 入力 | 結果 |
| --- | --- | --- |
| 1 | `.md` 1 個ステージ済み、`git commit -m "docs"` | exit=0, 705 バイトの JSON、`jq .` 通る。ファイル名 `note.md` が入る |
| 2 | `.py` のみステージ、`git commit -m "code"` | exit=0, 出力なし（0 バイト） |
| 3 | 何もステージなし、`git commit -m "empty"` | exit=0, 出力なし |
| 4 | `.md` を未ステージのまま変更、`git commit -am "docs update"` | exit=0, 705 バイトの JSON（`-a` 経路で拾えている）。同条件で `-m`（`-a` 無し）だと出力なし ← 正しい |
| 5 | `git status` / `git log --oneline` / `ls -l` | いずれも exit=0, 出力なし |
| 6 | リポジトリの外（`CLAUDE_PROJECT_DIR` を非 git ディレクトリに設定）、`git commit -m "x"` | exit=0, 出力なし |
| 7 | ファイル名 `a b".md`・`日本語 ファイル.md` をステージ | exit=0, 769 バイトの JSON。`systemMessage` / `additionalContext` にファイル名が正しく（文字化けなく、引用符もそのまま）出て `jq .` 通る |

**終了ステータスが 0 以外になる経路は見つからなかった。**

使ったコマンドの形（例、ケース1）:

```sh
printf '%s' '{"tool_input":{"command":"git commit -m \"docs\""}}' \
  | CLAUDE_PROJECT_DIR="$REPO" .claude/hooks/check-md-commit.sh > out.json
echo $?          # → 0
jq . out.json     # → 正しくパースできる
```

### つまずいた点（hook の不具合ではなく、自分のテスト手順の問題）

最初 `out=$(... | hook)` として変数に取り込んだあと `echo "$out" | jq .` を
したところ `jq: parse error: Invalid string: control characters ...` に
なった。ファイルへリダイレクトして `jq . out.json` にしたら問題なく通った
ため、**hook の出力そのものは正しい**（`\n` は JSON エスケープ済みの
2 文字であり、生の改行ではなかった）。シェルの変数展開・`echo` を経由する
過程で崩れただけと判断する。**これは hook の不具合ではない。**

## B. 設定の形

- `jq . .claude/settings.json` → 正しくパースできた（内容は依頼書どおり）
- `.claude/hooks/check-md-commit.sh` に実行権限あり
  （`ls -l` で `.rwxr-xr-x`）
- `${CLAUDE_PROJECT_DIR}` を `/home/ytani/work/ytsched` に置き換えたパス
  `/home/ytani/work/ytsched/.claude/hooks/check-md-commit.sh` が実在し、
  `[ -x ]` も真
- `.claude/settings.local.json` は**変更されていない**。`git status --short`
  には出てこない（`.gitignore:90` で無視されている）。内容も
  `{"enabledMcpjsonServers": ["playwright"]}` のままで、hook の設定は
  入っていない

## C. `wording` が「足場」を挙げられるか

`.claude/agents/wording.md` に書かれた手順を、担当を起動せず自分でなぞった。

```sh
$ git grep -cF 足場 95895c1^ -- '*.md'
（出力なし、exit=1）  ← 前例 0 件

$ git grep -cF 足場 HEAD -- '*.md' | awk -F: '{s+=$NF} END{print s+0}'
14   ← 現状の HEAD を基準にすると前例ありに見えてしまう（実装報告どおり）
```

implementer の申し送りどおり、**`HEAD` を基準にすると「足場」は前例 14 件で
挙がらない**ことを実際に確認した。`95895c1^` を基準にすると exit=1（前例
0 件）になり、これが正しい判定になる。

対象の 2 ファイルから語を拾えるかも確認した。

```
archives/agents/TODO-021/implementer1-report.md:18:「TODO-021 の足場」という位置づけを...
archives/agents/TODO-021/implementer1-report.md:149:   `test_web.py` は既に 761 行あり、「TODO-021 の足場」という位置づけを...
archives/agents/TODO-021/implementer1-report.md:162:   足場としては既存分で足りる**と判断した
archives/agents/TODO-021/reviewer-report.md:234:- `tests/` の差分（足場のテスト。依頼で対象外）
```

両ファイルとも「足場」がそのまま読める形で出てくるので、定義に書かれた
「語を拾うのは自分（LLM）が読む」手順で問題なく拾える。

**定義に不足は見つからなかった。**

## まとめ

- A・B・C いずれも問題なし。hook・設定・`wording` の定義とも、依頼書に
  書かれた挙動どおりに動くことを実際に確認した
- main の判断が要る点は特に無い。implementer の報告にある「`runner` を
  `verifier` に畳むか」「wording を実際に立てて 15 語出るか」は依頼書の
  範囲外（項目 A・B・C）なので、この報告では扱っていない
