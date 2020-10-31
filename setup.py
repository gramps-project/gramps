#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012,2020 Nick Hall
# Copyright (C) 2012      Rob G. Healey
# Copyright (C) 2012      Benny Malengier
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

'''
Gramps distutils module.
'''

#check python version first
import sys

if sys.version_info < (3, 5):
    raise SystemExit("Gramps requires Python 3.5 or later.")

from distutils import log
from setuptools import setup
from distutils.core import Command
from distutils.util import convert_path, newer
from distutils.command.build import build as _build
import os
import glob
import codecs
import subprocess
from stat import ST_MODE
from gramps.version import VERSION
import unittest
import argparse


svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument("--no-compress-manpages", dest="no_compress_manpages",
                       action="store_true")
args, passthrough = argparser.parse_known_args()
sys.argv = [sys.argv[0]] + passthrough

def substitute_variables(filename_in, filename_out, subst_vars):
    '''
    Substitute variables in a file.
    '''
    f_in = codecs.open(filename_in, encoding='utf-8')
    f_out = codecs.open(filename_out, encoding='utf-8', mode='w')
    for line in f_in:
        for variable, substitution in subst_vars:
            line = line.replace(variable, substitution)
        f_out.write(line)
    f_in.close()
    f_out.close()

def get_linguas():
    '''
    Read the po/LINGUAS file to get a list of all linguas.
    '''
    all_linguas = []
    with open(os.path.join('po', 'LINGUAS'), 'r', encoding='utf-8') as linguas:
        for line in linguas:
            if '#' in line:
                line = line[:line.find('#')]
            all_linguas.extend(line.split())
    return all_linguas

def build_trans(build_cmd):
    '''
    Translate the language files into gramps.mo
    '''
    data_files = build_cmd.distribution.data_files
    for lang in get_linguas():
        po_file = os.path.join('po', lang + '.po')
        mo_file = os.path.join(build_cmd.build_base, 'mo', lang, 'LC_MESSAGES',
                               'gramps.mo')
        mo_file_unix = (build_cmd.build_base + '/mo/' + lang +
                        '/LC_MESSAGES/gramps.mo')
        mo_dir = os.path.dirname(mo_file)
        if not(os.path.isdir(mo_dir) or os.path.islink(mo_dir)):
            os.makedirs(mo_dir)

        if newer(po_file, mo_file):
            cmd = 'msgfmt %s -o %s' % (po_file, mo_file)
            if os.system(cmd) != 0:
                os.remove(mo_file)
                msg = 'ERROR: Building language translation files failed.'
                ask = msg + '\n Continue building y/n [n] '
                reply = input(ask)
                if reply in ['n', 'N']:
                    raise SystemExit(msg)
            log.info('Compiling %s >> %s', po_file, mo_file)

        #linux specific piece:
        target = 'share/locale/' + lang + '/LC_MESSAGES'
        data_files.append((target, [mo_file_unix]))

def build_man(build_cmd):
    '''
    Compresses Gramps manual files
    '''
    data_files = build_cmd.distribution.data_files
    for man_dir, dirs, files in os.walk(os.path.join('data', 'man')):
        if 'gramps.1.in' in files:
            filename = os.path.join(man_dir, 'gramps.1.in')
            newdir = os.path.join(build_cmd.build_base, man_dir)
            if not(os.path.isdir(newdir) or os.path.islink(newdir)):
                os.makedirs(newdir)

            newfile = os.path.join(newdir, 'gramps.1')
            subst_vars = (('@VERSION@', VERSION), )
            substitute_variables(filename, newfile, subst_vars)

            src = 'gramps.1'
            if not args.no_compress_manpages:
                import gzip
                src += '.gz'
                man_file_gz = os.path.join(newdir, src)
                if os.path.exists(man_file_gz):
                    if newer(filename, man_file_gz):
                        os.remove(man_file_gz)
                    else:
                        filename = False
                        os.remove(newfile)

                if filename:
                    #Binary io, so open is OK
                    with open(newfile, 'rb') as f_in,\
                            gzip.open(man_file_gz, 'wb') as f_out:
                        f_out.writelines(f_in)
                        log.info('Compiling %s >> %s', filename, man_file_gz)

                    os.remove(newfile)
                    filename = False

            lang = man_dir[8:]
            src = build_cmd.build_base  + '/data/man' + lang  + '/' + src
            target = 'share/man' + lang + '/man1'
            data_files.append((target, [src]))

