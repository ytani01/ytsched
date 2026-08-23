# TODO-038 implementer への依頼（3 段目・クラス名の付け直し）

`TODO.md` の TODO-038 と、
[2 段目の依頼](implementer-request-2.md)・[2 段目の報告](implementer-report-2.md)
を読んでから始めること。1 段目・2 段目の変更は作業ツリーに未コミットで入っている。

2 段目で追加したクラスのうち、**値をそのまま名前にしたもの**を整理する。
`style` 属性を CSS へ寄せる利点は 2 つあって、
（1）インライン `style` を無くす、（2）同じ役割の箇所を 1 か所で変えられる
ようにする ——(2) は**役割で名付けたときだけ効く**。`.my-fs-xx-small` は
`style="font-size: xx-small"` の別名でしかなく、`xx-small` をやめたく
なった時点で名前が嘘になる。

**3 段目も見た目を 1 画素も変えないのが目標。** CSS の値は 1 つも変えない。
名前と、どの要素に付けるかだけを変える。

## やること 1 ── Bootstrap にあるものは自前で定義しない

同梱している Bootstrap は **4.5.0**。次の 4 つは Bootstrap に同じものが
あるので、テンプレート側を置き換え、`my.css` からは**定義ごと消す**。

| 消す（`my.css`） | 使用箇所 | 置き換え先（Bootstrap 4.5） |
|---|---|---|
| `.my-va-middle` | 11 | `.align-middle` |
| `.my-fw-bold`   | 4  | `.font-weight-bold` |
| `.my-va-bottom` | 3  | `.align-bottom` |
| `.my-hidden`    | 2  | `.d-none` |

**Bootstrap 側はどれも `!important` が付いている**（`.font-weight-bold` は
`font-weight: 700!important`）。計算後の値は同じはずだが、`!important` が
効いて他の宣言に勝つようになる可能性があるので、**画素単位の比較で
確かめること**。

`.my-fw-bold` は `sde.html` の `class_type` / `class_title` と
`main.html` の `class_today` から参照されている。やること 2 で
`class_type` / `class_title` は無くなるので、そちらを先にやってもよい。

## やること 2 ── 役割がはっきりしている箇所は役割で名付ける

値をそのままの名前で残すのは、**役割がまとめられない 1 か所きりの
ところだけ**にする。下の表のとおりに直す。数値は**いま CSS に書いてある値を
そのまま持ってくる**（変えない）。

### `sde.html`

| いまの `class` | 新しいクラス | 中身 |
|---|---|---|
| `my-fs-xx-small my-fw-bold my-lh-12`（時刻の欄 `col-1`） | `.my-sde-time` | `font-size: xx-small; font-weight: bold; line-height: 12px` |
| `my-fs-small`（ToDo の □ の `<i class="far fa-square">`） | `.my-sde-check` | `font-size: small` |
| `class_type` の `my-fs-x-small` | `.my-sde-type` | `font-size: x-small` |
| `class_title` の `my-fs-medium` | `.my-sde-title` | `font-size: medium` |
| `my-fs-small`（`@{{ sde.place }}` の `<span>`） | `.my-sde-place` | `font-size: small` |
| `my-fs-small my-lh-10`（詳細の開閉ラベルの `col-1`） | `.my-sde-detail-sw` | `font-size: small; line-height: 10px` |
| `my-fs-x-small`（詳細本文の `col-11 longtext`） | `.my-sde-detail` | `font-size: x-small` |

**重要（`is_important()`）の太字は、種別・タイトルとは別のクラスに分ける。**
いまは `class_type` / `class_title` の 2 つの変数それぞれに
`my-fw-bold` を足し込んでいて、`{% if %}` の中で 4 行書いている。
次の形にすれば 2 行で済み、種別とタイトルの `class` も固定になる。

```
{% set class_important = '' %}
{% if sde.is_important() %}
{% set class_important = 'font-weight-bold' %}
{% end %}
...
<span class="my-sde-type {{ class_important }}">
<span class="my-sde-title {{ class_important }}">
```

これで `sde.html` から `my-fs-*` / `my-lh-*` / `my-fw-bold` が全部消える。
**消えていることを grep で確かめること。**

### `main.html` の日付ブロック（`my-date-col` の中の 4 つの `div`）

