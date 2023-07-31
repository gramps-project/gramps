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
Provide an interface to the gspell interface. If the gspell package is not
present, we default to no spell checking.

"""

# -------------------------------------------------------------------------
#
# Python classes
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Set up logging
#
# -------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".Spell")

# -------------------------------------------------------------------------
#
# GTK libraries
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

HAVE_GSPELL = False

try:
    import gi

    gi.require_version("Gspell", "1")
    from gi.repository import Gspell

    langs = Gspell.language_get_available()
    for lang in langs:
        LOG.debug("%s (%s) dict available", lang.get_name(), lang.get_code())
    if langs:
        HAVE_GSPELL = True
    else:
        LOG.warning(_("You have no installed dictionaries."))
except (ImportError, ValueError):
    pass

# -------------------------------------------------------------------------
#
# Gramps classes
#
# -------------------------------------------------------------------------
from gramps.gen.config import config

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------


class Spell:
    """Attach a Gspell instance to the passed TextView instance."""

    _spellcheck_options = {"off": _("Off")}

    if HAVE_GSPELL:
        _spellcheck_options["on"] = _("On")

    def __init__(self, textview):
        self._active_spellcheck = "off"

        if not HAVE_GSPELL:
            return

        locale_code = glocale.locale_code()
        gspell_language = None
        if locale_code is not None:
            gspell_language = Gspell.language_lookup(locale_code[:5])
            if gspell_language is None:
                gspell_language = Gspell.language_lookup(locale_code[:2])
        checker = Gspell.Checker.new(gspell_language)
        buffer = Gspell.TextBuffer.get_from_gtk_text_buffer(textview.get_buffer())
        buffer.set_spell_checker(checker)
        self.gspell_view = Gspell.TextView.get_from_gtk_text_view(textview)

        if config.get("behavior.spellcheck"):
            self.spellcheck = "on"
        else:
            self.spellcheck = "off"

        self.__real_set_active_spellcheck(self.spellcheck)

    # Private

    def __real_set_active_spellcheck(self, spellcheck_code):
        """Set active spellcheck by its code."""
        if self._active_spellcheck == spellcheck_code:
            return

        self.gspell_view.set_inline_spell_checking(spellcheck_code == "on")
        self.gspell_view.set_enable_language_menu(spellcheck_code == "on")
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
