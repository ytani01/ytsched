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


@pytest.fixture
def touch_page(server):
    """タッチ操作を有効にした chromium のタブを 1 つ開く。"""
    if not Path(CHROMIUM).exists():
        pytest.skip(f"chromium が無い: {CHROMIUM}")

    with playwright_api.sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROMIUM)
        context = browser.new_context(
            viewport=VIEWPORT, is_mobile=True, has_touch=True
        )
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


def test_date_column_and_edit_menu_are_delegated(page, server):
    """日付欄と編集画面の戻る操作がイベント委譲で動く（TODO-108）。"""
    monday = _monday_of(datetime.date.today())
    date = monday.strftime("%Y-%m-%d")
    _open(page, server, date)

    page.locator(f"#date-{date} .my-date-col").click()
    page.wait_for_selector("#input_form", state="visible")
    assert page.locator("#date").input_value() == date

    page.locator('[data-action="back"]').first.click()
    page.wait_for_selector("#main", state="visible")
    assert _date_in_url(page) == date


def _open_edit(page, server, date, sde_id=None):
    """編集画面を開いて、描画が終わるまで待つ。"""
    url = f"{server}edit/?date={date}"
    if sde_id:
        url += f"&sde_id={sde_id}"
    page.goto(url, wait_until="load")
    page.wait_for_selector("#input_form", state="visible")


def test_detail_click_does_not_submit(page, server):
    """詳細欄をクリックしただけでは更新せず、入力欄へフォーカスする。"""
    _open_edit(page, server, datetime.date.today().isoformat())

    page.locator("#detail").click()

    assert page.evaluate("document.activeElement.id") == "detail"
    assert "/edit/" in page.url


def test_detail_tap_does_not_submit(touch_page, server):
    """タッチで詳細欄を押しただけでは更新せず、入力欄へフォーカスする。"""
    _open_edit(touch_page, server, datetime.date.today().isoformat())

    touch_page.locator("#detail").tap()

    assert touch_page.evaluate("document.activeElement.id") == "detail"
    assert "/edit/" in touch_page.url


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
    write_conf(
        tmp_path / "data", {"AutoTurnMsec": "300", "LoadWeekPages": "9"}
    )
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    forward = page.locator("#forward_button")
    _tap(page, forward)
    _tap(page, forward)  # 350msec 以内の 2 回目でダブルタップになる

    # 何も操作しなくても、自動送りで週が進み続ける
    expected = monday + datetime.timedelta(days=7 * 5)
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday >= monday",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )


def test_tap_again_stops_auto_page_turn(page, server, tmp_path):
    """自動送り中にもう一度タップすると止まる（TODO-084）。"""
    write_conf(
        tmp_path / "data", {"AutoTurnMsec": "300", "LoadWeekPages": "9"}
    )
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    forward = page.locator("#forward_button")
    _tap(page, forward)
    _tap(page, forward)  # ダブルタップで自動送りが始まる

    # ダブルタップでの 2 回に加え、自動送りで少なくとも 1 回進んだことを
    # 確認する。300msec ごとの途中の週を正確に待つと、Playwright が
    # 確認する前に通り過ぎたときに待ち続けてしまう。
    expected = monday + datetime.timedelta(days=7 * 3)
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday >= monday",
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


