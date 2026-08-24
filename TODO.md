# TODO

**残っている項目: TODO-047・TODO-048・TODO-049。**
これまでに 46 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-050` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にある。既存データは
`ytsched migrate` で一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-047. Bootstrap をやめて、素の CSS にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

- [ ] いま使っている Bootstrap のクラスの代わりを `my.css` に書く
- [ ] `base.html` から `bootstrap.min.css` の読み込みを外す
- [ ] `static/vendor/bootstrap/` を消す
- [ ] 見た目が変わっていないことを、変更の前後のキャプチャで確かめる

### いま使っているもの

`base.html` が読み込んでいるのは `bootstrap.min.css`（v5.3.8、236KB）だけで、
Bootstrap の JavaScript は入っていない。テンプレート 4 つで使っている
Bootstrap のクラスは、次の 3 種類にとどまる。

- グリッド: `container-fluid` `row` `col` `col-1`〜`col-11`
- 余白: `p-0` `p-1` `m-0` `m-1`
- 配置ほか: `text-center` `text-start` `text-end` `align-middle`
  `align-bottom` `d-none` `border` `fixed-bottom` `alert` `alert-danger`

ドロップダウン・モーダル・折りたたみは使っていない。メニューの開閉は
`#menu-sw:checked ~ .my-bar-content` という CSS で書いてある（`my.css`）。

### なぜやるか

- 236KB のうち、使っているのは上の 3 種類だけ
- フレームワーク側の変更に振り回される。既定のフォントが変わって行の高さが
  ずれた件（TODO-040）のせいで、`--bs-body-font-family` を固定している
- `my.css` にある 5 か所の `!important` は、Bootstrap の詳細度
  （specificity）に勝つためのもの。外せば要らなくなる

### 気をつけること

- `row` / `col-N` は Bootstrap では flexbox だが、CSS Grid に置き換える。
  flex の子が既定の `min-width: auto` で縮まない件（TODO-045、`.longtext`）
  も、そのときに見直す
- `align-middle` は `vertical-align: middle` で、Grid の `align-self: center`
  とは別物。どちらの意味で使っている箇所なのかを、テンプレートごとに見る
- `alert` / `alert-danger` は `main.html` の 1 か所だけ
- Font Awesome（288KB）も、使っているアイコンは 25 種類ほどしかないが、
  今回は触らない。減らすなら別の項目にする

### 確かめ方

見た目を変えないための項目なので、テストでは確かめられない。
`tools/screenshot.py`（TODO-046）で変更の前と後のキャプチャを撮り、
突き合わせる。幅は既定の 412px と 800px。一覧（`main.html`）と
編集画面（`edit.html`）の両方を撮ること。

---

## TODO-048. Font Awesome をやめて、アイコンを SVG にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier |

- [ ] 使っている 23 個のアイコンの SVG を用意する
- [ ] それをまとめた `icons.svg` を作り、`static/icons/` に置く
- [ ] テンプレートの `<i class="fas fa-...">` を `<svg><use></svg>` に
      置き換える
- [ ] 大きさ（`fa-lg` / `fa-2x` / `fa-9x`）と回転（`fa-spin`）の代わりを
      `my.css` に書く（`.my-spinner` の隣に置く）
- [ ] `base.html` から `all.css` の読み込みを外し、
      `static/vendor/fontawesome/` を消す
- [ ] 見た目が変わっていないことを、変更の前後のキャプチャで確かめる

TODO-047（Bootstrap をやめる）とは独立していて、どちらを先にやってもよい。
触るファイルは重なるので、同時には進めないこと。

### いま使っているもの

`static/vendor/fontawesome/` は 288KB（`all.css` 130KB、`fa-solid-900.woff2`
119KB、`fa-regular-400.woff2` 20KB）。読み込んでいるのは `base.html` の
1 行だけで、Python・JavaScript・CSS からは参照していない
（`my.css` のコメントに 2 か所出てくるだけ）。

使っているアイコンは 23 個。

