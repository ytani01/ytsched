# TODO

**残っている項目: TODO-056,TODO-065,TODO-066,TODO-067,TODO-068。**
これまでに 63 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-069` から。**

着手する項目は利用者が指定する。

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

## TODO-065. 編集画面に「戻る」ボタンを追加

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ + verifier |

- [ ] 編集画面のフッターに「戻る」ボタンを足す
- [ ] 保存せずに週表示へ戻ることを確かめる

### やること

`src/ytsched/webroot/templates/edit.html` のフッター（`id="menu"`）に、
保存しないで週表示へ戻るボタンを足す。位置は左端。

- **アイコンは `#reply` を使う。** `icons.svg` の 23 個のうち、実際に
  使われていないのはこれだけだった（唯一の参照が下記のコメントの中）
- **`history.back()` は使わない。** 更新ボタン（`sync`）は保存したあと
  編集画面へリダイレクトして留まるので（`main_handler.py` の
  `exec_cmd()`、TODO-050）、更新を 2 回押していると `history.back()` は
  ひとつ前の編集画面へ戻ってしまう。`edit.html` には `url_prefix` と
  `date` が渡っているので、`{{ url_prefix }}?date={{ date }}` への
  直リンクにする
- 戻り先の日付は `orig_date`（行が実際に入っているファイルの日付）では
  なく **`date`（表示していた日付）** にする。押す前に見ていた週へ戻す
- **フッターの桁数を調整する。** いまは `col-2`(更新) + `col-2`(確定) +
  `col-2`(複製/空) + `col-4`(空き) + `col-2`(削除) で 12。左端に
  `col-2` を足す分、空きを `col-4` から `col-2` に縮める

### 決めたこと

- **未保存の変更があっても確認しない。** 押したらそのまま戻る
- **検索モード中に編集へ入った場合の戻り先は考えない。** 検索語は
  `conf.json` に残るので、週表示へ移っても検索モードのままになりうるが、
  この項目では触らない

### 経緯

`edit.html` には、同じものが最初からコメントアウトされたまま入っている
（`b54376e` の時点で既にあり、2021 年の Perl 版から持ってきたもの）。
`#reply` を使い、`onmousedown="history.back();"` になっている。
上のとおり `history.back()` は使えないので、そのまま外して有効にはしない。

### 確かめ方

- 編集画面から戻るボタンを押して、**編集内容が保存されずに**週表示へ
  戻ること
- 更新ボタンを 2 回押したあとに戻るボタンを押しても、編集画面ではなく
  週表示へ戻ること
- 確かめるときは `--datadir` に一時ディレクトリを指定する

---

## TODO-066. (ユーザーが追加)ヘッダー表示の変更

|      | main | 担当 |
|------|------|------|
| 見込み |  |  |

- ヘッダーの期間表示は廃止。
- 今週からの相対位置(-3w など)は、ゲージの針の上に表示して、針と一緒に動くようにする。
- 相対位置(-3w など)が今週の場合「±0」と表示する。

---

## TODO-067. (ユーザーが追加)フッターの表示が不揃いなのを修正

- フッターに表示される フォームの入力欄 や アイコンの縦位置をきれいに揃える。

---

## TODO-068. 編集画面から週表示に戻ったとき、スピナーが表示されっぱなしになるのを修正

- TODO-065 に入れられるなら、TODO-065で対応。

---


## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

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
