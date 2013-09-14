# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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

from __future__ import unicode_literals

import sys
import subprocess
import re

if sys.version_info[0] < 3:
    cuni = unicode
else:
    def to_utf8(s):
        return s.decode("utf-8", errors = 'replace')
    cuni = to_utf8

def _get_svn_revision(path, command, stdout_to_rev):
    stdout = ""
    try:
        p = subprocess.Popen(
                "{} \"{}\"".format(command, path),
                shell=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
    except:
        return "" # subprocess failed
    # subprocess worked
    if stdout and len(stdout) > 0: # has output
        try:
            stdout = cuni(stdout) # get a proper string
        except UnicodeDecodeError:
            pass
        rev = stdout_to_rev(stdout)
        return "-r" + rev if rev else ""
    else: # no output from svnversion
        return ""

def get_svn_revision(path=""):
    return _get_svn_revision(path, "svnversion -n",
            lambda stdout: stdout if stdout[0].isdigit() else ""
            ) or get_git_svn_revision(path)

def get_git_svn_revision(path=""):
    def stdout_to_rev(stdout):
        m = re.search("Revision:\s+(\d+)", stdout, re.MULTILINE)
        return m.group(1) if m else ""

    return _get_svn_revision(path, "git svn info", stdout_to_rev)
