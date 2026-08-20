# implementer の報告（TODO-020）

JSON Lines への読み書きと、移行ツール `ytsched migrate` を実装した。

## 変更・作成したファイル

### 変更

- `src/ytsched/ytsched.py`
  - `htmlstr2text()` / `text2htmlstr()` を削除。代わりにモジュール
    レベルの `normalize()` を追加（全角括弧の半角化と小文字化だけ）
  - `SchedDataEnt`: `__init__()` は `detail` をそのまま持つ。
    `__str__()` の変換も外した。`to_dict()` / `from_dict()` /
    `dict_str()` / `dict_time()` / `time2str()` を追加。
    `mk_dataline()` は `json.dumps(..., ensure_ascii=False)` を返す。
    `is_important()` / `is_canceled()` / `get_sortkey()` /
    `search_str()` が `normalize()` を通す（`is_todo()` と
    `is_holiday()` は変えていない）
  - 定数 `DATE_FORMAT = "%Y-%m-%d"` / `TIME_FORMAT = "%H:%M"` を追加
  - `SchedDataFile`: `PATH_FORMAT` を `.jsonl`、`TODO_PATH_FORMAT` を
    `ToDo.jsonl` に。`ENCODE`（utf-8 → euc_jp のリスト）をやめ、
    `ENCODING = "utf-8"` にした。`load()` はバイナリで読んで
    `split(b"\n")` で切り、`split_lines()` / `load_line()` に分けた。
    `save()` は `.bak` の仕組みそのままで、書く中身だけが JSON になった
- `src/ytsched/__main__.py`
  - `migrate` サブコマンドを追加（`--datadir` / `--dry-run` /
    `--error-file` / `--debug`）
  - `x_data1` の `.replace("\t", "<tab>")` を外した
- `tests/test_ytsched.py`
  - `htmlstr2text` / `text2htmlstr` のテストを `normalize()` の
    テストに差し替え。データ行は `mk_dataline()` ヘルパで JSON を作る形に。
    壊れた行 5 種類、日付の食い違い、正規化（全角括弧）のテストを追加
- `tests/test_web.py`
  - 直書きしていたタブ区切りの行を `mk_dataline()`（JSON）に。
    ファイル名と、書き出した内容の検証を `.jsonl` / JSON に合わせた

### 作成

- `src/ytsched/migrate.py` — 移行ツールの本体
  （`decode_line()` / `split_lines()` / `split_fields()` /
  `conv_date()` / `conv_time()` / `html2text()` / `line2dict()` と
  `Migrator` クラス、結果を持つ `MigrateStat`）
- `tests/test_migrate.py` — 移行ツールのテスト（64 件）

`tests/data/old_format/` と `tests/make_test_data.py` は触っていない。
文書（`CLAUDE.md`、`docs/data-format.md`）も触っていない（writer の担当）。

## 自分で確かめたこと

- `mise run lint`（ruff / basedpyright / mypy）: すべて通った
- `mise run test`: **273 passed**（変更前は 209）
- `tests/data/old_format/` を一時ディレクトリへコピーして
  `ytsched migrate` を実行し、出力を目で確認した。
  ファイル 8・行 27・飛ばした行 0。依頼書が挙げた確認項目はすべて
  満たしている（`\xad` を含む行が U+FFFD 付きで残る、`&amp;#160;` が
  空白になる、`28:00` が `04:00` になる、`（重要）` が残る、U+2028 で
  行が割れない、6 列は空文字で埋め 8 列はタブでつなぎ直す、対象外の
  3 ファイルは変換されない）。同じことを `tests/test_migrate.py` に
  入れてある
- 変換したディレクトリで `uv run ytsched webapp --datadir <一時ディレクトリ>
  --port 10185` を起動して確認（実データは触っていない）:
  - 一覧が 200 で出る。`（重要）健康診断の申込` が全角のまま表示され、
    かつ太字（`is_important()` が真）になる
  - 追加（`cmd=add`）した予定で、`place` のタブと `detail` の
    改行・タブが JSON の `\t` `\n` として保存され、画面にも
    そのまま出る（旧形式ではタブが空白に潰れていた）
  - 壊れた行を仕込んだファイルで、5 種類とも
    「その行だけ飛ばして警告」になり、同じファイルの他の行は読めた。
    日付の食い違いは警告のうえ行の `date` が使われた

