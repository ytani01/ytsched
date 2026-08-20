# TODO

**残っている項目: TODO-019。**
これまでに 18 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-020` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移すと決めた**
（TODO-018）。**まだ実装していない。** 移行先の仕様は
`docs/data-format.md` にある。既存データは移行ツールで一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-019. 移行元のテストデータを作る

見込み: main = Opus 5 / effort high、担当 = main + verifier

- [ ] 合成データを生成するスクリプトを書く
- [ ] 生成したデータを `tests/` 以下に置く
- [ ] 仕様書に挙げた特徴を全部再現できているか確かめる

（背景）

JSON Lines への移行ツール（TODO-020）を作るには、変換元のデータが要る。
手元の `~/ytsched/data` は空で、既存データは `tmp_test_data/` にあるが、
これは**個人の予定そのもの**で `.gitignore` の `tmp*` から外れない。
`tests/` へコピーすると git 管理下に入ってしまう。

そこで、**実データの構造だけを写して中身を架空にした合成データ**を作る。
リポジトリに個人の予定を入れず、移行ツールのテストに必要な網羅性は
保てる。

（再現する特徴）

`docs/data-format.md`「実データを調べて分かったこと」に挙げたものを
一通り含める。

- utf-8 のファイルと euc_jp のファイルの両方
- **どちらでも読めない 1 行を含むファイル**（他の行は euc_jp で読める）。
  移行が行ごとのデコードでないと落ちることを捕まえるため、これが要
- `&amp;#160;` のような二重エスケープ、`&nbsp;` `&gt;` `&lt;` `&quot;`、
  `<br />`、`<br />` 以外の HTML タグ
- `★` `(キャンセル` `(欠` `x` などで始まる `title`、全角括弧を含むもの
- 空の `title`、空のファイル、範囲外の時刻（`28:00`）
- `:-:` `HH:MM-:` `:-HH:MM` `HH:MM-HH:MM` の 4 通りの時刻欄
- UUID でない `sde_id`（13〜18 文字）、重複する `sde_id`
- `ToDo.cgi`（`type` が `□` で始まる行）
- 移行の対象外のファイル（`{日}-backup.cgi`、`{日}.cgi.bak`）

（決めること）

置き場所を `tests/data/` にするか、別の名前にするか。既存のテストが
使っているディレクトリ構成に合わせて決める。

（担当を分ける理由）

作るのはデータと生成スクリプトだけなので、実装は main でよい。ただし
**「仕様書に挙げた特徴を全部再現できているか」は試せる**ので、確認は
verifier に分ける。挙動や分岐が変わる項目ではないので reviewer は
入れない。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

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
