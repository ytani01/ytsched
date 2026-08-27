# TODO-088. 一覧の組み立てと検索を分ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 26,925 / cache_creation 310,551 / 概算 $6.0 |
|      | main 57% + implementer 24% + verifier 10% + reviewer 5% + wording 4%（料金の割合） |

分担の理由と各担当の報告は
[`archives/agents/TODO-088/`](../agents/TODO-088/README.md) にある。

## きっかけ

基本設計のレビュー（2026-08-27）の B。

`load_sched()`（112 行）が「月曜から 7 日ぶんを並べる」と「最大 1,825 日
さかのぼって、当たった日だけ残す」という別々のことを、**同じ `while` の
中で分岐しながら**やっていた。検索かどうかの分岐は `get()` に 1 か所、
`load_sched()` に 4 か所。

## やったこと

`src/ytsched/sched_load.py`（376 行）を新しく作り、一覧の組み立てを
そちらへ移した。`sched_update.py`（TODO-087）と同じく、**tornado を
import しない。**

- **`load_week()`（通常モード）と `search()`（検索モード）に分けた。**
  共通なのは 1 日ぶんを集める `_load_day()` だけ。分岐を写すのでは
  なく、それぞれのモードに要る道だけを書いた
- **条件を 2 つに分けた。** 表示の条件は `SchedLoadCond`、検索だけが
  使う検索語と目標件数は `SchedSearchCond`。`SchedLoadCond` から
  `search_re` / `search_n` に加えて、**どこからも読まれていなかった
  `todo_sde`** も外し、フィールドは 8 個から 5 個になった。
  `search_mode` プロパティも消した（どちらのメソッドを呼ぶかで表す）
- `get()` から週の組み立てを `mk_weeks()` へ出した

`main_handler.py` は 1,215 行から 973 行になった（TODO-087 の前は
1,391 行）。

### 検索モードの `weeks` の `monday`

分ける前は、検索モードの `weeks` は `monday` を `None` にしていて、
テンプレートが `{% if w['monday'] %}` で `data-monday` を出すかどうかを
決めていた。**検索でも実際の月曜（`date` を含む週）を入れるようにし、
テンプレート側の条件を `{% if not search_mode %}` に変えた。**

出てくる HTML は変わらない（通常モードの `monday` は必ず値があるので
今までも必ず出ていた。検索モードでは今までも出なかった）。`weeks` の
値の型が揃うので、**TODO-091 で dataclass にするときに、`None` に
なりうる型を持ち込まずに済む。**

## テスト

挙動を変えていないので、テストの期待値は変えていない。`load_todo()` →
`mk_todo_by_date()` → `load_sched()` を直に呼んでいた
`tests/test_main_handler.py` の `call_load_sched()` を、`SchedLoader`
経由（検索語の有無で `search()` / `load_week()` を呼び分ける）に
書き換えた。

- 475 件すべて通過。`ruff format` / `ruff check` / `basedpyright` /
  `mypy` すべて問題なし
- **verifier が、変更前のコードを `git worktree` で取り出して別の
  ポートで動かし、同じデータで HTML を突き合わせた。** 通常表示
  （平日・月曜・日曜）、検索（目標件数 1 / 5 / 100、当たらない語）、
  ToDo の日数、絞り込みと否定、`data-monday` / `data-offset` の
  出方まで見て、**差は無し**
- reviewer が、分ける前の `load_sched()` と 1 行ずつ突き合わせた。
  打ち切りの判定順、1 件も当たらない日の扱い、ToDo だけ当たった日、
  並び順、`todo_today_sde` を足す条件のすべてで一致。指摘は無し

## main が直したもの

implementer が型を絞り込むために入れた `assert search_re is not None`
を、`if search_re is not None:` で分岐する形に直した。`search_mode` と
同じ条件なので分岐の意味は変わらず、`src/` で唯一の `assert` を
持ち込まずに済む。
