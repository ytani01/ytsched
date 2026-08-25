# TODO-048 verifier 報告

## 1. lint・型チェック・テスト

- `mise run lint`: ○（`ruff format` が `tools/icons_preview.py` を
  自動整形したが、TODO-048 と無関係な既存のずれなので `git checkout --`
  で戻した。今回の作業のせいで壊れているわけではない）
- `uv run pytest tests`: ○ **427 件全部通過**（implementer の報告と同じ）
- `mise run build`（`test` を経由）でも同じ整形ずれが再度出たので、
  もう一度 `git checkout --` で戻した

## 2. アイコンが実際に画面へ出るか

- `GET /ytsched/static/icons/icons.svg` → **200**
- `<symbol id="...">` の数 → **23**
- 一覧画面（`main_open`）・メニュー開（`menu_open`）・編集画面（既存・新規）・
  検索バー（`?search_str=報告`）・読み込み中のしるし（`#loadingSpinner` を
  `page.evaluate()` で強制表示）を実際にキャプチャして目で確認。
  **どこも空白になっていない。** アイコンが絵として出ている
  （チェックボックスの四角、開閉の山形、ホーム・虫眼鏡・ハンバーガー・
  前後の矢印、編集画面上部の丸矢印 3 つ、下部の同期・チェック・複製・
  ゴミ箱、検索バーの虫眼鏡＋上向き丸、読み込み中の回転する円弧）

## 3. 対応表どおりか

- `git diff` と依頼書の対応表を突き合わせ、一致を確認
- **`arrow-alt-circle-up` の入れ替わりなし。** `main.html:197` は
  `#circle-up-fill`（検索バーの塗りつぶし丸）、`edit.html:213` は
  `#circle-up`（編集画面上部、輪郭だけの丸）。実際の絵でも
  塗りと輪郭で見分けがつくことを確認

## 4. 消し残し

`grep -rn 'fa-\|fas \|far \|fontawesome' src/` → `main.html:158` と
`my.css:470-471` の `fa-caret-right` / `fa-grip-lines` コメント（ゲージの
由来、依頼どおり残すもの）だけ。それ以外の消し残しなし。

## 5. キャプチャの突き合わせ

`todo048-verify-*` を撮り直した（main / menu / edit / editnew / search /
spinner、412px・800px）。`todo048-before-*` → `todo048-impl-*` →
`todo048-verify-*` で、画面サイズ・行の詰まり具合・アイコンの縦位置に
崩れなし（`todo048-impl-*` と `todo048-verify-*` は同じ実装なので、
サイズは完全一致。412x900 で確認）。`todo048-before-*` / `todo048-impl-*`
は消していない。

## 6. README.md の「外部のライブラリ」節

- `static/vendor/` は実際に存在しない（○）
- `icons.svg` の `<symbol>` は 23 個（○、上記と一致）
- `docs/licenses/bootstrap-LICENSE` は実在する（○）
- 記述と実態は合っている

## 7. `uv build` の wheel

`mise run build` → `dist/ytsched-0.3.5.dev0+gba1d735f9.d20260825-py3-none-any.whl`
の中身を `unzip -l` で確認。`static/icons/icons.svg` が入っており、
`vendor/` は入っていない。

## その他

- 起動確認は `--datadir` を一時ディレクトリに向けて実施。実データは
  触っていない。使ったサーバは終了後に PID を確認して kill 済み
- implementer 報告の「気づいたが直さなかったもの」（README の記載）は
  main が既に直している。「迷ったところ」（`edit.html` のコメントアウト
  戻るボタンを書き換えたこと）は妥当と判断（消し残しチェックに引っかから
  ないようにする以上の意図は無く、描画にも影響しない）

## 判断が要る点

なし。指摘事項も無し。
