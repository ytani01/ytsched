# TODO-036 reviewer への依頼

TODO-036（`click_utils.py` の導入）の変更を見てほしい。**CLI の挙動が
変わる項目**なので入ってもらった。

対象の変更（すべて未コミット。`git diff` と、新規の `click_utils.py`）:

- `src/ytsched/click_utils.py`（新規）
- `src/ytsched/__main__.py`
- `src/ytsched/webapp.py`

背景は `TODO.md` の「TODO-036」の節と
`archives/agents/TODO-036/implementer-request.md`。実装者の報告は
`archives/agents/TODO-036/implementer-report.md`。

## 決まっていること（蒸し返さなくてよい）

利用者との相談で決まったもの。**これらの方針そのものへの異論は要らない**
（方針に沿った実装として問題がある場合は指摘してほしい）:

- `webapp` の `--version` / `-v` は `version_option` に寄せ、
  `WebServer` の `version` 引数と `sys.exit(0)` ごと消す
- `cli` と 3 つのサブコマンドすべてに `click_common_opts` を付ける
- `--version` の表示は `ytsched <ver>`（小文字）のままでよい
- グループ側の `--debug` はサブコマンドへ引き継ぐ
- `click_utils.py` は他のプロジェクトと共通のファイルなので、
  **型ヒント以外は中身を変えない**

## 見てほしいところ

- `_is_debug()` の作りは妥当か。`ctx.obj` が `None` / dict 以外のときの扱い、
  `loggerInit()` が `cli` とサブコマンドで 2 回呼ばれることの影響
- `click_utils.py` の型ヒントが、実際の使われ方と合っているか
  （`Func` / `Decorator` の別名、`click.pass_context` を通した後の型）
- 全コマンドに `version_option` が付いたことによる副作用は無いか
  （eager オプションが処理される順序、`--version` と引数の組み合わせなど）
- `WebServer` から `version` 引数を消したことで、追随できていない箇所は無いか
  （呼び出し元、テスト、テンプレート、文書）
- このリポジトリの決まり（`docs/Developer.md`、`src/README.md`、
  `CLAUDE.md`）からの逸脱
- 文書（`README.md` / `docs/Developer.md` / `src/README.md`）に、
  今回の変更で書き直しが要る箇所は無いか

## やらないこと

- **コードは直さない。** 見つけたことは報告するだけ。直すかどうかは main が決める。

## 報告

`archives/agents/TODO-036/reviewer-report.md` に書く。指摘には重みを付け、
「直すべき」「好みの範囲」「範囲外」を分けること。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
