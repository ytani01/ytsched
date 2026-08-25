# TODO-048 verifier への追加の依頼: 行の高さの直し

最初の確認のあと、**main が計測して 1 つ崩れを見つけた**ので、直した。
その直しを確かめてほしい。**コードは直さないこと。**

## 何が崩れていたか

詳細（detail）のある予定の行が、**44.00px → 50.25px** に太っていた。

原因は、開閉スイッチ（`sde.html` の `.my-sde-detail-sw` の中の
`<label class="m-1">`）。Font Awesome の `.fa-lg` は
`line-height: .05em` を持っていて、**`<i>` 自体の高さがほぼ 0 に
なっていた**（実測で 0.81px）。字面はその枠からはみ出して描かれるので、
行の高さには響かない。
SVG は 16.25px の箱をそのまま占めるので、`label` の余白 `m-1`（4px）が
効いてしまい、行が 6.25px 高くなった。

キャプチャを目で見比べただけでは気づけない差だったので、
`getBoundingClientRect()` で数えて見つけた。

## 直し方

- `sde.html`: `<label class="m-1" for="{{ sw_id }}">` の `m-1` を外した
- `my.css`: `.my-sde-detail-sw label { margin: 1px; }` を足した
  （`.my-sde-detail-sw` の直後。コメント付き）

これで **44.25px** になり、変更前の 44.00px とほぼ同じに戻った。

## そのほか、最初の確認のあとに変わったもの

- `tools/icons_preview.py` が `mise run lint` で整形された。
  **これは戻さずに残した。** `mise run fmt` は `--line-length 78` で走るが、
  前のコミットではそれを通していなかった。今回の直しの一部として入れる

## 確かめてほしいこと

1. **行の高さが戻っているか。** 変更前と直したあとを、**目ではなく数字で**
   突き合わせる。`page.evaluate()` で `.my-sde` の
   `getBoundingClientRect().height` を並べて比べること

   変更前の状態は、HEAD の webroot を取り出して `--webroot` で
   指せば動かせる（main はこの形で比べた）:

   ```sh
   mkdir -p /tmp/oldroot && git archive HEAD src/ytsched/webroot | tar -x -C /tmp/oldroot
   uv run ytsched webapp --datadir <一時dir> \
     --webroot /tmp/oldroot/src/ytsched/webroot --port 10093   # 変更前
   uv run ytsched webapp --datadir <一時dir> --port 10094       # 直したあと
   ```

   **`--datadir` は自分で用意した一時ディレクトリにすること。**
   main が使っている
   `/tmp/claude-649/…/a2bb2f43-…/scratchpad/data` は共用で、
   `conf.json` に検索文字列が保存されるため、検索を試すと相手の画面が
   変わってしまう（実際に起きた）
2. **他の行の高さが変わっていないか。** 詳細の無い行（21.5 / 23 / 26px）が
   そのままか
3. **開閉スイッチが今までどおり押せるか。** `label` の余白を削ったので、
   押せる範囲が狭くなっていないか。押す範囲は親の `.my-btn`（`.col-1`）の
   はずだが、実際に押して詳細が開くことを確かめること
4. `mise run lint` と `uv run pytest tests`（main の手元では lint 通過・
   427 件通過）
5. キャプチャを撮り直して、崩れが無いこと（`todo048-verify2-*`）

## 報告

`archives/agents/TODO-048/verifier-report-2.md` に書く。**返事は 5 行以内。**
