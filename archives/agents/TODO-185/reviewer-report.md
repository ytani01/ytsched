# TODO-185 reviewer 報告

対象: `git diff`（未コミット）と `archives/agents/TODO-185/implementer-report.md`。
コードは直していない。

## 確信度の高い指摘

### 1. `tests/test_browser.py:1986` のドラッグテストの余裕が 800ms → 300ms に縮む

`test_gauge_drag_does_not_move_screen_while_dragging` は、暗黙に
「追従タイマーが 1 秒」であることに寄りかかっている。

```
page.mouse.down()          # ここで 500ms のタイマーが張られる
page.wait_for_timeout(200)
page.mouse.move(end_x, y)  # pointermove でタイマーが張り直される（+500ms）
page.wait_for_timeout(200)
assert _date_in_url(page) == monday.strftime("%Y-%m-%d")  # 追従していないこと
```

タイマーが発火するのは最後の `mouse.move` から 500ms 後。assert が走るのは
その 200ms 後 + `_date_in_url()` の往復。**余裕は 300ms しかない**
（既定 1000ms のときは 800ms あった）。負荷が高いときに
`wait_for_timeout(200)` が伸びる、あるいは Playwright の往復が延びると、
assert の前に追従が起きて URL が変わり、このテストが落ちる。

同じ理由で `test_gauge_drag_needle_does_not_jump_back_on_release`
（2158 行）も、`mouse.move` → `wait_for_timeout(200)` →
MutationObserver を仕込む `page.evaluate()` → `mouse.up()` の間が
500ms を超えると、離す前に追従が走る。こちらは observer を張ったあとの
`left` の変化が 50% を経由しないので落ちないと見ているが、
挙動が不定になる点は同じ。

このリポジトリは Raspberry Pi 上で、TODO-181 でも同種の
タイミングテストが負荷で落ちている。**判断が要る点**として、
少なくとも 1986 行のテストには `write_conf(tmp_path / "data",
{"GaugeFollowMsec": "3000"})`（`AutoTurnMsec` を `"300"` に固定して
いる 293 行と同じやり方）で待ち時間を固定しておくのが確実。

### 2. 「1 秒」と書いた場所が 1 か所残っている（`month.js:62`）

```
src/ytsched/webroot/static/js/month.js:62
   * (TODO-178)。ゲージドラッグの 1 秒後の追従判定に使う。
```

`hasBlockOfDate()` は `gaugeBarDragWeekIsLoaded()` から呼ばれる、
まさにこの追従判定の部品。TODO-185 の「『1 秒』と書いてあるコメントを、
値に依らない書き方へ直す」の対象に入るはずだが、implementer は
`gauge.js` の 5 か所だけを直している。

### 3. ブラウザテストのテスト名・docstring・コメントも「1 秒」のまま

- `tests/test_browser.py:2038` `def test_gauge_drag_follows_after_1_second_stop(...)`
- 2039 行 docstring「ゲージドラッグで 1 秒止まると」
- 2058 行「# 1 秒以上止まったら、追従が起きる」
- 2066 行「timeout=3000,  # 1 秒タイマー + スクロール処理の時間」
- 2083 行「# ドラッグして 1 秒後の追従を起こす」

既定が 500 になった以上、いずれも実態と食い違う。テストは
`timeout=3000` なので通り続けるが、名前が仕様と違う状態が残る。
指摘 1 で待ち時間を conf で固定するなら、その値に合わせて書き直すのが
自然。

## 見て問題が無かったところ

- **`AutoTurnMsec` の経路との突き合わせ**: `CONF_KEY_*` / `DEF_*` /
  `*_MIN` / `*_MAX` の置き場所（`MainBinder`）、`DisplayArgs` への追加、
  `_get_conf_int()` の呼び方、`MainHandler` への再エクスポート
  （テスト用。`AutoTurnMsec` も同じく src からは使われていない）、
  `main_view.py` の `common` への追加、`conf.py` の `DEF_CONF` と
  その上のコメント一覧 — すべて `AutoTurnMsec` と同じ形で、食い違いは無い。
  `main_view.py` の `common` は週間・月間の両方の返り値に展開されるので、
  月間表示でも値が渡る
- **既存の `conf.json` に `GaugeFollowMsec` が無い場合**: `_get_conf_int()`
  は `get_conf()` が `None` を返した時点で既定値を返し、警告も出さない。
  `DEF_CONF` はファイルが無いときの書き出しにしか使わないので、
  既存ユーザの `conf.json` が書き換わることもない
