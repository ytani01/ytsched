# TODO-171 implementer 報告

## 変更したファイル

- `src/ytsched/ytsched.py` — `SDE_ID_PATTERN`（`{UUID}-{版}`、版は
  `[1-9][0-9]*` でゼロ埋めしない）と、`split_id()`/`id_uuid()`/
  `id_version()`/`format_id()`/`next_id()` を `SchedDataEnt` に追加。
  `new_id()` は `format_id(uuid4, 1)` を返すよう変更
- `src/ytsched/sched_update.py` — `exec_update()` で `fix`/`update` の
  ときだけ、追加側の ID を `next_id()` で決めるようにした
- `src/ytsched/trash_handler.py` — `_restore_id()` を追加し、`_restore()`
  で使用。ゴミ箱と復活先の日付ファイルの両方の最大版 + 1 を UUID に
  付けて復活する（旧形式なら今までどおり新規 UUID）。`get()` の
  グループ化キーを `SchedDataEnt.id_uuid()` に変更
- `src/ytsched/trash.py` — `TrashEntry.version` プロパティ追加。
  `entries()` の絞り込みを版を除いた UUID 部分の一致に変更。`get()` に
  完全一致の確認を追加。`max_version(uuid_part)` を追加
- `src/ytsched/fix_id.py` — 全面書き換え。対象に `trash.jsonl` を追加、
  判定を 3 通り（既に新形式／UUID／それ以外）に、`FixIdStat.lines_already_uuid`
  を `lines_already_ok` に改名、docstring を書き直し
- `src/ytsched/webroot/templates/trash.html` — 版の表示を追加
- テスト: `tests/test_ytsched.py`・`tests/test_fix_id.py`・
  `tests/test_trash.py`・`tests/test_web.py` に、ID の分解・次版・
  ゼロ埋め非許容・ゴミ箱の絞り込み・`max_version()`・編集での版増加・
  復活でのバージョン引き継ぎ・グループ化・版表示のテストを追加、
  既存の一部（`test_update`、`test_fix_does_not_duplicate`、
  `test_update_redirects_to_edit`）を新しい ID 形式に合わせて修正
- 文書: `docs/data-format.md`（`sde_id` の行、ゴミ箱の節、実データ統計の節）、
  `docs/Install.md`、`docs/Developer.md`、`src/README.md` を新しい形式に
  合わせて書き直し

## 途中の仕様変更への対応

作業中に main から「版はゼロ埋めしない（`-1`, `-2`, … `-1000`）」への
変更指示を受けた。当初 `-001` 形式で実装・テストしていたものを、
正規表現（`[1-9][0-9]*`）・`format_id()`・`id_version()`・すべての
テストの期待値・文書の記述を `-1` 形式へ書き換えた。ゼロ埋めを新しい
形式と見なさないことを見るテストを `test_ytsched.py`・`test_fix_id.py`
に追加した。

## 確認したこと

- `mise run fmt` / `typecheck` / `lint` が通ることを確認
- `uv run pytest -q --ignore=tests/test_browser.py` で 595 件成功
- `tests/test_browser.py` はタイミング依存の 2 件
  （`test_home_button_double_tap_by_touch_returns_to_the_top_screen`）が
  この環境では時々失敗する（今回の変更と無関係、実測 500〜831ms かかり
  閾値 500/600ms を超える）。それ以外の 652 件（このテストを含めた全体
  654 件中）は成功することを確認済み

## 残る懸念・やらなかったこと

- 依頼どおり、実データへの `fix-id` の適用は行っていない（利用者が実行）
- `TODO.md` のチェックボックスは触っていない

## 2 回目の依頼: 復活の版の決め方の穴を塞ぐ

reviewer 指摘（`reviewer-report.md` の「1.」。日付を変える編集のあと、
生きている予定が別の日付ファイルへ移ると、`_restore_id()` がそれを
見落として復活した予定の `sde_id` が生きている予定と衝突する）を
`archives/agents/TODO-171/implementer-task-2.md` の指示どおりに直した。

- `src/ytsched/ytsched.py`
  - `SchedDataFile` に `TODO_FNAME`・`DAILY_GLOB` 定数と
    `list_all_files(topdir, include_trash=True)` を追加。
    `{年}/{月}/{日}.jsonl`・`ToDo.jsonl`・（`include_trash` なら）
    `trash.jsonl` を列挙する。`date2path()` は `TODO_FNAME` 定数を使うよう
    整理（挙動は変えていない）
  - `SchedData.max_version(uuid_part)` を追加。`list_all_files(...,
    include_trash=False)` で日々のファイルと `ToDo.jsonl` だけを走査し、
    UUID の文字列を含まない行は JSON として解析せずに飛ばす。`trash.jsonl`
    は見ない（`TrashFile.max_version()` が扱う分と重複させないため）
- `src/ytsched/fix_id.py` — `IdFixer` 独自の `DAILY_GLOB`/`TODO_FNAME`/
  `TRASH_FNAME` を削除し、`find_files()` は
  `SchedDataFile.list_all_files()` を呼ぶだけにした（列挙を 2 か所に
  書かない、という指示のとおり）。未使用になった `ClassVar` の import も外した
- `src/ytsched/trash_handler.py` — `_restore_id()` の「復活先の日付の
  ファイルを見る」ループを削除し、`self._trash().max_version(uuid_part)`
  と `self._sd.max_version(uuid_part)`（と元の版）の最大 + 1 にする形へ
  整理
- `docs/data-format.md` のゴミ箱の節を、全走査で版を決めることに合わせて
  書き直し
- テスト
  - `tests/test_ytsched.py` — `SchedDataFile.list_all_files()`（3 種の
    ファイルを拾うこと・`include_trash=False` で除くこと・無ければ
    スキップすること）と `SchedData.max_version()`（複数ファイルに
    散らばった同じ UUID から拾うこと・別の UUID を拾わないこと・
    `trash.jsonl` を見ないこと・該当が無ければ 0）を追加
  - `tests/test_web.py` に
    `test_restore_after_date_change_does_not_collide_with_live_entry`
    を追加。reviewer の再現手順（追加 → 日付を変えて編集 → 古い版を
    復活）をそのまま踏み、復活した `sde_id` が生きている予定ともゴミ箱の
    行とも重ならないことを見る
  - 既にあった `test_restore_keeps_uuid_and_increments_version` は変更なし
    のまま通ることを確認

### 確認したこと

- `mise run fmt` / `typecheck` / `lint` が通ることを確認
- `uv run pytest -q --ignore=tests/test_browser.py` で 603 件成功
  （直し前の 595 件 + 今回追加した 8 件）
- `tests/test_browser.py` は前回報告のとおり、今回の変更と無関係な
  タイミング依存の 2 件が時々失敗しうる状態のまま（未再実行）

### 判断が要る点

なし。依頼書の直し方（データディレクトリ全体走査、列挙の一本化、
`trash.jsonl` は `TrashFile.max_version()` に任せる）をそのまま実装した。
