# TODO-128. README を特徴と最低限の使い方に絞り、詳細を文書へ分ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort medium | main + verifier |
| 消費 | output 16,758 / cache_creation 140,878 / 概算 $2.3 |
|      | main 82% + verifier 18%（料金の割合） |

verifier の報告は
[archives/agents/TODO-128/verifier-report.md](../agents/TODO-128/verifier-report.md)
にある。

## きっかけ

`README.md` が 263 行あり、導入手順・systemd のユニット・`conf.json` の
設定表・同梱ライブラリ・アイコンの作り直しまで抱えていて、特徴が
読み取りにくかった。内容も、ゴミ箱・月間ミニカレンダー・
`ytsched holiday`・`TrashMax` といった後から入った機能に追いついて
いなかった。

## やったこと

- `README.md`（263 行 → 134 行）— 特徴のアピールと最低限の使い方に絞った。
  ゴミ箱・月間ミニカレンダー・`ytsched holiday`・ホーム画面への追加を
  特徴に足し、末尾に 4 つの文書への案内表を置いた。「課題・問題点」からは
  検索の行を落とし、繰り返し・期間の予定だけ残した
- `docs/Install.md`（新設）— インストール・更新・systemd --user・
  リバースプロキシ・`ytsched holiday`・`ytsched migrate`
- `docs/User.md` — 冒頭に「書き方の基本ルール・週の表示・月間ミニ
  カレンダー・メニュー・フィルター・ゴミ箱・ホーム画面への追加・設定」を
  足し、元からあった検索の説明を `## 検索` の下へ移した（見出しは `###`）。
  設定の表には `TrashMax` を足した。TODO 番号の言及（TODO-071）は消した
- `docs/Developer.md` — 「外部のライブラリ」の節（同梱の CSS・アイコン・
  `tools/make-icons.sh`）を足し、冒頭のリンクに `Install.md` を加えた

### verifier が見つけたこと

`docs/User.md` に「週表示のフッター左端のゴミ箱アイコンから開く」と
書いていたが、フッター左端は三本線のメニューで、ゴミ箱はそれを開いた
先のパネルの中にあった。ToDo の日数とフィルターの入力欄も同じパネル内
なので、「メニュー」の節を作って 3 つともそこから開くことを書き直した。

## テスト

- `mise run test` — 547 件すべて通過（文書だけの変更。README を参照する
  テストは無い）
- verifier が、設定値の既定と範囲・ミニカレンダーのスイッチの位置・
  連番の複製・CLI のオプションと既定値を実装と突き合わせ、
  6 つの `.md` の相対リンクの実在も確認。リンク切れなし
- `git show HEAD:README.md` と突き合わせ、移した内容に抜け落ちが
  無いことを確認
