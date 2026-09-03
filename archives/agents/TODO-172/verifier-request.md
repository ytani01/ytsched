# TODO-172 verifier への依頼

## 目的

ゴミ箱画面の見た目を直した変更が、実際に動き、既存の動きを壊して
いないことを確かめる。**コードは直さない。** 見つけたことは報告する。

## 変更したファイル

- `src/ytsched/webroot/templates/trash.html`
- `src/ytsched/webroot/static/css/my.css`

変更の中身は `git diff HEAD` で見られる（未コミット）。

## やったこと（TODO-172 の 3 点）

1. 削除日時（`版 2 ・ … に削除`）を、予定の枠（`.my-date-block`）の
   外から中の 2 行目へ移した（`.my-trash-trashed-at`）
2. 同じ予定の内容が 2 件以上あるグループに
   `.my-trash-group-multi` を付け、背景色 `#CCC` の帯でくくった。
   左右のパディングは `.my-trash-main` のぶんを負のマージンで
   相殺してある（予定の幅を削ってタイトルを折り返させないため）
3. チェックボックス（`.my-trash-select`）を 1.25rem へ大きくし、
   `.my-trash-actions` を `justify-content: center` にして復活ボタンの
   隣へ寄せた

## 完了条件

- [ ] `mise run lint` / `mise run typecheck` / `mise run test` が通る
- [ ] ゴミ箱画面（`/ytsched/trash`）が HTTP 200 で出る
- [ ] 復活（1 件）が動く
- [ ] チェックボックスでの複数選択と、ヘッダーの一括削除が動く
- [ ] ヘッダーの「表示中をすべて選択」が動く
- [ ] ゴミ箱が空のときに「ゴミ箱は空です」が出て、ヘッダーの
      チェックボックスと削除ボタンが無効のまま

## 検証のしかた

**`~/ytsched/data` を触らないこと。** 一時ディレクトリを作り、
`--datadir` に渡す。ポートは **10086** を使う（10085 は管理者が使用中）。

```sh
uv run ytsched webapp --datadir <一時ディレクトリ> --port 10086 &
```

ゴミ箱のデータは `trash.jsonl` を自分で作ってよい。形式は
`docs/data-format.md` の「ゴミ箱」の節にある。**同じ UUID で版が違う行を
2 件以上**入れて、グループ表示も確かめること。

画面は `mise run shot -- http://localhost:10086/ytsched/trash -p <名前>`
で撮れる（`docs/Developer.md` の 6 節）。撮った画像のパスを報告に書く。

終わったらサーバを止める（`pgrep` で PID を確かめてから kill。
`pkill` は使わない）。

## 報告

`archives/agents/TODO-172/verifier-report.md` に書く。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
