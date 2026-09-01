# TODO-156. notify に `--days` と `--memo` オプションを足す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ（実装）+ reviewer + verifier |
| 実施 | Sonnet 5 / effort medium | main のみ（実装）+ reviewer + verifier |

## きっかけ

`ytsched notify` は 1 日ぶんの予定しか出せなかった。数日先までまとめて
見たい場合や、通知に一言添えたい場合に対応する。

## やったこと

- `src/ytsched/notify.py` の `build_notify_text()` に `days`（既定 1）と
  `memo`（既定 `None`）を足した。`days` は `date` から連続した日数ぶんの
  予定の節を続けて出し、期限が近い ToDo の節は全体の最後に 1 回だけ
  （`date` を基準に判定）出す。`memo` を指定すると、メッセージの先頭に
  出す
- `src/ytsched/__main__.py` の `notify` サブコマンドに `--days`
  （`click.IntRange(min=1)`）・`--memo` を足した
- `docs/Developer.md` のオプション表と説明に追記した

## テスト

`tests/test_notify.py` に、`days` で複数日の節が連続して並ぶこと、
`days` > 1 でも ToDo の節が最後に 1 回だけ出ること、`memo` が先頭に
出ること、`memo` を指定しなければ何も足されないことのテストを足した。

reviewer に別途見させ、`--days` に 0 以下を渡すと検証なしで予定の節が
消える指摘を受けたため、`click.IntRange(min=1)` で弾くようにした
（それ以外の指摘は無し）。

verifier に別途確かめさせ、`ruff format`・`ruff check`・
`basedpyright`・`pytest`（607 件）が通ること、一時ディレクトリで
`ytsched notify --days 3`・`--memo` を実際に実行した出力が期待どおり
であること、`--days` を指定しない既定の挙動がこれまでと変わらないことを
確認した。問題は見つからなかった。詳細は
`archives/agents/TODO-156/verifier-report.md`。
