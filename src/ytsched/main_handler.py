#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
MainHandler
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import re
import math
import datetime
from .handler import HandlerBase
from .ytsched import SchedDataEnt


def days2y_offset(days: float) -> int:
    """
    Parameters
    ----------
    days: float

    Returns
    -------
    y_offset: int

    """
    dd = 0.6
    a = 70
    b = 0

    if days == 0:
        return 0

    y_offset = round(math.log10(float(abs(days)) + dd) * a + b)

    if days < 0:
        return -y_offset
    return y_offset


DAYS_YEAR = 31 + 28.25 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31
DAYS_MONTH = DAYS_YEAR / 12
print('DAYS_YEAR=%s, DAYS_MONTH=%s' % (DAYS_YEAR, DAYS_MONTH))

GAGE = [
    {'label': '-30y', 'y_offset': days2y_offset(-DAYS_YEAR * 30)},
    {'label': '-10y', 'y_offset': days2y_offset(-DAYS_YEAR * 10)},
    {'label':  '-3y', 'y_offset': days2y_offset(-DAYS_YEAR * 3)},
    {'label':  '-1y', 'y_offset': days2y_offset(-DAYS_YEAR * 1)},
    {'label':  '-3m', 'y_offset': days2y_offset(-DAYS_MONTH * 3)},
    {'label':  '-1m', 'y_offset': days2y_offset(-DAYS_MONTH * 1)},
    {'label':  '-1w', 'y_offset': days2y_offset(   -7)},
    {'label':  '-3d', 'y_offset': days2y_offset(   -3)},

    {'label':  '+3d', 'y_offset': days2y_offset(   +3)},
    {'label':  '+1w', 'y_offset': days2y_offset(   +7)},
    {'label':  '+1m', 'y_offset': days2y_offset(+DAYS_MONTH * 1)},
    {'label':  '+3m', 'y_offset': days2y_offset(+DAYS_MONTH * 3)},
    {'label':  '+1y', 'y_offset': days2y_offset(+DAYS_YEAR * 1)},
    {'label':  '+3y', 'y_offset': days2y_offset(+DAYS_YEAR * 3)},
    {'label': '+10y', 'y_offset': days2y_offset(+DAYS_YEAR * 10)},
    {'label': '+30y', 'y_offset': days2y_offset(+DAYS_YEAR * 30)},
]


