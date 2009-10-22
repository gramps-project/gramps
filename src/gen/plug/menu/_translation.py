#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Brian G. Matherly
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
# $Id: _filter.py 12756 2009-07-02 20:01:28Z gbritton $

"""
Option class representing a list of available translators.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gen.plug.menu import EnumeratedListOption
from TransUtils import get_available_translations, Translator

#-------------------------------------------------------------------------
#
# TranslationOption class
#
#-------------------------------------------------------------------------
class TranslationOption(EnumeratedListOption):
    """
    This class describes an option that provides a list of available 
    translations. Each possible value represents one of the possible 
    translations.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Translation"
        @type label: string
        @return: nothing
        """      
        EnumeratedListOption.__init__(self, label, 
                                      Translator.DEFAULT_TRANSLATION_STR)
        
        self.add_item(Translator.DEFAULT_TRANSLATION_STR, _("default"))
        for tran in get_available_translations():
            self.add_item(tran, tran)
        
    def get_translator(self):
        """
        Return a translator for the currently selected translation.
        
        @return: a translator object
        @rtype: TransUtils.Translator
        """
        return Translator(self.get_value())
