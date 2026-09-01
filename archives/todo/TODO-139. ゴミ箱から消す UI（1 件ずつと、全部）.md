# TODO-139. ゴミ箱から消す UI（1 件ずつと、全部）

|        | main                    | 担当                                       |
|--------|-------------------------|--------------------------------------------|
| 見込み | Opus 5 / effort medium  | implementer + verifier + reviewer          |
| 実施   | Opus 5 / effort medium  | implementer + verifier + reviewer + writer |
| 消費   | output 59,447 / cache_creation 630,501 / 概算 $8.1 |
|        | main 43% + implementer 31% + verifier 19% + reviewer 5% + writer 3%（料金の割合） |

## きっかけ

ゴミ箱画面（TODO-086）には「復活」しか無く、消した予定は `trash.jsonl`
にたまる一方だった。1 件ずつ完全に消すのと、全部まとめて消すのを画面から
できるようにする。

## やったこと

- `TrashFile`（`trash.py`）に `delete(sde_id, trashed_at)` と `clear()`
  を足した。どちらも `trash.jsonl` を全件書き直すが、**`.bak` は
  作らない**（ゴミ箱のゴミ箱になって意味が無いため）。書き直しは、
  同じディレクトリの一時ファイルへ書いてから `Path.replace()` で
  差し替える。**JSON として読めない行は書き直しでも残す**（`entries()`
  は警告して飛ばすだけなので、書き直しで消すと復旧の手がかりが失われる）
- `TrashHandler.post()` の `cmd` を `restore` / `delete` / `clear` の
  3 つに分けた。`delete` / `clear` のあとはゴミ箱画面へ redirect する
- `trash.html` に、行ごとの削除ボタンと、ヘッダの「空にする」ボタンを
  足した。**どちらも `confirm()` で確認をはさむ**（消したら戻せないため。
  単一ユーザ用のアプリなので、間違いタップを止められればよい）。
  `?sde_id=` で絞り込んで開いているとき、および 0 件のときは「空にする」を
  出さない（出ているものだけが消えるのか全部消えるのかが紛らわしいため）。
  0 件のときは「ゴミ箱は空です」を出す
- **確認は `data-confirm` 属性と `trash-page.js`（新規）で行う。**
  最初は `onsubmit="return confirm(...)"` を指示していたが、TODO-108 で
  インラインイベントハンドラを禁止しており、`tests/test_web.py` の
  `test_templates_have_no_inline_event_handlers` が落ちる。implementer が
  読み替えて報告してきた
- 削除した日時は、秒までを表示する（`trash.jsonl` にはマイクロ秒まで
  持つが、それは同じ `sde_id` を短時間に何度も削除したときの区別に
  使う値で、画面に出す意味は無い）
- 削除ボタンと「空にする」は控えめな赤（`#C33`）にして、復活ボタンと
  見分けられるようにした

## スクリーンショットで見つけた表示崩れ

テストが全件通ったあとにスマホ幅（390px）で画面を撮ったら、3 つ崩れて
いた。**どれもテストでは分からない。**

- 「空にする」をヘッダの 2 行目に置いたため、ヘッダが高くなった分だけ
  1 件目が隠れた（`.my-trash-main` の `padding-top: 55px` はヘッダ
  1 行ぶんしかない）。→ **ヘッダは 1 行のままにして、「空にする」は
  リストの一番下へ移した。** 全部消すのはリストを見終わってからの操作
  なので、下にあるほうが誤タップも減る
- 削除ボタンを足すぶん列幅を `col-2/2/6/2` に振り直したら、日付
  （`2026/09/06 (Sun)`）が折り返して時刻と重なった
- ボタン列が狭く、復活と削除のアイコンが縦に並んだ

`col-3`（日付）/ `col-2`（時刻）/ `col-4`（種別・タイトル）/ `col-3`
（ボタン）に直し、ボタン列は flex で横に並べた。

## 見送ったこと

- **1 件削除したあとの redirect 先は、絞り込みを維持せず常に
  `/ytsched/trash`。** reviewer から「`?sde_id=` で絞り込んで開いていると
  削除後に絞り込みが外れる」と指摘があったが、`?sde_id=` へのリンクは
  テンプレートにも JavaScript にも無く、URL を手で打つときしか使わない。
  実際に困る場面が無いので現状のままにした

## テスト

`tests/test_trash.py` に `TrashFile.delete()` / `clear()` の単体テスト
（1 行だけ消える・他の行と壊れた行が残る・見つからないときに `False`・
ファイルが無くても落ちない・パーミッションが変わらない）、
`tests/test_web.py` の `TestTrashHandler` に `cmd=delete`（成功・404）と
`cmd=clear` の HTTP テストを足した。

## 確認

verifier が `uv run pytest`（578 件）・`ruff format --check` /
`ruff check` / `basedpyright` を通し、一時データディレクトリでアプリを
起動して、1 件削除で同じ `sde_id` の別の行が巻き添えにならないこと、
`confirm()` のキャンセルで送信されないこと（playwright で
`page.on("dialog", ...)` を `dismiss()`）などを実測した。報告は
[archives/agents/TODO-139/verifier-report.md](../agents/TODO-139/verifier-report.md)。

**verifier と reviewer が独立に、書き直しで `trash.jsonl` の
パーミッションが 0644 から 0600 に変わることを見つけた**
（`tempfile.mkstemp()` が 0600 で作った一時ファイルを、そのまま差し替えて
いたため）。`SchedDataFile.save()` は既存ファイルのパーミッションを保つ
ので、そちらに合わせて `os.fchmod()` で引き継ぐよう直した。**pytest は
この不具合があるときも 578 件すべて通っていた。** reviewer の報告は
[archives/agents/TODO-139/reviewer-report.md](../agents/TODO-139/reviewer-report.md)、
分担の理由は
[archives/agents/TODO-139/README.md](../agents/TODO-139/README.md)。
