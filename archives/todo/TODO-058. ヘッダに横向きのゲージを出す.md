# TODO-058. ヘッダに横向きのゲージを出す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 26,542 / cache_creation 286,554 / 概算 $4.2 |
|      | main 62% + implementer 25% + verifier 8% + reviewer 5%（料金の割合） |

## きっかけ

左端の縦ゲージは、画面の左に 22px の帯を取り続けるわりに、目盛りが 16 個
あって読み取りにくかった。TODO-055 で週バーを入れたことで、ヘッダに 1 行
足す余地ができたので、**縦ゲージを横ゲージに置き換える**ことにした。

利用者と相談して決めたこと（2026-08-26）:

- **縦ゲージは横ゲージに置き換える。併存させない**
- 置き場所は**週バーの下に 1 行**
- **ゲージのクリックで移動する機能は作らない**（表示だけ）
- 検索モードでは週バーごと出ないので、横ゲージも出さない
- **`wording` は立てない**（利用者の指示）

## やったこと

### 目盛りを割合（%）にした

縦ゲージは `log10(|days| + 0.6) × 70` で px を直に出していた
（`main_handler.py` の `days2y_offset()`）。横は端末で幅が変わるので、
**中央 50% を今週、両端を ±30y とする割合**に直した。

```python
def days2x_percent(days: float) -> float:
    ...
    x_percent = (
        50.0 * math.log10(abs(days) + dd) / math.log10(DAYS_GAGE_MAX + dd)
    )
    x_percent = min(x_percent, 50.0)
```

- `DAYS_GAGE_MAX = DAYS_YEAR * 30`。**50.0 で頭打ちにした**ので、
  30 年より先の日付でも針が帯からはみ出さない
- ラベルの位置は Python が出し、針の位置は JavaScript が出すので、
  **`my.js` の `days2xPercent()` を同じ式にしてある**。JavaScript 側にも
  `DAYS_YEAR = 365.25` と `DAYS_GAGE_MAX` を定数で置いた
- 目盛りは 16 個から **8 個**に減らした（`-30y` `-1y` `-1m` `-1w`
  `+1w` `+1m` `+1y` `+30y`）

| ラベル | `x_percent` | `left` |
|--------|-------------|--------|
| ±1w    | ∓10.90      | 39.10% / 60.90% |
| ±1m    | ∓18.47      | 31.53% / 68.47% |
| ±1y    | ∓31.73      | 18.27% / 81.73% |
| ±30y   | ∓50.00      | 0% / 100% |

### 帯を週バーの中に入れた

`#week_bar` の `.row` の後ろに `.my-gage-bar` を足した。**週バーの中に
置いたので、`onloadHdr` が `offsetHeight` から `paddingTop` を出す経路
（TODO-055）にそのまま乗り、高さが増えても一番上の日付ブロックが隠れない。**
`{% if not search_mode %}` の中なので、**検索モードでは帯ごと出ない**。

そのぶん、**検索モードでは `gage_r` が存在しない**ようになった。
`dispGage()` の先頭に `if (!elGageR0) return;` を足してある。

帯の中身は 4 つ。針だけが SVG で、あとは `div`。

- `.my-gage-axis` — 目盛りの軸（左右いっぱい）
- `.my-gage-base` — 今週のしるし（中央に固定）
- `svg#gage_r` — 針（`left` を JavaScript が書き換える）
- `.my-gage-label` × 8 — ラベル（`left` をテンプレートが埋める）

`.my-gage-bar` に `margin: 0 12px` を入れてある。**両端のラベル
（±30y）は `left: 0%` / `left: 100%` に置かれ、`translateX(-50%)` で
半分はみ出す**ので、その逃げ。

### 針が動く見せ方は変えていない

`sessionStorage` に直前の週の月曜を持ち、`transition` を効かせずにそこへ
一度置いてから今の週へ動かす経路（TODO-049）は**そのまま残した**。
対象が `bottom` から `left` に変わっただけ。
`.my-gage-r.my-gage-r-no-transition` の詳細度をクラス 2 つにしてある理由
（TODO-049 reviewer 指摘 2）も変わらない。

### 消したもの

- 縦ゲージ一式（`gage_r_base`・ラベル 16 個・`elGageRBase`・
  `onloadHdr` の `centerY` とラベルを配る `for` ループ）
- `main` の `padding-left: 22px`（縦ゲージ用の余白）
- CSS の `.my-osd-base` / `.my-gage` / `.my-gage-text`

### テストの切り出し範囲を直した

`tests/test_web.py` の `TestWeekBar.week_bar()` は `id="week_bar"` から
`<!-- container -->` までを切り出していた。**横ゲージのラベルに `+1w`
という文字列があるので、「今週のときは週の差を出さない」を見るテストが
それを拾って落ちた。** 切り出しを `</div><!-- row -->` までに狭めた。

## テスト

- `mise run fmt` / `typecheck` / `lint` / `test` — すべて通った（439 件）
- `days2x_percent` のテストを `tests/test_handler.py` に書き直した。
  0 のとき・符号が対称なこと・単調に増えることに加えて、**±30y で 50 に
  なること**と**60y でも 50 のままであること**（頭打ち）を足した
- verifier が playwright（`env -u DISPLAY`、`/usr/bin/chromium`）で確認:
  - 週送りで `#gage_r` の `getBoundingClientRect().left` が 200 →
    241.4 まで連続して変わり、**0.15〜0.2 秒かけて動く**
  - ホームボタンで中央（200）へ戻る
  - 検索モードでは `#week_bar` も `#gage_r` も DOM に無く、
    console の error / pageerror も無し
  - キャプチャ 360px / 412px / 800px。**360px でもラベル 8 個が
    重ならない**ので、`±1m` を落とす案（立てたときの逃げ道）は使わずに済んだ

## 残っているもの

**TODO-057（スワイプで隣の週を指に追従させる）は、ゲージの位置を
`sessionStorage` に持った直前の週から補間する経路を前提にしている。**
その経路は今回そのまま残したので、TODO-057 の前提は変わっていない。

分担の理由と各担当の報告は
[`archives/agents/TODO-058/`](../agents/TODO-058/README.md) にある。