## 単独で決めた判断

1. **移行ツールを `src/ytsched/migrate.py` として分けた。**
   `__main__.py` には click のサブコマンド（`migrate`）だけを置き、
   変換の中身は関数に分けてテストしやすくした。既存の `DataFileApp`
   （`x_data1`）と同じく「CLI は薄く」の形に合わせている
2. **`--error-file` の既定は、カレントディレクトリの
   `migrate-errors.txt`。** データディレクトリの中に置くと移行対象の
   ディレクトリを汚すため外に出した。変換できない行が 0 件なら
   ファイルは作らない。書式は `{元のパス}:{行番号}\t{元の行}`
3. **既に `.jsonl` があるファイルは、警告して飛ばす**（上書きしない）。
   途中で失敗しても、もう一度実行すれば残りだけが変換される。
   `--force` のような上書きの手段は用意していない
4. **`--dry-run` では `.jsonl` もエラーファイルも書かない**（件数だけ出す）
5. **新形式を読むときの時刻は `datetime.time.fromisoformat()` で読み、
   読めなければ警告して `None` にする。**「時を 24、分を 60 で割った
   余りにする」は仕様書では移行ツール（手順 4）の話なので、読み込み側では
   やっていない。移行後のファイルに範囲外の時刻は残らない。
   これに伴い、旧テスト `test_load_hour_and_minute_are_normalized` は
   移行ツール側のテスト（`test_conv_time` の `28:00-:` →`04:00`）に移した
6. **`sde_id` が欠けている行は、新しい UUID を発行して読む**
   （`SchedDataEnt.__init__` の既存の振る舞いのまま）。`date` のように
   行を飛ばす扱いにはしていない。仕様書が必須にしているのは `date` だけ
7. **`from_dict()` は `date` が無い／読めないときに `ValueError` を
   投げ、飛ばすかどうかは `SchedDataFile.load_line()` が決める。**
   警告のメッセージにファイル名と行番号を出したいため、判断を
   読み込み側に寄せた
8. **末尾の改行 1 つでは「空行」の警告を出さない。**
   `split_lines()` が末尾の `\n` を 1 つだけ落としてから分ける。
   ふつうに保存したファイルを読むたびに警告が出ると意味が無くなるため。
   本当の空行（中間の空行、末尾の 2 つ目以降の改行）は警告する
9. **`html2text()`（移行）は `<br />` 以外のタグを残す。** 仕様書の
   手順 5 のとおりで、旧 `htmlstr2text()` は流用していない

## 直さずに残したもの

- **`SchedDataEnt.TIME_NULL`（`":-:"`）が、どこからも参照されなく
  なった。** 以前はテストが使っていただけで、実装は
  `get_timestr()` / `get_sortkey()` の中でリテラルの `":-:"` を
  使っている。消すのは TODO-020 の範囲を超えるので残した
- **`migrate-errors.txt` は `.gitignore` に入っていない。**
  リポジトリのルートで `ytsched migrate` を実行すると、変換できない行が
  あったときに未追跡ファイルとして残る。`.gitignore` を触るのは
  範囲外と判断して手を付けていない
- `main_handler.py` の `search_str = search_str.lower()`（利用者が入れる
  検索文字列の側）は、依頼のとおりそのままにした。全角括弧を含む
  正規表現は、正規化された照合対象には当たらない（仕様どおり）
- `base.html` の `{% autoescape None %}` は現状維持（TODO-012）

## うまくいかなかったところ

特になし。`mise run lint` の指摘（`FURB122`、`TRY004`、`UP037`、
`RUF100`）はその場で直した。

---

## reviewer の指摘への対応（2026-08-21 追記）

