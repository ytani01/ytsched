# -*- coding: utf-8 -*-
#
# (c) Yoichi Tanibayashi
#
"""
YTスケジューラ
"""
__author__  = 'Yoichi Tanibayashi'
__date__    = '2021/01'

import time
import os
import shutil
import re
import datetime
import collections
from .my_logger import get_logger


def htmlstr2text(intext: str) -> str:
    """
    Parameters
    ----------
    intext: str

    Returns
    -------
    outtext: str

    """
    resub_tbl = {
        r'&amp;#160;': ' ',
        r'&gt;': '>',
        r'&lt;': '<',
        # r'&amp;': '&',
        r'&nbsp:': ' ',
        r'&#160;': ' ',
        r'\<BR *\/*\>': '\n'
    }

    outtext = intext
    # outtext = html2text.html2text(intext)

    outtext = outtext.replace('&nbsp;', ' ')
    outtext = outtext.replace('（', '(')
    outtext = outtext.replace('）', ')')

    for k in resub_tbl:
        # outtext = outtext.replace(k, replace_tbl[k])
        outtext = re.sub(k, resub_tbl[k], outtext, flags=re.IGNORECASE)

    return outtext


def text2htmlstr(intext: str) -> str:
    """
    Parameters
    ----------
    intext: str
        normal text string

    Returns
    -------
    outtext: str
        HTML text
    """
    outtext = intext.rstrip('\n')

#    outtext = outtext.replace('&', '&amp;')
#    outtext = outtext.replace('>', '&gt;')
#    outtext = outtext.replace('<', '&lt;')
#    outtext = outtext.replace(' ', '&nbsp;')

    outtext = outtext.replace('\t', ' ')
    outtext = outtext.replace('\r', '')
    outtext = outtext.replace('\n', '<br />')
    return outtext


