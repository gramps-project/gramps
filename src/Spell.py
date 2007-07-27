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
LOG = logging.getLogger(".Spell")

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
    LOG.warn(_("Spelling checker is not installed"))
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

# All official dictionaries available for GNU Aspell.
# ftp://ftp.gnu.org/gnu/aspell/dict/0index.html
LANGUAGES = {
    'af': _('Afrikaans'),
    'am': _('Amharic'),
    'ar': _('Arabic'),
    'az': _('Azerbaijani'),
    'be': _('Belarusian'),
    'bg': _('Bulgarian'),
    'bn': _('Bengali'),
    'br': _('Breton'),
    'ca': _('Catalan'),
    'cs': _('Czech'),
    'csb': _('Kashubian'),
    'cy': _('Welsh'),
    'da': _('Danish'),
    'de': _('German'),
    'de-alt': _('German - Old Spelling'),
    'el': _('Greek'),
    'en': _('English'),
    'eo': _('Esperanto'),
    'es': _('Spanish'),
    'et': _('Estonian'),
    'fa': _('Persian'),
    'fi': _('Finnish'),
    'fo': _('Faroese'),
    'fr': _('French'),
    'fy': _('Frisian'),
    'ga': _('Irish'),
    'gd': _('Scottish Gaelic'),
    'gl': _('Galician'),
    'gu': _('Gujarati'),
    'gv': _('Manx Gaelic'),
    'he': _('Hebrew'),
    'hi': _('Hindi'),
    'hil': _('Hiligaynon'),
    'hr': _('Croatian'),
    'hsb': _('Upper Sorbian'),
    'hu': _('Hungarian'),
    'hy': _('Armenian'),
    'ia': _('Interlingua'),
    'id': _('Indonesian'),
    'is': _('Icelandic'),
    'it': _('Italian'),
    'ku': _('Kurdi'),
    'la': _('Latin'),
    'lt': _('Lithuanian'),
    'lv': _('Latvian'),
    'mg': _('Malagasy'),
    'mi': _('Maori'),
    'mk': _('Macedonian'),
    'mn': _('Mongolian'),
    'mr': _('Marathi'),
    'ms': _('Malay'),
    'mt': _('Maltese'),
    'nb': _('Norwegian Bokmal'),
    'nds': _('Low Saxon'),
    'nl': _('Dutch'),
    'nn': _('Norwegian Nynorsk'),
    'ny': _('Chichewa'),
    'or': _('Oriya'),
    'pa': _('Punjabi'),
    'pl': _('Polish'),
    'pt': _('Portuguese'),
    'pt_BR': _('Brazilian Portuguese'),
    'pt_PT': _('Portuguese'),
    'qu': _('Quechua'),
    'ro': _('Romanian'),
    'ru': _('Russian'),
    'rw': _('Kinyarwanda'),
    'sc': _('Sardinian'),
    'sk': _('Slovak'),
    'sl': _('Slovenian'),
    'sr': _('Serbian'),
    'sv': _('Swedish'),
    'sw': _('Swahili'),
    'ta': _('Tamil'),
    'te': _('Telugu'),
    'tet': _('Tetum'),
    'tl': _('Tagalog'),
    'tn': _('Setswana'),
    'tr': _('Turkish'),
    'uk': _('Ukrainian'),
    'uz': _('Uzbek'),
    'vi': _('Vietnamese'),
    'wa': _('Walloon'),
    'yi': _('Yiddish'),
    'zu': _('Zulu'),
}

class Spell:
    """Attach a gtkspell instance to the passed TextView instance.
    """
    lang = locale.getlocale()[0]
    
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
        
        if self.lang and Config.get(Config.SPELLCHECK):
            # if LANG is not a correct key (pt_BR or pt_PT),
            #  try only the language part of LANG
            if self.lang not in self._installed_languages.keys():
                self.lang = self.lang.split('_')[0]
            # if this still doesn't work we fall back to 'off'
            if self.lang not in self._installed_languages.keys():
                self.lang = 'off'
        else:
            self.lang = 'off'

        self._active_language = 'off'
        self.__real_set_active_language(self.lang)

    # Private
    
    def __real_set_active_language(self, lang_code):
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

    def __sort_languages(lang_a, lang_b):
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
            
    # Public API
    
    def get_all_languages(self):
        """Get the list of installed language names."""
        langs = self._installed_languages.values()
        langs.sort(self.__sort_languages)
        return langs
    
    def set_active_language(self, language):
        """Set active language by it's name."""
        for code, name in self._installed_languages.items():
            if name == language:
                self.__real_set_active_language(code)
                return
        
    def get_active_language(self):
        """Get the name of the active language."""
        return self._installed_languages[self._active_language]

