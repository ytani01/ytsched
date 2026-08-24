# TODO-041 verifier への依頼

## 直したこと

`src/ytsched/webroot/templates/main.html` の 1 か所だけ。読み直したあとの
位置合わせに渡す `behavior` を `"auto"` から `"instant"` に変えた。

```
     scrollToDate(location.pathname,
                  el_date.value, el_sde_align.value,
                  "instant");
```

`scrollTo()` の `"auto"` は「即座に」ではなく「CSS の `scroll-behavior` に
従う」という意味で、TODO-040 で入れた Bootstrap 5.3.8 が
`:root{scroll-behavior:smooth}` を持っているため、一瞬で飛んでいた位置合わせが
アニメーションになっていた。それが「スクロールで追加読み込みが起きるたびに
画面が下から上へ流れる」という症状。

## 確かめてほしいこと

### 1. lint とテスト

```sh
mise run lint
mise run test
```

`main.html` を変えているので、テンプレートを見ているテストがあれば影響する。
落ちたら出力をそのまま報告すること。

### 2. 追加読み込みの直後に、狙った位置へ一度で移るか

これが本題。**headless の Chromium は smooth スクロールを実行しない**ので、
`"auto"` が smooth に化けていれば追加読み込みの直後の `scrollY` は `0` の
まま動かない。直っていれば `scrollToId` が狙った位置に一致する。

修正前に main が測った値は次のとおり（viewport 412x915、データ無しの
一時 datadir）。

| | 値 |
|---|---|
| 追加読み込み直後の `scrollY` | `0`（動かない＝症状が出ている） |
| `scrollToId` が狙った位置 | `2611` |

手順。**`--datadir` は一時ディレクトリを指定する**（実データを汚さない）。
ポートは `10098` を使うこと。

```sh
mkdir -p /tmp/<自分の作業場>/data
uv run ytsched webapp --datadir /tmp/<自分の作業場>/data --port 10098 &
```

Playwright は uv で一時的に入れて使う（プロジェクトの依存は増やさない）。
ブラウザは既にあるものを実行ファイル指定で使う。

```sh
uv run --no-project --with playwright python <スクリプト>
```

```python
b = await p.chromium.launch(
    executable_path="/home/ytani/.cache/ms-playwright/chromium-1200/chrome-linux/chrome")
page = await b.new_page(viewport={"width": 412, "height": 915})
```

スクロールで追加読み込みを起こすとき、**`scroll` イベント経由では headless
で `scrollHdr` が発火しなかった**ので、main は下端へ `instant` で移してから
`scrollHdr` を直接呼んだ。同じ経路（`doPost` → 遷移 → `onloadHdr` →
`scrollToDate`）を通る。

```python
await page.evaluate(
    "window.scrollTo({top: document.body.scrollHeight, behavior:'instant'})")
await page.evaluate("scrollHdr('manual')")
await page.wait_for_timeout(3000)
```

遷移したあとに見る値。

```python
await page.evaluate("window.scrollY")
await page.evaluate("document.getElementById('sde_align').value")  # bottom になる
# scrollToId が狙った位置
await page.evaluate("""(() => {
    const d = document.getElementById('date').value;
    const el = document.getElementById(`date-${d}`);
    if (!el) return null;
    const win_h = document.documentElement.clientHeight;
    const mb = document.getElementById('menu_bar').offsetHeight;
    return el.offsetTop + el.offsetHeight - win_h + mb + 30;
})()""")
```

**判定**: 遷移後の `scrollY` が `0` ではなく、狙った位置と一致すれば直っている。

### 3. ボタン操作の smooth が残っているか

`scrollToDate` / `moveToMonday` の既定は `"smooth"` のままにしてある。
下のメニューバーの `<`／`>`（`moveToMonday`）とホームボタンが、
今までどおり動くことを見ておくこと。headless では smooth のアニメーションが
走らないので**位置が動かないのが正常**。エラーが出ていないか、
遷移するはずのときに遷移するか、を見る。

## 決まりごと

- **コードは直さないこと。** 見つけたことは報告するだけ。直すかどうかは main が決める
- **`mise run upgradeproject` は走らせないこと**
- 終わったらアプリのプロセスを止める。`pkill` はパターンで自分のシェルを
  巻き込むので、`pgrep` で PID を確かめてからその PID を kill すること
- 報告は `archives/agents/TODO-041/verifier-report.md` に書く。
  返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内
