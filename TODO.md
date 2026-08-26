# TODO

**残っている項目: TODO-051・TODO-056・TODO-062・TODO-063。**
これまでに 60 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-065` から。**

着手する項目は利用者が指定する。

---

## TODO-051. `DISPLAY` があると画面のキャプチャが撮れないのを直す（保留）

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ + verifier |

- [ ] `tools/screenshot.py` が `DISPLAY` を外して chromium を起動するようにする
- [ ] `DISPLAY` がある状態と無い状態の両方で撮れることを確かめる
- [ ] `docs/Developer.md` の「画面を撮る」に、この事情を書き足す

**2026-08-25 に着手したが、症状が再現しなかったので保留にした。**

### 症状

TODO-047 で分かった。`DISPLAY=localhost:11.0`（ssh の X11 転送）が設定されて
いると、`Page.screenshot()` が「fonts loaded」の直後で 30 秒待ってタイムアウト
する。`env -u DISPLAY` を付けると通る。playwright 1.55.0・1.58.0・1.61.0・
1.62.0 の 4 つ、chromium の起動オプション 4 通り（`--disable-gpu` ほか）、
`<h1>hello</h1>` だけのページでも同じで、ページの高さも関係なかった。

### 保留にした理由

**2026-08-25 に、同じ条件（`DISPLAY=localhost:11.0`、playwright 1.62.0、
chromium 151.0.7922.137）のはずが、どの撮り方でもそのまま撮れた。** 環境に
よって出たり出なかったりすることになり、直したかどうかを確かめられない。
当時の X サーバーは、もう同じものを用意できない。

また撮れなくなったら、**そのときの `DISPLAY` と X サーバーの様子を控えてから**
着手する。headless で動かす以上 `DISPLAY` は要らないので、直し方は「常に外す」
でよさそうだという見立ては変わっていない。

### ついでに決めたこと

`DEF_URL` に `--urlprefix` の既定（`/ytsched`）が入っていなかった件は、
`http://localhost:10085/ytsched/` にすると決めて直した（2026-08-25）。編集画面は
前置きが無いと 404 になるため。`docs/Developer.md` の「画面を撮る」にも書いた。

### 確かめ方

- `DISPLAY` を設定した状態で `mise run shot` が通ること。
  **これが今できないことなので、いちばん大事**
- `env -u DISPLAY` を付けた状態でも今までどおり通ること
- 保存された PNG が壊れていないこと（`file` で見る）

---

## TODO-056. JavaScript の退行を捕まえられるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |

- [ ] ブラウザを動かすテストを、どう置くか決める
- [ ] TODO-049 のホームボタンの退行を捕まえるテストを書く
- [ ] `mise` のタスクと `docs/Developer.md` に、走らせ方を書く

TODO-049 から立てた（2026-08-26）。

### なぜやるか

**TODO-049 で `my.js` の `scrollToId()` に持ち込んだ退行（今日から離れた週で
ホームボタンを押すと、URL だけが今日に書き換わって画面は前の週のまま）を、
reviewer も verifier も捕まえられず、利用者が見つけた。** `tests/` には
ブラウザを起動するテストが 1 件も無く、`mise run test` は `pytest` だけで
JavaScript を実行しない。**`AsyncHTTPTestCase` では原理的に捕まえられない**
（HTML は返るが、`my.js` は動かない）。

**TODO-054 は、この穴が空いたまま済ませた**（2026-08-26）。確認は playwright を
手で動かして行っており（CDP の `Input.dispatchTouchEvent` でスワイプを組み立てた）、
**その手順は `archives/agents/TODO-054/verifier-report.md` にあり、ここで
テストを書くときにそのまま使える。**

### 決めること（着手するときに相談する）

- **playwright を `pytest` の依存に入れるかどうか。** 入れると `mise run test`
  が重くなる。`tools/screenshot.py` は `uv run --with playwright` で都度取って
  くる形にしてあり（TODO-046）、依存には入れていない。同じやり方で
  `mise run test:js` のような別のタスクに分ける手もある
- **どこまで書くか。** 今回の退行 1 件を捕まえるだけにするか、週送り・ホーム・
  検索結果からの移動といった主要な操作をひととおり押さえるか
- **ブラウザをどこから持ってくるか。** `tools/screenshot.py` はシステムの
  `/usr/bin/chromium` を使っている（`~/.cache/ms-playwright` にあるビルドは
  版が合わず起動しない。TODO-045）。テスト側も同じ前提でよいか

### 気をつけること

- **`--datadir` には必ず一時ディレクトリを指定する**
  （`~/ytsched/data` の実データを汚さない）
- **検索語は `conf.json` に残る。** TODO-049 の確認中、担当が使った検索語が
  一時ディレクトリの `conf.json` に残っていて、あとから同じデータディレクトリを
  見たときに検索モードのままになっていた。テストごとにデータディレクトリを
  分けるか、始めに消すこと

### 確かめ方

- TODO-049 のホームボタンの退行を、**わざと元へ戻したときに落ちる**こと。
  落ちないテストでは意味が無い
- 走らせ方が `docs/Developer.md` を読んで再現できること

---

## TODO-062. スワイプが、60px 動くまで指に追従しないのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ + verifier |

- [ ] 追従を始める条件を見直す
- [ ] 実機（スマホ）で、指に追従することを確かめる

2026-08-26 に、利用者から「スワイプしても画面が動くアニメーションが無い」と
言われて立てた。

### 分かっていること

`my.js` の `touchMoveHdr()` は、横に `SWIPE_MIN_X`（60px）動くまで
`translateX()` を掛けない。縦スクロールを邪魔しないための条件だが
（TODO-054）、そのぶん**指を 60px 動かすまで画面はまったく動かず、超えた
瞬間に 60px 飛ぶ**。指に追従している感じがしない。

