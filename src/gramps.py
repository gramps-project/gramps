#! /usr/bin/python -O

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

if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = None

try:
    import StartupDialog
    
    if StartupDialog.need_to_run():
        StartupDialog.StartupDialog(gramps_main.Gramps,arg)
    else:
        gramps_main.Gramps(arg)
except:
    import DisplayTrace
    DisplayTrace.DisplayTrace()

gtk.mainloop()
