# TODO

**残っている項目: TODO-221、TODO-222。** これまでに 220 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-223` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-221. 毎朝の通知で、予定の無い日を省けるようにし、詳細も出せるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `ytsched notify` に `--skip-empty` を足す。`--days` で複数日を出すとき、
  予定の無い日を出さない
- [ ] 全部の日に予定が無いときは、期間の見出し
  （`2026-10-05 (月) 〜 10-11 (日)`）の下に「予定なし」を 1 行出す
- [ ] `ytsched notify` に `--detail` を足す。予定の行の下に detail を全行、
  予定の行より 1 段深く字下げして出す
- [ ] テストを足す
- [ ] `docs/User.md`・`docs/Developer.md` の使用例を書き足す

背景: TODO-153 の毎朝の通知を広げる。利用者と次のように決めた。

- どちらもオプションで指定したときだけ有効にする。指定しなければ今の出力と
  変わらないので、今の cron の設定は変えなくてよい
- 予定も ToDo も無い日でも 1 通は届く、という今の動きは変えない
- 場所（place）の表示と Web 画面へのリンクは、今回は足さない
  （リンクは TODO-222 で扱う）

---

## TODO-222. ytsched notify で、日付をリンクにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `ytsched notify` に `--url` を足す。**指定したときだけ**、日付の見出しを
  Slack の `<URL?date=YYYY-MM-DD|日付>` の形のリンクにする。
  指定しなければ今の出力のまま
- [ ] `--url` を指定したときは、予定の行を、時刻の桁が揃うよう行ごとに
  `` ` `` で囲む
- [ ] `slack-send.sh` に、本文をコードブロックで囲まずに送るオプションを足す
  （このリポジトリの外。`~/bin/slack-send.sh`、元は
  [slack-send](https://github.com/ytani01/slack-send)）
- [ ] テストを足し、`docs/User.md`・`docs/Developer.md` に `--url` の例を足す

背景: `slack-send.sh` は本文全体を ```` ``` ```` で囲んで送る
（`~/bin/slack-send.sh` の `jq` の行）。コードブロックの中ではリンクに
ならないので、`slack-send.sh` の側も変える。リンク先の
`?date=YYYY-MM-DD` は Web 画面がそのまま受け付ける（`main_binder.py` の
`date` 引数）。リンクは `--url` を指定したときだけ付けると利用者と決めた
（既定の URL は持たない）。

注意:

- `--url` と、`slack-send.sh` の素通しのオプションは組にして使う。
  片方だけだと、`<URL|日付>` や `` ` `` が文字のまま出る
- TODO-221 の `--detail` で出す詳細の行も、`--url` のときに `` ` `` で
  囲むかを揃える。先に済んだほうに合わせる

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
