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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import subprocess

def get_git_revision(path="", history=100, 
                     delim="alpha",
                     format="--date=short --format=%cd"):
    stdout = ""
    command = "git log -%s %s" % (history, format)
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
            stdout = stdout.decode("utf-8", errors = 'replace')
        except UnicodeDecodeError:
            pass
        if stdout:
            count = 0
            date = None
            for line in str.splitlines(stdout):
                if count == 0:
                    date = line
                elif line != date:
                    break
                count += 1
            return delim + date.replace("-", "") + ("%03d" % count)
        else:
            return ""
    else: # no output from git log
        return ""

