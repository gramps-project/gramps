#! /usr/bin/env python3
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
update_doc.py for Gramps API(s) documentation.

Examples:
   python update_doc.py -t

      Tests if 'sphinx' and 'python' are well configured.
"""

from __future__ import print_function

import os
import sys
from argparse import ArgumentParser

# You can set these variables from the command line.
SPHINXBUILD = "sphinx-build"

if sys.platform == "win32":
    pythonCmd = os.path.join(sys.prefix, "bin", "python.exe")
    sphinxCmd = os.path.join(sys.prefix, "bin", "sphinx-build.exe")
elif sys.platform in ["linux", "linux2", "darwin", "cygwin"]:
    pythonCmd = os.path.join(sys.prefix, "bin", "python")
    sphinxCmd = SPHINXBUILD
else:
    print("Update Docs ERROR: unknown system, don't know sphinx, ... commands")
    sys.exit(0)


def tests():
    """
    Testing installed programs.
    We made tests (-t flag) by displaying versions of tools if properly
    installed. Cannot run all commands without 'sphinx' and 'python'.
    """
    try:
        print("\n=================='python'=============================\n")
        os.system("""%(program)s -V""" % {"program": pythonCmd})
    except:
        print("Please, install python")

    try:
        print("\n=================='sphinx-build'=============================\n")
        os.system("""%(program)s""" % {"program": sphinxCmd})
    except:
        print("Please, install sphinx")


def main():
    """
    The utility for handling documentation stuff.
    What is need by Gramps, nothing more.
    """

    parser = ArgumentParser(
        description="This program aims to handle manual" " and translated version.",
    )

    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        dest="test",
        default=True,
        help="test if 'python' and 'sphinx' are properly installed",
    )

    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        dest="build",
        default=True,
        help="build documentation",
    )

    args = parser.parse_args()

    if args.test:
        tests()

    if args.build:
        build()


def build():
    """
    Build documentation.
    """

    # testing stage

    os.system("""%(program)s -b html . _build/html""" % {"program": sphinxCmd})
    # os.system('''%(program)s -b changes . _build/changes''' % {'program': sphinxCmd})
    # os.system('''%(program)s -b linkcheck . _build/linkcheck''' % {'program': sphinxCmd})
    # os.system('''%(program)s -b devhelp . _build/devhelp''' % {'program': sphinxCmd})


if __name__ == "__main__":
    main()
