#
# (c) 2026 ytani01
#
"""ブラウザを動かすテスト（TODO-056）

``pytest`` だけでは ``static/js/`` のスクリプトが動かないので、退行を
捕まえられない（TODO-049 のホームボタンの不具合を、テストが 1 件も
落ちないまま見逃した）。ここでは実際にサーバを起動し、playwright で
chromium を動かして、URL だけでなく**画面が変わったか**まで見る。

ブラウザはシステムの ``/usr/bin/chromium`` を使う。
``~/.cache/ms-playwright`` に入るビルドは版が合わず起動しない
（TODO-045）。無ければテストごと skip する。
"""

import datetime
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

playwright_api = pytest.importorskip("playwright.sync_api")

CHROMIUM = "/usr/bin/chromium"

URL_PREFIX = "/ytsched"

CONF_FNAME = "conf.json"

# 週の内容が 1 画面に収まる高さ。TODO-049 の退行は「1 画面に収まって
# いるか」を先に見ていたせいで起きたので、収まる大きさで見ないと
# 再現しない
VIEWPORT = {"width": 412, "height": 1600}

# サーバの起動を待つ上限（秒）
BOOT_TIMEOUT = 20.0


def _free_port():
    """空いている port 番号を 1 つ取る。"""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def server(tmp_path):
    """テスト用のデータディレクトリでアプリを起動する。

    実データ（``~/ytsched/data``）を汚さないよう、``--datadir`` には
    必ず ``tmp_path`` を渡す。検索語は ``conf.json`` に残るので、
    テストごとに作り直す（TODO-056）。
    """
    datadir = tmp_path / "data"
    port = _free_port()

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "ytsched",
            "webapp",
            "--port",
            str(port),
            "--datadir",
            str(datadir),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://127.0.0.1:{port}{URL_PREFIX}/"

    limit = time.time() + BOOT_TIMEOUT
    while True:
        if proc.poll() is not None:
            raise RuntimeError("webapp が起動しなかった")
        try:
            with urllib.request.urlopen(base_url, timeout=1.0) as res:
                if res.status == 200:
                    break
        except urllib.error.URLError, TimeoutError, ConnectionError:
            pass
        if time.time() > limit:
            proc.terminate()
            raise RuntimeError("webapp の起動が待ち切れなかった")
        time.sleep(0.2)

    try:
        yield base_url
    finally:
        proc.terminate()
        proc.wait(timeout=10)


@pytest.fixture
def page(server):
    """chromium のタブを 1 つ開く。"""
    if not Path(CHROMIUM).exists():
        pytest.skip(f"chromium が無い: {CHROMIUM}")

    with playwright_api.sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROMIUM)
        context = browser.new_context(viewport=VIEWPORT)
        pg = context.new_page()
        try:
            yield pg
        finally:
            context.close()
            browser.close()


def _open(page, base_url, date):
    """``date`` の週を開いて、描画が終わるまで待つ。"""
    page.goto(f"{base_url}?date={date}", wait_until="load")
    # onloadHdr() が visibility を戻すまで待つ
    page.wait_for_selector("#main", state="visible")


def _date_in_url(page):
    """いま開いている URL の ``date``。"""
    from urllib.parse import parse_qs, urlparse

    query = parse_qs(urlparse(page.url).query)
    return query.get("date", [None])[0]


def _monday_of(date):
    """``date`` を含む週の月曜。"""
    return date - datetime.timedelta(days=date.weekday())


def write_conf(datadir, conf):
    """``conf.json`` を書く（テストの下ごしらえ用。``tests/test_web.py``
    と同じ形）。

    ``server`` フィクスチャがアプリを起動したあとに書いてよい
    （``conf.json`` はリクエストのたびに読み直される）。
    """
    import json

    (datadir / CONF_FNAME).write_text(
        json.dumps(conf, ensure_ascii=False), encoding="utf-8"
    )


def _tap(page, locator):
    """マウスでタップ相当の操作をする（``pointerdown`` → ``pointerup``、
    位置は動かさない。TODO-084）。"""
    box = locator.bounding_box()
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.up()


