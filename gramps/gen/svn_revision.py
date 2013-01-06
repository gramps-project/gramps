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

import sys
import subprocess

if sys.version_info[0] < 3:
    cuni = unicode
else:
    def to_utf8(s):
        return s.decode("utf-8")
    cuni = to_utf8

def get_svn_revision(path=""):
    stdout = ""
    try:
        p = subprocess.Popen("svnversion -n \"%s\"" % path, shell=True, 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
    except:
        return "" # subprocess failed
    # subprocess worked
    if stdout: # has output
        stdout = cuni(stdout) # get a proper string
        if " " in stdout: # one of svnversion's non-version responses:
            # 'Unversioned directory'
            # 'Unversioned file'
            # 'Uncommitted local addition, copy or move'
            return ""
        else:
            return "-r" + stdout
    else: # no output from svnversion
        return ""

