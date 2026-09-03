# TODO-168. `ruff` が `archives/` を見ないようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort medium | main + verifier |
| 消費 | output 7,608 / cache_creation 53,888 / 概算 $1.0 |
|      | main 93% + verifier 7%（料金の割合） |

分担の理由と verifier の報告は
[archives/agents/TODO-168/](../agents/TODO-168/README.md) にある。

## きっかけ

`ruff format` は Markdown の中の ```` ```python ```` ブロックも整形する。
TODO-167 で implementer が対象パスを指定せず `uv run ruff format` を叩いた
ところ、`archives/` 以下の報告ファイル 9 件と
`archives/agents/TODO-060/probe.py` が書き換わった（管理者が戻した）。
`archives/` は決着した項目の記録で、整形の対象ではない。

`mise run fmt` は `src tests tools` に絞ってあるのでタスク経由では起きない。
効くのは `pyproject.toml` 側で、そこに書けば対象を指定せずに叩いたときも
`ruff check` も `archives/` を見なくなる。

## やったこと

`pyproject.toml` の `[tool.ruff]` に `extend-exclude = ["archives"]` を足した。
変更はこの 1 箇所だけ。

`exclude` ではなく `extend-exclude` にしたのは、ruff の既定の除外
（`.git`、`.venv`、`__pycache__` など）を残したまま足すため。`exclude` に
書くと既定を上書きしてしまう。

## テスト

verifier が確かめた。

- 対象パスを指定せずに `uv run ruff format --check .` と
  `uv run ruff check .` を叩き、出力にも `ruff check --show-files` の
  ファイル一覧にも `archives/` のパスが出ないこと
- `src tests tools` を指定したときの結果が変わらないこと
  （`41 files already formatted` / `All checks passed!`）
- `git status` の差分が `pyproject.toml` だけであること
