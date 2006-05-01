#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
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

# $Id$

"""
Provide an interface to the gtkspell interface. This requires
python-gnome-extras package. If the gtkspell package is not
present, we default to no spell checking.

"""

import Config

from gettext import gettext as _

#-----------------------------------------------------------
#
# Attempt to instantiate a gtkspell instance to check for
# any errors. If it succeeds, set a success flag so that we
# know to use the spelling check in the future
#
#------------------------------------------------------------

success = False
try:
    import gtk
    import gtkspell
    import locale

    lang = locale.getlocale()[0]
    if lang == None:
        print _("Spelling checker cannot be used without language set.")
        print _("Set your locale appropriately to use spelling checker.")
    else:
        gtkspell.Spell(gtk.TextView()).set_language(lang)
        success = True
except ImportError, msg:
    print _("Spelling checker is not installed")
except TypeError,msg:
    print "Spell.py: ", msg
except RuntimeError,msg:
    print "Spell.py: ", msg
except SystemError,msg:
    msg = _("Spelling checker is not available for %s") % lang
    print "Spell.py: %s" % msg

#-----------------------------------------------------------
#
# Spell - if the initial test succeeded, attach a gtkspell
#         instance to the passed TextView instance
#
#------------------------------------------------------------
class Spell:

    def __init__(self,obj):
        if success and Config.get(Config.SPELLCHECK):
            self.spell = gtkspell.Spell(obj)
            lang = locale.getlocale()[0]
            self.spell.set_language(lang)
