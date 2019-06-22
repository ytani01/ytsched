#!/usr/bin/env python3
#
# (c) Yoichi Tanibayashi
#
'''
YTスケジューラ
'''
__author__  = 'Yoichi Tanibayashi'
__date__    = '2019'
__version__ = '0.0.2'

import time
import os, shutil

#####
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
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('')
        
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
        self.logger.debug('')
        return '\t'.join((self.sde_id, self.sde_date, self.sde_time,
                          self.sde_type, self.sde_title, self.sde_place,
                          self.sde_text))

    def print1(self):
        self.logger.debug('')

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
        self.logger.debug('')
        sde_id = str(time.time()).replace('.','-')
        return sde_id

    def is_todo(self):
        self.logger.debug('')
        if self.sde_type == '':
            return False
        return self.sde_type.startswith(self.TYPE_PREFIX_TODO)

    def is_holiday(self):
        self.logger.debug('')
        if self.sde_type == '':
            return False
        return self.sde_type in self.TYPE_HOLYDAY

    def is_important(self):
        self.logger.debug('')
        if self.sde_title == '':
            return False
        return self.sde_title[0] in self.TITLE_PREFIX_IMPORTANT

    def get_date(self):
        '''
        Returns
        -------
        (year, month, day)
        '''
        self.logger.debug('')
        return [int(i) for i in self.sde_date.split('/')]

    def set_date(self, d=None):
        '''
        d = (year, month, day)
        '''
        self.logger.debug('d=%s', d)

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
        self.logger.debug('')

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
        self.logger.debug('t1=%s, t2=%s', t1, t2)

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


#####
class SchedDataFile:
    '''
    スケジュール・データ・ファイル
    '''
    
    DEF_TOP_DIR     = '/home/ytani/ytsched/data'
    PATH_FORMAT = '%s/%04d/%02d/%02d.cgi'
    BACKUP_EXT  = '.bak'
    ENCODE      = ['utf-8', 'euc_jp']
    
    def __init__(self, y=None, m=None, d=None, topdir=DEF_TOP_DIR,
                 debug=False):
        self.debug  = debug
        self.logger = get_logger(__class__.__name__, debug=self.debug)
        self.logger.debug('y/m/d = %s/%s/%s', y, m, d)
        
        self.topdir = topdir
        self.y      = y
        self.m      = m
        self.d      = d

        self.pathname = self.date2path(self.y, self.m, self.d, self.topdir)

        pl = self.pathname.split('/')
        self.filename = pl.pop()
        self.dirname  = '/'.join(pl)
        
        self.sde_list = self.load()

    def date2path(self, y, m, d, topdir=''):
        self.logger.debug('y/m/d = %s/%s/%s', y, m, d)

        if topdir == '':
            topdir = self.topdir
            
        return self.PATH_FORMAT % (topdir, self.y, self.m, self.d)

    def load(self):
        '''
        データファイルの読み込み

        Notes
        -----
        初期化時に自動的に実行される
        '''
        self.logger.debug('')
        
        ok = False
        for e in self.ENCODE:
            try:
                f = open(self.pathname, encoding=e)
            except FileNotFoundError:
                self.logger.warn('%s: not found', self.pathname)
                return []
            
            try:
                lines = f.readlines()
            except UnicodeDecodeError:
                self.logger.info('%s: decode error', e)
                f.close()
                continue
            else:
                f.close()
                ok = True

        if not ok:
            self.logger.warn('%s: invalid encoding', self.pathname)
            return []
        
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
        self.logger.debug('')
        
        if os.path.exists(self.pathname):
            backup_pathname = self.pathname + BACKUP_EXT
            shutil.move(self.pathname, backup_pathname)
            
        f = open(self.pathname, mode='w')
        for sde in self.sde_list:
            line = self.mk_dataline(sde)
            f.write(line)
        f.close()
    

#####
class Sample:
    def __init__(self, yyyy, mm, dd, topdir='', debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('')

        self.sdf = SchedDataFile(yyyy, mm, dd, topdir=topdir,
                                 debug=self.debug)

    def main(self):
        self.logger.debug('')

        if self.sdf.sde_list == []:
            print('===== No data =====')

        else:
            for sde in self.sdf.sde_list:
                sde.print1()

    def end(self):
        self.logger.debug('')
       

#####
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('year', type=int, default=2019)
@click.argument('month', type=int, default=1)
@click.argument('day', type=int, default=1)
@click.option('--data-dir', '--dir', 'dirname', type=click.Path(), default='',
              help='data directory')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(year, month, day, dirname, debug):
    logger = get_logger(__name__, debug)
    logger.info('%d/%d/%d', year, month, day)
    logger.info('dirname=%s', dirname)
    logger.info('debug=%s', debug)

    app = Sample(year, month, day, topdir=dirname, debug=debug)
    try:
        app.main()
    finally:
        app.end()
        
if __name__ == '__main__':
    main()
