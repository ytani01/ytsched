# TODO-031 writer 報告

## 実物の確かめ方

以下を実際に読んでクラス名・メソッド名・URL・継承関係を確認した。

- `src/ytsched/ytsched.py`（`SchedDataEnt`/`SchedDataFile`/`SchedData`）
- `src/ytsched/handler.py`（`HandlerBase`）
- `src/ytsched/main_handler.py`（`MainHandler`。`post()` が `self.get()` に
  委譲するだけであること、`get_conf_arg()` が値を `Conf.cgi` へ保存する
  経路も確認）
- `src/ytsched/edit_handler.py`（`EditHandler`。`post()` も `self.get()` を
  呼ぶだけ）
- `src/ytsched/webapp.py`（`WebServer` が `tornado.web.Application` に渡す
  URL の一覧。`/`・`url_prefix`・`url_prefix/` が `MainHandler`、
  `url_prefix/edit`・`url_prefix/edit/` が `EditHandler`）
- `src/ytsched/migrate.py`・`docs/data-format.md`「変換の手順」（デコードの
  分岐、項目数 7 未満/8 以上の分岐）

## 入れた図

- `src/README.md`「データモデル」節: `classDiagram`。
  `SchedDataEnt`/`SchedDataFile`/`SchedData` の積み上がりと、
  `MainHandler`/`EditHandler` が `SchedData` 経由でアクセスすることを表現
- `src/README.md`「Web ハンドラ」節: `classDiagram`。
  `tornado.web.RequestHandler` → `HandlerBase` → `MainHandler`/`EditHandler`
  の継承と、`WebServer` が割り当てる URL
- `src/README.md`: 新しく「リクエストが来てから画面が出るまでの流れ」節を
  「Web ハンドラ」節のあとに作り、`sequenceDiagram` を追加。
  `Conf.cgi` をリクエストのたびに読む点、`post()` が `get()` に委譲する点、
  キャッシュに当たればファイルを読まない点を示した
- `docs/data-format.md`「変換の手順」節: `graph TD`。デコードの分岐
  （utf-8 → euc_jp → `errors="replace"`）と、項目数 7 未満/8 以上の分岐を
  表現

いずれも `style`/`classDef` は使わず、既存の文章は削っていない。

## 気づいたこと（コードと文書の食い違い）

食い違いは見つからなかった。文書の記述（`src/README.md` の各節、
`docs/data-format.md`「変換の手順」）はコードの実装と一致していた。

## 書けなかったところ

「GitHub で実際に図として表示されるか確かめる」は行っていない
（このリポジトリの手元には `mermaid-cli` を入れない方針のため、構文の
目視確認までにとどめた）。
