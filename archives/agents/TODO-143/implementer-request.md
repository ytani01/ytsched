# TODO-143 implementer への依頼

## 目的

週間表示（`main.html`）のフッターにあるゴミ箱アイコンの横に、ゴミ箱の
件数を表示する。

## 対象範囲

- `src/ytsched/trash.py`: `TrashFile.count()` を足す
  - ゴミ箱ファイルの有効な行数を返す。`entries()` は `max_entries=100`
    で頭打ちなので件数には使えない
  - 壊れた行は `entries()` と同じ考え方で飛ばす（数に入れない）。
    ただし `SchedDataEnt.from_dict()` までは呼ばず、軽く済ませる
  - ファイルが無ければ 0
- `src/ytsched/main_handler.py`: `MainHandler.get()` の `render()` に
  `trash_count=` を渡す。`TrashFile` の作り方は
  `src/ytsched/trash_handler.py` の `_trash()` に倣う
  （`TrashFile(self._app_info.datadir)`）
- `src/ytsched/webroot/templates/main.html`: フッターのゴミ箱リンク
  （`<a class="my-btn" href="{{ url_prefix }}trash">` のあたり）で、
  アイコンの右に件数を出す。**0 件でも「0」を出す**
  - 見た目は周りのフッターに揃える。既存のクラス（`my-fs-small` など）を
    使い、新しい CSS は増やさない方向で。必要なら `my.css` に足してよいが
    最小限に
- テスト
  - `tests/test_trash.py`: `count()` の単体テスト（0 件、複数件、
    壊れた行が混ざったとき、100 件を超えるとき）
  - `tests/test_web.py`: 週間表示の HTML に件数が出ること
    （0 件のときと、1 件以上のとき）

## 完了条件

- 上記のコードとテストが入っている
- `uv run pytest` が通る
- `uv run ruff format` / `uv run ruff check` / `uv run basedpyright` /
  `uv run mypy` が通る

## 注意

- アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する
- `mise run upgradeproject` は走らせない

## 報告

`archives/agents/TODO-143/implementer-report.md` に、変更点・検証結果・
残る懸念を書く。返事は 5 行以内で。
