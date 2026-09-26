# TODO

**残っている項目: TODO-200。** これまでに 199 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-201` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-200. メニューから ToDo の日数を変えられない

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Sonnet 5 / high）+ verifier（Sonnet 5 / medium） |

- [ ] ToDo の日数の `<select>` を、選び直したときだけ送信するようにする
- [ ] 検索・フィルタのアイコンは今までどおり押したときに送信する

### きっかけ

フッターの ToDo の日数の `<select>` を押すと、選び直す前にページが
読み直され、値を変えられない。

TODO-108 でインラインイベントをイベント委譲へ移したとき、この `<select>` が
`data-action="submit-form"` になった。`submit-form` は `actionChangeHdr` だけで
なく `actionMouseDownHdr`（`main-page.js:262`）でも拾われるので、`<select>` を
押した時点で今の値のまま送信される。

### 方針

- `<select>` の action を `change` 専用の名前（`submit-on-change`）に変え、
  `actionChangeHdr` の `case` もその名前にする
- 検索・フィルタのアイコン（`<svg>`）の `submit-form` は `mousedown` のまま

### 確認

verifier が Playwright で確かめる。`--datadir` は一時ディレクトリ。
`<select>` をクリックしただけではページが読み直されないこと、
`1w` を選ぶと読み直し後に `1w` が選ばれていて `conf.json` の `ToDo_Days` が
`7` になっていることを、それぞれ 1 回ずつ測る。フィルタのアイコンを押すと
送信されることも 1 回見る。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
