# TODO-152 verifier への依頼

## 目的

`docs/User.md` に画面図（6 枚）を入れた。注釈を重ねる `tools/annotate.py`
と、注釈の位置を書いた `tools/user-figs.json` を新しく置いた。
その結果が壊れていないかを確かめる。

## 変更したもの

- `docs/user-week.png` `docs/user-month.png` `docs/user-menu.png`
  `docs/user-search.png` `docs/user-trash.png` `docs/user-edit.png` — 新規
- `tools/annotate.py` — 新規。キャプチャに引き出し線と吹き出しを重ねる
- `tools/user-figs.json` — 新規。注釈の位置
- `docs/User.md` — 図を貼り、本文を整理した。検索バーの擬似図
  （コードブロック）を実画面の図に差し替えた。編集画面の節を足した
- `docs/Developer.md` — 「図に注釈を入れる」を足した
- `mise.toml` — `figs` タスクを足した

## 作った手順（再現できるか確かめるのに使う）

1. 一時ディレクトリにサンプルデータを置く（下記）
2. `uv run ytsched webapp --datadir <一時ディレクトリ> --port <空き port>`
3. `tools/screenshot.py` で 6 画面を撮る（下記）
4. `uv run python tools/annotate.py --srcdir <撮った先> -o /tmp/<試す先>`

撮る順番と高さ:

```sh
B=http://localhost:<port>/ytsched
uv run python tools/screenshot.py "$B/"          -w 412 --height 853 --scale 2 -p week
uv run python tools/screenshot.py "$B/?view=month" -w 412 --height 815 --scale 2 -p month
uv run python tools/screenshot.py "$B/"          -w 412 --height 853 --scale 2 -p menu \
  --open --toggle "#menu-sw"
uv run python tools/screenshot.py "$B/trash"     -w 412 --height 370 --scale 2 -p trash
uv run python tools/screenshot.py "$B/edit?date=2026-09-01&sde_id=<面会の sde_id>" \
  -w 412 --height 545 --scale 2 -p edit
uv run python tools/screenshot.py "$B/?search_str=%E4%BC%9A%E8%AD%B0" \
  -w 412 --height 500 --scale 2 -p search
curl -s -o /dev/null "$B/?search_str=%20"   # 検索を解除して conf.json を戻す
```

**検索は最後に撮る。** `search_str` は `conf.json` に保存され、検索中は
月間表示にならない（`month_mode` より検索モードが優先）。なお
`?search_str=`（空）では解除できない（tornado が空の引数を渡さない）。
空白 1 文字を渡すこと。

サンプルデータ（今日 = 2026-09-01 の週。README のトップ画像と揃えてある）:

```
2026/08/31.jsonl : 07:00-11:00 [朝活] (欠)バックギャモン @泰生ポーチ / 寝坊(^^;)
2026/09/01.jsonl : 10:00-11:30 [面会] 佐藤さん @1Fロビー / 新技術に関する提案
                   15:00-17:00 資料作成 @オフィス / ・データのまとめ ・グラフの作成
                   19:00       [会食] 田中さん @渋谷
2026/09/02.jsonl : 13:00-15:00 [会議] ★事業戦略会議 @会議室1
2026/09/04.jsonl : 18:00-20:00 [パーティー] 親睦会 @六本木
2026/08/24, 08/12, 07/29, 07/08, 06/17 : 検索結果用の「…会議」5 件
ToDo.jsonl       : 2026-09-02 □ToDo 会議資料
trash.jsonl      : 3 件（面会 佐藤さん / [会食] 打合せ #2 / □ToDo 経費精算）
```

## 確かめること

1. `mise run lint`（ruff format / ruff check / basedpyright / mypy /
   eslint / prettier）と `uv run pytest` が通ること
2. `docs/user-*.png` 6 枚が PNG として壊れていないこと（`identify`）
3. `docs/User.md` から 6 枚すべてを参照していて、パスが切れていないこと。
   他の文書からのリンクも切れていないこと
   （`docs/Developer.md` が archives の TODO-152 を指している）
4. **図の中身を目で見る。** 吹き出しが画面の外へはみ出していないか、
   引き出し線が指し示す先とずれていないか、文字が切れていないか
5. `docs/User.md` の本文と図の食い違いが無いか。とくに:
   - 編集画面の 5 つのボタンの説明（戻る／更新／完了／複製／削除）が
     実装（`edit.html` の `data-cmd`、`main_handler.exec_cmd()`）と
     合っているか
   - 検索結果の説明が、擬似図を消したあとも足りているか
6. `tools/annotate.py` が動くこと。上の手順で撮り直してから
   `--only user-week -o /tmp/...` で 1 枚だけ作れること。
   `--only` に無い名前を渡したときにエラーで終わること
7. 実データ（`~/ytsched/data`）に触れていないこと。
   **アプリを起動するときは `--datadir` に必ず一時ディレクトリを指定し、
   port も空いているものを使う**（10085 は別の作業で使われていた）

## 報告

`archives/agents/TODO-152/verifier-report.md` に書く。
**コードや画像は直さないこと。** 見つけたことは報告だけする。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。
