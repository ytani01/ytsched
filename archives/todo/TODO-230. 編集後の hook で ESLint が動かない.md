# TODO-230. 編集後の hook で ESLint が動かない

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 不明 | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 不明 | 20 | 7,397 | 8,936 | 818,379 | 100% |
| 合計 |  |  | 20 | 7,397 | 8,936 | 818,379 | 計 834,732 |

- 集計は決着のコミットの前のもの
- 追跡するファイルを変えず、確かめる中身もコマンド 1 回で済むので、担当は立てなかった

## きっかけ

TODO-227 で `.js` を編集したとき、`.claude/hooks/fmt-one.sh` が `npx canceled due to missing packages` で止まった。

## やったこと

- このマシンに `node_modules` が無かったのが原因で、`npm ci` で入れた（`docs/Developer.md` の手順）
- hook は `npx --no-install` で呼ぶのが正しいので変えていない

## 確かめたこと

- `eslint` 10.9.1 と `prettier` 3.9.6 が入り、`node_modules` は Git の対象外
- TODO-227 で整形されなかった `edit-page.js` に `prettier --check` と `eslint` をかけ、どちらも通った
- エラーの `eslint@10.14.0` とロックファイルの 10.9.1 が食い違っていた理由は調べていない。入れたあとは起きないので、調べる必要が無くなった

## 残ること

- TODO-231: `npm audit` の警告（5 件）
