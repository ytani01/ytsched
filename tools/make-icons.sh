#!/bin/sh
#
# (c) 2026 Yoichi Tanibayashi
#
# アイコン画像を SVG から作り直す (TODO-039)。
#
# 元は static/icons/icon.svg 1 つだけ。角丸を落として全面を青で塗った版
# （iOS 用）と、中身を 85% に縮めた版（Android の maskable 用）は、
# この中で sed を当てて作る。デザインを直すときは icon.svg だけ直す。
#
# ImageMagick 6 の convert が要る（内蔵の SVG レンダラを使う）。
#
set -eu

cd "$(dirname "$0")/.."

STATIC="src/ytsched/webroot/static"
ICONS="${STATIC}/icons"
SRC="${ICONS}/icon.svg"
BG="#4488CC"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

# 角丸を落として全面を塗り、中身を $1 倍にした SVG を作る。
# 中身の中心は (256, 252) なので、そこを (256, 256) へ寄せてから縮める。
mk_square_svg() {
    scale="$1"
    out="$2"
    tr='translate(256,256)'" scale(${scale}) "'translate(-256,-252)'
    sed -e 's/rx="96" ry="96"/rx="0" ry="0"/' \
        -e "s|<g id=\"calendar\">|<g id=\"calendar\" transform=\"${tr}\">|" \
        "${SRC}" > "${out}"
}

mk_square_svg 1 "${TMPDIR}/square.svg"
mk_square_svg 0.85 "${TMPDIR}/maskable.svg"

echo "# ${STATIC}/favicon.ico (16, 32, 48)"
convert -background none "${SRC}" \
        -define icon:auto-resize=48,32,16 "${STATIC}/favicon.ico"

echo "# ${ICONS}/icon-192.png"
convert -background none "${SRC}" -resize 192x192 \
        -depth 8 -strip PNG32:"${ICONS}/icon-192.png"

echo "# ${ICONS}/icon-512.png"
convert -background none "${SRC}" -resize 512x512 \
        -depth 8 -strip PNG32:"${ICONS}/icon-512.png"

echo "# ${ICONS}/icon-maskable-512.png"
convert -background none "${TMPDIR}/maskable.svg" -resize 512x512 \
        -depth 8 -strip PNG32:"${ICONS}/icon-maskable-512.png"

# iOS はアイコンの透過を扱わないので、青で塗りつぶして alpha を落とす。
# 角丸も付けない（iOS が自前で角を丸めるため、二重になる）。
echo "# ${ICONS}/apple-touch-icon.png"
convert -background "${BG}" "${TMPDIR}/square.svg" -resize 180x180 \
        -alpha remove -alpha off -depth 8 -strip \
        PNG24:"${ICONS}/apple-touch-icon.png"

echo "# done"
