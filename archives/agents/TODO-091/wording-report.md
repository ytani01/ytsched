# TODO-091 wording 報告

対象: TODO-091 の完了コミットに入る `.md` 5 ファイル。

- `TODO.md`（差分のみ。TODO-091 の節を削除し、目次へ 1 行追加。新語なし）
- `archives/todo/TODO-091. SchedData の渡し方と、表示に渡す値の dataclass 化.md`
- `archives/agents/TODO-091/README.md`
- `archives/agents/TODO-091/implementer-report.md`
- `archives/agents/TODO-091/verifier-report.md`

件数は `git grep -cF <語> HEAD -- '*.md'` の合計（その文書が入る前）。
前例なしの順に並べる。

---

## 1. 診断表示 / 診断値（「診断」）

- 箇所:
  - TODO-091.md L37「**キャッシュ件数の表示は残す**（版数の隣の診断表示。
    消すかどうかは別の UI 判断…）」
  - README.md L19「表示自体は無害な診断値なので残し」
- `git grep`: 「診断表示」「診断値」ともに前例なし。「診断」は 4 件あるが
  すべてテストデータの文字列（`（重要）健康診断の申込`）で、意味が違う
- 見立て: **この文脈での言い換え。** `get_cache_size()` の画面表示を
  「診断表示 / 無害な診断値」と呼んでいる。開発者に向けた内部情報という
  意図は分かるが、リポジトリでこの呼び方の前例はない。main の判断対象

## 2. 属性参照

- 箇所: TODO-091.md L40・implementer-report.md L34・verifier-report.md L46
  「`w['offset']` などの添字を `w.offset` の属性参照に」
- `git grep`: 前例なし
- 見立て: **一般的な用語**（Python の attribute access）。リポジトリでは初出

## 3. 添字

- 箇所: TODO-091.md L39「週ループの `w['offset']` などの添字を」
- `git grep`: 前例なし
- 見立て: **一般的な日本語**（subscript / 添字アクセス）。初出

## 4. 週ループ

- 箇所: TODO-091.md L39・implementer-report.md L32「`main.html`: 週ループの」
- `git grep`: 前例なし（「週パネル」は 4 件あり定着済み）
- 見立て: **説明的な複合語。** 「週パネル」と同系で通じるが、初出

## 5. 戻り値注釈

- 箇所: TODO-091.md L30「`load_week()` / `search()` の戻り値注釈を
  `list[SchedDay]` に」
- `git grep`: 前例なし
- 見立て: **一般的な用語**（return type annotation）。初出

## 6. キャッシュ件数

- 箇所: TODO-091.md L36・L57、implementer-report.md、verifier-report.md
  「キャッシュ件数の表示は残す」「版数の隣にキャッシュ件数が出る」
- `git grep`: 前例なし（`get_cache_size` の値のこと）
- 見立て: **説明的。** キャッシュのエントリ数という素直な意味で、造語性は低い

## 7. 波及

- 箇所: implementer-report.md L57「範囲外への波及は確認した限り無し」
- `git grep`: 前例なし
- 見立て: **一般的な日本語。** 問題なし

## 8. UI 判断

- 箇所: TODO-091.md L37「消すかどうかは別の UI 判断なので」、README.md L20
- `git grep`: 前例なし
- 見立て: **説明的な略し方。**「UI に関わる判断」の意で通じる。造語性は低い

## 9. 実テンプレート

- 箇所: TODO-091.md L59・verifier-report.md L46
  「`test_web.py` / `test_browser.py` が実テンプレートで通っている」
- `git grep`: 前例なし（`実ブラウザ` 1 件、`実データ` 158 件と同じ `実〜` の形）
- 見立て: **既存の言い回しの延長。** フィクスチャでなく本物のテンプレート、
  の意。造語性は低い

---

## まとめ

- 読んだファイル: 上記 5 ファイル
- 前例なしの語: **9 語**（診断表示/診断値、属性参照、添字、週ループ、
  戻り値注釈、キャッシュ件数、波及、UI 判断、実テンプレート）
- 10 語未満。大半は一般的な専門用語か普通の日本語で、`.md` そのものは
  概ね問題ないと見る
- **main の判断が要る筆頭は「診断表示 / 診断値」**（No.1）。画面の
  キャッシュ件数表示をこの語で呼ぶ前例はリポジトリにない