class SchedDataEnt:
    """
    スケジュール・データ・エンティティ
    """
    TIME_NULL = ':-:'
    TITLE_NULL = ''

    TYPE_PREFIX_TODO = '□'
    TYPE_HOLYDAY = ['休日', '祝日']

    TITLE_PREFIX_IMPORTANT = ['(重要)', '!', '！', '★', '☆']
    TITLE_PREFIX_CANCELED = [
        '(キャンセル',
        '(欠',
        '(中止',
        '(休',
        '(無効',
        '(不要',
        'x'
    ]

    _mylog = get_logger(__name__, False)

    def __init__(self, sde_id=None,
                 date: datetime.date = datetime.date.today(),
                 time_start: datetime.time = '',
                 time_end: datetime.time = '',
                 sde_type='', title=TITLE_NULL, place='', detail='',
                 debug=False):
        """ Constructor """
        self._dbg = debug
        self.__class__._mylog = get_logger(self.__class__.__name__,
                                           self._dbg)
        self._mylog.debug('(%s)%s %s-%s [%s] %s @%s:\'%s\'',
                          sde_id, date, time_start, time_end,
                          sde_type, title, place, detail)

        self.sde_id = sde_id
        self.date = date
        self.time_start = time_start
        self.time_end = time_end
        self.type = sde_type
        self.title = title
        self.place = place
        self.detail = htmlstr2text(detail)

        if not self.title:
            self.title = self.TITLE_NULL

        if not self.sde_id:
            self.sde_id = SchedDataEnt.new_id()

    def __str__(self):
        """ str(self) """
        out_str = '(%s) ' % (self.sde_id)
        out_str += self.date.strftime('%Y/%m/%d ')

        if self.time_start:
            out_str += self.time_start.strftime('%H:%M-')
        else:
            out_str += ':-'

        if self.time_end:
            out_str += self.time_end.strftime('%H:%M ')
        else:
            out_str += ': '

        out_str += '[%s]' % (htmlstr2text(self.type))
        out_str += '%s' % (htmlstr2text(self.title))
        out_str += '@%s: ' % (htmlstr2text(self.place))
        out_str += htmlstr2text(self.detail)

        return out_str

    def mk_dataline(self):
        """
        ファイル保存用の文字列を生成
        """
        date_str = self.date.strftime('%Y/%m/%d')

        time_start_str = ':'
        if self.time_start:
            time_start_str = self.time_start.strftime('%H:%M')

        time_end_str = ':'
        if self.time_end:
            time_end_str = self.time_end.strftime('%H:%M')

        time_str = time_start_str + '-' + time_end_str
        text_htmlstr = text2htmlstr(self.detail)

        return '\t'.join([self.sde_id, date_str, time_str,
                          self.type, self.title, self.place,
                          text_htmlstr])

    def search_str(self):
        """
        Returns
        -------
        search_str: str

        """
        search_str = '#%s +%s @%s detail:%s' % (
            self.type, self.title, self.place,
            self.detail.replace('\n', ' '))

        return search_str.lower()

    @classmethod
    def new_id(cls):
        sde_id = str(time.time()).replace('.', '-')
        cls._mylog.debug('sde_id=%s', sde_id)
        return sde_id

    @classmethod
    def type_is_todo(cls, sde_type: str) -> bool:
        """
        Parameters
        ----------
        sde_type: str

        """
        cls._mylog.debug('sde_type=%s', sde_type)
        if sde_type:
            return sde_type.startswith(cls.TYPE_PREFIX_TODO)

        return False

    def is_todo(self):
        """
        """
        # self._mylog.debug('')
        if self.type:
            return self.type.startswith(self.TYPE_PREFIX_TODO)

        return False

    def is_holiday(self):
        """
        """
        # self._mylog.debug('')
        if self.type == '':
            return False
        return self.type in self.TYPE_HOLYDAY

    def is_important(self):
        """
        """
        if self.title == '':
            return False
        for start_str in self.TITLE_PREFIX_IMPORTANT:
            if self.title.lower().startswith(start_str):
                return True

        return False

    def is_canceled(self):
        """
        """
        if self.title == '':
            return False

        for start_str in self.TITLE_PREFIX_CANCELED:
            if self.title.lower().startswith(start_str):
                return True

        return False

    def get_sortkey(self):
        """
        """
        sort_key = '%02d%02d%02d %s' % (
            self.date.year, self.date.month, self.date.day,
            self.get_timestr())
        if sort_key.endswith(':-:'):
            if self.is_holiday():
                sort_key = sort_key.replace(':-:', '  :  -  :  ')
            elif self.title.startswith('('):
                sort_key = sort_key.replace(':-:', '99:99-99:99')
            else:
                sort_key = sort_key.replace(':-:', '33:33-33:33')
        # self._mylog.debug('sort_key=\'%s\'', sort_key)
        return sort_key

    def get_date(self):
        """
        Returns
        -------
        (year, month, day)
        """
        return (self.date.year, self.date.month, self.date.day)

    def set_date(self, d: datetime.date = None) -> None:
        """
        Parameters
        ----------
        d: datetime.date

        """
        self._mylog.debug('d=%s', d)

        if d is None:
            self.date = datetime.date.today()
            return

        self.date = d

    def get_timestr(self) -> str:
        """
        Returns
        -------
        'HH:MM-HH:MM' : str
        ':-:', ':-HH:MM', 'HH:MM-'

        """
        time_start_str = ':'
        if self.time_start:
            time_start_str = self.time_start.strftime('%H:%M')

        time_end_str = ':'
        if self.time_end:
            time_end_str = self.time_end.strftime('%H:%M')

        time_str = '%s-%s' % (time_start_str, time_end_str)

        return time_str

    def set_time(self, t1=None, t2=None):
        """
        Parameters
        ----------
        t1: (hour1, minute1)
        t2: (hour2, minute2)
        """
        self._mylog.debug('t1=%s, t2=%s', t1, t2)

        if t1 is None or len(t1) < 2:
            h1 = ''
            m1 = ''
        else:
            h1 = '02d' % t1[0]
            m1 = '02d' % t1[1]

        if t2 is None or len(t2) < 2:
            h2 = ''
            m2 = ''
        else:
            h2 = '02d' % t2[0]
            m2 = '02d' % t2[1]

        self.time = '%s:%s-%s:%s' % (h1, m1, h2, m2)