def test_home_button_moves_the_view(page, server):
    """ホームボタンで、URL だけでなく画面も今週へ動く（TODO-049）。

    ``scrollToId()`` が「1 画面に収まっているか」を DOM に目的の日が
    あるかより先に見ていたころは、**URL だけが書き換わって画面は
    前の週のまま**になった。表示中の週に無い日を指されても
    「スクロールで足りた」と答えてしまい、読み直しが飛んだため。

    移動先は今日ではなく今週の月曜（TODO-105）。
    """
    today = datetime.date.today()
    monday = _monday_of(today)
    far = today - datetime.timedelta(days=70)

    _open(page, server, far.strftime("%Y-%m-%d"))

    # 開いた時点では、今日は画面に無い
    today_id = f"#date-{today.strftime('%Y-%m-%d')}"
    assert page.locator(today_id).count() == 0

    page.locator("#home_button").click()

    # URL が変わるだけでは足りない。今週の欄が実際に出ること
    page.wait_for_selector(today_id, state="visible", timeout=10000)
    assert _date_in_url(page) == monday.strftime("%Y-%m-%d")


def test_forward_button_moves_a_week(page, server):
    """週送り（次）が、次の週の月曜まで進む（TODO-063）。

    週の途中の日付から直に月曜を求めていたころは、**同じ週の月曜**に
    なって週が送れなかった。
    """
    # 週の途中（水曜）から始める
    start = _monday_of(datetime.date.today()) + datetime.timedelta(days=2)
    _open(page, server, start.strftime("%Y-%m-%d"))

    page.locator("#forward_button").click()

    expected = _monday_of(start) + datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_back_button_moves_a_week(page, server):
    """週送り（前）が、前の週の月曜まで戻る（TODO-063）。"""
    start = _monday_of(datetime.date.today()) + datetime.timedelta(days=2)
    _open(page, server, start.strftime("%Y-%m-%d"))

    page.locator("#back_button").click()

    expected = _monday_of(start) - datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_double_tap_starts_auto_page_turn(page, server, tmp_path):
    """ダブルタップすると、入力を止めても週が送られ続ける（TODO-084）。

    ``AutoTurnMsec`` を下限（300）にして待つ時間を短くする。
    """
    write_conf(tmp_path / "data", {"AutoTurnMsec": "300", "LoadMonths": "2"})
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    forward = page.locator("#forward_button")
    _tap(page, forward)
    _tap(page, forward)  # 350msec 以内の 2 回目でダブルタップになる

    # 何も操作しなくても、自動送りで週が進み続ける
    expected = monday + datetime.timedelta(days=7 * 5)
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday === monday",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )


def test_tap_again_stops_auto_page_turn(page, server, tmp_path):
    """自動送り中にもう一度タップすると止まる（TODO-084）。"""
    write_conf(tmp_path / "data", {"AutoTurnMsec": "300", "LoadMonths": "2"})
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    forward = page.locator("#forward_button")
    _tap(page, forward)
    _tap(page, forward)  # ダブルタップで自動送りが始まる

    expected = monday + datetime.timedelta(days=7 * 3)
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday === monday",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )

    _tap(page, forward)  # 次のタップで止める（週は送らない）
    # 止めたタイミングで動いていたインターバルによる最後の遷移が直後に起きることがあるため少し待つ
    page.wait_for_timeout(400)
    stopped_at = page.locator(".my-week-cur").get_attribute("data-monday")

    # 止めたあと、``AutoTurnMsec`` の何倍か待っても週が変わらない
    page.wait_for_timeout(1200)
    assert (
        page.locator(".my-week-cur").get_attribute("data-monday")
        == stopped_at
    )


def test_swipe_from_button_does_not_move_a_week(page, server):
    """ボタンの上から始めた横の払いは、週送りとして拾わない（TODO-084）。

    ``swipe.js`` が拾ってしまうと、シングルタップの 1 週送りと
    二重に効いてしまう。
    """
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    box = page.locator("#forward_button").bounding_box()
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2

    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 150, y, steps=5)  # 30px 以上、右へ払う
    page.mouse.up()

    page.wait_for_timeout(500)
    assert page.locator(".my-week-cur").get_attribute(
        "data-monday"
    ) == monday.strftime("%Y-%m-%d")


def _mark(page):
    """「このあとページが読み直されたか」を見るための目印を置く。

    読み直しが起きれば ``window`` ごと作り直されるので、目印は消える
    (TODO-069)。
    """
    page.evaluate("window.__ytsched_mark = 1")