main が「直す」と決めた 5 点に対応した。直さないと決まったもの
（reviewer の指摘 1・3、`BR_PATTERN`、BOM、`dict_str()` の
`str(value)`、`TIME_NULL`）には手を付けていない。

### 1.（指摘 2）読み込みで飛ばした行を、保存で書き戻す

- `SchedDataFile.__init__()` に `self.skipped_lines: list[bytes] = []` を
  用意し（`load()` より前）、`load()` が飛ばした行を**生のバイト列のまま**
  ここへ足すようにした
- `save()` はバイナリ（`mode="wb"`）で開き、予定を書き出したあとに
  `skipped_lines` を**元のバイトのまま**末尾へ書き戻す。デコードできない
  行もそのまま復元される
- `.bak` の仕組みは変えていない

**writer 向けの、実装した振る舞い（3〜4 行）:**

> 読み込みで飛ばした行は、生のバイト列のまま覚えておき、次の保存で
> ファイルの末尾へ元のバイトのまま書き戻す。予定の行が先、飛ばした行が
> あとに並ぶ。したがって、保存を何回くり返しても壊れた行は失われず、
> 本体にも `.bak` にも残る。読み直すたびにまた飛ばされて警告も出続ける
> （利用者が手で直せば、そこで消える）。

- 実際の動きを確認した。壊れた 5 種類（空行・euc_jp のバイト・
  `{ broken`・`[1,2,3]`・`date` の無い行）を仕込んだファイルに対し、
  アプリから追加を 2 回行っても、本体・`.bak` の両方に 5 行とも
  元のバイトのまま残った（旧形式で問題になっていた経路が閉じた）
- テストを書き直した。`test_load_broken_line_is_not_saved` を消し、
  `test_load_broken_line_is_written_back`、
  `test_load_broken_line_survives_two_saves`（保存 2 回）、
  `test_broken_line_bytes_are_kept`（5 種類 + 空白だけの行の 6 通りで
  バイト列が完全一致）、`test_broken_line_is_skipped_again`（書き戻した
  行はまた飛ばされ、警告も出る）、
  `test_no_broken_line_writes_nothing_extra`（余計なものを書かない）、
  `test_skipped_lines_of_new_file` を足した

### 2.（指摘 4）`split_lines()` の二重実装をやめた

`migrate.py` の `split_lines()` を消し、`Migrator.conv_file()` は
`SchedDataFile.split_lines()` を呼ぶようにした（`migrate.py` は
もともと `SchedDataFile` を import している）。
`tests/test_migrate.py` の該当テストも `SchedDataFile.split_lines()` を
見る形に直した。

### 3. 移行ツールのテストが `--error-file` の既定を使っていた

`tests/test_migrate.py` に `mk_migrator(datadir, **kwargs)` ヘルパを足し、
`error_file` の既定を `{datadir}/errors.txt`（＝ `tmp_path` の下）に
するようにした。`Migrator(...)` を直に呼ぶ箇所は全部これに置き換えてある
（既定のカレントディレクトリを使う呼び出しは残っていない）。
テストの実行後にリポジトリ直下へ `migrate-errors.txt` が落ちないことを
確認した。

### 4. `except` の書き方を揃えた

`ytsched.py` の `dict_time()` を `except (ValueError, TypeError) as e:` に
した。あわせて警告に理由（`{e}`）を出すようにした。

**判断が要った点:** 括弧を付けるだけでは `ruff format` が PEP 758 の
括弧なし（`except ValueError, TypeError:`）へ戻してしまう
（`requires-python >= 3.14` のため。実測）。`as` 句がある場合は
括弧が要るので戻されない。**`as e` を付けて括弧付きを保つ**形にした。
これで `ytsched.py` の複数例外の `except` は 2 か所とも括弧付きで、
`mise run lint` を通しても崩れない。

### 5. 移行ツールで、対象ファイルが 0 件なら警告を出す

`Migrator.main()` の先頭で、対象が 0 件なら
`no target file .. check --datadir` の警告を出すようにした
（終了コードは変えていない）。CLI でも警告が出ることを確認し、
テスト（`test_no_target_file_warns`）も足した。