class SchedDataFile:
    """
    スケジュール・データ・ファイル
    """
    DEF_TOP_DIR = '~/ytsched/data'
    PATH_FORMAT = '%s/%04s/%02s/%02s.cgi'
    TODO_PATH_FORMAT = '%s/ToDo.cgi'

    BACKUP_EXT = '.bak'
    ENCODE = ['utf-8', 'euc_jp']

    def __init__(self, date: datetime.date = None, topdir=DEF_TOP_DIR,
                 debug=False):
        """
        date: datetime.date
            None: ToDo
        topdir: str

        """
        self._dbg = debug
        self._mylog = get_logger(__class__.__name__, self._dbg)
        self._mylog.debug('date=%s, topdir=%s', date, topdir)

        self.date = date
        self.topdir = os.path.expanduser(topdir)

        self.pathname = self.date2path(self.date, self.topdir)

        pl = self.pathname.split('/')
        self.filename = pl.pop()
        self.dirname  = '/'.join(pl)

        self.is_holiday = False
        self.sde = self.load()

    def __str__(self):
        """ __str__ """
        out_str = 'file:%s, sde:%s, holiday:%s' % (
            self.pathname, len(self.sde), self.is_holiday)
        return out_str

    def date2path(self,
                  date: datetime.date = None,
                  topdir: str = DEF_TOP_DIR) -> str:
        """
        Parameters
        ----------
        date: datetime.date
            None: ToDo
        Returns
        -------
        path: str

        """
        if date:
            pathname = self.PATH_FORMAT % (topdir,
                                           date.strftime('%Y'),
                                           date.strftime('%m'),
                                           date.strftime('%d'))
        else:
            pathname = self.TODO_PATH_FORMAT % (topdir)

        return pathname

    def load(self):
        """
        データファイルの読み込み

        Notes
        -----
        初期化時に自動的に実行される

        休日・祝日が含まれる場合は、``is_holiday``をTrueにする
        """
        # self._mylog.debug('')

        self.is_holiday = False
        ok = False
        for enc in self.ENCODE:
            # self._mylog.debug('enc=%s', enc)
            try:
                with open(self.pathname, encoding=enc) as f:
                    lines = f.readlines()
                    ok = True
                    break
            except FileNotFoundError:
                self._mylog.debug('%s: not found .. ignored',
                                  self.pathname)
                return []
            except UnicodeDecodeError:
                self._mylog.debug('%s: decode error .. try next ..', enc)

        if not ok:
            self._mylog.warning('%s: invalid encoding', self.pathname)
            return []

        # self._mylog.debug('lines=%s', lines)
        out = []
        for l in lines:
            d = [htmlstr2text(d1) for d1 in l.split('\t')]
            # self._mylog.debug('d=%s', d)

            date1 = d[1].split('/')
            date2 = datetime.date(int(date1[0]),
                                  int(date1[1]),
                                  int(date1[2]))

            time1 = d[2].split('-')

            time_start1 = time1[0].split(':')
            # self._mylog.debug('time_start1=%s', time_start1)

            time_end1 = time1[1].split(':')
            # self._mylog.debug('time_end1=%s', time_end1)

            if time_start1[0]:
                time_start2 = datetime.time(
                    int(time_start1[0]) % 24, int(time_start1[1]) % 60)
            else:
                time_start2 = ''

            if time_end1[0]:
                time_end2 = datetime.time(
                    int(time_end1[0]) % 24, int(time_end1[1]) % 60)
            else:
                time_end2 = ''

            sde = SchedDataEnt(d[0], date2, time_start2, time_end2,
                               d[3], d[4], d[5], d[6], debug=self._dbg)
            if not self.is_holiday:
                self.is_holiday = sde.is_holiday()
                if self.is_holiday:
                    self._mylog.debug('is_holiday=%s', self.is_holiday)

            out.append(sde)

        out2 = sorted(out, key=lambda x: x.get_sortkey())
        return out2

    def save(self):
        """
        データファイルへ保存

        Notes
        -----
        全て上書きされる。
        ファイルが存在する場合は、バックアップされる。
        """
        self._mylog.debug('')

        if os.path.exists(self.pathname):
            backup_pathname = self.pathname + self.BACKUP_EXT
            shutil.move(self.pathname, backup_pathname)

        os.makedirs(os.path.dirname(self.pathname), exist_ok=True)

        if self.sde:
            with open(self.pathname, mode='w') as f:
                for sde in self.sde:
                    line = sde.mk_dataline()
                    f.write(line + '\n')

    def add_sde(self, sde: SchedDataEnt) -> None:
        """
        Parameters
        ----------
        sde: SchedDataEnt

        """
        self._mylog.debug('sde=%s', sde)
        self.sde.append(sde)
        self.sde = sorted(self.sde, key=lambda x: x.get_sortkey())

    def del_sde(self, sde_id: str = None) -> None:
        """
        Parameters
        ----------
        sde_id: str

        """
        self._mylog.debug('sde_id=%s', sde_id)
        for sde in self.sde:
            if sde.sde_id == sde_id:
                self._mylog.debug('DEL:%s', sde)
                self.sde.remove(sde)
                break

        for sde in self.sde:
            self._mylog.debug('%s', sde)

    def get_sde(self, sde_id: str = None) -> SchedDataEnt:
        """
        Parameters
        ----------
        sde_id: str

        Returns
        -------
        sde: SchedDataEnt

        """
        self._mylog.debug('sde_id=%s', sde_id)

        for sde in self.sde:
            if sde_id == sde.sde_id:
                return sde

        return None