def _marked(page):
    """目印が残っているか（＝ページが読み直されていないか）。"""
    return page.evaluate("window.__ytsched_mark === 1")


def _cur_monday(page):
    """いま見ている週の月曜（``.my-week-cur`` の ``data-monday``）。"""
    return page.locator(".my-week-cur").get_attribute("data-monday")


def test_week_move_does_not_reload_the_page(page, server):
    """読み込んだ範囲の中の週送りは、ページを読み直さない（TODO-069）。

    前後 1 ヶ月ぶんの週を DOM に持つので、隣の週へはサーバへ行かずに
    移れる。**目印が残ったまま週が変わること**を見る。
    """
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    assert _cur_monday(page) == monday.strftime("%Y-%m-%d")
    _mark(page)

    page.locator("#forward_button").click()

    expected = monday + datetime.timedelta(days=7)
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday === monday",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )

    assert _marked(page), "週送りでページが読み直された"
    assert _date_in_url(page) == expected.strftime("%Y-%m-%d")


def test_week_move_reloads_outside_the_loaded_range(page, server):
    """持っている範囲の外へ出るときは読み直す（TODO-069）。

    既定の ``LoadMonths``（1）では前後 4 週を持つので、5 回送ると
    範囲の外に出る。そこで初めてサーバへ行く。
    """
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))
    _mark(page)

    for i in range(1, 6):
        page.locator("#forward_button").click()
        expected = monday + datetime.timedelta(days=7 * i)
        page.wait_for_function(
            "(monday) => document.querySelector('.my-week-cur')"
            ".dataset.monday === monday",
            arg=expected.strftime("%Y-%m-%d"),
            timeout=10000,
        )
        if i < 5:
            assert _marked(page), f"{i} 回目でページが読み直された"
        # 350msec 以内に次のクリックが入るとダブルタップと見なされ、
        # 自動ページ送りが始まってしまう（TODO-084）。それを避けるため、
        # 次のクリックまで間を空ける
        page.wait_for_timeout(400)

    assert not _marked(page), "範囲の外へ出ても読み直されなかった"


def test_week_panel_in_flow_follows_the_week(page, server):
    """見ている週だけが通常フローに残る（TODO-069）。

    ``position: absolute`` の週は body の高さを決めないので、
    見ている週を差し替えたら ``my-week-cur`` も一緒に動かないと、
    body の高さが前の週のままになる。
    """
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    page.locator("#forward_button").click()
    expected = monday + datetime.timedelta(days=7)
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday === monday",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )

    # 通常フローに残るのは 1 つだけで、それが今の週
    assert page.locator(".my-week-cur").count() == 1
    position = page.evaluate(
        "() => getComputedStyle("
        "document.querySelector('.my-week-cur')).position"
    )
    assert position == "static"


def _write_sched(tmp_path, date, title):
    """1 日分のデータファイルを書く（``tests/test_web.py`` と同じ形）。"""
    import json

    path = tmp_path / "data" / date.strftime("%Y") / date.strftime("%m")
    path.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "sde_id": f"id-{date}",
            "date": date.isoformat(),
            "time_start": "09:00",
            "time_end": "10:00",
            "type": "会議",
            "title": title,
            "place": "",
            "detail": "",
        },
        ensure_ascii=False,
    )
    (path / (date.strftime("%d") + ".jsonl")).write_text(
        line + "\n", encoding="utf-8"
    )


def test_popstate_in_search_mode_does_not_reload(page, server, tmp_path):
    """検索モードの「戻る」で、画面内にある日なら読み直さない（TODO-069）。

    検索モードの週は週の区切りに合わないので ``data-monday`` を持たず、
    ``weekOffsetOfDate()`` はいつも null を返す。**「週が分からない」を
    「持っている範囲の外」と取り違えると、検索モードの戻るが毎回
    読み直しになる**（reviewer の指摘）。
    """
    today = datetime.date.today()
    other = today - datetime.timedelta(days=3)
    _write_sched(tmp_path, today, "けんさくよう")
    _write_sched(tmp_path, other, "けんさくよう")

    _open(page, server, today.strftime("%Y-%m-%d"))
    page.locator("#search_str").fill("けんさくよう")
    page.evaluate("document.forms['form_search'].submit()")
    page.wait_for_load_state("load")
    page.wait_for_selector("#main", state="visible")

    # 検索モードでは週が 1 つだけ
    assert page.locator(".my-week-panel").count() == 1

    today_id = f"#date-{today.strftime('%Y-%m-%d')}"
    page.wait_for_selector(today_id)

    _mark(page)

    # 画面内で完結する移動を 1 つ履歴に積んでから、戻る
    page.evaluate("(d) => pushDateInUrl(d)", other.strftime("%Y-%m-%d"))
    page.go_back()
    page.wait_for_timeout(1000)

    assert _marked(page), "検索モードの戻るでページが読み直された"


