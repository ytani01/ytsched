# TODO

**残っている項目: TODO-080〜TODO-083。**
これまでに 79 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-084` から**（TODO-071 は欠番）。

着手する項目は利用者が指定する。

TODO-080〜083 は、基本設計のレビュー（2026-08-27）で挙がった 11 件を
振り分けたもの（TODO-077〜079 は決着済み）。中身は [`docs/design-review.md`](docs/design-review.md)
にある。**着手するときは、まずそちらの該当する節を読むこと。**

---

## TODO-080. キャッシュがファイルの更新に追随しないのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

- [ ] 読み込んだときの `mtime` を持たせ、変わっていたら読み直す
- [ ] `DEF_CACHE_SIZE`（20,000）を今の使い方に合わせて見直す

`SchedData._sdf_cache` は `mtime` を見ないので、`ytsched migrate` や
手でファイルを直しても、サーバが生きている間は古い内容を返し続ける。
ホームボタンのダブルタップは DOM を取り直すだけで、サーバ側は古いまま。

上限 20,000 件は、TODO-069 で 1 リクエスト 63 日ぶんを読むように
なる前の数字で、実際にはまず捨てられない。

詳しくは `docs/design-review.md` の C。

---

## TODO-081. ハンドラの役割と、依存の渡し方を整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

- [ ] 引数と設定値の変換・検証を `HandlerBase` から出す
- [ ] `SchedData` を `initialize()` で渡すようにする
- [ ] `CONF_KEY_LOAD_MONTHS` など、定数の置き場所のズレを直す

**挙動は変えない。** `handler.py` にあるのは「`conf.json` の読み書き」
「引数と設定値の変換・検証」「表示に使える日付の範囲」の 3 つで、
後ろの 2 つは `self` をログにしか使わない純粋な関数。
`RequestHandler` を継承していることと関係が無く、テストを書くのに
ハンドラを組み立てる必要がある。

依存は `tornado.web.Application` の設定に入れて
`app.settings.get("sd")` で取り出しているため、`self._sd` の型が
`Any` になり、型チェッカが `SchedData` として見られない。

詳しくは `docs/design-review.md` の D・G。

---

## TODO-082. import の意図と実態のズレ、使われていない属性、細かい 5 件を片付ける

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |

- [ ] `__init__.py` の import をやめるか、`migrate.py` のコメントを直すか決める
- [ ] 使われていない属性 3 つと、それを固定しているテスト
- [ ] `__main__.py` の docstring とヘルプの文字列、`x_data1` の扱い
- [ ] `webapp` の `--size_limit` の既定値を `DEF_SIZE_LIMIT` にする
- [ ] ruff の設定を `mise.toml` から `pyproject.toml` へ移す
- [ ] `SchedDataFile.__init__` のパスの分解を `os.path` にする

`migrate.py` は「`handler.py` を import すると移行ツールが tornado に
依存してしまう」と書いてあるのに、`__init__.py` が `MainHandler` と
`WebServer` を import しているので、`ytsched migrate` は結局 tornado を
読み込む。**決めること:** `__init__.py` の import をやめるか、
コメントを実情に合わせるか。

使われていない属性は `HandlerBase._app` / `_req`、
`SchedDataFile.filename` / `dirname`、`SchedData.get_keys()`。
どれもテストがアサートしているので、消すならテストも一緒に消す。

`x_data1` はデバッグ用と `src/README.md` にあるが、`ytsched --help` には
他の 2 つと並んで出る。**残すか消すかを決める。**

ruff は `ignore` だけが `pyproject.toml` にあり、`--line-length 78` と
`--extend-select I` は `mise.toml` のコマンド行にある。**移すのは
置き場所だけで、規則を増やすかどうかは別の項目にする。**

詳しくは `docs/design-review.md` の H・J・K。

---

## TODO-083. `my.js` と `main.html` の JavaScript を分ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

- [ ] グローバルな状態（`elMain` `activeWeekOffset` など）の持ち方を決める
- [ ] `my.js` を、コメントで分かれている 6 つに分ける
- [ ] `main.html` の `<script>` の関数本体を `my.js` 側へ移す

**挙動は変えない。** `my.js` 1,358 行がすべてトップレベルの
`const`／`let` で、中身はスピナー / ゲージ / URL と遷移 / 週の管理 /
キーボード / スワイプとマウスの 6 つにコメントで分かれている。
`main.html` の先頭にも 120 行の `<script>` があり、`my.js` の
グローバル変数を書き換えている（`// declared in my.js`）。
これが分けにくくしている一番の理由なので、**先に状態の持ち方を決める。**

