# TODO-114 verifier 報告

コードリーディングによる照合のみ（アプリ起動・pytest は依頼になく未実施）。

## 照合結果（一致）

- 左上ボタン（`data-action="search-prev"`）: `main.html` の
  `data-date="{{ date }}"` `data-days="{{ str(date_from - date_to)[:-14] }}"`
  → `doGetDate()`（nav.js）で `date + days = date_from`（一番古い日）を新しい
  起点にして GET する。GET には `search_str` を含めないため、
  `MainBinder._update_conf_arg`（`empty_is_given=True`）が `conf_value`
  （保存済み `SearchStr`）を使い続ける。「起点だけ変わり検索文字列は残る」
  という記述と一致
- さかのぼる範囲: `handler_util.SEARCH_HARD_LIMIT_DAYS = 365*5`、
  `SchedLoad.SEARCH_ENOUGH_DAYS = 365`。`_search_prev()` の打ち切り条件
  （`search_count > 0` のときだけ 1 年の `date_from1` で止める）は
  「約 5 年前まで／1 件でも見つかっていれば 1 年より前には行かない」と一致
- 検索をやめる手段: 左端日付（`data-action="date-post"` → `search_str: ""`
  を POST、`empty_is_given=True` で conf をクリア）、入力欄を空にして
  虫めがね（`submit-form` → 同じく空文字を送信）の 2 つ。記述と一致
- ホームボタン: シングル・ダブルとも `search_str` を明示的に空にしないため
  （シングルは現在値をそのまま POST、ダブルは `search_str` を送らず conf
  の値が残る）、いずれも検索は解除されない。「シングル・ダブルとも解除
  されない」という記述と一致
- 消しゴム（`clear-search`）: `document.getElementById("search_str").value = ""`
  のみで、送信処理は呼んでいない。記述と一致
- 検索対象文字列: `SchedDataEnt.search_str()` は
  `f"#{type} +{title} @{place} detail:{detail}"` を `normalize()`
  （全角括弧→半角、`lower()`）した文字列。表の `\+打合せ`（件名が
  「打合せ」で始まる）は一致
- エラーメッセージ「検索の正規表現が正しくないので、検索していません」は
  `main.html` 70 行目の文言と完全一致。エラー時は `search_mode` が偽になり
  通常表示へ戻る点も一致
- `README.md` 23 行目・`docs/Developer.md` 5 行目の `User.md` へのリンクは
  実在するファイルを指している

## 気になった点（誤りとまでは言えない簡略化）

- `docs/User.md` の表で `@新宿` を「場所が「新宿」の予定」と説明している。
  実装は `search_str()` が生成した1本の文字列全体に対する正規表現一致
  なので、`@新宿` は「場所」欄に限らず、`detail` 欄などに文字列として
  たまたま `@新宿` という並びが現れた場合にも一致しうる（例は考えにくいが
  理論上はありうる）。「場所欄が新宿だけを厳密に指す」という誤読を招く
  可能性はあるが、通常の使い方では実用上ほぼ一致するため、修正するか
  どうかは判断が要る点として報告するのみに留める

## 未実施

- pytest 全体の実行（依頼で不要と指定）
- アプリ起動しての目視確認（依頼で必須ではないため、コード照合で十分と判断）