### 確かめたこと

- `mise run lint`: ○（ruff / basedpyright / mypy とも 0 件）
- `uv run pytest tests`: ○ **289 passed**（対応前は 273）
- 一時ディレクトリでアプリを起動し、上の 1 の振る舞いを実際に確認
  （実データ `~/ytsched/data` には触れていない）。確認に使った
  一時ディレクトリは片付けた。`ytsched webapp` のプロセスが残って
  いないことも `pgrep` で確認した

---

## 空行の書き戻しをやめた（2026-08-21）

reviewer の指摘 B と、足りないテストの 2 件に対応した。
「直さなくてよい」とされた 2 件（`dict_time()` の `TypeError`、
移行ツールの終了コード）には手を付けていない。

### 1.（指摘 B）空行は書き戻さない

- `SchedDataFile.load()` は、飛ばした行のうち**空行だけ**を
  `skipped_lines` に積まないようにした。ほかの 4 種類（utf-8 で
  デコードできない・JSON として読めない・オブジェクトでない・
  `date` が無い／読めない）は、これまでどおり書き戻す
- 空行の判定を `SchedDataFile.is_empty_line()`（staticmethod）に
  まとめ、`load()` と `load_line()` の両方から呼ぶようにした。
  規則が 2 か所に散らないようにするため
- **なぜ空行だけ別扱いなのかは、`load()` の中のコメントと、
  `is_empty_line()` / `load()` / `save()` の docstring に残した**
  （「飛ばしても失うデータが無いため」）

**writer 向けの、実装した振る舞い（2〜3 行）:**

> 飛ばした行のうち、**空行（空白だけの行を含む）は書き戻さない。**
> 飛ばしても失うデータが無いため、保存するとファイルから消える。
> したがって、手で編集して空行が入っても、一度保存すれば
> `empty line .. ignored` の警告は出なくなる。残りの 4 種類は
> これまでどおり末尾へ元のバイトのまま書き戻される。

テスト:

- `BROKEN_RAW_LINES` を「書き戻される 4 種類」に絞り、
  空行・空白だけの行は `EMPTY_RAW_LINES` に分けた
  （`test_broken_line_bytes_are_kept` /
  `test_broken_line_is_skipped_again` は 4 種類を見る）
- `test_empty_line_is_not_written_back` — 空行・空白だけの行が
  `skipped_lines` に入らず、保存するとファイルから消える
  （ファイル全体のバイト一致で確認）
- `test_empty_line_warning_stops_after_save` — 1 回目の読み込みでは
  警告が出て、保存したあとの読み込みでは**警告が出ない**

### 2. 全行が壊れているファイルのテスト

`test_all_lines_broken_survives_two_saves` を足した。
`[1, 2]` と `{ x` だけのファイル（`sde` が 0 件、`skipped_lines` が
2 行）に対し、`SchedDataFile` を作り直して追加 → 保存を 2 回くり返し、

- 本体・`.bak` の**両方**が、元の 2 行を**バイト列のまま**末尾に持つこと
- 本体が 4 行（追加 2 件 + 壊れた 2 行）で、二重に書かれていないこと

を押さえた。`docs/data-format.md` が旧形式の消失例として挙げている
経路が閉じていることの固定になる。

### 確かめたこと

- `mise run lint`: ○（ruff / basedpyright / mypy とも 0 件）
- `uv run pytest tests`: ○ **290 passed**（対応前は 289）
- 一時ディレクトリでアプリを起動して実際に確認した。
  「読める行 1 + 空行 + 空白だけの行 + `{ broken` + euc_jp のバイト」の
  ファイルに 1 件追加して保存すると、**空行 2 つは消え、壊れた 2 行は
  元のバイトのまま残った**。別プロセス（`ytsched x-data1`）で読み直すと、
  警告は壊れた 2 行の分だけで、`empty line` の警告は出なくなっていた
- 使った一時ディレクトリは片付け、`ytsched webapp` のプロセスが
  残っていないことを `pgrep` で確認した。実データ `~/ytsched/data` には
  触れていない
