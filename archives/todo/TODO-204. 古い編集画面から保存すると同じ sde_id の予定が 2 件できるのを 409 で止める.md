# TODO-204. 古い編集画面から保存すると同じ sde_id の予定が 2 件できるのを 409 で止める

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort high | main（実装）+ reviewer（Opus 5.5 / high、再レビュー 1 回）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | high | 140 | 31,766 | 120,548 | 7,153,122 | 79% |
| reviewer | Opus 5.5 | high | 54 | 1,478 | 67,891 | 1,240,324 | 14% |
| verifier | Sonnet 5.5 | medium | 40 | 2,381 | 65,279 | 540,894 | 7% |
| 合計 |  |  | 234 | 35,625 | 253,718 | 8,934,340 | 計 9,223,917 |

- 立てたのは TODO-205〜209 と同じコミットなので、`--since '2026-09-30 04:23:00'`（着手した最初のやり取り）で切った
- main の分には、この項目と関係の無いやり取り（ccspk の辞書に「空」を登録した件、Claude Code の更新内容の要約）も入っている
- main の effort は `~/.claude/settings.json` の `modelSettings` の値（`claude-opus-5-5` は `high`）
- reviewer・verifier のモデルと effort は、その時点の定義ファイルのまま

## きっかけ

`sched_update.py` の `exec_update()` は、`cmd_del()` が何も消さなくても
`cmd_add()` を続ける。1 回目の保存で版が `-1` → `-2` になったあと、
古い画面（`-1`）から保存すると、削除は空振りし、`next_id()` が同じ `-2` を
もう一度作る。2026-09-30 のレビューで再現した（同じファイルに
`…-2` が 2 行）。

409 で止めると決めた（利用者が決めた。2026-09-30）。保存ボタンの
2 回押しでは 1 回目は保存されているので、2 回目がエラー画面になるのは
受け入れる。`del` の空振りは書き込みが起きないので変えない。
409 のときは、tornado の既定の画面ではなく、日本語の説明と一覧への
リンクがある画面を出す。TODO-206 の 403 でも同じ作りの画面を使う。
404・500 は既定の画面のまま。

## やったこと

- `SchedUpdater.is_conflict()`（`sched_update.py`）を足した。`cmd` が
  `fix`/`update` で、送られた `sde_id` が `orig_date` のファイルに無ければ真。
  `sde_id` が空なら新規作成として見ない
- `MainHandler.exec_cmd()`（`main_handler.py`）が、`exec_update()` の前に
  これを見て `HTTPError(409)` にする。ゴミ箱にもデータにも何も書かない
- `HandlerBase.write_error()`・`ERROR_MESSAGES`・`HTML_ERROR`（`handler.py`）と
  `templates/error.html` を足した。`ERROR_MESSAGES` にあるステータス（今は 409）
  だけ、日本語の説明と一覧へのリンクを出す。TODO-206 の 403 はここに 1 行足す
- レビューで、編集画面の新規が仮の ID（`SchedDataEnt("", date)` が振る `…-1`）を
  `sde_id` として送るため、新規作成が 409 になることが分かった。利用者が
  「新規では ID 欄を空にする」を選び、`edit.html` の `sde_id` 欄を `new_flag` の
  ときだけ空にした。これで、編集画面から作った予定の最初の版は `…-2` ではなく
  `…-1` になり、`add` と揃った
- テスト（`tests/test_web.py` の `TestConflict`）: 2 つのタブで編集、同じフォームを
  2 回送る、ToDo（`orig_date` が無い）、編集画面の新規から保存、404 が既定の画面の
  まま、の 5 件
- 既存の `test_update_sde_not_found` は `SchedDataFile.get_sde` を丸ごと差し替えて
  いたため 409 に先に引っかかった。差し替え先を `SchedUpdater.get_modified_sde` に
  変えた（見ている 404 の分岐は同じ）
- `src/README.md` のクラス図・テンプレートの一覧・`HandlerBase`・`MainHandler` の説明

## 確かめたこと

verifier の報告は `archives/agents/TODO-204/verifier-report.md`。

- `mise run lint`・`typecheck` が通り、`mise run test` は 703 passed
- 壊すと落ちるか: `is_conflict()` を常に偽にする・`ERROR_MESSAGES` から 409 を消す →
  `TestConflict` の 409 の 3 件が落ちる。`edit.html` を戻す →
  `test_new_from_edit_page_is_not_409` が落ちる
- ブラウザ（chromium、400x800）: 新規作成は保存でき、2 つのタブで A → B の順に更新すると
  B が 409 で説明とリンクが出た。リンクで一覧が開く。データは 1 行のまま。
  コンソールのエラーは 409 の応答そのものの 1 件だけで、`pageerror` は 0 件

## 残ること

- `error.html` の描画そのものが失敗すると、本文の無い 409 になる（reviewer の確信度の
  低い指摘）。テンプレートは固定の文字列しか使わず、起きる場面が考えにくいので手を入れない

## 分担の振り返り

分担の理由と報告は `archives/agents/TODO-204/`。

- **reviewer** が、新規作成が 409 になる不具合を見つけた。main のテストは
  `sde_id=""` を直接 POST していて、編集画面が実際に送る値を通っていなかった。
  直したあとの再レビュー（同じ担当に続けて頼んだ）では指摘は無かった。
  確信度の低いもの 2 件（描画の失敗、エラー画面で一覧用の JS が動くか）も挙げ、
  後者は verifier のブラウザ確認で見た
- **verifier** は食い違いを見つけなかった。壊すと落ちるかの 3 つと、ブラウザでの
  再現・コンソールのエラーの確認を、測った値つきで返した
- 見込みとの食い違いは、再レビューが 1 回増えたことだけ。main の割合が大きいのは、
  範囲に関係の無いやり取りが入ったのと、利用者とのやり取り（409 の意味、新規の
  見分け方の相談）が会話を伸ばしたため
- 次に同じ規模の項目をやるなら: **フォームの値で分岐を足すときは、最初から
  「画面を GET して、出てきた値をそのまま POST する」テストを書く。** 直接 POST する
  テストだけでは、画面が実際に送る値との食い違いを拾えない。編成は同じでよく、
  直しの再レビューは担当を立て直さず続けて頼む（今回は 5 回のツール呼び出しで済んだ）
