# TODO-185. ゲージの追従までの待ち時間を、定数にして conf.json で変えられるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer + writer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 24,172 | 89,923 | 45% |
| implementer | Sonnet 5 | medium | 10,976 | 93,804 | 30% |
| reviewer | Opus 5 | high | 14,342 | 74,749 | 18% |
| verifier | Sonnet 5 | medium | 3,359 | 30,255 | 4% |
| writer | Sonnet 5 | medium | 3,072 | 37,645 | 3% |
| 合計 |  |  | 55,921 | 326,376 | 概算 $7.2 |

- implementer・verifier・writer は定義ファイル（`.claude/agents/*.md`）の
  モデル・effort のまま
- reviewer だけ、定義のモデル（sonnet）を Opus 5 に上書きした。既定値が
  1000 → 500 に変わってタイミングに依存するブラウザテストへ影響が出る
  恐れがあり、それを見つけるのに上位モデルを充てた
- writer は見込みに入れていなかった。このファイルを書かせるために立てた
- 概算料金は、Sonnet 5 を $3/$15 で計算している。2026-09-01 に導入価格の
  $2/$10 から上がったので、`tools/token-usage.py` の `PRICING` をこの項目の
  作業中に書き換えた。TODO-184 までの概算は導入価格のまま

## きっかけ

ドラッグ中に指を止めてから追従するまでの待ち時間が、`gauge.js` に `1000`
と直に書いてあった（TODO-178）。反応が遅く感じるので既定を 500 へ縮め、
あとから手で調整できるように設定項目にした。

## やったこと

`AutoTurnMsec`（TODO-084）とまったく同じ経路で `GaugeFollowMsec`
（既定 500、範囲 100〜3000）を通した。

- `main_binder.py` に `CONF_KEY_GAUGE_FOLLOW_MSEC` / `DEF_GAUGE_FOLLOW_MSEC` /
  `GAUGE_FOLLOW_MSEC_MIN` / `GAUGE_FOLLOW_MSEC_MAX` の定数を置き、
  `DisplayArgs.gauge_follow_msec` へ `_get_conf_int()` で入れる
- `conf.py` の `DEF_CONF` に `"GaugeFollowMsec": "500"` を足す
- `main_view.py` の `common`、`main.html` の `#main` に
  `data-gauge-follow-msec="{{ gauge_follow_msec }}"`、`main-page.js` の
  `onloadHdr()` で `dataset.gaugeFollowMsec` を読んで `gauge.js` へ渡す
- `gauge.js` の `startGaugeBarFollowTimer()` で、渡された値
  （`Number(ytsched.gauge_follow_msec)`）を使って待ち時間を決める

`gauge.js` は `base.html` から全ページ（編集画面・ゴミ箱を含む）で
読み込まれるため、値が入っていないときに 500 へ落とすフォールバックを
`gauge.js` 側にも置いた。無いと `setTimeout(fn, NaN)` が 0ms 扱いになって
即座に追従してしまう。この点だけ `AutoTurnMsec`（JS 側の既定が無い）と
経路が違い、既定値がサーバ側と二重管理になるのは承知のうえで残した
（見送ったものに後述）。

「1 秒」と書いてあったコメントを、値に依らない書き方へ直した。`gauge.js`
の 5 か所に加えて、reviewer が `month.js:62`（`hasBlockOfDate()` のコメント）
とブラウザテストのテスト名・docstring・コメントの残りを見つけ、implementer
が直した。テスト名は `test_gauge_drag_follows_after_1_second_stop` →
`test_gauge_drag_follows_after_stopping` に変えた。

### 既定が 500 になったことでブラウザテストの余裕が縮んだ件

reviewer の指摘 1。`test_gauge_drag_does_not_move_screen_while_dragging`
は「追従が起きないこと」を見る assert までの余裕が、既定 1000ms のときの
800ms から、既定 500ms では 300ms に縮む。この機械は負荷でタイミング
テストが落ちることがある（TODO-181）ので、`write_conf` で
`GaugeFollowMsec` を `"3000"` に固定した。`mouse.move` → `mouse.up()` の
間が 500ms を超えると挙動が不定になる
`test_gauge_drag_needle_does_not_jump_back_on_release` も、同じ理由で
待ち時間を固定した。

### 範囲そのものは変えていない

追従の範囲（前後 `LoadWeekPages` 週まで。既定 4）は、この項目では変えて
いない。実測では前後 4 週ちょうどで追従が止まり、`LoadWeekPages` を 52
にすれば 52 週まで広がるが、週パネルが 105 枚・HTML が 2.2 MB になる。
範囲外でも読み直して追従させる案は、読み直しでドラッグが切れるので見送る。

### 見送ったもの

- `gauge.js` 側のフォールバック 500 とサーバ側既定の二重管理。
  フォールバック自体は要るので、消さずに残した
- `docs/User.md` の操作の説明にゲージのドラッグ追従の記述が無い件。
  TODO-178 からの積み残しで、この項目の範囲外

## テスト

`test_web.py` に `AutoTurnMsec` と同じ形で、既定値・conf からの値・
範囲外（`"50"`／`"99999"`）・数字でない値（`"abc"`）・手で書いた値が
消えないこと、の 5 点を足した。`test_handler.py` の `DEF_CONF` 突き合わせにも
足した。

- `mise run fmt` / `typecheck` / `lint` — 通る
- `uv run pytest tests/ --ignore=tests/test_browser.py -q` — 611 passed
- `uv run pytest tests/test_browser.py -q -k gauge` — 15 passed
- verifier がアプリを起動し、`--datadir` に一時ディレクトリを指定して
  `data-gauge-follow-msec` が、未設定 → 500・`"1500"` 指定 → 1500・
  範囲外 `"50"` → 500 になることを確かめた

## この項目から出た別項目

スマホのタップドラッグでは指を止めても追従しない件を TODO-186 として
立てた。`gaugeBarPointerMoveHdr` が pointermove のたびにタイマーを
張り直すため、指の微細な揺れで発火しない。既定を 500 に縮めても
これは直らない（reviewer も同じ見立て）。

## 分担の振り返り

- **各担当が何を見つけたか**: verifier は指摘ゼロ（全項目パス）。
  reviewer は実質的な指摘を 3 件出し、うち 1 件（ブラウザテストの余裕が
  300ms に縮む）はテストが通っている状態では出てこない種類のもの。
  implementer は「1 秒」を `gauge.js` の 5 か所しか直しておらず、
  `month.js` とテスト側の残りを見落とした
- **見込みと食い違ったのはなぜか**: 見込みの 3 担当のとおり。ただし
  reviewer はモデルを上げ、このファイルを書かせる writer が 1 つ増えた
- **次に同じ規模の項目をやるなら、どう組むか**: 料金は
  main 45% + implementer 30% + reviewer 18% + verifier 4% + writer 3%。
  verifier は発見ゼロだが $0.3 と安く、アプリを起動しての確認は main では
  代えにくいので次も分ける。逆に、`AutoTurnMsec` のような先例をなぞる
  だけの経路の追加は implementer に任せる価値が薄く（$2.2 使って
  「1 秒」の直し漏れが出た）、main が直接書いて reviewer に見せる組み方も
  試す余地がある

分担の理由と各担当の報告は `archives/agents/TODO-185/` にある。