def _center_x(page, selector):
    """要素の左右の中心（px）。"""
    box = page.locator(selector).bounding_box()
    assert box is not None
    return box["x"] + box["width"] / 2


def test_gauge_label_moves_with_the_needle(page, server):
    """週の差のラベルが、針と一緒に動く（TODO-066）。

    ラベルは針の入れ物の中にあるので、針が動けばラベルも同じだけ動く。
    今週から離れた週を開き、ラベルの文字と、針との中心のずれを見る。
    """
    today = datetime.date.today()
    far = _monday_of(today) + datetime.timedelta(days=3 * 7)

    _open(page, server, far.strftime("%Y-%m-%d"))

    label = page.locator("#gauge_r_label")
    label.wait_for(state="visible", timeout=10000)

    # 針が動き終わるのを待つ（transition は 0.3s）
    page.wait_for_function(
        "() => document.getElementById('gauge_r_label').textContent.trim() === '+3w'",
        timeout=10000,
    )
    page.wait_for_timeout(500)

    # 針より右にいる（今週は中央）
    assert _center_x(page, "#gauge_r") > page.viewport_size["width"] / 2

    # ラベルの中心が、針の中心とそろっている
    assert (
        abs(
            _center_x(page, "#gauge_r_label")
            - _center_x(page, ".my-gauge-r-needle")
        )
        < 2
    )


def test_gauge_label_is_plus_minus_zero_in_this_week(page, server):
    """今週のときは ``±0``（TODO-066）。"""
    today = datetime.date.today()

    _open(page, server, today.strftime("%Y-%m-%d"))

    page.wait_for_function(
        "() => document.getElementById('gauge_r_label').textContent.trim()"
        " === '\\u00b10'",
        timeout=10000,
    )


def test_gauge_diff_label_reflects_the_week_offset(page, server):
    """今週から離れていれば、その差を出す（TODO-072）。

    以前は ``tests/test_web.py`` の ``test_week_diff_is_displayed`` が
    サーバ側の ``calc_gauge_label()`` の戻り値を HTML から見ていたが、
    その関数を消した TODO-078 で、JavaScript 側の ``gaugeDiffLabel()``
    を ``page.evaluate()`` で直に呼ぶ形へ移した。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    for weeks, expected in [(3, "+3w"), (-1, "-1w")]:
        got = page.evaluate("(days) => gaugeDiffLabel(days)", weeks * 7)
        assert got == expected, f"weeks={weeks}"


def test_gauge_diff_label_switches_unit(page, server):
    """1 ヶ月からは月数、1 年からは年数（TODO-072）。

    以前は ``tests/test_web.py`` の
    ``test_unit_switches_to_months_and_years`` が見ていたが、TODO-078 で
    ``gaugeDiffLabel()`` を直に呼ぶ形へ移した。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    for weeks, expected in [(5, "+1.1m"), (-5, "-1.1m"), (53, "+1.0y")]:
        got = page.evaluate("(days) => gaugeDiffLabel(days)", weeks * 7)
        assert got == expected, f"weeks={weeks}"


def test_days2x_percent_zero(page, server):
    """0 のとき 0（TODO-078。以前は ``tests/test_handler.py`` の
    ``test_days2x_percent_zero`` が Python 側で見ていた）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    assert page.evaluate("days2xPercent(0)") == 0.0


def test_days2x_percent_sign(page, server):
    """符号が対称（TODO-078。以前は
    ``tests/test_handler.py`` の ``test_days2x_percent_sign``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    plus7 = page.evaluate("days2xPercent(7)")
    minus7 = page.evaluate("days2xPercent(-7)")
    assert plus7 == pytest.approx(-minus7)
    assert plus7 > 0
    assert minus7 < 0


