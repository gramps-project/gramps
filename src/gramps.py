#! /usr/bin/python -O

import const
import sys
import os
import locale
import intl

#-------------------------------------------------------------------------
#
# Cope with versioned pygtk installation.
#
#-------------------------------------------------------------------------
try:
    import pygtk
    pygtk.require('2.0')
except ImportError:
    pass

import gtk

#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------
if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
else:
    loc = "locale"

#-------------------------------------------------------------------------
#
# gramps libraries
#
#-------------------------------------------------------------------------
import gramps_main 
import const

if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = None

intl.bindtextdomain("gramps",loc)
intl.bind_textdomain_codeset("gramps",'UTF-8')
intl.textdomain("gramps")
locale.setlocale(locale.LC_NUMERIC,"C")

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
