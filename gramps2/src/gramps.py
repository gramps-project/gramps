#! /usr/bin/python -O
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allinghamg
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

import sys
import os
import locale

try:
    import pygtk
    pygtk.require('2.0')
except ImportError:
    pass

import gtk.glade
import intl

#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------
if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
else:
    loc = "/usr/share/locale"

intl.bindtextdomain("gramps",loc)
intl.bind_textdomain_codeset("gramps",'UTF-8')
intl.textdomain("gramps")
locale.setlocale(locale.LC_NUMERIC,"C")

#-------------------------------------------------------------------------
#
# Cope with versioned pygtk installation.
#
#-------------------------------------------------------------------------

import gtk

#-------------------------------------------------------------------------
#
# gramps libraries
#
#-------------------------------------------------------------------------
import gramps_main 

args = sys.argv[1:]

try:
    import StartupDialog
    
    if StartupDialog.need_to_run():
        StartupDialog.StartupDialog(gramps_main.Gramps,args)
    else:
        gramps_main.Gramps(args)
except:
    import DisplayTrace
    DisplayTrace.DisplayTrace()

gtk.mainloop()
