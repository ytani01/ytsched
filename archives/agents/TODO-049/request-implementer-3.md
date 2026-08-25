# TODO-049 implementer への依頼（3 回目 / ホームボタンが効かないのを直す）

**利用者が見つけた不具合。**「ホームボタンをシングルクリックしても
今日に飛ばない気がする」。main が再現させて原因まで特定した。

## 症状（再現済み）

今日から離れた週を出しているとき、ホームボタンを 1 回押すと、
**URL だけが今日の日付に書き換わり、画面の中身は前の週のまま**になる。

```
[412x900] body_h=568 win_h=900 収まる=True
    表示中: date-2026-09-28 .. date-2026-10-04
    URL(前): .../ytsched/?date=2026-09-28
    URL(後): .../ytsched/?date=2026-08-26   ← 今日に変わった
    表示中: date-2026-09-28 .. date-2026-10-04   ← 中身は変わっていない
    => 今日(2026-08-26)が画面にある: False
```

412px でも 800px でも同じ。**この状態でリロードすると今日の週が出る**
ので、URL と画面が食い違ったままになる。

## 原因

`my.js` の `scrollToId()`（408 行目あたり）が、

```js
const body_h = document.body.clientHeight;
const win_h = document.documentElement.clientHeight;

elMain.style.visibility = "visible";
if (body_h <= win_h) {
    console.log(`body_h=${body_h} < win_h=${win_h}`);
    return true;              // ← 目的の要素があるか見ずに「成功」を返す
}

const el = document.getElementById(id);   // ← ここに来ない
...
if (el == null) {
    if (search_str) { return true; }
    return false;             // ← 「無かった」を伝える道
}
```

**目的の要素が DOM にあるかどうかを見る前に、「1 画面に収まっている」
というだけで `true`（＝スクロールで用が足りた）を返している。**

呼び出し元の `scrollToDate()` はこれを成功とみなし、
`cur_day.value` を書き換えて `pushDateInUrl()` で URL を積んだうえで、
**`doGet()` を呼ばずに戻る**。だから画面が変わらない。

### なぜ今まで出なかったか

**TODO-049 で持ち込んだ退行。** 前は前後 45 日（91 日ぶん）を縦に
並べていたので `body_h <= win_h` はまず成り立たず、この近道に入らな
かった。入らなければ `el == null` → `false` → `doGet()` で読み直し、
という正しい道を通っていた。週表示にして 7 日だけになったことで、
予定の少ない週では 1 画面に収まるようになり、近道に入るようになった。

**表示中の週の中の日へ飛ぶときは、今も正しく動く**（その日は DOM に
あるので、スクロール不要＝ `true` で正しい）。壊れているのは
**DOM に無い日へ飛ぼうとしたとき**だけ。

## 直し方

**要素があるかどうかを、1 画面に収まっているかどうかより先に見ること。**
順番を入れ替えるだけで直るはず。

```js
elMain.style.visibility = "visible";

const el = document.getElementById(id);
const el_search = document.getElementById('search_str');
const search_str = el_search.value;

if (el == null) {
    if (search_str) { return true; }
    return false;
}

const body_h = document.body.clientHeight;
const win_h = document.documentElement.clientHeight;
if (body_h <= win_h) {
    return true;   // 画面に収まっているので、スクロールは要らない
}
... （以下は今のまま）
```

**次の 2 つを保つこと。**

- `elMain.style.visibility = "visible"` は、どの道を通っても必ず
  行われること（今もそうなっている）
- 検索モードで、結果に無い日を指されたときに `doGet()` へ落とさない
  こと（`if (search_str) return true;` の意味）。ここは変えない

**なぜこの順でなければならないか**をコメントに書くこと（TODO-049）。
順番に意味があることが読めないと、また入れ替えられる。

## 確かめること

- `mise run fmt` / `typecheck` / `lint` / `test`
- **上の症状が直ること。** 今日から離れた週（例:
  `?date=2026-09-28`）を出してホームボタンを 1 回押し、
  **今日を含む週が実際に表示される**こと。幅 412px と 800px の両方で。
  main が使った確認スクリプトが
  `/tmp/claude-649/-home-ytani-work-ytsched/b5243af0-0fb5-4f51-b1bf-755631d38738/scratchpad/home_check.py`
  にある（port 18077 のサーバを見る。そのままでも、書き直して使っても
  よい）
- **同じ週の中の日へ飛ぶときに、余計な読み直しが起きないこと。**
  日付の欄を押したときなどに `doGet()` へ落ちてしまうと、画面が
  ちらついて遅くなる
- **ホームボタンの 2 回押し**（`doGet` で読み直す道）が今までどおり
  動くこと
- **検索したとき**に、結果の日付を押すとその週へ飛ぶこと（verifier が
  1 回目に確認した動き）
- **戻る/進む**（`popstateHdr` も `scrollToId` を呼ぶ）が壊れないこと。
  main が確認した限りでは今も正しく動いている

## 報告

`archives/agents/TODO-049/implementer-report-3.md` に書くこと。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。

**この退行を捕まえるテストを足せるなら足すこと。** ただし
`AsyncHTTPTestCase` では JavaScript が動かないので、Python 側の
テストでは捕まえられない。足せないと判断したなら、その理由を報告に
書くこと（archives に残す）。
