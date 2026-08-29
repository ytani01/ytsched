# TODO-107 計画確認（verifier）

## 結果

- × `window.ytsched` を採る方針自体は妥当だが、ES Modules を見送る理由と
  TODO-108 との境界の説明は正確でない。ES Module から
  `window.ytsched` へ公開すれば、インラインイベントハンドラとの併用は可能で、
  TODO-108 は技術上の必須前提ではない。また、イベント委譲後は
  テンプレート用関数を非公開にできるため、「名前空間の構成は変えない」も
  将来の実装を過度に制約する。例えば「ES Modules への移行まで含めると変更が
  大きくなるため、この項目では素の `<script>` を維持する。インラインイベント
  ハンドラの廃止は TODO-108 で扱う」とし、TODO-108 で名前空間を維持すると
  断定しないのが適切。
- ○ テンプレート由来の値は `base.html` の `url_prefix` と `main.html` の
  `search_str0` / `today_str` / `auto_turn_msec` の4つで一致した。
- ○ 関数を呼ぶインラインイベントハンドラがあるテンプレートは
  `main.html` / `edit.html` / `sde.html` の3つで一致した。
- × 「各ファイル内だけで使う名前は外へ出さない」と
  `page.evaluate()` を名前空間経由へ直す項目の関係が曖昧。
  テストが直接参照する名前は `pushDateInUrl` / `gaugeDiffLabel` /
  `days2xPercent` / `xPercent2days` / `DAYS_YEAR` の5つで、後ろ4つは現在の
  `gauge.js` のコメントではファイル内だけで使う名前とされている。
  これらをテスト用にも公開する方針なら5つを明記するか、内部名を公開しない
  方針なら表示結果・操作によるテストへ直す必要がある。
- △ 暗黙のグローバルは `nav.js` の `d1_str` / `data_obj` と
  `week.js` の `d1_str` で一致した。不要な引数は `nav.js` だけでなく、
  `edit-page.js` の `onloadEdit(event)`、`main-page.js` の
  `homeButtonHdr(event)`、`nav.js` の `popstateHdr(event)` にある。
  「暗黙のグローバル変数や、複数ファイルの不要な引数を含む指摘」とすると
  範囲が明確になる。
- ○ 各 JavaScript 先頭には公開名・依存先のコメントがあり、
  `src/README.md` にも現在のグローバル公開と値の渡し方が書かれているため、
  両方を更新対象にするのは妥当。
- ○ `page.evaluate()` の対象説明は上記の公開方針を決めれば十分。
  一覧・編集の両画面で `pageerror` を捕捉する確認も必要十分。ただし現在の
  `page` fixture は自動収集せず、既存の収集は一覧の検索テスト1件だけなので、
  実装時にはリスナーを付けて両画面を実際に開く必要がある。
- ○ `git diff --check` は終了コード0、出力なし。

## 実行したコマンド

- `rg -n -C 3 "TODO-107|TODO-108" TODO.md`
- `git diff -- TODO.md`
- `rg -n "\\bon[a-zA-Z]+\\s*=" src/ytsched/webroot/templates`
- `npx eslint src/ytsched/webroot/static/js --rule 'no-undef:error' --rule 'no-unused-vars:error'`
  （現行設定を上書きして170件を検出し、上記の実体を確認）
- `rg -n "page\\.evaluate" tests/test_browser.py`
- `rg -n -C 4 "pageerror" tests/test_browser.py`
- `git diff --check`

## 修正後の再確認

- ○ ES Modules を見送る理由は変更規模に基づく説明へ直り、TODO-108 は
  インラインイベントハンドラの廃止だけを扱う境界になった。前回の × は解消。
- ○ `page.evaluate()` が直接使う5種類を列挙し、テストから使う名前も
  `window.ytsched` へ公開する方針が明記された。前回の × は解消。
- ○ 暗黙のグローバル変数と、複数ファイルにある不要な引数を分けて記述した。
  前回の △ は解消。
- ○ 一覧・編集の両画面で `pageerror` を収集するブラウザテストの追加が
  明記され、確認方法の曖昧さも解消。
- ○ 再実行した `git diff --check` は終了コード0、出力なし。
