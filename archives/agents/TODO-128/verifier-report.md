# TODO-128 verifier 報告

## `mise run test`

`cd ~/work/ytsched && mise run test`

○ fmtjs / lintjs / typecheck（mypy: 35 files, basedpyright: 0/0/0）すべて通過。
○ pytest 547 件すべて通過（132.41s）。README を参照するテストは無し。

## 記述と実装の食い違い

- ○ `LoadMonths` 既定 1・範囲 0〜24（`main_binder.py` `DEF_LOAD_MONTHS` /
  `LOAD_MONTHS_MIN` / `MAX`）
- ○ `AutoTurnMsec` 既定 700・範囲 300〜10000（同ファイル）
- ○ `TrashMax` 既定 100（`trash_handler.py` `DEF_TRASH_MAX`）
- ○ 月間ミニカレンダーのスイッチは CSS 上も実際に「左上」
  （`my.css` `.my-mini-cal-sw { position: absolute; left: 0; top: 0; }`、
  コメントにも「スイッチだけ左上に重ねる」とある）
- ○ 連番の複製（半角 `#`+数字、ToDo は日付を動かさない）は
  `sched_update.py` の `TITLE_COUNTER_RE` とコメントの通り
- ○ `ytsched holiday` / `migrate` のオプション（`--datadir` `--dry-run`
  `--url`、`--error-file`）、`ytsched webapp` の既定値
  （port 10085, urlprefix `/ytsched`, datadir `~/ytsched/data`）は
  `__main__.py` / `webapp.py` と一致
- △ **ゴミ箱の入口の説明がやや不正確。** `docs/User.md` は「週表示の
  フッター左端のゴミ箱アイコンから開く」と書くが、実装では
  フッター左端のアイコンはハンバーガーメニュー（`#bars`、
  `main.html` 300行目付近の `menu_sw`）で、それを開いた先のパネル内に
  ゴミ箱アイコン（`#trash`、388行目付近）がある。「フッターのメニューを
  開くとゴミ箱アイコンがある」のような書き方の方が実態に近い

## リンク切れ

○ README.md / docs/Install.md / docs/User.md / docs/Developer.md /
  src/README.md / tests/README.md の相対リンクをすべて洗い出し、
  実ファイルの有無を確認。リンク切れなし
  （`docs/fig1.png`, `docs/data-format.md`, `docs/Install.md`,
  `docs/User.md`, `docs/Developer.md`, `src/README.md`,
  `tests/README.md`, `docs/licenses/bootstrap-LICENSE`,
  `docs/javascript-scroll.svg` すべて存在）

## README から移した内容の抜け落ち

`git show HEAD:README.md` と突き合わせ済み。移動前の内容はすべて
移し先（Install.md / User.md / Developer.md）に残っている。
「課題・問題点」から検索の行が落ちているのは TODO の指示通り。

## 判断が要る点

- 上記「ゴミ箱の入口」の記述（`docs/User.md` の「フッター左端の
  ゴミ箱アイコン」という言い回し）を直すかどうか
