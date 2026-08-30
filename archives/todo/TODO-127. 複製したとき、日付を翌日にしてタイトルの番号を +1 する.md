# TODO-127. 複製したとき、日付を翌日にしてタイトルの番号を +1 する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Sonnet 5 / effort default | main + verifier |
| 消費 | output 26,143 / cache_creation 162,691 / 概算 $1.9 |
|      | main 88% + verifier 12%（料金の割合） |

verifier の報告は
[archives/agents/TODO-127/verifier-report.md](../agents/TODO-127/verifier-report.md)
にある。

## きっかけ

編集画面の複製ボタン（`cmd=add`）は、フォームの内容をそのまま新しい
`sde_id` で追加するだけだった。同じ予定を連番で作り足すとき、日付と
タイトルの番号を毎回手で直していた。

## やったこと

- `src/ytsched/sched_update.py`
  - `SchedUpdater.TITLE_COUNTER_RE` — タイトル末尾の半角 `#` + 半角数字
    にマッチする正規表現（`r"#([0-9]+)$"`）。`#` の前の空白の有無は
    問わない
  - `SchedUpdater.increment_title_counter()` — マッチしなければ
    `None`、マッチすれば `#N+1` にした文字列を返す
  - `exec_update()` の `cmd == "add"` 分岐で、`increment_title_counter()`
    がマッチしたときだけ、タイトルを置き換え、かつ ToDo でなければ
    日付を 1 日進める。マッチしなければ何も変えない（今までどおり）。
    ToDo は日付（締切）を動かさず、タイトルの番号だけ +1 する
- `tests/test_web.py`（`TestUpdate`）にテストを 4 件追加
  - タイトル末尾が `#N` の複製は翌日・`#N+1` になる
  - `#N` 以外は日付・タイトルとも変わらない
  - ToDo の複製は日付を動かさず番号だけ +1 になる
  - 半角 `#` + 全角数字（例 `#１`）は対象外のまま変わらない

### verifier が見つけたこと

最初の実装は `TITLE_COUNTER_RE = re.compile(r"#(\d+)$")` としていた。
Python の `\d` は全角数字（Unicode の Nd カテゴリ）にもマッチするため、
半角 `#` + 全角数字（`会議 #１` のような表記）まで複製対象になり、
置き換え後に全角数字が半角へ化けてしまう不具合があった。「全角は対象
外」という要件は満たしていたが、「`#` は半角・数字は全角」という
中間の組み合わせを見落としていた。`[0-9]` に絞って直し、再現するテスト
（`test_add_with_fullwidth_digit_counter_keeps_date_and_title`）を足した。

`cmd=add` は編集画面では複製ボタン（`{% if not new_flag %}`）だけが
使う経路で、新規作成フォームには出ない、という確認も verifier に
してもらった。テストヘルパー `add_sde()` が `cmd=add` を新規作成の
代わりに流用している点と、今回の機能が衝突しないことも確かめている。

## テスト

- `uv run ruff format --check src tests` / `uv run ruff check src tests` /
  `uv run basedpyright src tests tools`: 緑
- `uv run pytest`: 547 passed
