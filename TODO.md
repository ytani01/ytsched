# TODO

**残っている項目: TODO-020。**
これまでに 19 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-021` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移すと決めた**
（TODO-018）。**まだ実装していない。** 移行先の仕様は
`docs/data-format.md` にある。既存データは移行ツールで一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-020. JSON Lines への移行ツールと、読み書きの実装

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer

- [ ] `SchedDataFile` の読み書きを JSON Lines にする
- [ ] 判定・検索の照合に使う正規化を入れ、読み込み時の文字置換をやめる
- [ ] 旧形式から変換する移行ツールを作る
- [ ] テストを足す
- [ ] `CLAUDE.md` の「データモデルの勘所」を新形式に合わせて書き直す

（背景）

仕様は `docs/data-format.md` にある。TODO-018 で決めたところまでで、
**実装は手つかず**。TODO-019 で作った合成テストデータ
（`tests/data/old_format/`）を使って進める。

（やること）

- **読み書き** — `SchedDataFile.load()` / `save()` を JSON Lines にする。
  行ごとにデコードし、読めない行はその行だけ飛ばす。`.bak` の仕組みは
  変えない
- **正規化** — 「重要」「取り消し」の判定、`get_sortkey()`、
  `search_str()` の 3 か所で、全角括弧を半角にして小文字化した
  コピーを使って照合する。**保存する文字列は変えない。**
  `htmlstr2text()` / `text2htmlstr()` による読み書き時の変換は無くす
- **移行ツール** — `docs/data-format.md` の 6 手順のとおりに変換する。
  `{日}.cgi` と `ToDo.cgi` だけを対象にし、変換できない行は捨てずに
  書き出して報告する。CLI のサブコマンドとして足すか、別のスクリプトに
  するかは実装時に決める
- **文書** — `CLAUDE.md` の「データモデルの勘所」は旧形式の説明のまま
  なので、書き直す

（気をつけること）

- **「重要」「取り消し」「ToDo」の判定方法は変えない**（TODO-018 で
  決めた条件）。判定を安定させるだけで、判定の仕方そのものは動かさない
- 現状は `（重要）打合せ` が入力直後と再読み込み後で判定が食い違う。
  正規化を入れると**挙動が変わる**（どちらでも重要と判定されるようになる）。
  この変化は意図したもので、テストで押さえる
- `base.html` の `{% autoescape None %}` は現状維持（TODO-012）

（担当を分ける理由）

複数のファイルにまたがり、実装とテストと文書がまとまって要るので
implementer を立てる。動くかの確認は verifier。**分岐や条件式の意味が
変わる**（判定の正規化、壊れた行の切り分け）ので、TODO-017 の基準に従い
reviewer も入れる。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-019.** 移行元のテストデータを作る](archives/todo/TODO-019.%20移行元のテストデータを作る.md)
- [**TODO-018.** データ形式の見直し（何を変えるかを決める）](archives/todo/TODO-018.%20データ形式の見直し（何を変えるかを決める）.md)
- [**TODO-017.** reviewer の起用基準と、verifier を一律で立てる運用の見直し](archives/todo/TODO-017.%20reviewer%20の起用基準と%20verifier%20の運用.md)
- [**TODO-016.** `date` が空の POST と、存在しない `sde_id` の扱い](archives/todo/TODO-016.%20date%20が空の%20POST%20と、存在しない%20sde_id%20の扱い.md)
- [**TODO-015.** ruff の整形・書き換え系の指摘を解消](archives/todo/TODO-015.%20ruff%20の整形・書き換え系の指摘を解消.md)
- [**TODO-012.** 不正な正規表現を入れられたときの扱い](archives/todo/TODO-012.%20不正な正規表現を入れられたときの扱い.md)
- [**TODO-010.** CLAUDE.md の作成](archives/todo/TODO-010.%20CLAUDE.md%20の作成.md)
- [**TODO-009.** README の更新](archives/todo/TODO-009.%20README%20の更新.md)
- [**TODO-008.** uv tool install 方式へ](archives/todo/TODO-008.%20uv%20tool%20install%20方式へ.md)
- [**TODO-007.** loguru への移行](archives/todo/TODO-007.%20loguru%20への移行.md)
- [**TODO-006.** 型ヒントの整備](archives/todo/TODO-006.%20型ヒントの整備.md)
- [**TODO-004.** lint・型チェックと mise タスク](archives/todo/TODO-004.%20lint・型チェックと%20mise%20タスク.md)
- [**TODO-014.** サブエージェントの報告ファイル名](archives/todo/TODO-014.%20サブエージェントの報告ファイル名.md)
- [**TODO-005.** 明らかなバグの修正](archives/todo/TODO-005.%20明らかなバグの修正.md)
- [**TODO-003.** pytest によるテスト整備](archives/todo/TODO-003.%20pytest%20によるテスト整備.md)
- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
