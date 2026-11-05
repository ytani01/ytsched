# TODO-231. `npm audit` の警告を見る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ（決めるだけ。直すなら implementer + verifier を立て直す） |
| 実施 | Opus 5.5 / effort 不明 | main（実行）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 不明 | 30 | 9,112 | 16,226 | 1,642,461 | 74% |
| ver-229（verifier） | Sonnet 5.5 | medium | 34 | 7,176 | 39,931 | 548,359 | 26% |
| 合計 |  |  | 64 | 16,288 | 56,157 | 2,190,820 | 計 2,263,329 |

- TODO-229・TODO-232 と同時に進めたので、集計の範囲が重なっている。main と verifier は 3 項目で共通

## きっかけ

TODO-230 の `npm ci` で、開発用パッケージに 5 件（high 1、moderate 4）の警告が出た。`npm audit --omit=dev` は 0 件。

## やったこと

- `npm audit fix`（`--force` なし）を流し、`package-lock.json` を更新した。`eslint` は 10.9.1 から 10.14.0 になった。high の 1 件が消えた

## やらないと決めた理由（残りの moderate 4 件）

- 残りは `eslint` が依存する `minimatch` などの 4 件で、直すには `--force` で `eslint` を 9.39.5 へ下げるしかない
- 警告は `minimatch` の DoS で、開発用の lint が手元のファイルに使うだけなので実害が小さい。主要バージョンを下げる害の方が大きい。依頼は「やって」だったので main が判断した

## 確かめたこと

verifier の報告は `archives/agents/TODO-231/verifier-report.md`。

- `npm ci` のあと `mise run lint` は終了ステータス 0 で、ESLint の指摘は無い
- `npm audit` は 4 件（moderate 4、high 0）、`npm audit --omit=dev` は 0 件
- ブラウザテストが 4 回に 1 回落ちたが、パッケージとは関係なく TODO-232 で直した

## 分担の振り返り

- **各担当が見つけたもの:** verifier は lint に問題が無いことを確かめ、ついでに走らせたテストの不具合を見つけた
- **見込みと食い違った点:** 見込みは決めるだけだったが、利用者の指示で実行した。`npm audit fix` は 1 コマンドなので implementer は立てなかった
- **次の編成への指示:** 依存関係の更新は main + verifier でよい。`--force` の中身は流す前に `npm audit --json` の `fixAvailable` で見る