| 種類 | アイコン |
|------|---------|
| solid（`fas`）19 個 | `angle-down` `arrow-alt-circle-up` `arrows-alt-h` `backspace` `bars` `check-square` `chevron-left` `chevron-right` `clone` `exclamation-triangle` `filter` `home` `list-alt` `plus-square` `reply` `search` `spinner` `sync` `trash-alt` |
| regular（`far`）4 個 | `arrow-alt-circle-up` `arrow-alt-circle-down` `dot-circle` `square` |

`arrow-alt-circle-up` は solid と regular の両方を使っていて、
字形が違うので SVG も別々に要る（名前としては 22 種類）。
大きさは `fa-lg`（1.25em）・`fa-2x`（2em）・`fa-9x`（9em）で指定して
いて、読み込み中のしるしは `fa-spin`（2 秒・linear・無限）で回している。

### なぜやるか

- 288KB のうち、使っているのは 22 個だけ。SVG にすれば数 KB で足りる
- **アイコンフォントは、フォント側の既定値が変わると位置がずれる。**
  ゲージの針と基準線がずれた件（TODO-042）がそれで、TODO-043 で SVG に
  描き直して直した。今回は残りのアイコンに同じことをする
- フォントの読み込みが終わるまでアイコンが出ない

### やり方

TODO-043 は SVG をテンプレートに直接書いたが、今回は 22 個あり、
同じアイコンを 2 か所で使うものもある。`<symbol>` を並べた 1 つの
`icons.svg` を置き、各所からは `<use>` で参照する形にする。

```html
<svg class="my-icon my-icon-lg">
  <use href="{{ static_url('icons/icons.svg') }}#home"></use>
</svg>
```

色は `fill: currentColor` にすれば、いまと同じく親の文字色に従う。

SVG の元をどこから持ってくるかは、着手するときに決める。

- **woff2 から取り出す。** いま入っている 7.3.1 の字形と必ず一致する。
  `all.css` が `--fa: "\f015"` の形でコードポイントを持っているので、
  そこから引ける。`uv run --with fonttools` で変換できるが、フォントの
  座標系は y 軸が上向きなので、反転が要る
- **配布物から取る。** Font Awesome Free の zip に `svgs/` がある。
  単純だが、ネットワークが要る

### ライセンス

Font Awesome Free は、**フォントが SIL OFL 1.1、アイコン（SVG）は
CC BY 4.0** と、部分ごとに違う。SVG を持つ形に変えると CC BY 4.0 の
ほうになり、帰属表示が要る。`vendor/fontawesome/LICENSE.txt` を消さずに
`static/icons/` へ移し、出典を書き添えること。

### 確かめ方

見た目を変えないための項目なので、テストでは確かめられない。
`tools/screenshot.py`（TODO-046）で変更の前と後のキャプチャを撮り、
突き合わせる。アイコンは一覧・編集画面・メニューバーに散っているので、
一覧（`main.html`）と編集画面（`edit.html`）の両方を、開いた状態も
含めて撮ること。読み込み中のしるし（`fa-spinner` + `fa-spin`）は
キャプチャに写らないので、別に見ること。

---

## TODO-049. 1 画面 1 週間の表示にして、左右のスワイプで週を送る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

- [ ] 1 画面に月曜から日曜までの 1 週間だけを出す
- [ ] 左右のスワイプで週を送る
- [ ] ゲージを週単位にする
- [ ] 今の縦に並べる表示（スクロールでの追加読み込み）を外す
- [ ] 見た目と操作を、変更の前後のキャプチャで確かめる

### なぜやるか

システム手帳の使用感に近づけ、直感的に操作できるようにする。今は
前後 45 日（`DEF_DAYS`）の範囲を縦に連続して並べ、画面の端まで
スクロールすると次を読み直している。どこを見ているのかが分かりにくく、
1 週間という区切りも画面からは読み取れない。

### 表示の形

- **月曜が先頭、日曜が末尾**の 1 週間だけを 1 画面に出す
- 1 週間分が 1 画面に収まらないときは、今までどおり上下にスクロールする
- 左右のスワイプで週を進めたり戻したりする
- 上記以外は今と同じ

下部のメニューバーにある ←/→ は、すでに `moveToMonday()` で
「次（前）の月曜へ」動いているので、考え方は変えずに済む。

### ゲージ

