# TODO-182 verifier report

## 結論

**不具合あり。** `--my-gauge-shift: 0`（単位なし）のせいで、軸・今週の
しるし・目盛りラベルの `top` が全部 0 に潰れ、帯の上端で重なって描かれる。
`0` を `0px` にすれば意図どおりになる。

## 差分の確認

`git diff HEAD -- src/ytsched/webroot/static/css/my.css` は依頼どおりの 3 点
のみ（`.my-gauge-bar` height 44px→50px、`--my-gauge-shift` 12px→0、直前コメント
の書き直し）。他ファイルの変更なし。

## lint / pytest

| 項目 | コマンド | 結果 |
|------|----------|------|
| lint | `mise run lint` | ○ ruff format 43 files unchanged / ruff check passed / basedpyright 0 errors / mypy 40 files no issues / eslint OK |
| test | `uv run pytest -q` | ○ 673 passed（約 216s） |

ゲージ関連のブラウザテスト（bounding_box・ドラッグ・クリック・ダブルタップ）は
すべて緑。ただし後述のとおり、軸・目盛りの**縦位置を見るテストが無い**ので、
この不具合はテストをすり抜ける。

## playwright（`--datadir` は毎回一時ディレクトリ）

chromium `/usr/bin/chromium`、幅 360 / 412 / 480 / 600 で確認。

- `.my-gauge-bar` の高さ = **50px**（全幅で）。○
- 目盛りラベル 14 個、横方向は帯からはみ出さない。○
- `#week_bar` は `position: fixed`、`body` の `padding-top` は JS が実測で
  58px を設定。一覧の先頭（`.my-week-cur .my-month-header`）は y=62 で
  週バー下端 y=58 の下に来る（かぶらない）。○
- ドラッグ／タップで週が移る（ラベル `±0`→`+1.3y` など）。針の縦位置
  （needle top）はドラッグ・タップの前後で 16 のまま変わらない。○
- 検索モード（`#search_str` に「会議」→ Enter）で `#week_bar` と
  `.my-gauge-bar` が count 0 になり消える。`.my-week-panel` は 1 枚。
  console エラーなし。○
- 全幅で console エラー・pageerror なし。○

## 不具合の詳細

`src/ytsched/webroot/static/css/my.css:665`

```css
:root {
    --my-gauge-shift: 0;      /* ← 単位なし */
}
```

`.my-gauge-axis`（676〜）・`.my-gauge-base`（687〜）・`.my-gauge-label`
（751〜）は `top: calc(19px + var(--my-gauge-shift))` のように**長さと
`var()` を足している**。`var()` が単位なしの `0` に展開されると
`calc(19px + 0)` となり、CSS では長さ＋数値は不正なので `top` の宣言ごと
無効になり、`top` が 0（静的位置）に落ちる。

実測（幅 412、値を差し替えて比較）:

| 要素 | 現状（`0`） | `0px` にすると | `12px`（旧 HEAD） |
|------|------------|----------------|-------------------|
| `.my-gauge-axis` top | 0 | 19px | 31px |
| `.my-gauge-base` top | 0 | 15px | 27px |
| `.my-gauge-label` top | 0 | 22px | 34px |

`.my-gauge-r`（針の入れ物）は `top: var(--my-gauge-shift)` で `calc` を
使っていないため、`top: 0`（単位なし 0 は有効）でたまたま正しい位置。

### 見た目への影響

`~/tmp/playwright-mcp/TODO-182-weekbar-committed.png`（現状）と
`TODO-182-weekbar-with-0px.png`（`0px` に直したとき）を保存した。

現状は、14 個の目盛りラベルが帯の最上段に張り付き、針の上に出るはずの
差分ラベル「±0」が目盛りの「-1w」「+1w」や針と重なって潰れ、読めない。
軸線も最上段。帯の下 4 割ほどが空きになる。依頼のいう「軸・今週のしるし・
針・目盛りが帯の上寄り、下端に約 18px の余白」にはならず、**目盛りが
軸・針・差分ラベルと重なる**壊れた状態。