def test_week_move_updates_cur_day_and_hides_date_inputs(page, server):
    """週送りで #cur_day を揃え、ヘッダー・フッターに日付欄を出さない。"""
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    page.locator("#forward_button").click()

    expected = (monday + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    page.wait_for_function(
        "(monday) => document.querySelector('.my-week-cur')"
        ".dataset.monday === monday",
        arg=expected,
        timeout=10000,
    )

    assert page.locator("#header_date").count() == 0
    assert page.locator("#footer_date").count() == 0
    assert page.locator("#cur_day").input_value() == expected


def test_week_move_reloads_outside_the_loaded_range(page, server):
    """持っている範囲の外へ出るときは読み直す（TODO-069）。

    既定の ``LoadWeekPages``（4）では前後 4 週を持つので、5 回送ると
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


def test_week_panel_content_top_matches_cur_and_near(page, server):
    """隣の週（``position: absolute``）と今の週（通常フロー）とで、
    中身（月見出し）の縦位置がそろっている（TODO-163）。

    ``.my-month-header`` の margin-top が、週パネルがブロック整形
    コンテキストを作るかどうかで抜け方が変わり、4px ズレていた。
    週送りの最中に隣の週が一瞬 4px 下にズレて見えたのはこれが原因。
    """
    monday = _monday_of(datetime.date.today())
    _open(page, server, monday.strftime("%Y-%m-%d"))

    cur_top = page.locator(
        ".my-week-cur .my-month-header"
    ).first.bounding_box()["y"]
    near_top = page.locator(
        ".my-week-near .my-month-header"
    ).first.bounding_box()["y"]

    assert cur_top == near_top


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


def _write_trash(tmp_path):
    """ゴミ箱画面用の合成データを書く。"""
    import json

    entries = [
        {
            "trashed_at": "2026-08-30T14:23:05",
            "sde_id": "trash-1",
            "date": "2026-08-20",
            "time_start": "09:00",
            "time_end": "10:00",
            "type": "予定",
            "title": "削除する項目 1",
            "place": "",
            "detail": "",
        },
        {
            "trashed_at": "2026-08-29T14:23:05",
            "sde_id": "trash-2",
            "date": "2026-08-21",
            "time_start": "09:00",
            "time_end": "10:00",
            "type": "予定",
            "title": "残す項目 2",
            "place": "",
            "detail": "",
        },
    ]
    (tmp_path / "data" / "trash.jsonl").write_text(
        "".join(
            json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries
        ),
        encoding="utf-8",
    )


def test_trash_select_confirm_and_delete(page, server, tmp_path):
    """確認を経て、選んだ項目だけを削除する（TODO-141）。"""
    _write_trash(tmp_path)
    page.goto(f"{server}trash", wait_until="load")

    entries = page.locator(".my-trash-entry .my-trash-select")
    delete_button = page.locator("#trash-delete-form button")
    assert entries.count() == 2
    assert delete_button.is_disabled()

    entries.nth(0).check()
    assert not delete_button.is_disabled()
    select_all = page.locator("#trash-select-all")
    assert not select_all.is_checked()
    assert not select_all.evaluate("el => el.indeterminate")

    messages = []

    def dismiss(dialog):
        messages.append(dialog.message)
        dialog.dismiss()

    page.once("dialog", dismiss)
    delete_button.click()
    assert messages == ["選択した 1 件を完全に消します。よろしいですか?"]
    assert entries.count() == 2

    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_navigation(wait_until="load"):
        delete_button.click()
    assert page.url == f"{server}trash"
    assert page.locator(".my-trash-entry").count() == 1
    assert page.get_by_text("残す項目 2").count() == 1
    assert page.get_by_text("削除する項目 1").count() == 0


def test_trash_entry_shows_date_column_like_search_result(
    page, server, tmp_path
):
    """検索結果と同じ日付欄つきで出て、編集画面へは行けない（TODO-148）。"""
    _write_trash(tmp_path)
    page.goto(f"{server}trash", wait_until="load")

    entries = page.locator(".my-trash-entry")
    assert entries.count() == 2
    date_cols = page.locator(".my-trash-entry .my-date-col")
    assert date_cols.count() == 2
    assert date_cols.nth(0).locator(".my-date-day").inner_text() == "20"
    assert "(Thu)" in date_cols.nth(0).locator(".my-date-wday").inner_text()

    # 編集画面への遷移が起きない（クリックしても URL が変わらない）
    page.locator(".my-trash-entry .my-sde-content-col").first.click()
    assert page.url == f"{server}trash"


def test_trash_date_column_click_moves_to_that_week(page, server, tmp_path):
    """日付欄を押すと、その日を含む週の週間表示へ移る（TODO-149）。"""
    _write_trash(tmp_path)
    page.goto(f"{server}trash", wait_until="load")

    with page.expect_navigation(wait_until="load"):
        page.locator(".my-trash-entry .my-date-col").first.click()

    assert page.url == f"{server}?date=2026-08-20&sde_align=top"
    # 2026-08-20 (木) を含む週の月曜 2026-08-17 が表示される
    assert page.locator("#date-2026-08-17").count() == 1
    assert page.locator("#date-2026-08-20").count() == 1


def test_trash_select_all_checks_and_unchecks_displayed_entries(
    page, server, tmp_path
):
    """全選択・全解除で表示中の全項目を切り替えられる（TODO-142）。"""
    _write_trash(tmp_path)
    page.goto(f"{server}trash", wait_until="load")

    entries = page.locator(".my-trash-entry .my-trash-select")
    select_all = page.locator("#trash-select-all")
    select_all.check()

    assert entries.count() == 2
    assert entries.nth(0).is_checked()
    assert entries.nth(1).is_checked()
    assert not select_all.evaluate("el => el.indeterminate")
    assert not page.locator("#trash-delete-form button").is_disabled()

    select_all.uncheck()
    assert not entries.nth(0).is_checked()
    assert not entries.nth(1).is_checked()
    assert not select_all.is_checked()
    assert not select_all.evaluate("el => el.indeterminate")
    assert page.locator("#trash-delete-form button").is_disabled()


def test_detail_change_submits_update_on_blur(page, server, tmp_path):
    """詳細を変えてフォーカスを外すと、更新して編集画面に戻る。"""
    date = datetime.date.today()
    _write_sched(tmp_path, date, "変更前")
    _open_edit(page, server, date.isoformat(), f"id-{date}")

    page.locator("#detail").fill("変更後の詳細")
    with page.expect_navigation(wait_until="load"):
        page.locator("#title").click()

    assert page.locator("#detail").input_value() == "変更後の詳細"


def test_update_button_still_submits(page, server, tmp_path):
    """更新ボタンは、これまでどおり予定を更新する。"""
    date = datetime.date.today()
    _write_sched(tmp_path, date, "変更前")
    _open_edit(page, server, date.isoformat(), f"id-{date}")

    page.locator("#title").fill("更新ボタンで変更")
    with page.expect_navigation(wait_until="load"):
        page.locator(
            '[data-action="submit-cmd"][data-cmd="update"]'
        ).first.click()

    assert page.locator("#title").input_value() == "更新ボタンで変更"


def test_update_button_in_bottom_bar_also_submits(page, server, tmp_path):
    """下側の帯の更新ボタンも予定を更新する（TODO-177）。

    ボタンの帯は上下 2 か所にあり、``edit-page.js`` は
    ``.my-edit-bar`` を回してリスナーを付けている。上の
    ``test_update_button_still_submits`` が押すのは DOM 順で先に来る
    上側なので、下側にもリスナーが付いていることをここで見る。
    """
    date = datetime.date.today()
    _write_sched(tmp_path, date, "変更前")
    _open_edit(page, server, date.isoformat(), f"id-{date}")

    assert (
        page.locator('[data-action="submit-cmd"][data-cmd="update"]').count()
        == 2
    )

    page.locator("#title").fill("下の更新ボタンで変更")
    with page.expect_navigation(wait_until="load"):
        page.locator(
            '[data-action="submit-cmd"][data-cmd="update"]'
        ).last.click()

    assert page.locator("#title").input_value() == "下の更新ボタンで変更"


def test_long_search_result_loads_without_javascript_error(
    page, server, tmp_path
):
    """ヘッダーが無い長い検索表示でも読み込み処理が完了する（TODO-111）。"""
    today = datetime.date.today()
    for days in range(20):
        _write_sched(
            tmp_path,
            today - datetime.timedelta(days=days),
            "けんさくよう",
        )
    write_conf(tmp_path / "data", {"SearchN": "20"})

    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    _open(page, server, today.strftime("%Y-%m-%d"))
    page.locator("#search_str").fill("けんさくよう")
    page.evaluate("document.forms['form_search'].submit()")
    page.wait_for_load_state("load")
    page.wait_for_selector("#main", state="visible")

    assert page.locator("#header_date").count() == 0
    assert page.locator("#footer_date").count() == 0
    assert page.evaluate(
        "document.body.clientHeight >= document.documentElement.clientHeight"
    )
    assert errors == []


def test_main_and_edit_pages_load_without_javascript_error(page, server):
    """一覧・編集画面の読み込みで pageerror が出ない（TODO-107）。"""
    today = datetime.date.today().isoformat()
    errors = []
    page.on("pageerror", lambda error: errors.append(error))

    _open(page, server, today)
    page.goto(f"{server}edit/?date={today}", wait_until="load")
    page.wait_for_selector("#input_form", state="visible")

    assert errors == []


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
    page.evaluate(
        "(d) => window.ytsched.pushDateInUrl(d)",
        other.strftime("%Y-%m-%d"),
    )
    page.go_back()
    page.wait_for_timeout(1000)

    assert _marked(page), "検索モードの戻るでページが読み直された"


def _open_search(page, server, tmp_path, today, search_n=1):
    """``today`` にヒットする 1 件を書き、検索モードで開く（TODO-116）。

    ``doSubmit()`` を通さず ``form_search`` を直に送ることで、hidden の
    ``cur_day`` を ``today`` のまま送る。これで検索の基準日（``date_to``）
    が ``today`` になる。
    """
    _write_sched(tmp_path, today, "けんさくよう")
    write_conf(tmp_path / "data", {"SearchN": str(search_n)})

    _open(page, server, today.strftime("%Y-%m-%d"))
    page.locator("#search_str").fill("けんさくよう")
    page.evaluate("document.forms['form_search'].submit()")
    page.wait_for_load_state("load")
    page.wait_for_selector("#main", state="visible")
    _assert_search_screen(page)


def _in_search_mode(page):
    """検索モードで表示されているか（TODO-165）。

    サーバは検索モードのときだけ ``#main`` に ``data-search-date-to`` を
    付ける（``main.html``）。

    TODO-164 では ``#footer_date`` の有無で見ていたが、あの欄は
    TODO-119 で消えていて**どちらのモードでも 0 件**になる。検索モードか
    どうかを何も見ていなかった。
    """
    return page.locator("#main[data-search-date-to]").count() > 0


def _assert_search_screen(page):
    """検索画面の見た目になっていること（週パネル 1 枚・週バー無し）。"""
    assert _in_search_mode(page), "検索モードになっていない"
    assert page.locator(".my-week-panel").count() == 1
    assert page.locator("#week_bar").count() == 0


def _assert_top_screen(page):
    """トップ画面（検索していない週間表示）の見た目になっていること。"""
    assert not _in_search_mode(page), "検索モードが解けていない"
    assert page.locator("#search_str").input_value() == ""
    assert page.locator("#week_bar").count() == 1
    assert page.locator(".my-week-panel").count() > 1
    assert page.locator("#main[data-view='month']").count() == 0


def test_footer_forward_button_moves_search_date_by_a_week(
    page, server, tmp_path
):
    """検索モードのフッターの ＞ は、検索の基準日を 1 週間進める（TODO-116）。

    ``moveToMonday()`` を通すと、いったん月曜へ丸められてしまい、表示
    期間が長いほど先へ進まなくなる。丸めずに ±7 日するだけになったか
    を見る。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    page.locator("#forward_button").click()

    expected = today + datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_footer_back_button_moves_search_date_by_a_week(
    page, server, tmp_path
):
    """検索モードのフッターの ＜ は、検索の基準日を 1 週間戻す（TODO-116）。"""
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    page.locator("#back_button").click()

    expected = today - datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_double_tap_forward_starts_auto_page_turn_in_search_mode(
    page, server, tmp_path
):
    """検索画面の ＞ のダブルタップで、再読み込み後も自動で進む（TODO-123）。"""
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)
    write_conf(
        tmp_path / "data",
        {"SearchStr": "けんさくよう", "SearchN": "1", "AutoTurnMsec": "300"},
    )

    forward = page.locator("#forward_button")
    _tap(page, forward)
    first = today + datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={first.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )
    page.wait_for_selector("#main", state="visible")
    _tap(page, forward)

    expected = today + datetime.timedelta(days=7 * 5)
    page.wait_for_function(
        "(date) => new URL(location.href).searchParams.get('date') >= date",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )


