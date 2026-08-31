# TODO-130. ミニカレンダーのドットと四角を 1px 大きくする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier |
| 消費 | output 4,544 / cache_creation 31,838 / 概算 $0.4 |
|      | main 61% + verifier 39%（料金の割合） |

分担と担当の報告は
[archives/agents/TODO-130](../agents/TODO-130/README.md) にある。

## きっかけ

月間ミニカレンダーの印（TODO-129）は、予定が丸、ToDo が四角で、どちらも
4px 角だった。4px だと丸みがほとんど出ず、2 つの印を見分けにくい。

## やったこと

`src/ytsched/webroot/static/css/my.css` の `.my-mini-cal-dot` と
`.my-mini-cal-sq` の `width` / `height` を 4px から 5px にした。
奇数サイズにすると円の丸みが出やすい。

印が 2 つ並んでも横幅は `5px + gap 1px + 5px = 11px` で、セル幅 24px に
収まる。1 セルに出る印は予定と ToDo の最大 2 個で、増える仕組みは無い。

## テスト

`mise run lint`（ruff format / ruff check / eslint / basedpyright / mypy）
と `mise run test`（553 passed）が通ることを verifier が確認した。
ブラウザでの見え方は目視していない。