**週単位にして残す。**変えるのは針に渡す値だけで、対数目盛りの仕組みは
そのまま使える。

| | 今 | 週単位にしたら |
|---|---|---|
| 針の位置の元になる値 | `getTopDateString()`（画面最上部に見えている日） | 表示中の週の月曜 |
| 針を動かす仕掛け | スクロールのたびに `scrollHdr0` → `dispGage` | 週を切り替えたときだけ |
| `days2yOffset()` / `days2y_offset()` | 対数スケール | そのまま |
| ラベル（`GAGE`、-30y〜+30y） | 固定位置 | そのまま |
| 基準線 `gage_r_base` | 今日 = 0 | 今週の月曜 = 0 |

`my.js` からはスクロールへの追従が消えるので、`scrollHdr()` /
`scrollHdr0()` / `getTopDateString()` が要らなくなる。Python 側の
`GAGE` は手を入れずに済む。

基準線の意味が「今日」から「今週の月曜」に変わるのは、むしろ分かり
やすくなる。今は今日を表示していても画面最上部の日が今日とは限らず
針がずれるが、週単位なら今週を出している間は必ず基準線に重なる。

針は 7 日刻みで飛ぶことになるが、位置は十分読める。

| 週 | 針の位置(px) | 隣の週との差 |
|---|---|---|
| ±1週 | 62 | 62 |
| ±2週 | 82 | 20 |
| ±3週 | 93 | 11 |
| ±4週 | 102 | 9 |
| ±13週(3ヶ月) | 137 | 2 |
| ±52週(1年) | 179 | 0.4 |

遠くなるほど 1px を切るが、それは今の日単位でも同じで、「だいたい
どのへんか」を見るためのものなので構わない。

- **ラベルは今のまま。**目盛りが対数なので、ラベルも `1m` `3m` `1y`
  `3y` `10y` `30y` と対数的に並んでいる。`±4w` のような等間隔の週表記に
  置き換えると、近くだけ間延びして遠くは重なり、1 画面に数十年が収まる
  という利点が消える
- 針が飛ぶので、CSS の `transition` で滑らせる。針が上下に動くのが
  見えれば、それ自体が「どちらへめくったか」の手がかりになる

### ToDo

**今のままにする。**期限が `todo_days` で指定した日数以内になった ToDo を
今日の欄にも出す仕組み（`load_todo()` の `todo_today_sde`）は変えない。
今日を含む週を表示しているときに見える、という点も今と同じ。

### 一緒に考えた案

この項目に入れるかどうかは、見直すときに決める。

1. **週を URL に持たせて GET にする**（`/?date=2026-08-24` など）。今は
   `doPost()` が form を作って submit しているので、ブラウザの戻る/進むが
   使えず、リロードすると再送信になる。URL にすれば戻る＝前に見ていた週に
   なり、`history.pushState` とも噛み合い、iOS の画面端スワイプ（戻る）とも
   競合しない。**スワイプの土台になるので、分けて先にやる案もある**
2. **前後の週を先読みして DOM に持つ。**3 週分（前・今・次）を持てば、
   スワイプの瞬間に切り替わり、裏で次を取りに行ける
3. **スワイプを指に追従させる。**閾値を超えたら切り替えるだけでも動くが、
   隣の週が指について出てくるとめくった感じが出る。ゲージの
   `transition` で代用できるかもしれない
4. **今週から何週離れているかを出す。**今は各日に `+3` のような日数差が
   出ている。週表示ならヘッダに `+3w` を出し、今週から離れているときだけ
   ホームボタンを目立たせる
5. **日の欄そのものをタップで追加。**週表示だと 1 日あたりの余白が広く
   なるので、今の小さな `+` ボタンでなく、空き領域を押したらその日の
   編集画面へ、が自然
6. **キーボードの ←/→ で週送り**（PC で見るとき）
7. **ゲージを触って週へ飛ぶ。**今のゲージは表示専用だが、上下に
   ドラッグすれば近くは 1 週ずつ、遠くは数年先まで一気に移動できる。
   週単位なら飛び先が「その週」に定まるので、日単位のときより素直に作れる
