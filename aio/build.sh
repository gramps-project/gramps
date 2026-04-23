#!/usr/bin/env bash
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       Steve Youngs <steve@youngs.cc>
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
# Assumption: script is executed from the 'aio' directory
#
# arguments: build.sh <cleanup> <build-number>
#   clean-up     : [true|false]. clean the python venv on completion
#   build-number : the build number to use when DEV_VERSION is not True
#
# install prerequisites
## prerequisites in msys packages
pacman -S --needed --noconfirm \
    base-devel \
    git \
    intltool \
    mingw-w64-ucrt-x86_64-adwaita-icon-theme \
    mingw-w64-ucrt-x86_64-geocode-glib \
    mingw-w64-ucrt-x86_64-gexiv2 \
    mingw-w64-ucrt-x86_64-ghostscript \
    mingw-w64-ucrt-x86_64-goocanvas \
    mingw-w64-ucrt-x86_64-hunspell \
    mingw-w64-ucrt-x86_64-iso-codes \
    mingw-w64-ucrt-x86_64-nsis \
    mingw-w64-ucrt-x86_64-osm-gps-map \
    mingw-w64-ucrt-x86_64-python \
    mingw-w64-ucrt-x86_64-python-build \
    mingw-w64-ucrt-x86_64-python-cairo \
    mingw-w64-ucrt-x86_64-python-cffi \
    mingw-w64-ucrt-x86_64-python-cx-freeze \
    mingw-w64-ucrt-x86_64-python-distlib \
    mingw-w64-ucrt-x86_64-python-gobject \
    mingw-w64-ucrt-x86_64-python-graphviz \
    mingw-w64-ucrt-x86_64-python-icu \
    mingw-w64-ucrt-x86_64-python-jsonschema \
    mingw-w64-ucrt-x86_64-python-lief \
    mingw-w64-ucrt-x86_64-python-lxml \
    mingw-w64-ucrt-x86_64-python-networkx \
    mingw-w64-ucrt-x86_64-python-nose \
    mingw-w64-ucrt-x86_64-python-packaging \
    mingw-w64-ucrt-x86_64-python-pillow \
    mingw-w64-ucrt-x86_64-python-pip \
    mingw-w64-ucrt-x86_64-python-psycopg2 \
    mingw-w64-ucrt-x86_64-python-requests \
    mingw-w64-ucrt-x86_64-python-setuptools \
    mingw-w64-ucrt-x86_64-python-wheel \
    mingw-w64-ucrt-x86_64-rust \
    mingw-w64-ucrt-x86_64-toolchain \
    perl-XML-Parser \
    subversion \
    unzip

# Older versions from archives due to compatibility issues with
# latest versions.  When resolved, move back to list above.
pacman -U --needed --noconfirm \
    https://repo.msys2.org/mingw/ucrt64/mingw-w64-ucrt-x86_64-enchant-2.6.7-5-any.pkg.tar.zst \
    https://repo.msys2.org/mingw/ucrt64/mingw-w64-ucrt-x86_64-graphviz-12.2.1-4-any.pkg.tar.zst \
    https://repo.msys2.org/mingw/ucrt64/mingw-w64-ucrt-x86_64-gspell-1.14.0-4-any.pkg.tar.zst

## create a python virtual environment so that we have a clean starting point
pythonvenv=$TMP/grampspythonenv
rm -rf $pythonvenv
python -m venv $pythonvenv --system-site-packages
source $pythonvenv/bin/activate

## prerequisites in pip packages
python -m pip install --upgrade pip
pip install --upgrade orjson==3.11.7 pydot pydotplus pygraphviz requests selenium

## download dictionaries
mkdir -p /ucrt64/share/enchant/hunspell
pushd /ucrt64/share/enchant/hunspell
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

mkdir -p /ucrt64/share/enchant/voikko
pushd /ucrt64/share/enchant/voikko
wget --no-verbose -N https://www.puimula.org/htp/testing/voikko-snapshot-v5/dict.zip
unzip -q -o dict.zip
rm dict.zip
popd

