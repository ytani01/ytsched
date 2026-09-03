# TODO-170 writer への依頼

## 目的

新しいサブコマンド `ytsched fix-id`（TODO-170）を文書に反映する。
実装は済んでいて、テストも通っている。**コードは触らない。**

- 仕様: `TODO.md` の TODO-170 の節
- 実装: `src/ytsched/fix_id.py`、`src/ytsched/__main__.py` の `fix-id`
- 実装の説明: `archives/agents/TODO-170/implementer-report.md` と
  `implementer-report-2.md`
- 実データでの実測値（verifier が確かめた）:
  `archives/agents/TODO-170/verifier-report.md`

## 直す文書

1. `docs/data-format.md`
   - `sde_id` の説明（キーと値の表。「移行で振り直さないので、両方が
     混ざる」と書いてある行）を、**`ytsched fix-id` で UUID へ
     振り直せる**ことが分かるように直す。旧形式から来た ID の形
     （13〜18 文字）の説明は、経緯として残してよい
   - 「`sde_id` は 13352 種類で、8 種類が重複していた」という調査結果の
     記述があるので、振り直せば一意になることに触れる
   - 開発者向けの文書なので `(TODO-170)` の番号参照を入れてよい
2. `docs/Install.md`
   - `ytsched migrate` / `ytsched holiday` の説明と同じ形で、
     `ytsched fix-id` の節を足す。**旧形式から移行した人向けの手順**
     として書く（`migrate` の直後あたりが自然）
   - **元に戻せないこと**、まず `--dry-run` で件数を確かめること、
     `.bak` を作らないので**事前にデータディレクトリごとコピーして
     おく**ことを書く
   - **利用者向けの文書なので TODO 番号は書かない**
3. `docs/Developer.md`
   - `ytsched migrate` / `ytsched holiday` のコマンド例が並んでいる
     ところに `ytsched fix-id` を足す
4. `src/README.md`
   - ソースの構成一覧（`migrate.py` の行がある表）に `fix_id.py` を足す。
     既存の書き方に揃える

## 書くときの注意

- 既存の節の書き方・語彙にそのまま揃える。新しい言い回しを作らない
- コマンドの動きを実物と食い違わせない。迷ったら
  `src/ytsched/fix_id.py` と `uv run ytsched fix-id --help` を見る
- 実行例の出力を載せるなら、verifier の報告にある実測値を使う

## やらないこと

- **コードは触らない**（`src/ytsched/*.py`、`tests/`）
- `TODO.md`・`archives/` は main が書く。触らない
- `README.md`（リポジトリ直下）は、`migrate` に触れている 92 行目が
  あるが、**今回は触らなくてよい**（`fix-id` は移行後の後始末なので、
  トップの README に足す必要は無いと main が判断した）

## 報告

`archives/agents/TODO-170/writer-report.md` に書く。返事は 5 行以内。
