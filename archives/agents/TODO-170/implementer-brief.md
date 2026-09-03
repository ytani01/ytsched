# TODO-170 implementer への依頼

## 目的

全データを走査して、UUID でない `sde_id` を UUID へ振り直すサブコマンド
`ytsched fix-id` を作る。仕様は `TODO.md` の TODO-170 の節を読むこと
（そちらが正。ここには要点だけ書く）。

## やること

1. `src/ytsched/fix_id.py`（新規）
   - `holiday.py` の `HolidayStat` / `HolidayRegistrar` の作りに倣う
     （dataclass の集計と、`main()` を持つクラス）
   - 対象は `{topdir}/{年}/{月}/{日}.jsonl` と `{topdir}/ToDo.jsonl` のみ。
     **`trash.jsonl` は対象外**。`.cgi` / `.bak` も対象外
   - 1 行ずつ JSON として読み、`sde_id` が UUID の形でなければ
     `SchedDataEnt.new_id()` で差し替えて書き戻す。
     **他のキーは値も並び順も変えない**（`json.loads` の結果は挿入順を
     保つので、`sde_id` だけ代入して `json.dumps(..., ensure_ascii=False)`
     で書き直せばよい）
   - UUID の判定は正規表現。小文字ハイフン付き 36 文字
     （`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`）。
     `uuid.UUID()` でのパースは、波括弧付きやハイフン無しも通してしまう
     ので使わない
   - **JSON として読めない行、`sde_id` キーが無い行、`sde_id` が文字列で
     ない行は、そのまま書き戻して数える**（`SchedDataFile.load()` が
     読めない行を `skipped_lines` に残すのと同じ考え方）。行は捨てない
   - ファイルの読み書きはバイト列で行い、行は `\n` で切る
     （`str.splitlines()` は U+2028 でも切ってしまう。
     `docs/data-format.md` と `SchedDataFile.split_lines()` を見ること）
   - 書き戻しは**同じディレクトリの一時ファイルへ書いてから
     `os.replace()`**。バックアップ（`.bak`）は作らない
   - **書き換える行が 1 行も無いファイルは書かない**（更新時刻を動かさない）
   - `--dry-run` のときは 1 バイトも書かず、件数だけ数える
   - 集計して返すもの: 走査したファイル数、書き換えたファイル数、
     書き換えた行数、元から UUID だった行数、読めなかった（そのまま
     残した）行数
2. `src/ytsched/__main__.py`
   - サブコマンド `fix-id` を足す。`migrate` の定義をそのまま手本にする
     （`--datadir` / `--dry-run` / `click_common_opts` / `_is_debug`）
   - `help` は日本語で、何をするコマンドかと「元に戻せないので
     `--dry-run` で確かめてから実行すること」を書く
3. `tests/test_fix_id.py`（新規）
   - `tests/test_holiday.py` と `tests/test_migrate.py` の書き方に倣う。
     `tmp_path` に一時的なデータディレクトリを作って確かめる
   - 見ること: 非 UUID が UUID に変わる / 元から UUID の行は変わらない /
     `sde_id` 以外のキーが値も並び順も変わらない / 同じ ID が重複して
     いても行ごとに別の UUID になる / JSON として読めない行が残る /
     `trash.jsonl` が変わらない / `--dry-run` で 1 バイトも変わらない /
     変更の無いファイルの更新時刻が動かない / 書き換えた後のファイルを
     `SchedDataFile` が読める
   - CLI を `click.testing.CliRunner` で叩くテストも 1 つ入れる
     （既存のテストに前例があればそれに倣う）

## やらないこと

- 文書（`docs/`・`README.md`）は writer が別に書く。**触らない**
- `TODO.md` と `archives/` は main が書く。触らない
- `ytsched.py` / `trash.py` / ハンドラ類は変えない
- **`~/ytsched/data` の実データには絶対に触らない。** 動作確認は
  `--datadir` に一時ディレクトリを指定すること

## 完了条件

- `uv run ruff format` / `uv run ruff check` / `uv run basedpyright` /
  `uv run pytest` が通る（`mise run fmt` / `lint` / `typecheck` / `test`
  でもよい。`mise run upgradeproject` は走らせない）
- 一時ディレクトリに作ったデータで `ytsched fix-id --dry-run` と
  本番実行の両方を自分でも叩いて、件数と結果を確かめる

## 報告

`archives/agents/TODO-170/implementer-report.md` に書く。返事は 5 行以内。
