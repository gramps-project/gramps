#! /usr/bin/python -O

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

#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------
import os
import locale

try:
    import pygtk; pygtk.require('2.0')
except ImportError: # not set up for parallel install
    pass 

import gtk.glade
import intl

if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
else:
    loc = "locale"


intl.bindtextdomain("gramps",loc)
intl.bind_textdomain_codeset("gramps",'UTF-8')
intl.textdomain("gramps")
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
try:
    import pygtk; pygtk.require('2.0')
except ImportError: # not set up for parallel install
    pass 

import gtk
import gnome.ui

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
