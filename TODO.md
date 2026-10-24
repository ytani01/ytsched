# TODO

**残っている項目: TODO-226。** これまでに 225 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-227` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-226. 編集画面で Ctrl+Enter で確定する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus / high）+ verifier（Sonnet / medium） |

- [ ] 編集画面のどの欄でも Ctrl+Enter（Mac は Cmd+Enter も）で確定（`cmd=fix`）する。端末の判定はしない
- [ ] Enter 単独は今どおり（詳細欄は改行、他は何もしない）。日本語入力の変換中（`isComposing`）は無視する

**無駄を省く工夫:** 確定は既存の `submitCmd("fix")` を通すので、保存の中身は確かめ直さない。verifier は Playwright で、1 行の欄・詳細欄で Ctrl+Enter を 1 回ずつ、詳細欄の Enter 単独を 1 回送るだけにする。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
