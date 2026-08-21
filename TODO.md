# TODO

**残っている項目: TODO-023・TODO-024。**
これまでに 23 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-026` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にある。既存データは
`ytsched migrate` で一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-023 mise.tomlの見直し

mise.tomlを使いやすいようにしたい。
現在の内容は、全部書き直してもいいし、不要なら削除してもいい。


---

## TODO-024. リファクタリングで見つかった 8 件の扱いを決める

見込み: main = Sonnet 5 / effort medium、担当 = main のみ

- [ ] 500 になる 2 件の直し方を決める
- [ ] 画面の使い勝手 3 件を、実際に使いながら決める
- [ ] 些細な 2 件と、速度の 1 件を、直すか見送るか決める

（背景）

TODO-021 のリファクタリングの途中で、挙動がおかしそうな箇所が 8 件
見つかった。TODO-021 は**挙動を変えない**項目だったので直さず、
**現状のままテストに書き留めてある**。8 件の中身と、それぞれを押さえて
いるテスト名は
[`archives/todo/TODO-021. リファクタリング（挙動は変えない）.md`](archives/todo/TODO-021.%20リファクタリング（挙動は変えない）.md)
の「見つけたが直さなかった挙動」にある。

（決めること）

性質が 3 つに分かれるので、決め方も分ける。

- **入力を検証していなくて 500 になる 2 件** — `search_n=`（空）と、
  `year`/`month`/`day` に数字でない値や `day=0`。**選択肢の判断は要らない**
  （500 を返すのが正しいはずがない）。直し方だけの話
- **画面の使い勝手 3 件** — 空の `filter_str` で絞り込みを解除できない、
  `Conf.cgi` には `ABC` のまま保存されて画面には `abc` と出る、
  `sde_align` だけ保存されず毎回 `top` に戻る。**どう動いてほしいかは
  使っている本人にしか分からない。しばらく使ってから答えを出す**
- **些細な 2 件と、速度の 1 件** — `〆` 行の余分な空白、未使用の
  `MainHandler.COOKIE_TODO_DAYS`、検索で 1 件も当たらないときに
  1825 日ぶんスキャンすること。ついでに直すか、見送るか

（気をつけること）

- **この項目は決めるだけ。** 直すのは別の項目にする
- 直すときは、TODO-021 で足したゴールデンマスターテストが**落ちる**。
  それは挙動を変えたのだから当然で、そのときはテストを書き直してよい
  （TODO-021 の中では書き換えてはいけなかった、という違い）

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-025.** 文書の確認を分ける仕組みを決める](archives/todo/TODO-025.%20文書の確認を分ける仕組みを決める.md)
- [**TODO-022.** 軽量な担当 runner を作る](archives/todo/TODO-022.%20軽量な担当%20runner%20を作る.md)
- [**TODO-021.** リファクタリング（挙動は変えない）](archives/todo/TODO-021.%20リファクタリング（挙動は変えない）.md)
- [**TODO-020.** JSON Lines への移行ツールと、読み書きの実装](archives/todo/TODO-020.%20JSON%20Lines%20への移行ツールと、読み書きの実装.md)
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
