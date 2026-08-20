# TODO-019 verifier 報告

`tests/data/old_format/` を実際に Python で読んで確かめた
（README や実装コードは信じず、バイト列・デコード結果を毎回計算し
直した）。使ったコマンド・スクリプトは下に貼る。

## 1. 仕様書に挙げた特徴が全部あるか

すべて確認できた。

- **utf-8 / euc_jp 両方**: `2005/07/13.cgi` `2005/07/14.cgi`
  `2012/01/09.cgi` が euc_jp、`2021/08/01.cgi` `2021/08/02.cgi`
  `2021/08/04.cgi` `ToDo.cgi` が utf-8。実際に
  `bytes.decode("utf-8")` / `decode("euc_jp")` を試して確認（○）。
- **どちらでも読めない 1 行を含むファイル**:
  `2005/07/13.cgi` の 1 行目（`tests/make_test_data.py` の
  `DAY_20050713` 1 件目、生成後は `.cgi` の 1 行目）。
  ファイル全体は utf-8・euc_jp どちらでもデコード失敗（実測: utf-8 は
  位置 41 の `0xb2` で、euc_jp は位置 110 の `0xad` で例外）。
  行ごとに分けると 1 行目のみ両方失敗、2・3 行目は euc_jp で成功。
  1 行目を `decode("euc_jp", errors="replace")` すると
  `'1120729620-000164\t2005/07/13\t...\t資料は前日までに配布<BR>
  【欠席】�以上'` となり、タブで割ると **7 列**、`date` 列も
  `2005/07/13` のまま読める（○）。
- **`&amp;#160;`（3 件）、`&nbsp;`（4 件）、`&gt;`（1 件）、`&lt;`
  （1 件）、`&quot;`（2 件）、`<br />`（大小・スラッシュ有無込みで
  9 件）、`<br />` 以外のタグ**（`<b>` `</b>`
  `<a href="https://example.com/">` `</a>`、`2021/08/02.cgi`）：
  すべて実データを正規表現・文字列カウントで実測して確認（○）。
- **`★` `(キャンセル` `(欠` `x` で始まる title、全角括弧を含む
  title**: `★月次の打合せ`（`2021/08/01.cgi`）、`★定期検診`
  （`ToDo.cgi`）、`(キャンセル)△△社打合せ`（`2005/07/13.cgi`）、
  `(欠)◇◇システム定例`（`2005/07/13.cgi`）、
  `x中止になった工場見学`（`2021/08/01.cgi`）、`（重要）健康診断の
  申込`ほか全角括弧を含む title 6 件を実測（○）。
- **空の title**（2 件: `2005/07/14.cgi` 3 行目、`ToDo.cgi` の
  `□予約` の行）、**空のファイル**（`2021/08/03.cgi`、0 バイト実測）、
  **範囲外の時刻 `28:00`**（`2012/01/09.cgi` 5 行目、`28:00-:`）を
  実測で確認（○）。
- **時刻欄の 4 通り**: 全行の 3 列目を集めて確認したところ、
  `HH:MM-HH:MM`（例 `09:00-10:00`）、`HH:MM-:`（例 `09:00-:`）、
  `:-HH:MM`（例 `:-17:00`）、`:-:` の 4 通りとも実在した（○）。
- **UUID でない `sde_id`、長さ 13・15・16・17・18 の全部**:
  全行の 1 列目の長さ集合を計算したところ
  `{13, 15, 16, 17, 18}` で 5 種類すべて揃っていた（○、
  14 文字はもともと仕様に含まれていない）。
  **重複する `sde_id`**: `1627783341-8621308` が
  `2021/08/01.cgi` に 1 回、`2021/08/02.cgi` に 2 回、
  合計 **3 回**（README の記述どおり、実測で確認）（○）。
- **`ToDo.cgi`、`type` が `□` 始まり**: 5 行とも `□解約` `□予約`
  `□` `□病院` `□` で、全行 `□` 始まり（○）。
- **移行対象外のファイル**: `2021/08/01-backup.cgi`
  `2021/08/01.cgi.bak` `iappli_log.cgi` すべて実在（○）。
- **`detail` の U+2028**: `2021/08/02.cgi` の 3 行目
  （`前半のまとめ 後半のまとめ<br />以上`）に実在。
  `split("\n")` で切ると 3 行（各 7 列）のまま、
  `str.splitlines()` で切ると **4 行**に割れることを実測で確認
  （仕様書の「1 件が 2 行に割れる」を再現）（○）。
- **列の数が 7 でない行（6 列・8 列）**: `2021/08/04.cgi` の
  2 行目が 6 列、3 行目が 8 列（1 行目は 7 列）と実測で確認（○）。

漏れは見つからなかった。

## 2. 生成スクリプトが決定的か

```sh
uv run python tests/make_test_data.py   # 1 回目
find tests/data/old_format -type f ! -name README.md | sort | xargs sha256sum > hash1.txt
uv run python tests/make_test_data.py   # 2 回目
find tests/data/old_format -type f ! -name README.md | sort | xargs sha256sum > hash2.txt
diff hash1.txt hash2.txt
```

差分なし（○、11 ファイル全部一致）。`README.md` も 2 回目の実行後に
残っていることを確認（`clean()` が `README.md` だけ除外している
とおり）。

## 3. README の表が実物と合っているか

各ファイルの実際の行数（改行の数）とエンコーディングを
`wc -l` / decode テストで数え、README の表と突き合わせた。
**全 11 行、文字コード・行数とも一致**（ずれなし）。

| ファイル | README | 実測 |
| --- | --- | --- |
| 2005/07/13.cgi | euc_jp, 3行 | euc_jp(行ごと), 3行 |
| 2005/07/14.cgi | euc_jp, 3行 | euc_jp, 3行 |
| 2012/01/09.cgi | euc_jp, 5行 | euc_jp, 5行 |
| 2021/08/01.cgi | utf-8, 5行 | utf-8, 5行 |
| 2021/08/02.cgi | utf-8, 3行 | utf-8, 3行 |
| 2021/08/03.cgi | —, 0行 | 0バイト |
| 2021/08/04.cgi | utf-8, 3行 | utf-8, 3行 |
| ToDo.cgi | utf-8, 5行 | utf-8, 5行 |
| 2021/08/01-backup.cgi | utf-8, 1行 | utf-8, 1行 |
| 2021/08/01.cgi.bak | utf-8, 2行 | utf-8, 2行 |
| iappli_log.cgi | utf-8, 3行 | utf-8, 3行 |

## 4. lint・テスト・git

- `uv run ruff format --line-length 78 src tests`: 変更なし
  （`16 files already formatted`）（○）
- `uv run ruff check --extend-select I src tests`:
  `All checks passed!`（○）
- `uv run basedpyright src tests`: `0 errors, 0 warnings, 0 notes`（○）
- `uv run mypy src tests`: `Success: no issues found in 15 source
  files`（○）
- `uv run pytest tests`: `178 passed in 0.65s`（○）
- `git status --short --untracked-files=all` で
  `tests/data/old_format/2021/08/01.cgi.bak` は `??`（未追跡＝git
  から見えている）で、`git check-ignore -v` は
  `.gitignore:94:!tests/data/old_format/**/*.cgi.bak` を返し
  ignore されていないことを確認（○）。`.gitignore` の diff も
  該当行を追加していることを確認済み。

## 不具合・懸念

見つからなかった。

## 判断が要る点

なし。全項目 ○。
