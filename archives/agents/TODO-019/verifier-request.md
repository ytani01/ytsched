# TODO-019 verifier への依頼

## 何を確かめてほしいか

`tests/data/old_format/` に置いた**合成テストデータ**が、
**TODO-019 に挙げた特徴を全部再現できているか**。

データは `tests/make_test_data.py` が生成する。中身は架空で、実データ
（`tmp_test_data/`。個人の予定なのでリポジトリに入れない）の構造だけを
写したもの。移行ツール（TODO-020）の変換元として使う。

**「README に書いてあるからそうだろう」で通さないこと。**
実際にファイルを読んで確かめる。確かめ方はあなたが決めてよい
（Python を書いて数えるのが早いはず）。一時ファイルを作るなら
`tests/` や `archives/` の外に置くこと。

## 確認する項目

### 1. 仕様書に挙げた特徴が全部あるか

`TODO.md` の TODO-019「（再現する特徴）」と、
`docs/data-format.md`「実データを調べて分かったこと」に挙がっているもの。
1 つずつ、**どのファイルの何行目で満たされているか**を突き止めて
報告してほしい。見つからなかったものは「無い」と書く。

- utf-8 のファイルと euc_jp のファイルの両方があるか
- **どちらでも読めない 1 行を含むファイル**があるか。その行以外は
  euc_jp で読めるか。壊れた行も、euc_jp の `errors="replace"` なら
  タブ 7 列として成立し、日付も読めるか
- `&amp;#160;` の二重エスケープ、`&nbsp;` `&gt;` `&lt;` `&quot;`、
  `<br />`、`<br />` 以外の HTML タグ
- `★` `(キャンセル` `(欠` `x` などで始まる `title`、全角括弧を含むもの
- 空の `title`、空のファイル（0 バイト）、範囲外の時刻（`28:00`）
- `:-:` `HH:MM-:` `:-HH:MM` `HH:MM-HH:MM` の 4 通りの時刻欄が全部あるか
- UUID でない `sde_id`。**長さが 13・15・16・17・18 文字のものが
  全部あるか**。重複する `sde_id` があるか（何回出てくるか）
- `ToDo.cgi` があり、`type` が `□` で始まる行が入っているか
- 移行の対象外のファイル（`{日}-backup.cgi`、`{日}.cgi.bak`、
  `iappli_log.cgi`）があるか
- **`detail` に U+2028（LINE SEPARATOR）を含む行**があるか。
  その行を `str.splitlines()` で切ると壊れ、`split("\n")` なら
  壊れないことを実際に確かめる
- **列の数が 7 でない行**（6 列と 8 列）があるか

### 2. 生成スクリプトが決定的か

`uv run python tests/make_test_data.py` を 2 回続けて実行して、
できるファイルが 1 バイトも変わらないこと（ハッシュで比べる）。
`README.md` が消えずに残ること。

### 3. README の表が実物と合っているか

`tests/data/old_format/README.md` の表にある**文字コードと行数**が、
実際のファイルと合っているか。1 行でもずれていたら報告してほしい。

### 4. lint・テスト・git

- `uv run ruff format --line-length 78 src tests`（変更が出ないこと）
- `uv run ruff check --extend-select I src tests`
- `uv run basedpyright src tests`
- `uv run mypy src tests`
- `uv run pytest tests`
- `git status --short --untracked-files=all` で、
  **`tests/data/old_format/2021/08/01.cgi.bak` が git から見えているか**
  （`.gitignore` の `*.bak` を打ち消す指定を足してある）。
  `git check-ignore -v` で確かめられる

## 既知のこと（報告しなくてよい）

- **移行ツールもそれを使うテストコードも、まだ無い。** この項目で作るのは
  データと生成スクリプトだけ。実装は TODO-020
- あなたの定義ファイル（`.claude/agents/verifier.md`）に
  「データ形式（タブ区切りテキスト）は変えない」とあるが、これは
  TODO-018 で覆っていて、**JSON Lines へ移すと決まっている**。
  定義の書き直しは別途 main が判断する
- `tmp_test_data/` は実データ。`.gitignore` で除外してある。
  **報告に中身を書かないこと**（件数や形式の統計はよい）

## 報告

`archives/agents/TODO-019/verifier-report.md` に書く。
返事は 5 行以内。
