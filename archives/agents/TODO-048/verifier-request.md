# TODO-048 verifier への依頼

Font Awesome をやめて自作の SVG アイコンに差し替えた。**実装は
implementer が済ませ、`README.md` は main が直した。** その両方を確かめる。

- 実装の報告: `archives/agents/TODO-048/implementer-report.md`
- 依頼書: `archives/agents/TODO-048/implementer-request.md`（対応表がある）
- 変更は `git diff` と `git status` で見られる（`vendor/fontawesome/` は
  `git rm -r` 済みなので `git status` 側に出る）

**コードは直さないこと。** 見つけたことは報告して、直すかどうかは main が決める。

## 確かめること

1. **lint・型チェック・テスト。** `mise run lint` と
   `uv run pytest tests`。implementer は「427 件全部通過、
   落ちたものは無い」と報告している。同じ結果になるか
2. **アイコンが実際に画面へ出るか。** ここが今回いちばん大事。
   `<use href="…icons.svg?v=…#home">` という参照の形なので、**絵が
   出ていなくても HTML は正しく見える。** 必ず画面で見ること

   ```sh
   uv run ytsched webapp \
     --datadir /tmp/claude-649/-home-ytani-work-ytsched/a2bb2f43-efc3-49b3-b5f9-66676d2024ec/scratchpad/data \
     --port 10090
   ```

   URL は `http://localhost:10090/ytsched/`。**実データは触らないこと**

   - `/ytsched/static/icons/icons.svg` が 200 で返ること
   - 一覧・編集画面で、アイコンが**空白になっていない**こと。
     `page.evaluate()` で `<svg>` の `getBoundingClientRect()` を見る、
     キャプチャを見る、などで確かめる
3. **対応表どおりか。** 依頼書の表と `git diff` を突き合わせる。
   とくに **`arrow-alt-circle-up` の solid と regular**
   （`main.html` が `circle-up-fill`、`edit.html` が `circle-up`）が
   入れ替わっていないか。実際の絵でも見ること
4. **消し残しが無いか。**
   `grep -rn 'fa-\|fas \|far \|fontawesome' src/` で出るのは、
   ゲージの大きさの由来を書いた `fa-caret-right` / `fa-grip-lines` の
   コメント（`main.html` と `my.css`）だけのはず
5. **キャプチャの突き合わせ。** `~/tmp/playwright-mcp/` に
   `todo048-before-*`（変更前・main が撮った）と `todo048-impl-*`
   （変更後・implementer が撮った）がある。**字形は別物になるので画素の
   一致は見ない。** 見るのは、アイコンの**大きさ・縦位置・行の詰まり
   具合**が崩れていないか。**自分でも撮り直して**（`todo048-verify-*`
   という名前で）、implementer のものと同じになるか見ること

   ```sh
   env -u DISPLAY uv run --with playwright python tools/screenshot.py \
     'http://localhost:10090/ytsched/' -p todo048-verify --open
   ```

   `env -u DISPLAY` を付けるのはこの環境の癖（TODO-051）。
   **`todo048-before-*` と `todo048-impl-*` は消さないこと**
6. **`README.md` の「外部のライブラリ」の節**（main が書き直した）。
   書いてあることが実態と合っているか。とくに:
   - `static/vendor/` がもう無いこと
   - `icons.svg` の `<symbol>` が 23 個であること
   - `docs/licenses/bootstrap-LICENSE` が実在すること
7. **`uv build` で作った wheel の中身。** `vendor/` を消して
   `icons.svg` を足したので、パッケージに入るファイルが変わっている。
   `mise run build` して、wheel に `static/icons/icons.svg` が入り、
   `vendor/` が入っていないことを見る

## 報告

`archives/agents/TODO-048/verifier-report.md` に書く。**返事は 5 行以内**で、
終わったか・報告ファイルのパス・判断が要る点だけ。全文は貼らない。
