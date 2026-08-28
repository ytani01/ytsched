# verifier 報告 (TODO-104)

## 1. lint / typecheck / pytest

- `mise run lint` ○（ruff format 31 files unchanged、ruff check・eslint 全部通過）
- `mise run typecheck` ○（basedpyright 0 errors、mypy 0 issues, 28 source files）
- `uv run pytest -q` — 502 件成功、1 件失敗
  （`tests/test_browser.py::test_tap_again_stops_auto_page_turn`）
  - `git stash` して変更前のコードで同じテストを単体実行しても同じ差分
    （`'2026-09-21' == '2026-09-14'` の assert 失敗）で落ちることを確認。
    今回の変更とは無関係。

## 2. 起動して画面で確認

一時ディレクトリ (`/tmp/.../scratchpad/todo104-data`) を `--datadir` に
指定して起動、Playwright (viewport 412x800) で確認。

- ○ 既定でミニカレンダー（テーブル 2 個＝当月+翌月）とスイッチが出る
- ○ スイッチを押すとミニカレンダーが消え（table count 0）、スイッチは残る
  （switch count 1）。もう一度押すと戻る（table count 2）
- ○ 消した状態でリロードしても消えたまま。`conf.json` に
  `"MonthCal": "0"` が書かれていることを確認
- ○ 週を送った先（forward で 1 週送った週）のパネルでもスイッチが効き、
  押しても週は動かない（`data-monday` が押す前後で同じ）
- ○ 検索モード（`?search_str=test`）ではスイッチ・ミニカレンダーとも
  0 件（初回 `?search=test` という誤ったパラメータ名で試して 9/18 と
  出てしまい焦ったが、`search_str` が正しいパラメータ名だった。実装の
  不具合ではない）
- ○ 幅 412px で `document.documentElement.scrollWidth` は 412（横スクロールなし）
- ○ `conf.json` に手で `{"MonthCal": "xyz"}` を書いた状態で開くと、
  既定どおり表示（table count 2、switch count 1）、HTTP 200

## 3. スイッチの位置・大きさ（判断が要る点）

`bounding_box()` で計測: スイッチは row 内 `x=4, y=0`、大きさ
**幅16px×高さ24px**。スクリーンショット参照:

- ON: `/home/ytani/tmp/playwright-mcp/todo104-minical-switch-on.png`
- OFF: `/home/ytani/tmp/playwright-mcp/todo104-minical-switch-off.png`

ON のスクリーンショットを見ると、**カレンダーの曜日は月始まり
（月火水木金土日）で、日曜は一番右の列**。スイッチは左端（月曜列の
真上）に置かれており、**依頼書の「日曜日の日付欄の下あたり」とは
異なる位置**になっている。「左上」は満たしているが「日曜日の下」は
満たしていない。implementer の報告にも「具体的な px 指定が無かった
ため目視で決めた」とあるが、決めた位置は日曜ではなく月曜の下。

大きさは 16×24px で、他のボタン類（フッタのアイコンなど）と比べて
かなり小さい。タップできなくはないが「押しやすい大きさ」かどうかは
main の判断が要る。

## 判断が要る点まとめ

1. スイッチの位置が「日曜日の下」ではなく「月曜（左端）の下」になっている。
   これでよいか、位置を直すか
2. スイッチの大きさ（16×24px）が押しやすいと言えるか

## 再確認（スイッチの大きさ）

main による CSS 修正後の再確認。

- `uv run pytest tests/test_web.py -q` ○ 125 件成功
- `--datadir` に一時ディレクトリを指定して起動、Playwright (412x800) で確認
  - ○ ON/OFF どちらもレイアウト崩れなし。ミニカレンダーは中央のまま
    （table の x=32/211, 幅169 で左右対称）、`scrollWidth` は
    ON/OFF とも 412（横スクロールなし）
  - ○ スイッチの当たり判定（`bounding_box()`）は
    **幅16×高さ24px → 幅40×高さ29px** に拡大したことを確認
  - ○ 押すとミニカレンダー消滅（table count 0→2）、スイッチは残り、
    もう一度押すと戻ることを再確認
  - スイッチの位置は今回の修正対象外のため変わらず、`x=0`
    （行の左端＝月曜列の下）のまま。前回指摘した「日曜日の下」との
    食い違いは未解消（今回の依頼の範囲外）

スクリーンショット:
- ON: `/home/ytani/tmp/playwright-mcp/todo104-minical-switch-v2-on.png`
- OFF: `/home/ytani/tmp/playwright-mcp/todo104-minical-switch-v2-off.png`
