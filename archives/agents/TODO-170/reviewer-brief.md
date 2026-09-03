# TODO-170 reviewer への依頼

## 目的

`ytsched fix-id`（TODO-170）の実装をレビューする。**全データを一括で
書き換えるコマンドで、失敗すると実データが壊れる**ため、データを失う
道が無いかを最優先で見る。

## 見る範囲

- `src/ytsched/fix_id.py`（新規）
- `src/ytsched/__main__.py` の `fix-id` サブコマンド（差分だけ）
- `tests/test_fix_id.py`（新規）

仕様は `TODO.md` の TODO-170 の節、実装の説明は
`archives/agents/TODO-170/implementer-report.md`。

## 特に見てほしいところ

- **行を失う道が無いか。** 読めない行・空行・末尾の改行の有無・
  空ファイル・改行で終わらないファイル。`SchedDataFile.split_lines()` の
  戻り値の仕様と、書き戻すときの `b"\n"` の付け方が噛み合っているか
  （元のファイルに無かった改行を足していないか、逆に落としていないか）
- 一時ファイル → `Path.replace()` の書き戻しで、途中で落ちたときに
  元のファイルが壊れないか。一時ファイルが残らないか。`fsync` の要否
- `sde_id` 以外を変えていないと言い切れるか
  （`json.dumps` の区切り文字、`ensure_ascii`、非 ASCII、`null`、
  数値の書き戻し、U+2028 のような文字）
- 対象ファイルの選び方（`DAILY_GLOB`）が広すぎないか・狭すぎないか。
  `trash.jsonl` や `.bak`、旧 `.cgi` を拾わないか
- テストが仕様を実際に見ているか。抜けている観点
- `_log = getLogger(__name__)` が使われていない（main も気づいた）。
  他のモジュールと揃っているかどうかも含めて見てほしい
- プロジェクトの決まり（`CLAUDE.md`、`src/README.md`、ログの書き方、
  docstring の形）からの逸脱

## やらないこと

- **コードを直さない。** 見つけたことは報告に書く。直すかどうかは main が決める
- テストの実行は verifier が別に行うので、走らせなくてよい

## 報告

`archives/agents/TODO-170/reviewer-report.md` に書く。指摘は重い順に
並べ、それぞれ「どこが・なぜ問題か・どうなると壊れるか」を書く。
返事は 5 行以内。
