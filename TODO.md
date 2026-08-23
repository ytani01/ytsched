# TODO

**残っている項目: TODO-031, TODO-032, TODO-034**
これまでに 31 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-035` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にある。既存データは
`ytsched migrate` で一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-031. 文書に Mermaid の図を入れる

見込み: main = Opus 5 / effort medium、担当 = writer + verifier + wording

- [ ] どの図をどこに入れるかを決める
- [ ] Mermaid のソースを書いて、文書に埋め込む
- [ ] GitHub で実際に図として表示されるか確かめる

（背景）

TODO-030 で文書を 6 つに分けたが、どれも文章と箇条書きだけで、
クラス同士の関係やモジュールの依存は読まないと分からない。

**Mermaid にする。** Markdown の中に ```mermaid のブロックを書くだけで
GitHub がそのまま図として表示する。ソースが数行で済み、コードが変わった
ときに直しやすい。SVG を直に書く手もあるが、座標を自分で決めることになり、
git の差分を読んでも意味が分からない。`docs/javascript-scroll.svg` は
画面の座標そのものを説明する図なので直書きのままでよく、**今回のような
関係を示す図とは別の用途**。

（決めること）

**どの図を作るか。着手するときに利用者と決める。** 候補:

1. `src/README.md` — `SchedDataEnt` / `SchedDataFile` / `SchedData` の
   積み上がり（`classDiagram`）
2. `src/README.md` — `HandlerBase` と `MainHandler` / `EditHandler` の
   継承、`WebServer` からの組み立て（`classDiagram` か `graph`）
3. `src/README.md` — リクエストが来てから画面が出るまでの流れ
   （`sequenceDiagram`）
4. `docs/data-format.md` — 旧形式から JSON Lines への移行の手順（`graph`）
5. `tests/README.md` — `helpers.py` とテストファイルの関係（`graph`）

全部入れると多すぎるので、**絞る**。

（気をつけること）

- **色を決め打ちにしない。** GitHub にも Artifact にもダークテーマが
  あるので、背景色を固定すると片方で読めなくなる
- 図を入れても、文章のほうを消さない。図だけでは分からない「なぜそう
  なっているか」は文章側にある
- `mermaid-cli`（`mmdc`）で SVG に書き出す案は**採らない**。依存が増える
  わりに、GitHub がそのまま表示できる以上の利点が無い。必要になったら
  そのとき考える

---

## TODO-032. 改良案

今、考えられる改良案をまとめる。
簡単に修正出来るものはまとめて修正する。
難しいものは個別の項目として分離する。

改良案
- Conf.cgi を JSON 形式にする。

---

## TODO-034. `orig_date` と `expanduser()` の紛らわしいところを片付ける

見込み: main = Sonnet 5 / effort medium、担当 = verifier のみ（実装は main）

- [ ] `sde.html` が送っている `orig_date` を消す
- [ ] `date2path()` の `expanduser()` を 1 か所に寄せる

（背景）

どちらも**今はバグではない**が、読む人に誤解させる。TODO-029 の
reviewer と TODO-028 の reviewer から、それぞれ据え置かれていたもの。

**1. `sde.html` の `orig_date`。** `sde.html` が `orig_date` を組み立てて
`doPost()` のパラメータに載せているが、受け取る `EditHandler.get()` は
`orig_date` を読んでいない（TODO-029 より前からそう）。ToDo のときは
`'{{ None }}'` が文字列 `"None"` として送られている。TODO-029 で
「`orig_date` は handler が決める」と方針が定まったので、送る側の
死んだコードが残っているのは紛らわしい。

**2. `date2path()` の `expanduser()`。** `SchedDataFile.__init__` と
`SchedData.sdf_exists()` の 2 か所に分かれている。`topdir` を省いて
`date2path()` を単独で呼ぶと `~` が展開されないまま渡る道が開いている
（現状、そう呼んでいる箇所は無い）。

（気をつけること）

- 1 は、消す前に `sde.html` の `doPost()` を通る経路をすべて洗うこと。
  受け取る側が読んでいないことの確認だけでは足りない
- 2 は展開する場所を寄せるだけで、`~` の展開そのものの挙動は変えない

---

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-029.** コードレビューで見つかった 3 件を直す](archives/todo/TODO-029.%20コードレビューで見つかった%203%20件を直す.md)
- [**TODO-028.** リファクタリングで見つかった残り 5 件を直す](archives/todo/TODO-028.%20リファクタリングで見つかった残り%205%20件を直す.md)
- [**TODO-027.** 不正な入力で 500 になるのをやめる](archives/todo/TODO-027.%20不正な入力で%20500%20になるのをやめる.md)
- [**TODO-033.** URL_PREFIX の改名に追随できていない箇所を直す](archives/todo/TODO-033.%20URL_PREFIX%20の改名に追随できていない箇所を直す.md)
- [**TODO-030.** ドキュメントの役割を分ける](archives/todo/TODO-030.%20ドキュメントの役割を分ける.md)
- [**TODO-023.** mise.toml の見直し](archives/todo/TODO-023.%20mise.toml%20の見直し.md)
- [**TODO-024.** リファクタリングで見つかった 8 件の扱い](archives/todo/TODO-024.%20リファクタリングで見つかった%208%20件の扱い.md)
- [**TODO-026.** 文書の確認の担当と hook を作る](archives/todo/TODO-026.%20文書の確認の担当と%20hook%20を作る.md)
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
