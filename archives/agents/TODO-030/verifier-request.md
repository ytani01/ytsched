# 依頼: TODO-030 ドキュメントの確認（verifier）

writer が 6 つの文書を書いた。**書いたとおりに動くか**と、**移し漏れが
無いか**を確かめてほしい。文書は直さないこと。見つけたことは報告する。

- 依頼書: `archives/agents/TODO-030/writer-request.md`
- writer の報告: `archives/agents/TODO-030/writer-report.md`
- 決めたこと: `TODO.md` の TODO-030 の節

対象（`git status` で確認できる）:
新規 `src/README.md`・`docs/Developer.md`・`tests/README.md`、
変更 `CLAUDE.md`・`README.md`・`docs/data-format.md`。

## 確かめること

### 1. コマンド例が書いたとおりに動くか

`README.md` と `docs/Developer.md` に載っているコマンドを、**実際に叩いて**
確かめる。writer も確認したと報告しているが、**その報告を信じず自分で叩く**。

- `mise` のタスク（`fmt` / `typecheck` / `lint` / `test` / `build`）が
  文書に書かれた依存関係のとおりか。`mise tasks` の出力と突き合わせる
- `mise run webapp -- --datadir ... --port ...` の引数の渡し方が
  書かれたとおりに効くか
- `uv run ytsched migrate` のオプションが文書の記述と合っているか
  （`--help` で確認。実データは絶対に触らない）
- 個別コマンド（`uv run pytest` / `ruff` / `basedpyright` / `mypy`）の
  書き方が正しいか
- **アプリを起動して確かめるときは `--datadir` に一時ディレクトリを指定する**
- **`mise run upgradeproject`（`uppj`）は絶対に走らせない**

`README.md` の systemd のユニットは実際に登録しなくてよいが、
`ExecStart` のパスとオプションが今の CLI と合っているかは見ること。

### 2. 記述が今のコードと合っているか

`src/README.md` と `tests/README.md` の内容を、`src/ytsched/` と `tests/` の
実物と突き合わせる。

- モジュール・クラス・メソッドの名前が実在するか（消えた `COOKIE_TODO_DAYS`
  のような、もう無いものを書いていないか）
- `tests/` のファイル一覧と、各ファイルが「何を見ているか」の説明が合っているか
- テストの件数を書いているなら、実際に `pytest` を走らせた数と合っているか

### 3. リンクが辿れるか

6 文書すべての Markdown リンクについて、リンク先が実在するかを確かめる。
**文書ごとに階層が違う**ので相対パスに注意（`docs/` からは `../src/README.md`、
`src/` からは `../docs/data-format.md`）。画像（`docs/fig1.png`、
`docs/javascript-scroll.svg`、`docs/sample1.png`、`docs/refill1.jpg`）への
参照も含める。`README.md` から移した figure が `docs/Developer.md` から
正しい相対パスで参照されているかは特に見ること。

### 4. 移し漏れが無いか

**ここが一番大事。** `CLAUDE.md` は 225 行から 100 行に減っている。
`git diff CLAUDE.md` で消えた記述を 1 つずつ拾い、**それぞれの移り先が
新しい文書のどこかにあるか**を確かめる。`README.md` の「memo」節についても
同じ（`docs/Developer.md` へ移ったはず）。

移り先が無いものがあれば、それを列挙して報告する。
「Claude 向けだったので落として構わない」と自分で判断せず、**落ちている
事実を報告する**（残すかどうかは管理者が決める）。

### 5. 役割分担が守られているか

`TODO.md` の TODO-030 が決めた分担に沿っているか。特に:

- `docs/Developer.md` に**テストの構成**が残っていないか
  （走らせ方だけのはず。構成は `tests/README.md`）
- `src/README.md` に、docstring を読めば分かる細部（メソッドごとの引数の
  一覧など）が書かれていないか
- `docs/data-format.md` の**中身が変わっていないか**
  （相互リンクの追加だけのはず。`git diff` で確認）

## 報告

`archives/agents/TODO-030/verifier-report.md` に書く。
実際に叩いたコマンドと出力を残すこと。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
