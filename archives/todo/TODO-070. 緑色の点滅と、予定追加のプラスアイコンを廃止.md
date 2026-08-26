# TODO-070. 緑色の点滅と、予定追加のプラスアイコンを廃止

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier + wording |
| 実施 | Opus 5 / effort high | main + verifier + wording |
| 消費 | output 20,033 / cache_creation 164,282 / 概算 $3.1 |
|      | main 89% + verifier 6% + wording 5%（料金の割合） |

## きっかけ

要らなくなった表示が 2 つ残っていた。どちらも消すだけで、触る場所も
重ならないので 1 項目にまとめた。元の TODO-071（新規追加のプラスアイコン
廃止）をこちらへ吸収したので、**TODO-071 は欠番**。

- **緑色の点滅**は、予定を追加・更新したあと、その行と日付欄を 5 秒ほど
  緑色で光らせるもの（`.5s` × 10 回）。今となっては無意味、と利用者の判断
- **プラスアイコン**は、各日のスケジュールの下にあった「予定を追加」の
  ボタン。TODO-055 で日付の欄を押しても追加できるようにした。日付の欄の
  ほうが大きくて押しやすく、小さいアイコンは要らなくなっていた

## やったこと

**点滅**

- `my.css` — `@keyframes blink` と `.blink` を削除
- `main.html` — `class_blink`（日付欄に付いていた）を削除
- `sde.html` — `class_blink`（更新した行に付いていた）を削除
- `main_handler.py` — 点滅させる行を伝えるためだけに動いていた
  `modified_sde_id` の受け渡しを削除した
  - `post()` のリダイレクト URL に `modified_sde_id=` を載せるのをやめた
  - `get()` でクエリから受け取るのと、`render()` へ渡すのをやめた
  - 受け取り手がいなくなった `exec_cmd()` の 2 番目の戻り値も落とし、
    `tuple[date | None, str | None]` にした
  - ただし `exec_cmd()` の**中**の `modified_sde_id` は残した。
    `cmd=update` のあと編集画面へ戻る URL を組むのに使っていて、
    点滅とは別の用途

**プラスアイコン**

- `main.html` — 各日の下の `<!-- スケジュール追加ボタン -->` の `div` を削除
- `my.css` — `.my-add-btn` を削除
- `icons.svg` — `#plus-square` を削除（他に参照は無かった）

**テスト**

- `test_modified_sde_id_from_query`（クエリから受け取ることを見ていた）を削除
- `test_add_redirects_to_list` から `modified_sde_id=` の assert を外した

## テスト

verifier が確認した（`archives/agents/TODO-070/verifier-report.md`）。

- `mise run fmt` / `typecheck` / `lint` / `test` はすべて通過（453 passed）
- `blink` / `plus-square` / `my-add-btn` の消し残しは無し
  （`my.css` の `BlinkMacSystemFont` はフォント名で無関係）
- 一時ディレクトリを `--datadir` に指定してサーバを起動し、curl で確認。
  予定を追加すると `Location: /ytsched/?date=...` へ 302 で戻り、
  クエリに `modified_sde_id` は付かない。日付欄の `onmousedown` は
  残っていて、編集画面へ行く道は生きている
