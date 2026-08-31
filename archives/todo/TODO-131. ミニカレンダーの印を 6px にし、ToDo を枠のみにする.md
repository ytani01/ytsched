# TODO-131. ミニカレンダーの印を 6px にし、ToDo を枠のみにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier |
| 消費 | output 2,323 / cache_creation 39,852 / 概算 $0.6 |
|      | main 75% + verifier 25%（料金の割合） |

分担と担当の報告は
[archives/agents/TODO-131](../agents/TODO-131/README.md) にある。

## きっかけ

TODO-130 で印を 4px から 5px にしたが、丸と四角の差はまだ小さかった。
大きさだけでは見分けが付きにくい。

## やったこと

`src/ytsched/webroot/static/css/my.css` を直した。

| | 変更前 | 変更後 |
|---|---|---|
| `.my-mini-cal-dot`（予定） | 5px 角・塗り | 6px 角・塗り |
| `.my-mini-cal-sq`（ToDo） | 5px 角・塗り | 6px 角・`border: 1px solid #28F`（塗りなし） |

塗りと枠の差を付けたことで、大きさだけのときよりはっきり見分けられる。
ToDo が未完のチェック枠らしく見えるのも意味と合う。

`*` に `box-sizing: border-box` が効くので、枠線 1px は 6px の内側。
印が 2 つ並んでも `6px + gap 1px + 6px = 13px` で、セルの内側の幅
22px（24px − 枠線 2px）に収まる。

決める前に、4px・5px・6px＋枠の 3 つを実際に撮って見比べた。撮り方は
`docs/Developer.md` の「画面を撮る」にある `mise run shot`。

## テスト

`mise run lint`（ruff format / ruff check / eslint / basedpyright / mypy）と
`mise run test`（553 passed）が通ることを verifier が確認した。
`.my-mini-cal-sq` へ背景色が他のルールから回り込んでいないことも確認した。
