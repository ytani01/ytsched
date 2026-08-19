#!/bin/sh -e
#
# install script
#
#   (c) 2021 Yoichi Tanibayashi
#
############################################################
help() {
    cat <<'END'

[インストール後のディレクトリ構造]

 $HOME/ ... ホームディレクトリ
    |
    +- bin/ .. BINDIR シェルスクリプトなど
    |   |
    |   +- Ytsched .. WRAPPER_SCRIPT
    |   +- boot-Ytsched.sh .. 起動スクリプト
    |
    +- ytsched/ .. WORKDIR
    |   |
    |   +- log/ .. LOGDIR
    |   |
    |   +- webroot/ .. WEBROOT
    |   |   |
    |   |   +- templates/
    |   |   +- static/
    |   |       |
    |   |       +- css/
    |   |       +- js/
    |   |       +- images/
    |   |       :
    |   +- env/ .. VENVDIR
    |   |
    |   +- upload/
    |   +- data/ .. DATADIR
    |   :   |
    |   :   +- todo.txt
    |   :   +- 2021/
    |   :   :
    |
    +- env1/ .. python3 Virtualenv(venv) for build 【ユーザが作成する】
        |
        +- ytsched2/ .. MYDIR
        |   |
        |   +- build/ .. BUILD_DIR
        |
        +- subpackage1/
        |
        :

END
}

############################################################
MYNAME=`basename $0`
cd `dirname $0`
MYDIR=`pwd`
echo "MYDIR=$MYDIR"


MY_PKG="ytsched"
WRAPPER_SCRIPT="Ytsched"


echo "MY_PKG=$MY_PKG"
echo "WRAPPER_SCRIPT=$WRAPPER_SCRIPT"

WRAPPER_SRC="$WRAPPER_SCRIPT.src"
echo "WRAPPER_SRC=$WRAPPER_SRC"

BINDIR="$HOME/bin"
mkdir -pv $BINDIR

WORKDIR="$HOME/$MY_PKG"
echo "WORKDIR=$WORKDIR"

VENVDIR="$WORKDIR/env"
echo "VENVDIR=$VENVDIR"

WEBROOT="$WORKDIR/webroot"
echo "WEBROOT=$WEBROOT"

LOGDIR="$WORKDIR/log"
echo "LOGDIR=$LOGDIR"

DATADIR="$WORKDIR/data"
echo "DATADIR=$DATADIR"

PKGS_TXT="pkgs.txt"

GITHUB_TOP="git@github.com:ytani01"

CUILIB_PKG="cuilib"
CUILIB_DIR="CuiLib"
CUILIB_GIT="${GITHUB_TOP}/${CUILIB_DIR}.git"

BUILD_DIR="$MYDIR/build"

INSTALLED_FILE="$BUILD_DIR/installed"

FAST_MODE=0

#
# fuctions
#
cd_echo() {
    cd $1
    echo "### [ `pwd` ]"
    echo
}

install_python_pkg_from_git() {
    _PKG=$1
    _DIR=$2
    _GIT=$3

    cd_echo $VIRTUAL_ENV

    echo "### install/update $_PKG"
    echo

    if [ ! -d $_DIR ]; then
        git clone $_GIT || exit 1
    fi

    cd_echo ./$_DIR
    git pull
    pip install .
    echo
}

usage() {
    echo
    echo "  Usage: $MYNAME [-f] [-u] [-h]"
    echo
    echo "    -f  fast mode"
    echo "    -u  uninstall"
    echo "    -c  clean"
    echo "    -h  show this usage"
    echo
}

uninstall() {
    cd_echo $MYDIR

    if [ -f $INSTALLED_FILE ]; then
        echo "### remove installed files"
        echo
        rm -fv `cat $INSTALLED_FILE`
        echo
    fi

    echo "### remove build/"
    echo
    rm -rfv build
    echo

    echo "### $WORKDIR"
    echo
    if [ -d $WORKDIR ]; then
        rm -rfv $WEBROOT
        echo
        
        if [ -d $DATADIR ]; then
            echo "DATADIR=$DATADIR: exists .. Important !!"
        fi
        if [ -d $LOGDIR ]; then
            echo "LOGDIR=$LOGDIR: exists"
        fi
    fi
    echo
    
}

