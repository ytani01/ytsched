# TODO-107 計画確認の語彙確認（wording）

## 結果

HEAD に前例の無い候補語は 15 語あった。いずれも一般的な技術用語か
普通の説明であり、リポジトリ独自の言い換えには見えない。

| 語 | 出てくるファイルと箇所 | 前例件数 | 見立て |
| --- | --- | ---: | --- |
| `公開範囲` | `TODO.md:82` | 0 | 公開する対象の範囲を指す普通の説明。 |
| `暗黙のグローバル変数` | `TODO.md:77`、`verifier-plan-report.md:29,57` | 0 | JavaScript で宣言せずに作られるグローバル変数を指す一般的な技術用語。 |
| `不要な引数` | `TODO.md:78`、`verifier-plan-report.md:26,29,57` | 0 | 使われていない引数を指す普通の説明。 |
| `計画確認` | `README.md:8`、`verifier-plan-report.md:1` | 0 | 計画を確認する工程を表す普通の説明。 |
| `技術上の必須前提` | `verifier-plan-report.md:8` | 0 | 技術的に必須ではないことを説明する表現。少し硬いが意味は明確。 |
| `名前空間経由` | `verifier-plan-report.md:19` | 0 | 名前空間を介した参照を指す普通の説明。意味は明確。 |
| `自動収集` | `verifier-plan-report.md:36` | 0 | 自動で収集する動作を指す普通の説明。 |
| `変更規模` | `verifier-plan-report.md:53` | 0 | 変更の大きさを指す普通の説明。 |
| `公開方針` | `verifier-plan-report.md:34` | 0 | 何を公開するかの方針を指す普通の説明。 |
| `検証方法` | `README.md:4` | 0 | 検証の方法を指す普通の説明。 |
| `現行コード` | `README.md:3` | 0 | 現在のコードを指す普通の説明。 |
| `公開名` | `verifier-plan-report.md:31` | 0 | 外部へ公開する名前を指す普通の説明。意味は明確。 |
| `依存先` | `verifier-plan-report.md:31` | 0 | 依存する対象を指す一般的な技術用語。 |
| `値の渡し方` | `TODO.md:82`、`verifier-plan-report.md:32` | 0 | 値を受け渡す方法を指す普通の説明。 |
| `表示結果・操作` | `verifier-plan-report.md:24` | 0 | テストで確認する対象を並べた普通の説明。 |

造語には見えない。`技術上の必須前提` と `名前空間経由` は
このリポジトリでは初出だが、文脈から意味を迷わず読み取れるため、修正は
不要と見立てる。

## 読んだファイル

- `TODO.md`
- `archives/agents/TODO-107/README.md`
- `archives/agents/TODO-107/verifier-plan-report.md`
- `archives/agents/TODO-107/wording-plan-report.md`（この報告自身）

前例なし語数: 15 語。
