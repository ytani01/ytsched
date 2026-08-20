# TODO

**残っている項目: TODO-022・TODO-023。**
これまでに 21 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-024` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にある。既存データは
`ytsched migrate` で一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-022. 軽量な担当 runner を作る

見込み: main = Sonnet 5 / effort medium、担当 = main のみ

- [x] サブエージェントが `CLAUDE.md` を読めているかを確かめる
- [x] 共通の前提の置き場所を決める
- [x] `.claude/agents/runner.md` を作る（haiku）
- [x] TODO-021 で使ってみて、結果を TODO-021 の `実施:` に残す

（背景）

サブエージェントを軽くしたい。`effort` は定義ファイルでしか指定
できないので、モデルを落とすなら定義を分ける必要がある。狙いは
モデルの費用ではなく、**軽い担当には仕事の範囲も狭く書ける**こと。

（やること）

- **runner（haiku）** — `mise run lint` と `mise run test` を走らせて、
  結果をそのまま報告する。**異常の切り分けはしない**（それは verifier）。
  この線引きを定義に明記する
- **重複の解消** — 今の 4 つの定義には同じプロジェクト前提が書き写して
  あり、TODO-020 では同じ 5 行を 4 ファイルで書き換えた。5 つ目を足す前に
  置き場所を 1 つにする。ただし**サブエージェントが `CLAUDE.md` を
  読めているなら書き写し自体が要らない**ので、先に確かめる

（気をつけること）

- 定義を増やすのは 1 つだけ。`implementer` の軽い版は、当てになる項目が
  来てから決める
- **定義ファイルを置いたら Claude Code の再起動が要る**（利用者が行う）
- 効果の判定は TODO-021 で行う。足りなければ verifier に戻す

（確かめたこと）

**サブエージェントには `~/.claude/CLAUDE.md` と `ytsched/CLAUDE.md` の
両方が届いていた。** 起動した担当にツールを使わせずに、渡された文脈だけを
答えさせて確かめた。定義ファイルの本文も届いている（システムプロンプト
ではなく、最初のメッセージ本文として、CLAUDE.md より前に置かれている）。
プロジェクトの前提は、CLAUDE.md 側と定義の「このプロジェクト」節の
**2 か所で重複**していると、担当自身が指摘した。

これを受けて、**書き写しをやめた**。既存 4 定義から「このプロジェクト」節と
「シェルの注意」節を削り、CLAUDE.md に無かった 1 件（起動確認では
`--datadir` に一時ディレクトリ）を `CLAUDE.md` の「担当への共通の前提」へ
移した。

**runner が走らせるのは `mise run lint` / `mise run test` ではなく、
個別のコマンドにした。** `mise run test` は `lint` → `upgradeproject` に
依存していて、呼ぶたびに `rm -f uv.lock` → `uv sync` →
`uv pip install -U` まで走る。テストが壊れたときに、変更のせいか依存が
上がったせいかが分からなくなる。

（担当を分けない理由）

定義ファイルを 1 つ作るだけ。実際に動かして試すのは TODO-021 の中。

---

## TODO-023 mise.tomlの見直し

mise.tomlを使いやすいようにしたい。
現在の内容は、全部書き直してもいいし、不要なら削除してもいい。


---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

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
