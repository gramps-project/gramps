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
from gen.ggettext import gettext as _
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
    HAVE_GTKSPELL = False

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import config

if (not config.get('behavior.ignore-spellcheck')) and (not HAVE_GTKSPELL):
    LOG.warn(_("Spelling checker is not installed"))

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

class Spell(object):
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
                    gtkspell_spell = gtkspell.Spell(self.textview)
                    self._active_spellcheck = spellcheck_code
                except:
                    # attaching the spellchecker will fail if
                    # the language does not exist
                    # and presumably if there is no dictionary
                    pass
        else:
            if spellcheck_code == 'on':
                return
            else:
                gtkspell_spell = gtkspell.get_from_text_view(self.textview)
                gtkspell_spell.detach()
                self._active_spellcheck = spellcheck_code

    # Public API
    
    def get_all_spellchecks(self):
        """Get the list of installed spellcheck names."""
        return self._spellcheck_options.values()
    
    def set_active_spellcheck(self, spellcheck):
        """Set active spellcheck by it's name."""
        for code, name in self._spellcheck_options.items():
            if name == spellcheck:
                self.__real_set_active_spellcheck(code)
                return
        
    def get_active_spellcheck(self):
        """Get the name of the active spellcheck."""
        return self._spellcheck_options[self._active_spellcheck]

