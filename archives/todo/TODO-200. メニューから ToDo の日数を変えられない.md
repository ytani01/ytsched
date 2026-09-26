# TODO-200. メニューから ToDo の日数を変えられない

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Sonnet 5 / high）+ verifier（Sonnet 5 / medium） |
| 実施 | Opus 5.5 / effort high | main（実装）+ reviewer（Sonnet 5 / high）+ verifier（Sonnet 5 / medium） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5.5 | high | 3,220 | 8,451 | 60% |
| verifier | Sonnet 5 | medium | 1,160 | 39,746 | 27% |
| reviewer | Sonnet 5 | high | 1,704 | 32,685 | 13% |
| 合計 |  |  | 6,084 | 80,882 | 概算 $1.1 |

- 集計は決着のコミット前の時点まで。main の分は決着の作業ぶん少し増える

## きっかけ

フッターの ToDo の日数の `<select>` を押すと、選び直す前にページが
読み直され、値を変えられなかった。

TODO-108 でインラインイベントをイベント委譲へ移したとき、この `<select>` が
`data-action="submit-form"` になった。`submit-form` は `actionChangeHdr` だけで
なく `actionMouseDownHdr` でも拾われるので、`<select>` を押した時点で
今の値のまま送信されていた。

## やったこと

- `main.html`: `<select id="todo_days">` の action を `submit-on-change` にした
- `main-page.js`: `actionChangeHdr` の `case "submit-form"` を
  `case "submit-on-change"` にした。change で `submit-form` を使う要素は
  ほかに無い
- 検索・フィルタのアイコン（`<svg>`）の `submit-form` は mousedown のまま

## 確かめたこと

verifier が Playwright（390×844、一時 datadir）で実測した
（[報告](../agents/TODO-200/verifier-report.md)）。

- `<select>` を押しただけでは読み直されない
- `1w` を選ぶと送信され、読み直し後の値が `7`、`conf.json` の `ToDo_Days` が `"7"`
- フィルタのアイコンを押すと送信される
- 変更前に戻すと、`<select>` を押しただけで読み直しが起きる（不具合の再現）

## 分担の振り返り

- reviewer: 指摘なし。change・mousedown の両方で拾われる要素がほかに無いことを確かめた
- verifier: 3 項目と不具合の再現のすべてで期待どおりの値を得た。食い違いなし
- 見込みと実施は同じ
- 次に同じ規模（テンプレートと JS の 2 か所、分岐 1 つ）なら、reviewer は
  effort medium で足りる。確認する範囲が `rg` 1 回で済む。verifier は
  変更前の再現まで含めて今回の組み方のままでよい
