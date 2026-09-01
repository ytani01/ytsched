# TODO-140. ゴミ箱の「空にする」をヘッダーへ移し、空にしたら週間表示へ戻る

|        | main                     | 担当                       |
| ------ | ------------------------ | -------------------------- |
| 見込み | Sonnet 5 / effort medium | main + verifier + reviewer |
| 実施   | GPT-5 / effort high      | main + verifier + reviewer |

分担の理由と報告は
[archives/agents/TODO-140/README.md](../agents/TODO-140/README.md) にある。
`tools/token-usage.py` は Claude Code の transcript を集計する仕組みで、
Codex で行ったこの項目は集計できないため、消費の行は省いた。

## きっかけ

ゴミ箱の「空にする」が一覧の末尾にあり、件数が多いとスクロールしないと
操作できなかった。また、空にしたあとは「ゴミ箱は空です」と表示するだけの
ゴミ箱画面に留まっていた。

## やったこと

- ゴミ箱のヘッダーを、左の戻るボタン、中央の「ゴミ箱」と件数、右の
  「空にする」アイコンという並びにした。「空にする」は `#trash` の
  アイコンを使い、`aria-label="空にする"` を付けた
- `data-confirm` による確認ダイアログをそのまま残した。これまでと同じく、
  `sde_id` で絞り込んでいるときと 0 件のときは「空にする」を出さない
- 本文末尾の「空にする」ボタンを削除し、不要になった
  `.my-trash-clear-row` を CSS から削除した。`.my-trash-clear` は、復活・
  個別削除と同じアイコンボタンの基本スタイルを使うようにまとめた
- `TrashHandler._clear()` のリダイレクト先を `/ytsched/trash` から
  `/ytsched/` へ変え、空にしたら週間表示へ戻るようにした
- `tests/test_web.py` に、通常表示では全消去フォームがヘッダー内だけに
  あること、件数がタイトル横にあること、絞り込み中と 0 件ではボタンが
  無いことを追加した。全消去後のリダイレクト先の期待値も週間表示へ
  書き換えた

## テスト

- main: `uv run pytest tests/test_web.py -k 'TrashHandler' -q` — 15 件通過
- main: Ruff の format check と lint — 通過
- main: 一時データで起動し、390px と 800px のスクリーンショットで、
  ヘッダーが 1 行に収まり、中央の件数と右端のアイコンが正しく表示される
  ことを確認
- verifier: `mise run test` — formatter、Ruff、basedpyright、mypy、
  ESLint、pytest 581 件がすべて通過
- verifier: 一時データで通常・絞り込み・0 件の HTML、全消去の 302 と
  `Location: /ytsched/`、`trash.jsonl` が空になることを確認
- verifier: Playwright で確認ダイアログをキャンセルすると消去されず、
  承認すると週間表示へ移ってゴミ箱が空になることを確認
- reviewer: 指摘なし
