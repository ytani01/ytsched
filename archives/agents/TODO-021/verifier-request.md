# TODO-021 verifier への依頼

## この項目の性質

TODO-021 は**リファクタリング**で、**挙動は一切変えていない**はず。
だからあなたの仕事は「新機能が動くか」ではなく、
**「変える前と同じに動くか」**を確かめること。

## 確かめてほしいこと

### 1. テストと lint・型チェック

順に走らせて、結果を**実際の数字ごと**報告する。

```sh
uv run ruff format --line-length 78 src tests
uv run ruff check --fix --extend-select I src tests
uv run basedpyright src tests
uv run mypy src tests
uv run pytest tests
```

- `ruff` の 2 つが**書き換えたかどうか**（`git diff --stat` で見る）
- pytest の件数。**すべて通ること**

### 2. 既存テストが書き換えられていないこと

**これがこの項目でいちばん大事な確認。**

`git diff` で `tests/` を見る。TODO-021 では
「現状の挙動を押さえるテスト」を**足した**だけで、
**既存のテストは 1 行も書き換えていない**はず。

- リファクタリング側のコミット前差分で、`tests/` の**既存の行**が
  変わっていないか
- 変わっていたら、**どのテストの、どの行が、どう変わったか**を報告する。
  これは「挙動が変わった印」なので、見つけたら最優先で報告

（着手前のベースラインは `290 passed`。テストは足されているので
件数は増えている。増えた分がどれかは
`archives/agents/TODO-021/implementer1-report.md` にある）

### 3. アプリが実際に動くか

`--datadir` には**必ず一時ディレクトリ**を指定する。

- `run_in_background` で `uv run ytsched webapp --datadir <一時dir> --port <空きポート>`
  を起動し、数秒待って curl で HTTP ステータスを見る
- 一覧画面の HTML を実際に取得し、テンプレートが展開されている
  （`{{ }}` や `{%` が生で残っていない）ことを目で見る
- **リファクタリングで触った経路を、実際に叩く。** 最低限:
  - フィルタ（`filter_str=`）を付けた一覧
  - 検索（`search_str=`）を付けた一覧。`search_n=1` のような
    小さい値でも
  - **不正な正規表現**（例 `filter_str=[`）。TODO-012 のとおり、
    その条件を無視して全件が出て、入力欄には元の文字列が残ること
  - `year` / `month` / `day` を付けた一覧
  - 予定の追加（`cmd=add`）→ 修正（`cmd=fix`）→ 削除（`cmd=del`）
  - ToDo（`sde_type` の先頭が `□`）の追加と、**その完了**
    （`deadline_date` を付けて `sde_type` を ToDo でないものにする）
- サーバのログに例外やトレースバックが出ていないこと
- 終わったら `pgrep -f` で PID を確かめてから kill する

### 4. `ytsched x_data1` が動くか

`__main__.py` の `DataFileApp.end()` を消してある。
`uv run ytsched x_data1 <年> <月> <日> --datadir <一時dir>` が
これまでどおり動く（例外を出さず、データを出力する）ことを見る。

## 報告

`archives/agents/TODO-021/verifier-report.md` に書く。

- 確認した項目ごとに ○ / ×、**実際に得られた値**
  （HTTP ステータス、テスト件数、出力の要点）
- 使ったコマンドそのもの（main が再現できるように）
- 見つかった不具合。ファイル名・行・症状
- **既存テストの書き換えがあれば、最優先で**

---

## 追記（main より）

- 着手前のベースラインは **290 passed**。ゴールデンマスターテストが +40 されて
  **330 passed** が今の期待値
- リファクタリングの中身は
  `archives/agents/TODO-021/implementer2-report.md` にある。先に読むこと
- **`tests/` の差分は `tests/test_main_handler.py`（新規）と
  `tests/test_handler.py` への 1 件追記だけ**のはず。
  それ以外の既存テストが変わっていたら最優先で報告