| いまの `class` | 新しいクラス | 中身 |
|---|---|---|
| `text-left my-lh-12` | `text-left` + `.my-date-ym` | `line-height: 12px` |
| 　└ `my-fs-xx-small`（年） | `.my-date-year` | `font-size: xx-small` |
| 　└ `my-fs-small`（月） | `.my-date-month` | `font-size: small` |
| `text-center my-fs-large my-lh-16` | `text-center` + `.my-date-day` | `font-size: large; line-height: 16px` |
| `text-right my-fs-x-small my-lh-12` | `text-right` + `.my-date-wday` | `font-size: x-small; line-height: 12px` |
| `text-center my-fs-x-small my-lh-14` | `text-center` + `.my-date-diff` | `font-size: x-small; line-height: 14px` |

`text-left` / `text-center` / `text-right` は Bootstrap のまま残す。
`class_today` は `font-weight-bold`（やること 1）に置き換える。

### `edit.html`

`my-fs-large` が 6 か所にあり、**どれも「編集フォームの 1 行」**という
同じ役割。`.my-edit-row`（`font-size: large`）1 つにまとめる。

- `<div class="row p-1 my-fs-large">`（日付・時刻）→ `row p-1 my-edit-row`
- `<div class="row my-fs-large">`（タイトル・場所）→ `row my-edit-row`
- `<div id="div_detail" class="row p-0 my-fs-large">` → `row p-0 my-edit-row`
- 種別の行は `<div class="row">` の中の `<div class="col my-fs-large">` に
  付いている。**`row` のほうへ移して `col` からは外す**（他の行と揃う）。
  継承するので計算後の値は同じはずだが、**画素単位で確かめること**
- `<span class="my-fs-large">@</span>`（場所）は、親の行がすでに `large`
  なので**冗長。外せるはず**。外して画素が変わるなら残して報告すること

残りはこうする。

| いまの `class` | 新しいクラス | 中身 |
|---|---|---|
| `my-fs-x-large`（`【` `】` の 2 か所） | `.my-edit-bracket` | `font-size: x-large` |
| `my-fs-small`（`<span id="wday">`） | `.my-edit-wday` | `font-size: small` |
| `my-fs-x-small`（`#div_id` の行） | `.my-edit-id` | `font-size: x-small` |

これで `edit.html` からも `my-fs-*` が全部消える。**grep で確かめること。**

### 値そのままの名前で残すもの

`main.html` のメニューバー・検索欄まわりの 10 か所ほど。ここは 1 か所ずつ
役割が違い、名前を付けても使い回せない。`.my-fs-*` のまま残す。

## やること 3 ── 使われなくなった定義を消す

上の置き換えで参照が 0 になったクラスは、`my.css` から**定義ごと消す**。
`.my-lh-10` `.my-lh-12` `.my-lh-14` `.my-lh-16` は全部消えるはず。
`.my-fs-*` は `main.html` に残るものだけを残す。

**消す前に、`templates/` と `static/` を grep して参照が 0 であることを
確かめること。** 逆向きも見ること（`my.css` にある `.my-*` が全部
使われているか）。

## 確かめること

2 段目と同じやり方で、**画素単位の比較をもう一度やること**。
比較の相手は「3 段目を始める前の作業ツリー」（HEAD ではない。HEAD には
1 段目・2 段目が入っていない）。**main が退避してある**ので、これを使うこと。

```
/home/ytani/.claude/jobs/795ce790/tmp/webroot-before-step3/
```

`templates/` と `static/` がそのまま入っている。旧版のサーバを立てるときは、
このディレクトリを `webroot` として使えばよい（作業ツリーを汚さない）。
**この退避先は書き換えないこと。**

- 一覧・編集を、少なくとも **412 幅と 740 幅**で比べる
- **取り消し済みの予定・重要（★）の予定・ToDo（期限が過去 / 1 週間以内 /
  先）・祝日・今日の日付ブロック**を含むデータで比べること。
  今回いじる `class_important` と `class_today` はそこにしか出ない
- 詳細を開いた状態も比べること
- 2 段目の報告にある「取り消し済みの詳細を開くと空行が 2 行減る」は
  **そのままでよい**（利用者が了承済み）。3 段目でそれ以上変えないこと
- `mise run lint` / `mise run test` が通ること
- **一時ディレクトリ**を `--datadir` に指定し、**ポート 10096** で起動して
  一覧・編集が 200 で返ること

## 環境の注意

- **ポート 12345 で利用者が `ytsched` を動かしている。止めないこと**
- 起動には 10096 を使う。使い終わったら止めること
- `mise run upgradeproject` は走らせない
- **ファイルを作るときは絶対パスを使うこと**（1 段目で
  `src/ytsched/webroot/archives/` に作られてしまった）

## 決まりごと

- **`TODO.md` は編集しない。git commit もしない**
- 報告は
  `/home/ytani/work/ytsched/archives/agents/TODO-038/implementer-report-3.md`
  に書き、返事は 5 行以内で
