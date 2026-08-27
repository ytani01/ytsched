# TODO-088 の分担

`load_sched()` を「1 週ぶんを組み立てる」と「検索結果を集める」に分け、
一覧の組み立てを `sched_load.py` へ出した項目。

## なぜこの分担にしたか

見込みの段階で implementer + verifier + reviewer と決めてあり、
そのまま実施した。

- **implementer を分けた。** 新しいモジュール 1 本、`main_handler.py`、
  テンプレート、テストにまたがる。設計（2 つのメソッドへの分け方、
  条件を 2 つの dataclass に分けること、検索モードの `monday`）は
  main が決めて [implementer-request.md](implementer-request.md) に
  書き、implementer はそのとおりに作るだけにした
- **verifier を立てた。** ここは**テストが通っても安心できない**。
  分ける前は 1 つの `while` の中に分岐が 4 か所あり、写し間違えても
  多くの場合はテストを通ってしまう。そこで
  **変更前のコードを `git worktree` で取り出して別のポートで動かし、
  同じデータで HTML を突き合わせる**ことを依頼の本命にした
- **reviewer を入れた。** 「挙動は変えない」が前提の分割なので、
  打ち切りの判定順・並び順・ToDo を足す条件を、分ける前と 1 行ずつ
  突き合わせる担当が要る

## 依頼書と報告

- [implementer-request.md](implementer-request.md) /
  [implementer-report.md](implementer-report.md)
- [verifier-request.md](verifier-request.md) /
  [verifier-report.md](verifier-report.md)
- [reviewer-request.md](reviewer-request.md) /
  [reviewer-report.md](reviewer-report.md)

## 結果

- implementer — 依頼どおり。テストの期待値は変えずに済んだ。型を
  絞り込むために入れた `assert` 1 行だけを判断として報告してきた
  （main が `if` での分岐に直した）
- verifier — 475 件通過、lint すべて通過。HTML の突き合わせは
  **差ゼロ**（通常表示 3 通り、検索 4 通り、ToDo の日数 2 通り、
  絞り込み 2 通り）。途中、自分のデータの作り方の誤りで偽の差分を
  1 度出したが、作り直して解消したことも報告してきた
- reviewer — 指摘無し。依頼した 9 点すべてを分ける前と突き合わせて確認
