# TODO-008. uv tool install 方式へ — 分担

## 分担

| 担当 | 範囲 | 報告 |
|---|---|---|
| main（Sonnet 5 / medium） | 下調べ（`DEF_WEBROOT` / `DEF_DATADIR` の実装確認）、依頼と取りまとめ | — |
| `implementer` | `install.sh` / `Ytsched.src` の削除、`uv tool install` の手順確認、systemd --user ユニット例の作成 | [implementer-report.md](implementer-report.md) |
| `verifier` | 削除の確認、`uv tool install` からの起動と HTTP 応答の再確認、ユニット例の構文検証 | [verifier-report.md](verifier-report.md) |

依頼書は [implementer-request.md](implementer-request.md) /
[verifier-request.md](verifier-request.md) にある。

## この分担にした理由

常設の定義（implementer + verifier）で足りると判断した。設計の余地が
小さく（`pyproject.toml` の `[project.scripts]` は TODO-004 で既に
入っている）、`reviewer` は付けていない。

## 決着

項目そのものの記録は
[archives/todo/TODO-008. uv tool install 方式へ.md](../../todo/TODO-008.%20uv%20tool%20install%20方式へ.md)
にある。
