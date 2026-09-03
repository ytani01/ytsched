# TODO-170 writer 報告

## 直したファイル

- `docs/data-format.md`
  - `sde_id` の行に、`ytsched fix-id` で UUID でないものだけを
    振り直せることを追記（TODO-170 を参照）。旧形式の ID の形
    （13〜18 文字）の説明はそのまま残した
  - 「13352 種類・8 種類が重複」の記述の後ろに、`fix-id` で振り直せば
    一意になる旨を追記
- `docs/Install.md`
  - 「7. 旧形式からの移行」の直後に「8. `sde_id` を UUID に揃える」を
    新設。`migrate`/`holiday` の節と同じ形（説明 → コマンド例）で書き、
    元に戻せないこと、まず `--dry-run` で件数を確かめること、
    `.bak` を作らないので事前にデータディレクトリごとコピーしておくこと
    （`cp -a` の例）を書いた。TODO 番号は書いていない
- `docs/Developer.md`
  - `ytsched migrate` の例のすぐ後ろに `ytsched fix-id` の説明と
    コマンド例（`--dry-run` → 本番）を追加（TODO-170 を参照）
- `src/README.md`
  - モジュール一覧の `migrate.py` の行の下に `fix_id.py` の行を追加
    （TODO-170 を参照）

## 確かめたこと

- `TODO.md` の TODO-170 の節、`archives/agents/TODO-170/` の
  implementer-report.md・implementer-report-2.md・verifier-report.md を
  読んだ
- `src/ytsched/fix_id.py`（docstring・`main()` の出力文言・
  `is_empty_line` の扱いなど）を読んだ
- `src/ytsched/__main__.py` の `fix-id` サブコマンド定義（オプション・
  help 文言）を読んだ
- `uv run ytsched fix-id --help` を実際に実行し、オプション
  （`--datadir`/`--data`、`--dry-run`、共通オプション）が文書と
  食い違わないことを確認した
- `docs/Install.md`・`docs/Developer.md` の既存の `migrate`/`holiday`
  節の書き方（見出し番号、コマンド例の並べ方、文体）を読んで揃えた
- 4 ファイルの `git diff` で差分を目視確認した

## コードは触っていない

`src/ytsched/*.py`・`tests/` は読んだのみで変更していない。
`TODO.md`・`archives/` も編集していない。

## 判断が要る点

なし。依頼書の指示どおりに書いた。
