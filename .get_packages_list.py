import os

from distutils2.util import find_packages

exclude_list = ('src.gui.glade', 'src.guiQML', 'src.guiQML.views', 'src.images', 'src.plugins',
                'src.webapp', 'src.webapp.grampsdb', 'src.webapp.grampsdb.templatetags', 'src.webapp.grampsdb.view', )

packages = sorted(find_packages(exclude=exclude_list))

for package in packages:
    print("            '%s'," % package)