def test_double_tap_back_starts_auto_page_turn_in_search_mode(
    page, server, tmp_path
):
    """検索画面の ＜ のダブルタップで、再読み込み後も自動で戻る（TODO-123）。"""
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)
    write_conf(
        tmp_path / "data",
        {"SearchStr": "けんさくよう", "SearchN": "1", "AutoTurnMsec": "300"},
    )

    back = page.locator("#back_button")
    _tap(page, back)
    first = today - datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={first.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )
    page.wait_for_selector("#main", state="visible")
    _tap(page, back)

    expected = today - datetime.timedelta(days=7 * 5)
    page.wait_for_function(
        "(date) => new URL(location.href).searchParams.get('date') <= date",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )


def test_tap_again_stops_auto_page_turn_in_search_mode(
    page, server, tmp_path
):
    """検索画面で自動送り中に同じボタンを押すと止まる（TODO-123）。"""
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)
    write_conf(
        tmp_path / "data",
        {"SearchStr": "けんさくよう", "SearchN": "1", "AutoTurnMsec": "300"},
    )

    forward = page.locator("#forward_button")
    _tap(page, forward)
    first = today + datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={first.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )
    page.wait_for_selector("#main", state="visible")
    _tap(page, forward)
    expected = today + datetime.timedelta(days=7 * 3)
    page.wait_for_function(
        "(date) => new URL(location.href).searchParams.get('date') >= date",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )
    page.wait_for_selector("#main", state="visible")

    _tap(page, forward)
    page.wait_for_timeout(400)
    stopped_at = _date_in_url(page)
    page.wait_for_timeout(1200)
    assert _date_in_url(page) == stopped_at


