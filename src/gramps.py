#! /usr/bin/python -O

import traceback
import intl
import os
import gtk
import gnome.ui
import locale

if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
else:
    loc = "locale"
    
intl.textdomain("gramps")
intl.bindtextdomain("gramps",loc)

locale.setlocale(locale.LC_NUMERIC,"C")

import gramps_main 
import sys
import locale

try:
    if len(sys.argv) > 1:
        gramps_main.main(sys.argv[1])
    else:
        gramps_main.main(None)
except:
    traceback.print_exc()
        
    fname = os.path.expanduser("~/gramps.err")
    errfile = open(fname,"w")
    traceback.print_exc(file=errfile)
    errfile.close()


