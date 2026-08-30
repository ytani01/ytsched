# TODO-085 の分担

implementer が実装とテストと文書、verifier が確認を担当した。

新しいモジュール 1 本に加えて `ytsched.py`・テスト・`docs/data-format.md`・
`src/README.md` にまたがるので、実装を分けた。設計（置き場所・1 行の形・
追記する場所）は着手前に利用者と決めてあり、判断の余地が残っていなかった
ので reviewer は入れていない。

verifier には、テストと lint に加えて**アプリを実際に起動して HTTP で
操作し、`trash.jsonl` の中身を見る**ところまでさせた。ゴミ箱に入るのが
「編集後」ではなく「編集前」の内容かどうかは、単体テストだけだと
実装と同じ思い込みのまま通ってしまうため。あわせて、既存のテストが
実データディレクトリに `trash.jsonl` を作ってしまう経路が無いかも
確かめさせている。

報告:

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