8. **予定をドラッグして別の日へ移す。**システム手帳の使用感には一番近いが、
   タッチのドラッグ処理と保存が要り、他と比べて重い。**後回しにする**

### 決めること

- **7 日の並べ方。**今の日付ブロックの形のまま縦に 7 日並べるか、横 7 列に
  するか。スマホの縦画面では 1 列あたり 50px 前後になり、予定が多い日は
  読めなくなるので、縦 7 行を勧める
- **上の案 1（URL・GET 化）を別の項目にするか。**土台になるので分けて
  先にやるほうが安全だが、手戻りは増える
- **検索モードの表示。**検索結果は日付が飛び飛びなので、週の区切りに
  合わない。検索中は週表示を外して今の縦に並べる表示を出すのが素直だが、
  それでよいか
- 上の案のうち、どれをこの項目に含めるか

### 気をつけること

- **TODO-047（Bootstrap をやめる）・TODO-048（Font Awesome をやめる）と、
  触るファイルが重なる。**同時には進めないこと
- **iOS Safari の画面端スワイプ（戻る）と競合する。**画面の左端から始まる
  横スワイプは OS に取られる
- **縦スクロールと横スワイプの切り分けが要る。**1 週間分が画面に収まらない
  ときは上下にスクロールするので、縦の動きが優勢なら横スワイプを無視する

### 確かめ方

