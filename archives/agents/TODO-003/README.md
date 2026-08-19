# TODO-003 のサブエージェント編成

対応する項目: [TODO-003. pytest によるテスト整備](../../todo/TODO-003.%20pytest%20によるテスト整備.md)

`.claude/agents/` の常設定義（TODO-013 で置いたもの）を、初めてそのまま
使った回。項目を立てたときに担当を決めてあったので、着手時に分担案を出して
承認を待つ手順は要らなかった。

## 分担

| 名前 | 定義 | 担当 |
|---|---|---|
| [implementer](../../../.claude/agents/implementer.md) | opus / effort high | `tests/` の作成、`pyproject.toml` への dev 依存追加 |
| [verifier](../../../.claude/agents/verifier.md) | sonnet / effort medium | `uv sync` / `pytest` / `--runxfail` / カバレッジ / アプリ起動の実測 |
| [reviewer](../../../.claude/agents/reviewer.md) | opus / effort high | テストが現状の挙動を正しく写しているか（**バグごと固定していないか**） |

報告:

- [report-implementer.md](report-implementer.md)
- [report-verifier.md](report-verifier.md)
- [report-reviewer.md](report-reviewer.md)

依頼: [request-implementer.md](request-implementer.md)

main（管理者）は依頼と判断に徹し、`TODO.md` の更新とコミットを受け持った。

## この分担にした理由

- **`reviewer` を入れたのがこの項目の肝。** テストを足す項目に「良いか」を
  見る担当を付けたのは、**バグを「正しい挙動」として固定してしまう**のが
  この項目でいちばん怖い失敗だから。固定してしまうと、TODO-005 で直したときに
  テストが落ちて「直すのをやめる」方向に引っ張られる。
  実際 `reviewer` は、`implementer` も `verifier` も気づかなかった
  **空振りする assert 2 件**（`filter_str` が入力欄にそのまま出るので、
  絞り込みが壊れても通ってしまう）を見つけた。
  `verifier` の「動くか」だけでは出てこない指摘
- `implementer` を Opus にしたのは、「現状の挙動を固定する」と
  「バグを固定しない」を両立させる判断が要るため。どのバグに xfail を付け、
  どれはテストを書かないかは、機械的には決まらない
- `verifier` を Sonnet にしたのは、確認の手順が決まっていて判断が要らないため。
  実際、報告の数字と実測がすべて一致することを確かめただけで足りた
- `verifier` と `reviewer` に **`Edit` を持たせていない**のがそのまま効いた。
  `reviewer` は 4 件の確信度の高い指摘を出したが、直すかどうかは main が判断し、
  そのうち 3 件を TODO-003 の内で直させ、1 件は TODO-005 へ回した

## 分かったこと

- **報告をファイルで受け渡す形は、2 巡目で効いた。** `reviewer` への依頼で
  `report-implementer.md` を読ませたので、`implementer` が単独で決めた判断
  10 件をそのまま検討させられた。main が書き写す手間も伝達漏れも無かった
- `reviewer` が**報告ファイルを書けず**、返答に全文を貼ってきた
  （main が `report-reviewer.md` へ保存した）。定義では `Write` を
  持たせてあるので、原因は分かっていない。次に同じことが起きるようなら
  定義を見直す