- **`gauge.js` を全ページで読む件**: ドラッグのハンドラを `window` に
  登録しているのは `main-page.js:670-672` だけで、これは `main.html` からしか
  読まれない。編集画面・ゴミ箱では `startGaugeBarFollowTimer()` に
  到達する経路が無い。`Number(undefined) || 500` の落とし方も妥当で、
  フォールバックが無いと `setTimeout(fn, NaN)` が 0ms 扱いになって
  即座に追従してしまう（`main.html` でも、ハンドラ登録から
  `onloadHdr()` が走るまでの隙間で `gauge_follow_msec` は undefined）。
  ここを握り潰さずに既定へ落とすのは正しい
- **範囲 100〜3000 の下限 100**: 押した瞬間から 100ms で追従するので
  「タップ」との区別がほぼ無くなるが、誤爆しても行き先は
  「指のある位置の週」なので実害は小さく、離せば同じ週に落ち着く。
  手で書く上級者向けの設定として、下限 100 は許容範囲だと見る
- **追加したテスト**: 既定値・conf からの値・範囲外（`"50"` / `"99999"`）・
  数字でない値（`"abc"`）・手で書いた値が消えないこと、の 5 点を
  押さえていて、`AutoTurnMsec` 側と揃っている。境界値ちょうど
  （`"100"` / `"3000"`）が通ることは見ていないが、`AutoTurnMsec` も
  見ていないので、揃っているという意味では問題無い。
  `test_handler.py` の `DEF_CONF` 突き合わせも足されている
- **文書**: `docs/User.md` は「次の 5 つ」＝表の行数と一致、TODO 番号も
  書いていない。`src/README.md` の「この 4 つ」（`ConfFile` の項）と
  「この 3 つと、月間表示の `LoadMonthPages`」（`MainHandler` の項）は
  どちらも数が合っている。既定・範囲の記述もコードと一致。
  `tests/README.md` の追記も実態どおり。
  implementer 報告の「`src/README.md` の 377 行目付近は触っていない」は
  報告の誤りで、実際には `gauge_follow_msec` が足されている（差分のほうが正しい）

## 確信度の低いもの（気になった程度）

- **`gauge.js` の `DEF_GAUGE_FOLLOW_MSEC = 500` が、サーバ側の既定
  （`MainBinder.DEF_GAUGE_FOLLOW_MSEC`）と二重管理になる。**
  `AutoTurnMsec` には JS 側の既定が無いので、この点だけ経路が違う。
  上に書いたとおりフォールバック自体は要ると思うので、消せとは言わない。
  片方だけ変わってもテストは気づかない、という程度の話
- **`docs/User.md` の JSON の例が `"GaugeFollowMsec": "500"`** で、
  既定値と同じ。他のキーは既定と違う値を書いて「変えた例」になって
  いるので、揃えるなら `"300"` などにしたほうが例として分かりやすい
- **`docs/User.md` の操作の説明（19〜20 行）には「ゲージを押すと飛ぶ」しか
  書いておらず、ドラッグして指を止めると追従する動作の説明が無い。**
  設定の表だけに「ドラッグ中に指を止めてから」と出てくる状態。
  TODO-178 のときからの積み残しで、この項目の範囲外
- `gauge.js:27` の書き換え「一定時間**ごと**の追従判定」は、実際には
  「止まってから一定時間**後**」なので、`ごと` は残さないほうが正確
  （元の「1 秒ごと」も同じ誤りだった）

## 参考: スマホでの追従の遅さ（TODO-186 の予定分。この項目では直さない）

既定を 500 に縮めても、**指のドラッグでは効かない可能性が高い**と見る。

`gaugeBarPointerMoveHdr` は末尾で無条件に `startGaugeBarFollowTimer()` を
呼び、その中で `clearTimeout()` してから張り直す。タッチでは指を止めた
つもりでも微細な揺れで `pointermove` が 60Hz 前後（間隔 16ms 程度）で
届き続けるため、500ms のタイマーはいつまでも発火しない。1000ms を
500ms にしても、「イベントが 500ms 途切れる」ことが起きなければ同じ。

安く直すなら、`gaugeBarPointerMoveHdr` の中で
**`gaugeBarDragMonday` が前回と変わったときだけタイマーを張り直す**
のが効くはず（週が変わらない揺れではタイマーを温存する）。針とラベルの
追従は今までどおり毎回動かせる。TODO-186 を立てるときの案として。
