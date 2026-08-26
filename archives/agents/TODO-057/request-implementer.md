# TODO-057 implementer への依頼

`TODO.md` の `## TODO-057. スワイプで隣の週を指に追従させる` を実装する。
**決めごとは済んでいる**ので、そこは変えずに作る。読む順は
`TODO.md` の TODO-057 の節 → この依頼書。

## やること

左右のスワイプで、隣の週の中身が指について動くようにする。

## 触るファイル

- `src/ytsched/main_handler.py`
- `src/ytsched/webroot/templates/main.html`
- `src/ytsched/webroot/static/js/my.js`
- `src/ytsched/webroot/static/css/my.css`

## 作り

### 1. サーバが 3 週分を出す（`main_handler.py`）

`get()` の中で、`load_sched()` を**週ごとに呼ぶ**。

- 通常モード: `date - 7日`・`date`・`date + 7日` の 3 回
- 検索モード: 今までどおり `date` の 1 回だけ

`render()` へ `weeks` を足す。要素はこの形にする。

```python
{"pos": "prev" | "cur" | "next", "sched": [...]}
```

**既存の `sched`・`date_from`・`date_to` はそのまま残す。** 週バーと
検索モードの行が使っている。これらは**中央の週の値**（今の値のまま）。

`load_todo()` は今までどおり 1 回だけ呼び、結果を 3 回の
`load_sched()` に渡す。`todo_today_sde` は「今日」の日にだけ付くので、
3 週のどこかに入る。

### 2. テンプレートを 3 パネルに分ける（`main.html`）

いまの `{% for sched_ent in sched %}` のループを、`weeks` のループで
包む。日付ブロックを出す中身は変えない。

```
<div id="week_wrap" class="my-week-wrap">
  {% for w in weeks %}
  <div class="my-week-panel my-week-{{ w['pos'] }}">
    {% for sched_ent in w['sched'] %}
      ... いまの中身 ...
    {% end %}
  </div>
  {% end %}
</div>
```

**日付ブロックの `id` は、中央のパネルにだけ付ける。**

```
{% if w['pos'] == 'cur' %}id="date-{{ sched_date }}"{% else %}data-date="{{ sched_date }}"{% end %}
```

これが**この項目でいちばん外しやすいところ**。`my.js` の
`scrollToId()` は `getElementById('date-YYYY-MM-DD')` で探すので、
隣の週にも同じ `id` があると「画面内にある」と判断して読み直しを
飛ばす。**TODO-049 の退行（URL だけ変わって画面が変わらない）と
まったく同じ形になる。**

検索モードでは `weeks` が 1 要素なので、パネルは `my-week-cur` が
1 つだけになり、見た目は今までと変わらない。

`touchmove` の登録を `{passive: false}` に変える。横の動きと判定した
あと `preventDefault()` で縦スクロールを止めないと、追従できない。
他の 3 つ（`touchstart`・`touchend`・`touchcancel`）は `passive` の
まま。

### 3. CSS（`my.css`）

```
.my-week-wrap  { position: relative; }
.my-week-panel { width: 100%; }
.my-week-prev,
.my-week-next  { position: absolute; top: 0; width: 100%;
                 visibility: hidden; }
.my-week-prev  { left: -100%; }
.my-week-next  { left: 100%; }
```

**中央のパネルだけが通常フローに残り、`body` の高さを決める。**
ラッパーが `position: relative` なので、隣のパネルの `top: 0` は
中央のパネルと同じ上端に並ぶ。ページを縦にスクロールしてもラッパー
ごと動くので、**縦のずれを別に補正する必要は無いはず**。ここは
実際に確かめて、報告に書くこと。

画面の外に置いたパネルで横スクロールバーが出ないよう、`body` に
`overflow-x: hidden` を入れる。

滑らせるときだけ `transition` を掛けるクラスを別に作る
（追従している間は掛けない）。

### 4. 追従と、送りの判定（`my.js`）

- 指が触れたら、いまの `touchStartHdr` の見送り条件（2 本以上の指・
  画面の左右の端・入力欄の上）をそのまま使う
- `touchmove` で、横の動きと判定したら隣のパネルを見えるようにして、
  ラッパーに `transform: translateX(dx)` を掛ける。同時に
  `preventDefault()`
- 指を離したら、**画面幅の 1/3 以上動いていたか、速く払ったとき**
  （`|dx| / 経過ミリ秒` がしきい値を超えたとき）は送る。それ以外は
  `transform` を 0 へ戻す
- **`SWIPE_MAX_MSEC`（800ms）は廃止する。** 指について動くと、ゆっくり
  引っ張って位置を見ながら決める操作が自然になるため
- `SWIPE_X_PER_Y`（縦との切り分け）と `SWIPE_EDGE_PX`（画面端の除外）は
  そのまま

### 5. 送りの経路を 1 本にまとめる（`my.js`）

`moveToMonday()` に「隣の週まで滑らせてから `doGet()` する」を仕込む。

- スワイプ・メニューバーの ◀▶・キーの ←→ が、どれもここを通る
- `transitionend` を待って `doGet()` する。**イベントが来なかった
  ときのために、タイマーでも進むようにしておく**（来ないと週送りが
  効かなくなる）

## 変えないこと

- 送りが決まったあとは**今までどおり `doGet()` でページを読み直す**。
  DOM を差し替える形にはしない
- ゲージと URL は**確定してから**合わせる。`dispGage()` が
  `sessionStorage` の前の週から補間する今の経路をそのまま使う
- 週バー（`fixed-top`）とメニューバー（`fixed-bottom`）は動かさない。
  動かすのは `<main>` の中の週パネルだけ
- `onloadHdr` の高さ計算と `padding` は、**中央のパネル**を基準にする

## 確かめること

`mise run fmt` → `typecheck` → `lint` → `test` を通す。
**`mise run upgradeproject` は走らせない。**

アプリを起動して確かめるときは、`--datadir` に必ず一時ディレクトリを
指定する（`~/ytsched/data` の実データを汚さないため）。

- 週送りが、スワイプ・メニューバーの ◀▶・キーの ←→ のどれでも動くこと
- ホームボタン（1 回押し・2 回押し）が今までどおり効くこと。
  **今日から離れた週で押したときが要注意**（TODO-049 の退行の箇所）
- 検索モードで、見た目と動きが今までと変わらないこと
- 縦にスクロールする週で、縦スクロールが今までどおりできること

## 報告

`archives/agents/TODO-057/implementer-report.md` に書く。

- 何をどう変えたか（ファイルごと）
- `fmt`/`typecheck`/`lint`/`test` の結果
- **決めごとと違う作りにしたところがあれば、その理由**
- **縦のずれの補正が要ったかどうか**
- 判断が要ると思ったところ

**返事は 5 行以内**（終わったか・報告ファイルのパス・判断が要る点）。
報告の中身を返事に貼らないこと。