def test_tap_outside_stops_auto_page_turn_without_week_slide_in_search_mode(
    page, server, tmp_path
):
    """検索画面の自動送りは週枠を滑らせず、別の場所で止まる（TODO-123）。"""
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)
    write_conf(
        tmp_path / "data",
        {"SearchStr": "けんさくよう", "SearchN": "1", "AutoTurnMsec": "300"},
    )

    forward = page.locator("#forward_button")
    _tap(page, forward)
    first = today + datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={first.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )
    page.wait_for_selector("#main", state="visible")
    _tap(page, forward)
    expected = today + datetime.timedelta(days=7 * 3)
    page.wait_for_function(
        "(date) => new URL(location.href).searchParams.get('date') >= date",
        arg=expected.strftime("%Y-%m-%d"),
        timeout=10000,
    )
    page.wait_for_selector("#main", state="visible")

    assert not page.locator("#week_wrap").evaluate(
        "(el) => el.classList.contains('my-week-wrap-sliding')"
    )
    _tap(page, page.locator("#search_str"))
    page.wait_for_timeout(400)
    stopped_at = _date_in_url(page)
    page.wait_for_timeout(1200)
    assert _date_in_url(page) == stopped_at


def _touch_tap(page, locator):
    """``locator`` の中心を指で 1 回タップする（TODO-165）。

    ``page.touchscreen.tap()`` は CDP でタッチを流し込むので、ブラウザが
    ``touchstart``/``touchend`` に続けて ``mousedown``/``mouseup`` も
    作る。``homeButtonHdr()`` は ``mousedown`` から呼ばれるので、JS で
    組み立てた ``TouchEvent``（``_touch_swipe``）では届かない。
    """
    box = locator.bounding_box()
    assert box is not None
    page.touchscreen.tap(
        box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    )


def _double_tap_home_in_search(page, tap, interval_msec=None):
    """検索画面のホームボタンを 2 回タップする（TODO-165）。

    1 回目のタップで即座にページの読み直しが始まるので、2 回目が落ちる
    先は間隔によって変わる。

    - ``interval_msec`` が ``None``: 間を置かずに続けて押す。2 回目は
      **読み直しの途中**（まだ生きている古いページ）に落ちる
    - 数値: 読み直しが終わるのを待ってから、1 回目の ``interval_msec``
      ミリ秒後に押す。2 回目は**読み直した先のページ**に落ちる

    検索画面の読み直しにかかる時間（この開発機で 180〜360 ミリ秒）と
    同じくらいの間隔は、2 回目が遷移の最中に落ちて Playwright からは
    狙って置けない。その帯は ``None`` 側で代わりに見る。

    **読み直しが間に合わないときは skip せずに落とす。** skip にすると、
    主要な退行テストが黙って消える。
    """
    if interval_msec is None:
        tap(page)
        tap(page)
        return

    start = time.monotonic()
    _mark(page)
    tap(page)
    page.wait_for_function("() => window.__ytsched_mark !== 1", timeout=10000)
    page.wait_for_selector("#main", state="visible")

    elapsed = (time.monotonic() - start) * 1000
    assert elapsed < interval_msec, (
        f"1 回目の読み直しに {elapsed:.0f} ミリ秒かかり、"
        f"{interval_msec} ミリ秒後の 2 回目を置けない"
    )
    page.wait_for_timeout(interval_msec - elapsed)
    tap(page)


def _wait_for_top_screen(page, monday):
    """トップ画面（``monday`` の週、先頭合わせ）になるまで待つ。"""
    page.wait_for_url(
        lambda url: (
            f"date={monday.strftime('%Y-%m-%d')}" in url
            and "sde_align=top" in url
        ),
        timeout=10000,
    )
    page.wait_for_selector("#main", state="visible")


def test_home_button_single_tap_still_reloads_search_screen(
    page, server, tmp_path
):
    """検索画面でホームボタンを 1 回だけ押すと、検索を保ったまま今週の
    月曜へ読み直す（TODO-164・TODO-165）。

    TODO-165 で 1 回目の遅延（350 ミリ秒）をやめたので、ダブルタップの
    判定を挟んでもシングルタップがそのまま効くことを見る。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)
    _mark(page)

    page.locator("#home_button").click()

    # 今日が月曜だと、検索画面の URL がすでに date=<今週の月曜> なので、
    # URL だけ見ても何も検証したことにならない。読み直しが起きたことを
    # 目印で確かめる
    page.wait_for_function("() => window.__ytsched_mark !== 1", timeout=10000)
    page.wait_for_selector("#main", state="visible")

    monday = _monday_of(today)
    assert _date_in_url(page) == monday.strftime("%Y-%m-%d")
    # ダブルタップではないので sde_align は付かない
    assert "sde_align=top" not in page.url
    _assert_search_screen(page)
    assert page.locator("#search_str").input_value() == "けんさくよう"


def test_home_button_double_tap_returns_to_the_top_screen_from_search(
    page, server, tmp_path
):
    """検索画面でホームボタンをダブルタップすると、トップ画面（今週の
    週間表示）へ戻る（TODO-165）。

    TODO-164 では ``sde_align=top`` を付けて ``doGet`` するだけだった。
    検索モードかどうかはサーバが ``conf.json`` の ``SearchStr`` で決めて
    いるので、**検索モードのまま基準日だけが動いていた**。
    ``search_str`` を空にして POST するようにして直した。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    _double_tap_home_in_search(
        page, lambda pg: _tap(pg, pg.locator("#home_button"))
    )

    _wait_for_top_screen(page, _monday_of(today))
    _assert_top_screen(page)


