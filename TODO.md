# TODO

**残っている項目: TODO-208〜209。** これまでに 207 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-210` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-208. trash.jsonl にデコードできないバイトがあると一覧が 500 になるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `TrashFile` の `entries()`・`count()`・`delete_many()` で、デコード
      できない行はその行だけ警告して飛ばす（`delete_many()` は元のバイトの
      まま残す。壊れた行を消さない方針は今と同じ）
- [ ] 不正なバイトを含む `trash.jsonl` で、一覧・ゴミ箱画面・一括削除が
      動くテストを足す

テキストモードで開いていて、デコードは `try` の外（`for line in f`）で
起きる。`count()` は `MainHandler.get()` が毎回呼ぶので、一覧画面ごと
500 になる。`SchedDataFile` はバイトで読んで行ごとにデコードしている。

---

## TODO-209. レビューで見つかった小さい食い違いをまとめて直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

- [ ] `ConfFile.DEF_CONF` の `ToDo_Days` を `"1y"` から `"365"` にする。
      `tests/test_handler.py:334`（`TODO_DAYS[...]` で引いている）も直す
- [ ] `holiday.py` の `urlopen()` にタイムアウト（30 秒）を付ける
- [ ] 使われていない `SchedData.sdf_has_sde()` と、そのテストを消す
- [ ] `base.html` の `{% autoescape None %}` を消す
- [ ] `src/README.md` を実装に合わせる: CLI の数（5 つ）、
      `load_month_cal()` の判定のしかた、「テンプレートの autoescape」の節

`"1y"` は `int()` で読めず、リクエストのたびに WARNING が出る（値は既定の
365 に落ちるので表示は変わらない。2026-09-30 に実測）。**既にある
`conf.json` は書き換えない**ので、手元の `"1y"` は画面で ToDo の日数を
一度変えるか、手で直す。

`{% autoescape None %}` は tornado では書いたファイルの中だけに効き、
`base.html` にはそのあと式が無いので何も変えていない。子テンプレートは
エスケープされている（2026-09-30 に実測）。`src/README.md` の
「エスケープを切っている」はこれと食い違う。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。
