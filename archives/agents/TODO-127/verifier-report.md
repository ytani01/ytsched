# TODO-127 verifier 報告

## 1. lint / 型チェック

- `uv run ruff format --check src tests` → ○（35 files already formatted）
- `uv run ruff check src tests` → ○（All checks passed!）
- `uv run basedpyright src tests tools` → ○（0 errors, 0 warnings, 0 notes）

## 2. テスト

- `uv run pytest -q` → ○ **546 passed in 125.88s**（依頼どおりの件数）

## 3. ロジックの確認（`src/ytsched/sched_update.py`）

`TITLE_COUNTER_RE = re.compile(r"#(\d+)$")` と `increment_title_counter()`、
`exec_update()` の `cmd == "add"` 分岐を読んだ。

- 末尾が半角 `#` + 半角数字 → `title[:m.start(1)] + str(n)` で番号だけ
  +1 になる。○
- 末尾が `#N` 以外 → `increment_title_counter()` が `None` を返し、`title`・
  `date` とも変更なし。○
- ToDo（`SchedDataEnt.type_is_todo(sde_type)` が真）→ タイトルの番号は
  +1 になるが、`date` はそのまま（`not type_is_todo(...)` の条件で
  ガードされている）。○
- 全角 `＃１`（`＃` も全角）→ 正規表現の `#` はコードポイントが異なるため
  マッチせず、対象外。○（`python3 -c` で実測: `re.search(r'#(\d+)$', '会議＃１')`
  は `None`）

### 気づいたこと（バグではないが報告）

**半角 `#` + 全角数字（例: `会議 #１`）はマッチしてしまう。**
Python の `\d`（`re.UNICODE` が既定）は全角数字（Unicode の Nd カテゴリ）にも
マッチするため、`TITLE_COUNTER_RE.search("会議#１")` は
`match='#１'` にヒットする。依頼書・TODO-127 本文が挙げている「全角対象外」の
例は `＃１`（`＃` も全角）のみで、「`#` は半角・数字だけ全角」という中間の
組み合わせには言及が無い。実装のままだと、この組み合わせも複製対象になり、
かつ `str(n)` で置換後は全角数字が半角数字に化ける（例: `会議#１` →
`会議#2`）。実用上のタイトルで半角 `#` に全角数字を続ける表記がどこまで
あるかは不明だが、意図した仕様（半角のみ対象）とは食い違うので報告する。
直すかどうかは判断してください。

```
$ python3 -c "
import re
p = re.compile(r'#(\d+)\$')
print(p.search('会議#１'))
"
<re.Match object; span=(2, 4), match='#１'>
```

### `cmd=add` の呼び出し元（新規作成との衝突は無いか）

`edit.html` を見ると、`cmd=add` ボタン（複製アイコン）は
`{% if not new_flag %}` で囲まれており、**既存の予定を開いた編集画面
だけに表示される**（`edit_handler.py` の `new_flag` は `sde_id` が
空のときだけ真）。新規作成フォーム（`new_flag=True`、タイトル初期値は
空文字）には `cmd=add` ボタンが無く、`update`/`fix`/`del` のみが出る。
つまり **UI からの通常操作では、`cmd=add` は複製にしか使われず、
「真に新規作成でタイトルがたまたま `#1` で終わる」経路は無い**。
ただし API は `cmd=add` を直接 POST できるので、フォームを介さずに
新規追加として `sde_id=""` かつタイトル末尾が `#N` のリクエストを送れば、
このケースでも日付・番号が動く。これは実装の仕様（複製かどうかを
区別するフラグが無く、`cmd=add` すべてに一律適用）どおりの挙動で、
バグとは考えない（依頼の懸念点への回答として記載）。

テストヘルパー `add_sde()`（デフォルト title `"新しい予定"`）や
既存の `test_add`（title `"会議1"` 等）はいずれも末尾が `#N` 形式では
ないため、今回の変更で既存テストの前提と矛盾しない。実際 pytest は
546 件全通過。

## 4. 追加テストの確認

- `test_add_duplicate_increments_title_and_date`: `write_data()` で
  実データを直接書いてから、実際に HTTP POST（`post_body`、モック無し）
  で `cmd=add` を送り、翌日のファイルを実際に読んでタイトルを確認して
  いる。実装を経由した end-to-end のテストで、誤魔化しは無い。
- `test_add_without_counter_keeps_date_and_title`: 既存の `add_sde()`
  ヘルパーを使い、日付・タイトルが変わらないことを確認。妥当。
- `test_add_todo_duplicate_keeps_date`: ToDo ファイルへ直接書き込んでから
  複製し、タイトルの集合・日付の集合を確認。ToDo のケースをカバーして
  いて妥当。ただし、複製前の「元の #1 のエントリがそのまま残っている
  こと」を個別に検証せず、`titles == {"...#1", "...#2"}` のように集合で
  まとめて確認している点はやや粗いが、意図した仕様は検証できている。

## 総括

見つかった問題は 1 点（半角 `#` + 全角数字がマッチしてしまう、報告の
「気づいたこと」参照）。それ以外は仕様どおり動作し、lint・型チェック・
テスト（546 件）はすべて通過。
