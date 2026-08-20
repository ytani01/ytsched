# implementer への依頼（TODO-020）

JSON Lines への移行ツールと、読み書きの実装。

**先に読むもの**（この依頼はそれらの補足で、置き換えるものではない）:

- `TODO.md` の TODO-020
- `docs/data-format.md` — **移行先の仕様。ここが決まりの置き場所**
- `tests/data/old_format/README.md` — 変換元のテストデータ（TODO-019 で
  用意した合成データ。何を再現しているか一覧がある）

**この項目はデータ形式を変える。** `.claude/agents/*.md` に以前あった
「データ形式（タブ区切りテキスト）は変えない」は、この着手に合わせて
書き直してある。旧形式は残さない（両方を読めるようにはしない）。

## 範囲

コードとテストを実装する。**文書（`CLAUDE.md` の「データモデルの勘所」、
`docs/data-format.md` の冒頭にある「まだ実装していない」の記述）は
writer が別に担当するので、手を出さなくてよい。**

## 1. `ytsched.py` — 判定・検索に使う正規化

モジュールレベルに正規化の関数を 1 つ置く。

```python
def normalize(text: str) -> str:
    """判定・検索の照合に使う形へ揃える（保存する文字列は変えない）。"""
```

揃えるのは 2 つだけ。全角括弧を半角にする（`（`→`(`、`）`→`)`）、
小文字にする。**`unicodedata.normalize("NFKC", …)` は使わない**（理由は
`docs/data-format.md`）。

使う場所は次の 3 か所。**ここ以外には広げない。**

- `is_important()` / `is_canceled()` — いまの `self.title.lower()` を
  `normalize(self.title)` にする
- `get_sortkey()` — 表題の先頭の `(` を見ているところ
- `search_str()` — 照合対象の組み立て。いまは最後に `.lower()` している

**`is_todo()` と `is_holiday()` は変えない。**`type` を見る判定で、
仕様書が正規化の対象に挙げていない。

`TITLE_PREFIX_IMPORTANT` / `TITLE_PREFIX_CANCELED` / `TYPE_PREFIX_TODO` /
`TYPE_HOLYDAY` の**中身は変えない**（TODO-018 で決めた条件）。

`main_handler.py` の `search_str = search_str.lower()`（利用者が入れる
検索文字列の側）は**そのまま**。仕様書の「検索文字列そのものは正規化
しない」に当たり、既存のテストもこの挙動を押さえている。

## 2. `ytsched.py` — 読み書きを JSON Lines に

- `htmlstr2text()` / `text2htmlstr()` は**消す**。`SchedDataEnt.__init__()`
  の `self.detail = htmlstr2text(detail)` も、`__str__()` の呼び出しも同様
- パスは `.jsonl` に。`PATH_FORMAT` は `{年}/{月}/{日}.jsonl`、
  `TODO_PATH_FORMAT` は `ToDo.jsonl`
- 文字コードは **utf-8 のみ**。`ENCODE`（utf-8 → euc_jp と試すリスト）は
  やめる
- 書き出しは `json.dumps(…, ensure_ascii=False)`。キーは
  `sde_id` `date` `time_start` `time_end` `type` `title` `place` `detail`
  の順で、**書くときは全部出す**
- `mk_dataline()` は「ファイルに書く 1 行」を返す役目のまま、中身を JSON に
  する（`__main__.py` の `x_data1` とテストが呼んでいる）。`x_data1` に
  ある `.replace("\t", "<tab>")` は要らなくなるので外す
- dict との相互変換を分けておくと、テストが書きやすい
  （`to_dict()` と、`from_dict()` のような読み側）

### 読み込み

**バイナリで読んで `split(b"\n")` で切り、行ごとに utf-8 でデコードする。**
`str.splitlines()` は使わない（U+2028 で切れてしまう。実データに 1 件
あった。`detail` に生の U+2028 が入りうる）。

飛ばす行（**その行だけ飛ばし、ファイル全体は捨てない。飛ばしたら警告**）:

- 空行
- utf-8 でデコードできない行
- JSON として読めない行
- オブジェクトでない行（配列や数値だけの行）
- `date` が無い、または日付として読めない行

欠けたキーの既定値は、`type` `title` `place` `detail` が空文字、
`time_start` `time_end` が null。

