# reviewer 報告 (TODO-104)

## 確認した範囲

- `git diff`（`src/ytsched/handler_util.py` / `main_handler.py` /
  `webroot/static/css/my.css` / `webroot/templates/main.html` /
  `tests/test_handler_util.py` / `tests/test_web.py`）
- `update_conf_arg()` / `convert_value()` の実装まで遡って、保存される
  値・変換失敗時の扱い・`empty_is_given=False` の分岐を追った
- `mk_weeks()` の呼び出し箇所（1 か所のみ）、`render()` への
  `month_cal` の受け渡し
- `swipe.js`（`mouseDownHdr`/`mouseUpHdr`）と `.my-week-panel` /
  `.my-mini-cal-row` の CSS。スイッチの `onmousedown="doPost(...)"` が
  既存の日付セル（`main.html` の `on_date_col`）と同じ委譲の仕組みに
  乗っているかを確認
- `icons.svg` に `check-square`/`square` が存在すること

## 指摘

**無し。**

`update_conf_arg()` の仕組みには正しく載っている。

- 不正な値（例: `"2"`）は `convert_value()` が `ValueError` を
  捕まえて `None` を返すので「渡されていない」扱いになり、
  `conf.json` へは保存されない（TODO-027 と同じ経路）
- 空文字は `empty_is_given=False` のため「渡されていない」扱いになり、
  `todo_days` と同じ分岐に乗る
- 保存される値は `save_value = converted if isinstance(converted, str)
  else value` の分岐により、`converted` が `bool` なので常に
  `value`（リクエストの生文字列 `"1"`/`"0"`）が使われ、`conf.json` には
  文字列で入る。テスト `test_month_cal_is_saved` もこれを確認している
- 引数なし・`conf.json` にも無いときは `DEF_MONTH_CAL = True`（既定で
  出す）に落ちる。`conf.json` の値が `"0"`（文字列としては truthy）の
  ときも正しく `False` に変換される

`mk_weeks()` は呼び出し箇所が 1 か所（`get()`）のみで、引数の足し漏れは
無い。検索モードは `get()` 側で `search_mode` が別に管理されており、
`month_cal` はそれに影響しない（テンプレート側で `{% if not
search_mode %}` の外枠は変更していない）。

テンプレートは `w.month_cals` の空・非空ではなく `month_cal` の値で
分岐しており、依頼どおり。スイッチ自体は `{% if month_cal %}` の外に
あるので、消してあるときも残る。`doPost()` に渡す `date` は
`w.monday`、`month_cal` は反転値の文字列で、依頼と一致する。

CSS の `position: absolute` は、`.my-mini-cal-row` が `.my-week-panel`
（`width: 100%`）の中にあり、スイッチはその行の左端 (`left: 4px`) に
収まるので、中央寄せされた月間ミニカレンダーとは重ならない。スワイプは
`swipe.js` の `mouseDownHdr`/`mouseUpHdr` が `[onmousedown]` を持つ
要素を汎用的に拾って委譲する仕組みなので、`position: absolute` にした
新しい要素でも既存の日付セルと同じに扱われ、ドラッグの邪魔にはならない。

テストは、依頼書に挙げられた 5 つの場合分け（既定で出る、
`month_cal=0` で消えてスイッチは残る、`conf.json` の `"0"` で引数なしでも
消える、保存される、検索モードで両方出ない）を過不足なくカバーしている。

## 確信度の低い所見（参考）

- `test_month_cal_0_in_conf_hides_without_argument` は、ミニカレンダーが
  消えることだけを確認していて、そのときスイッチが未チェック
  （`#square`）で出ていることまでは確認していない。他のテストで
  スイッチの表示・チェック状態は別途確認済みなので実害は薄いが、
  この場合分けだけ厚みが違う
- スイッチの当たり判定はアイコンそのまま（`.my-icon` = 1em = 16px）で、
  `.my-mini-cal-row` の `min-height: 24px` の中に左詰めで置かれている。
  実機（412px）で押せることは implementer が Playwright で確認済みとの
  ことだが、絶対配置かつ小さめのアイコンなので、指の太さによっては
  押しにくく感じる可能性はある（見た目・触感の話で、動作の正しさとは
  別の観点）
