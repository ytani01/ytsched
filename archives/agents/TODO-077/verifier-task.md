# TODO-077 verifier への依頼

TODO-077（`fix` で `.bak` が中間状態に上書きされるのを直す）の実装が
終わった。実際に動くかを確かめてほしい。

- 実装の報告: `archives/agents/TODO-077/implementer-report.md`
- 依頼書: `archives/agents/TODO-077/implementer-task.md`
- 背景: `TODO.md` の TODO-077、`docs/design-review.md` の B

## 確かめてほしいこと

1. `mise run lint`（`ruff format` / `ruff check` / `basedpyright` /
   `mypy`）と `uv run pytest tests` を走らせ、結果をそのまま報告する
2. **本題の再現。** 一時ディレクトリを `--datadir` にしてアプリを起動し、
   同じ日に 2 件（A・B）の予定を作る。B を `fix`（修正）する POST を
   送り、次の 2 つを実際にファイルの中身で確かめる
   - `.bak` に **A・B の両方**が、修正前の内容で残っている
   - 本体のファイルに A と、修正後の B が入っている
3. **直す前は本当に壊れていたか。** `git stash` で変更を退避して同じ
   手順を踏み、`.bak` が A だけになることを確かめる（確かめたら
   `git stash pop` で戻すこと）。**戻し忘れないこと**
4. 日付を変える `fix`（`orig_date` と `date` が違う）でも壊れていないか。
   元の日のファイルから消え、新しい日のファイルに入り、**どちらの
   `.bak` も 1 回分だけ**であること
5. `add` / `del` / `update` が今までどおり保存されること（HTTP 経由）
6. ToDo（`ToDo.jsonl`）の追加・削除・完了も保存されること

## 決まりごと

- **コードを直さない。** 見つけたことは報告するだけ
- 報告は `archives/agents/TODO-077/verifier-report.md` に書く。
  返事は 5 行以内
- **`mise run upgradeproject` は走らせない**
- `~/ytsched/data` の実データを触らない。必ず `--datadir` で一時ディレクトリを指定する
