# TODO-168 の分担

| 担当 | 何を任せたか |
|------|--------------|
| main（Opus 5 / effort medium） | `pyproject.toml` の 1 行の変更、依頼の作成、文書の仕上げ |
| verifier | 対象パスを指定せずに `ruff` を叩き、`archives/` が対象外になったことの確認 |

## この分担にした理由

設定ファイルに 1 行足すだけで、実装を分ける規模ではない（implementer は
立てていない）。一方で確かめる中身は「対象パスを指定せずに叩いたときに
`archives/` が本当に外れるか」で、実際に走らせないと分からない。
`CLAUDE.md` の「試せる手順があるなら分ける」に当たるので verifier を分けた。

挙動の変わるコードは無いので reviewer は入れていない。

- [verifier への報告](verifier-report.md)（依頼は Agent ツールで直接渡した）
