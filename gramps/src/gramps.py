#! /usr/bin/python -O

import intl
import os

intl.textdomain("gramps")

if os.environ.has_key("GRAMPSI18N"):
    locale = os.environ["GRAMPSI18N"]
else:
    locale = "locale"
    
intl.bindtextdomain("gramps",locale)

import gramps_main 
import sys

if len(sys.argv) > 1:
    gramps_main.main(sys.argv[1])
else:
    gramps_main.main(None)
