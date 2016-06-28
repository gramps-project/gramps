#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
# Copyright (C) 2014       Vassilii Khachaturov
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Provide an interface to the gtkspell interface. This requires
python-gnome-extras package. If the gtkspell package is not
present, we default to no spell checking.

"""

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".Spell")

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi import Repository

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

HAVE_GTKSPELL = False

# Attempting to import gtkspell gives an error dialog if gtkspell is not
# available so test first and log just a warning to the console instead.
repository = Repository.get_default()
if repository.enumerate_versions("GtkSpell"):
    try:
        import gi
        gi.require_version('GtkSpell', '3.0')
        from gi.repository import GtkSpell as Gtkspell
        HAVE_GTKSPELL = True
    except:
        pass
elif repository.enumerate_versions("Gtkspell"):
    try:
        import gi
        gi.require_version('Gtkspell', '3.0')
        from gi.repository import Gtkspell
        HAVE_GTKSPELL = True
    except:
        pass

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.config import config

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class Spell:
    """Attach a gtkspell instance to the passed TextView instance.
    """
    _spellcheck_options = {'off': _('Off')}

    if HAVE_GTKSPELL:
        _spellcheck_options['on'] = _('On')

    def __init__(self, textview):
        self.textview = textview

        if HAVE_GTKSPELL and config.get('behavior.spellcheck'):
            self.spellcheck = 'on'
        else:
            self.spellcheck = 'off'

        self._active_spellcheck = 'off'
        self.__real_set_active_spellcheck(self.spellcheck)

    # Private

    def __real_set_active_spellcheck(self, spellcheck_code):
        """Set active spellcheck by its code."""
        if self._active_spellcheck == 'off':
            if spellcheck_code == 'off':
                return
            else:
                try:
                    #transfer full GTK object, so assign to an attribute!
                    if Gtkspell._namespace == "Gtkspell":
                        self.gtkspell_spell = Gtkspell.Spell.new()
                    elif Gtkspell._namespace == "GtkSpell":
                        self.gtkspell_spell = Gtkspell.Checker.new()
                        try:
                            #check for dictionary in system locale (LANG)
                            #if exist it will be default one
                            self.gtkspell_spell.set_language(None)
                            #TODO: use "get_language_list" for use when there
                            #is no English or systemlocale one
                        except:
                            #else check for English dictionary
                            #if exist it will be default one
                            #other installed one will also be available
                            self.gtkspell_spell.set_language("en")
                            #if that fails no spellchecker will be available
                    with self.textview.undo_disabled():
                        success = self.gtkspell_spell.attach(self.textview)
                    try:
                        #show decoded language codes in the context menu
                        #requires the iso-codes package from  http://pkg-isocodes.alioth.debian.org
                        self.gtkspell_spell.set_property("decode-language-codes", True)
                    except TypeError:
                        #available in GtkSpell since version 3.0.3 (2013-06-04)
                        pass
                    self._active_spellcheck = spellcheck_code
                except Exception as err:
                    # attaching the spellchecker will fail if
                    # the language does not exist
                    # and presumably if there is no dictionary
                    if not self.gtkspell_spell.get_language_list():
                        LOG.warning(_("You have no installed dictionaries. "
                                      "Either install one or disable spell "
                                      "checking"))
                    else:
                        LOG.warning(_("Spelling checker initialization "
                                      "failed: %s"), err)
        else:
            if spellcheck_code == 'on':
                return
            else:
                    if Gtkspell._namespace == "Gtkspell":
                        self.gtkspell_spell = Gtkspell.Spell.get_from_text_view(self.textview)
                    elif Gtkspell._namespace == "GtkSpell":
                        self.gtkspell_spell = Gtkspell.Checker.get_from_text_view(self.textview)
                    self.gtkspell_spell.detach()
                    self._active_spellcheck = spellcheck_code

    # Public API

    def get_all_spellchecks(self):
        """Get the list of installed spellcheck names."""
        return list(self._spellcheck_options.values())

    def set_active_spellcheck(self, spellcheck):
        """Set active spellcheck by it's name."""
        for code, name in list(self._spellcheck_options.items()):
            if name == spellcheck:
                self.__real_set_active_spellcheck(code)
                return

    def get_active_spellcheck(self):
        """Get the name of the active spellcheck."""
        return self._spellcheck_options[self._active_spellcheck]
