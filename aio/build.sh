#!/usr/bin/env bash
#
# Assumption: script is executed from the 'aio' directory
#
# install prerequisites
## prerequisites in msys packages
pacman -S --needed --noconfirm mingw-w64-x86_64-python mingw-w64-x86_64-python-pip mingw-w64-x86_64-gexiv2 mingw-w64-x86_64-ghostscript mingw-w64-x86_64-python-cairo mingw-w64-x86_64-python-gobject mingw-w64-x86_64-python-icu mingw-w64-x86_64-iso-codes mingw-w64-x86_64-hunspell mingw-w64-x86_64-enchant perl-XML-Parser intltool mingw-w64-x86_64-python-lxml mingw-w64-x86_64-python-jsonschema mingw-w64-x86_64-gspell mingw-w64-x86_64-geocode-glib mingw-w64-x86_64-python-pillow git mingw-w64-x86_64-graphviz mingw-w64-x86_64-goocanvas mingw-w64-x86_64-osm-gps-map base-devel subversion mingw-w64-x86_64-python-graphviz mingw-w64-x86_64-osm-gps-map mingw-w64-x86_64-nsis mingw-w64-x86_64-python-cx-freeze  mingw-w64-x86_64-python-requests mingw-w64-x86_64-adwaita-icon-theme mingw-w64-x86_64-python-networkx mingw-w64-x86_64-python-psycopg2 upx mingw-w64-x86_64-python-packaging unzip mingw-w64-x86_64-python-nose mingw-w64-x86_64-python-wheel
pacman -S --needed --noconfirm mingw-w64-x86_64-toolchain

wget -N https://github.com/bpisoj/MINGW-packages/releases/download/v5.0/mingw-w64-x86_64-db-6.0.30-1-any.pkg.tar.xz
pacman -U --needed --noconfirm mingw-w64-x86_64-db-6.0.30-1-any.pkg.tar.xz

pacman -S --needed --noconfirm  mingw-w64-x86_64-python-bsddb3

## prerequisites in pip packages
python -m pip install --upgrade pip
pip install --upgrade pydot pydotplus requests asyncio
SETUPTOOLS_USE_DISTUTILS=stdlib pip install pygraphviz

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
    wget ${rootdir}${dir}/index.aff
    mv index.aff ${lang}.aff
    wget ${rootdir}${dir}/index.dic
    mv index.dic ${lang}.dic
done
popd

mkdir -p /mingw64/share/enchant/voikko
pushd /mingw64/share/enchant/voikko
wget -N https://www.puimula.org/htp/testing/voikko-snapshot-v5/dict.zip
unzip -o dict.zip
rm dict.zip
popd

# Assumption: script is executed from the 'aio' directory!
#cd D:/a/gramps/gramps/aio

## create a directory structure for icons
mkdir /mingw64/share/icons/gnome
mkdir /mingw64/share/icons/gnome/48x48
mkdir /mingw64/share/icons/gnome/48x48/mimetypes
mkdir /mingw64/share/icons/gnome/scalable
mkdir /mingw64/share/icons/gnome/scalable/mimetypes
mkdir /mingw64/share/icons/gnome/scalable/places

# Change to the gramps root directory
cd ..
cp images/gramps.png /mingw64/share/icons
cd images/hicolor/48x48/mimetypes
for f in *.png
do
    cp $f /mingw64/share/icons/gnome/48x48/mimetypes/gnome-mime-$f
done
cd ../../scalable/mimetypes
for f in *.svg
do
    cp $f /mingw64/share/icons/gnome/scalable/mimetypes/gnome-mime-$f
done
cd ../../../..
cp /mingw64/share/icons/hicolor/scalable/places/*.svg /mingw64/share/icons/gnome/scalable/places

# build gramps
rm -rf dist aio/dist
python setup.py bdist_wheel
appbuild="r$(git rev-list --count HEAD)-$(git rev-parse --short HEAD)"
appversion=$(grep "^VERSION_TUPLE" gramps/version.py|sed 's/.*(//;s/, */\./g;s/).*//')
unzip -d aio/dist dist/*.whl
cd aio

# create nsis script
cat grampsaio64.nsi.template|sed "s/yourVersion/$appversion/;s/yourBuild/$appbuild/">grampsaio64.nsi
# build cx_freeze executables
python setup.py build_exe --no-compress
# build installer
cd mingw64/src
makensis grampsaio64.nsi
# result is in mingw64/src

exit 0