def build_intl(build_cmd):
    '''
    Merge translation files into desktop and mime files
    '''
    data_files = build_cmd.distribution.data_files
    base = build_cmd.build_base

    merge_files = (('data/gramps.desktop', 'share/applications', '--desktop'),
                   ('data/gramps.xml', 'share/mime/packages', '--xml'),
                   ('data/gramps.appdata.xml', 'share/metainfo', '--xml'))

    for filename, target, option in merge_files:
        filenamelocal = convert_path(filename)
        newfile = os.path.join(base, filenamelocal)
        newdir = os.path.dirname(newfile)
        if not(os.path.isdir(newdir) or os.path.islink(newdir)):
            os.makedirs(newdir)
        merge(filenamelocal + '.in', newfile, option)
        data_files.append((target, [base + '/' + filename]))

def merge(in_file, out_file, option, po_dir='po'):
    '''
    Run the msgfmt command.
    '''
    if (not os.path.exists(out_file) and os.path.exists(in_file)):
        cmd = (('GETTEXTDATADIR=%(po_dir)s msgfmt %(opt)s '
                '--template %(in_file)s -d %(po_dir)s -o %(out_file)s') %
                {'opt' : option,
                 'po_dir' : po_dir,
                 'in_file' : in_file,
                 'out_file' : out_file})
        if os.system(cmd) != 0:
            msg = ('ERROR: %s was not merged into the translation files!\n' %
                    out_file)
            raise SystemExit(msg)
        log.info('Compiling %s >> %s', in_file, out_file)

class build(_build):
    """Custom build command."""
    def run(self):
        build_trans(self)
        if not sys.platform == 'win32':
            build_man(self)
        build_intl(self)
        _build.run(self)

class test(Command):
    """Command to run Gramps unit tests"""
    description = "run all unit tests"
    user_options = []


    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.exists('build'):
            raise RuntimeError("No build directory. Run `python setup.py build` before trying to run tests.")
        os.environ['GRAMPS_RESOURCES'] = '.'
        all_tests = unittest.TestLoader().discover('.', pattern='*_test.py')
        unittest.TextTestRunner(verbosity=self.verbose).run(all_tests)

#-------------------------------------------------------------------------
#
# Packages
#
#-------------------------------------------------------------------------
package_core = ['gramps',
                'gramps.cli',
                'gramps.cli.plug',
                'gramps.gen.utils.docgen',
                'gramps.gen',
                'gramps.gen.datehandler',
                'gramps.gen.db',
                'gramps.gen.display',
                'gramps.gen.filters',
                'gramps.gen.filters.rules',
                'gramps.gen.filters.rules.citation',
                'gramps.gen.filters.rules.event',
                'gramps.gen.filters.rules.family',
                'gramps.gen.filters.rules.media',
                'gramps.gen.filters.rules.note',
                'gramps.gen.filters.rules.person',
                'gramps.gen.filters.rules.place',
                'gramps.gen.filters.rules.repository',
                'gramps.gen.filters.rules.source',
                'gramps.gen.lib',
                'gramps.gen.merge',
                'gramps.gen.mime',
                'gramps.gen.plug',
                'gramps.gen.plug.docbackend',
                'gramps.gen.plug.docgen',
                'gramps.gen.plug.menu',
                'gramps.gen.plug.report',
                'gramps.gen.proxy',
                'gramps.gen.simple',
                'gramps.gen.utils',
                'gramps.gen.utils.docgen',
                'gramps.test',
                'gramps.plugins',
                'gramps.plugins.db',
                'gramps.plugins.db.bsddb',
                'gramps.plugins.db.dbapi',
                'gramps.plugins.docgen',
                'gramps.plugins.drawreport',
                'gramps.plugins.export',
                'gramps.plugins.gramplet',
                'gramps.plugins.graph',
                'gramps.plugins.importer',
                'gramps.plugins.lib',
                'gramps.plugins.lib.maps',
                'gramps.plugins.mapservices',
                'gramps.plugins.quickview',
                'gramps.plugins.rel',
                'gramps.plugins.sidebar',
                'gramps.plugins.textreport',
                'gramps.plugins.tool',
                'gramps.plugins.view',
                'gramps.plugins.webreport',
                'gramps.plugins.webstuff',
                ]
package_gui = ['gramps.gui',
               'gramps.gui.editors',
               'gramps.gui.editors.displaytabs',
               'gramps.gui.filters',
               'gramps.gui.filters.sidebar',
               'gramps.gui.logger',
               'gramps.gui.merge',
               'gramps.gui.plug',
               'gramps.gui.plug.export',
               'gramps.gui.plug.quick',
               'gramps.gui.plug.report',
               'gramps.gui.selectors',
               'gramps.gui.views',
               'gramps.gui.views.treemodels',
               'gramps.gui.widgets',
               ]

