#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
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

# $Id:TransUtils.py 9912 2008-01-22 09:17:46Z acraphae $

"""
Provide translation assistance
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gettext
import os

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const

#-------------------------------------------------------------------------
#
# Public Constants
#
#-------------------------------------------------------------------------
if "GRAMPSI18N" in os.environ:
    LOCALEDIR = os.environ["GRAMPSI18N"]
elif os.path.exists( os.path.join(const.ROOT_DIR, "lang") ):
    LOCALEDIR = os.path.join(const.ROOT_DIR, "lang")
else:
    LOCALEDIR = os.path.join(const.PREFIXDIR, "share/locale")

LOCALEDOMAIN = 'gramps'

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------
def setup_gettext():
    """
    Setup the gettext environment.

    :returns: Nothing.

    """
    gettext.bindtextdomain(LOCALEDOMAIN, LOCALEDIR)
    gettext.textdomain(LOCALEDOMAIN)
    
    #following installs _ as a python function, we avoid this as TransUtils is
    #used sometimes:
    #gettext.install(LOCALEDOMAIN, LOCALEDIR, unicode=1)

def get_addon_translator(filename, domain='addon'):
    """
    Get a translator for an addon. 
    Assumes filename_dir/locale/LANG/LC_MESSAGES/addon.mo.
    """
    import locale
    LANG = locale.getlocale()[0] or "en"
    path = os.path.dirname(os.path.abspath(filename))
    trans = Translator(LANG)
    try:
        fallback = gettext.translation(domain, 
                                       os.path.join(path, "locale"), 
                                       languages=[LANG])
        trans.trans.add_fallback(fallback)
    except:
        if LANG and not LANG.startswith("en"):
            print ("WARN: can't add local '%s' addon translation for '%s'." % 
                   (filename, LANG))
    return trans
    
def get_available_translations():
    """
    Get a list of available translations.

    :returns: A list of translation languages.
    :rtype: unicode[]
    
    """
    languages = ["en"]
    
    for langdir in os.listdir(LOCALEDIR):
        mofilename = os.path.join( LOCALEDIR, langdir, 
                                   "LC_MESSAGES", "%s.mo" % LOCALEDOMAIN )
        if os.path.exists(mofilename):
            languages.append(langdir)

    languages.sort()

    return languages
    
def sgettext(msgid, sep='|'):
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
    msgval = gettext.gettext(msgid)
    if msgval == msgid:
        sep_idx = msgid.rfind(sep)
        msgval = msgid[sep_idx+1:]
    return msgval

def sngettext(singular, plural, n, sep='|'):
    """
    Strip the context used for resolving translation ambiguities.
    
    The translation of singular/plural is returned unless the translation is
    not available and the singular contains the separator. In that case,
    the returned value is the portion of singular following the last
    separator. Default separator is '|'.

    :param singular: The singular form of the string to be translated.
                      may contain a context seperator
    :type singular: unicode
    :param plural: The plural form of the string to be translated.
    :type plural: unicode
    :param n: the amount for which to decide the translation
    :type n: int
    :param sep: The separator marking the context.
    :type sep: unicode
    :returns: Translation or the original with context stripped.
    :rtype: unicode

    """
    msgval = gettext.ngettext(singular, plural, n)
    if msgval == singular:
        sep_idx = singular.rfind(sep)
        msgval = singular[sep_idx+1:]
    return msgval

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
            self.trans = None
        else:
            # fallback=True will cause the translator to use English if 
            # lang = "en" or if something goes wrong.
            self.trans = gettext.translation(LOCALEDOMAIN, languages=[lang], 
                                             fallback=True)
            
    def gettext(self, message):
        """
        Return the translated string.
        
        :param message: The message to be translated.
        :type message: string
        :returns: The translated message
        :rtype: unicode
        
        """
        if self.trans is None:
            return gettext.gettext(message)
        else:
            return self.trans.gettext(message)