@pytest.mark.parametrize("interval_msec", [500, 600])
def test_home_button_double_tap_by_touch_returns_to_the_top_screen(
    page_touch, server, tmp_path, interval_msec
):
    """指でのダブルタップは、現実的な間隔でも成立する（TODO-165）。

    TODO-164 の作りは 1 回目のタップから 350 ミリ秒後に読み直しを始めて
    いたので、それより遅い 2 回目は読み直しに飲まれて消えた。実機で
    成立したのはタップ間隔 270 ミリ秒までで、人の指には狭すぎた。
    TODO-164 のテストがマウスの速いクリックしか再現しておらず、これを
    見逃した。

    間隔は、TODO-164 が落ちる 350 ミリ秒より広いところを取る。300 ミリ秒
    あたりは検索画面の読み直しにかかる時間と重なって狙って置けないので、
    その帯は
    ``test_home_button_double_tap_returns_to_the_top_screen_from_search``
    （間を置かずに 2 回）が見ている。
    """
    today = datetime.date.today()
    _open_search(page_touch, server, tmp_path, today)

    _double_tap_home_in_search(
        page_touch,
        lambda pg: _touch_tap(pg, pg.locator("#home_button")),
        interval_msec,
    )

    _wait_for_top_screen(page_touch, _monday_of(today))
    _assert_top_screen(page_touch)


def test_home_button_tap_after_another_operation_is_not_a_double_tap(
    page, server, tmp_path
):
    """検索画面で「ホーム → 別の操作 → ホーム」は、1 秒に収まっても
    ダブルタップにしない（TODO-165）。

    ダブルタップの記録はページの読み直しをまたいで残るので、捨てないと
    「ホームを 1 回押しただけなのに検索が消えた」ことになる。ホーム
    ボタン以外を押したら記録を捨てる（``homeTapPointerDownHdr()``）。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    page.locator("#home_button").click()
    monday = _monday_of(today)
    page.wait_for_selector("#main", state="visible")
    page.wait_for_function(
        "(date) => new URL(location.href).searchParams.get('date') === date",
        arg=monday.strftime("%Y-%m-%d"),
        timeout=10000,
    )

    # 間に別の操作を挟む（1 週送り）。ここで記録が捨てられる
    _mark(page)
    page.locator("#forward_button").click()
    page.wait_for_function("() => window.__ytsched_mark !== 1", timeout=10000)
    page.wait_for_selector("#main", state="visible")

    # 続けてホームを 1 回。ここまで 1 秒に収まっていてもシングル扱い
    _mark(page)
    page.locator("#home_button").click()
    page.wait_for_function("() => window.__ytsched_mark !== 1", timeout=10000)
    page.wait_for_selector("#main", state="visible")

    _assert_search_screen(page)
    assert page.locator("#search_str").input_value() == "けんさくよう"


def test_home_button_double_tap_keeps_the_tap_record(page, server, tmp_path):
    """ダブルタップが成立しても、タップの記録は消さない（TODO-165）。

    消してしまうと、トップ画面の読み込みが終わる前の 3 回目のタップが
    「1 回目」に戻り、検索語つきの POST が 2 回目の遷移を上書きして
    **検索画面へ引き戻される**。

    その競合自体は、ローカルのサーバでは遷移が速すぎて 3 回目が必ず
    新しいページに落ちるため再現できない。記録が残っていることを直に
    見る。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    _double_tap_home_in_search(
        page, lambda pg: _tap(pg, pg.locator("#home_button"))
    )

    _wait_for_top_screen(page, _monday_of(today))
    assert page.evaluate(
        "() => sessionStorage.getItem('ytsched_search_home_tap')"
    ), "ダブルタップの成立でタップの記録が消えた"


def test_home_button_double_tap_reloads_the_week_view(page, server):
    """週間表示のホームボタンのダブルタップは、今までどおり今週の月曜を
    先頭にして読み直す（TODO-069・TODO-165）。

    TODO-165 で ``doGet`` から ``doPost``（``search_str`` を空にする）へ
    変えたが、``MainHandler.post()`` のリダイレクト先は同じ URL になる。
    """
    today = datetime.date.today()
    monday = _monday_of(today)
    _open(page, server, monday.strftime("%Y-%m-%d"))
    _mark(page)

    home = page.locator("#home_button")
    _tap(page, home)
    _tap(page, home)

    _wait_for_top_screen(page, monday)
    assert not _marked(page), "ダブルタップでページが読み直されなかった"


def test_home_button_double_tap_returns_to_the_week_view_from_month(
    page, server
):
    """月間表示でホームボタンをダブルタップすると、週間表示へ戻る
    （TODO-165）。

    ``view`` は ``conf.json`` に保存されない（``get_view()``）ので、
    ``view`` を付けない読み直しで週間表示に戻る。
    """
    today = datetime.date.today()
    monday = _monday_of(today)
    page.goto(
        f"{server}?date={monday.strftime('%Y-%m-%d')}&view=month",
        wait_until="load",
    )
    page.wait_for_selector("#main", state="visible")
    assert page.locator("#main[data-view='month']").count() == 1

    home = page.locator("#home_button")
    _tap(page, home)
    _tap(page, home)

    _wait_for_top_screen(page, monday)
    _assert_top_screen(page)


