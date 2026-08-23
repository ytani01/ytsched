# TODO-032 reviewer の報告

`Conf.cgi` → `conf.json` の変更（未コミット）を読んだ。対象は
`git diff` の 10 ファイル（`src/ytsched/handler.py`、`main_handler.py`、
`migrate.py`、`docs/data-format.md`、`src/README.md`、`tests/README.md`、
テスト 4 つ）。

**範囲を超えた変更は見つからなかった。** `main_handler.py` の差分は
コメントと docstring の `Conf.cgi` → `conf.json` だけで、
`get_conf_arg()` / `convert_value()` のロジックには手が入っていない。
テストも、旧テストが見ていた「空の値」「値が壊れているときの既定値への
落とし方」「不正な値を保存しない」はすべて JSON 版に置き換わっている
（タブ特有の 3 件は、JSON では意味が無いので差し替えで妥当）。

以下、確信度の高いものから。

---

## 1. `docs/data-format.md` の「移行ツールの使い方」節が追随していない

**確信度: 高**

`Conf.cgi` の変換について書き足したのは「対象にするファイル」節
（205 行あたり）だけで、その下の「移行ツールの使い方」節（322〜331 行）が
旧のままになっている。

- 322 行 — 「対象は「対象にするファイル」に挙げた `{年}/{月}/{日}.cgi` と
  `ToDo.cgi` だけ」。`Conf.cgi` が対象に増えたので、いまは事実と違う
- 325 行 — 「既に `.jsonl` があるファイルは、警告して飛ばす」。
  `conf.json` にも同じ扱い（`migrate_conf()` の `already exists .. skipped`）が
  あるが書かれていない
- 330 行 — 「終わりに、変換したファイル数・飛ばしたファイル数・変換した
  行数・飛ばした行数（…）を出す」。実際は
  `設定ファイル    : 変換 N, 飛ばした N` の 1 行が増えている

この節は「移行ツールの仕様の置き場所」として使われている（オプションの
表もここにある）ので、ここが古いままだと、あとで読む人が
`Conf.cgi` の扱いに気づけない。TODO-032 のチェック項目
「文書を直す（`src/README.md`、`docs/data-format.md`）」の範囲内。

## 2. `conv_conf()` だけ、変換できなかった行を捨てている

**確信度: 高（捨ててよいかどうかは判断が要る）**

`src/ytsched/migrate.py:348-350`

```python
            if "\t" not in line:
                self.__log.warning(f"{path}:{i}: no tab .. ignored")
                continue
```

`conv_file()`（299-305 行）は、変換できなかった行を
`self.error_lines` に積んで `--error-file` へ書き出し、
`stat.error_lines` にも数える。`docs/data-format.md` にも
「変換できない行（日付が読めないなど）は、捨てずに書き出して報告する」と
書いてある。`conv_conf()` はここだけ warning を出して黙って捨てる。
`MigrateStat` にも数える場所が無いので、**サマリを見ても捨てたことが
分からない**。

どういう入力で問題になるか: 旧 `Conf.cgi` に、タブでなく空白で区切られた
行や、途中で壊れた行が入っている場合。移行は「成功」に見えて、
その設定だけ消える。ログを追わない限り気づけない。

実データの `Conf.cgi` はアプリが書いたものなので、実際に該当する行が
ある可能性は低い。ただ、**そう判断して捨てるなら、`conv_conf()` の
docstring に「予定データと違い、error-file には出さない」と書いておく
ほうがよい**（いまの docstring は「読み方は他の変換と揃える」とだけ
書いてあり、揃っていない点が読み取れない）。ここは main の判断。

## 3. `load_conf()` の docstring が、実装より広いことを約束している

**確信度: 高（文言と実装の食い違い。どちらを直すかは判断）**

`src/ytsched/handler.py:72-75`

> **読めない設定ファイルでも例外にしない。** JSON として壊れて
> いる場合は、警告を 1 行出して空の dict を返す。

実際に捕まえているのは `FileNotFoundError` /
`json.JSONDecodeError` / `UnicodeDecodeError` の 3 つだけ。
`conf.json` がディレクトリだった（`IsADirectoryError`）、
読み取り権限が無い（`PermissionError`）場合は、そのまま抜けて
リクエストが 500 になる。`__init__` から呼ばれるので、**全ページが
開けなくなる**。

