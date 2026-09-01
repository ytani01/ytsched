# TODO-145. ゴミ箱が 0 件のときは、フッターのゴミ箱アイコンを無効にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |
| 実施 | Opus 5 / effort medium | main のみ + verifier |
| 消費 | output 7,048 / cache_creation 36,787 / 概算 $0.6 |
|      | main 74% + verifier 26%（料金の割合） |

## きっかけ

週間表示フッターのゴミ箱アイコン（TODO-143・TODO-144 で件数を出した）は、
ゴミ箱が空でもクリックでき、何も無いゴミ箱画面へ飛んでしまう。
0 件のときはグレーアウトさせ、クリックに反応しないようにする。

## やったこと

- `src/ytsched/webroot/templates/main.html`
  `trash_count` が 0 のときは `href` を出さず、`my-btn-disabled` を付ける。
  `<a>` は `href` が無ければクリックに反応しないので、無効化はこれで足りる
- `src/ytsched/webroot/static/css/my.css`
  `.my-btn-disabled` を追加（`color: #999` / `opacity: 0.4` /
  `pointer-events: none`）。`pointer-events` は、`href` が無くても
  ホバーやタップの反応を残さないために併せて指定した
- `tests/test_web.py`
  `test_trash_count_zero` を、`my-btn-disabled` が付いていて開始タグに
  `href` が無く、件数が `0` であることを見る形に書き換えた
  （`<use href=...>` がリンクの中にあるので、`href` の有無は
  開始タグの範囲だけで見る）

クラス名は Bootstrap の `disabled` と衝突しないよう `my-btn-disabled` にした。

## テスト

verifier（`archives/agents/TODO-145/verifier-report.md`）で確認した。

- `uv run pytest` … 589 件通過
- `mise run lint` / `mise run typecheck` … 通過
- 一時ディレクトリを `--datadir` に指定してアプリを起動し、`/` の HTML を
  実際に取得。ゴミ箱 0 件のとき `<a class="my-btn my-btn-disabled">` に
  `href` が無いことを確認
- `my-btn-disabled` の名前の衝突が無いことを grep で確認
