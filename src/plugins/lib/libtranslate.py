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

# $Id$

"""
Translator class for use by plugins.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gettext
_ = gettext.gettext

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import TransUtils
import DateHandler

#------------------------------------------------------------------------
#
# Private Constants
#
#------------------------------------------------------------------------
_LANG_MAP = {
    "bg" : _("Bulgarian"),
    "ca" : _("Catalan"),
    "cs" : _("Czech"),
    "da" : _("Danish"),
    "de" : _("German"),
    "en" : _("English"),
    "eo" : _("Esperanto"),
    "es" : _("Spanish"),
    "fi" : _("Finnish"),
    "fr" : _("French"),
    "he" : _("Hebrew"),
    "hr" : _("Croatian"),
    "hu" : _("Hungarian"),
    "it" : _("Italian"),
    "lt" : _("Lithuanian"),
    "mk" : _("Macedonian"),
    "nb" : _("Norwegian Bokmal"),
    "nl" : _("Dutch"),
    "nn" : _("Norwegian Nynorsk"),
    "pl" : _("Polish"),
    "pt" : _("Portuguese"),
    "ro" : _("Romanian"),
    "ru" : _("Russian"),
    "sk" : _("Slovak"),
    "sl" : _("Slovenian"),
    "sq" : _("Albanian"),
    "sv" : _("Swedish"),
    "tr" : _("Turkish"),
    "zh" : _("Chinese")
}

_COUNTRY_MAP = {
    "BR" : _("Brazil"),
    "CN" : _("China")
}

#------------------------------------------------------------------------
#
# Public Functions
#
#------------------------------------------------------------------------
def get_language_string(lang_code):
    """
    Given a language code of the form "lang_region", return a text string 
    representing that language.
    """
    code_parts = lang_code.rsplit("_")
    
    lang = code_parts[0]
    if lang in _LANG_MAP:
        lang = _LANG_MAP[lang]
    
    if len(code_parts) > 1:
        country = code_parts[1]
        if country in _COUNTRY_MAP:
            country = _COUNTRY_MAP[country]
        retstr = _("%(language)s (%(country)s)") % \
                { 'language' : lang, 'country'  : country  }
    else:
        retstr = lang
        
    return retstr

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
            if lang in DateHandler.LANG_TO_DISPLAY:
                self.__dd = DateHandler.LANG_TO_DISPLAY[lang](None)
            else:
                self.__dd = DateHandler.displayer
            
    def gettext(self, message):
        """
        Return the unicode translated string.
        
        :param message: The message to be translated.
        :type message: string
        :returns: The translated message
        :rtype: unicode
        
        """
        if self.__trans is None:
            return unicode(gettext.gettext(message))
        else:
            return self.__trans.ugettext(message)
        
    def ngettext(self, singular, plural, n):
        """
        Return the unicode translated singular/plural string.
        
        The translation of singular/plural is returned unless the translation is
        not available and the singular contains the separator. In that case,
        the returned value is the portion of singular following the last
        separator. Default separator is '|'.
    
        :param singular: The singular form of the string to be translated.
                          may contain a context separator
        :type singular: unicode
        :param plural: The plural form of the string to be translated.
        :type plural: unicode
        :param n: the amount for which to decide the translation
        :type n: int
        :returns: The translated singular/plural message
        :rtype: unicode
    
        """
        if self.__trans is None:
            return unicode(gettext.ngettext(singular, plural, n))
        else:
            return self.__trans.ungettext(singular, plural, n)
        
    def sgettext(self, msgid, sep='|'):
        """
        Strip the context used for resolving translation ambiguities.
        
        The translation of msgid is returned unless the translation is
        not available and the msgid contains the separator. In that case,
        the returned value is the portion of msgid following the last
        separator. Default separator is '|'.
    
        :param msgid: The string to translated.
        :type msgid: unicode
        :param sep: The separator marking the context.
        :type sep: unicode
        :returns: Translation or the original with context stripped.
        :rtype: unicode
    
        """
        msgval = self.gettext(msgid)
        if msgval == msgid:
            sep_idx = msgid.rfind(sep)
            msgval = msgid[sep_idx+1:]
        return unicode(msgval)
        
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
