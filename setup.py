#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012 Nick Hall
# Copyright (C) 2012 Rob G. Healey
# Copyright (C) 2012 Benny Malengier
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

'''
Gramps distutils module.
'''

#check python version first
import sys
major, minor1, minor2, s, tmp = sys.version_info

if (major==2 and minor1<7) or major<2 or major>3:
    raise SystemExit("""Gramps requires Python 2.7 or later, Python 3 not supported.""")

from distutils import log
from distutils.core import setup
from distutils.util import convert_path, newer
from distutils.command.build import build as _build
from distutils.command.install import install as _install
import os
import glob
import codecs
import commands
from stat import ST_MODE

VERSION = '4.0.0'
ALL_LINGUAS = ('bg', 'ca', 'cs', 'da', 'de', 'en_GB', 'es', 'fi', 'fr', 'he',
               'hr', 'hu', 'it', 'ja', 'lt', 'nb', 'nl', 'nn', 'pl', 'pt_BR',
               'pt_PT', 'ru', 'sk', 'sl', 'sq', 'sv', 'uk', 'vi', 'zh_CN')
INTLTOOL_FILES = ('src/data/tips.xml', 'src/plugins/lib/holidays.xml')

def intltool_version():
    '''
    Return the version of intltool as a tuple.
    '''
    cmd = 'intltool-update --version | head -1 | cut -d" " -f3'
    retcode, version_str = commands.getstatusoutput(cmd)
    if retcode != 0:
        return None
    else:
        return tuple([int(num) for num in version_str.split('.')])

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

def build_trans(build_cmd):
    '''
    Translate the language files into gramps.mo
    '''
    data_files = build_cmd.distribution.data_files
    for lang in ALL_LINGUAS:
        po_file = os.path.join('po', lang + '.po')
        mo_file = os.path.join(build_cmd.build_base, 'mo', lang, 'gramps.mo')

        mo_dir = os.path.dirname(mo_file)
        if not(os.path.isdir(mo_dir) or os.path.islink(mo_dir)):
            os.makedirs(mo_dir)

        if newer(po_file, mo_file):
            cmd = 'msgfmt %s -o %s' % (po_file, mo_file)
            if os.system(cmd) != 0:
                msg = 'ERROR: Building language translation files failed.'
                raise SystemExit(msg)

        #linux specific piece:
        target = os.path.join(['share', 'locale', lang, 'LC_MESSAGES'])
        data_files.append((target, [mo_file]))

        log.info('Compiling %s >> %s.', po_file, target)

