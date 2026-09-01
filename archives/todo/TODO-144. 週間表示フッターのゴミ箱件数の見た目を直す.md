# TODO-144. 週間表示フッターのゴミ箱件数の見た目を直す

|        | main                 | 担当            |
| ------ | -------------------- | --------------- |
| 見込み | Opus 5 / effort high | main + verifier |
| 実施   | Opus 5 / effort high | main + verifier |
| 消費   | output 7,015 / cache_creation 39,445 / 概算 $0.7 | |
|        | main 60% + verifier 40%（料金の割合） | |

分担の理由、依頼、報告は
[archives/agents/TODO-144/README.md](../agents/TODO-144/README.md) にある。

## きっかけ

TODO-143 で足したゴミ箱の件数表示について、利用者から 3 点の指摘が出た。

- 数字に下線が付いている
- カッコが要らない
- 文字が小さすぎる

下線は、`.my-bar a.my-btn` が `a` の色だけ打ち消していて
`text-decoration` を指定していなかったため。アイコンだけのボタンでは
見えなかったが、横に文字を出したことで表に出た。

フォントの大きさは `my-fs-medium`（`font-size: medium`）を選んだ。
下線を消す範囲は、span だけでなくバー内のボタン全体にした（他はアイコン
だけなので見た目は変わらない）。どちらも利用者が選択。

フッター上段の `cache_size` の `(N)` はそのままにした（今回はゴミ箱の
件数だけ、と利用者が指定）。

## やったこと

- `my.css` の `.my-bar a.my-btn` に `text-decoration: none` を足した
- `main.html` のゴミ箱リンク内の件数からカッコを外し、クラスを
  `my-fs-xx-small` から `my-fs-medium` へ変えた
- `tests/test_web.py` の件数を見る 2 件のテストは `\(0\)` / `\(2\)` を
  探していたので、カッコとクラスの変更に合わせて書き直した

## テスト

- main: `uv run pytest tests/test_web.py -k trash_count` — 2 件通過
- verifier: `uv run pytest` — 589 件通過。`ruff check` / `basedpyright` /
  `mypy` — 通過
- verifier: `--datadir` に一時ディレクトリを指定してアプリを起動し、
  curl で確認。件数の span がカッコ無しの `my-fs-medium` になっていること、
  `trash.jsonl` に 3 件足すと `3` に変わること、`cache_size` の表示が
  変わっていないこと、配信される CSS に `text-decoration: none` が
  入っていることを確認
- verifier が `ruff format --check` で `tests/test_web.py` の変更 2 行が
  88 桁を超えていることを見つけた。main が `ruff format` を掛けて解消