指を離したあとの動き（0.2 秒で隣の週まで滑る。`slideWeekWrap()`）と、
検索モードで滑らないこと（隣の週がそもそも DOM に無い。
`hasAdjacentWeek()`）は、どちらも TODO-057 で決めたとおりで、ここでは
変えない。

### 決めること（着手するときに相談する）

- **閾値をどう変えるか。** 60px を下げるだけにするか、横向きと判定する
  までは指の動きより小さく動かすか、判定した時点で 60px を引いてから
  追従させるか
- **縦スクロールを邪魔しないか。** 閾値を下げると、縦に
  スクロールしたいだけの指で週が動きだす。どこまで下げられるかは実機で
  試す

### 確かめ方

- 実機（スマホ）で、指の動きに合わせて隣の週が見えてくること
- 縦スクロールが、今までどおりできること
- 週送り（画面幅の 1/3 以上動かす・速く払う）が今までどおり効くこと

---

## TODO-063. 週送りが、同じ週の月曜に止まるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier + reviewer |

- [ ] `moveToMonday()` が、表示している週の月曜を基準に前後の月曜を出すようにする
- [ ] ホームボタンのあと、左の矢印・左スワイプで前の週へ行くことを確かめる

2026-08-26 に、利用者から「ホームボタンで今日に移動したあと、左の矢印や
左スワイプで前の週に行かない」と言われて立てた。

### 分かっていること

`my.js` の `moveToMonday()` は、`cur_day`（今表示している日付）から前後の
月曜を計算する。

```javascript
days = 1 - wday;      // 月曜までの戻り
if (days == 0) {
    days = -7;        // Mon
}
```

`cur_day` が月曜なら 7 日前の月曜になるが、**週の途中（例: 水曜）だと
「同じ週の月曜」になる**。ホームボタンは `date=今日` を渡すので、今日が
水曜なら `cur_day` は水曜。前の週へ行こうとしても同じ週の月曜で止まる。

サーバー側は渡された日付から月曜を計算して週を出しているので
（`main_handler.py:913`）、**表示されている週は今週で正しい。ずれている
のは `cur_day` だけ**。

### 直し方

**`moveToMonday()` の側を直す**（2026-08-26 に相談して決めた）。`cur_day`
をまず「その週の月曜」に丸めてから、前後へ 7 日ずらす。ホームボタンが渡す
日付を月曜に変える手もあるが、それだと検索結果から週の途中の日付で開いた
ときに同じことが起きる。

**ホームボタンで移動したあとのスクロール位置は、今までどおり今日の
ブロックに合わせる**（利用者に確認済み）。週の先頭には合わせ直さない。

### 確かめ方

- 今日が月曜以外の日に、ホームボタン → 左の矢印で前の週へ行くこと
- 同じく、右の矢印で次の週へ行くこと
- 月曜を表示しているときの週送りが、今までどおり効くこと
- 検索結果から週の途中の日付で開いたあとも、前後の週へ行けること

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-064.** PC のマウスの左右ドラッグでも週を送れるようにする](archives/todo/TODO-064.%20PC%20のマウスの左右ドラッグでも週を送れるようにする.md)
- [**TODO-061.** スマホの幅で、ヘッダとフッタの表示が崩れるのを直す](archives/todo/TODO-061.%20スマホの幅で、ヘッダとフッタの表示が崩れるのを直す.md)
- [**TODO-057.** スワイプで隣の週を指に追従させる](archives/todo/TODO-057.%20スワイプで隣の週を指に追従させる.md)
- [**TODO-060.** ゲージの針が、毎回中央から動き出すのを直す](archives/todo/TODO-060.%20ゲージの針が、毎回中央から動き出すのを直す.md)
- [**TODO-059.** ゲージの目盛りを詰めて、3m・3y・10y を足す](archives/todo/TODO-059.%20ゲージの目盛りを詰めて、3m・3y・10y%20を足す.md)
- [**TODO-058.** ヘッダに横向きのゲージを出す](archives/todo/TODO-058.%20ヘッダに横向きのゲージを出す.md)
- [**TODO-055.** 週表示に合わせて、ヘッダと日付欄を直す](archives/todo/TODO-055.%20週表示に合わせて、ヘッダと日付欄を直す.md)
- [**TODO-054.** 左右のスワイプで週を送る](archives/todo/TODO-054.%20左右のスワイプで週を送る.md)
- [**TODO-049.** 1 画面 1 週間の表示にする](archives/todo/TODO-049.%201%20画面%201%20週間の表示にする.md)
- [**TODO-048.** Font Awesome をやめて、自作の SVG アイコンにする](archives/todo/TODO-048.%20Font%20Awesome%20をやめて、自作の%20SVG%20アイコンにする.md)
- [**TODO-052.** 項目を立てる・アーカイブする作業のトークンを減らす](archives/todo/TODO-052.%20項目を立てる・アーカイブする作業のトークンを減らす.md)
- [**TODO-053.** キャプチャで、404 のページを黙って撮ってしまうのを直す](archives/todo/TODO-053.%20キャプチャで、404%20のページを黙って撮ってしまうのを直す.md)
- [**TODO-050.** 週を URL に持たせて GET にする](archives/todo/TODO-050.%20週を%20URL%20に持たせて%20GET%20にする.md)
- [**TODO-047.** Bootstrap をやめて、素の CSS にする](archives/todo/TODO-047.%20Bootstrap%20をやめて、素の%20CSS%20にする.md)
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
