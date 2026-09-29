# TODO-207 reviewer の報告

対象: `git diff -- src/ytsched/ytsched.py tests/test_ytsched.py`
（`SchedDataFile.save()` と、末尾に足した 2 つのテスト）

## 確信度の高い指摘

### 1. `docs/data-format.md` の「バックアップ」の節が、書く順序と合わなくなった

- 場所: `docs/data-format.md:160-161`
- 文書: 「書く前に、既存のファイルが空でなければ `.bak` を付けた名前へ
  退避する」
- 実装: 一時ファイルへ書き終えて**から**元のファイルを `.bak` へ移し、
  一時ファイルを `replace()` で差し替える
- `CLAUDE.md` に「形式を変えたらあの文書も書き直す」とある。保存形式そのもの
  は変わっていないが、この節は保存の手順を書いているので食い違う。
  TODO-207 のチェック項目には文書の修正が入っていない。直すかどうかは
  main の判断

## 保つものの確認（一致）

- 空でないファイルだけ `.bak` に残す: 一致（`st_size > 0` の判定は元のまま）
- `skipped_lines` を元のバイトのまま書き戻す: 一致（バイナリで `raw_line + b"\n"`）
- `_stat_key` を持ち直す: 一致。一時ファイルの `fstat()` の値を使うが、
  `chmod()`（ctime だけ変わる）と `replace()`（rename）は mtime・size を
  変えないので、差し替えたあとのファイルと同じ値になる。失敗時は持ち直さない
- パーミッション: 一致。元のファイルがあれば `chmod(st_mode)`（ファイル種別の
  ビットはカーネルが落とす。`trash.py` の `fchmod()` と同じ扱い）、無ければ
  `open("xb")` で umask に従う
- 失敗時: 書き込み中の失敗なら元のファイルと `.bak` は手つかず、一時ファイルは
  `unlink()` される。`shutil.move()` の失敗でも元のファイルは残る
- 一時ファイルの名前 `.{name}.{uuid4 hex}`: `DAILY_GLOB`
  （`[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].jsonl`、`ytsched.py:458`）にも
  `ToDo.jsonl` の決め打ち（`ytsched.py:555`）にも当たらない。`migrate.py:235`
  は `.cgi` だけ。`fix_id.py` はこの一覧を使う。走査に混ざる箇所は無し
- 呼び出し元（`SchedData.save()`、`trash_handler.py:138`、
  `sched_update.py:147`、`holiday.py:195`）: 引数・戻り値・例外の伝わり方とも
  変わらず、影響無し
- `uuid` は既に import 済み。新しい依存は無し
- テストが旧実装で落ちるか: 作業ツリーのコピー（scratchpad）で `save()` を
  `HEAD` の版に戻して 2 件を実行し、**2 件とも落ちた**
  - `test_save_failure_keeps_original_and_backup`: 本体が空になって落ちる
  - `test_save_keeps_permission`: `st_mode & 0o777` が `0o644`（期待 `0o640`）で落ちる
  - 頭の中での当てはめ: 一時ファイルへの `chmod()` を消すと後者が、
    `except` の `unlink()` を消すと前者の `iterdir()` の比較が落ちる

## 確信度の低いもの（実害は未確認）

### a. `.bak` へ移してから `replace()` までの間、本体が無い

- 場所: `ytsched.py` の `shutil.move(self.pathname, backup_pathname)` と
  `tmp_pathname.replace(self.pathname)` の間
- この間にプロセスが落ちるか `replace()` が失敗すると、本体が無く、内容は
  `.bak` にだけ残る（前の `.bak` は失われる）。次に読むとその日は空に見える。
  別プロセス（`holiday` などの CLI）がこの間に読んでも空に見える
- 旧実装にも同じ窓があり（しかも書き込み全体の間）、今回は狭くなっている。
  TODO の「`.bak` は元のファイルを移して作る」どおりなので範囲内。
  本体が常にある形にするなら、`.bak` をハードリンクで作ってから
  `replace()` する手もある。やるかどうかは main の判断

### b. 失敗のテストの `.bak` の比較が、本体の比較と独立していない

- 場所: `tests/test_ytsched.py` の `test_save_failure_keeps_original_and_backup`
- 1 回目の `save()` で `.bak` も本体も `DATALINE1` になるので、失敗時に
  「`.bak` が本体で上書きされた」としても `.bak` の比較では区別できない。
  今の実装の順序でその状態になると本体が無くなり、本体の比較で落ちるので、
  いまのテストの強さとしては足りている

### c. 一時ファイル名が衝突したときの `unlink()`

- `open("xb")` が `FileExistsError` になると、`except` が既にあった同名の
  ファイルを消す。名前が uuid4 なので現実には起きない。書き留めるだけ
