# TODO-087 verifier への依頼

TODO-087 で、更新の実行（`cmd=add/fix/update/del`）を `MainHandler` から
`src/ytsched/sched_update.py`（`SchedUpdater` / `SchedUpdateForm`）へ
移した。**挙動は一切変えていないはず**なので、それを確かめてほしい。

設計は `archives/agents/TODO-087/implementer-request.md`、実装の報告は
`implementer-report.md` にある。

## やってほしい確認

1. `uv run pytest -q` — 件数を報告（475 件通っていたはず）
2. `mise run lint` — 通るか
3. **アプリを起動して、更新の 4 つの経路を実際に叩く**
   （`--datadir` は必ず一時ディレクトリ。実データを触らない）
   - `cmd=add` で予定を足す → 302 で `?date=...` へ飛ぶ。
     データファイル（JSON Lines）に 1 行増えているか
   - `cmd=fix` で直す → 内容が入れ替わっているか（行が増えていないか）
   - `cmd=update` → 302 の飛び先が `edit/` の URL になっているか
     （`date` / `sde_id` / `todo_flag` が付く）
   - `cmd=del` → 行が消えているか
4. **エラーの経路**
   - `date=2026-13-45` のような読めない日付を `cmd=add` に付けたら
     **400**（書き込みが起きる前に断る）。そのときデータファイルが
     できていないこと
   - `time_start=99:99` でも 400
5. サーバのログに例外・トレースバックが出ていないこと

## 既知（報告しなくてよい）

- `main_handler.py` の `load_sched()` まわりが長いこと（TODO-088 の範囲）
- テストの docstring に `cmd_del()` などの旧い言い回しが残っていること

報告は `archives/agents/TODO-087/verifier-report.md`。返事は 5 行以内。
