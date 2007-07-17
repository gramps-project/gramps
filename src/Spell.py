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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import locale

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".Spell")

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
try:
    import gtkspell
    HAVE_GTKSPELL = True
except ImportError:
    log.warn(_("Spelling checker is not installed"))
    HAVE_GTKSPELL = False

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import Config

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
LANGUAGES = {
    'da': _('Danish'),
    'de': _('German'),
    'en': _('English'),
    'es': _('Spanish'),
    'fi': _('Finnish'),
    'fr': _('French'),
    'it': _('Italian'),
    'la': _('Latin'),
    'nl': _('Dutch'),
    'nn': _('Norwegian'),
    'ru': _('Russian'),
    'sv': _('Swedish'),
}

class Spell:
    """Attach a gtkspell instance to the passed TextView instance.
    """
    _LANG = locale.getlocale()[0]
    
    _installed_languages = {'off': _('None')}

    if HAVE_GTKSPELL:
        for lang_code, lang_name in LANGUAGES.items():
            try:
                gtkspell.Spell(gtk.TextView()).set_language(lang_code)
                _installed_languages[lang_code] = lang_name
            except RuntimeError:
                pass

    def __init__(self, textview):
        self.textview = textview
        
        if self._LANG and Config.get(Config.SPELLCHECK):
            # if LANG is not a correct key (pt_BR or pt_PT),
            #  try only the language part of LANG
            if self._LANG not in self._installed_languages.keys():
                self._LANG = self._LANG.split('_')[0]
            # if this still doesn't work we fall back to 'off'
            if self._LANG not in self._installed_languages.keys():
                self._LANG = 'off'
        else:
            self._LANG = 'off'

        self._active_language = 'off'
        self._real_set_active_language(self._LANG)

    def _real_set_active_language(self, lang_code):
        """Set the active language by it's code."""
        if self._active_language == 'off':
            if lang_code == 'off':
                return
            else:
                gtkspell_spell = gtkspell.Spell(self.textview)
        else:
            gtkspell_spell = gtkspell.get_from_text_view(self.textview)
            if lang_code == 'off':
                gtkspell_spell.detach()
                self._active_language = lang_code
                return
                
        gtkspell_spell.set_language(lang_code)
        self._active_language = lang_code
        
    def _sort_languages(self, lang_a, lang_b):
        """Put language names in alphabetical order.
        
        Except 'None', which should be always the first.
        
        """
        if lang_a == _('None'):
            return -1
        if lang_b == _('None'):
            return 1
        if lang_a < lang_b:
            return -1
        if lang_a > lang_b:
            return 1
        return 0
            
        
    def get_all_languages(self):
        """Get the list of installed language names."""
        langs = self._installed_languages.values()
        langs.sort(self._sort_languages)
        return langs
    
    def set_active_language(self, language):
        """Set active language by it's name."""
        for code, name in self._installed_languages.items():
            if name == language:
                self._real_set_active_language(code)
                return
        
    def get_active_language(self):
        """Get the name of the active language."""
        return self._installed_languages[self._active_language]
