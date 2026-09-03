# TODO-174 verifier 報告

## 1. `uv run pytest`

○ `uv run pytest -q` → **664 passed, 1 failed**（203.69s）

× `tests/test_web.py::TestMonthMiniCal::test_shows_two_months` が失敗。

```
captions = re.findall(
    r"my-mini-cal-caption[^>]*>\s*([^<]+?)\s*<", panel
)
assert captions == ["2021/03", "2021/04"]
AssertionError: assert ['\n', '2021/...n', '2021/04'] == ['2021/03', '2021/04']
At index 0 diff: '\n' != '2021/03'
```

原因: `mini_cal.html` の変更で `<caption class="my-mini-cal-caption">` の
直後が改行になり、その次に `<span ...>2021/03</span>` が来る形になった。
テストの正規表現は `caption` タグの `>` の直後から最初の `<` までを
キャプチャする作りなので、`\n` だけを拾ってしまい `2021/03` に届かない。
依頼文に名指しされていた 721 行目付近の正規表現がまさにこれで、
修正が必要（テストを span の中身まで見るように直すか、テンプレート側で
`>` の直後に空白を入れないようにするか）。

○ `tests/test_browser.py::test_month_view_round_trip` は **単独実行で
pass**（`.my-week-cur .my-mini-cal-caption` の中心クリックは、
`text-align: center` で span が中央に来るため、そのまま span に当たる）。

○ 依頼にあった `tests/test_web.py` の 792・803・814・860 行目付近の
assert（`"my-mini-cal-caption" in/not in panel` という部分文字列判定）は
クラス名自体を変えていないため影響なし。全て pass。

## 2. lint / format / 型チェック

- ○ `uv run ruff format --check` → `71 files already formatted`
- ○ `uv run ruff check` → `All checks passed!`
- ○ `uv run basedpyright` → `0 errors, 0 warnings, 0 notes`
- ○ `uv run mypy src` → `Success: no issues found in 21 source files`

## 3. HTML の実物確認

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18174` を起動し、
`curl` で `date=2026-09-03`（週間表示）と `date=2026-09-03&view=month`
（月間表示）を取得して確認。HTTP は両方 200。ログに例外・トレースバックなし。
`{{` の残存もなし（0 件）。

週間表示（押せる方）:
```
<caption class="my-mini-cal-caption">
<span class="my-mini-cal-caption-btn my-btn"
data-action="month-view"
data-date="2026-09-01">2026/09</span>
</caption>
```

月間表示（押せない方、span なし・枠なし）:
```
<caption class="my-mini-cal-caption">
2026/09
</caption>
```

依頼どおり、週間表示だけ `my-mini-cal-caption-btn my-btn` の span が付き、
月間表示には付かないことを確認した。

アプリは確認後 kill 済み（`pgrep -f "ytsched webapp.*18174"` で PID を
確認し、個別に kill。ポート 18174 に残存プロセスなし）。

## main の判断が要る点

- `tests/test_web.py::TestMonthMiniCal::test_shows_two_months` が
  落ちている。依頼文で名指しされていた懸念がそのまま的中した形。
  テスト側の正規表現を span の中身まで拾うように直すか、テンプレートの
  改行位置を変えるか、どちらで直すかは main の判断が要る。