def test_days2x_percent_is_monotonic(page, server):
    """単調に増える（TODO-078。以前は
    ``tests/test_handler.py`` の ``test_days2x_percent_is_monotonic``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    values = [
        page.evaluate("(d) => days2xPercent(d)", d)
        for d in [1, 3, 7, 30, 365]
    ]
    assert values == sorted(values)


def test_days2x_percent_clamps_at_30y(page, server):
    """±30y がゲージの端 (50) になる（TODO-078。以前は
    ``tests/test_handler.py`` の ``test_days2x_percent_clamps_at_30y``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    days_year = page.evaluate("DAYS_YEAR")
    assert page.evaluate(
        "(d) => days2xPercent(d)", days_year * 30
    ) == pytest.approx(50.0)
    assert page.evaluate(
        "(d) => days2xPercent(d)", -days_year * 30
    ) == pytest.approx(-50.0)


def test_days2x_percent_stays_clamped_beyond_30y(page, server):
    """30y より先の日付でも、端 (50) で頭打ちのまま（TODO-078。以前は
    ``tests/test_handler.py`` の
    ``test_days2x_percent_stays_clamped_beyond_30y``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    days_year = page.evaluate("DAYS_YEAR")
    assert page.evaluate(
        "(d) => days2xPercent(d)", days_year * 60
    ) == pytest.approx(50.0)
    assert page.evaluate(
        "(d) => days2xPercent(d)", -days_year * 60
    ) == pytest.approx(-50.0)


def _gauge_mark_left(page, label_text):
    """``label_text`` の目盛りの ``left`` (%) を返す。無ければ ``None``。"""
    left = page.evaluate(
        """(text) => {
            for (const el of document.querySelectorAll('.my-gauge-label')) {
                if (el.textContent === text) {
                    return el.style.left;
                }
            }
            return null;
        }""",
        label_text,
    )
    if left is None:
        return None
    return float(left.rstrip("%"))


def test_gauge_marks_are_drawn_at_the_same_position(page, server):
    """目盛りが 14 個描かれ、``-1w``/``+1w`` の位置が変わっていない
    （TODO-078）。

    以前は ``main_handler.py`` の ``GAUGE`` をテンプレートが描いていた。
    期待値は、JavaScript 側へ寄せる**前**の HTML から実測した
    （``50 + days2x_percent(±7)`` を ``'%.2f'`` で丸めた値）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    assert page.locator(".my-gauge-label").count() == 14
    assert _gauge_mark_left(page, "-1w") == pytest.approx(46.21, abs=0.01)
    assert _gauge_mark_left(page, "+1w") == pytest.approx(53.79, abs=0.01)


def test_x_percent2days_inverts_days2x_percent(page, server):
    """``xPercent2days()`` が ``days2xPercent()`` の逆になっている
    （TODO-074）。往復させて元の日数に戻ることを見る。
    """
    today = datetime.date.today()
    _open(page, server, today.strftime("%Y-%m-%d"))

    for days in (0, 1, 7, 30, 100, 365, 3650, -1, -7, -100, -3650):
        got = page.evaluate(
            "(days) => xPercent2days(days2xPercent(days))", days
        )
        assert got == pytest.approx(days, abs=1e-6), f"days={days}"


def test_gauge_bar_click_moves_to_the_tapped_week(page, server):
    """ゲージの帯をクリックすると、その位置に応じた週へ移る（TODO-074）。

    3 週間先 (21 日) が指す位置を ``days2xPercent()`` で計算し、その
    座標をそのままクリックする。21 は 7 の倍数なので、逆算した先は
    ちょうど月曜になる。
    """
    today = datetime.date.today()
    monday = _monday_of(today)
    _open(page, server, monday.strftime("%Y-%m-%d"))

    target_days = 21
    x_percent = page.evaluate("(d) => days2xPercent(d)", target_days)

    box = page.locator(".my-gauge-bar").bounding_box()
    assert box is not None
    click_x = box["x"] + box["width"] * (50 + x_percent) / 100
    click_y = box["y"] + box["height"] / 2

    page.mouse.move(click_x, click_y)
    page.mouse.down()
    page.mouse.up()

    expected = monday + datetime.timedelta(days=target_days)
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday === monday",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )
    assert _date_in_url(page) == expected.strftime("%Y-%m-%d")
