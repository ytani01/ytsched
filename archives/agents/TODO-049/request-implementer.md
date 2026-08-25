# TODO-049 implementer への依頼

`TODO.md` の「## TODO-049. 1 画面 1 週間の表示にする」の節を**必ず先に
読むこと**。背景・表示の形・ゲージの考え方・気をつけることが書いてある。
以下はその補足で、着手時に利用者と決めたことを含む。

## チェック項目（TODO.md より）

- [ ] 1 画面に月曜から日曜までの 1 週間だけを出す
- [ ] 今の縦に並べる表示（スクロールでの追加読み込み）を外す
- [ ] ゲージを週単位にする
- [ ] 見た目を、変更の前後のキャプチャで確かめる

4 つ目のキャプチャは verifier と main が担当する。**implementer は
1〜3 を実装し、テストを直すところまで**。

## 着手時に利用者と決めたこと（この 2 つは TODO.md に書いていない）

1. **`--days` は消す。** 週表示になると通常の表示に効かなくなり、残る
   用途は `date_range()` の余白計算だけ。そこは
   `SEARCH_MODE_MAX_DAYS`（1825）のほうが常に大きく、実質使われない。
   「渡せるのに効かない」オプションを残さない
2. **ゲージの針は、前に見ていた週の位置から動かす。** `sessionStorage`
   に直前の週を持ち、読み込み時にまずその位置へ置いてから、次の
   フレームで今の週へ動かす。`transition` だけでは、ページを読み直す
   ので針が動いて見えない（初期値が `auto` で補間が起きない）

## 変えないこと

- **検索モードは今のまま。** 縦に並べる表示、`SEARCH_MODE_MAX_DAYS` /
  `SEARCH_MODE_DAYS` / `search_n` による打ち切り、`sde_align` の
  `bottom`、どれも変えない
- **Python 側の `GAGE`（`main_handler.py` の定数）と `days2y_offset()`**。
  対数目盛りの仕組みも、ラベル（-30y〜+30y）もそのまま
- **ToDo の扱い**（`load_todo()` の `todo_today_sde`）
- **テンプレートへ渡す `date`** は、今までどおり「指定された日」のまま。
  月曜へ丸めない。`class_blink`（`main.html`）と `cur_day` がこれを
  見ているので、丸めると毎回月曜が光ってしまう
- **左右のスワイプは TODO-054、ヘッダと日付欄の手直しは TODO-055。**
  この項目では触らない

## 変更の中身

### 1. 週の範囲にする（`main_handler.py`）

`load_sched()` の通常モードの範囲を「`date` を含む週の月曜〜日曜」にする。

```
monday = date - datetime.timedelta(date.weekday())
date_from = monday
date_to = monday + datetime.timedelta(6)
```

`while` で日をさかのぼる仕組みと、`sched[::-1]` で古い順に返すところは
そのまま使える。検索モードの分岐（`if search_mode:`）は変えない。

`date.weekday()` は月曜が 0、日曜が 6。

### 2. `--days` を消す

- `__main__.py` の `--days` オプションと、`webapp()` への引数
- `webapp.py` の `days` 引数、`self._days`、`settings["days"]`
- `handler.py` の `self._days` と、`date_range()` の
  `max(self._days, self.SEARCH_MODE_MAX_DAYS)` → `SEARCH_MODE_MAX_DAYS`
- `main_handler.py` の `DEF_DAYS`
- テスト側: `tests/helpers.py` の `make_app(days=...)`、
  `tests/test_handler.py`、`tests/test_webapp.py`、
  `tests/test_main_handler.py` の `DAYS`

`date_range()` の docstring に `--days` の話が書いてあるので、そこも
直す。

### 3. ゲージを週単位にする（`my.js`）

- **`dispGage(date_str)` の基準を変える。** 今は
  `getDaysFromToday(date_str)`（今日からの日数）だが、
  **「渡された日を含む週の月曜」と「今週の月曜」の差**にする。
  `date_str` を月曜へ丸める処理を関数の中に置けば、検索モードで
  `date_from`（飛び飛びの日）を渡しても同じ関数で済む
- **`sessionStorage` で前の週を憶える。** 読み込み時に、前の週が
  あればまずその位置へ針を置き（`transition` を効かせない）、次の
  フレームで今の週へ動かす。今の週は必ず保存する
- **消すもの**: `getTopDateString()`、`scrollHdr()`、`scrollHdr0()`、
  `scrollHdrTimer`、`scrollFlag`。`scrollFlag` は `scrollHdr()` の
  ためのガードなので、`scrollToId()` / `scrollToDate()` /
  `popstateHdr()` からも参照を落とす
- **`moveToMonday()` の先読み判定を消す。** 今は「3 週先・2 週前
  （`days2`）が DOM にあるか」を見てスクロールで済ませているが、
  週表示では前後の週は DOM に無い。常に `doGet()` する形にして、
  `days2` と `el_d2` の計算を落とす

### 4. `main.html`

- `onloadHdr` の `window.addEventListener('scroll', scrollHdr0, ...)` を
  やめる。検索の有無によらず `dispGage(date_from)` を呼ぶ
- 使われなくなる hidden の `date_to` を消す。**`sde.html` が使っている
  のはテンプレート変数の `date_to` のほう**なので、そちらは残す
  （`render()` の引数も残す）
- `body_h < win_h` の早期 return と `scrollToDate(...)` の呼び出しは
  残す。1 週間が画面に収まらないときは今までどおり上下にスクロールし、
  `date` の日に合わせる

### 5. `my.css`

`.my-gage-r` に `transition` を足す。`sessionStorage` で前の週へ置く
ときだけ効かせないようにする（クラスを付け外しするか、
`transition: none` を一時的に当てるかは任せる）。

## テスト

`tests/test_main_handler.py` の次の 2 件が、範囲を `DEF_DAYS` で見て
いるので週表示に書き直す。

- `TestSearchModeRange.test_normal_mode_range_is_days_before_and_after`
- `TestLoadSchedSkipsMissingFiles.test_normal_mode_sched_is_same_as_opening_every_day`

**足すこと**: 週の境界が正しいかを見るテスト。少なくとも次の 3 つ。

- 月曜を指定したとき、その日が `date_from` になる
- 日曜を指定したとき、その週の月曜まで戻る（`date_from` が 6 日前）
- 年をまたぐ週（例: 2025-12-29(月)〜2026-01-04(日)）でも 7 日ちょうど

検索モードのテスト（`TestSearchModeRange` の他の 5 件）は、通るまま
であること。通らなくなったら、それは検索モードを壊しているので直す。

## 気をつけること

- **`.longtext`（詳細の欄）を `row` の孫にしないこと。** 中身に押し
  広げられないための `min-width: 0` は `my.css` の `.row > *` に
  まとめてかけてあり、直接の子にしか当たらない。入れ子を深くすると
  `text-overflow: ellipsis` が黙って効かなくなる（TODO-045・TODO-047）
- **`mise run upgradeproject` は走らせないこと。** `mise run fmt` /
  `typecheck` / `lint` / `test` はよい
- **アプリの起動を確かめるときは、`--datadir` に一時ディレクトリを
  指定する**（`~/ytsched/data` の実データを汚さない）

## 報告

`archives/agents/TODO-049/implementer-report.md` に書くこと。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。

報告に入れてほしいこと:

- 触ったファイルと、それぞれ何をしたか
- `mise run fmt` / `typecheck` / `lint` / `test` の結果（そのまま貼る）
- 足したテストと、何を見ているか
- 迷ったところ、main の判断が要ると思ったところ
