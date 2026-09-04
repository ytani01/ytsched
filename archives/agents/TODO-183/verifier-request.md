# TODO-183 verifier への依頼

## 目的

TODO-183「ゴミ箱の戻るボタンで、直前に表示していた週へ戻る」の実装が、
実際に動くかを確かめる。**コードは直さない。**見つけたことは報告する。

## 前提

- 仕様は `archives/agents/TODO-183/implementer-request.md`
- 実装の報告は `archives/agents/TODO-183/implementer-report.md`
- 変更されたのは以下（`git diff` で見られる。コミット前）:
  `src/ytsched/trash_handler.py` /
  `src/ytsched/webroot/templates/main.html` /
  `src/ytsched/webroot/templates/trash.html` /
  `src/ytsched/webroot/static/js/main-page.js` /
  `tests/test_web.py` / `tests/test_browser.py` / `TODO.md`

## 確かめること

1. `mise run fmt` → `mise run lint` → `mise run typecheck` →
   `mise run test` が通る（`upgradeproject` は走らせない）。
   `fmt` が差分を出したら、その旨を報告する（自分で直さない）。
2. **実際にアプリを起動して、手で確かめる。**
   `--datadir` に一時ディレクトリを必ず指定すること（実データを汚さない）。
   ゴミ箱に項目が要るので、`trash.jsonl` を置いてから起動する。
   - 週間表示で今日以外の週（例: 3 週間先）を開き、フッターのハンバーガー
     メニューを開いてゴミ箱アイコンを押す。URL が
     `…/trash?date={その週の月曜}` になるか。
   - ゴミ箱の戻るボタンで、**その週**へ戻るか（今日の週ではないこと）。
   - ゴミ箱で 1 件だけ選んで完全に削除 → ゴミ箱に戻り、そこから戻る
     ボタンで同じ週へ戻れるか。
   - ゴミ箱を空になるまで削除 → 週間表示へ移り、そこが**同じ週**か。
   - 復活ボタンは今までどおり、**復活した予定の日付の週**へ移ること
     （直前の週へ戻ってはいけない）。
   - ゴミ箱が 0 件のとき、フッターのアイコンが今までどおり押せないこと。
3. **月間表示（`?view=month`）からゴミ箱へ入ったときに、`date` が
   空にならないか。** `ytState.activeMonday` が月間表示でも入っている
   前提の実装なので、ここは実際に確かめてほしい。空だと
   `?date=` になって今日の週に戻ってしまう。
4. **検索表示からゴミ箱へ入ったとき**も、`date` が空にならないか。
5. `URL_PREFIX` を付けた状態でも壊れていないか（テストは付けている）。

ブラウザ操作は playwright を使ってよい（`tests/test_browser.py` の
やり方に倣う）。手で確かめるのが難しい項目は、その理由を報告する。

## 報告

`archives/agents/TODO-183/verifier-report.md` に、確かめた手順と結果、
見つけた問題（あれば再現手順つき）を書く。返事は 5 行以内。