class MainHandler(HandlerBase):
    """
    Web request handler
    """
    DEF_DAYS = 45
    SEARCH_MODE_MAX_DAYS = 365 * 5
    SEARCH_MODE_DAYS = 365
    DEF_SEARCH_N = 5

    TODO_DAYS = {'off': -1,
                 'today': 0,
                 '1d': 1,
                 '3d': 3,
                 '1w': 7,
                 '2w': 14,
                 '1m': 30,
                 '1y': 365,
                 'all': 365 * 100
                 }
    DEF_TODO_DAYS = 365

    COOKIE_TODO_DAYS = "todo_days"

    def post(self):
        """ POST """
        self._mylog.debug('request=%s', self.request.__dict__)
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)

        self.get()

    def get(self):
        """ GET method and rendering """
        self._mylog.debug('request=%s', self.request)
        self._mylog.debug('request.path=%s', self.request.path)

        modified_sde_id = self.get_argument('sde_id', '')

        #
        # search_str
        #
        search_str0 = self.get_conf(self.CONF_KEY_SEARCH_STR)
        search_str = self.get_argument('search_str', None)
        if search_str:
            if search_str != search_str0:
                self.set_conf(self.CONF_KEY_SEARCH_STR, search_str)
            else:
                pass

        elif search_str0:
            search_str = search_str0

        else:
            search_str = ''

        self._mylog.debug('search_str=\'%s\'', search_str)

        #
        # command (add/fix/del)
        #
        cmd = self.get_argument('cmd', None)

        modified_date = None
        modified_sde_id = None
        if cmd in ['add', 'fix', 'update', 'del']:
            modified_date, modified_sde_id = self.exec_update(cmd)
            self._mylog.debug('modified_date=%s, modified_sde_id=%s',
                              modified_date, modified_sde_id)

            if cmd not in ['del']:
                sdf = self._sd.get_sdf(modified_date)
                sde = sdf.get_sde(modified_sde_id)
                self._mylog.debug('sde=%s', sde)

                todo_flag = sde.is_todo()
                if todo_flag:
                    modified_date = sde.date

            self._mylog.debug('modified_date=%s', modified_date)

            if cmd in ['update']:
                self.render(self.HTML_EDIT,
                            title=self._title,
                            author=self._author,
                            version=self._version,
                            url_prefix=self._url_prefix,

                            post_url=self._url_prefix,
                            date=modified_date,
                            sde=sde,
                            new_flag=False,
                            todo_flag=todo_flag,
                            search_str=search_str,
                            )
                return

        #
        # set Date
        #
        cur_day = datetime.date.today()  # default

        cur_day_str = self.get_argument('cur_day', None)
        if cur_day_str:
            cur_day = datetime.date.fromisoformat(cur_day_str)
        self._mylog.debug('cur_day=%s', cur_day)

        date = None  # default

        date_str = self.get_argument('date', None)
        self._mylog.debug('date_str=%s', date_str)
        if date_str:
            date = datetime.date.fromisoformat(date_str)

        if modified_date:
            date = modified_date

        year = self.get_argument('year', None)
        month = self.get_argument('month', None)
        day = self.get_argument('day', None)

        if year and month and day:
            date = datetime.date(int(year), int(month), int(day))

        if not date:
            date = cur_day

        self._mylog.debug('date=%s', date)

        #
        # todo_days_value
        #
        todo_days_value0 = self.get_conf(self.CONF_KEY_TODO_DAYS)
        self._mylog.debug('todo_days_value0=%s', todo_days_value0)

        todo_days_value = self.get_argument('todo_days', None)
        if todo_days_value:
            if todo_days_value != todo_days_value0:
                self.set_conf(self.CONF_KEY_TODO_DAYS, todo_days_value)
            else:
                pass

        elif todo_days_value0:
            todo_days_value = todo_days_value0

        else:
            todo_days_value = self.DEF_TODO_DAYS

        todo_days_value = int(todo_days_value)
        self._mylog.debug('todo_days_value=%a', todo_days_value)

        #
        # sde_align
        #
        sde_align = self.get_argument('sde_align', None)
        self._mylog.debug('sde_align=%s', sde_align)
        if not sde_align:
            sde_align = "top"
            self._mylog.debug('[fix]sde_align=%s', sde_align)

        #
        # filter_str
        #
        filter_str0 = self.get_conf(self.CONF_KEY_FILTER_STR)
        self._mylog.debug('filter_str0=%a', filter_str0)
        filter_str = self.get_argument('filter_str', '')
        self._mylog.debug('filter_str=%a', filter_str)
        if filter_str:
            if filter_str != filter_str0:
                self.set_conf(self.CONF_KEY_FILTER_STR, filter_str)
            else:
                pass

        elif filter_str0:
            filter_str = filter_str0

        else:
            filter_str = ''

        filter_str = filter_str.lower()
        self._mylog.debug('filter_str=%a', filter_str)

        #
        # search_str
        #
        search_str0 = self.get_conf(self.CONF_KEY_SEARCH_STR)
        search_str = self.get_argument('search_str', None)
        self._mylog.debug('search_str=\'%s\'', search_str)
        if search_str is not None:
            if search_str != search_str0:
                self.set_conf(self.CONF_KEY_SEARCH_STR, search_str)
            else:
                pass

        elif search_str0:
            search_str = search_str0
        else:
            search_str = ''

        search_str = search_str.lower()
        self._mylog.debug('search_str=\'%s\'', search_str)

        #
        # search_n
        #
        search_n_str0 = self.get_conf(self.CONF_KEY_SEARCH_N)
        search_n_str = self.get_argument('search_n', None)
        if search_n_str is not None:
            if search_n_str != search_n_str0:
                self.set_conf(self.CONF_KEY_SEARCH_N, search_n_str)
            else:
                pass

        elif search_n_str0:
            search_n_str = search_n_str0
        else:
            search_n_str = str(self.DEF_SEARCH_N)

        search_n = int(search_n_str)
        self._mylog.debug('search_n=%s', search_n)

        #
        # load ToDo
        #
        today = datetime.date.today()

        todo_sdf = self._sd.get_sdf(None)
        todo_sde = []  # 後に、日々のスケジュール`out_sde`に統合
        todo_today_sde = []  # 期限は先だが、今日に表示すべきToDo
        for sde in todo_sdf.sde:
            try:
                if filter_str.startswith('!'):
                    if re.search(filter_str[1:], sde.search_str()):
                        continue

                else:
                    if not re.search(filter_str, sde.search_str()):
                        continue

            except re.error as ex:
                self._mylog.warning(
                    '%s:%s:%s:%s',
                    type(ex).__name__, ex,
                    filter_str, sde.search_str())
                continue

            if search_str:
                try:
                    if not re.search(search_str, sde.search_str()):
                        continue

                except re.error as ex:
                    self._mylog.warning(
                        '%s:%s:%s:%s',
                        type(ex).__name__, ex,
                        search_str, sde.search_str())
                    continue

            todo_sde.append(sde)
            self._mylog.debug('sde=%s', sde)

            if sde.date > today + datetime.timedelta(todo_days_value):
                continue

            if sde.date == today:
                continue

            todo_today_sde.append(sde)
            self._mylog.debug('sde=%s', sde)

        #
        # load schedule data
        #
        sched = []
        date_from = date - datetime.timedelta(self._days)
        date_to = date + datetime.timedelta(self._days - 1)

        if search_str:
            date_from = date - datetime.timedelta(
                self.SEARCH_MODE_MAX_DAYS)
            date_from1 = date - datetime.timedelta(
                self.SEARCH_MODE_DAYS)
            date_to = date

        search_count = 0
        delta_day1 = datetime.timedelta(1)
        date1 = date_to + delta_day1
        while date1 > date_from:
            if search_str and search_count > 0:
                if search_count >= search_n:
                    date_from = date1
                    break

                if date1 <= date_from1:
                    date_from = date1
                    break

            date1 -= delta_day1

            sdf = self._sd.get_sdf(date1)

            out_sde = []
            for sde in sdf.sde:
                # self._mylog.debug('sde=%s', sde)
                if filter_str.startswith('!'):
                    try:
                        if re.search(filter_str[1:],
                                      sde.search_str()):
                            continue
                    except re.error as ex:
                        self._mylog.warning(
                            '%s:%s:%s:%s',
                            type(ex).__name__, ex,
                            filter_str, sde.search_str())
                        continue
                else:
                    try:
                        if not re.search(filter_str, sde.search_str()):
                            continue
                    except re.error as ex:
                        self._mylog.warning(
                            '%s:%s:%s:%s',
                            type(ex).__name__, ex,
                            filter_str, sde.search_str())
                        continue

                if search_str:
                    if sde.date == datetime.date(2021, 3, 1):
                        self._mylog.debug('sde.search_str()=%s',
                                          sde.search_str())
                    try:
                        if not re.search(search_str, sde.search_str()):
                            continue
                    except re.error as ex:
                        self._mylog.warning(
                            '%s:%s:%s:%s',
                            type(ex).__name__, ex,
                            search_str, sde.search_str())
                        continue

                out_sde.append(sde)
                search_count += 1

            if todo_days_value >= 0:
                # todo_sde
                for sde in todo_sde:
                    if search_str:
                        if not re.search(search_str, sde.search_str()):
                            continue

                    if sde.date == date1:
                        out_sde.append(sde)
                        self._mylog.debug('out_sde.append:%s', sde)

                # todo_today_sde
                if not search_str:
                    if date1 == datetime.date.today():
                        for sde in todo_today_sde:
                            out_sde.append(sde)

            if search_str and not out_sde:
                continue

            out_sde = sorted(out_sde, key=lambda x: x.get_sortkey())

            sched.append({
                'date': date1,
                'is_holiday': sdf.is_holiday,
                'sde': out_sde
            })

        sched = sched[::-1]

        #
        # render
        #
        self.render(self.HTML_MAIN,
                    title=self._title,
                    author=self._author,
                    version=self._version,
                    url_prefix=self._url_prefix,

                    today=datetime.date.today(),
                    delta_day1=delta_day1,
                    date=date,
                    date_from=date_from,
                    date_to=date_to,
                    sched=sched,
                    modified_sde_id=modified_sde_id,
                    todo_days_list=self.TODO_DAYS,
                    todo_days_value=todo_days_value,
                    filter_str=filter_str,
                    search_str=search_str,
                    search_n=search_n,
                    sde_align=sde_align,
                    sd=self._sd,
                    gage=GAGE,
                    )

    def exec_update(self, cmd: str) -> (datetime.date, str):
        """
        Parameters
        ----------
        cmd: str

        Returns
        -------
        date: datetime.date
            更新された日付
        modified_sde_id: str
            更新されたスケジュールID
        """
        self._mylog.debug('')

        # get orig_date
        orig_date = None
        orig_date_str = self.get_argument('orig_date', None)
        if orig_date_str:
            orig_date = datetime.date.fromisoformat(orig_date_str)

        self._mylog.debug('orig_date=%s', orig_date)

        # get (new) date
        date = None
        date_str = self.get_argument('date', None)
        if date_str:
            date = datetime.date.fromisoformat(date_str)

        self._mylog.debug('date=%s', date)

        # get times
        time_start_str = self.get_argument('time_start', None)
        if time_start_str:
            time_start = datetime.time.fromisoformat(time_start_str)
        else:
            time_start = None

        time_end_str = self.get_argument('time_end', None)
        if time_end_str:
            time_end = datetime.time.fromisoformat(time_end_str)
        else:
            time_end = None

        self._mylog.debug('time_start, time_end: %s-%s',
                          time_start, time_end)

        # get sde_type, title, place
        sde_type = self.get_argument('sde_type', '')
        title = self.get_argument('title', '')
        place = self.get_argument('place', '')
        self._mylog.debug('[%s]%s@%s', sde_type, title, place)

        # get detail
        detail = self.get_argument('detail', '')
        self._mylog.debug('detail:\'%s\'', detail)

        # set deadline_*
        deadline_date_str = self.get_argument('deadline_date', '')
        deadline_time_start_str = self.get_argument(
            'deadline_time_start', '')
        deadline_time_end_str = self.get_argument('deadline_time_end', '')
        if deadline_time_end_str:
            deadline_time_end_str = '-' + deadline_time_end_str
        self._mylog.debug('deadline: %s %s%s',
                          deadline_date_str,
                          deadline_time_start_str, deadline_time_end_str)

        if deadline_date_str and not SchedDataEnt.type_is_todo(sde_type):
            #
            # ToDoが完了した場合
            # ``date``, ``time_start``を現在日時にする
            #
            date = datetime.date.today()
            self._mylog.debug('[fix] date=%s', date)

            time_start = datetime.datetime.now().time()
            # msec を切り捨てる
            time_start = datetime.time.fromisoformat(time_start.strftime('%H:%M'))
            self._mylog.debug('[fix] time_start=%s', time_start)
            time_end = None

            detail = '〆%s %s%s\n%s' % (
                deadline_date_str.replace('-', '/'),
                deadline_time_start_str, deadline_time_end_str,
                detail)
            self._mylog.debug('[fix] detail=%s', detail)

        # sde_id
        sde_id = self.get_argument('sde_id')
        self._mylog.debug('sde_id=%s', sde_id)

        # exec cmd
        self._mylog.debug('EXEC: %s', cmd)

        new_sde = None
        modified_sde_id = None

        if cmd in ['add']:
            sde_id = None

        if cmd in ['del', 'fix', 'update']:
            self.cmd_del(orig_date, sde_id)

        if cmd in ['add', 'fix', 'update']:
            new_sde = self.cmd_add(sde_id, date, time_start, time_end,
                                   sde_type, title, place, detail)

        if new_sde:
            modified_sde_id = new_sde.sde_id
            date = new_sde.date
            if new_sde.is_todo():
                date = None

        self._mylog.debug('date=%s, modified_sde_id=%s',
                          date, modified_sde_id)
        return date, modified_sde_id

    def cmd_add(self, sde_id, date, time_start, time_end,
                sde_type, title, place, detail):
        """
        Parameters
        ----------
        sde_id: str
        date: datetime.date
        time_start, time_end:
        sde_type: str
        title: str
        place: str
        detail: str

        Returns
        -------
        new_sde: SchedDataEnt

        """
        self._mylog.debug('sde_id=%s, date=%s', sde_id, date)

        new_sde = SchedDataEnt(sde_id, date, time_start, time_end,
                               sde_type, title, place, detail,
                               debug=self._dbg)
        if new_sde.is_todo():
            self._sd.add_sde(None, new_sde)
        else:
            self._sd.add_sde(date, new_sde)

        return new_sde

    def cmd_del(self, date, sde_id):
        """
        Parameters
        ----------
        date: datetime.date

        sde_id: str

        """
        self._mylog.debug('date=%s, sde_id=%s', date, sde_id)

        self._sd.del_sde(date, sde_id)
