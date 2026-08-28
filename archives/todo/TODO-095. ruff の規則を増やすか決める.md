# TODO-095. ruff の規則を増やすか決める

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ |
| 実施 | Opus 5 / effort medium | main + verifier + wording |
| 消費 | output 17,730 / cache_creation 153,154 / 概算 $2.5 |
|      | main 89% + wording 7% + verifier 4%（料金の割合） |

## きっかけ

2026-08-27 の基本設計のレビューの P。ruff は既定の規則（`E4,E7,E9,F`）に
`I` が乗っただけで、TODO-082 は置き場所を `pyproject.toml` へ移しただけ
だった。規則を増やすかは決めていなかった。

「決めるだけ」の項目なので、見込みの担当は `main のみ` にしていた。実際には
`pyproject.toml` と `ytsched.py` を変えたので、確認を verifier に分けた。

## 何を材料に決めたか

候補の規則を実際に走らせて、指摘の数を数えた
（`uv run ruff check --select ALL --statistics src tests`）。

| 規則 | 指摘数 | 中身 |
|------|--------|------|
| `B`（bugbear） | 1 | `ytsched.py:870` の未使用ループ変数 |
| `SIM` | 0 | — |
| `UP`（pyupgrade） | 0 | — |
| `PTH` | 約 45 | `os.path.join` 14、`open` 13、`os.stat` 7 など |
| `RUF` | 約 660 | ほぼ全部 RUF001-003 |
| `D` / `ANN` / `S101` / `COM812` | 1000 超 | — |

`RUF001`-`RUF003`（ambiguous-unicode-character）は、日本語のコメントと
docstring に含まれる全角文字を「紛らわしい」と拾ったもの。**このプロジェクト
では誤検知にしかならない。**

`D`（docstring の書式）・`ANN`（型注釈の欠落）・`S101`（テストの `assert`）・
`COM812`（末尾カンマ）も、今の書き方と合わないので見送った。

## やったこと

- `pyproject.toml` の `extend-select` を `["I"]` から
  `["I", "B", "SIM", "UP"]` にした
- `B007` の 1 件を直した。`ytsched.py` のキャッシュ破棄のループで、
  ループ変数 `i` を本体では使わず、コメントアウトした `debug` の中だけで
  参照していた。`_i` に改名し、コメントの中も揃えた

`PTH` は**足していない**。書き換えが済んでいない状態で有効にすると `lint`
が 45 件出たままになるので、書き換えと同時に足すことにして、TODO-100 を
別に立てた。

## 担当の走らせ方の反省

`wording` を verifier と同時に起動したのは無駄だった。wording の対象には
**担当の報告ファイルも含まれる**（CLAUDE.md）のに、起動した時点では
`archives/agents/TODO-095/verifier-report.md` がまだ無く、対象から漏れた。
結局あとでもう一度走らせることになった。

**wording は、他の担当の報告ファイルが出揃ってから最後に 1 回だけ走らせる。**

## テスト

- `uv run ruff check src tests` — `All checks passed!`
- `mise run lint` / `typecheck` / `test` — verifier が確認
