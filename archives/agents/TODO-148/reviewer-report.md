# TODO-148 reviewer 報告

## 結論

確信度の高い問題は見つからなかった。指摘は「気になる」程度のもの 1 件のみ
（節を分けて後ろに書く）。TODO.md の各チェック項目は diff の内容と合って
いる。

## 見た点ごとの確認結果

### 1. `sde.html` の変数追加の影響

- `main.html` は `{% include sde.html %}` を 1 か所（238〜245 行）でしか
  呼んでいない。この 1 ループ（`for sched_ent in w.sched`）が
  `search_mode` の分岐を内側に含む形になっており、週間・月間・検索の
  すべての描画がここを通る。`sde_editable = True` / `sde_uniq = ''` は
  そのループの中・`.my-day-entries` の直後、`for sde in sched_ent.sde`
  の直前にあり、抜け漏れの経路は無い
- `trash.html` は `for entry_index, entry in enumerate(group)` の中で
  毎回 `sde_editable = False` / `sde_uniq` を設定してから `<article>` を
  書いているので、全エントリで確実に設定される
- `{% set %}` の位置は、どちらも「使う直前・ループの中」で、
  `sde.html` 冒頭のコメントが要求する条件（呼び出し側で設定してから
  include する）を満たしている

### 2. id の一意性

- `sw_id = 'sw%s-%s%s' % (sde.sde_id, today_flag, sde_uniq)`
- `main.html` は `sde_uniq = ''` なので、`sw_id` の値は変更前と完全に
  同じ文字列になる（既存の折りたたみの id は変わらない）
- `trash_handler.py` の `groups` は `sde_id` ごとの辞書
  （`by_id.setdefault(entry.sde.sde_id, []).append(entry)`）から作るため、
  各グループは単一の `sde_id` にしかならない。`sde_uniq` は
  `'-%s-%s' % (group_index, entry_index)`（どちらも `enumerate()`）で、
  ページ全体の `(group_index, entry_index)` の組は重複しない。同じ
  `sde_id` の重複グループ（`tests/test_web.py` の
  `test_get_groups_same_id_and_shows_timestamp` が使うデータ）でも
  `entry_index` が 0 / 1 で分かれるため衝突しない

### 3. CSS

- `.my-date-block` は 12 列グリッドで、`.my-date-col`(span 1) +
  `.my-day-entries`(共通 span 11、`.my-trash-entry` の中だけ span 9 に
  上書き) + `.my-trash-actions`(span 2) = 12 と合っている
- `.my-trash-entry .my-day-entries` は子孫セレクタで詳細度
  (0,2,0) が共通ルール (0,1,0) より高く、ソース順に関係なく確実に勝つ。
  同様の「文脈限定の上書き」は `.my-week-wrap-dragging .my-week-near`
  `.my-month-grid .my-mini-cal` に前例があり、書き方として逸脱していない
- 削除した 5 クラス（`.my-trash-entry-row` `.my-trash-date-col`
  `.my-trash-time-col` `.my-trash-entry-summary` `.my-trash-detail`）は
  テンプレート・JS・CSS・テストのどこにも残っていないことを
  grep で確認した
- 残っているクラス名（`my-trash-entry` `my-trash-actions` など）は
  役割の名前になっており、TODO-146 の書き方（1 要素 1 クラス、
  Bootstrap 由来の名前を使わない）から外れていない

### 4. テスト

- `tests/test_web.py::test_entry_has_date_column_like_search_result` は
  `<main>` 内に絞って `data-action="edit-sde" data-date=` が無いことを
  確認しており、単純な文字列一致で緩くなっていない
- `tests/test_browser.py::test_trash_entry_shows_date_column_like_search_result`
  は実際にクリックして URL が変わらないことまで見ている（DOM 属性の
  有無だけでなく、挙動を確認している）
- 消えた `.my-sde-place` / `.my-trash-detail` の直接描画は、`sde.html`
  側の同等の表示（`@place`、詳細の折りたたみ）に置き換わっており、
  テストを弱めて通した形跡は無い
- `write_trash()` / `_write_trash()` のデータ（曜日・日付）と、
  テストのアサーション（`my-wday-0` = 月曜、`(Thu)` など）は実際の
  曜日と一致することを確認した

### 5. その他

- `trash_handler.py` の `today=datetime.date.today()` は、
  `main_view.py` の `"today": datetime.date.today()` と同じ形で、
  プロジェクト内で揃っている
- `trash.html` の `enumerate()` 利用は、Tornado テンプレートに
  `loop.index` が無いための代替として妥当（`sde.html` 側のコメントにも
  理由が書いてある）
- `<article class="my-trash-entry">` から `my-sde my-sde-normal` を
  外した判断（実装報告の「判断が要った点 1」）は、二重の枠を避けるための
  妥当な対応で、CSS 側にも `.my-trash-entry` 自身のスタイル
  （`margin-top` だけ）に矛盾は無い

## 確信度の低い指摘（気になる程度）

- `.my-trash-actions` の `grid-column` を `span 3` から `span 2` に
  狭めている。復活ボタン（`my-icon-xl` の SVG）とチェックボックスが
  1 列分（12 分の 2）に収まるかは、見た目を実際に確認しないと分からない。
  レイアウト崩れの可能性としては小さいが、確認していないので念のため
  書いておく
