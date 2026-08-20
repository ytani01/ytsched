# TODO-010. CLAUDE.md の作成

見込み: main = Opus 5 / effort medium、担当 = verifier
実施: main = Sonnet 5 / effort medium、担当 = verifier

## きっかけ

Python 3.14 / uv / pytest への移行が一通り済んだので（TODO-009 まで）、
移行後の構成・コマンド・設計の勘所をまとめた `CLAUDE.md` を作ることにした。

## やったこと

`README.md`（利用者向けの説明）、`pyproject.toml`、`mise.toml`、
`src/ytsched/` 配下の全ファイル（`ytsched.py`・`handler.py`・
`main_handler.py`・`edit_handler.py`・`webapp.py`・`mylog.py`・
`__main__.py`）、`webroot/templates/` のテンプレート、`tests/` の構成を
読み、プロジェクトルートに `CLAUDE.md` を新規作成した。

内容は次の節に分けた。

- 構成（ディレクトリ・ファイルと役割）
- データモデルの勘所（`SchedDataEnt` / `SchedDataFile` / `SchedData` の
  関係、ファイルパスの形式、`utf-8`→`euc_jp` の順で読むエンコーディングの
  扱い、保存時に空でない既存ファイルだけ `.bak` へ退避する挙動、
  `SchedData` によるキャッシュ、`Conf.cgi` の位置づけ）
- Web の構成（`WebServer` の URL prefix、`MainHandler` が GET/POST とも
  同じ `get()` を呼ぶ作り、`base.html` の `{% autoescape None %}` を
  現状維持と決めた経緯への参照）
- コマンド（`mise.toml` のタスクの依存関係、個別コマンド、起動コマンド）
- ログ（`mylog.py` の使い方）

## テスト

`verifier` に、上記の各節が実物のコード・ファイル構成と食い違って
いないかを確認させた。ディレクトリ・ファイルの実在、
`SchedDataFile`/`SchedData`/`Conf.cgi` まわりの記述、`URL_PREFIX` や
`autoescape None` の記述、`mise.toml` のタスク依存順、`mylog.py` の
使い方、いずれも実装と一致しており、日本語表現にも造語や不自然な
直訳は無いとの報告を受けた。指摘は無し。
