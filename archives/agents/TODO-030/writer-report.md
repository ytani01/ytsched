# TODO-030 writer 報告

## やったこと

1. **`src/README.md`（新規）** — ソースの構成、`SchedDataEnt` /
   `SchedDataFile` / `SchedData` の関係、`HandlerBase` / `MainHandler` /
   `EditHandler` の関係、フィルタ・検索文字列の扱い、`base.html` の
   autoescape を、開発者が初めて読む順序でまとめた。`migrate.py` を
   モジュール一覧に追加（`CLAUDE.md` の旧「構成」節から漏れていた）。
   個別メソッドの引数は書かず、データ形式・テストの構成は他文書へ委ねた。

2. **`docs/Developer.md`（新規）** — 技術スタック表、開発環境の用意
   （`git clone` → `uv sync`）、`mise` のタスクと依存関係、個別コマンド、
   「テストの走らせ方」（構成は `tests/README.md` へ委譲）、ログの書き方
   （サンプルは `mylog.py` の docstring から転記）、`README.md` の
   「memo」節（JavaScript `Date` の罠、scroll の図）を移した。

3. **`tests/README.md`（新規、追加指示で足した）** — `tests/` の各ファイル
   が何を見ているか、`helpers.py` の役割、ゴールデンマスターテスト
   （TODO-021、`test_handler.py` の `test_settings_are_read`）の位置づけ、
   テストデータの置き場所。走らせ方は書かず `docs/Developer.md` へリンク。

4. **`CLAUDE.md`** — 「構成」「データモデルの勘所」「Web の構成」
   「コマンド」の 4 節を「コードを触る前に読むこと」に置き換え、
   `src/README.md` / `docs/Developer.md` / `tests/README.md` /
   `docs/data-format.md` への案内にした。「ログ」は守るべき一行だけ残し、
   サンプルは `docs/Developer.md` へのリンクにした。「これは何か」
   「サブエージェントの分担」はそのまま残した。

5. **`README.md`** — 「memo」節を削除し、末尾に「開発者向け」節を足して
   `docs/Developer.md` / `docs/data-format.md` へリンクした。インストール・
   systemd の手順はそのまま残した。

6. **`docs/data-format.md`** — 中身は変えず、「この文書について」に
   `src/README.md` / `docs/Developer.md` / `tests/README.md` /
   `README.md` への相互リンクを 1 段落だけ足した。

## 確かめたこと

- `src/ytsched/*.py` を実際に読んで一覧・クラス関係・フィルタ処理
  （`compile_filter` / `compile_search` / `search_mode`）を確認
  （`wc -l`、`grep -n "^class \|^def "`、`Read` で各ファイル）。
- `mylog.py` の docstring 中のログ用サンプルコードをそのまま転記。
- `tests/helpers.py`・各 `test_*.py` の冒頭 docstring・`wc -l` で
  役割を確認。
- コマンド例は実行して確認: `uv --version` / `mise tasks` /
  `uv run ytsched --help`（`migrate` / `webapp` / `x-data1` の出力を確認）、
  `uv run ytsched webapp --datadir <一時ディレクトリ> --port 10199` を
  起動し `curl` で `200` を確認してから停止、`uv run pytest tests -q`
  （330 件 pass、ドキュメント変更の前後どちらも実行）。
- 6 文書すべての Markdown リンクを `realpath -m` で解決し、全リンクが
  存在するファイルを指すことを確認（スクリプトで一括チェック）。

## 判断が要る点

特になし。追加指示（`tests/README.md` の新規作成、`docs/Developer.md` の
「テストの構成」を走らせ方だけに絞る、リンクを 6 文書に拡張）も反映済み。

## 追記（verifier の指摘への対応）

`src/README.md` のみを直した（他の文書は触っていない）。

1. 「データモデル」節の `SchedDataEnt` の項目に、`detail` は素のテキスト
   のままで、画面の改行表示は CSS の `white-space: pre-wrap` が担う旨
   （テンプレート側でタグを差し込んでいるわけではない）を足した。
   `webroot/static/css/my.css`（`.longtext-sw:checked ~ .longtext` に
   `white-space: pre-wrap` が今もある）と `webroot/templates/sde.html`
   （`{{ detail }}` をそのまま埋め込んでいるだけで、タグは差し込んで
   いない）を実際に読んで確認した。
2. 「データモデル」節の `SchedDataFile` の項目に、パスの決め方は
   `date2path()` が担うこと、規則は `docs/data-format.md` にあることを
   一言足した。
