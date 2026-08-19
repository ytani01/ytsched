# TODO-001. git リポジトリの初期化

見込み: Sonnet 5 / effort low（サブエージェントなし）
実施: Opus 5 / effort high（サブエージェントなし）

## きっかけ

2021 年に作ったまま `.git` が無く、バージョン管理されていなかった。
TODO-002 で hatch-vcs（git タグからバージョンを決める）を使うので、
git は必須。`setup.cfg` に MIT と書いてあるのに `LICENSE` ファイルも
無かった。

## やったこと

- `git init`。既定ブランチは `master`、作業用に `develop` を切った
  （`tmr` と同じ運用）
- **移行前の状態をそのまま初期コミットした**（`get-pip.py` も含む）。
  移行の前後を履歴で追えるようにするため
- `get-pip.py`（1.9MB）を削除。pip の同梱は uv に移る以上まったく不要
- `LICENSE`（MIT）を追加。年は作成年から現在までで `2021-2026`
- `.gitignore` を `tmr` のものに差し替えた。元は 130 行の
  GitHub 標準テンプレートで、`.python-version` を無視していた
  （TODO-002 でコミットしたいので外れて都合がよい）。
  ytsched 固有で `.claude/settings.local.json` を足した
  （`.claude/agents/` は残したいので、ディレクトリごとは無視しない）

コミットは 3 つに分けた。

1. `chore: 初期コミット（移行前の状態）`
2. `docs(todo): 最新の開発環境への移行を TODO-001〜TODO-012 として立てる`
3. `chore: git リポジトリを初期化し、LICENSE と .gitignore を整える（TODO-001）`

## テスト

テストはまだ無い（TODO-003 で作る）。`git check-ignore -v` で、
`.obsidian/`・`.claude/settings.local.json`・`uv.lock` が無視され、
`.python-version` は無視されないことを確かめた。

## 決めたこと

**`uv.lock` は追跡しない。** `.gitignore` の `*.lock` に含まれる。
`tmr` が同じで、`mise run upgradeproject` が毎回 `rm -f uv.lock` して
`uv sync` し直す（常に最新へ上げる）方針と一貫している。

## 残したこと

`pkgs.txt`（0 バイトの空ファイル）は、この項目の範囲外なので残した。
`setup.py` などと一緒に TODO-002 で片付ける。
