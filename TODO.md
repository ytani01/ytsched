# TODO

**残っている項目: TODO-027, TODO-028, TODO-029, TODO-030**
これまでに 26 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-031` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にある。既存データは
`ytsched migrate` で一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-027. 不正な入力で 500 になるのをやめる

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer

- [ ] 数字・日付にならない値を既定値へ落とし、ログに警告を出す
- [ ] 不正な値を `Conf.cgi` へ保存しない
- [ ] ゴールデンマスターテストを新しい挙動に合わせて書き直す

（背景）

TODO-024 で決めた方針にもとづく。対象は `search_n`・`todo_days`・
`year`/`month`/`day`・`date`・`cur_day` の 5 か所。**`search_n=abc` や
`todo_days=abc` は `Conf.cgi` に残るので、一度踏むとトップページも
開けなくなる**（実測は
[TODO-024](archives/todo/TODO-024.%20リファクタリングで見つかった%208%20件の扱い.md)
の表）。読むときに既定値へ落とすだけでは直らないので、保存の側も
直す必要がある。

扱い方は TODO-012（不正な正規表現はその条件を無視して全件を出す）に
揃える。

（気をつけること）

- TODO-021 で足したゴールデンマスターテストが落ちる。挙動を変えたの
  だから当然で、書き直してよい

---

## TODO-028. リファクタリングで見つかった残り 5 件を直す

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer

- [ ] `filter_str` を空で送れば解除できるようにする
- [ ] `filter_str` を小文字にしてから `Conf.cgi` へ保存する
- [ ] `detail` の `〆` 行に残る余分な空白を直す
- [ ] 使われていない `MainHandler.COOKIE_TODO_DAYS` を消す
- [ ] 検索モードの 1825 日スキャンを、挙動を変えずに速くする

（背景）

TODO-024 で決めた方針にもとづく。独立した 5 件の寄せ集めで、どれも
`main_handler.py` に集まっている。`sde_align` が毎回 `top` に戻る件は
**今のままでよい**と決めた（TODO-024）。

1825 日スキャンは、さかのぼる範囲（`SEARCH_MODE_MAX_DAYS`）は変えず、
ファイルの無い日は開きに行かずに飛ばす。1 件も当たらないうちだけ 1825 日
さかのぼるのは古い予定を拾うための設計なので、範囲そのものは縮めない。

（気をつけること）

- `filter_str` の 2 件は挙動が変わるので、ゴールデンマスターテストが
  落ちる。書き直してよい

---

## TODO-029. コードレビューで見つかった 3 件を直す

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer

- [ ] 移行のときに行末の `\r` を落とす
- [ ] 編集画面の `orig_date` を、その行が入っているファイルの日付にする
- [ ] 検索・フィルタ文字列を `normalize()` に通す

（背景）

TODO-021 までの変更（`src/` 全体）を `/code-review` にかけて出た 3 件。
どれも JSON Lines へ移したときに入ったもので、テストは 330 件とも
通っている。

**1. 移行のときの `\r`。** `SchedDataFile.split_lines()` は `b"\n"` だけで
切って `\r` を落とさない。CRLF の旧 `.cgi` を `ytsched migrate` にかけると、
各行の最後のフィールド（`detail`）の末尾に `\r` が入ったまま `.jsonl` へ
書かれる（実測で `"detail": "議題\n・進捗\r"`）。旧形式ではテキストモードの
`readlines()` と `text2htmlstr()` の `replace("\r", "")` で消えていたので、
移行で新しく入る。表示にも残る（`sde.html` の `rstrip('\n')` では `\r` が
取れず、`white-space: pre-wrap` で末尾に空行が出る）。
`docs/data-format.md` にある 53460 行／53628 件の一致確認は、両側とも
同じ `\r` 付きを見ていたので捕まらなかった。

**2. `date` が食い違う行。** `load_line()` は、行の `date` がファイル名から
決まる日付と違っても、警告を出して行側の日付を残す。すると `edit.html` が
`orig_date` にその日付を出すので、`fix` したときに `cmd_del()` が別の日の
ファイルを見に行って空振りし（それでも `save()` は走ってそのファイルと
`.bak` を書き直す）、`cmd_add()` が表示していた日のファイルへ複製を書く。
結果は「表示が古いまま」ではなく重複。実データには該当する行は無い。

**3. 検索・フィルタ文字列の正規化。** 照合される側の
`SchedDataEnt.search_str()` は `normalize()`（全角括弧を半角にして小文字化）
を通るのに、入力側は `.lower()` しかしていない。`会議（重要）` と表示されて
いる予定を `（重要）` で検索しても当たらない（実測）。
`docs/data-format.md` は「これは旧形式でも同じだった」と書いているが、
旧形式は保存する文字列そのものが半角になっていたので、見えているとおりに
打てば当たった。今は表示と検索が食い違う。

（決めたこと）

- **2 は、読み込みの方針（行の `date` を信じる）は変えず、編集画面が渡す
  `orig_date` だけを「その行が実際に入っているファイルの日付」にする。**
  `del` が空振りしなくなり、重複しなくなる。表示上の日付との食い違いは
  そのまま残る
- **3 は入力側も `normalize()` に通す。** 全角括弧は半角になるので、
  正規表現のキャプチャグループとして解釈される。`（重要）` は
  `(重要)` として当たる。全角括弧をリテラルとして書きたいときは `\(` と
  打つ必要がある。`docs/data-format.md` の当該の段落も書き直す

（気をつけること）

- 1 を直しても、**すでに移行して `\r` が入ってしまったデータは直らない**。
  実データを移行済みなら、手当てが要るかを着手時に確かめる
- 2・3 は挙動が変わるので、TODO-021 で足したゴールデンマスターテストが
  落ちるかもしれない。落ちたら書き直してよい

---

## TODO-030. ドキュメント ``docs/Developer.md`` などの整備

ドキュメントの役割を明確に分け、重複を避ける。

- README.md: ytsched利用者用
- docs/Developer.md: ytsched開発者用。技術スタック、開発ツールなどの説明。コードについては、src/README.md
- docs/data-format.md: データフォーマット詳細
- src/README.md: ソースコードの構成、クラス構造など、全体的な説明。個別のコード内のdocstringsでわかるような詳細は説明しない。
- CLAUDE.md: claude 用。通常、人間は読まない(たまに、確認することはある)。

関係するもの同士リンクをつけて、相互参照出来るようにする。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

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
