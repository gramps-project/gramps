#! /usr/bin/python -O

#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------
import os
import intl
import locale

if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
else:
    loc = "locale"

intl.textdomain("gramps")
intl.bindtextdomain("gramps",loc)
locale.setlocale(locale.LC_NUMERIC,"C")

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys

#-------------------------------------------------------------------------
#
# GNOME/GTK libraries
#
#-------------------------------------------------------------------------
import gtk
import gnome.ui
import gnome.config

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