`0px` にすると、差分ラベル「±0」が針の上に出て読め、目盛りは帯の下寄り、
軸線は中ほど、目盛りの下に余白、という意図どおりの並びになる。

## main の判断が要る点

1. `--my-gauge-shift: 0` → `0px` に直すか（`calc()` 側を
   `calc(19px + 0px + var(...))` 等にする手もあるが、`0px` が最小）。
2. 縦位置の退行を捕まえるテストが無い。`.my-gauge-label` か
   `.my-gauge-axis` の `top`（bounding_box）を見る assert を
   `tests/test_browser.py` に足すか。

---

# 2 回目の検証（修正 ＋ 回帰テスト）

## 差分の確認

- `my.css`: `--my-gauge-shift: 0` → `0px`。直前コメントに「calc で長さと
  数値は足せず、宣言ごと無効になるので 0 でも単位を落とさない」を追記。
  他の変更は 1 回目のまま（bar height 44→50、コメント書き直し）。
- `tests/test_browser.py`: `test_gauge_marks_sit_below_the_top_of_the_bar`
  を 1 件追加（`.my-gauge-label` の bounding_box が帯上端から 10px 超
  下がり、帯下端との間に 8px 超残ることを見る）。`_open` ヘルパ既存。

## lint / pytest

| 項目 | コマンド | 結果 |
|------|----------|------|
| lint | `mise run lint` | ○ ruff / basedpyright 0 errors / mypy 40 files OK / eslint OK |
| test | `uv run pytest -q` | ○ **674 passed**（約 235s。1 回目 673 ＋ 新規 1） |
| 新テスト単体 | `uv run pytest tests/test_browser.py::test_gauge_marks_sit_below_the_top_of_the_bar -q` | ○ 1 passed |

## 新テストが修正前で落ちること

tracked ファイルは書き換えない方針なので、`src/ytsched/webroot` を一時
ディレクトリへコピーし、コピー側の `my.css` の `--my-gauge-shift` だけを
`0`（単位なし）に書き換えて `--webroot` で起動し、新テストの 2 つの
アサーションを同じ手順（`_open` 相当 → `.my-gauge-label` の bounding_box）
で評価した。

- `--my-gauge-shift: 0`（単位なし）: `label.y - bar.y = 0.00`
  → `assert ... > 10` が **FAIL**。テストは回帰を捕まえる。
- 本物の webroot（`0px`）: `uv run pytest ... ::test_gauge_marks_sit_below_the_top_of_the_bar` が pass。

## playwright（`--datadir` は毎回一時ディレクトリ、幅 360/412/480/600）

`0px` の状態で、全幅で同じ値:

| 要素 | 帯上端からの top〜bottom |
|------|-------------------------|
| 帯 `.my-gauge-bar` | 高さ 50px |
| 軸 `.my-gauge-axis` | 19〜20 |
| 今週のしるし `.my-gauge-base` | 15〜24 |
| 針 `.my-gauge-r-needle` | 12〜20 |
| 差分ラベル `#gauge_r_label`（±0） | -1〜9（針の上） |
| 目盛り `.my-gauge-label` ×14 | 22〜32 |

- ±0 ラベルは針より上（bottom 9 ≤ 針 top 12）。○
- 目盛りは軸より下（top 22 ≥ 軸 top 19）、帯の下寄り。○
- 目盛り下端 32 と帯下端 50 の間に **18px** の余地。○
- 目盛り 14 個、横方向のはみ出しなし。○
- console エラー・pageerror なし（全幅）。○

スクショ: `~/tmp/playwright-mcp/TODO-182-weekbar-fixed-0px.png`（修正後）、
`TODO-182-weekbar-committed.png`（1 回目の壊れた状態）。

## 懸念

なし。1 回目の指摘は解消。回帰テストも実際に回帰を捕まえる。
