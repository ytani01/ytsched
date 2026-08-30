# TODO-085 implementer 報告

## 変更・作成したファイル

- `src/ytsched/trash.py`（新規） — `TrashFile` クラス。`topdir` を受け取り、
  `add(sde)` で `trash.jsonl` へ 1 行追記するだけ。`SchedDataEnt` を
  実行時にインポートすると `ytsched.py` と循環インポートになるため、
  `from __future__ import annotations` を付けて型注釈だけの参照にした
  （実行時 import は `TYPE_CHECKING` の下）
- `src/ytsched/ytsched.py` — `TrashFile` を import。`SchedData.__init__()`
  で 1 つ持たせ、`SchedData.del_sde()` で `sdf.del_sde()` を呼ぶ**前**に
  `sdf.get_sde(sde_id)` で対象を取り、見つかればその場で
  `self._trash.add(sde)` を呼ぶ。見つからなければ何もしない。その場で
  追記する理由（余分に残る失敗のほうが害が小さい）をコメントに残した
- `tests/test_trash.py`（新規） — `TrashFile` 単体（1 行の形・キーの並び・
  親ディレクトリ作成・`~` 展開）と、`SchedData.del_sde()` 経由の統合テスト
  （削除で 1 行増える／未知の ID では触らない／2 回消すと 2 行で順序が
  保たれる／`SchedUpdater.cmd_del()`→`cmd_add()` で fix を再現し、編集前の
  内容が入る）を追加
- `docs/data-format.md` — 「ゴミ箱（TODO-085）」の節を「バックアップ」の
  前に追加。置き場所・1 行の形・追記のみで `.bak` を作らないこと・
  復活 UI は TODO-086 の範囲であることを書いた
- `src/README.md` — モジュール一覧に `trash.py` の説明を 1 行追加

## 確かめたこと

- `uv run python -c "..."` で `add_sde` → `save` → `del_sde` を直接実行し、
  `trash.jsonl` に 1 行、未知の ID では増えないことを目で確認
- `mise run fmt` / `typecheck` / `lint` / `test` を通し、525 件全て pass
  （`mise run upgradeproject` は走らせていない）

## 判断したこと

- `trash.py` から `SchedDataEnt` を型注釈だけで参照するために
  `from __future__ import annotations` を追加した。ほかのモジュールに
  前例が無いが、循環インポートを避けるための最小限の変更として妥当と
  判断した
- fix（編集）のテストは `SchedUpdater.cmd_del()` → `cmd_add()` を直接
  呼んで再現した（tornado を経由しない層のテスト）。`sched_update.py` は
  対象範囲外だが、呼び出すだけで変更はしていない

## 残したもの

- ゴミ箱の読み出し・復活 UI は TODO-086 の範囲なので未着手
