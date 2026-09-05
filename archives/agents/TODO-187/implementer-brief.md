# TODO-187 implementer への依頼

## 目的

ゲージ（スライダー）を、いまのヘッダー（`#week_bar`）に加えて、
**フッター（メニューバー）の直上にも同じものを出す**。
指はフッター側にあるので、下でも同じ操作ができるようにする。

`TODO.md` の「TODO-187」の節を必ず読むこと。

## 対象範囲

- `src/ytsched/webroot/templates/main.html`
- `src/ytsched/webroot/static/js/gauge.js`
- `src/ytsched/webroot/static/js/main-page.js`
- `src/ytsched/webroot/static/js/state.js`
- `src/ytsched/webroot/static/css/my.css`
- `tests/test_browser.py`

## やること

1. **`main.html` に 2 つ目のゲージ**をフッターの直上に出す。中身は上と
   全く同じ（`.my-gauge-bar` / `.my-gauge-axis` / `.my-gauge-base` /
   `.my-gauge-r` + `.my-gauge-r-label` + `.my-gauge-r-needle`）。
   検索モードでは出さない（上と同じ `{% if not search_mode %}` の条件）。
   外側は `.my-week-bar` と同じ役割の入れ物を新しいクラスで用意する
   （背景色 `#48C`・`padding: .25rem`）。

2. **id をやめる。** `#gauge_r` / `#gauge_r_label` の id を落とし、
   `.my-gauge-r` / `.my-gauge-r-label` で引く形に統一する。

3. **`gauge.js` を、ゲージが複数ある前提へ直す。**
   - `dispGaugeMarks()` は `.my-gauge-bar` 全部に目盛りを描く
   - 針の位置・ラベルの文字・`my-gauge-r-no-transition` の付け外しは、
     `.my-gauge-r` 全部に反映する（上下が必ず同じ位置・同じラベルになる）
   - `placeGaugeWithoutTransition()` のレイアウト確定
     （`getBoundingClientRect()`）も全部に対して行う
   - `state.js` の `ytState.elGaugeR0` は複数を持てないので、
     配列を持つ形（例: `elGaugeRs`）へ直す。「検索モードでゲージが無い」
     の判定は、いまの `null` チェックの代わりに**空かどうか**で見る。
     参照している `main-page.js` のコメントも直す

4. **`mondayFromClientX()` は、pointerdown で触れた帯の矩形を使う。**
   いまは `document.querySelector(".my-gauge-bar")`（＝常に上の帯）を
   見ているので、下の帯をドラッグすると位置が合わない。
   `gaugeBarDragStart` に、`closest(".my-gauge-bar")` で得た要素を持たせ、
   pointermove / pointerup でもそれを使う。

5. **`my.css` に下のゲージ用のクラス**を足す（`position: fixed` /
   `z-index: 50` / 左右 0 / 背景色）。`bottom` は JavaScript が入れる。
   メニューを開くと `.my-bar-content`（`z-index: 100`）がせり上がって
   下のゲージを隠す、という前提（TODO.md 参照）。

6. **`main-page.js` の `onloadHdr()`** で、下のゲージの `bottom` を
   メニューバー（`#menu_bar`）の高さに合わせ、`body` の `paddingBottom`
   を「メニューバーの高さ ＋ 下のゲージの高さ」にする。
   位置合わせは読み込み時に一度だけでよい（閉じたメニューバーの高さは
   変わらない）。**`body_h` / `win_h` を測るより先に**入れること
   （既存の `paddingTop` と同じ理由）。

7. **`tests/test_browser.py`**
   - 既存の `#gauge_r` / `#gauge_r_label` 参照（14 箇所ほど）を
     クラス指定へ直す。要素が 2 つになるので、Playwright の locator は
     `.first` を使うなどして strict mode 違反を出さないこと
   - 足すテスト（3 つ）:
     - 上下のゲージの針が同じ位置（`style.left`）になること
     - 上下のラベルが同じ文字になること
     - **下のゲージをドラッグしても週が移ること**
       （既存の `test_gauge_drag_*` の書き方に倣う）

## 前提・注意

- 上下が同時に操作されたときのことは考えない
- `~/.claude/CLAUDE.md`・`CLAUDE.md`（プロジェクト）の決まりに従う
- コメントは既存の書き方（`(TODO-187)` の付け方）に揃える
- アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する
- `mise run upgradeproject` は走らせない。
  `mise run fmt` / `lint` / `typecheck` / `test` は叩いてよい
- 最低限、`npx prettier` 相当の整形（`mise run fmt`）と
  `mise run lint` を通してから終えること

## 完了条件

上の 1〜7 が済み、`mise run lint` が通り、
`tests/test_browser.py` のゲージ関連テストが通ること。

## 報告

`archives/agents/TODO-187/implementer-report.md` に、
**変更点・検証結果・残る懸念**だけを書く。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。
