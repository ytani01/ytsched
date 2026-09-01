# TODO-143 implementer 報告

## 変更したファイル

- `src/ytsched/trash.py`: `TrashFile.count()` を追加。ファイルが無ければ
  0。壊れた行（JSON デコード失敗、`trashed_at` が無い/文字列でない）は
  警告して飛ばす。`SchedDataEnt.from_dict()` は呼ばず、軽量なチェックに
  留めた。`entries()` と違い件数は頭打ちにしない
- `src/ytsched/main_handler.py`: `TrashFile` を import し、`get()` の
  `render()` に `trash_count=TrashFile(self._app_info.datadir).count()`
  を追加
- `src/ytsched/webroot/templates/main.html`: フッターのゴミ箱リンク内、
  アイコンの右に `<span class="my-fs-xx-small align-middle">
  ({{ trash_count }})</span>` を追加。既存クラスのみ使用、CSS は増やして
  いない
- `tests/test_trash.py`: `count()` の単体テストを 4 件追加（ファイル無し
  で 0、複数件、壊れた行が混ざる場合、100 件を超える場合）
- `tests/test_web.py`: `TrashFile` / `SchedDataEnt` を import し、
  `TestMainHandler` に週間表示のゴミ箱件数を見るテストを 2 件追加
  （0 件のとき、`TrashFile.add()` で 2 件追加したとき）

## 確認したこと

- `uv run pytest tests/test_trash.py tests/test_web.py -q` → 163 件通過
- `uv run pytest -q`（全体）→ 589 件通過
- `uv run ruff format` / `uv run ruff check` / `uv run basedpyright` /
  `uv run mypy` を対象ファイルに実行し、いずれも問題なし
  （`ruff check` で `re.S` を `re.DOTALL` に直す指摘のみあり、修正済み）

## 判断したこと

- `count()` の壊れた行の判定基準は、依頼どおり「JSON デコード失敗」と
  「`trashed_at` が無い/文字列でない」だけに留め、`sde_id` の型異常など
  `SchedDataEnt.from_dict()` でしか分からないものはチェックしていない
  （依頼の「軽く済ませる」という指示に沿った）
- 件数表示の見た目は、フッター上段の `cache_size` 表示
  （`my-fs-xx-small` の `span`）に揃えた

## 残る懸念

特になし。
