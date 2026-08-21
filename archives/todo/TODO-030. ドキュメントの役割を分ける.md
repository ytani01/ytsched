# TODO-030. ドキュメントの役割を分ける

見込み: main = Opus 5 / effort high、担当 = writer + verifier + wording
実施: main = Opus 5 / effort high、担当 = writer + verifier + wording

## きっかけ

文書が `README.md`・`CLAUDE.md`・`docs/data-format.md` の 3 つしかなく、
開発者向けの情報とコードの構成が `README.md` と `CLAUDE.md` に混ざって
いた。`CLAUDE.md` の「構成」「データモデルの勘所」「Web の構成」
「コマンド」は、本来なら人間の開発者も読むもの。

役割をこう分けた。

| 文書 | 役割 |
| --- | --- |
| `README.md` | 利用者向け |
| `docs/Developer.md` | 開発者向け。技術スタック、開発ツール、テストの走らせ方 |
| `docs/data-format.md` | データ形式の詳細 |
| `src/README.md` | ソースの構成、クラス構造 |
| `tests/README.md` | テストの構成 |
| `CLAUDE.md` | Claude 向け |

`tests/README.md` は最初の分けかたから漏れていて、着手したあとに
利用者の指摘で足した。`docs/Developer.md` が**走らせ方**、
`tests/README.md` が**構成**という切り分けは、`docs/Developer.md` と
`src/README.md` の切り分けに合わせたもの。

## やったこと

- `src/README.md`・`docs/Developer.md`・`tests/README.md` を新しく作った
- `CLAUDE.md` の 4 節（構成・データモデルの勘所・Web の構成・コマンド）は
  **本文を消して、上の 3 つへのリンクにした**。225 行から 100 行に減った。
  「これは何か」「サブエージェントの分担」は `CLAUDE.md` にしか無い内容
  なので残した
- `README.md` の「memo」節（JavaScript の `Date` の罠、
  `javascript-scroll.svg`）を `docs/Developer.md` へ移した
- `docs/data-format.md` は中身を変えず、相互リンクだけ足した
- 6 つの文書が互いに辿れるようにした
- `migrate.py` が旧 `CLAUDE.md` の構成一覧から漏れていたので、
  `src/README.md` に入れた

（決めたこと）

**`CLAUDE.md` の重複はリンクに置き換える。** 重複がゼロになる代わりに、
Claude は毎回リンク先を開くことになる（自動では読まれない）。そのため
`CLAUDE.md` 側に「コードを触る前に読むこと」と明記した。

## テスト

verifier が確かめた（`archives/agents/TODO-030/verifier-report.md`）。

- `README.md` と `docs/Developer.md` のコマンド例を実際に叩いた。
  `mise tasks` の依存関係が記述と一致、`mise run lint` 通過、
  `pytest` 330 件通過、`migrate --help` / `webapp --help` のオプションが
  記述と一致。一時ディレクトリで起動して HTTP 200・例外なし
- 6 文書の Markdown リンクと画像参照がすべて辿れた
- モジュール一覧・テストファイル一覧が実物と一致
- `docs/data-format.md` は相互リンク 4 行のみで本文無変更

**移し漏れが 2 件見つかった。**

1. **`white-space: pre-wrap` の注記** — 本当の移し漏れ。
   「画面の改行表示は CSS が担っている（テンプレート側でタグを差し込んで
   いるわけではない）」という念押しが 6 文書のどこにも無かった。
   知らずに `sde.html` を触ると壊せるので `src/README.md` へ足した
2. **`date2path()` のパスの決め方** — 移し漏れではなかった。パスの規則
   そのものは `docs/data-format.md` の「ファイルの置き場所」に、
   ディレクトリ図つきで旧 `CLAUDE.md` より詳しく書かれていた。ただし
   「コードのどこが担うか」が辿れないので、メソッド名とリンクだけ足した

直したのは writer（確認の担当には直させない）。

wording が `.md` 9 本を見た（`archives/agents/TODO-030/wording-report.md`）。
前例の無い語は 7 語（走らせ方・コードを触る前に読むこと・移し漏れ・
移り先・落として構わない・案内・読み物）。**いずれも一般的な日本語で、
TODO-021 の「足場」のような造語ではないのでそのまま残した。**
直したのは「掛ける」→「かける」の 1 か所だけ（同じ意味のひらがな表記が
`TODO.md`・`docs/data-format.md` に前例としてあり、表記が割れていた）。

## 分担について

`archives/agents/TODO-030/README.md` に理由と報告がある。

**reviewer は入れなかった**（コードの挙動が変わらず、分岐も条件式も
動かないため）。**verifier は入れた**。文書だけの項目だが、
`README.md` と `docs/Developer.md` に実際に叩けるコマンドが載るので、
「試せる手順があるなら再現は必ず分ける」（TODO-017）に当たる。
結果として、その verifier が移し漏れを見つけた。**文書だけの項目でも、
書いた本人は「移したつもり」で済ませてしまう**という点は、コードで
実装と確認を分ける理由とそのまま同じだった。
