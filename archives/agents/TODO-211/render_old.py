"""旧アプリ（c4e31b4）の sde.html を tornado で描画し、エスケープを確かめる。

使い方: プロジェクトのトップで ``uv run python archives/agents/TODO-211/render_old.py``
title / place / detail に実体参照と HTML タグを入れ、出力の該当行を見る。
"""

import datetime
import subprocess
import sys
import tempfile
from pathlib import Path

import tornado.template as T

OLD = "c4e31b4"


class Sde:
    sde_id = "id1"
    date = datetime.date(2026, 9, 30)
    time_start = None
    time_end = None
    type = "会議"
    place = "X&quot;Y <i>p</i>"

    def __init__(self, title, detail):
        self.title = title
        self.detail = detail

    def is_holiday(self):
        return False

    def is_todo(self):
        return False

    def is_canceled(self):
        return False

    def is_important(self):
        return False


root = Path(tempfile.mkdtemp())
for f in ("base", "sde"):
    (root / f"{f}.html").write_text(
        subprocess.check_output(
            ["git", "show", f"{OLD}:webroot/templates/{f}.html"], text=True
        ),
        encoding="utf-8",
    )
# main.html と同じく、base.html を継承して sde.html を include する
(root / "wrap.html").write_text(
    '{% extends "base.html" %}{% block content %}'
    '{% set sde_count = 0 %}{% include "sde.html" %}{% end %}',
    encoding="utf-8",
)
t = T.Loader(str(root)).load("wrap.html")
ns = dict(
    sde=Sde("T &quot;a&quot; &amp; <b>x</b>", "D &quot;q&quot; &lt;u&gt;\nline2"),
    title="ttl",
    version="v",
    url_prefix="/",
    sched_date=datetime.date(2026, 9, 30),
    today_flag=0,
    today=datetime.date(2026, 9, 30),
    delta_day1=datetime.timedelta(1),
    modified_sde_id=None,
    len=len,
    str=str,
    static_url=lambda x: "/static/" + x,
    xsrf_form_html=lambda: "",
)
for _ in range(30):
    try:
        out = t.generate(**ns)
        break
    except NameError as e:
        name = str(e).split("'")[1]
        print("stub", name, file=sys.stderr)
        ns[name] = ""
print(out.decode())