def build_man(build_cmd):
    '''
    Compresses Gramps manual files
    '''
    data_files = build_cmd.distribution.data_files
    build_data = build_cmd.build_base + os.sep + 'data' + os.sep
    for man_dir, dirs, files in os.walk(os.path.join('data', 'man')):
        if 'gramps.1.in' in files:
            filename = os.path.join(man_dir, 'gramps.1.in')
            newdir = os.path.join(build_cmd.build_base, man_dir)
            if not(os.path.isdir(newdir) or os.path.islink(newdir)):
                os.makedirs(newdir)

            newfile = os.path.join(newdir, 'gramps.1')
            subst_vars = ((u'@VERSION@', VERSION), )
            substitute_variables(filename, newfile, subst_vars)

            import gzip
            man_file_gz = os.path.join(newdir, 'gramps.1.gz')
            if os.path.exists(man_file_gz):
                if newer(newfile, man_file_gz):
                    os.remove(man_file_gz)
                else:
                    filename = False
                    os.remove(newfile)

            while filename:
                f_in = open(newfile, 'rb')
                f_out = gzip.open(man_file_gz, 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()

                os.remove(newfile)
                filename = False

            lang = man_dir[8:]
            src = build_data + 'man' + lang + os.sep + 'gramps.1.gz'
            target = os.path.join('share', 'man', lang, 'man1')
            data_files.append((target, [src]))

            log.info('Compiling %s >> %s.', src, target)

def build_intl(build_cmd):
    '''
    Merge translation files into desktop and mime files
    '''
    if intltool_version() < (0, 25, 0):
        return
    data_files = build_cmd.distribution.data_files
    base = build_cmd.build_base

    merge_files = (('data' + os.sep + 'gramps.desktop',
                    'share' + os.sep + 'applications',
                    '-d'),
                    ('data' + os.sep + 'gramps.keys',
                    'share' + os.sep + 'mime-info',
                    '-k'),
                    ('data' + os.sep + 'gramps.xml',
                    'share' + os.sep + 'mime' + os.sep + 'packages',
                    '-x'))

    for filename, target, option in merge_files:
        filename = convert_path(filename)
        newfile = os.path.join(base, filename)
        newdir = os.path.dirname(newfile)
        if not(os.path.isdir(newdir) or os.path.islink(newdir)):
            os.makedirs(newdir)
        merge(filename + '.in', newfile, option)
        data_files.append((target, [base + os.sep + filename]))

    for filename in INTLTOOL_FILES:
        filename = convert_path(filename)
        merge(filename + '.in', filename, '-x', po_dir=os.sep + 'tmp',
              cache=False)

def merge(in_file, out_file, option, po_dir='po', cache=True):
    '''
    Run the intltool-merge command.
    '''
    option += ' -u'
    if cache:
        cache_file = os.path.join('po', '.intltool-merge-cache')
        option += ' -c ' + cache_file

    if (not os.path.exists(out_file) and os.path.exists(in_file)):
        cmd = (('LC_ALL=C intltool-merge %(opt)s %(po_dir)s %(in_file)s '
                '%(out_file)s') % 
              {'opt' : option, 
               'po_dir' : po_dir,
               'in_file' : in_file, 
               'out_file' : out_file})
        if os.system(cmd) != 0:
            msg = ('ERROR: %s was not merged into the translation files!\n' % 
                    out_file)
            raise SystemExit(msg)

def install_template(install_cmd):
    '''
    Pre-install hook to populate template files.
    '''
    build_scripts = os.path.join(install_cmd.build_base, 'scripts')
    if not(os.path.isdir(build_scripts) or os.path.islink(build_scripts)):
        os.makedirs(build_scripts)
    data_files = install_cmd.distribution.data_files
    write_gramps_script(install_cmd, build_scripts)
    data_files.append(('bin', [build_scripts + os.sep + 'gramps']))
    write_const_py(install_cmd)

def write_gramps_script(install_cmd, build_scripts):
    '''
    Write the build/scripts/gramps file.
    '''
    filename = os.path.join(build_scripts, 'gramps')
    f_out = open(filename, 'w')
    f_out.write('#! /bin/sh\n')
    f_out.write('export GRAMPSDIR=%sgramps\n' % install_cmd.install_lib)
    f_out.write('exec %s -O $GRAMPSDIR/gramps.py "$@"\n' % sys.executable)
    f_out.close()

    if os.name == 'posix':
        # set read and execute bits
        mode = ((os.stat(filename)[ST_MODE]) | 0555) & 07777
        log.info('changing mode of %s to %o', filename, mode)
        os.chmod(filename, mode)

def write_const_py(install_cmd):
    '''
    Write the const.py file.
    '''
    const_py_in = os.path.join('src', 'gen', 'const.py.in')
    const_py = os.path.join('src', 'gen', 'const.py')
    if hasattr(install_cmd, 'install_data'):
        #during install
        prefix = "'%s'" % install_cmd.install_data
        sysconfdir = "'%s'" % os.path.join(install_cmd.install_data, 'etc') # Is this correct?
    else:
        #in build
        prefix = 'os.path.join(os.path.dirname(__file__), os.pardir)'
        sysconfdir = prefix + ' + "' + os.sep + 'etc"'  # Is this correct?
    
    subst_vars = ((u'@VERSIONSTRING@', VERSION), 
                  (u'"@prefix@"', prefix),
                  (u'"@sysconfdir@"', sysconfdir))
                  
    substitute_variables(const_py_in, const_py, subst_vars)

def update_posix():
    '''
    post-hook to update Linux systems after install

    these commands are not system stoppers, so there is no reason for
            system exit on failure to run.
    '''
    if os.name != 'posix':
        return
    # these commands will be ran on a Unix/ Linux system after install only...
    for cmd, options in (
            ('ldconfig',                ''),
            ('update-desktop-database', '&> /dev/null'),
            ('update-mime-database',    '/usr/share/mime &> /dev/null'),
            ('gtk-update-icon-cache',   '--quiet /usr/share/icons/hicolor')):
        sys_cmd = ('%(command)s %(opts)s') % {
                    'command' : cmd, 'opts' : options}
        os.system(sys_cmd)

class build(_build):
    """Custom build command."""
    def run(self):
        build_trans(self)
        build_man(self)
        build_intl(self)
        write_const_py(self)
        _build.run(self)

class install(_install):
    """Custom install command."""
    _install.user_options.append(('enable-packager-mode', None, 
                         'disable post-installation mime type processing'))
    _install.boolean_options.append('enable-packager-mode')

    def initialize_options(self):
        _install.initialize_options(self)
        self.enable_packager_mode = False

    def run(self):
        install_template(self)
        _install.run(self)
        if self.enable_packager_mode:
            log.warn('WARNING: Packager mode enabled.  Post-installation mime '
                            'type processing was not run.')
        else:
            update_posix()

DOC_FILES = ['AUTHORS', 'COPYING', 'FAQ', 'INSTALL', 'LICENSE', 'NEWS',
             'README', 'TODO']
GEDCOM_FILES = glob.glob(os.path.join('example', 'gedcom', '*.*'))
GRAMPS_FILES = glob.glob(os.path.join('example', 'gramps', '*.*'))
PNG_FILES = glob.glob(os.path.join('data', '*.png'))
SVG_FILES = glob.glob(os.path.join('data', '*.svg'))

data_list = [
            os.path.join('data', '*.txt'), 
            os.path.join('data', '*.xml'),
            os.path.join('gui', 'glade', '*.glade'), 
            os.path.join('images','*.ico'), 
            os.path.join('images', '*.png'),
            os.path.join('images', 'splash.jpg'), 
            os.path.join('images', '*.svg'), 
            os.path.join('images', '16x16', '*.png'), 
            os.path.join('images', '22x22', '*.png'), 
            os.path.join('images', '48x48', '*.png'), 
            os.path.join('images', 'scalable', '*.svg')
            ]

# add all subdirs of plugin with glade:
basedir = os.path.join('src', 'plugins')
for (dirpath, dirnames, filenames) in os.walk(basedir):
    root, subdir = os.path.split(dirpath)
    if subdir.startswith("."): 
        dirnames[:] = []
        continue
    for dirname in dirnames:
        # Skip hidden and system directories:
        if dirname.startswith("."):
            dirnames.remove(dirname)
        #we add to data_list so glade , xml, files are found, we don't need the src/ part
        data_list.append(os.path.join(dirpath[4:], '*.glade'))
        data_list.append(os.path.join(dirpath[4:], '*.xml'))
        data_list.append(os.path.join(dirpath[4:], '*.png'))
        data_list.append(os.path.join(dirpath[4:], '*.svg'))
        data_list.append(os.path.join(dirpath[4:], '*.css'))
        data_list.append(os.path.join(dirpath[4:], '*.html'))
        data_list.append(os.path.join(dirpath[4:], '*.js'))
data_list.append(os.path.join('plugins', 'webstuff', 'images', '*.gif'))
data_list.append(os.path.join('plugins', 'webstuff', 'images', '*.ico'))
#                               'plugins' + os.sep + '*.glade', 
#                               'plugins' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'docgen' + os.sep + '*.glade', 
#                               'plugins' + os.sep + 'docgen' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'drawreport' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'export' + os.sep + '*.glade', 
#                               'plugins' + os.sep + 'export' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'gramplet' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'graph' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'import' + os.sep + '*.glade', 
#                               'plugins' + os.sep + 'import' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'lib' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'lib' + os.sep + '*.xml', 
#                               'plugins' + os.sep + 'lib' + os.sep + 'maps' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'mapservices' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'quickview' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'rel' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'sidebar' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'textreport' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'tool' + os.sep + '*.glade', 
#                               'plugins' + os.sep + 'tool' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'view' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'webreport' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'webstuff' + os.sep + '*.html', 
#                               'plugins' + os.sep + 'webstuff' + os.sep + '*.py', 
#                               'plugins' + os.sep + 'webstuff' + os.sep + 'css' 
#                                    + os.sep + '*.css', 
#                               'plugins' + os.sep + 'webstuff' + os.sep + 'css' 
#                                    + os.sep + 'swanky-purse' + os.sep + '*.css', 
#                               'plugins' + os.sep + 'webstuff' + os.sep + 'css'
#                                    + os.sep + 'swanky-purse' + os.sep + 'images' + os.sep + '*.png',
#                               'plugins' + os.sep + 'webstuff' + os.sep + 'images'
#                                    + os.sep + '*.png', 
#                               'plugins' + os.sep + 'webstuff' + os.sep + 'images'
#                                    + os.sep + '*.svg', 
#                               'plugins' + os.sep + 'webstuff' + os.sep + 'javascript'
#                                    + os.sep + '*.js']

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
      cmdclass = {'build': build, 'install': install},
      package_dir = {'gramps': 'src'}, 
      packages = ['gramps',
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
            'gramps.gui',
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
            'gramps.test',
            'gramps.plugins', 
            'gramps.plugins.docgen', 
            'gramps.plugins.drawreport', 
            'gramps.plugins.export', 
            'gramps.plugins.gramplet', 
            'gramps.plugins.graph',
            'gramps.plugins.import', 
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
            ],
      package_data={'gramps': data_list},
      data_files=[('share' + os.sep + 'mime-info', 
                        ['data' + os.sep + 'gramps.mime']),
                  ('share' + os.sep + 'icons' + os.sep + 'gnome' + os.sep 
                    + '48x48' + os.sep + 'mimetypes', PNG_FILES), 
                  ('share' + os.sep + 'icons' + os.sep + 'gnome' + os.sep 
                    + 'scalable' + os.sep + 'mimetypes', SVG_FILES), 
                  ('share' + os.sep + 'icons', ['src' + os.sep + 'images' 
                    + os.sep + 'gramps.png']), 
                  ('share' + os.sep + 'doc' + os.sep + 'gramps' + os.sep 
                    + 'example' + os.sep + 'gedcom', GEDCOM_FILES), 
                  ('share' + os.sep + 'doc' + os.sep + 'gramps' + os.sep 
                    + 'example' + os.sep + 'gramps', GRAMPS_FILES), 
                  ('share' + os.sep + 'doc' + os.sep + 'gramps', DOC_FILES)]
)
