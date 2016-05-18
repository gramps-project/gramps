#! /usr/bin/env python
#
# update_po - a gramps tool to update translations
#
# Copyright (C) 2006-2006  Kees Bakker
# Copyright (C) 2006       Brian Matherly
# Copyright (C) 2008       Stephen George
# Copyright (C) 2012
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

"""
update_man.py for command line documentation.

Examples:
   python update_man.py -t

      Tests if 'sphinx' and 'python' are well configured.
"""

from __future__ import print_function

import os
import sys
from argparse import ArgumentParser

DOCUTILS = True
try:
    import docutils.core, docutils.writers
except:
    DOCUTILS = False

LANGUAGES = ['sv', 'nl', 'pl', 'cs', 'pt_BR', 'fr']
VERSION = '5.0.0'
DATE = ''

# You can set these variables from the command line.
SPHINXBUILD   = 'sphinx-build'

if sys.platform == 'win32':
    pythonCmd = os.path.join(sys.prefix, 'bin', 'python.exe')
    sphinxCmd = os.path.join(sys.prefix, 'bin', 'sphinx-build.exe')
elif sys.platform in ['linux2', 'darwin', 'cygwin']:
    pythonCmd = os.path.join(sys.prefix, 'bin', 'python')
    sphinxCmd = SPHINXBUILD
else:
    print ("Update Man ERROR: unknown system, don't know sphinx, ... commands")
    sys.exit(0)

def tests():
    """
    Testing installed programs.
    We made tests (-t flag) by displaying versions of tools if properly
    installed. Cannot run all commands without 'sphinx' and 'python'.
    """
    try:
        print("\n=================='python'=============================\n")
        os.system('''%(program)s -V''' % {'program': pythonCmd})
    except:
        print ('Please, install python')

    try:
        print("\n=================='Sphinx-build'=============================\n")
        os.system('''%(program)s''' % {'program': sphinxCmd})
    except:
        print ('Please, install sphinx')

    if not DOCUTILS:
        print('\nNo docutils support, cannot use -m/--man and -o/--odt arguments.')

def main():
    """
    The utility for handling documentation stuff.
    What is need by Gramps, nothing more.
    """

    parser = ArgumentParser(
                         description='This program aims to handle documentation'
                                      ' and related translated versions.',
                         )

    parser.add_argument("-t", "--test",
            action="store_true", dest="test",  default=True,
            help="test if 'python' and 'sphinx' are properly installed")

    parser.add_argument("-b", "--build",
            action="store_true", dest="build",  default=False,
            help="build man documentation (via sphinx-build)")

    parser.add_argument("-m", "--man",
            action="store_true", dest="man",  default=False,
            help="build man documentation (via docutils)")

    parser.add_argument("-o", "--odt",
            action="store_true", dest="odt",  default=False,
            help="build odt documentation (via docutils)")

    args = parser.parse_args()

    if args.test:
        tests()

    if args.build:
        build()

    if args.man and DOCUTILS:
        man()

    if args.odt and DOCUTILS:
        odt()

def build():
    """
    Build documentation.
    """

    # testing stage

    os.system('''%(program)s -b html . _build/html''' % {'program': sphinxCmd})
    os.system('''%(program)s -b htmlhelp . _build/htmlhelp''' % {'program': sphinxCmd})
    if DOCUTILS:
        os.system('''%(program)s -b man . .''' % {'program': sphinxCmd})
    os.system('''%(program)s -b text . _build/text''' % {'program': sphinxCmd})
    os.system('''%(program)s -b changes . _build/changes''' % {'program': sphinxCmd})
    #os.system('''%(program)s -b linkcheck . _build/linkcheck''' % {'program': sphinxCmd})
    os.system('''%(program)s -b gettext . _build/gettext''' % {'program': sphinxCmd})

    for lang in LANGUAGES:
        os.system('''%(program)s -b html -D language="%(lang)s" master_doc="%(lang)s" %(lang)s %(lang)s'''
                   % {'lang': lang, 'program': sphinxCmd})
        os.system('''%(program)s -b htmlhelp -D language="%(lang)s" master_doc="%(lang)s" %(lang)s %(lang)s'''
                   % {'lang': lang, 'program': sphinxCmd})
        if DOCUTILS:
            os.system('''%(program)s -b man %(lang)s %(lang)s'''
                       % {'lang': lang, 'program': sphinxCmd})
        os.system('''%(program)s -b text -D language="%(lang)s" master_doc="%(lang)s" %(lang)s %(lang)s'''
                   % {'lang': lang, 'program': sphinxCmd})
        # for update/migration
        os.system('''%(program)s -b gettext -D language="%(lang)s" master_doc="%(lang)s" . _build/gettext/%(lang)s'''
                   % {'lang': lang, 'program': sphinxCmd})

def man():
    """
    man file generation via docutils (python)

    from docutils.core import publish_cmdline, default_description
    from docutils.writers import manpage
    """

    os.system('''rst2man en.rst gramps.1''')

    for lang in LANGUAGES:
        os.system('''rst2man %(lang)s/%(lang)s.rst -l %(lang)s %(lang)s/gramps.1'''
                   % {'lang': lang})

def odt():
    """
    odt file generation via docutils (python)

    from docutils.core import publish_cmdline_to_binary, default_description
    from docutils.writers.odf_odt import Writer, Reader
    """

    os.system('''rst2odt en.rst gramps.odt''')

    for lang in LANGUAGES:
        os.system('''rst2odt %(lang)s/%(lang)s.rst -l %(lang)s %(lang)s/gramps.odt'''
                   % {'lang': lang})

if __name__ == "__main__":
    main()
