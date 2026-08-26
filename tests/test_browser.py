#
# (c) 2026 Yoichi Tanibayashi
#
"""ブラウザを動かすテスト（TODO-056）

``pytest`` だけでは ``my.js`` が動かないので、JavaScript の退行を
捕まえられない（TODO-049 のホームボタンの不具合を、テストが 1 件も
落ちないまま見逃した）。ここでは実際にサーバを起動し、playwright で
chromium を動かして、URL だけでなく**画面が変わったか**まで見る。

ブラウザはシステムの ``/usr/bin/chromium`` を使う。
``~/.cache/ms-playwright`` に入るビルドは版が合わず起動しない
（TODO-045）。無ければテストごと skip する。
"""

import datetime
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest

playwright_api = pytest.importorskip("playwright.sync_api")

CHROMIUM = "/usr/bin/chromium"

URL_PREFIX = "/ytsched"

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
    if not os.path.exists(CHROMIUM):
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


def test_home_button_moves_the_view(page, server):
    """ホームボタンで、URL だけでなく画面も今日へ動く（TODO-049）。

    ``scrollToId()`` が「1 画面に収まっているか」を DOM に目的の日が
    あるかより先に見ていたころは、**URL だけが今日に書き換わって
    画面は前の週のまま**になった。表示中の週に無い日を指されても
    「スクロールで足りた」と答えてしまい、読み直しが飛んだため。
    """
    today = datetime.date.today()
    far = today - datetime.timedelta(days=70)

    _open(page, server, far.strftime("%Y-%m-%d"))

    # 開いた時点では、今日は画面に無い
    today_id = f"#date-{today.strftime('%Y-%m-%d')}"
    assert page.locator(today_id).count() == 0

    page.locator("#home_button").click()

    # URL が今日になるだけでは足りない。今日の欄が実際に出ること
    page.wait_for_selector(today_id, state="visible", timeout=10000)
    assert _date_in_url(page) == today.strftime("%Y-%m-%d")


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


def _center_x(page, selector):
    """要素の左右の中心（px）。"""
    box = page.locator(selector).bounding_box()
    assert box is not None
    return box["x"] + box["width"] / 2


def test_gage_label_moves_with_the_needle(page, server):
    """週の差のラベルが、針と一緒に動く（TODO-066）。

    ラベルは針の入れ物の中にあるので、針が動けばラベルも同じだけ動く。
    今週から離れた週を開き、ラベルの文字と、針との中心のずれを見る。
    """
    today = datetime.date.today()
    far = _monday_of(today) + datetime.timedelta(days=3 * 7)

    _open(page, server, far.strftime("%Y-%m-%d"))

    label = page.locator("#gage_r_label")
    label.wait_for(state="visible", timeout=10000)

    # 針が動き終わるのを待つ（transition は 0.3s）
    page.wait_for_function(
        "() => document.getElementById('gage_r_label').textContent.trim() === '+3w'",
        timeout=10000,
    )
    page.wait_for_timeout(500)

    # 針より右にいる（今週は中央）
    assert _center_x(page, "#gage_r") > page.viewport_size["width"] / 2

    # ラベルの中心が、針の中心とそろっている
    assert (
        abs(
            _center_x(page, "#gage_r_label")
            - _center_x(page, ".my-gage-r-needle")
        )
        < 2
    )


def test_gage_label_is_plus_minus_zero_in_this_week(page, server):
    """今週のときは ``±0``（TODO-066）。"""
    today = datetime.date.today()

    _open(page, server, today.strftime("%Y-%m-%d"))

    page.wait_for_function(
        "() => document.getElementById('gage_r_label').textContent.trim()"
        " === '\\u00b10'",
        timeout=10000,
    )
