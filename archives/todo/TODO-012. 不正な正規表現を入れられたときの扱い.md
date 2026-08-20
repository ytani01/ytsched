# TODO-012. 不正な正規表現を入れられたときの扱い

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier
実施: main = Opus 5 / effort medium、担当 = implementer + verifier

分担の理由と各担当の報告は `archives/agents/TODO-012/` にある。

## きっかけ

`filter_str` / `search_str` は利用者の入力をそのまま `re.search()` へ
渡していた。`re.error` を捕まえたあと `continue` していたため、
打ち掛けの正規表現（`(` だけ、など）を入れた瞬間に全件が消えていた。
警告はログにしか出ないので、画面からは理由が分からない。

## やったこと

- `get()` の中で正規表現を 1 回だけコンパイルするようにし、ループの中に
  散らばっていた `try` / `except re.error` をすべて無くした。
  `main_handler.py` に `compile_re()` と `filter_match()` を足した
- コンパイルに失敗したら `warning` をログへ出し、**その条件を無視して
  全件を出す**（`continue` をやめた）
- 検索モードかどうかの判定を、「`search_str` が空でないか」から
  「正規表現としてコンパイルできたか」へ変えた。`main.html` の
  `{% if search_str %}` のうち、検索モードを見ていた 2 箇所
  （検索期間・件数のバー、年の見出し）も `search_mode` に変えた。
  入力欄の `value` と JS の `search_str0` は表示用なのでそのまま
- `main.html` の先頭に、Bootstrap の `alert alert-danger` で警告
  メッセージを 1 行出すようにした。フィルタと検索の両方が不正なときは
  ` / ` で区切って 1 行に並べる

決めたこと。

- **入力欄の文字列と `Conf.cgi` への保存は今までどおり残す。**
  不正な文字列を消すと、打ち掛けのものを直せなくなる。マッチに使うか
  どうかだけを分けた
- **保存された不正な文字列でも、警告メッセージは出し続ける**
  （2026-08-20）。絞り込みが無視された状態は続くので、出さないと
  「なぜ絞り込まれていないのか」が分からなくなる
- **`base.html` の `{% autoescape None %}` は現状維持**（切ったまま）。
  単一ユーザで、リバースプロキシで認証する前提。自分が書いたものが
  自分に見えるだけなので実害が無い。エスケープを切っている理由と
  されていた「`detail` の `<br />` を通すため」は今はもう成り立って
  いない（読み込み時に `htmlstr2text()` で改行へ戻され、表示は CSS の
  `white-space: pre-wrap` が担っている）が、全テンプレートの `{{ }}` を
  洗い直す手間に見合わないので戻さない

## テスト

`tests/test_web.py` の `test_invalid_regex`（200 が返ることだけを見て
いた）を、次の 6 つに書き直した。

- `test_invalid_filter_str_shows_all`
- `test_invalid_filter_str_negative_shows_all`
- `test_invalid_search_str_shows_all`
- `test_invalid_filter_str_and_search_str`
- `test_valid_search_str_shows_search_bar`
- `test_invalid_filter_str_is_saved`

`uv run pytest tests` は 174 件すべて通る。basedpyright と mypy も
エラー無し。`ruff check` の指摘は TODO-015 の分が残っているが、
`main_handler.py` と `tests/test_web.py` に絞ると HEAD の 25 件から
23 件へ減っており、増えていない。

verifier がアプリを起動して確認した範囲では、正しい正規表現のときの
絞り込み・検索・`search_n` による打ち切り・ToDo への絞り込み・`!` 付きの
否定フィルタは今までどおり動いている。`![` のように否定付きで中身が
不正な場合も、正しく「フィルタが不正」と判定される。
