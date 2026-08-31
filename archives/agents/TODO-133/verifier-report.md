# TODO-133 verifier 報告

対象: `src/ytsched/webroot/static/css/my.css` の `.my-mini-cal*` 群（CSS のみ）。

## 1. lint / test

- `mise run lint` ○ ruff format / ruff check / eslint / basedpyright / mypy
  すべて通過（`upgradeproject` は実行していない）。
- `mise run test` ○ `uv run pytest tests` 556 passed in 137.04s。

## 2. アプリの起動・HTML

- 一時ディレクトリ（`/tmp/.../scratchpad/ytsched-datadir/conf.json` に
  `{"MonthCal": "1"}`）を用意し、`uv run ytsched webapp --port 8765
  --datadir <一時ディレクトリ>` で起動。
- `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/` → `200`
- 取得した HTML に `{{` `{%` の生残りなし。サーバログに例外・トレース
  バックなし（`INFO webapp.py:127 main()> start server: run forever ..`
  のみ）。
- `class="my-mini-cal"` 18 個、`my-mini-cal-caption` 18、`my-mini-cal-row`
  9、`my-mini-cal-wdays` 18、`my-mini-cal-wday` 126 と、従来どおりのマーク
  アップが出ている（新規データディレクトリなのでスケジュール無く、
  `my-mini-cal-dot` / `my-mini-cal-sq` は今回は出現しなかった。データが
  無いことによるもので CSS の不具合ではない）。

## 3. 幅の見積り（実測）

Playwright（chromium, viewport 360×800/1200）で実測。

- `.my-mini-cal-row`（表示されている週の行）: `x:0 width:360`
  （`document.documentElement.clientWidth` も `document.body.scrollWidth`
  も 360 で一致、横スクロールなし）。
- 2 つの `.my-mini-cal` はそれぞれ幅 177px（`(360-6)/2=177`）で、
  `flex:1 1 0` により残り幅を均等に分け合っている。`max-width:200px` の
  上限には掛かっていない。
- 日セルは実測 `width:26.28px height:30px`（`table-layout:fixed` により
  177px を 7 列で均等割）。

**判断が要る点**: TODO-133 の本文にある「`container` の左右パディング
12px ずつ」という前提は、実際に `.my-mini-cal-row` を包む要素が
`main.html` の `<div class="container-fluid p-0">`（59 行目）であり、
`.p-0`（`my.css` 256 行目、`padding: 0`）が `.container-fluid` 自身の
padding-left/right（`--my-gutter-x` 由来の 12px、123-127 行目）を
CSS の後勝ちで上書きするため、**実際にはパディング 0 で全幅 360px が
使える**（実測とも一致）。今回は結果的に「はみ出さない」という結論に
変わりはなく、むしろ想定より余裕がある方向のズレなので実害は無いが、
TODO 本文の前提記述と実装場所の実態が食い違っている点は記録しておく。

## 4. 高さの見積り

- `box-sizing: border-box`（`*` に適用、49 行目）のため、`.my-mini-cal-dot`
  / `.my-mini-cal-sq` は `border` を含めても width/height は 8px のまま。
- セル内の縦積み: `.my-mini-cal-daynum`（line-height 16px）+
  `.my-mini-cal-marks` の `margin-top: 1px` + マーク本体 8px
  ≈ 25px。セル高 30px に対して約 5px の余裕があり、収まる。
- 実測でも `.my-mini-cal-day` の高さは 30px ちょうどで、はみ出しは
  見られなかった。

## 使ったコマンド

```
mise run lint
mise run test
uv run ytsched webapp --port 8765 --datadir <tmp>
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/
uv run python <playwright script; viewport 360x800/1200>
```

## 見つかった不具合

なし。