packages = package_core + package_gui

#-------------------------------------------------------------------------
#
# Package data
#
#-------------------------------------------------------------------------

# add all subdirs of plugin with glade:
package_data_core = []
basedir = os.path.join('gramps', 'plugins')
for (dirpath, dirnames, filenames) in os.walk(basedir):
    root, subdir = os.path.split(dirpath)
    if subdir.startswith("."):
        dirnames[:] = []
        continue
    for dirname in dirnames:
        # Skip hidden and system directories:
        if dirname.startswith("."):
            dirnames.remove(dirname)
        #we add to data_list so glade , xml, files are found, we don't need the gramps/ part
        package_data_core.append(dirpath[7:] + '/' + dirname + '/*.glade')
        package_data_core.append(dirpath[7:] + '/' + dirname + '/*.xml')
        package_data_core.append(dirpath[7:] + '/' + dirname + '/*.ini')

package_data_gui = ['gui/glade/*.glade']
package_data = package_data_core + package_data_gui

#-------------------------------------------------------------------------
#
# Resources
#
#-------------------------------------------------------------------------
data_files_core = []
DOC_FILES = ['AUTHORS', 'COPYING', 'FAQ', 'INSTALL', 'NEWS', 'README.md',
             'TODO']
GEDCOM_FILES = glob.glob(os.path.join('example', 'gedcom', '*.*'))
GRAMPS_FILES = glob.glob(os.path.join('example', 'gramps', '*.*'))
IMAGE_WEB = glob.glob(os.path.join('images', 'webstuff', '*.png'))
IMAGE_WEB.extend(glob.glob(os.path.join('images', 'webstuff','*.ico')))
IMAGE_WEB.extend(glob.glob(os.path.join('images', 'webstuff', '*.gif')))
CSS_FILES = glob.glob(os.path.join('data', 'css', '*.css'))
SWANKY_PURSE = glob.glob(os.path.join('data', 'css', 'swanky-purse', '*.css'))
SWANKY_IMG = glob.glob(os.path.join('data', 'css', 'swanky-purse', 'images', '*.png'))
data_files_core.append(('share/doc/gramps', DOC_FILES))
data_files_core.append(('share/doc/gramps/example/gedcom', GEDCOM_FILES))
data_files_core.append(('share/doc/gramps/example/gramps', GRAMPS_FILES))
data_files_core.append(('share/gramps/images/webstuff', IMAGE_WEB))
data_files_core.append(('share/gramps/css', CSS_FILES))
data_files_core.append(('share/gramps/css/swanky-purse', SWANKY_PURSE))
data_files_core.append(('share/gramps/css/swanky-purse/images', SWANKY_IMG))

PNG_FILES = glob.glob(os.path.join('data', '*.png'))
SVG_FILES = glob.glob(os.path.join('data', '*.svg'))
data_files_core.append(('share/icons/gnome/48x48/mimetypes', PNG_FILES))
data_files_core.append(('share/icons/gnome/scalable/mimetypes', SVG_FILES))

DTD_FILES = glob.glob(os.path.join('data', '*.dtd'))
RNG_FILES = glob.glob(os.path.join('data', '*.rng'))
XML_FILES = glob.glob(os.path.join('data', '*.xml'))
data_files_core.append(('share/gramps', XML_FILES))
data_files_core.append(('share/gramps', DTD_FILES))
data_files_core.append(('share/gramps', RNG_FILES))

