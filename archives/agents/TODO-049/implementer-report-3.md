# TODO-049 implementer 報告（3 回目 / ホームボタンが効かない不具合を直す）

依頼書どおり、`scrollToId()` で「目的の要素が DOM にあるか」を
「1 画面に収まっているか」より先に見る順番へ入れ替えた。

## 触ったファイル

- `src/ytsched/webroot/static/js/my.js`
  - `scrollToId()` の中身を並べ替え。`elMain.style.visibility =
    "visible"` は今までどおりどの道でも必ず実行したうえで、
    `document.getElementById(id)` と `el == null` の判定
    （検索モードで結果に無い日を指されたときは `true` を返す分岐を
    含む）を先に行い、そのあとで `body_h <= win_h` の「1 画面に
    収まっているので、スクロールは要らない」判定をするようにした。
    なぜこの順でなければならないかをコメントに書いた（不具合の
    症状・原因も含めて）
  - それ以外（`scrollToDate()`・`popstateHdr()`・`moveToMonday()` など）
    は触っていない

## `mise run fmt` / `typecheck` / `lint` / `test`

すべて green（JS のみの変更なので Python 側のテスト結果自体に
変化は無い。430 件通ることの確認のみ）。

```
[fmt] ruff format: 変更なし / ruff check: All checks passed!
[typecheck] basedpyright: 0 errors, 0 warnings, 0 notes / mypy: Success
[test] 430 passed
```

## 確かめたこと

- **症状が直ること。** main の確認スクリプト
  `home_check.py`（port 18077。静的ファイルはディスクから直接配信
  されるので、`my.js` を直しただけで再起動なしに反映された）を
  そのまま実行し、412px・800px の両方で
  `?date=2026-09-28` からホームボタンを 1 回押すと
  `date-2026-08-24 .. date-2026-08-30`（今日を含む週）へ実際に
  切り替わることを確認した（修正前は `date-2026-09-28 ..
  date-2026-10-04` のまま止まっていたはず、というのが main の再現
  内容どおり）
- **同じ週の中の日へ飛ぶときに、余計な読み直しが起きないこと。**
  別途 playwright で `scrollToDate()` を今週内の日付へ呼び、
  `load` イベントが 0 回（＝ページ遷移が起きていない）で `URL` だけ
  `pushState` により書き換わることを確認した
- **ホームボタンの 2 回押し。** `dblclick("#home_button")` で
  `doGet()` の道を通り、今日の週（`date-2026-08-24 ..
  date-2026-08-30`）が表示されることを確認した
- **検索したとき、結果の日付を押すとその週へ飛ぶこと。** 別の一時
  データディレクトリ（port 18103）に予定を 1 件置いて検索し、結果の
  日付欄（`.my-date-col`）をクリックすると、その日を含む週
  （`date-2026-08-17 .. date-2026-08-23`）へ切り替わることを確認した
- **戻る/進む。** `#forward_button` で次の週へ進んだあと
  `page.go_back()` すると、元の週（`?date=2026-08-26`）に正しく
  戻ることを確認した（`popstateHdr()` 経由）

確認に使ったスクリプトは
`/tmp/claude-649/-home-ytani-work-ytsched/.../scratchpad/`
（`extra_checks.py` / `same_week_check.py` /
`search_and_popstate_check.py` / `search_click_fix.py`）に置いた
（scratchpad なのでコミット対象ではない）。

## テストを足せるかどうか

**足さなかった。** 依頼書にもあるとおり `AsyncHTTPTestCase` は
JavaScript を実行しないので、この不具合（ブラウザ側の分岐の順番）は
Python 側のテストでは原理的に捕まえられない。playwright で捕まえる
自体は可能（実際、上の確認はすべて playwright で行った）だが、

- `tests/` 配下にはブラウザを起動するテストが 1 件も無く、
  `mise run test` の対象は `pytest` のみで JS 実行環境を持たない
- playwright を `pytest` の依存として組み込み、CI/`mise run test` から
  ヘッドレスブラウザを起動する仕組みを新設することになり、
  「この不具合 1 件を直す」という範囲を大きく超える
  （依存を増やす・テストの走らせ方を変える判断が要る）

と判断し、テストは足していない。この判断でよいかは main に確認して
ほしい。

## 判断が要る点

- 上記「テストを足せるかどうか」の判断（playwright ベースの回帰
  テストを新設するかどうか）は、この項目の範囲を超えると考え、
  main の判断に委ねる
