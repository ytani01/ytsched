# TODO-078 implementer への依頼

`TODO.md` の TODO-078 と `docs/design-review.md` の A・E を先に読むこと。

## 決まっていること（main が決めた。蒸し返さない）

**JavaScript に寄せて、Python 側のゲージの計算を消す。**
目盛りの位置も針の上の文字も、サーバが埋めるのは読み込み直後の一度だけで、
あとは `my.js` が書き換えている。JavaScript 側には同じ式が既にあるので、
初回の描画も JavaScript にやらせれば、Python 側は要らなくなる。
両方残して一致を見るテストを置く案は採らない（比べるのに結局ブラウザが
要るうえ、二重に持つこと自体は解消しない）。

## やること

### 1. `my.js` に目盛りを描く処理を足す

`src/ytsched/webroot/static/js/my.js` の横ゲージの節（`days2xPercent()`
の近く）に、目盛りの一覧（`-30y` から `+30y` までの 14 個）と、それを
`.my-gauge-bar` の中へ `<div class="my-gauge-label" style="left:…%">` として
描く関数を足す。

- 一覧の日数は、いま `main_handler.py` の `GAUGE` が使っているものと
  **同じ値**にする（`-DAYS_YEAR*30`, `-DAYS_YEAR*10`, `-DAYS_YEAR*3`,
  `-DAYS_YEAR`, `-DAYS_MONTH*3`, `-DAYS_MONTH`, `-7`, `+7`, `+DAYS_MONTH`,
  `+DAYS_MONTH*3`, `+DAYS_YEAR`, `+DAYS_YEAR*3`, `+DAYS_YEAR*10`,
  `+DAYS_YEAR*30`）
- `left` の値は今と同じ `50 + xPercent` で、小数点以下 2 桁に揃える
  （テンプレートの `'%.2f' %` と同じ見え方にする）
- **検索モードでは `.my-gauge-bar` が無い**ので、無ければ何もしない
- 呼ぶのは読み込み時。既存の `dispGauge()` / `onloadHdr()` の並びを見て、
  針の位置合わせ（TODO-060 で「毎回中央から動き出す」のを直した箇所）を
  壊さない順に入れること。**針の位置合わせのコードには触らない**

### 2. 針の上の文字を JavaScript が埋めるようにする

`main.html` の `{{ gauge_label }}` を空にして、読み込み時に
`setGaugePosition()`（またはそれを呼ぶ既存の入口）が
`gaugeDiffLabel()` の結果を入れるようにする。**すでに毎回書き換えて
いるので、初回にも必ず通るかどうかだけを確かめること。**
通らない経路があれば、そこで呼ぶようにする。

### 3. Python 側を消す

`src/ytsched/main_handler.py` から次を消す。

- `days2x_percent()` / `calc_gauge_label()`
- `DAYS_YEAR` / `DAYS_MONTH` / `DAYS_GAUGE_MAX` / `DAYS_GAUGE_K` / `GAUGE`
- `render()` に渡している `gauge=GAUGE` と `gauge_label=…`
- 使われなくなる `import math`（他で使っていないか確かめること）

`main.html` の `{% for d in gauge %}` の繰り返しも消す。
コメントは「JavaScript 側が描く」ことが分かるように書き直す。

## 気をつけること

- **見え方を変えない。** 目盛りの位置・文字・CSS クラス名は今のまま
- `.my-gauge-label` の CSS（`my.css`）は変えない
- ゲージが出るのは検索モードでないときだけ、という条件は変えない

## テスト

- `tests/test_main_handler.py` の `calc_gauge_label` のテスト
  （`test_calc_gauge_label_rounds_to_monday` /
  `test_calc_gauge_label_switches_unit`）は、対象が消えるので**消す**。
  import も直す
- `tests/test_web.py` の `gauge_label()` を使うテスト（3 か所ほど）は、
  HTML に文字が入らなくなるので通らなくなる。**ブラウザ側で同じことを
  見ているテストが `tests/test_browser.py` にすでにある**
  （`test_gauge_label_moves_with_the_needle` /
  `test_gauge_label_is_plus_minus_zero_in_this_week`）。
  重複しているものは消し、ブラウザ側に無い観点（週をずらしたときの
  `+3w` / `-1.2m` のような単位の切り替わり）は
  `tests/test_browser.py` へ移すこと。**観点を減らさない**
- 目盛りが 14 個描かれ、`-1w` と `+1w` の位置が今までと同じであることを
  ブラウザのテストで見る。位置の期待値は、この変更を入れる**前**の
  HTML から実測して書くこと（`git stash` や `git show HEAD:` で
  変更前のテンプレート出力を得られる）

`mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
**`mise run upgradeproject` は走らせないこと。**
アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する。

### テスト（追記）

`tests/test_handler.py` にも `days2x_percent()` のテストが 5 本ある
（`test_days2x_percent_*`）。対象が消えるのでこれらも消す。
ただし**観点は減らさない**こと。JavaScript 側の `days2xPercent()` を
`tests/test_browser.py` の `page.evaluate()` で呼べば、同じ 5 つの観点
（0 のとき 0 / 符号が対称 / 単調に増える / 30y で 50% に張り付く /
それを超えても 50% のまま）をブラウザ側で見られる。
`test_x_percent2days_inverts_days2x_percent` が同じやり方をしているので、
それに倣うこと。

`tests/README.md` の `test_handler.py` の説明（「`days2x_percent` の
テスト」）も直す。