data_files_gui = []
IMAGE_FILES = glob.glob(os.path.join('images', '*.*'))
THEME = os.path.join('images', 'hicolor')
ICON_16 = glob.glob(os.path.join(THEME, '16x16', 'actions', '*.png'))
ICON_22 = glob.glob(os.path.join(THEME, '22x22', 'actions', '*.png'))
ICON_24 = glob.glob(os.path.join(THEME, '24x24', 'actions', '*.png'))
ICON_48 = glob.glob(os.path.join(THEME, '48x48', 'actions', '*.png'))
ICON_SC = glob.glob(os.path.join(THEME, 'scalable', 'actions', '*.svg'))
data_files_gui.append(('share/gramps/images', IMAGE_FILES))
data_files_gui.append(('share/gramps/images/hicolor/16x16/actions', ICON_16))
data_files_gui.append(('share/gramps/images/hicolor/22x22/actions', ICON_22))
data_files_gui.append(('share/gramps/images/hicolor/24x24/actions', ICON_24))
data_files_gui.append(('share/gramps/images/hicolor/48x48/actions', ICON_48))
data_files_gui.append(('share/gramps/images/hicolor/scalable/actions', ICON_SC))
APP_16 = os.path.join(THEME, '16x16', 'apps', 'gramps.png')
APP_22 = os.path.join(THEME, '22x22', 'apps', 'gramps.png')
APP_24 = os.path.join(THEME, '24x24', 'apps', 'gramps.png')
APP_48 = os.path.join(THEME, '48x48', 'apps', 'gramps.png')
APP_SC = os.path.join(THEME, 'scalable', 'apps', 'gramps.svg')
data_files_gui.append(('share/icons/hicolor/16x16/apps', [APP_16]))
data_files_gui.append(('share/icons/hicolor/22x22/apps', [APP_22]))
data_files_gui.append(('share/icons/hicolor/24x24/apps', [APP_24]))
data_files_gui.append(('share/icons/hicolor/48x48/apps', [APP_48]))
data_files_gui.append(('share/icons/hicolor/scalable/apps', [APP_SC]))

data_files = data_files_core + data_files_gui

#-------------------------------------------------------------------------
#
# Setup
#
#-------------------------------------------------------------------------
setup(name = 'gramps',
      description = ('Gramps (Genealogical Research and Analysis Management '
                     'Programming System)'),
      long_description = ('Gramps (Genealogical Research and Analysis '
                          'Management Programming System) is a full featured '
                          'genealogy program supporting a Python based plugin '
                          'system.'),
      version = VERSION,
      author = 'Donald N. Allingham',
      author_email = 'don@gramps-project.org',
      maintainer = 'Gramps Development Team',
      maintainer_email = 'benny.malengier@gmail.com',
      url = 'http://gramps-project.org',
      license = 'GPL v2 or greater',
      platforms = ['FreeBSD', 'Linux', 'MacOS', 'Windows'],
      cmdclass = {'build': build, 'test': test},
      packages = packages,
      package_data = {'gramps': package_data},
      extras_require={
          "bsddb": ["bsddb3"],
          "image": ["Pillow"],
          "i18n": ["PyICU"],
          "GUI":  ["PyGObject", "pycairo"],
          "testing": ["jsonschema", "mock", "lxml"],
      },
      data_files = data_files,
      scripts = ['scripts/gramps'],
      classifiers = [
          "Development Status :: 1 - Planning",
          "Environment :: Console",
          "Environment :: MacOS X",
          "Environment :: Plugins",
          "Environment :: Web Environment",
          "Environment :: Win32 (MS Windows)",
          "Environment :: X11 Applications :: GTK",
          "Intended Audience :: Education",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: Other Audience",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Natural Language :: Arabic",
          "Natural Language :: Bulgarian",
          "Natural Language :: Catalan",
          "Natural Language :: Chinese (Simplified)",
          "Natural Language :: Croatian",
          "Natural Language :: Czech",
          "Natural Language :: Danish",
          "Natural Language :: Dutch",
          "Natural Language :: English",
          "Natural Language :: Esperanto",
          "Natural Language :: Finnish",
          "Natural Language :: French",
          "Natural Language :: German",
          "Natural Language :: Greek",
          "Natural Language :: Hebrew",
          "Natural Language :: Hungarian",
          "Natural Language :: Icelandic",
          "Natural Language :: Italian",
          "Natural Language :: Japanese",
          "Natural Language :: Macedonian",
          "Natural Language :: Norwegian",
          "Natural Language :: Polish",
          "Natural Language :: Portuguese",
          "Natural Language :: Portuguese (Brazilian)",
          "Natural Language :: Romanian",
          "Natural Language :: Russian",
          "Natural Language :: Serbian",
          "Natural Language :: Slovak",
          "Natural Language :: Slovenian",
          "Natural Language :: Spanish",
          "Natural Language :: Swedish",
          "Natural Language :: Turkish",
          "Natural Language :: Vietnamese",
          "Operating System :: MacOS",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: Other OS",
          "Operating System :: POSIX :: BSD",
          "Operating System :: POSIX :: Linux",
          "Operating System :: POSIX :: SunOS/Solaris",
          "Operating System :: Unix",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Topic :: Database",
          "Topic :: Desktop Environment :: Gnome",
          "Topic :: Education",
          "Topic :: Scientific/Engineering :: Visualization",
          "Topic :: Sociology :: Genealogy",
          ]
)
