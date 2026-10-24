# reviewer の報告（TODO-221 / TODO-224）

対象: 未コミットの `git diff`（`src/ytsched/notify.py`、`src/ytsched/__main__.py`、
`tests/test_notify.py`、`docs/Developer.md`、`docs/UsersGuide.md`）。
テスト・lint は走らせていない（verifier の分）。一部の境界値は `format_entry` /
`format_detail_lines` を直接呼んで確かめた（下の「実測」）。

## 要修正

無し。

## 検討

1. `docs/UsersGuide.md` 追記部「全部の日に予定が無ければ、期間と「予定なし」だけが
   届く」が実装と合わない。`build_notify_text` は日の節が全部空でも、`--memo` を
   先頭に出し、期限の近い ToDo があればその節も後ろに出す。「だけ」と書いてあると、
   ToDo の節が付いたときに利用者が不具合だと読む。`docs/Developer.md` 側の
   「1 通は必ず届く」には問題が無い。
2. `tests/test_notify.py` の `test_detail_lines_indented`: `format_detail_lines` の
   `rstrip("\n")` を消してもこのテストは落ちない。`"1 行目\n2 & 行目\n"` の
   末尾の改行は 1 つで、`splitlines()` がもともと捨てるため。末尾の改行が 2 つ以上
   （`"a\n\n"`）あると、`rstrip` を消すと `"    "` の行が 1 つ増える（実測）。
   `sde.html` の `rstrip('\n')` に合わせるつもりなら、末尾の改行を 2 つにした入力を
   1 件足すと守れる。
3. CLI の配線（`__main__.py` の `--skip-empty` / `--detail` を `build_notify_text` へ
   渡すところ）にテストが無い。`skip_empty=detail, detail=skip_empty` のように
   取り違えても、今のテストはどれも落ちない。もっとも notify の CLI テストは
   これまでも無く（`--url` などにも無い）、今回の差分で新しく生じた穴ではない。
   verifier が CLI を実際に叩いて確かめるなら足りる。

## 好みの範囲

1. `--url` のとき、詳細の行を `` ` `` で囲んでいない点。囲まないことで、詳細中の
   URL は Slack で自動でリンクになり、等幅で揃える理由も無いので、方針としては
   妥当だと考える。代わりに、詳細中の `*` `_` `~` は mrkdwn の書式として効く
   （`_foo_` が斜体になる、など）。気になるなら利用者に確かめる程度。

## 確信度の低いもの

- `--url` のとき、詳細の行に `` ` `` が 1 つだけあると、次の予定の行の開きの
  `` ` `` と組になって、その予定の行の表示が崩れるおそれがある。Slack の
  インラインコードが改行をまたぐかどうかは確かめていない（実害は未確認）。
  予定の行では `` ` `` を `'` に置き換えているが、詳細の行では置き換えていない。
- 詳細の途中にある空行は `"    "`（空白 4 つだけ）の行になる（実測）。Slack では
  見た目に影響しないと思われる（未確認）。

## 問題無い点

- `format_entry` は `sde.html` の `sde_type` / `sde_title` / place の組み立てと同じになる。ToDo は `type[1:]`、`□` だけなら種別無し、非 ToDo はそのまま、`type` が空・`None` なら種別無し、title 空は `__`、place 空は `@` 無し。
- `--skip-empty` の判定 `sd.get_sdf(day).sde` は、`build_schedule_section` が並べる集合と同じなので、「予定が無い」の意味がずれない（ToDo は `get_sdf(None)` 側にあり、日のファイルに混ざらない）。
- 全部空のときの期間見出しは `format_period_header(date, days)`、1 日なら日付だけ、`--url` なら先頭の日へのリンク。テストの期待値どおり。
- `--skip-empty` / `--detail` を付けなければ、`if not day_sections` の分岐は `--days` が `IntRange(min=1)` なので通らず、日の節の組み立ても `link_header` に括り出しただけで同じ。出力の変化は TODO-224 の形式変更だけ。
- `--url` のとき、予定の行は `format_schedule_line` の結果全体を `slack_escape` し `` ` `` を `'` にしているので、種別・場所にも効く。ToDo の行も行全体をエスケープしている。詳細の行も `slack_escape` を通る。
- 足したテストは、`or "__"` を消す、`place` の判定を消す、`□` を除かない、ToDo の行のエスケープを外す、`skip_empty` の判定を消す・`day` を `date` と取り違える、詳細の字下げを変える、のいずれでも落ちる強さがある。
- 範囲: TODO-221・TODO-224 の項目の外への変更は無い。`docs/UsersGuide.md` に TODO 番号は書かれていない。

## 実測

`uv run python -c` で `notify.py` の関数を直接呼んだ結果:

| 入力 | 結果 |
| --- | --- |
| `format_detail_lines`, detail=`"a\n\nb\n\n"` | `['    a', '    ', '    b']` |
| 同, `"a\r\nb\r\n"` | `['    a', '    b']` |
| 同, `"\n"` | `[]` |
| `format_entry`, type=`□`・title 空・place 空 | `'__'` |
| `format_entry`, type=`□□x`・title=`t` | `'[□x] t'`（`sde.html` と同じ） |

## 作り込みすぎ

作り込みすぎ: なし。`link_header` は 2 か所から呼ばれ、`format_period_header` の
1 日の分岐は仕様（1 日なら日付だけ）に要る。

net: -0 lines possible.
