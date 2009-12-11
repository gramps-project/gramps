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

# $Id:  $

"""
Translator class for use by plugins.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gettext

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import TransUtils
import DateHandler

#-------------------------------------------------------------------------
#
# Translator
#
#-------------------------------------------------------------------------
class Translator:
    """
    This class provides translated strings for the configured language.
    """
    DEFAULT_TRANSLATION_STR = "default"
    
    def __init__(self, lang=DEFAULT_TRANSLATION_STR):
        """
        :param lang: The language to translate to. 
            The language can be:
               * The name of any installed .mo file
               * "en" to use the message strings in the code
               * "default" to use the default translation being used by gettext.
        :type lang: string
        :return: nothing
        
        """
        if lang == Translator.DEFAULT_TRANSLATION_STR:
            self.__trans = None
            self.__dd = DateHandler.displayer
        else:
            # fallback=True will cause the translator to use English if 
            # lang = "en" or if something goes wrong.
            self.__trans = gettext.translation(TransUtils.get_localedomain(), 
                                               languages=[lang], 
                                               fallback=True)
            self.__dd = DateHandler.LANG_TO_DISPLAY[lang](None)
            
    def get_text(self, message):
        """
        Return the translated string.
        
        :param message: The message to be translated.
        :type message: string
        :returns: The translated message
        :rtype: unicode
        
        """
        if self.__trans is None:
            return gettext.gettext(message)
        else:
            return self.__trans.gettext(message)
        
    def get_date(self, date):
        """
        Return a string representing the date appropriate for the language being
        translated.
        
        :param date: The date to be represented.
        :type date: :class:`~gen.lib.date.Date`
        :returns: The date as text in the proper language.
        :rtype: unicode
        """
        return self.__dd.display(date)