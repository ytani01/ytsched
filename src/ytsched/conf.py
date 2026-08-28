#
# (c) 2026 ytani01
#
"""
ConfFile: ``conf.json`` の読み書き
"""

__author__ = "ytani01"
__date__ = "2026/08"

import json
import os
from pathlib import Path

from .mylog import getLogger


class ConfFile:
    """``conf.json`` のキャッシュ付き読み書き (TODO-090)。

    ``SchedUpdater``/``SchedLoader`` と同じく tornado を知らないクラス。
    ``WebServer`` が 1 つだけ作り、全ハンドラで使い回す
    (``SchedData`` と同じ持ち方)。

    外部からの書き換えの検出は ``SchedDataFile.is_stale()`` と同じ
    やり方 (``Path.stat()`` の ``st_mtime``/``st_size`` の組)。未保存の
    変更 (``set()`` してから ``save_if_dirty()`` するまでの間) が
    あるうちは、``refresh()`` しても読み直さない (読み直すと、その
    変更が消えるため)。
    """

    __log = getLogger(__qualname__)

    FNAME = "conf.json"
    ENCODING = "utf-8"

    def __init__(self, pathname: str | Path):
        """Constructor

        Parameters
        ----------
        pathname: str | Path
            ``conf.json`` のパス

        """
        self.pathname = Path(pathname)

        self._conf: dict[str, str] = {}
        self._stat_key: tuple[float, int] | None = None
        self._dirty = False

        self._load()

    def _load(self) -> None:
        """``conf.json`` を読み込んで ``self._conf`` へ入れる。

        ファイルが無ければ空の dict にする。**JSON として読めなくても
        例外にしない。** 壊れている場合やトップレベルが object でない
        場合は、警告を 1 行出して空の dict にする。値が文字列でない
        キーは、そのキーだけ飛ばす。不正な正規表現の扱い
        (TODO-012)、不正な引数の扱い (TODO-027) と同じ考え方
        (設定ファイルが壊れて画面が出ないほうが困る)。

        ファイルそのものが読めない場合 (``PermissionError`` など) は
        捕まえない。設定の中身の問題ではなく、直すべき環境の問題なので、
        黙って既定値で動かない (TODO-032)。
        """
        self.__log.debug("")

        try:
            with self.pathname.open(mode="rb") as f:
                raw = f.read()
                st = os.fstat(f.fileno())
        except FileNotFoundError:
            self._conf = {}
            # ``None`` は「無い」ことを表す。あとでファイルができれば
            # ``Path.stat()`` の結果と食い違うので、``is_stale()`` が
            # 読み直しが要ると判断できる (``SchedDataFile`` と同じ。
            # TODO-080)
            self._stat_key = None
            return

        # 読んだ fd から ``fstat()`` するので、読んだ内容とずれない
        self._stat_key = (st.st_mtime, st.st_size)

        try:
            text = raw.decode(self.ENCODING)
            data = json.loads(text)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.__log.warning(f"{self.pathname}: {e} .. ignored")
            self._conf = {}
            return

        if not isinstance(data, dict):
            self.__log.warning(f"{self.pathname}: not an object .. ignored")
            self._conf = {}
            return

        # JSON の object のキーは必ず文字列
        conf: dict[str, str] = {}
        loaded: dict[str, object] = data
        for param, value in loaded.items():
            if not isinstance(value, str):
                self.__log.warning(
                    f"{self.pathname}: {param!a}={value!a}:"
                    " not a string .. ignored"
                )
                continue

            self.__log.debug(f"{param!a},{value!a}.")
            conf[param] = value

        self._conf = conf

    def is_stale(self) -> bool:
        """読み込んだあとに、ファイルが外部で書き換えられたか
        (``SchedDataFile.is_stale()`` と同じやり方。TODO-090)。

        Returns
        -------
        bool

        """
        try:
            st = self.pathname.stat()
        except OSError:
            current_key = None
        else:
            current_key = (st.st_mtime, st.st_size)

        return current_key != self._stat_key

    def refresh(self) -> None:
        """変わっていれば読み直す。1 リクエストごとに 1 回呼ばれる想定
        (``HandlerBase.__init__``。TODO-090)。

        未保存の変更 (``_dirty``) があるうちは読み直さない。
        """
        if self._dirty:
            return

        if self.is_stale():
            self.__log.debug(f"reload (stale): {self.pathname}")
            self._load()

    def get(self, name: str) -> str | None:
        """設定値を返す。無ければ ``None`` を返す。"""
        self.__log.debug(f"name={name}")

        return self._conf.get(name)

    def set(self, name: str, value: str) -> None:
        """設定値を変更する。``conf.json`` へはまだ書かない
        (``save_if_dirty()`` が書く。TODO-090)。
        """
        self.__log.debug(f"name={name}, value='{value}'")

        if self._conf.get(name) == value:
            return

        self._conf[name] = value
        self._dirty = True

    def save_if_dirty(self) -> None:
        """変更があれば ``conf.json`` へ書き出す。無ければ何もしない
        (``HandlerBase.on_finish()`` から、リクエストの終わりに 1 回
        だけ呼ばれる想定。TODO-090)。

        ``_save()`` が失敗しても (``PermissionError`` など) 例外は
        外へ出さない。**``ConfFile`` は 1 プロセスに 1 つを全リクエスト
        で共有する**ので、ここで ``_dirty`` を ``False`` に戻さずに
        例外を伝えると、``refresh()`` が ``if self._dirty: return`` で
        以後ずっと止まり（外部の書き換えを二度と拾えなくなる）、
        ``set_conf()`` を呼んでいないリクエストでも ``on_finish()`` の
        たびに書き込みを再試行して失敗し続ける
        (TODO-090 のレビューで指摘)。

        書けなかった値はメモリ上の ``self._conf`` に残したまま
        （失われない）、``_dirty`` だけ ``False`` に戻す。``_stat_key`` は
        書き込みが実際には起きていないので持ち直さない（あとで外部から
        書き換えられれば ``refresh()`` が読み直せる）。書けなかったこと
        自体は、不正な正規表現の扱い (TODO-012)・設定ファイルが壊れて
        いる場合の扱い (TODO-032) と同じ考え方で、警告を 1 行出す
        だけにして 500 にはしない（``conf.json`` は設定だけなので、
        書けなくても画面は出したほうがよい）。
        """
        if not self._dirty:
            return

        try:
            self._save()
        except OSError as e:
            self.__log.warning(f"{self.pathname}: {e} .. not saved")

        self._dirty = False

    def _save(self) -> None:
        """``conf.json`` へ書き出す。

        書いたあとの ``_stat_key`` はここで持ち直す
        (``SchedDataFile.save()`` と同じ。TODO-090)。
        """
        self.__log.debug("")

        with self.pathname.open(mode="w", encoding=self.ENCODING) as f:
            json.dump(self._conf, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            st = os.fstat(f.fileno())
            self._stat_key = (st.st_mtime, st.st_size)

    def to_dict(self) -> dict[str, str]:
        """テストなどで中身をまとめて見るための dict (コピー)。"""
        return dict(self._conf)
