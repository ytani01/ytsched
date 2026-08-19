#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
EditHandler
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import datetime
from .handler import HandlerBase
from .ytsched import SchedDataEnt


class EditHandler(HandlerBase):
    """
    Web request handler
    """
    def get(self, date=None, sde_id=None, todo_flag=False):
        """
        ``date``の優先順位
          1. Parameter
          2. getargument('date')
          3. today()

        ``sde_id``の優先順位
          1. Parameter
          2. getargument('sde_id')
          3. SchedDataEnt.new_id()

        Parameters
        ----------
        date: datetime.date

        sde_id: str

        todo_flag: bool

        """
        self._mylog.debug('date=%s, sde_id=%s, todo_flag=%s',
                          date, sde_id, todo_flag)
        self._mylog.debug('request=%s', self.request)
        self._mylog.debug('request.path=%s', self.request.path)

        #
        # date
        #
        if not date:
            date_str = self.get_argument('date', None)

            if date_str:
                date = datetime.date.fromisoformat(date_str)

        if not date:
            date = datetime.date.today()

        #
        # search_str
        #
        search_str = self.get_argument('search_str', None)
        self._mylog.debug('search_str=%s', search_str)

        #
        # sde_id
        #
        if not sde_id:
            sde_id = self.get_argument('sde_id', None)

        #
        # todo_flag
        #
        todo_flag = self.get_argument('todo_flag', False)
        if todo_flag == 'true':
            todo_flag = True
        else:
            todo_flag = False

        self._mylog.debug('date=%s, sde_id=%s, todo_flag=%s',
                          date, sde_id, todo_flag)

        #
        # sde
        #
        new_flag = False

        if sde_id:
            if todo_flag:
                sdf = self._sd.get_sdf(None)
            else:
                sdf = self._sd.get_sdf(date)

            sde = sdf.get_sde(sde_id)

        else:
            sde = SchedDataEnt('', date, debug=self._dbg)
            self._mylog.debug('sde_id=%s', sde.sde_id)
            new_flag = True

        self.render(self.HTML_EDIT,
                    title=self._title,
                    author=self._author,
                    version=self._version,

                    url_prefix=self._url_prefix,
                    post_url=self._url_prefix,
                    date=date,
                    sde=sde,
                    new_flag=new_flag,
                    todo_flag=todo_flag,
                    search_str=search_str,
                    )

    def post(self):
        """
        """
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)
        self.get()