日々のファイルで、**ファイル名から決まる日付と行の `date` が食い違う
ときは警告を出し、行の `date` を使う**（ファイル名を信じて黙って
書き換えない）。ToDo のファイルにはこの確認をしない。

`FileNotFoundError` のときに空リストを返すのは、いまと同じ。

### 保存

`.bak` の仕組みは**変えない**。既存ファイルが空でなければ `.bak` へ
退避してから上書きし、空のファイルは退避しない。

## 3. 移行ツール — `ytsched migrate`

**CLI のサブコマンドとして足す**（`__main__.py`。実装の本体は別モジュール
に分けてよい）。`--datadir` は既定を `SchedDataFile.DEF_TOP_DIR` にする。

対象は `{年}/{月}/{日}.cgi` と `ToDo.cgi` **だけ**。`{日}-backup.cgi`、
`{日}.cgi.bak`、`iappli_log.cgi` は対象にしない。

変換は `docs/data-format.md` の「変換の手順」1〜6 のとおり。要点:

1. **行ごとにデコードする**（ファイル単位ではない）。utf-8 → euc_jp の順に
   試し、どちらでも読めない行は euc_jp の `errors="replace"` で読んで
   **行は残す**
2. タブで分ける。7 個未満は空文字で埋め、8 個以上は 8 個目から先を
   `detail` の続きとしてタブでつなぎ直す（**捨てない**）
3. `YYYY/MM/DD` → `YYYY-MM-DD`
4. 時刻を `time_start` / `time_end` に分ける。空の側は null。
   **範囲外の値は旧コードと同じく時を 24、分を 60 で割った余りにする**
   （実データの `28:00` が `04:00` になる）
5. `type` `title` `place` `detail` を素のテキストに戻す。**この順**で:
   `<br />` を改行に（大小・スラッシュの有無を問わない）→
   `html.unescape()` を **2 回**（3 回以上はかけない）→
   NBSP（U+00A0）を半角空白に。
   **`<br />` 以外の HTML タグはそのまま残す**
6. **全角括弧はそのままにする**

**旧コードの `htmlstr2text()` を流用しない**（全角括弧の半角化まで
やってしまい、手順 6 を破る）。

その他:

- 変換できない行（日付が読めないなど）は**捨てずに書き出して報告する**。
  書き出し先はオプションで指定できるようにする
- 元の `.cgi` は消さない
- `--dry-run` を付ける（書かずに件数だけ出す）
- 終わりに、ファイル数・行数・飛ばした行数を出す

## 4. テスト

- 既存のテストは `.cgi` 前提で書かれている（`tests/test_ytsched.py`、
  `tests/test_web.py` に旧形式を直書きしている箇所が多い）。JSON Lines に
  合わせて直す
- **正規化** — `（重要）打合せ` が、作った直後も保存して読み直したあとも
  重要と判定されること。**保存された文字列は `（重要）打合せ` のまま**で、
  画面にもそのまま出ること。取り消し・`get_sortkey()`・`search_str()` も
  全角と半角の両方で同じに効くこと
- **壊れた行** — 上の「飛ばす行」の 5 種類それぞれで、その行だけが
  飛ばされ、同じファイルの他の行は読めること
- **食い違う `date`** — 警告が出て、行の `date` が使われること
- **移行ツール** — `tests/data/old_format/` を一時ディレクトリへコピーして
  変換し、結果を確かめる。少なくとも次を押さえる:
  どちらでも読めない 1 バイトを含む行が残ること、`&amp;#160;` が空白に
  なること、`28:00` が `04:00` になること、全角括弧が残ること、
  U+2028 で 1 件が 2 行に割れないこと、6 列・8 列の行の扱い、
  対象外の 3 ファイルが変換されないこと
- `tests/data/old_format/` と `tests/make_test_data.py` は**書き換えない**
  （TODO-019 で決着した移行元のデータ）

## 確かめること

`mise run lint` と `uv run pytest tests` を通す。アプリを一時ディレクトリで
起動して動くことも自分で見ておく（最終的な確認は verifier が別に行う）。

## 報告

`archives/agents/TODO-020/implementer-report.md` に書く。返事は 5 行以内。
単独で決めた判断（モジュールの分け方、オプション名など）は必ず報告に書く。
