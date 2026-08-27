# TODO-080 verifier への依頼

TODO-080（キャッシュがファイルの更新に追随しないのを直す）の実装が
終わった。実際に動くかを確かめてほしい。

- 実装の報告: `archives/agents/TODO-080/implementer-report.md`
- 依頼書: `archives/agents/TODO-080/implementer-task.md`
- 背景: `TODO.md` の TODO-080、`docs/design-review.md` の C

**`DEF_CACHE_SIZE` は、実装者の 1500 から main が 2000 へ変えた**
（検索モードが最大 1825 日ぶん開きうるため）。

## 確かめてほしいこと

1. `mise run lint` と `uv run pytest tests` を走らせ、結果をそのまま報告する
2. **本題。サーバを動かしたまま、外からデータファイルを書き換えて、
   画面に反映されるか。** 一時ディレクトリを `--datadir` にして
   `ytsched webapp` を起動し、
   - まずブラウザか `curl` で、ある日の予定を表示させる（キャッシュに載る）
   - **サーバは止めずに**、その日の `.jsonl` をエディタや `sed` で書き換える
   - もう一度同じ URL を取り、書き換えた内容が出ること
   - 直す前（`git worktree add <一時dir> HEAD` で用意。`git stash` は
     auto mode に拒否されるので使わないこと）では**古い内容のまま**
     であることも確かめる
3. **ファイルを消したとき**に 500 にならないこと（同じ手順で、
   表示させたあとにファイルを消して、もう一度取る）
4. **無かった日のファイルを、サーバを動かしたまま作った**ときに
   読めること
5. 書き込み（`add` / `fix` / `del`）が今までどおり動くこと。
   `save()` の直後に無駄な読み直しが起きていないこと
   （`--debug` のログで `cache miss` や読み直しの行を見るとよい）
6. `ytsched migrate` を走らせたあと、サーバを再起動せずに新しい
   データが見えること（これがこの項目の元の動機）

## 決まりごと

- **コードを直さない。** 見つけたことは報告するだけ
- 報告は `archives/agents/TODO-080/verifier-report.md` に書く。返事は 5 行以内
- **`mise run upgradeproject` は走らせない**
- `~/ytsched/data` の実データを触らない。必ず `--datadir` を指定する
