#!/usr/bin/env bash
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       The Gramps project
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
# Assumption: script is executed from the 'aio-pyinstaller' directory
#
# arguments: build.sh <cleanup> <build-number>
#   cleanup      : [true|false]. clean the python venv on completion
#   build-number : the build number to use when DEV_VERSION is not True
#
# install prerequisites
## prerequisites in msys packages
pacman -S --needed --noconfirm \
    base-devel \
    git \
    intltool \
    mingw-w64-x86_64-adwaita-icon-theme \
    mingw-w64-x86_64-enchant \
    mingw-w64-x86_64-geocode-glib \
    mingw-w64-x86_64-ghostscript \
    mingw-w64-x86_64-goocanvas \
    mingw-w64-x86_64-graphviz \
    mingw-w64-x86_64-gspell \
    mingw-w64-x86_64-hunspell \
    mingw-w64-x86_64-iso-codes \
    mingw-w64-x86_64-nsis \
    mingw-w64-x86_64-osm-gps-map \
    mingw-w64-x86_64-python \
    mingw-w64-x86_64-python-bsddb3 \
    mingw-w64-x86_64-python-build \
    mingw-w64-x86_64-python-cairo \
    mingw-w64-x86_64-python-cffi \
    mingw-w64-x86_64-python-distlib \
    mingw-w64-x86_64-python-gobject \
    mingw-w64-x86_64-python-graphviz \
    mingw-w64-x86_64-python-icu \
    mingw-w64-x86_64-python-jsonschema \
    mingw-w64-x86_64-python-lief \
    mingw-w64-x86_64-python-lxml \
    mingw-w64-x86_64-python-networkx \
    mingw-w64-x86_64-python-nose \
    mingw-w64-x86_64-python-packaging \
    mingw-w64-x86_64-python-pillow \
    mingw-w64-x86_64-python-pip \
    mingw-w64-x86_64-python-psycopg2 \
    mingw-w64-x86_64-python-requests \
    mingw-w64-x86_64-python-setuptools \
    mingw-w64-x86_64-python-wheel \
    mingw-w64-x86_64-pyinstaller \
    mingw-w64-x86_64-pyinstaller-hooks-contrib \
    mingw-w64-x86_64-rust \
    mingw-w64-x86_64-toolchain \
    perl-XML-Parser \
    subversion \
    unzip

wget --no-verbose -N https://github.com/bpisoj/MINGW-packages/releases/download/v5.0/mingw-w64-x86_64-db-6.0.30-1-any.pkg.tar.xz
pacman -U --needed --noconfirm mingw-w64-x86_64-db-6.0.30-1-any.pkg.tar.xz

## create a python virtual environment so that we have a clean starting point
pythonvenv=$TMP/grampspythonenv
rm -rf $pythonvenv
python -m venv $pythonvenv --system-site-packages
source $pythonvenv/bin/activate

## prerequisites in pip packages
python -m pip install --upgrade pip
pip install --upgrade asyncio orjson pydot pydotplus requests selenium pyinstaller pyinstaller-hooks-contrib

