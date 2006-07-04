#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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

"Report Generation Framework"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# Support for printing generated files
#
#-------------------------------------------------------------------------
def get_print_dialog_app ():
    """Return the name of a program which sends stdin (or the program's
    arguments) to the printer."""
    for printdialog in ["/usr/bin/kprinter --stdin",
                        "/usr/share/printconf/util/print.py"]:
        if os.access (printdialog.split (' ')[0], os.X_OK):
            return printdialog

    return "lpr"

def run_print_dialog (filename):
    """Send file to the printer, possibly throwing up a dialog to
    ask which one etc."""
    os.environ["FILE"] = filename
    return os.system ('cat "$FILE" | %s &' % get_print_dialog_app ())