# Assumption: script is executed from the 'aio' directory!

## create a directory structure for icons
mkdir -p /ucrt64/share/icons/gnome
mkdir -p /ucrt64/share/icons/gnome/48x48
mkdir -p /ucrt64/share/icons/gnome/48x48/mimetypes
mkdir -p /ucrt64/share/icons/gnome/scalable
mkdir -p /ucrt64/share/icons/gnome/scalable/mimetypes
mkdir -p /ucrt64/share/icons/gnome/scalable/places

# Change to the gramps root directory
cd ..
cp images/gramps.png /ucrt64/share/icons
cd images/hicolor/48x48/mimetypes
for f in *.png; do
    cp $f /ucrt64/share/icons/gnome/48x48/mimetypes/gnome-mime-$f
done
cd ../../scalable/mimetypes
for f in *.svg; do
    cp $f /ucrt64/share/icons/gnome/scalable/mimetypes/gnome-mime-$f
done
cd ../../../..
cp /ucrt64/share/icons/hicolor/scalable/places/*.svg /ucrt64/share/icons/gnome/scalable/places

# build gramps
rm -rf dist gramps.egg-info aio/dist aio/GrampsAIO64.egg-info aio/$MSYSTEM
python -m build --wheel
if `grep -q '^DEV_VERSION\s*=\s*True' gramps/version.py`; then
    # <branch_name>-<short_commit_id>
    appbuild="$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)"
else
    # <VERSION_QUALIFIER>-<build-number>
    # VERSION_QUALIFIER is taken from gramps/version.py
    appbuild="$(sed -nr "s/^VERSION_QUALIFIER = \"-(.+)\"/\1/p" gramps/version.py)-$2"
fi
appversion=$(grep "^VERSION_TUPLE" gramps/version.py | sed 's/.*(//;s/, */\./g;s/).*//')
unzip -q -d aio/dist dist/*.whl
cd aio

# escape sed replacement patterns
escapedappversion=$(echo $appversion | sed 's/\\/\\\\/g; s/[\/&]/\\&/g')
escapedappbuild=$(echo $appbuild | sed 's/\\/\\\\/g; s/[\/&]/\\&/g')
# create nsis script
cat grampsaio64.nsi.template | sed "s/yourVersion/$escapedappversion/;s/yourBuild/$escapedappbuild/" >grampsaio64.nsi
# build cx_freeze executables
python setup.py build_exe

# Smoke test the frozen pip before packaging so stdlib-coverage gaps are
# caught here instead of by end users running the Addon Manager.
# $MSYSTEM is MINGW64/UCRT64/etc.; the matching build tree is the
# lowercase equivalent, so the command below works across environments
# without needing to be edited when the rest of the script is modernized.
echo "Smoke-testing bundled pip..."
msys_dir="${MSYSTEM,,}"
smoke_fail=0
for cmd in "./${msys_dir}/pip.exe --version" "./${msys_dir}/pip.exe install --dry-run --ignore-installed certifi"; do
    echo "--- $cmd ---"
    smoke_out=$($cmd 2>&1) || true
    echo "$smoke_out"
    if echo "$smoke_out" | grep -qiE "ImportError|ModuleNotFoundError|Traceback"; then
        echo "ERROR: Frozen pip emitted an error or traceback running: $cmd"
        smoke_fail=1
    fi
done
if [ "$smoke_fail" -ne 0 ]; then
    echo "ERROR: pip smoke test failed; aborting build before NSIS."
    echo "  Likely cause: a stdlib submodule pip (or one of its vendored"
    echo "  libraries) imports lazily was not picked up by cx_Freeze's"
    echo "  static scan. Add the missing module to INCLUDES or its parent"
    echo "  package to PACKAGES in aio/setup.py and rebuild."
    exit 1
fi

# build installer
cd ucrt64/src
makensis grampsaio64.nsi
# result is in ucrt64/src

# deactivate and delete the python virtual environment
if [ "$1" = "true" ]; then
    echo "post build cleanup"
    deactivate
    rm -rf $pythonvenv
fi

exit 0
