#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012 Nick Hall
# Copyright (C) 2012 Rob G. Healey <robhealey1@gmail.com>
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
from distutils import log
from distutils.core import setup
from distutils.util import convert_path, newer
from distutils.command.build import build as _build
from distutils.command.install import install as _install
import os
import sys
import glob
import codecs
import commands

# determine if the computer has ability to change file permissions or not?
if hasattr(os, 'chmod'):
    _has_chmod = True
else:
    _has_chmod = False

VERSION = '3.5.0'
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

        target = 'share/locale/' + lang + '/LC_MESSAGES'
        data_files.append((target, [mo_file]))

        log.info('Compiling %s >> %s.', po_file, target)

def build_man(build_cmd):
    '''
    Compresses Gramps manual files
    '''
    data_files = build_cmd.distribution.data_files
    build_data = build_cmd.build_base + '/data/'
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
            src = build_data + 'man' + lang + '/gramps.1.gz'
            target = 'share/man/' + lang + '/man1'
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

    merge_files = (('data/gramps.desktop',
                    'share/applications',
                    '-d'),
                    ('data/gramps.keys',
                    'share/mime-info',
                    '-k'),
                    ('data/gramps.xml',
                    'share/mime/packages',
                    '-x'))

    for filename, target, option in merge_files:
        filename = convert_path(filename)
        newfile = os.path.join(base, filename)
        newdir = os.path.dirname(newfile)
        if not(os.path.isdir(newdir) or os.path.islink(newdir)):
            os.makedirs(newdir)
        merge(filename + '.in', newfile, option)
        data_files.append((target, [base + '/' + filename]))

    for filename in INTLTOOL_FILES:
        filename = convert_path(filename)
        merge(filename + '.in', filename, '-x', po_dir='/tmp', cache=False)

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
    data_files.append(('bin', [build_scripts + '/gramps']))
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

    # set eXecute bit for gramps startup script...
    # this is required for both Linux and MacOS 
    if _has_chmod:
        log.info('Changing permissions of %s from 644 to 775', filename)
        os.chmod(filename, 0775)

def write_const_py(install_cmd):
    '''
    Write the const.py file.
    '''
    const_py_in = os.path.join('src', 'const.py.in')
    const_py = os.path.join('src', 'const.py')
    prefix = install_cmd.install_data
    sysconfdir = os.path.join(prefix, 'etc') # Is this correct?
    
    subst_vars = ((u'@VERSIONSTRING@', VERSION), 
                  (u'@prefix@', prefix),
                  (u'@sysconfdir@', sysconfdir))
                  
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

        # change permissions of build directory after installation
        # so it can be deleted by normal user...
        if _has_chmod:
            os.system('chmod -R 777 build')

DOC_FILES = ['AUTHORS', 'COPYING', 'FAQ', 'INSTALL', 'NEWS', 'README', 'TODO']
GEDCOM_FILES = glob.glob(os.path.join('example', 'gedcom', '*.*'))
GRAMPS_FILES = glob.glob(os.path.join('example', 'gramps', '*.*'))
PNG_FILES = glob.glob(os.path.join('data', '*.png'))
SVG_FILES = glob.glob(os.path.join('data', '*.svg'))

setup(name = 'gramps', 
      description = ('Gramps (Genealogical Research and Analysis Management '
                     'Programming System)'), 
      long_description = ('Gramps (Genealogical Research and Analysis '
                          'Management Programming System) is a GNOME based '
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
                  'gramps.DateHandler', 
                  'gramps.Filters', 
                  'gramps.Filters.Rules', 
                  'gramps.Filters.Rules.Citation', 
                  'gramps.Filters.Rules.Event', 
                  'gramps.Filters.Rules.Family', 
                  'gramps.Filters.Rules.MediaObject', 
                  'gramps.Filters.Rules.Note', 
                  'gramps.Filters.Rules.Person', 
                  'gramps.Filters.Rules.Place', 
                  'gramps.Filters.Rules.Repository', 
                  'gramps.Filters.Rules.Source', 
                  'gramps.Filters.SideBar', 
                  'gramps.GrampsLocale', 
                  'gramps.GrampsLogger', 
                  'gramps.Merge', 
                  'gramps.Simple', 
                  'gramps.cli', 
                  'gramps.cli.plug', 
                  'gramps.docgen', 
                  'gramps.gen', 
                  'gramps.gen.db', 
                  'gramps.gen.display', 
                  'gramps.gen.lib', 
                  'gramps.gen.mime', 
                  'gramps.gen.plug', 
                  'gramps.gen.plug.docbackend', 
                  'gramps.gen.plug.docgen', 
                  'gramps.gen.plug.menu', 
                  'gramps.gen.plug.report', 
                  'gramps.gen.proxy', 
                  'gramps.gen.utils', 
                  'gramps.gui', 
                  'gramps.gui.editors', 
                  'gramps.gui.editors.displaytabs', 
                  'gramps.gui.plug', 
                  'gramps.gui.plug.report', 
                  'gramps.gui.selectors', 
                  'gramps.gui.views', 
                  'gramps.gui.views.treemodels', 
                  'gramps.gui.widgets'],
      package_data={'gramps': ['data/*.txt', 
                               'data/*.xml',
                               'data/templates/*.html', 
                               'data/templates/registration/*.html', 
                               'glade/*.glade', 
                               'images/*.ico', 
                               'images/*.png', 
                               'images/*.svg', 
                               'images/16x16/*.png', 
                               'images/22x22/*.png', 
                               'images/48x48/*.png', 
                               'images/scalable/*.svg', 
                               'plugins/*.glade', 
                               'plugins/*.py', 
                               'plugins/docgen/*.glade', 
                               'plugins/docgen/*.py', 
                               'plugins/drawreport/*.py', 
                               'plugins/export/*.glade', 
                               'plugins/export/*.py', 
                               'plugins/gramplet/*.py', 
                               'plugins/graph/*.py', 
                               'plugins/import/*.glade', 
                               'plugins/import/*.py', 
                               'plugins/lib/*.py', 
                               'plugins/lib/*.xml', 
                               'plugins/lib/maps/*.py', 
                               'plugins/mapservices/*.py', 
                               'plugins/quickview/*.py', 
                               'plugins/rel/*.py', 
                               'plugins/sidebar/*.py', 
                               'plugins/textreport/*.py', 
                               'plugins/tool/*.glade', 
                               'plugins/tool/*.py', 
                               'plugins/view/*.py', 
                               'plugins/webreport/*.py', 
                               'plugins/webstuff/*.html', 
                               'plugins/webstuff/*.py', 
                               'plugins/webstuff/css/*.css', 
                               'plugins/webstuff/css/swanky-purse/*.css', 
                               'plugins/webstuff/css/swanky-purse/images/*.png',
                               'plugins/webstuff/images/*.gif', 
                               'plugins/webstuff/images/*.ico', 
                               'plugins/webstuff/images/*.png', 
                               'plugins/webstuff/images/*.svg', 
                               'plugins/webstuff/javascript/*.js']},
      data_files=[('share/mime-info', ['data/gramps.mime']),
                  ('share/icons/gnome/48x48/mimetypes', PNG_FILES), 
                  ('share/icons/gnome/scalable/mimetypes', SVG_FILES), 
                  ('share/icons', ['src/images/gramps.png']), 
                  ('share/doc/gramps/example/gedcom', GEDCOM_FILES), 
                  ('share/doc/gramps/example/gramps', GRAMPS_FILES), 
                  ('share/doc/gramps', DOC_FILES)]
)
