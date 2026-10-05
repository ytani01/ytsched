# TODO-219 の依頼

開始時刻: 2026-10-05T11:43:25+09:00

## 目的

使われていないコードと重複を消す。**挙動は変えない。**

## 対象（TODO.md の TODO-219 の 5 項目）

1. `src/ytsched/trash.py` の `TrashFile.entries()`・`count()`・`delete_many()` に
   3 回ある 1 行の読み取り（`json.loads` → `data["trashed_at"]` の型確認 →
   4 種の例外）を 1 つの関数（モジュール内の private 関数か staticmethod）にまとめる。
   **保つもの:** 壊れた行の扱い。`entries()`/`count()` は警告して飛ばす
   （警告の文言・回数もそのまま）、`delete_many()` は元のバイトのまま残す。
   捕まえる例外の種類も今と同じにする。
2. `SchedDataEnt.get_date()`・`SchedDataEnt.set_date()`・`SchedData.get_keys()`
   （`src/ytsched/ytsched.py`）を消し、テストの該当箇所も消す。
   `MainBinder.get_date()` は別物なので触らない。テストが消えて見なくなる
   挙動が他のテストで見られているかを報告に書く。
3. `src/ytsched/ytsched.py` のコメントアウトしたログの行（`# self.__log` で始まる
   もの。複数行にまたがるものは続きの行も）を消す。
4. `TrashFile.delete()` を消し、テストを `delete_many()` に書き換える
   （戻り値は件数になるので `== 0` / `== 1` で比べる）。
5. `src/ytsched/click_utils.py` の `click_common_opts()` から `use_h`・`use_d`・`use_v`
   を消し、それぞれの分岐の中身を常に実行する形にする。

対象を探すコマンド:
`rg -n -w -e get_date -e set_date -e get_keys -e delete -e use_h -e use_d -e use_v -e '# self\.__log' src tests docs`
（`docs/` や `src/README.md` に消したメソッドの記述があれば直す）

## 完了条件

- `mise run fmt`・`mise run lint`・`mise run typecheck`・`mise run test` が通る
- 実装できたら `TODO.md` の TODO-219 のチェックボックスを入れる

## 報告

`archives/agents/TODO-219/implementer-report.md` に、変更点・検証結果・残る懸念
だけを書く。返事は「終わったか・報告ファイルのパス・判断が要る点」だけ。

## 追記（着手後に変わった前提）

項目 5 は取りやめ。`click_utils.py` は `mylog.py` と同じく他のプロジェクトと
そろえるため書き換え禁止（利用者の指示）。
