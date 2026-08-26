# TODO-058 implementer への依頼

左端の縦ゲージをやめて、**週バーの下に横向きのゲージの帯を 1 行**出す。
項目の背景と決まっていることは
[`TODO.md` の TODO-058](../../../TODO.md) を読むこと。

**設計はここに書いたとおりに作る。** 数値（px・色）は目安なので、
キャプチャを見て詰めてよい。式・ラベル・DOM の置き場所は変えない。

## 1. `src/ytsched/main_handler.py`

`days2y_offset()` を捨てて、**割合を返す関数に置き換える**。

```python
def days2x_percent(days: float) -> float:
    """今週の中心からの左右のずれを、ゲージの幅に対する割合 (%) で返す"""
```

- `dd = 0.6` は今までどおり
- `DAYS_GAGE_MAX = DAYS_YEAR * 30`（±30y がゲージの端）
- `days == 0` なら `0.0`
- それ以外は
  `50.0 * log10(abs(days) + dd) / log10(DAYS_GAGE_MAX + dd)`
- **50.0 で頭打ちにする**（30y より先の日付でも端から出ない）
- `days < 0` なら符号を反転する

`GAGE` は **8 個に減らし**、キーを `y_offset` から `x_percent` にする。

```python
GAGE = [
    {"label": "-30y", "x_percent": days2x_percent(-DAYS_YEAR * 30)},
    {"label": "-1y",  "x_percent": days2x_percent(-DAYS_YEAR)},
    {"label": "-1m",  "x_percent": days2x_percent(-DAYS_MONTH)},
    {"label": "-1w",  "x_percent": days2x_percent(-7)},
    {"label": "+1w",  "x_percent": days2x_percent(+7)},
    {"label": "+1m",  "x_percent": days2x_percent(+DAYS_MONTH)},
    {"label": "+1y",  "x_percent": days2x_percent(+DAYS_YEAR)},
    {"label": "+30y", "x_percent": days2x_percent(+DAYS_YEAR * 30)},
]
```

値はこうなるはず（確かめること）:

| ラベル | `x_percent` | `left` |
|--------|-------------|--------|
| ±1w    | ∓10.90      | 39.10% / 60.90% |
| ±1m    | ∓18.47      | 31.53% / 68.47% |
| ±1y    | ∓31.73      | 18.27% / 81.73% |
| ±30y   | ∓50.00      | 0% / 100% |

## 2. `src/ytsched/webroot/templates/main.html`

### 帯を足す

`{% if not search_mode %}` の中、**`#week_bar` の `.row` の後ろ**に足す。
`#week_bar` は `fixed-top` だが、`onloadHdr` が `offsetHeight` から
`paddingTop` を出しているので、高さが増えても追従する（TODO-055）。
**検索モードでは週バーごと出ないので、横ゲージも出ない。**

```html
    <!-- 横ゲージ (TODO-058) -->
    <div class="my-gage-bar">
      <div class="my-gage-axis"></div>
      <div class="my-gage-base"></div>
      <svg id="gage_r" class="my-gage-r" viewBox="0 0 12 8">
        <polygon points="0,0 12,0 6,8" />
      </svg>
      {% for d in gage %}
      <div class="my-gage-label"
        style="left:{{ '%.2f' % (50 + d['x_percent']) }}%">{{ d['label'] }}</div>
      {% end %}
    </div>
```

### 消す

- 今の `<!-- gages -->` のかたまり（`gage_r` / `gage_r_base` /
  `gage_r{{ i }}` のラベル）**まるごと**
- `onloadHdr` の中の `centerY`、`let gage = [...]` とその `for` ループ、
  `elGageRBase` の 2 行。**`elGageR0 = document.getElementById("gage_r")`
  と `dispGage(...)` の 2 か所は残す**
- `<main id="main" ...>` の `padding-left:22px`（縦ゲージ用の余白）