## download dictionaries
mkdir -p /mingw64/share/enchant/hunspell
pushd /mingw64/share/enchant/hunspell
rootdir=https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries/
dicts=(
    bg:bg_BG
    ca:ca_ES
    cs:cs_CZ
    da:da_DK
    de:de_DE
    el:el_GR
    en-AU:en_AU
    en-GB:en_GB
    en:en_US
    eo:eo
    es:es_ES
    fr:fr_FR
    he:he_IL
    hr:hr_HR
    hu:hu_HU
    is:is_IS
    it:it_IT
    lt:lt_LT
    nb:nb_NO
    nl:nl_NL
    nn:nn_NO
    pl:pl_PL
    pt:pt_BR
    pt-PT:pt_PT
    ru:ru_RU
    sk:sk_SK
    sl:sl_SI
    sr:sr_RS
    sv:sv_SE
    tr:tr_TR
    uk:uk_UA
    vi:vi_VN
)
for dict in "${dicts[@]}"; do
    dir=${dict%:*}
    lang=${dict#*:}
    wget --no-verbose ${rootdir}${dir}/index.aff
    mv index.aff ${lang}.aff
    wget --no-verbose ${rootdir}${dir}/index.dic
    mv index.dic ${lang}.dic
done
popd

mkdir -p /mingw64/share/enchant/voikko
pushd /mingw64/share/enchant/voikko
wget --no-verbose -N https://www.puimula.org/htp/testing/voikko-snapshot-v5/dict.zip
unzip -q -o dict.zip
rm dict.zip
popd

# Assumption: script is executed from the 'aio-pyinstaller' directory!

## create a directory structure for icons
mkdir -p /mingw64/share/icons/gnome
mkdir -p /mingw64/share/icons/gnome/48x48
mkdir -p /mingw64/share/icons/gnome/48x48/mimetypes
mkdir -p /mingw64/share/icons/gnome/scalable
mkdir -p /mingw64/share/icons/gnome/scalable/mimetypes
mkdir -p /mingw64/share/icons/gnome/scalable/places

# Change to the gramps root directory
cd ..
cp images/gramps.png /mingw64/share/icons
cd images/hicolor/48x48/mimetypes
for f in *.png; do
    cp $f /mingw64/share/icons/gnome/48x48/mimetypes/gnome-mime-$f
done
cd ../../scalable/mimetypes
for f in *.svg; do
    cp $f /mingw64/share/icons/gnome/scalable/mimetypes/gnome-mime-$f
done
cd ../../../..
cp /mingw64/share/icons/hicolor/scalable/places/*.svg /mingw64/share/icons/gnome/scalable/places

# build gramps wheel
rm -rf dist aio-pyinstaller/dist
python setup.py bdist_wheel
if grep -q '^DEV_VERSION\s*=\s*True' gramps/version.py; then
    # <branch_name>-<short_commit_id>
    appbuild="$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)"
else
    # <VERSION_QUALIFIER>-<build-number>
    # VERSION_QUALIFIER is taken from gramps/version.py
    appbuild="$(sed -nr "s/^VERSION_QUALIFIER = \"-(.+)\"/\1/p" gramps/version.py)-$2"
fi
appversion=$(grep "^VERSION_TUPLE" gramps/version.py | sed 's/.*(//;s/, */\./g;s/).*//')

# Extract the Gramps wheel into aio-pyinstaller/dist so gramps.spec can find it
unzip -q -d aio-pyinstaller/dist dist/*.whl

cd aio-pyinstaller || exit 1

# Verify orjson is importable before running PyInstaller
python -c "import orjson; print('orjson', orjson.__version__, 'found at', orjson.__file__)" || { echo "ERROR: orjson not importable — aborting"; exit 1; }

# build PyInstaller executables
pyinstaller gramps.spec

# Manual fallback: copy orjson package into bundle if PyInstaller missed it
ORJSON_DIR=$(python -c "import os, orjson; print(os.path.dirname(orjson.__file__))" 2>/dev/null)
BUNDLE_INTERNAL="dist/grampsaio/_internal"
echo "orjson package dir: $ORJSON_DIR"
echo "bundle _internal: $BUNDLE_INTERNAL"
if [ -n "$ORJSON_DIR" ] && [ -d "$BUNDLE_INTERNAL" ]; then
    if [ -z "$(find "$BUNDLE_INTERNAL" -name 'orjson*' 2>/dev/null)" ]; then
        echo "orjson missing from bundle, copying manually from: $ORJSON_DIR"
        cp -r "$ORJSON_DIR" "$BUNDLE_INTERNAL/"
    else
        echo "orjson already present in bundle:"
        find "$BUNDLE_INTERNAL" -name 'orjson*'
    fi
else
    echo "WARNING: could not copy orjson to bundle (ORJSON_DIR='$ORJSON_DIR', BUNDLE_INTERNAL dir exists: $([ -d "$BUNDLE_INTERNAL" ] && echo yes || echo no))"
fi

# stage NSIS support files alongside the built executables
mkdir -p dist/grampsaio/src
cat grampsaio64.nsi.template | sed "s/yourVersion/$appversion/;s/yourBuild/$appbuild/" >dist/grampsaio/src/grampsaio64.nsi
cp ../aio/gramps.ico  dist/grampsaio/src/
cp ../aio/grampsc.ico dist/grampsaio/src/
cp ../aio/grampsd.ico dist/grampsaio/src/
# MUI_PAGE_LICENSE needs the license file present at NSIS compile time
cp ../COPYING dist/grampsaio/src/

# build installer
cd dist/grampsaio/src || exit 1
makensis grampsaio64.nsi
# result is GrampsAIO-*.exe in dist/grampsaio/src/

cd ../../..

# deactivate and delete the python virtual environment
if [ "$1" = "true" ]; then
    echo "post build cleanup"
    deactivate
    rm -rf $pythonvenv
fi

exit 0
