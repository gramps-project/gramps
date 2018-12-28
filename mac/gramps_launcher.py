from os.path import join, dirname, abspath, normpath
from os import environ
from sys import argv, version
from platform import release


bundlepath = argv[0]

bundle_contents = join(bundlepath, 'Contents')
bundle_res = join(bundle_contents, 'Resources')

bundle_lib = join(bundle_res, 'lib')
bundle_bin = join(bundle_res, 'bin')
bundle_data = join(bundle_res, 'share')
bundle_etc = join(bundle_res, 'etc')

environ['XDG_DATA_DIRS'] = bundle_data
environ['DYLD_LIBRARY_PATH'] = bundle_lib
environ['LD_LIBRARY_PATH'] = bundle_lib
environ['GTK_DATA_PREFIX'] = bundle_res
environ['GTK_EXE_PREFIX'] = bundle_res
environ['GTK_PATH'] = bundle_res

environ['PANGO_RC_FILE'] = join(bundle_etc, 'pango', 'pangorc')
environ['PANGO_SYSCONFDIR'] = bundle_etc
environ['PANGO_LIBDIR'] = bundle_lib
environ['GDK_PIXBUF_MODULE_FILE'] = join(bundle_lib, 'gdk-pixbuf-2.0',
                                                '2.10.0', 'loaders.cache')
environ['GI_TYPELIB_PATH'] = join(bundle_lib, 'girepository-1.0')
environ['GVBINDIR'] = join(bundle_lib, 'graphviz')
environ['ENCHANT_MODULE_PATH'] = join(bundle_lib, 'enchant')

#Set $PYTHON to point inside the bundle
PYVER = 'python' + version[:3]

environ['GRAMPSDIR'] = join (bundle_lib, PYVER, 'site-packages', 'gramps')
environ['GRAMPSI18N'] = join(bundle_data, 'locale')
environ['GRAMPS_RESOURCES'] = bundle_data
environ['USERPROFILE'] = environ['HOME']
environ['APPDATA'] = join(environ['HOME'], 'Library', 'Application Support')
environ['PATH'] = join(bundle_contents, 'MacOS') + ':' + environ['PATH']

import gramps.grampsapp as app
app.main()