def test_keyboard_arrow_right_moves_search_date_by_a_week(
    page, server, tmp_path
):
    """検索モードでは → キーも、検索の基準日を 1 週間進める（TODO-117）。

    ``keyHdr()`` (keyboard.js) は ``moveToMonday()`` の代わりに
    ``moveActiveDate()`` (week.js) を呼ぶようになった。月曜へ丸めずに
    ±7 日するだけになったかを見る。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    page.keyboard.press("ArrowRight")

    expected = today + datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_keyboard_arrow_left_moves_search_date_by_a_week(
    page, server, tmp_path
):
    """検索モードでは ← キーも、検索の基準日を 1 週間戻す（TODO-117）。"""
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    page.keyboard.press("ArrowLeft")

    expected = today - datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


@pytest.fixture
def page_touch(server):
    """タッチのシミュレート用に ``has_touch`` を有効にしたタブ（TODO-117）。

    ``page`` フィクスチャのコンテキストは ``has_touch`` を付けていない。
    スワイプの検証には合成した ``TouchEvent`` を投げるので、
    ``TouchEvent``/``Touch`` コンストラクタが使えるコンテキストを別に作る。
    """
    if not Path(CHROMIUM).exists():
        pytest.skip(f"chromium が無い: {CHROMIUM}")

    with playwright_api.sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROMIUM)
        context = browser.new_context(viewport=VIEWPORT, has_touch=True)
        pg = context.new_page()
        try:
            yield pg
        finally:
            context.close()
            browser.close()


def _touch_swipe(page, x0, y0, x1, y1):
    """``(x0, y0)`` から ``(x1, y1)`` への 1 本指スワイプを合成する。

    ``touchStartHdr``/``touchMoveHdr``/``touchEndHdr`` (swipe.js) は
    ``isTrusted`` を見ないので、JS 側で組み立てた ``TouchEvent`` でも拾う。
    """
    page.evaluate(
        """([x0, y0, x1, y1]) => {
          const el = document.elementFromPoint(x0, y0);
          const mk = (x, y) => new Touch({
            identifier: 1, target: el, clientX: x, clientY: y,
            pageX: x, pageY: y,
          });
          const fire = (type, touches, changed) => {
            el.dispatchEvent(new TouchEvent(type, {
              touches, targetTouches: touches, changedTouches: changed,
              bubbles: true, cancelable: true,
            }));
          };
          const t0 = mk(x0, y0);
          fire("touchstart", [t0], [t0]);
          const t1 = mk(x1, y1);
          fire("touchmove", [t1], [t1]);
          fire("touchend", [], [t1]);
        }""",
        [x0, y0, x1, y1],
    )


def test_swipe_moves_search_date_by_a_week(page_touch, server, tmp_path):
    """検索モードでの左スワイプは、検索の基準日を 1 週間進める（TODO-117）。

    ``swipeFinish()`` (swipe.js) は ``moveToMonday()`` の代わりに
    ``moveActiveDate()`` (week.js) を呼ぶようになった。検索モードでは
    週パネルが 1 枚しか無く ``hasAdjacentWeek()`` が常に false になるので、
    指に追従させる表示は起きない。それでも ``touchend`` で基準日が
    ±7 日動くことを見る（表示については実装の報告を参照）。
    """
    today = datetime.date.today()
    _open_search(page_touch, server, tmp_path, today)

    _touch_swipe(page_touch, 380, 400, 50, 400)  # 左へ払う (次へ)

    expected = today + datetime.timedelta(days=7)
    page_touch.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_swipe_back_moves_search_date_by_a_week(page_touch, server, tmp_path):
    """検索モードでの右スワイプは、検索の基準日を 1 週間戻す（TODO-117）。"""
    today = datetime.date.today()
    _open_search(page_touch, server, tmp_path, today)

    _touch_swipe(page_touch, 50, 400, 380, 400)  # 右へ払う (前へ)

    expected = today - datetime.timedelta(days=7)
    page_touch.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_mouse_drag_moves_search_date_by_a_week(page, server, tmp_path):
    """検索モードでは PC のマウスの左右ドラッグも、検索の基準日を
    1 週間動かす（TODO-117）。

    検索モードでは週パネルが 1 枚しか無く ``hasAdjacentWeek()`` が常に
    false になるので、``swipeDragTo()`` がそこだけ見送って
    ``swipeDragging`` を立てるようにした。追従表示 (``translateX``) は
    出ないが、離したときに ``swipeFinish()`` (``moveActiveDate()``) へ
    届いて基準日が動くことを見る。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    x0, y0 = 380, 400
    x1 = x0 - 250  # 左へ払う (次へ)。SWIPE_MIN_X・win_w/3 を超える距離
    page.mouse.move(x0, y0)
    page.mouse.down()
    page.mouse.move(x1, y0, steps=5)
    page.mouse.up()

    expected = today + datetime.timedelta(days=7)
    page.wait_for_url(
        lambda url: f"date={expected.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_mouse_drag_within_move_threshold_still_works_as_a_click(
    page, server, tmp_path
):
    """検索モードでも、ドラッグと見なす距離に届かなければクリック扱いの
    まま（TODO-117）。

    ``swipeDragging`` を検索モードで立てるようにしたことで、検索結果の
    予定 (``[data-action="edit-sde"]``、``mouseDownHdr`` が押さえておいて
    ``mouseUpHdr`` がクリックとして呼び戻す経路) が押せなくならないかを見る。
    """
    today = datetime.date.today()
    _open_search(page, server, tmp_path, today)

    entry = page.locator('[data-action="edit-sde"]').first
    box = entry.bounding_box()
    assert box is not None
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2

    # 予定の上で、しきい値未満だけ動かして離す (クリックと同じ扱いになる
    # べき動き)
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 10, y, steps=2)
    page.mouse.up()

    page.wait_for_url(lambda url: "/edit/" in url, timeout=10000)


def _expected_month(monday, direction):
    """``monday`` の月から ``direction`` ヶ月進める/戻すと、表示は
    何年何月になるはずか。

    ``moveActiveMonth()`` (week.js) の内部の丸め方（月の中で何番目の
    月曜かを保つ）を Python 側で再現するのではなく、要件そのもの
    （「1 ヶ月単位で移動する」＝表示の年月がちょうど ``direction`` ヶ月
    分だけ動く）だけを計算する。実装の計算をそのまま Python で
    なぞると、実装に同じ不具合があってもテストが検出できない
    （TODO-136、reviewer の指摘）。
    """
    month_index = monday.month - 1 + direction
    year = monday.year + month_index // 12
    month = month_index % 12 + 1
    return year, month


def _mini_cal_box(page):
    """いま表示中の週のミニカレンダー（1 つめの表）の位置。

    ミニカレンダーは週ごとに 2 つ（表示中の月・翌月）出るので、
    表示中の週の panel (``.my-week-cur``) の中で探す。読み込んだ範囲の
    すべての週にも同じクラスの表があるので、スコープを絞らないと
    隠れている週の表を拾ってしまう。
    """
    box = page.locator(".my-week-cur .my-mini-cal").first.bounding_box()
    assert box is not None
    return box


