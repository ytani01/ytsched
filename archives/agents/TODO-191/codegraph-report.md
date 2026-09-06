# TODO-191 CodeGraph 調査報告 — ゴミ箱からの復元経路

## 1. 経路（ハンドラ→データファイル）

- ルーティング: `src/ytsched/webapp.py` が `TrashHandler`
  （`src/ytsched/trash_handler.py:16`）を URL に登録する
  （`from .trash_handler import TrashHandler` を import し、
  `WebServer.__init__` 内でハンドラ一覧に組み込む）。
- 復元は POST で入る。`TrashHandler.post()`
  （`src/ytsched/trash_handler.py:76-83`）が `cmd=restore` のとき
  `self._restore()` を呼ぶ（79行目）。
- `TrashHandler._restore()`（`trash_handler.py:114-135`）が本体:
  1. `sde_id` / `trashed_at` を引数から取得し、
     `self._trash().get(sde_id, trashed_at)`
     （`TrashFile.get`, `src/ytsched/trash.py:170`）でゴミ箱
     （`trash.jsonl`）から該当エントリを読み出す（116-119行目）。
  2. `self._restore_id(sde)`（`trash_handler.py:85-112`）で
     新しい `sde_id` を決める（後述の 2. 参照）。
  3. 読み出した内容から新しい `SchedDataEnt` を組み立て、
     タイトルの先頭に `(復活)` を付ける（123-132行目）。
  4. `self._sd.add_sde(restored.date, restored)` を呼ぶ（133行目）。
     `self._sd` は `SchedData`（`src/ytsched/ytsched.py:830`〜）で、
     その `add_sde(date, sde)`（`ytsched.py:1051-1071`）は
     `self.get_sdf(date)` でその日の `SchedDataFile` を取得・
     キャッシュし、`sdf.add_sde(sde)`
     （`SchedDataFile.add_sde`, `ytsched.py:781-790`。
     `self.sde.append(sde)` してソートし直すだけ）でメモリ上の
     一覧に足す。実ファイルへはまだ書かない。足した
     `SchedDataFile` を `self._dirty_sdf[date]` に記録する
     （1071行目）。
  5. `self._sd.save()`（134行目）を呼ぶ。`SchedData.save()`
     （`ytsched.py:1107-1121`）が `self._dirty_sdf.values()` を
     1 つずつ `sdf.save()`（`SchedDataFile.save`,
     `ytsched.py:738-779`）で保存する。ここが実際にファイルへ
     書き込む箇所: 既存ファイルが空でなければ `.bak` へ退避
     （762-766行目）、`self.sde` の各行を JSON 化して該当日の
     日次データファイルへ上書き保存（770-779行目）。復元先は
     `restored.date`（＝元の予定の `date`）に対応する日次ファイル
     （`SchedDataFile.date2path()` が決めるパス）。
  6. 最後に `self.redirect(...)` でその週の画面へ戻す（135行目）。

まとめると、経路は
`TrashHandler.post()`（trash_handler.py:76）→
`TrashHandler._restore()`（trash_handler.py:114）→
`SchedData.add_sde()`（ytsched.py:1051、メモリに追加のみ）→
`SchedData.save()`（ytsched.py:1107）→
`SchedDataFile.save()`（ytsched.py:738、実ファイルへ書き込み）。

## 2. `sde_id` の版番号の扱い

`TrashHandler._restore_id(sde)`（`trash_handler.py:85-112`）が決める。

- 元の `sde_id` が新形式（`{UUID}-{版}`）なら
  `SchedDataEnt.split_id()` で UUID と版に分解し、UUID を引き継ぐ。
- 版は、ゴミ箱（`TrashFile.max_version(uuid_part)`,
  `trash.py:181`）・現在のデータ全体（`SchedData.max_version`,
  `ytsched.py:1123` 付近）・そして元エントリ自身の版、の 3 つの
  最大値を取り、その **+1** にする（106-112行目のコメントどおり、
  日付を跨いだ編集で生きている予定を見落とさないよう、ゴミ箱と
  日次ファイル・`ToDo.jsonl` を含むデータディレクトリ全体を
  走査する。TODO-171 の対応）。
- 元の `sde_id` が新形式でなければ `_restore_id()` は `None` を返し、
  呼び出し元では `SchedDataEnt(restored_id, ...)` のコンストラクタが
  `sde_id` が空なら `SchedDataEnt.new_id()` で新しい UUID を発行する
  （`ytsched.py:104-105` 付近、`self.sde_id = sde_id if sde_id else
  SchedDataEnt.new_id()`）。

つまり、同じ UUID を保ったまま版番号だけ 1 つ繰り上げるのが基本の
挙動で、旧形式の ID だけ例外的に新しい UUID・版 1 から採番される。

## 3. 復元後のゴミ箱側エントリ

`TrashHandler._restore()`（`trash_handler.py:114-135`）を読む限り、
`self._trash().get(...)` で読み出すだけで、`TrashFile.delete()`
（`trash.py:243`）や `delete_many()`（`trash.py:197`）は
**呼んでいない**。つまり **復元してもゴミ箱（`trash.jsonl`）側の
エントリはそのまま残る**。ゴミ箱から消すのは `_delete_many()`
（`trash_handler.py:137-161`、`cmd=delete_many` の一括削除）だけで、
復元操作とは独立している。

同じ UUID から複数回復元すると、`TrashHandler.get()`
（`trash_handler.py:53-74`）の一覧表示は
`SchedDataEnt.id_uuid(entry.sde.sde_id)` で UUID ごとにグループ化
している（58-62行目）ので、同じ元エントリを何度でも選んで復元
できる状態のまま残る。

## 日本語クエリの空振り

3 回空振りした後、英語に切り替えた。

1. 「ゴミ箱から予定を復元する経路」 → No relevant code found
2. 「ゴミ箱 復元」 → No relevant code found
3. 「削除した予定を元に戻す処理」 → No relevant code found
4. "restore from trash handler" → ヒット（`TrashHandler` 一式が
   見つかった）。以降は "SchedData.add_sde and SchedData.save
   method implementation" 等、シンボル名寄りの英語クエリで
   `SchedData.save()`（ytsched.py:1107）の本体まで辿った。

## 確信が持てなかった点

- `SchedData.save()`（`ytsched.py:1107-1121`）の本体は、日本語・
  英語の自然文クエリでは何度も同じ抜粋（`SchedDataFile.save()` の
  738 行目付近）が返ってきて出てこず、最終的に
  `codegraph node "SchedData.save"` というシンボル直指定で
  ようやく確認できた（1107 行目）。`SchedDataFile.save`
  （738行目）と `SchedData.save`（1107行目）は同名メソッドで、
  自然文検索では前者ばかりヒットしやすい点に注意。
- ゴミ箱側エントリが残ることは `_restore()` の本体に `delete` 系の
  呼び出しが無いことから消去法で確認した。「意図的に残す仕様」で
  あることを裏付けるコメント（docstring 等）は見当たらなかった
  ので、コードの見た目からの結論。
