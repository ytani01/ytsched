# TODO-032 reviewer への依頼

`Conf.cgi`（タブ区切り）を `conf.json`（JSON）にする変更が、作業ツリーに
入っている（未コミット）。`git diff` で全体を見てほしい。

実装の依頼書は `implementer-request.md`。決まっていることは `TODO.md` の
TODO-032 の節にある。**実装者はセッションの上限で途中終了した**ので、
やり残しや中途半端なところが残っている可能性がある。

lint・型チェック・テストは main が走らせて通ることを確認済み。動作確認は
verifier が別に進めている。**こちらはコードの質を見てほしい。**

## 見てほしいところ

- `handler.py` の `load_conf()` / `save_conf()` — 壊れた JSON、
  トップレベルが dict でない、値が文字列でない、の 3 つの扱いが
  そろっているか。書き出しの形（`ensure_ascii=False` / `indent=2` /
  末尾の改行）に落とし穴が無いか
- `migrate.py` の `conv_conf()` / `migrate_conf()` — 既存の
  `conv_file()` / `migrate_file()` との一貫性。行のデコードや空行の
  扱いを、他の変換とそろえられているか。`main()` の中の呼ぶ位置と
  出力の書式
- **範囲を超えた変更が混じっていないか。** 今回は形式の変更だけで、
  `main_handler.py` の `get_conf_arg()` / `convert_value()` の挙動は
  変えないと決めている
- テストが、旧テストで見ていたことを落としていないか
  （`test_handler.py` はタブ特有のテストを差し替えている）
- プロジェクトの決まり（`CLAUDE.md`、`src/README.md`）からの逸脱

## やらないこと

- **コードは直さない。** 見つけたことは報告するだけ。
- `mise run upgradeproject` は走らせない。

## 報告

`archives/agents/TODO-032/reviewer-report.md` に書く。返事は
「終わったか・報告のパス・判断が要る点」の 5 行以内。