def _assert_moved_to_month(page, from_date, expected_year, expected_month):
    """URL の ``date`` が、``from_date`` から動いて、指定した年月の
    月曜になっていることを見る（TODO-136）。

    月をまたいでいれば必ず ``date`` が変わるはずなので、``from_date``
    のままではなくなるのをまず待ってから、年月・曜日を確かめる。
    """
    from_str = from_date.strftime("%Y-%m-%d")
    page.wait_for_url(
        lambda url: "date=" in url and f"date={from_str}" not in url,
        timeout=10000,
    )
    date_str = _date_in_url(page)
    assert date_str is not None
    moved = datetime.date.fromisoformat(date_str)
    assert (moved.year, moved.month) == (expected_year, expected_month)
    assert moved.weekday() == 0  # 月曜 (Python は月曜が 0)


def test_touch_swipe_in_mini_cal_moves_by_a_month(page_touch, server):
    """ミニカレンダーの領域での左スワイプは、1 ヶ月進める（TODO-136）。

    移動先の年月がちょうど 1 ヶ月進み、曜日が月曜になっていることを見る
    （移動先の日そのものは、月の中の週の位置に応じて実装が決める）。
    """
    monday = datetime.date(2026, 3, 2)
    _open(page_touch, server, monday.strftime("%Y-%m-%d"))

    box = _mini_cal_box(page_touch)
    x0 = box["x"] + box["width"] / 2
    y0 = box["y"] + box["height"] / 2

    _touch_swipe(page_touch, x0, y0, x0 - 250, y0)  # 左へ払う (次へ)

    _assert_moved_to_month(page_touch, monday, *_expected_month(monday, 1))


def test_touch_swipe_in_mini_cal_back_moves_by_a_month(page_touch, server):
    """ミニカレンダーの領域での右スワイプは、1 ヶ月戻す（TODO-136）。"""
    monday = datetime.date(2026, 3, 2)
    _open(page_touch, server, monday.strftime("%Y-%m-%d"))

    box = _mini_cal_box(page_touch)
    x0 = box["x"] + box["width"] / 2
    y0 = box["y"] + box["height"] / 2

    _touch_swipe(page_touch, x0, y0, x0 + 250, y0)  # 右へ払う (前へ)

    _assert_moved_to_month(page_touch, monday, *_expected_month(monday, -1))


def test_mouse_drag_in_mini_cal_moves_by_a_month(page, server):
    """PC のマウスでミニカレンダーの領域を左右にドラッグしても、
    月単位で動く（TODO-136）。

    週送りと違い、追従表示（``translateX``）は出ない
    （``moveActiveMonth()`` は ``scrollToDate()`` に乗せるだけで、
    週パネルを滑らせる対象ではないため）。ここでは離したあとの移動先
    だけを見る。
    """
    monday = datetime.date(2026, 3, 2)
    _open(page, server, monday.strftime("%Y-%m-%d"))

    box = _mini_cal_box(page)
    x0 = box["x"] + box["width"] / 2
    y0 = box["y"] + box["height"] / 2
    x1 = x0 - 250  # 左へ払う (次へ)。SWIPE_MIN_X・win_w/3 を超える距離

    page.mouse.move(x0, y0)
    page.mouse.down()
    page.mouse.move(x1, y0, steps=5)
    page.mouse.up()

    _assert_moved_to_month(page, monday, *_expected_month(monday, 1))


def test_mouse_drag_in_mini_cal_within_threshold_still_taps_the_day(
    page, server
):
    """ミニカレンダーの領域でも、ドラッグと見なす距離に届かなければ
    セルのタップ（``scroll-date``）として扱われる（TODO-136）。

    ``mouseDownHdr`` が押さえておいて ``mouseUpHdr`` がクリックとして
    呼び戻す経路（``[data-action="scroll-date"]``）が、ミニカレンダーの
    上でも今までどおり働くことを見る。月へは移らず、押したセルの日付
    （``monday`` の 1 週間後）へ移ることを確かめる。
    """
    monday = datetime.date(2026, 3, 2)
    _open(page, server, monday.strftime("%Y-%m-%d"))

    target_date = monday + datetime.timedelta(days=7)
    cell = page.locator(
        f'.my-week-cur .my-mini-cal td[data-date="{target_date}"]'
    )
    box = cell.bounding_box()
    assert box is not None
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2

    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 10, y, steps=2)  # しきい値未満だけ動かす
    page.mouse.up()

    page.wait_for_url(
        lambda url: f"date={target_date.strftime('%Y-%m-%d')}" in url,
        timeout=10000,
    )


def test_month_view_round_trip(page, server):
    """週間表示のミニカレンダーの ``YYYY/MM`` を押すと月間表示になり、
    日付を押すとその日を含む週の週間表示に戻る（TODO-137）。
    """
    monday = datetime.date(2026, 3, 2)
    _open(page, server, monday.strftime("%Y-%m-%d"))

    caption = page.locator(".my-week-cur .my-mini-cal-caption").first
    caption.click()

    page.wait_for_url(lambda url: "view=month" in url, timeout=10000)
    page.wait_for_selector("#main", state="visible")
    page.wait_for_selector(".my-week-cur.my-month-panel", state="visible")

    target_date = monday + datetime.timedelta(days=10)
    cell = page.locator(
        f'.my-week-cur .my-mini-cal td[data-date="{target_date}"]'
    )
    cell.click()

    page.wait_for_selector(
        f"#date-{target_date}", state="visible", timeout=10000
    )
    assert _date_in_url(page) == target_date.strftime("%Y-%m-%d")
    assert "view=month" not in page.url


def _same_block_other_month(today):
    """``today`` と同じ 6 ヶ月ブロックにあり、月だけが違う日を返す
    （TODO-173）。

    ブロックの区切りは 1〜6 月・7〜12 月なので、ブロックの先頭月
    （今日がその月なら次の月）の 15 日にする。ホームボタンを押す前の
    ゲージが ``±0`` にならない距離が要るので、月をずらす。
    """
    start_month = 1 if today.month <= 6 else 7
    month = start_month if today.month != start_month else start_month + 1
    return datetime.date(today.year, month, 15)


