# TODO-170 reviewer 報告

対象: `src/ytsched/fix_id.py`、`src/ytsched/__main__.py` の `fix-id` 部分、
`tests/test_fix_id.py`。

データを失う道（読めない行を落とす、ファイルを空にする、書き戻し途中で
元ファイルを壊す）は見当たらなかった。`split_lines()` の空行の扱い、
一時ファイル → `Path.replace()` の原子的な置き換え、例外時の一時ファイル
削除は、実際に再現コード（`uv run python` で `fix_file()` を直接呼ぶ）で
動きを確かめたうえで妥当だと判断した。

## 1. 元のファイルに無かった改行を、書き換えたファイルには足してしまう

`fix_file()`（`src/ytsched/fix_id.py:170`）は、書き戻すときに

```python
out_data = b"".join(line + b"\n" for line in out_lines)
```

としており、**どの行にも無条件で `\n` を付ける**。`split_lines()` は
末尾の改行を 1 つだけ剥がして返す仕様なので、元のファイルが改行で
終わっていれば往復して同じ結果になるが、**元のファイルが改行で終わって
いない場合、書き換えたファイルには新たに末尾の改行が付く**。

実際に確認した:

```
before: b'{"sde_id": "abc123def456", "title": "x"}'
after : b'{"sde_id": "3ef6cee0-2e6c-481c-b894-707e7f90ebca", "title": "x"}\n'
```

依頼書で名指しされていた観点（「元のファイルに無かった改行を足していないか」）
がそのまま起きている。`sde_id` 以外は変えない、という仕様には
厳密には抵触する。ただし実データは `SchedDataFile.save()`
（`src/ytsched/ytsched.py:668`）で書かれ、そちらは行ごとに必ず `\n` を
付けて保存するため、**実データが末尾改行なしになっている可能性は低い**。
テストにこのケース（末尾改行なしのファイル）が無いので、意図した挙動か
どうかがコードからは読み取れない。

## 2. `except UnicodeDecodeError, json.JSONDecodeError:`（Python 2 風の書き方）

`src/ytsched/fix_id.py:129`

```python
except UnicodeDecodeError, json.JSONDecodeError:
```

かっこが無いこの書き方は Python 2 の「例外を変数に束縛する」構文に見えるが、
実際に試したところ現行の Python（3.14 で確認）では `except (A, B):` と
同じ意味に構文解析され、両方の例外型を正しく捕まえる。**動作は正しい。**
ただし一般的な書き方ではなく、`ruff` / `basedpyright` も指摘しないため、
今後だれかが「Python 2 の遺物」と誤解して `except UnicodeDecodeError as
json.JSONDecodeError:` のように直してしまう危険がある。確信度は低いが、
`except (UnicodeDecodeError, json.JSONDecodeError):` と括弧を付けたほうが
安全だと思う。

## 3. `_log = getLogger(__name__)`（`fix_id.py:43`）が使われていない

`migrate.py`・`holiday.py` はモジュール直下の関数が `_log` でログを出すので
使われているが、`fix_id.py` のモジュール直下の関数は `is_uuid()` だけで
ログを出さないため、`_log` は定義されただけで一度も参照されない。
依頼書で main が気にしていた点の答えとしては、**書き方は他モジュールと
揃っているが、この行自体は死んでいる**。実害は無いので確信度は低い。

## 確信度が低いその他の点

- `lines_unreadable` には、ファイル本文中の空行（`json.loads("")` が
  `JSONDecodeError` になるため）も混ざる。`SchedDataFile.load()` 側は
  空行を `is_empty_line()` で別扱いにして警告もカウントもしないので、
  ここだけ扱いが違う。行は失わないので安全面の問題ではないが、
  実行結果の「読めなかった行」件数が、本来の壊れた行より多く出る
  可能性がある
- テストに「末尾改行なしのファイル」「空ファイル」「複数行のうち末尾行だけ
  読めない行」のケースが無い。1 の指摘と合わせて、境界値のテストが
  やや手薄

## その他

- `__main__.py` の `fix-id` サブコマンドは `migrate` と同じ形で、
  `_log = getLogger("main")` の使い方も含めて既存のコマンドと揃っている。
  問題は無い
- `json.dumps(data, ensure_ascii=False)` はデフォルトの区切り文字で、
  `SchedDataEnt.mk_dataline()` と同じ呼び方。区切り文字やキー順が
  変わる心配は無い
- `DAILY_GLOB` は `migrate.py` の `.cgi` 版と同じパターンで `.jsonl` に
  差し替えただけ。`trash.jsonl`・`.bak`・`.cgi` を拾わないことも
  実際にテストで確認されている
