# TODO-124. 週表示フッタの「ゴミ箱」の文字を消す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort medium | main + verifier |
| 消費 | output 2,364 / cache_creation 29,294 / 概算 $0.3 |
|      | main 63% + verifier 37%（料金の割合） |

分担と各担当の報告は
[archives/agents/TODO-124](../agents/TODO-124/README.md) にある。

## きっかけ

週表示のフッタで、ゴミ箱ボタンだけがアイコンの横に「ゴミ箱」という文字を
持っていた。隣の ToDo 日数・絞り込みはアイコンだけなので揃っていなかった。

## やったこと

- `src/ytsched/webroot/templates/main.html` のフッタから「ゴミ箱」の行を削った

リンク先も、アイコンも、他の画面も変えていない。

## テスト

- `mise run lint` — 通過
- `mise run test` — 536 passed
- verifier が一時データディレクトリでアプリを起動し、トップページのフッタの
  ゴミ箱リンクがアイコンだけになっていること、リンク自体は残っていることを確認
