# TODO

**残っている項目: TODO-044。**
これまでに 43 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-045` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にある。既存データは
`ytsched migrate` で一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-044. トークン消費の測り方と、担当の走らせ方を見直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + reviewer + wording |

- [ ] `tools/token-usage.py` の集計を直す
- [ ] 消費の行に概算料金を足す（`~/.claude/CLAUDE.md`）
- [ ] `.claude/agents/verifier.md` を絞る
- [ ] `.claude/agents/implementer.md` に読み方を足す

（背景）

アーカイブ済み 13 件の消費の行を transcript から取り直したところ、**消費の行が
測っているものと、実際に多く使っているものがずれていた。**

料金で見ると `cache_read` が 6〜7 割を占める（TODO-038 で 72%、TODO-042 で
59%、TODO-043 で 67%）。`cache_read` は「リクエスト数 × そのときのコンテキスト
長」で決まる。TODO-038 の implementer は 244 リクエストで 1 回あたり平均
222,000 トークン、verifier は 320 リクエストで平均 99,000 だった。

**担当ごとの割合も、消費の行と料金で食い違う。** TODO-038 の reviewer は消費の行
では 6%、料金では 1%。wording は 5% に対して 1%。担当を減らす方向では減らず、
減るのは 1 担当あたりのリクエスト数とコンテキストを絞ったとき。

集計そのものにも取りこぼしがある。サブエージェントの transcript には同じ
リクエストの usage が途中経過と最終値の両方で記録されていて、`collect()` は
先に出会った行（途中経過）を採っている。TODO-043 の verifier は記録上
output 654 だが、実際の出力は文字数から見て 2,800 トークン相当。
`cache_creation` 193,102 に対しては誤差だが、直しておく。

キャッシュの取り直しも起きている。TODO-043 の verifier は最後の 1 リクエストで
`cache_read` が 99,328 から 7,767 に落ち、92,116 を丸ごと書き直した（その担当の
`cache_creation` の 48%）。TODO-038 では 7 回で 405,794（32%）。コンテキストを
大きくしないことが、ここにも効く。

（決めたこと）

- 消費の行は `output` / `cache_creation` に**概算料金**を足す形にし、担当ごとの
  割合は料金で出す。形式はこう:

  ```
  | 消費 | output 33,589 / cache_creation 295,598 / 概算 $5.3 |
  |      | main 71% + verifier 25% + wording 3%（料金の割合） |
  ```

- 単価は `tools/token-usage.py` に持つ。cache write は入力の 1.25 倍、
  cache read は 0.1 倍で概算する。**Sonnet 5 の $2 / $10 は 2026-08-31 まで
  の価格**なので、そのあと書き換えが要る
- `CLAUDE.md` に測った結果そのものを残すのは、この項目ではやらない

（やらないこと）

- **担当のモデルを下げる案は入れない。** すでに全部 Sonnet か Haiku で、
  下げてもトークン数は変わらず単価しか動かない（wording を Haiku にしても
  $0.14 が $0.07 になる程度）
- **main の effort を見込みどおりから始める**のは、運用で気をつける話であって
  ファイルを変える話ではないので、やることに入れない。TODO-042・043 はどちらも見込み
  medium で立てて high で実施しており、main の output は TODO-042 で料金の
  18% を占めた

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

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
