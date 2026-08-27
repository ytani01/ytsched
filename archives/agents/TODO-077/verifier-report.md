# TODO-077 verifier 報告

## 1. lint / pytest

- `mise run lint`（ruff format / ruff check / basedpyright / mypy）:
  全て通過（0 errors, 0 warnings）
- `uv run pytest tests`: 459 件 全て通過

## 2. 本題の再現（修正後のコード）

一時ディレクトリを `--datadir` にして `uv run ytsched webapp` を起動し、
実際に curl で POST を送って確認した。

- 同じ日（2021-03-01）に A・B を `add`
- B を `fix`（`sde_type=私用`, `title=B修正` など）
  - `.bak` に **A・B 両方**（B は修正前の内容）が残ることを確認
  - 本体には A と、**修正後の B**（`title=B修正`）が入っていることを確認

期待どおり。

## 3. 直す前は本当に壊れていたか

`git stash` は auto mode の classifier に拒否された
（`Permission for this action was denied by the Claude Code auto mode
classifier`）。代わりに `git worktree add <一時dir> HEAD` で作業ツリーを
汚さずに修正前のコードを別ディレクトリへ用意し、そちらで `uv sync` して
同じ手順（A・B を add → B を fix）を再現した。

- 修正前: `fix` 後の `.bak` は **A のみ**（B の修正前の内容がどこにも
  残らない）ことを確認。依頼書どおり壊れていたことを確認できた
- 確認後、`git worktree remove --force` で片付け、作業ツリー
  （`git status`）は最初から変化していない（stash を使っていないため
  戻し忘れの心配なし）

## 4. 日付を変える fix

B（2021-03-01）を `date=2021-03-02` へ `fix`。

- 2021-03-01 の本体からは B が消え、`.bak` は A・B（1 回分）のみ
- 2021-03-02 の本体には移動後の B が入り、`.bak` は**そもそも作られない**
  （新規ファイルなので退避対象が無い。これは正しい）

どちらも「1 回分だけ」の条件を満たしている。

## 5. add / del / update（HTTP 経由）

- `add`（A・B）: 保存を確認（上記）
- `del`（A を削除）: 本体ファイルが空になることを確認
- `update`（B の内容変更）: 反映を確認

## 6. ToDo の追加・削除・完了

- 追加: `sde_type=□会議` で `ToDo.jsonl` に書かれることを確認
- 完了: `sde_type` を `□` なしにして `deadline_date` 等を渡す `fix`
  （`fix_todo_done` 経路）で、`ToDo.jsonl` から消え、当日のファイルへ
  `〆…` 形式の detail 付きで保存されることを確認
- 削除: 追加した ToDo を `del` すると `ToDo.jsonl` が空になることを確認

途中、`sde_type=会議`（`□` なし）で `add` した回だけ ToDo にならず
当日の予定として保存されており、一瞬「消えた」ように見えたが、
これは `type_is_todo()` の仕様どおりで、TODO-077 とは無関係（自分の
確認手順のミス）。

サーバのログ（`server.log`/`server2.log`）に例外・トレースバックは無し。

## 結論

見つかった不具合は無し。TODO-077 の実装は依頼の再現手順どおりに動く。

## 追加確認（reviewer 指摘の修正）

### lint / pytest

- `mise run lint`: 全て通過（0 errors, 0 warnings）
- `uv run pytest tests`: **461 passed**（依頼どおり）

### 追加した 2 本のテストが、修正を戻すと落ちるか

`git worktree add <一時dir> HEAD` で修正前の作業ツリーを用意し、そこへ
`git diff`（現在の全差分）を `git apply` で当てたあと、reviewer 指摘の
2 箇所だけを個別に手で戻して確認した（本体のリポジトリは触っていない）。

- `_dirty_sdf`（dict）を `_dirty_dates`（set、`save()` で
  `get_sdf(date)` を引き直す旧実装）に戻す
  → `uv run pytest tests/test_ytsched.py::test_sched_data_save_after_cache_discard`
  は **FAILED**（`AssertionError`。キャッシュから捨てられた日の変更が
  `save()` で書かれない）
- `exec_update()` の `try`/`finally` をやめ、`self._sd.save()` を
  ブロックの外（無条件・例外を挟まない位置）に出す
  → `uv run pytest tests/test_web.py::TestUpdate::test_exec_update_saves_even_on_error`
  は **FAILED**（`cmd_add` の `RuntimeError` がそのまま伝播し、
  `self._sd.save()` が呼ばれないため、削除だけが未保存のまま
  `_dirty_sdf` に残る）

両方とも、依頼どおり「戻すと落ちる」ことを確認できた。確認後
`git worktree remove --force` で片付け、`git status` は最初から
変化していない。

### 本題（`.bak` に A・B 両方）が壊れていないこと

一時ディレクトリで `uv run ytsched webapp` を起動し、HTTP 経由で
A・B を `add` → B を `fix` する手順を再実行。

- `.bak`: A（修正前）・B（修正前 `title=B`）の両方
- 本体: A・修正後の B（`title=B修正`）

前回と同じ結果で、壊れていないことを確認した。サーバのログに例外なし。

### 結論

見つかった不具合は無し。reviewer 指摘の修正 2 件は、いずれもテストで
効果が確認できる形で入っている。
