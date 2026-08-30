# TODO

**残っている項目: TODO-118**
これまでに 122 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-123` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-118. データ形式をObsidianが読みやすい形式に変更することを検討(実装はまだ)

現在は、jsonl形式でデータを保存しているが、
Obsidianで扱いやすい MD形式に変更することを検討したい。

- 1件1ファイルになるので、データのディレクトリ構成も変更する必要がある。
- 日付、時刻、タイプなどは、Obsidianのプロパティ(yamlフロントマター)にする。
- アプリの挙動は一切変えない。

この案が現実的かどうか、評価報告書を docs/ の下に保存して。
もし、どうしても挙動が変わってしまう部分がある場合は、それも列挙して。

---

## TODO-123. 検索画面のフッターをダブルタップして自動ページ送り

|      | main | 担当 |
|------|------|------|
| 見込み | GPT-5 / effort medium | implementer + verifier |

- [ ] 検索画面のフッターの ＜ ＞ をダブルタップすると、検索の基準日を
  1 週間ずつ自動で移動する
- [ ] 画面を読み直しても自動送りを続け、画面上の別の場所または同じボタンを
  押すと止める
- [ ] 検索画面の移動では週枠のアニメーションを出さない
- [ ] 週表示と同じページ送り間隔を使う
- [ ] ブラウザテストで前後の自動送りと停止を確認する

検索画面は 1 回移動するごとに画面を読み直すため、週表示のタイマーだけでは
自動送りを続けられない。読み直し後にも必要な状態だけを引き継ぐ。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-122.** ゴミ箱への入口と戻る操作を整理する](archives/todo/TODO-122.%20ゴミ箱への入口と戻る操作を整理する.md)
- [**TODO-121.** ゴミ箱の画面とアイコンを全体のデザインに揃える](archives/todo/TODO-121.%20ゴミ箱の画面とアイコンを全体のデザインに揃える.md)
- [**TODO-120.** 詳細欄を押しただけで更新されるのを直す](archives/todo/TODO-120.%20詳細欄を押しただけで更新されるのを直す.md)
- [**TODO-119.** フッターの日付入力欄を削除する](archives/todo/TODO-119.%20フッターの日付入力欄を削除する.md)
- [**TODO-086.** ゴミ箱について UI 追加](archives/todo/TODO-086.%20ゴミ箱について%20UI%20追加.md)
- [**TODO-085.** ゴミ箱の導入](archives/todo/TODO-085.%20ゴミ箱の導入.md)
- [**TODO-071.** 検索の検索期間の扱いを変更（対応しない）](archives/todo/TODO-071.%20検索の検索期間の扱いを変更（対応しない）.md)
- [**TODO-117.** 検索画面のキーボードとスワイプも、基準日を 1 週間ぶん動かす](archives/todo/TODO-117.%20検索画面のキーボードとスワイプも基準日を%201%20週間ぶん動かす.md)
- [**TODO-116.** 検索画面の ＜ ＞ で、検索の基準日が月曜に丸められるのを直す](archives/todo/TODO-116.%20検索画面の%20＜%20＞%20で検索の基準日が月曜に丸められるのを直す.md)
- [**TODO-115.** implementer の effort を medium に下げる](archives/todo/TODO-115.%20implementer%20の%20effort%20を%20medium%20に下げる.md)
- [**TODO-106.** MainHandler の引数解析とビューモデル構築の分離](archives/todo/TODO-106.%20MainHandlerの引数解析とビューモデル構築の分離.md)
- [**TODO-108.** HTML テンプレートのインラインイベントハンドラをイベント委譲へ移行](archives/todo/TODO-108.%20HTML%20テンプレートのインラインイベントハンドラをイベント委譲へ移行.md)
- [**TODO-112.** 自動ページ送りテストが実行タイミングによって失敗するのを直す](archives/todo/TODO-112.%20自動ページ送りテストが実行タイミングによって失敗するのを直す.md)
- [**TODO-113.** TODO の作業で品質を保ちながらトークンを減らす](archives/todo/TODO-113.%20TODO%20の作業で品質を保ちながらトークンを減らす.md)
- [**TODO-114.** 検索画面の操作説明を利用者向けに書く](archives/todo/TODO-114.%20検索画面の操作説明を利用者向けに書く.md)
- [**TODO-107.** JavaScript のグローバルスコープ整理と ESLint ルール有効化](archives/todo/TODO-107.%20JavaScript%20のグローバルスコープ整理と%20ESLint%20ルール有効化.md)
- [**TODO-111.** フッターの日付が週切り替えに連動しないのを直す](archives/todo/TODO-111.%20フッターの日付が週切り替えに連動しないのを直す.md)
- [**TODO-110.** フッターの日付表示が週の表示と連動するようにする](archives/todo/TODO-110.%20フッターの日付表示が週の表示と連動するようにする.md)
- [**TODO-109.** ヘッダーのゲージの下に日付入力欄を常時表示する](archives/todo/TODO-109.%20ヘッダーのゲージの下に日付入力欄を常時表示する.md)
- [**TODO-105.** ホームボタンで今週の月曜日へ移動する](archives/todo/TODO-105.%20ホームボタンで今週の月曜日へ移動する.md)
- [**TODO-104.** 月間ミニカレンダーの表示を切り替えるスイッチ](archives/todo/TODO-104.%20月間ミニカレンダーの表示を切り替えるスイッチ.md)
- [**TODO-103.** 月間ミニカレンダー](archives/todo/TODO-103.%20月間ミニカレンダー.md)
- [**TODO-102.** 週間表示のフッタのアイコンを入力欄の高さに揃える](archives/todo/TODO-102.%20週間表示のフッタのアイコンを入力欄の高さに揃える.md)
- [**TODO-101.** 編集画面フッターのボタンをセンタリングする](archives/todo/TODO-101.%20編集画面フッターのボタンをセンタリングする.md)
- [**TODO-100.** `os.path` を `pathlib` へ移す](archives/todo/TODO-100.%20os.path%20を%20pathlib%20へ移す.md)
- [**TODO-095.** ruff の規則を増やすか決める](archives/todo/TODO-095.%20ruff%20の規則を増やすか決める.md)
- [**TODO-094.** 細かいもの](archives/todo/TODO-094.%20細かいもの.md)
- [**TODO-093.** 表示中の週の月曜日の日付を DOM から `ytState` へ移す](archives/todo/TODO-093.%20表示中の週の月曜日の日付を%20DOM%20から%20ytState%20へ移す.md)
- [**TODO-099.** JavaScript の整形ツール（Prettier）を導入する](archives/todo/TODO-099.%20JavaScript%20の整形ツール（Prettier）を導入する.md)
- [**TODO-098.** JavaScript のリンター（ESLint）を導入する](archives/todo/TODO-098.%20JavaScript%20のリンター（ESLint）を導入する.md)
- [**TODO-097.** `.js` の呼び出し関係をファイル先頭のコメントに書く](archives/todo/TODO-097.%20.js%20の呼び出し関係をファイル先頭のコメントに書く.md)
- [**TODO-090.** 依存の渡し方と、キャッシュ・`conf.json` の扱いを揃える](archives/todo/TODO-090.%20依存の渡し方と、キャッシュ・conf.json%20の扱いを揃える.md)
- [**TODO-092.** テンプレートの掃除](archives/todo/TODO-092.%20テンプレートの掃除.md)
- [**TODO-091.** `SchedData` の渡し方と、表示に渡す値の dataclass 化](archives/todo/TODO-091.%20SchedData%20の渡し方と、表示に渡す値の%20dataclass%20化.md)
- [**TODO-089.** `edit.html` の JavaScript を `edit-page.js` へ出す](archives/todo/TODO-089.%20edit.html%20の%20JavaScript%20を%20edit-page.js%20へ出す.md)
- [**TODO-096.** Android の Firefox でアイコンが黒く塗りつぶされる](archives/todo/TODO-096.%20Android%20の%20Firefox%20でアイコンが黒く塗りつぶされる.md)
- [**TODO-084.** フッターの ◀▶ をダブルタップして自動ページ送り](archives/todo/TODO-084.%20フッターの%20◀▶%20をダブルタップして自動ページ送り.md)
- [**TODO-088.** 一覧の組み立てと検索を分ける](archives/todo/TODO-088.%20一覧の組み立てと検索を分ける.md)
- [**TODO-087.** 更新の実行を `MainHandler` から出す](archives/todo/TODO-087.%20更新の実行を%20MainHandler%20から出す.md)
- [**TODO-083.** `my.js` と `main.html` の JavaScript を分ける](archives/todo/TODO-083.%20my.js%20と%20main.html%20の%20JavaScript%20を分ける.md)
- [**TODO-082.** import の意図と実態のズレ、未使用の属性、定数の置き場所を片付ける](archives/todo/TODO-082.%20import%20の意図と実態のズレ、未使用の属性、定数の置き場所を片付ける.md)
- [**TODO-081.** ハンドラの役割と、依存の渡し方を整理する](archives/todo/TODO-081.%20ハンドラの役割と、依存の渡し方を整理する.md)
- [**TODO-080.** キャッシュがファイルの更新に追随しないのを直す](archives/todo/TODO-080.%20キャッシュがファイルの更新に追随しないのを直す.md)
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
