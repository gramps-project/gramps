#! /usr/bin/python -O

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

import traceback
import GdkImlib
import gtk
import gnome.ui
import gnome.config
import gramps_main 
import sys

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
    traceback.print_exc()
        
    fname = os.path.expanduser("~/gramps.err")
    errfile = open(fname,"w")
    traceback.print_exc(file=errfile)
    errfile.close()

gtk.mainloop()

