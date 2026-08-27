# TODO-088 verifier への依頼

TODO-088 で、一覧の組み立てを `MainHandler.load_sched()` から
`src/ytsched/sched_load.py`（`SchedLoader`）へ出し、**通常モード
（`load_week()`）と検索モード（`search()`）に分けた**。

**挙動は一切変えていないはず**（返す HTML が今までと同じ）なので、
それを確かめてほしい。設計は
`archives/agents/TODO-088/implementer-request.md`、実装の報告は
`implementer-report.md` にある。

## 1. いつもの確認

- `uv run pytest -q` — 件数を報告（475 件通っていたはず）
- `mise run lint` — 通るか

## 2. 変更の前後で HTML が同じか（**これが本命**）

「テストが通る」だけでは、検索の打ち切り条件の写し間違いは出てこない。
**変更前のコードを別に動かして、同じ URL の HTML を突き合わせてほしい。**

手順の例（このとおりでなくてよいが、同じことを確かめること）:

1. 変更前のコードを `git worktree` で取り出す

   ```
   git worktree add /tmp/<一時>/ytsched-old HEAD
   ```

   （HEAD は TODO-087 のコミット。作業ツリーの変更は含まれない）
2. データディレクトリを 2 つ作る。**中身は同じにすること**
   （片方を作ってから `cp -r` で複製する。`\cp` のようにバックスラッシュを
   付けるか `command cp` を使う。エイリアスで確認を聞かれて止まる）
   - 日付がばらけた予定を 10 件以上と、ToDo を数件入れる。
     **同じ語を含む予定を、数百日離れた日にも置く**（検索の打ち切りを
     見るため）。`ytsched webapp` に POST して作ってもよいし、
     `.jsonl` を直接書いてもよい（形式は `docs/data-format.md`）
3. 変更前・変更後をそれぞれ別のポートで起動する
   （`uv run ytsched webapp --port <番号> --datadir <それぞれのディレクトリ>`）
4. 同じ URL を両方から取って `diff` を取る。少なくとも次を見ること
   - `GET /ytsched/?date=<平日>` と `?date=<日曜>` と `?date=<月曜>`
   - 検索: `POST` で `search_str=<当たる語>` を送ったあとの表示
     （`search_n` を 1・5・100 と変えて 3 通り）
   - 検索: `search_str=<どこにも当たらない語>`
   - ToDo の日数を変えたとき（`todo_days=-1` と `todo_days=365`）
   - 絞り込み `filter_str` を付けたとき、`!` 始まり（否定）のとき
   - **`data-monday` と `data-offset` の出方**（通常モードでは週の数だけ
     出て、検索モードでは `data-monday` が 1 つも出ないこと）
5. **差が出たら、その URL と diff の該当部分を報告に貼る。**
   `version` や日付など、実行のたびに変わるものの差は除いてよい

## 3. サーバのログ

例外・トレースバックが出ていないこと。

## 既知（報告しなくてよい）

- `mk_todo_by_date()` が `search_match()` を二重にかけていること
  （TODO-094）
- `SEARCH_MODE_DAYS` / `SEARCH_MODE_MAX_DAYS` の名前（TODO-094）
- `sd=self._sd` をテンプレートへ渡していること（TODO-091）

終わったら `git worktree remove` で片付けること。
報告は `archives/agents/TODO-088/verifier-report.md`。返事は 5 行以内。
