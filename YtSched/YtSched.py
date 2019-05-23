#!/usr/bin/env python3
#
# (c) Yoichi Tanibayashi
#

'''
YTスケジューラー
'''
__author__  = 'Yoichi Tanibayashi'
__date__    = '2019/05/24'
__version__ = '0.0.1'

import sys
import time
import os, shutil

my_name = sys.argv.pop(0)

class SchedDataEnt:
    '''
    スケジュール・データ・エントリー    
    '''
    TIME_NULL              = ':-:'
    TYPE_PREFIX_TODO       = '□'
    TYPE_HOLYDAY           = ['休日', '祝日']
    TITLE_PREFIX_IMPORTANT = ['★', '☆']

    def __init__(self, sde_id='', sde_date='', sde_time='',
                 sde_type='', sde_title='', sde_place='', sde_text='',
                 debug=False):
        self.debug = debug

        self.sde_id    = sde_id
        self.sde_date  = sde_date
        self.sde_time  = sde_time
        self.sde_type  = sde_type
        self.sde_title = sde_title
        self.sde_place = sde_place
        self.sde_text  = sde_text

        if self.sde_id == '':
            self.sde_id = self.new_id()

        if self.sde_date == '':
            lt = time.localtime()
            self.sde_date = '%04d/%02d/%02d' % (lt.tm_year,
                                                lt.tm_mon,
                                                lt.tm_mday)

        if self.sde_time == '':
            self.sde_time = self.TIME_NULL

    def mk_dataline(self):
        '''
        ファイル保存用の文字列を生成
        '''
        return '\t'.join((self.sde_id, self.sde_date, self.sde_time,
                          self.sde_type, self.sde_title, self.sde_place,
                          self.sde_text))

    def print1(self):
        print('=====')
        print('ID=%s' % self.sde_id)
        print('%s, %s' % (self.sde_date, self.sde_time))
        print('[%s]%s@%s' % (self.sde_type, self.sde_title, self.sde_place))
        if self.is_todo():
            print('*ToDo')
        if self.is_holiday():
            print('*Holiday')
        if self.is_important():
            print('*Important')
        print('-----')
        print('%s' % self.sde_text)

    def new_id(self):
        sde_id = str(time.time()).replace('.','-')
        return sde_id

    def is_todo(self):
        if self.sde_type == '':
            return False
        return self.sde_type.startswith(self.TYPE_PREFIX_TODO)

    def is_holiday(self):
        if self.sde_type == '':
            return False
        return self.sde_type in self.TYPE_HOLYDAY

    def is_important(self):
        if self.sde_title == '':
            return False
        return self.sde_title[0] in self.TITLE_PREFIX_IMPORTANT

    def get_date(self):
        '''
        Returns
        -------
        (year, month, day)
        '''
        return [int(i) for i in self.sde_date.split('/')]

    def set_date(self, d=None):
        '''
        d = (year, month, day)
        '''
        if d == None or len(d) < 3:
            lt = time.localtime()
            yyyy = lt.tm_year
            mm = lt.tm_month
            dd = lt.tm_mday
        else:
            (yyyy, mm, dd) = d

        self.sde_date = '%04d/%02d/%02d' % (yyyy, mm, dd)
        

    def get_time(self):
        '''
        Returns
        -------
        ((hour1, minute1), (hour2, minute2))

        if not specified, return None
        ex.
        ((houre1, minute2), None)
        (None, (hour2, minute2))
        (None, None)

        '''
        (t1, t2) = self.sde_time.split('-')
        if t1 == ':':
            t1 = None
        else:
            (h1, m1) = t1.split(':')
            t1 = (int(h1), int(m1))

        if t2 == ':':
            t2 = None
        else:
            (h2, m2) = t2.split(':')
            t2 = (int(h2), int(m2))

        return (t1, t2)

    def set_time(self, t1=None, t2=None):
        '''
        t1 = (hour1, minute1)
        t2 = (hour2, minute2)
        '''
        if t1 == None or len(t1) < 2:
            h1 = ''
            m1 = ''
        else:
            h1 = '02d' % t1[0]
            m1 = '02d' % t1[1]
        if t2 == None or len(t2) < 2:
            h2 = ''
            m2 = ''
        else:
            h2 = '02d' % t2[0]
            m2 = '02d' % t2[1]

        self.sde_time = '%s:%s-%s:%s' % (h1, m1, h2, m2)


class SchedDataFile:
    '''
    スケジュール・データ・ファイル
    '''
    
    TOP_DIR     = '/home/pi/work'
    PATH_FORMAT = '%s/%04d/%02d/%02d.cgi'
    BACKUP_EXT  = '.bak'
    ENCODE      = ['utf-8', 'euc_jp']
    
    def __init__(self, y=None, m=None, d=None, topdir=TOP_DIR,
                 debug=False):
        self.debug  = debug
        
        self.topdir = topdir
        self.y      = y
        self.m      = m
        self.d      = d

        self.pathname = self.date2path(self.y, self.m, self.d, self.topdir)

        pl = self.pathname.split('/')
        self.filename = pl.pop()
        self.dirname  = '/'.join(pl)
        
        sde_list = self.load()

    def date2path(self, y, m, d, topdir=TOP_DIR):
        return self.PATH_FORMAT % (self.topdir, self.y, self.m, self.d)

    def load(self):
        '''
        データファイルの読み込み

        Notes
        -----
        初期化時に自動的に実行される
        '''
        ok = False
        for e in self.ENCODE:
            f = open(self.pathname, encoding=e)
            try:
                lines = f.readlines()
            except UnicodeDecodeError:
                f.close()
                continue
            else:
                f.close()
                ok = True

        if not ok:
            return None
        
        out = []
        for l in lines:
            d = l.split('\t')
            sde = SchedDataEnt(*d, debug=self.debug)
            out.append(sde)

        return out


    def save(self):
        '''
        データファイルへ保存

        Notes
        -----
        全て上書きされる。
        ファイルが存在する場合は、バックアップされる。
        '''
        if os.path.exists(self.pathname):
            backup_pathname = self.pathname + BACKUP_EXT
            shutil.move(self.pathname, backup_pathname)
            
        f = open(self.pathname, mode='w')
        for sde in self.sde_list:
            line = self.mk_dataline(sde)
            f.write(line)
        f.close()
    

###########
enc_list = ['utf-8', 'euc_jp']
def read_datafile(filename):
    ok = False
    for e in enc_list:
        print('e =', e)
        fo = open(filename, encoding=e)
        try:
            l = fo.readlines()
        except UnicodeDecodeError:
            fo.close()
            continue
        else:
            fo.close()
            ok = True
            break

    if ok:
        out = []
        for l1 in l:
            sd = l1.split('\t')
            sde = SchedDataEnt(*(l1.split('\t')))
            out.append(sde)
    else:
        out = None
    return out


file_names = sys.argv
for f1 in file_names:
    print('file:', f1)
    sched_data = read_datafile(f1)
    if sched_data == None:
        print('Error!')
        continue

    print('n=', len(sched_data))
    for d1 in sched_data:
        d1.print1()
