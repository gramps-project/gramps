#! /usr/bin/python -O

import traceback
import intl
import os

intl.textdomain("gramps")
_ = intl.gettext

if os.environ.has_key("GRAMPSI18N"):
    locale = os.environ["GRAMPSI18N"]
else:
    locale = "locale"
    
intl.bindtextdomain("gramps",locale)

import gramps_main 
import sys

try:
    if len(sys.argv) > 1:
        gramps_main.main(sys.argv[1])
    else:
        gramps_main.main(None)
except:

    fname = os.path.expanduser("~/gramps.err")
    errfile = open(fname,"w")
    traceback.print_exc(file=errfile)
    errfile.close()

    import gnome.ui

    msg1 = _("gramps has encountered an internal error.")
    msg2 = _("The error log has been saved to %s.") % fname
    gnome.ui.GnomeWarningDialog("%s\n%s" % (msg1,msg2))