def test_home_button_in_month_view_moves_the_gauge_needle(page, server):
    """月間表示でホームボタンを押すと、ゲージの針が中央（``±0``）へ戻る
    （TODO-173）。

    今日と同じ 6 ヶ月ブロックの別の月を開くと、移り先が同じパネルに
    なる。パネルの ``data-monday`` はブロックの代表日のままなので、
    ``setActiveBlockOfDate()`` が押された日付を ``setActiveWeek()`` へ
    渡さないと、針も ``activeMonday`` も動かなかった。
    """
    today = datetime.date.today()
    target = _same_block_other_month(today)

    page.goto(f"{server}?date={target}&view=month", wait_until="load")
    page.wait_for_selector("#main", state="visible")
    assert page.locator("#main[data-view='month']").count() == 1

    label = page.locator("#gauge_r_label")
    label.wait_for(state="visible", timeout=10000)
    page.wait_for_function(
        "() => document.getElementById('gauge_r_label').textContent.trim()"
        " !== ''",
        timeout=10000,
    )
    assert label.text_content().strip() != "\u00b10"

    _tap(page, page.locator("#home_button"))

    page.wait_for_function(
        "() => document.getElementById('gauge_r_label').textContent.trim()"
        " === '\u00b10'",
        timeout=10000,
    )

    # 読み直さずに、月間表示のまま針だけが動く
    assert page.locator("#main[data-view='month']").count() == 1
    assert _date_in_url(page) == _monday_of(today).strftime("%Y-%m-%d")


def test_touch_swipe_in_mini_cal_from_non_monday_moves_by_a_month(
    page_touch, server
):
    """``activeMonday`` が月曜以外の状態でも、ミニカレンダーのスワイプで
    月を移せる（TODO-138）。

    ミニカレンダーのセル（``scroll-date``）をクリックすると
    ``scrollToDate()`` が ``activeMonday`` にそのままクリックした日付を
    入れる。月曜以外の日をクリックしたあと、``moveActiveMonth()`` が
    それを月曜へ丸めずに計算すると例外で落ち、スワイプが効かなく
    なっていた。
    """
    monday = datetime.date(2026, 3, 2)
    _open(page_touch, server, monday.strftime("%Y-%m-%d"))

    non_monday = monday + datetime.timedelta(days=3)  # 木曜
    non_monday_cell = page_touch.locator(
        f'.my-week-cur .my-mini-cal td[data-date="{non_monday}"]'
    )
    non_monday_cell.click()
    page_touch.wait_for_url(
        lambda url: f"date={non_monday}" in url, timeout=10000
    )

    box = _mini_cal_box(page_touch)
    x0 = box["x"] + box["width"] / 2
    y0 = box["y"] + box["height"] / 2

    _touch_swipe(page_touch, x0, y0, x0 - 250, y0)  # 左へ払う (次へ)

    _assert_moved_to_month(
        page_touch, non_monday, *_expected_month(monday, 1)
    )


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
        got = page.evaluate(
            "(days) => window.ytsched.gaugeDiffLabel(days)", weeks * 7
        )
        assert got == expected, f"weeks={weeks}"


def test_gauge_diff_label_switches_unit(page, server):
    """1 ヶ月からは月数、1 年からは年数（TODO-072）。

    以前は ``tests/test_web.py`` の
    ``test_unit_switches_to_months_and_years`` が見ていたが、TODO-078 で
    ``gaugeDiffLabel()`` を直に呼ぶ形へ移した。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    for weeks, expected in [(5, "+1.1m"), (-5, "-1.1m"), (53, "+1.0y")]:
        got = page.evaluate(
            "(days) => window.ytsched.gaugeDiffLabel(days)", weeks * 7
        )
        assert got == expected, f"weeks={weeks}"


def test_days2x_percent_zero(page, server):
    """0 のとき 0（TODO-078。以前は ``tests/test_handler.py`` の
    ``test_days2x_percent_zero`` が Python 側で見ていた）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    assert page.evaluate("window.ytsched.days2xPercent(0)") == 0.0


def test_days2x_percent_sign(page, server):
    """符号が対称（TODO-078。以前は
    ``tests/test_handler.py`` の ``test_days2x_percent_sign``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    plus7 = page.evaluate("window.ytsched.days2xPercent(7)")
    minus7 = page.evaluate("window.ytsched.days2xPercent(-7)")
    assert plus7 == pytest.approx(-minus7)
    assert plus7 > 0
    assert minus7 < 0


def test_days2x_percent_is_monotonic(page, server):
    """単調に増える（TODO-078。以前は
    ``tests/test_handler.py`` の ``test_days2x_percent_is_monotonic``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    values = [
        page.evaluate("(d) => window.ytsched.days2xPercent(d)", d)
        for d in [1, 3, 7, 30, 365]
    ]
    assert values == sorted(values)


def test_days2x_percent_clamps_at_30y(page, server):
    """±30y がゲージの端 (50) になる（TODO-078。以前は
    ``tests/test_handler.py`` の ``test_days2x_percent_clamps_at_30y``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    days_year = page.evaluate("window.ytsched.DAYS_YEAR")
    assert page.evaluate(
        "(d) => window.ytsched.days2xPercent(d)", days_year * 30
    ) == pytest.approx(50.0)
    assert page.evaluate(
        "(d) => window.ytsched.days2xPercent(d)", -days_year * 30
    ) == pytest.approx(-50.0)


def test_days2x_percent_stays_clamped_beyond_30y(page, server):
    """30y より先の日付でも、端 (50) で頭打ちのまま（TODO-078。以前は
    ``tests/test_handler.py`` の
    ``test_days2x_percent_stays_clamped_beyond_30y``）。
    """
    _open(page, server, datetime.date.today().strftime("%Y-%m-%d"))

    days_year = page.evaluate("window.ytsched.DAYS_YEAR")
    assert page.evaluate(
        "(d) => window.ytsched.days2xPercent(d)", days_year * 60
    ) == pytest.approx(50.0)
    assert page.evaluate(
        "(d) => window.ytsched.days2xPercent(d)", -days_year * 60
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
            "(days) => window.ytsched.xPercent2days("
            "window.ytsched.days2xPercent(days))",
            days,
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
    x_percent = page.evaluate(
        "(d) => window.ytsched.days2xPercent(d)", target_days
    )

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
