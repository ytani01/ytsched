# TODO-144 verifier への依頼

## 目的

TODO-144（週間表示フッターのゴミ箱件数の見た目を直す）の変更が実際に
効いているかを確かめる。**コードは直さない。** 見つけたことは報告する。

## 変更の内容（main が実装済み）

未コミットの差分（`git diff`）。

- `src/ytsched/webroot/static/css/my.css`: `.my-bar a.my-btn` に
  `text-decoration: none` を足した（件数の下線を消すため）
- `src/ytsched/webroot/templates/main.html`: ゴミ箱リンク内の件数から
  カッコを外し、クラスを `my-fs-xx-small` → `my-fs-medium` にした
- `tests/test_web.py`: 上記に合わせて 2 件のテストの正規表現を直した

## 確かめること

- `uv run pytest` が通る
- `uv run ruff format --check` / `uv run ruff check` /
  `uv run basedpyright` / `uv run mypy` が通る
  （`ruff format --check` は `archives/todo/*.md` が既存で unformatted と
  出る。今回の変更と無関係なので区別して報告する）
- **アプリを起動して、週間表示フッターの HTML を curl で取り確かめる。**
  `--datadir` に一時ディレクトリを指定すること（実データを汚さない）
  - ゴミ箱リンク内の件数にカッコが無いこと
  - 件数の span が `my-fs-medium` になっていること
  - `trash.jsonl` に数件足したあと、件数がその数になること
- **フッター上段の `cache_size` の表示（`(N)`）が変わっていないこと。**
  今回はゴミ箱の件数だけを変える約束なので、ここが変わっていたら報告する
- 配信される CSS（`curl` で `static/css/my.css`）に
  `text-decoration: none` が入っていること

## 報告

`archives/agents/TODO-144/verifier-report.md` に、実行したコマンドと
その結果、見つけた問題を書く。返事は 5 行以内。
