# install prerequisites :
## prerequisites in msys packages :
pacman -S --needed --noconfirm mingw-w64-x86_64-python-pip mingw-w64-x86_64-python3-bsddb3 mingw-w64-x86_64-gexiv2 mingw-w64-x86_64-ghostscript mingw-w64-x86_64-python3-cairo mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-python3-icu mingw-w64-x86_64-iso-codes mingw-w64-x86_64-hunspell mingw-w64-x86_64-hunspell-en mingw-w64-x86_64-enchant perl-XML-Parser intltool mingw-w64-x86_64-python3-lxml mingw-w64-x86_64-python3-jsonschema mingw-w64-x86_64-gtkspell3 mingw-w64-x86_64-geocode-glib mingw-w64-x86_64-python3-pillow git mingw-w64-x86_64-graphviz mingw-w64-x86_64-goocanvas mingw-w64-x86_64-osm-gps-map base-devel mingw-w64-x86_64-toolchain subversion mingw-w64-x86_64-db mingw-w64-x86_64-python-bsddb3 mingw-w64-x86_64-graphviz mingw-w64-x86_64-python-graphviz mingw-w64-x86_64-osm-gps-map mingw-w64-x86_64-nsis mingw-w64-x86_64-python-cx-freeze  mingw-w64-x86_64-python3-requests mingw-w64-x86_64-enchant mingw-w64-x86_64-adwaita-icon-theme mingw-w64-x86_64-python-networkx mingw-w64-x86_64-python-psycopg2 upx mingw-w64-x86_64-python-packaging unzip mingw-w64-x86_64-python3-nose mingw-w64-x86_64-python-wheel
python3  -m pip install --upgrade pip
## prerequisites in pip packages
pip3 install --upgrade pydot pydotplus requests asyncio
## berkeley db, from sources (6.0.30 wanted, msys2 provides actually 6.0.19)
mkdir  ../build
cd ../build
if [ ! -f mingw-w64-x86_64-db-6.0.30-1-any.pkg.tar.xz ] ; then
  wget https://github.com/bpisoj/MINGW-packages/releases/download/v5.0/mingw-w64-x86_64-db-6.0.30-1-any.pkg.tar.xz
fi
pacman -U --noconfirm mingw-w64-x86_64-db-6.0.30-1-any.pkg.tar.xz
pacman -S --noconfirm mingw-w64-x86_64-python3-bsddb3
## pygraphviz, from sources
if [ ! -f Pygraphviz-1.4rc1.zip ] ; then
  wget  https://gramps-project.org/wiki/images/2/2b/Pygraphviz-1.4rc1.zip
fi
mkdir pygraphviz-1.4rc1
cd pygraphviz-1.4rc1
unzip -u ../Pygraphviz-1.4rc1.zip
MINGW_INSTALLS=mingw64 makepkg-mingw -sLf
pacman -U --noconfirm mingw-w64-x86_64-python3-pygraphviz-1.4rc1-0.0-any.pkg.tar.zst
## add some icons and dictionaries not easy to install 
cd ../../aio
tar --directory /mingw64/share/ -zxf share.tgz

# build gramps
cd ..
rm -rf dist aio/dist
python3 setup.py bdist_wheel
appbuild="r$(git rev-list --count HEAD)-$(git rev-parse --short HEAD)"
appversion=$(grep "^VERSION_TUPLE" gramps/version.py|sed 's/.*(//;s/, */\./g;s/).*//')
unzip -d aio/dist dist/*.whl
cd aio

# create nsis script
cat grampsaio64.nsi.template|sed "s/yourVersion/$appversion/;s/yourBuild/$appbuild/">grampsaio64.nsi
# build cx_freeze executables
python3 setup.py build_exe --no-compress
# build installer
makensis mingw64/src/grampsaio64.nsi
# result is in mingw64/src