見た目と操作が変わる項目なので、`tools/screenshot.py`（TODO-046）で
変更の前と後のキャプチャを撮って突き合わせる。幅は既定の 412px と 800px。
週を送ったあと、今週へ戻ったあと、検索したあとの 3 つの状態を撮ること。
ゲージの針が週ごとに正しい位置へ動くかは、今週・±1 週・±1 年で見る。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-046.** 画面のキャプチャを撮るスクリプトを置く](archives/todo/TODO-046.%20画面のキャプチャを撮るスクリプトを置く.md)
- [**TODO-045.** 詳細（detail）の見え方を直す](archives/todo/TODO-045.%20詳細（detail）の見え方を直す.md)
- [**TODO-044.** トークン消費の測り方と、担当の走らせ方を見直す](archives/todo/TODO-044.%20トークン消費の測り方と、担当の走らせ方を見直す.md)
- [**TODO-043.** ゲージの針と基準線を、アイコンフォントでなく図形で描く](archives/todo/TODO-043.%20ゲージの針と基準線を、アイコンフォントでなく図形で描く.md)
- [**TODO-042.** 左端のゲージの針の位置がずれているのを直す](archives/todo/TODO-042.%20左端のゲージの針の位置がずれているのを直す.md)
- [**TODO-041.** 追加読み込みのたびに自動スクロールが起きるのを直す](archives/todo/TODO-041.%20追加読み込みのたびに自動スクロールが起きるのを直す.md)
- [**TODO-039.** スマホ用の設定を追加](archives/todo/TODO-039.%20スマホ用の設定を追加.md)
- [**TODO-040.** bootstrap, fontawesome のバージョンアップ](archives/todo/TODO-040.%20bootstrap,%20fontawesomeのバージョンアップ.md)
- [**TODO-038.** HTML・CSS のリファクタリング](archives/todo/TODO-038.%20HTML・CSS%20のリファクタリング.md)
- [**TODO-037.** CDNに依存しないよう同梱する](archives/todo/TODO-037.%20CDNに依存しないよう同梱する.md)
- [**TODO-036.** click_utils.py を導入する](archives/todo/TODO-036.%20click_utils.py%20を導入する.md)
- [**TODO-032.** `Conf.cgi` を JSON 形式にする](archives/todo/TODO-032.%20Conf.cgi%20を%20JSON%20形式にする.md)
- [**TODO-031.** 文書に Mermaid の図を入れる](archives/todo/TODO-031.%20文書に%20Mermaid%20の図を入れる.md)
- [**TODO-035.** TODO 項目ごとのトークン消費量を記録する](archives/todo/TODO-035.%20TODO%20項目ごとのトークン消費量を記録する.md)
- [**TODO-034.** `orig_date` と `expanduser()` の紛らわしいところを片付ける](archives/todo/TODO-034.%20orig_date%20と%20expanduser%20の紛らわしいところを片付ける.md)
- [**TODO-029.** コードレビューで見つかった 3 件を直す](archives/todo/TODO-029.%20コードレビューで見つかった%203%20件を直す.md)
- [**TODO-028.** リファクタリングで見つかった残り 5 件を直す](archives/todo/TODO-028.%20リファクタリングで見つかった残り%205%20件を直す.md)
- [**TODO-027.** 不正な入力で 500 になるのをやめる](archives/todo/TODO-027.%20不正な入力で%20500%20になるのをやめる.md)
- [**TODO-033.** URL_PREFIX の改名に追随できていない箇所を直す](archives/todo/TODO-033.%20URL_PREFIX%20の改名に追随できていない箇所を直す.md)
- [**TODO-030.** ドキュメントの役割を分ける](archives/todo/TODO-030.%20ドキュメントの役割を分ける.md)
- [**TODO-023.** mise.toml の見直し](archives/todo/TODO-023.%20mise.toml%20の見直し.md)
- [**TODO-024.** リファクタリングで見つかった 8 件の扱い](archives/todo/TODO-024.%20リファクタリングで見つかった%208%20件の扱い.md)
- [**TODO-026.** 文書の確認の担当と hook を作る](archives/todo/TODO-026.%20文書の確認の担当と%20hook%20を作る.md)
- [**TODO-025.** 文書の確認を分ける仕組みを決める](archives/todo/TODO-025.%20文書の確認を分ける仕組みを決める.md)
- [**TODO-022.** 軽量な担当 runner を作る](archives/todo/TODO-022.%20軽量な担当%20runner%20を作る.md)
- [**TODO-021.** リファクタリング（挙動は変えない）](archives/todo/TODO-021.%20リファクタリング（挙動は変えない）.md)
- [**TODO-020.** JSON Lines への移行ツールと、読み書きの実装](archives/todo/TODO-020.%20JSON%20Lines%20への移行ツールと、読み書きの実装.md)
- [**TODO-019.** 移行元のテストデータを作る](archives/todo/TODO-019.%20移行元のテストデータを作る.md)
- [**TODO-018.** データ形式の見直し（何を変えるかを決める）](archives/todo/TODO-018.%20データ形式の見直し（何を変えるかを決める）.md)
- [**TODO-017.** reviewer の起用基準と、verifier を一律で立てる運用の見直し](archives/todo/TODO-017.%20reviewer%20の起用基準と%20verifier%20の運用.md)
- [**TODO-016.** `date` が空の POST と、存在しない `sde_id` の扱い](archives/todo/TODO-016.%20date%20が空の%20POST%20と、存在しない%20sde_id%20の扱い.md)
- [**TODO-015.** ruff の整形・書き換え系の指摘を解消](archives/todo/TODO-015.%20ruff%20の整形・書き換え系の指摘を解消.md)
- [**TODO-012.** 不正な正規表現を入れられたときの扱い](archives/todo/TODO-012.%20不正な正規表現を入れられたときの扱い.md)
- [**TODO-010.** CLAUDE.md の作成](archives/todo/TODO-010.%20CLAUDE.md%20の作成.md)
- [**TODO-009.** README の更新](archives/todo/TODO-009.%20README%20の更新.md)
- [**TODO-008.** uv tool install 方式へ](archives/todo/TODO-008.%20uv%20tool%20install%20方式へ.md)
- [**TODO-007.** loguru への移行](archives/todo/TODO-007.%20loguru%20への移行.md)
- [**TODO-006.** 型ヒントの整備](archives/todo/TODO-006.%20型ヒントの整備.md)
- [**TODO-004.** lint・型チェックと mise タスク](archives/todo/TODO-004.%20lint・型チェックと%20mise%20タスク.md)
- [**TODO-014.** サブエージェントの報告ファイル名](archives/todo/TODO-014.%20サブエージェントの報告ファイル名.md)
- [**TODO-005.** 明らかなバグの修正](archives/todo/TODO-005.%20明らかなバグの修正.md)
- [**TODO-003.** pytest によるテスト整備](archives/todo/TODO-003.%20pytest%20によるテスト整備.md)
- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
