# TODO-047 verifier への依頼

TODO-047「Bootstrap をやめて、素の CSS にする」の実装が終わった。
実際に動くかを確かめてほしい。

先に読むもの:

- `~/work/ytsched/TODO.md` の TODO-047 の節
- `archives/agents/TODO-047/implementer-request.md`（依頼書）
- `archives/agents/TODO-047/implementer-report.md`（実装者の報告）

変わったのは `my.css`・`base.html`・`README.md` の 3 つと、
`static/vendor/bootstrap/` の削除。**テンプレートの `class="..."` は
変えていない**（実装者の報告より）。

## 確かめてほしいこと（これだけ。思いついた確認を足さない）

1. `mise run lint`（ruff format / ruff check / basedpyright / mypy）
2. `uv run pytest tests`。件数を報告に書く
3. **アプリが起動して画面が出ること。** `--datadir` に一時ディレクトリを
   指定する。架空のデータが
   `/tmp/claude-649/-home-ytani-work-ytsched/6d4b41c4-d525-49f9-b349-30a9b032fdc2/scratchpad/data`
   にある（2026-08-25 を今日として作ってある）。**そのまま使わず、
   自分の一時ディレクトリへ `\cp -r` して使うこと**（`conf.json` が
   書き換わるため）

   ```
   uv run ytsched webapp --datadir <一時ディレクトリ> --port 10089
   ```

   URL は `/ytsched/` 配下。`http://localhost:10089/ytsched/`
4. **HTML を実際に取得して見る。**
   - `bootstrap.min.css` の `<link>` が消えていること
   - Font Awesome の `<link>` は残っていること
   - `{{ }}` や `{%` が生で残っていないこと
   - `my.css` が 200 で取れること。`/ytsched/static/vendor/bootstrap/bootstrap.min.css`
     が 404 になること
5. **サーバのログに例外やトレースバックが出ていないこと**
6. **キャプチャを自分で撮って、変更前と見比べること。** 実装者も
   やっているが、**同じことを独立にやり直してほしい**（この項目は
   「見た目が変わっていない」ことが成果物なので、そこがいちばん大事）
   - **`DISPLAY` があると chromium がフレームを返さずタイムアウトする。**
     `env -u DISPLAY` を付けて走らせる（TODO-051 の範囲。今回は直さない）
   - **`search_str` は `conf.json` にサーバ側で残る。** 撮る前に
     `conf.json` を `{}` に戻さないと、前後で条件がそろわない
   - 変更前のものは `~/tmp/playwright-mcp/todo047-before-*` と
     `todo047-cmpbefore-*` にある。**消さないこと。**
     自分が撮るものは `todo047-verify-*` のように別の名前にする
   - 撮るのは幅 412px と 800px の 2 つ。次の 5 通り

     | 状態 | URL / 撮り方 |
     |------|-------------|
     | 一覧 | `/ytsched/` |
     | 一覧（詳細を開く） | `/ytsched/` に `--open` |
     | メニューを開く | `/ytsched/` に `--open --toggle '#menu-sw'` |
     | 編集画面 | `/ytsched/edit/?date=2026-08-25&sde_id=id-0006` |
     | 検索モード | `/ytsched/?search_str=%E4%BC%9A%E8%AD%B0` |

   - **変更前を撮り直すには、`git stash` で変更を退避して撮り、
     戻す**のが確実。退避したものを戻し忘れないこと
   - 画素をそのまま比べると、日付ブロックの `blink` の位相の違いで
     必ずずれる（実装者が確かめている）。**ずれた画素数だけで
     「違う」と判断しないこと。** 拡大して目で見るか、DOM の
     計算値を比べる

## 既知で、報告しなくてよいこと

- `tools/screenshot.py` が `DISPLAY` に対応していない（TODO-051）
- `tools/screenshot.py` が `conf.json` の `search_str` を考えない
- Font Awesome がまだ入っている（TODO-048）
- `my.js` の `"instant"` が残っている（TODO-041 の回避。今回は触らない）

## 報告

`archives/agents/TODO-047/verifier-report.md` に書く。返事は 5 行以内。
コードは直さないこと。