`body_h` / `win_h` と `body_h < win_h` の分岐はそのまま残す。

## 3. `src/ytsched/webroot/static/css/my.css`

`.my-osd-base` / `.my-gage` / `.my-gage-text` / `.my-gage-r` /
`.my-gage-base` / `.my-gage-label` を、次の一式に置き換える。
`.my-gage-r.my-gage-r-no-transition` は**残す**（対象が `bottom` から
`left` に変わるだけ。詳細度を 2 つにしてある理由は TODO-049 のコメント
のまま）。`.my-osd-base` は他から使われていないので消してよい。

帯は `.my-bar`（白文字・背景 `#48C`）の中に入るので、針・軸・ラベルは
**白**にする。

```css
/* 横ゲージ (TODO-058)
   中央 (50%) が今週で、両端が ±30y。位置を割合で持つので、
   端末の幅が変わっても目盛りの意味は変わらない。
   左右の 12px は、両端のラベル (±30y) が半分はみ出すぶんの逃げ */
.my-gage-bar {
    position: relative;
    height: 21px;
    margin: 0 12px;
}

/* 目盛りの軸 */
.my-gage-axis {
    position: absolute;
    left: 0;
    right: 0;
    top: 7px;
    height: 1px;
    background-color: #FFF;
    opacity: 0.5;
}

/* 今週のしるし (中央に固定) */
.my-gage-base {
    position: absolute;
    top: 3px;
    left: 50%;
    width: 2px;
    height: 9px;
    background-color: #FFF;
    transform: translateX(-50%);
}

/* 針 (left は JavaScript が書き換える) */
.my-gage-r {
    position: absolute;
    top: 0;
    left: 50%;
    width: 12px;
    height: 8px;
    fill: #FFF;
    transform: translateX(-50%);
    transition: left 0.3s ease-out;
}

/* 目盛りのラベル (left はテンプレートが埋める) */
.my-gage-label {
    position: absolute;
    top: 9px;
    font-size: x-small;
    line-height: 12px;
    white-space: nowrap;
    transform: translateX(-50%);
}
```

## 4. `src/ytsched/webroot/static/js/my.js`

- `days2yOffset()` → `days2xPercent()`。**Python 側と同じ式・同じ
  頭打ち**にする（`DAYS_YEAR` にあたる `365.25` を JavaScript 側にも
  定数で置く）
- `setGagePosition()` は `bottom` を px で入れる代わりに、
  `elGageR0.style.left = ` に `${50 + days2xPercent(top_rel_days)}%` を
  入れる。`document.documentElement.clientHeight` と `centerY` は要らない
- **`dispGage()` の先頭で `elGageR0` が無ければ何もせずに返す。**
  検索モードでは週バーごと帯が出ないので、`gage_r` が存在しない
- `getGageMonday()` / `setGageMonday()` / `placeGageWithoutTransition()` /
  `sessionStorage` を使った補間は**そのまま残す**（TODO-049 の経路）。
  コメントの「針の位置 (`bottom`)」は `left` に直す

## 5. テストと文書

- `tests/test_handler.py` の `days2y_offset` のテストを
  `days2x_percent` に直す。0 のとき・符号が対称なこと・単調に増えること
  に加えて、**±30y で 50 になること**と**60y でも 50 のままであること**
  （頭打ち）を足す
- `tests/README.md` の `days2y_offset` の記述を直す
- 他に `days2y_offset` を参照している箇所が無いか grep で確かめる

## 決まった手順

`mise run fmt` / `typecheck` / `lint` / `test` を通すこと。
**`mise run upgradeproject` は走らせない。**

アプリを起動して見るときは、`--datadir` に**必ず一時ディレクトリ**を
指定する（`~/ytsched/data` を汚さない）。

## 報告

`archives/agents/TODO-058/implementer-report.md` に書く。返事は 5 行以内で、
終わったか・報告ファイルのパス・判断が要る点だけ。
