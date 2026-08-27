# TODO-084 writer への依頼

実装が終わった（implementer・verifier・reviewer とも決着）。文書を書く。

読むもの: `TODO.md` の TODO-084 の節、`git diff`、
[`request-implementer.md`](request-implementer.md)、
[`implementer-report.md`](implementer-report.md)、
[`verifier-report.md`](verifier-report.md)、
[`reviewer-report.md`](reviewer-report.md)。

## 1. `src/README.md`

- **`conf.json` の設定の説明。** `HandlerBase` の項に「**`LoadMonths` を
  除いて**、人が手で編集するファイルではない」とあるが、`AutoTurnMsec` も
  手で書く設定になった。**2 つになった**ことが分かるように直す。
- **`MainHandler` の項。** `LoadMonths` の説明の近くに `AutoTurnMsec`
  （既定 700、範囲 300〜10000）を足す。画面から変える UI は無く、
  アプリは読むだけ（`get_auto_turn_msec()`）なので手で書いた値は消えない、
  という点は `LoadMonths` と同じ。**設定を読むのは
  `get_conf_int()` に共通化した**ことにも触れる。
- **「週の移動（ブラウザ側）」の節。** フッターの ◀ ▶ の扱いが変わった。
  - ボタンは `onmousedown` を持たず、`data-page-turn="-1"` / `"1"` を
    持つだけ。`main-page.js` が `window` で `pointerdown` / `pointerup` を
    拾い、`closest()` で判定する（`swipe.js` の `mouseDownHdr()` と同じ形。
    `main-page.js` は `<header>` で読まれ、フッターのボタンより先に
    評価されるので、要素へ直に付けられない）
  - シングルタップは 1 週送る。ダブルタップ（350msec 以内）で
    `setInterval` の自動ページ送りが始まる
  - 止まるのは 4 つ: もう一度タップ、他の場所をタップ、キー操作、
    画面が隠れたとき。読み込んだ範囲の外へ出て `doGet()` に倒れたときも、
    ページごと読み直すので止まる
  - **ボタンの上から始めたスワイプ・ドラッグは、週送りとして拾わない。**
    `swipe.js` の `touchStartHdr()` / `mouseDownHdr()` が
    `[data-page-turn]` を見送り、`main-page.js` 側も 30px 以上動いていたら
    何もしない
  - `static/js/` は **8 本のまま**（新しいファイルは作っていない）。
    本数の記述を書き換えないこと
- Mermaid の図は、**いまの図（`moveToMonday()` の流れ）を変えない。**
  自動ページ送りは `moveToMonday()` を繰り返し呼ぶだけで、図の中身は
  変わらない。

## 2. `tests/README.md`

`test_browser.py` の説明に、TODO-084 で足した 3 本（ダブルタップで自動
ページ送りが始まる・次のタップで止まる・ボタンの上からの横払いでは週が
動かない）を 1〜2 行で足す。`test_web.py` 側の `AutoTurnMsec` のテストにも
触れてよい。

## 3. `archives/todo/TODO-084. フッターの ◀▶ をダブルタップして自動ページ送り.md`

`TODO.md` の TODO-084 の節を、決着した項目として 1 ファイルにまとめる。
骨格は「きっかけ / やったこと / テスト」。見出しの直後の表は、**見込みの
行をそのまま残し**、実施の行を足す（食い違ったまま両方残す）。

```
|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer + writer + wording |
| 消費 | （main が後で書く。行だけ置いておく） |
```

書くこと:

- **仕様を 2 度変えている。** 最初は「押しっぱなしのリピート＋マルチ
  タップを溜める」で、2026-08-28 にダブルタップでの自動ページ送りに
  書き換えた。**取りやめたほうの理由も残す**（`TODO.md` の
  「押しっぱなし（リピート）と、マルチタップを溜めておく扱いは
  取りやめた」）。旧仕様の作業は git の stash にあったが、コミット後に
  捨てた。**そこで分かったこと**は残す価値がある:
  - `slideWeekWrap()` は呼び出しが重なると前の回の `on_done()` を
    呼ばないので、間隔が短いと週が飛ぶ。`AUTO_TURN_MSEC_MIN` を 300 に
    したのはこれが理由
  - 滑っている最中に `swipe.js` の `cancelSwipeDrag()` が割り込むことが
    ある。今回はキューが無いので 1 回飛ぶだけで済む（reviewer の確認 2）
- 決めた仕様（キー名・既定値・範囲・止め方・ダブルタップと見なす間隔 350msec・
  30px の見送り）と、その理由
- 変えたファイルと、実装で判断した 2 点（`get_conf_int()` の
  クロージャ、`window` への委譲）
- テスト（`test_web.py` に 4 本、`test_browser.py` に 3 本、既存の連打
  テストに 400msec の待ちを入れたこと）と、verifier が確かめた範囲
- reviewer の確認結果（指摘なし。300msec の余裕の話は定数のコメントへ
  書き足した）
- `archives/agents/TODO-084/` への参照

## 4. `TODO.md`

- TODO-084 の節を消す
- 冒頭の「残っている項目」から TODO-084 を外し、「これまでに 85 件」を
  86 件に直す
- 「完了済み」の目次の先頭に TODO-084 を足す（新しい順）

## 前提

- **コード・テンプレート・テストは触らない。** `.md` だけ。
- 造語を作らない。このリポジトリで既に使われている語で書く
  （「週送り」「ダブルタップ」など）。

## 報告

`archives/agents/TODO-084/writer-report.md` に、直したファイルと、
判断が要った点を書く。返事は 5 行以内。
