# TODO-157. pyproject.toml の Tombi 警告を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ |
| 実施 | Sonnet 5 / effort medium | main のみ |

## きっかけ

`pyproject.toml` に対して Tombi が `project.license` の deprecated 警告と、
`tables-out-of-order` 警告を 7 件出していた。

## やったこと

- `license = { file = "LICENSE" }` を PEP 639 の SPDX 文字列形式
  `license = "MIT"` に変更した（LICENSE は MIT）
- `build-system` と `dependency-groups` を `tool.*` 系のテーブルより前に
  まとめ、`tool.hatch.*` / `tool.ruff.*` / `tool.mypy.*` /
  `tool.basedpyright` が連続するように並べ替えた

## テスト

`tombi lint pyproject.toml` で警告が消えたことを確認した。
`mise run lint`（`ruff format` / `ruff check` / `basedpyright` / `mypy`）が
通ることも確認した。テーブルの並べ替えとフィールドの表記変更のみで
アプリの挙動には影響しないため、テストは実行していない。
