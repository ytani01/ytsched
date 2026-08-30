# TODO-118 verifier 報告

対象: `docs/obsidian-format-review.md`。コード・実データは読むのみで、
一切書き換えていない。

## 1. 1 章の表

コードの場所（`date2path()` L429、`load()` L464、`load_line()` L584、
`save()` L636、`get_sdf()` L866、`is_stale()` L521、`sdf_exists()` L812、
`sdf_has_sde()` L835、`get_sortkey()` L322、`TrashFile`
`src/ytsched/trash.py` L33）は**すべて合っている**。`to_dict()` の 8 キー
（`sde_id` `date` `time_start` `time_end` `type` `title` `place` `detail`）
も一致。

行数: `ytsched.py` 1020 / `migrate.py` 431 / `sched_load.py` 484 —
**すべて `wc -l` と一致**。

テスト数「全体で 446 個」: `grep -c '^\s*def test_'` を全 `tests/*.py` に
かけると確かに合計 446（`test_ytsched.py` 112、`test_web.py` 129 も一致）。
ただし **`uv run pytest --collect-only -q` で実際に集まるテストは
536 個**（`test_migrate.py` は 48 def から 73 件、`test_ytsched.py` は
112 def から 177 件に増える。`@pytest.mark.parametrize` の展開分）。
「テストは全体で 446 個ある」は def の数としては正しいが、実際に
`pytest` を実行して得られる件数（536）とは違う。読み手が「pytest を
回すと 446 件通る」と早合点しないよう、"def の数" と書くか注記した方が
よいと考える（判断は main）。

## 2. 2 章の数字

`~/ytsched/data` を Python で数え直した（読み取りのみ）。

- 日ごとのファイル 6737（空 181）/ 予定 13415 件 / ToDo 9 件 /
  日付範囲 1934-03-15〜2030-01-30 / データのある日 6556 /
  平均 2.0・最大 10・1 件だけの日 2716 — **すべて一致**
- `title` が空 1149、禁止文字 938、Obsidian 記号 641、3 つのどれか
  2691（20.1%）— **一致**（「空」は空文字列だけでなく空白のみの
  1 件も含めて初めて 1149 になる。空文字列のみだと 1148 なので、
  報告書の定義どおりに数えると合う）
- 置換後の同日名前衝突 171 組・372 件 — **一致**（`{HHMM}-` を
  付けない、タイトルだけの衝突として数えると合う）
- `sde_id` 重複 8 種・最大 3 件、`detail` 改行 4734、前後空白 2200、
  `#` 始まり 18、`---` だけの行 9、U+2028 1 件 — **すべて一致**

## 3. 5 章（挙動）

- 5-1: `is_stale()` は `(st_mtime, st_size)` を比較（L521-546）。
  `save()` はキャッシュ全件を書き直す（L636-671）。`sdf_exists()` /
  `sdf_has_sde()` はどちらもファイルを開かず `is_file()` /
  `stat().st_size` のみ見る（L812-860）— **合っている**
- 5-2: `load()` の末尾は `sorted(out, key=...)`（L516）。Python の
  `sorted()` は安定ソート — **合っている**
- 5-3: `docs/data-format.md` 171 行に「保存する文字列は入力された
  まま変えない」の文言そのものがある。`base.html` 42 行目が
  `{% autoescape None %}` のまま — **合っている**
- 5-6: `save()` は `pathname.exists() and stat().st_size > 0` の
  ときだけ `.bak` へ退避（L659-663）— **合っている**
- 5-7: `skipped_lines` の書き戻しは `save()` 内 L671 にある。
  空行は `load()` 側で `skipped_lines` に入れない（L510-514）
  ので書き戻されない — **合っている**

## 4. 6 章の見積もりの根拠

- `.jsonl` に触れているテストファイルは 6 つ
  （`test_browser.py` `test_trash.py` `test_ytsched.py`
  `test_main_handler.py` `test_migrate.py` `test_web.py`）— **一致**
- 箇所数「80」: `grep -o '\.jsonl' tests/*.py | wc -l` で数え直すと
  **76**（内訳: test_browser 1 / test_trash 9 / test_ytsched 16 /
  test_main_handler 4 / test_migrate 23 / test_web 23）。**80 とは
  合っていない**。数え方（`grep -c` で行数か、`.py` 以外のファイルも
  含めるか等）を変えても 76 にしかならず、80 に一致する数え方は
  見つけられなかった
- `README.md` `src/README.md` `tests/README.md` `docs/Developer.md`
  `docs/code-review.md` — 全ファイルにデータ形式（JSON Lines /
  `data-format.md` への言及）の記述を確認。**一致**
  （`tests/README.md` は `.jsonl` という文字列そのものは無いが、
  28 行目に「旧形式（タブ区切り `.cgi`）から JSON Lines への」という
  記述があり、データ形式に触れている）

## まとめ・main の判断が要る点

- 1 章の「テストは全体で 446 個ある」は def の数であり、実際に
  `pytest` で集まる件数（536）とは異なる。書き方を直すか判断してほしい
- 6 章の「`.jsonl` に触れているのは...80 か所」は実際には 76 か所。
  数字を直すか判断してほしい
- それ以外（1 章の表・場所・行数、2 章の全項目、5 章の 5 点）は
  すべてコード・実データと一致した
