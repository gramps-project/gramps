import sys

ver = sys.version[0:3]

try:
    if ver == "1.5":
        from intl15 import *
    elif ver == "2.0":
        from intl20 import *
    elif ver == "2.1":
        from intl21 import *
    else:
        def gettext(s):
            return s

        def textdomain(s):
            return

        def bindtextdomain(s,x):
            return
except:
    def gettext(s):
        return s
    
    def textdomain(s):
        return
    
    def bindtextdomain(s,x):
        return