clean() {
    cd_echo $MYDIR

    echo "### clean"
    echo

    rm -rfv build dist *.egg-info
}

#
# main
#
cd_echo $MYDIR

while getopts fuch OPT; do
    case $OPT in
	f) FAST_MODE=1;;
        u) uninstall; exit 0;;
        c) clean; exit 0;;
        h) help; echo "#####"; usage; exit 0;;
        *) usage; exit 1;;
    esac
    shift
done

#
# install Linux packages
#
if [ -f $PKGS_TXT ]; then
    PKGS=`cat $PKGS_TXT`
    if [ ! -z $PKGS ]; then
        echo "### install Linux packages"
        echo
        sudo apt install `cat $PKGS_TXT`
        echo
    fi
fi

#
# work dirs
#
for d in $WORKDIR $WEBROOT $LOGDIR; do
    echo "### $d"
    echo
    if [ ! -d $d ]; then
        mkdir -pv $d
        echo
    fi
done

if [ -d $DATADIR ]; then
    BACKDIR="$DATADIR.bak"

    if [ $FAST_MODE -eq 0 -a -d $BACKDIR ]; then
        echo "$BACKDIR exists: move/copy/remove by yourself"
        echo
        exit 1
    fi
    echo "### backup $DATADIR to $BACKDIR"
    cp -rfv $DATADIR $BACKDIR
fi

#
# venv
#
cd_echo $WORKDIR

SUBDIR=`basename $VENVDIR`

if [ ! -f $VENVDIR/bin/activate ]; then
    rm -rfv $SUBDIR
fi
if [ ! -d $VENVDIR ]; then
    python3 -m venv `basename $VENVDIR`
fi
. $VENVDIR/bin/activate
echo "VIRTUAL_ENV=$VIRTUAL_ENV"
echo

#
# update pip, setuptools, and wheel
#
echo "### insall/update pip etc. .."
echo
pip install -U pip setuptools wheel
hash -r
echo
pip -V
echo

#
# install my python packages
#
#install_python_pkg_from_git $CUILIB_PKG $CUILIB_DIR $CUILIB_GIT

#
# install my package
#
cd_echo $MYDIR
echo "### install my python package"
echo
pip install .
echo

#
# version
#
cd_echo $MYDIR
MY_VERSION=`python setup.py --version`
echo "MY_VERSION=$MY_VERSION"
echo

#
# make $WRAPPER_SCRIPT
#
cd_echo $MYDIR

mkdir -pv $BUILD_DIR
echo -n > $INSTALLED_FILE
echo

echo "### build $WRAPPER_SCRIPT"

sed -e "s?%%% MY_PKG %%%?$MY_PKG?" \
    -e "s?%%% MY_VERSION %%%?$MY_VERSION?" \
    -e "s?%%% VENVDIR %%%?$VIRTUAL_ENV?" \
    -e "s?%%% WORKDIR %%%?$WORKDIR?" \
    -e "s?%%% WEBROOT %%%?$WEBROOT?" \
    -e "s?%%% DATADIR %%%?$DATADIR?" \
    $WRAPPER_SRC > $BUILD_DIR/$WRAPPER_SCRIPT

chmod +x $BUILD_DIR/$WRAPPER_SCRIPT
echo $BUILD_DIR/$WRAPPER_SCRIPT >> $INSTALLED_FILE

echo '-----'
cat $BUILD_DIR/$WRAPPER_SCRIPT | sed -n -e '1,/\#* main/p'
echo '  :'
echo '-----'
echo

#
# install scripts
#
echo "### install scripts"
echo
cp -fv $BUILD_DIR/$WRAPPER_SCRIPT $BINDIR
echo $BINDIR/$WRAPPER_SCRIPT >> $INSTALLED_FILE
echo

#
# install webroot
#
if [ ! -z $WEBROOT ]; then
    cd_echo $MYDIR/webroot
    cp -rfv * $WEBROOT
    echo
fi

#
# display usage
#
echo "### usage"
echo
$WRAPPER_SCRIPT -h
echo