TODO-056 で入れたブラウザのテストで、退行を捕まえられる。

詳しくは `docs/design-review.md` の I。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-079.** 表示の条件をまとめて `load_sched()` の引数を減らす](archives/todo/TODO-079.%20表示の条件をまとめて%20load_sched%20の引数を減らす.md)
- [**TODO-078.** ゲージの計算を 1 か所にする](archives/todo/TODO-078.%20ゲージの計算を%201%20か所にする.md)
- [**TODO-077.** `fix` で `.bak` が中間状態に上書きされるのを直す](archives/todo/TODO-077.%20fix%20で%20.bak%20が中間状態に上書きされるのを直す.md)
- [**TODO-076.** ゲージの綴りを `gage` から `gauge` に直す](archives/todo/TODO-076.%20ゲージの綴りを%20gage%20から%20gauge%20に直す.md)
- [**TODO-075.** 文書と実装のズレを直す](archives/todo/TODO-075.%20文書と実装のズレを直す.md)
- [**TODO-074.** ゲージをタップして、その週へジャンプできるようにする](archives/todo/TODO-074.%20ゲージをタップして、その週へジャンプできるようにする.md)
- [**TODO-073.** クレジット表示を「(c) 2026 ytani01」に統一する](archives/todo/TODO-073.%20クレジット表示を「(c)%202026%20ytani01」に統一する.md)
- [**TODO-072.** ゲージの針の上の相対日数の単位を調整する](archives/todo/TODO-072.%20ゲージの針の上の相対日数の単位を調整する.md)
- [**TODO-070.** 緑色の点滅と、予定追加のプラスアイコンを廃止](archives/todo/TODO-070.%20緑色の点滅と、予定追加のプラスアイコンを廃止.md)
- [**TODO-069.** 数ヶ月ぶんの週を DOM に持ち、週移動でページを読み直さない](archives/todo/TODO-069.%20数ヶ月ぶんの週を%20DOM%20に持ち、週移動でページを読み直さない.md)
- [**TODO-067.** フッターの入力欄とアイコンの縦位置を揃える](archives/todo/TODO-067.%20フッターの入力欄とアイコンの縦位置を揃える.md)
- [**TODO-066.** ヘッダーの期間表示をやめて、週の差を針と一緒に動かす](archives/todo/TODO-066.%20ヘッダーの期間表示をやめて、週の差を針と一緒に動かす.md)
- [**TODO-068.** 編集画面から週表示に戻ったとき、スピナーが表示されっぱなしになるのを修正](archives/todo/TODO-068.%20編集画面から週表示に戻ったとき、スピナーが表示されっぱなしになるのを修正.md)
- [**TODO-056.** JavaScript の退行を捕まえられるようにする](archives/todo/TODO-056.%20JavaScript%20の退行を捕まえられるようにする.md)
- [**TODO-065.** 編集画面に「戻る」ボタンを追加](archives/todo/TODO-065.%20編集画面に「戻る」ボタンを追加.md)
- [**TODO-062.** スワイプが、60px 動くまで指に追従しないのを直す](archives/todo/TODO-062.%20スワイプが、60px%20動くまで指に追従しないのを直す.md)
- [**TODO-063.** 週送りが、同じ週の月曜に止まるのを直す](archives/todo/TODO-063.%20週送りが、同じ週の月曜に止まるのを直す.md)
- [**TODO-051.** `DISPLAY` があると画面のキャプチャが撮れないのを直す（保留）](archives/todo/TODO-051.%20DISPLAY%20があると画面のキャプチャが撮れないのを直す（保留）.md)
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