`src/README.md` に足した説明（「読めない設定ファイル（壊れた JSON、
オブジェクトでない、値が文字列でないキー）は、警告を 1 行出して
無視する」）は、括弧の中でケースを列挙しているので実装と合っている。
食い違っているのは `handler.py` 側の太字の 1 文だけ。

対処は 2 つ。(a) 太字を「JSON として壊れていても例外にしない」に狭める、
(b) `except OSError` まで広げる。TODO-032 は「形式の変更だけ」なので
(a) が範囲に合う。

## 4. `UnicodeDecodeError` の分岐にテストが無い

**確信度: 高**

`load_conf()` で `UnicodeDecodeError` をわざわざ捕まえているのに、
`tests/test_handler.py` にそれを踏むテストが無い（壊れた JSON、
オブジェクトでない、値が文字列でない、の 3 つは足してある）。
`(datadir / CONF_FNAME).write_bytes("…".encode("euc_jp"))` で
1 件足せば埋まる。

移行前の `Conf.cgi` を手で `conf.json` にリネームした、といった状況で
実際に踏む分岐なので、押さえておく価値はある。

---

以下は確信度が低い。**気になった程度**で、直さない判断も十分あり得る。

## 5. `str(param)` は要らない（低）

`src/ytsched/handler.py:110` の `conf[str(param)] = value`。
JSON オブジェクトのキーは必ず `str` なので、この `str()` は効かない。
`json.load()` の戻りが `Any` なので型チェッカ対策かもしれないが、
`isinstance(data, dict)` を通ったあとなら
`data: dict[str, Any]` を明示するほうが意図が伝わる。

## 6. `Migrator.main()` の「no target file」警告（低）

`src/ytsched/migrate.py:397-400`。`find_files()` は `Conf.cgi` を
含まないので、`Conf.cgi` だけがあるディレクトリでも
`no target file .. check --datadir` が出る。そのあと設定の変換は
ちゃんと走るので、警告だけが紛らわしい。

## 7. 移行前にアプリを起動すると、旧設定を移行できなくなる（低）

`migrate_conf()` は `conf.json` が既にあれば飛ばす（正しい）。一方
アプリは、`filter_str` などを指定した最初のリクエストで `conf.json` を
新規に書く。**移行前にアプリを触ってしまうと、以後 `ytsched migrate` は
`already exists .. skipped` で旧 `Conf.cgi` を取り込めない。**
実害は設定 4 つの入れ直しだけなので大きくないが、`docs/data-format.md`
に「アプリを起動する前に移行する」と 1 行あってもよい。

## 8. 書き出しの書式が 2 か所にある（低）

`handler.save_conf()` と `Migrator.migrate_conf()` が、どちらも
`json.dump(..., ensure_ascii=False, indent=2)` + `f.write("\n")` を
書いている。両方にテストはあるが、**同じ書式であること**は
どのテストも押さえていない。片方だけ変えても気づけない。
ファイル名の定数を分けている理由（tornado への依存を持ち込まない）は
コメントで説明されていて妥当なので、書式も揃えるなら共通化ではなく
テストで縛るほうが素直だと思う。

## 9. 壊れた JSON のときの影響範囲（低・仕様の確認）

旧形式では、壊れた行 1 行を飛ばして他の行は読めた。JSON では 1 文字
壊れるだけで全設定が `{}` になり、次の `set_conf()` でファイルごと
上書きされる。設定は 4 つで画面から入れ直せるので実害は小さく、
JSON にする以上は避けられない。**そう決めたのなら、これは指摘ではない。**

## 10. `migrate.py` のモジュール docstring（低）

8 行目「対象は `{年}/{月}/{日}.cgi` と `ToDo.cgi` だけ。」の直後に、
11 行目で「`Conf.cgi` から `conf.json` への変換もここで行う」が続く。
続けて読むと矛盾して見える。8 行目を「予定データの対象は」に
限定すれば解ける。1 と同じ話。
