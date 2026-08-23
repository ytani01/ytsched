# TODO-038 implementer への依頼（2 段目・style 属性を CSS へ）

`TODO.md` の TODO-038 と、
[1 段目の依頼](implementer-request-1.md)・[1 段目の報告](implementer-report-1.md)
を読んでから始めること。1 段目（消すもの・直すもの）は済んでいる。

**2 段目は見た目を 1 画素も変えないのが目標。** main が同梱前後の画面を
画素単位で比べる。行の高さが 1px ずれただけでも出る。

## やること

`style` 属性を `static/css/my.css` のクラスへ寄せる。対象は
`main.html` / `sde.html` / `edit.html`。

### 寄せるもの / 残すもの

- **値が固定のものは CSS へ。** `font-size: x-small` `line-height: 12px`
  `text-align: center` など
- **データで変わるものは、クラスで表す。** 下に一覧を出す
- **JS が書き換えるものは、インラインのまま残す。**
  `#main` の `visibility`、`#loadingSpinner` の `display`、ゲージの
  `bottom`（`my.js` の `dispGage()` と `main.html` の `onloadHdr()` が
  触る）。**ここを CSS へ動かすと動かなくなる**

### クラスにするもの（データで変わるもの）

`main.html`

- 曜日の背景色 7 色（`bg_color_wday` の配列）→ `.wday-0`〜`.wday-6`
  のような 7 つのクラス。テンプレート側は
  `class="… wday-{{ weekday }}"` で済むようにする
- 日付ブロックの枠（通常 `2px solid #888` / 今日 `4px solid #28F`）
  → 2 つのクラス。`!important` が付いているので、外すと Bootstrap の
  `.border` に負ける。**同じ見え方になることを確かめること**
- 今日の `font-weight: bold`

`sde.html`

- 背景色 4 通り — 通常 `#FFF`、祝日 `#FAA`、ToDo は期限で
  `#FFE`（先）/ `#FFC`（1 週間以内）/ `#EEB`（過ぎた）
- `is_important()` の `font-weight: bold`（種別とタイトルの 2 か所）
- `is_canceled()` の取り消し線 — **下に注意を書く**

### 取り消し線（`is_canceled()`）の注意

いま `{% if sde.is_canceled() %}<span style="text-decoration: line-through">`
が**入れ子で 6 か所**繰り返されている。これを減らすのがこの項目の眼目だが、
**外側の 1 つにまとめてはいけない。**

- ToDo の行には、左端に `<i class="far fa-square">`（□ のアイコン）が
  ある。これは**今は取り消し線が引かれていない**。いちばん外側の
  `container-fluid` にクラスを付けると、□ にも線が入って見た目が変わる
- まとめるなら、**時刻の欄（`col-1`）・本文の欄（`col-11`）・詳細の欄**
  の 3 か所に付ける形にする。6 か所が 3 か所になれば十分

`text-decoration: line-through !important` の `!important` も、外すと
Bootstrap に負ける可能性がある。外す前に画面で確かめること。

### そのまま残すもの（消さない・動かさない）

- `sde.html` のいちばん外側の `font-size: 0`。**これは意味がある**
  （`display: inline-flex` の要素どうしの隙間を消している）。
  消すと横方向にずれる
- `border-radius` の値（`0px 15px 15px 0px` など）。見た目そのもの
- `main.html` の `padding-left: 22px`（ゲージの幅ぶん）

## クラス名の付け方

既にあるものに合わせる。`my.css` は `.my-bar` `.my-btn` `.my-osd-base`
`.my-gage` `.longtext` のように、**このアプリ独自のものに `my-` を
付けている**。Bootstrap のクラス名とぶつからないようにするためなので、
新しく足すものも同じ形にする（`.my-wday-0` `.my-sde-todo` など）。

`.longtext` のように `my-` が付いていないものもあるが、それに揃えない
こと（`my-` を付けるほうが多数派で、ぶつかりにくい）。

## 確かめること（自分の範囲で）

- `mise run test` が通る
- `mise run lint` が通る
- **一時ディレクトリ**を `--datadir` に指定し、**ポート 10096** で起動して、
  一覧・編集の両方が 200 で返ること
- `style="` の数が減っていること（前後の数を報告に書く）

**見た目の比較は main がやる。** ここでは「変えていないつもり」で
止めてよいが、**自分が見た目を変えたかもしれないと思ったところは、
全部報告に書くこと。** main が重点的に見る。

## 環境の注意

- **ポート 12345 で利用者が `ytsched` を動かしている。止めないこと**
- 起動には 10096 を使う
- `mise run upgradeproject` は走らせない

## 決まりごと

- **`TODO.md` は編集しない。git commit もしない**
- 報告は `archives/agents/TODO-038/implementer-report-2.md` に書き、
  返事は 5 行以内で