class SchedData:
    """ スケジュール・データ

    SchedDataFile をキャッシングする

    _sdf_cache = {
        date1: sdf1,
        date2: sdf2,
        :
    }

    date1, date2, .. : datetime.date
    sdf1, sf2, ..    : SchedDataFile

    """
    DEF_CACHE_SIZE = 20000
    CACHE_DISCARD_RATE = 0.1

    _mylog = get_logger(__name__, False)

    def __init__(self,
                 topdir: str = SchedDataFile.DEF_TOP_DIR,
                 cache_size: int = DEF_CACHE_SIZE,
                 debug=False):
        """ Constructor
        Parameters
        ----------
        cache_size: int

        """
        self._dbg = debug
        self._mylog = get_logger(self.__class__.__name__, self._dbg)
        self._mylog.debug('cache_size=%s, topdir=%s', cache_size, topdir)

        self._cache_size = cache_size
        self._topdir = topdir

        self._sdf_cache = collections.OrderedDict()

    def __str__(self):
        """ __str__ """
        out_str = 'topdir:%s, cache_size:%s' % (
            self._topdir, len(self._sdf_cache))
        return out_str

    def get_keys(self):
        """
        Returns
        -------
        date_list: list of str ['2021-01-01', '2021-01-02', .. ]
        
        """
        date_list = []
        for k in self._sdf_cache.keys():
            date_list.append('%s' % k)

        return date_list

    def get_cache_size(self):
        return len(self._sdf_cache)

    def get_sdf(self, date: datetime.date = None) -> SchedDataFile:
        """
        キャッシュがヒットすれば、そのデータを返す。
        ヒットしなければ、読み込む。

        Parameters
        ----------
        date: datetime.date

        topdir: str

        Returns
        -------
        sdf: SchedDataFile

        """
        # self._mylog.debug('date=%s', date)

        try:
            # self._mylog.debug('_sdf.keys=%s', self.get_keys())
            sdf = self._sdf_cache.pop(date)
            self._sdf_cache[date] = sdf
            # self._mylog.debug('_sdf.keys=%s', self.get_keys())
        except KeyError:
            self._mylog.warning('cache miss: date=%s', date)

            if self.get_cache_size() >= self._cache_size:
                discard_size = int(
                    self._cache_size * self.CACHE_DISCARD_RATE)
                for i in range(discard_size):
                    sdf = self._sdf_cache.popitem(last=False)
                    # self._mylog.debug('discard[%s/%s]: date=%s',
                    #                   i + 1, discard_size, sdf[0])

            sdf = SchedDataFile(date, self._topdir, debug=self._dbg)
            self._sdf_cache[date] = sdf
            # self._mylog.debug('_sdf.keys=%s', self.get_keys())

        # if not sdf.sde:
            # self._mylog.warning('%s sdf.sde=%s', date, sdf.sde)

        return sdf

    def get_sde(self, date: datetime.date = None, sde_id: str = ''
                ) -> SchedDataEnt:
        """
        Parameters
        ----------
        date: datetime.date

        topdir: str

        sde_id: str


        Returns
        -------
        sde: SchedDataEnt

        """
        self._mylog.debug('date=%s, sde_id=%s', date, sde_id)

        sdf = self.get_sdf(date)
        sde = sdf.get_sde(sde_id)
        self._mylog.debug('sde=%s', sde)
        return sde

    def add_sde(self,
                date: datetime.date = None,
                sde: SchedDataEnt = None) -> None:
        """
        Parameters
        ----------
        sde: SchedDataEnt

        """
        self._mylog.debug('date=%s, sde=%s', date, sde)

        sdf = self.get_sdf(date)
        sdf.add_sde(sde)
        sdf.save()

    def del_sde(self, date: datetime.date = None, sde_id: str = ''
                ) -> None:
        """ del_sde

        Parameters
        ----------
        date: datetime.date

        topdir: str

        sde_id: str

        """
        self._mylog.debug('date=%s, sde_id=%s', date, sde_id)

        sdf = self.get_sdf(date)
        sdf.del_sde(sde_id)
        sdf.save()
