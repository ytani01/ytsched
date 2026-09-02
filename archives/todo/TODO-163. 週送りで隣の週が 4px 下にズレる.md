# TODO-163. 週送りで隣の週が 4px 下にズレる

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Sonnet 5 / effort medium | main + verifier |
| 消費 | output 10,125 / cache_creation 74,273 / 概算 $0.8 |
|      | main 77% + verifier 23%（料金の割合） |

## きっかけ

矢印やスワイプで週を送ると、滑らせている間に見えている隣の週が 4px
下にズレていて、送り終わった瞬間に上がる。

`.my-month-header` の `margin-top: 4px` が、週パネルの状態でマージンの
抜け方が変わるのが原因。絶対配置の隣の週（`.my-week-near`）はブロック
整形コンテキストを作るのでマージンが中に残り、中身が 4px 下がる。通常
フローの今の週（`.my-week-cur`）は整形コンテキストを作らず（`#week_wrap`
の `position: relative` も `.my-week-viewport` の `overflow-x: clip` も
作らない）、マージンが外へ抜けて中身がパネルの上端に付く。

chromium で実測した値（幅 412px）:

| 週パネル | position | 先頭の月見出しの top |
|---|---|---|
| `.my-week-cur` | `static` | 45px |
| `.my-week-near` | `absolute` | 49px |

## やったこと

- `my.css` の `.my-week-near` / `.my-week-cur` を `display: block` から
  `display: flow-root` に変えた。どちらも整形コンテキストを持つように
  なり、ズレは 0 になる。月見出しの位置は 45px のまま変わらない
  （パネル自身の上端が 4px 上がって相殺される）ので、静止していると
  きの見た目は変えずに済んだ
- `tests/test_browser.py` に `test_week_panel_content_top_matches_cur_and_near`
  を追加した。`.my-week-cur .my-month-header` と
  `.my-week-near .my-month-header` の `bounding_box()` の `y` 座標が
  一致することを見る。修正前のコードに対して実行し、`45 == 49` で
  落ちることを確かめてから、修正を戻した

## テスト

- `uv run pytest -q`: 608 件通過（新規テストと、既存の週表示関連テスト
  `test_week_panel_in_flow_follows_the_week` を含む）
- `uv run ruff check .` / `uv run basedpyright`: 問題なし
- `uv run ruff format --check .`: 今回の変更ファイル 2 つは対象外
  （`archives/` 配下の既存 `.md` 9 件の未整形は TODO-163 と無関係）
- `--datadir` に一時ディレクトリを指定してアプリを実際に起動し、
  配信された CSS を取得して `.my-week-near` / `.my-week-cur` の両方に
  `display: flow-root` が反映されていることを確認（verifier）
