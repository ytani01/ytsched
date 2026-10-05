# TODO

**残っている項目: TODO-219。** これまでに 219 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-221` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-219. 使われていないコードと重複を整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Haiku 4.5、定型の実行） |

- [ ] `TrashFile` の `entries()`・`count()`・`delete_many()` に 3 回ある
      1 行の読み取り（`json.loads` → `trashed_at` の型確認 → 4 種の例外）を
      1 つの関数にまとめる（`src/ytsched/trash.py`）
- [ ] テストからしか呼ばれないメソッドを消す: `SchedDataEnt.get_date()`・
      `SchedDataEnt.set_date()`・`SchedData.get_keys()`（`src/ytsched/ytsched.py`）。
      テストの該当箇所も消す
- [ ] `src/ytsched/ytsched.py` のコメントアウトしたログの行（9 行）を消す
- [ ] `TrashFile.delete()`（`delete_many()` の互換用ラッパ、テストからしか
      呼ばれない）を消し、テストを `delete_many()` に書き換える
- [ ] `click_common_opts()` の `use_h`・`use_d`・`use_v` を消す
      （どの呼び出しも既定値のまま。`src/ytsched/click_utils.py`）

コード全体を無駄な処理・過剰な実装の観点で見直して見つけたもの。
**挙動は変えない。** 壊れた行を飛ばす・残す扱い（`entries()`/`count()` は
警告して飛ばす、`delete_many()` は元のバイトのまま残す）は保つ。

`mylog.py` の未使用部分は、他のプロジェクトとそろえるため残す（TODO-220）。

対象を探すコマンド:
`rg -n -w -e get_date -e set_date -e get_keys -e 'delete' -e use_h -e use_d -e use_v -e '# self\.__log' src tests`
（`get_date` は `MainBinder.get_date()` と同名なので、`SchedDataEnt` のほうだけが対象）

分担: `trash.py` の読み取りの整理で分岐が動くので reviewer を入れる。
reviewer → verifier の順に回す。

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
