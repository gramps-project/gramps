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

# $Id$

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gettext
import sys
import os
import locale
import logging

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ..const import LOCALE_DIR
from ..constfunc import mac, win, UNITYPE

#------------------------------------------------------------------------
#
# GrampsLocale Class
#
#------------------------------------------------------------------------
class GrampsLocale(object):
    """
    Encapsulate a locale
    """
    def __init__(self):
        self.localedir = None
        self.lang = None
        self.language = []
        if ("GRAMPSI18N" in os.environ
            and os.path.exists(os.environ["GRAMPSI18N"])):
            self.localedir = os.environ["GRAMPSI18N"]
        elif os.path.exists(LOCALE_DIR):
            self.localedir = LOCALE_DIR
        elif os.path.exists(os.path.join(sys.prefix, "share", "locale")):
            self.localedir = os.path.join(sys.prefix, "share", "locale")
        else:
            lang = os.environ.get('LANG', 'en')
            if lang and lang[:2] == 'en':
                pass # No need to display warning, we're in English
            else:
                logging.warning('Locale dir does not exist at %s', LOCALE_DIR)
                logging.warning('Running python setup.py install --prefix=YourPrefixDir might fix the problem')

        if not self.localedir:
#No localization files, no point in continuing
            return
        self.localedomain = 'gramps'

        if mac():
            from . import maclocale
            (self.lang, self.language) = maclocale.mac_setup_localization(self)
        else:
            self.lang = ' '
            try:
                self.lang = os.environ["LANG"]
            except KeyError:
                self.lang = locale.getlocale()[0]
            if not self.lang:
                try:
                    self.lang = locale.getdefaultlocale()[0] + '.UTF-8'
                except TypeError:
                    logging.warning('Unable to determine your Locale, using English')
                    self.lang = 'C.UTF-8'

            if "LANGUAGE" in os.environ:
                language = [l for l in os.environ["LANGUAGE"].split(":")
                            if l in self.get_available_translations()]
                self.language = language
            else:
                self.language = [self.lang[0:2]]

#GtkBuilder depends on reading Glade files as UTF-8 and crashes if it
#doesn't, so set $LANG to have a UTF-8 locale. NB: This does *not*
#affect locale.getpreferredencoding() or sys.getfilesystemencoding()
#which are set by python long before we get here.
        check_lang = self.lang.split('.')
        if len(check_lang) < 2  or check_lang[1] not in ["utf-8", "UTF-8"]:
            self.lang = '.'.join((check_lang[0], 'UTF-8'))
            os.environ["LANG"] = self.lang
        # Set Gramps's translations
        self.translation = self._get_translation(self.localedomain, self.localedir, self.language)
        # Now set the locale for everything besides translations.

        try:
            # First try the environment to preserve individual variables
            locale.setlocale(locale.LC_ALL, '')
            try:
                #Then set LC_MESSAGES to self.lang
                locale.setlocale(locale.LC_MESSAGES, self.lang)
            except locale.Error:
                logging.warning("Unable to set translations to %s, locale not found.", self.lang)
        except locale.Error:
            # That's not a valid locale -- on Linux, probably not installed.
            try:
                # First fallback is self.lang
                locale.setlocale(locale.LC_ALL, self.lang)
                logging.warning("Setting locale to individual LC_ variables failed, falling back to %s.", self.lang)

            except locale.Error:
                # No good, set the default encoding to C.UTF-8. Don't
                # mess with anything else.
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
                logging.error("Failed to set locale %s, falling back to English",  self.lang)
        # $LANGUAGE is what sets the Gtk+ translations
        os.environ["LANGUAGE"] = ':'.join(self.language)
        # GtkBuilder uses GLib's g_dgettext wrapper, which oddly is bound
        # with locale instead of gettext.
        locale.bindtextdomain(self.localedomain, self.localedir)

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------

    def get_localedomain(self):
        """
        Get the LOCALEDOMAIN used for the Gramps application.
        Required by gui/glade.py to pass to Gtk.Builder
        """
        return self.localedomain

    def get_language_list(self):
        """
        Return the list of configured languages.  Used by
        ViewManager.check_for_updates to select the language for the
        addons descriptions.
        """
        return self.language

    def _get_translation(self, domain = None,
                         localedir = None,
                         languages=None):
        """
        Get a translation of one of our classes. Doesn't return the
        singleton so that it can be used by get_addon_translation()
        """
        if not domain:
            domain = self.localedomain
        if not languages:
            languages = self.language
        if not localedir:
            localedir = self.localedir

        if gettext.find(domain, localedir, languages):
            return gettext.translation(domain, localedir,
                                       languages,
                                       class_ = GrampsTranslations)
        else:
            logging.debug("Unable to find translations for %s and %s in %s"
                             , domain, languages, localedir)
            return GrampsNullTranslations()

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------

    def get_localedomain(self):
        """
        Get the LOCALEDOMAIN used for the Gramps application.
        Required by gui/glade.py to pass to Gtk.Builder
        """
        return self.localedomain

    def get_language_list(self):
        """
        Return the list of configured languages.  Used by
        ViewManager.check_for_updates to select the language for the
        addons descriptions.
        """
        return self.language

    def get_translation(self, domain = None, languages = None):
        """
        Get a translation object for a particular language.
        See the gettext documentation for the available functions
        >>> glocale = GrampsLocale()
        >>> _ = glocale.get_translation('foo', 'French')
        >>> _ = tr.gettext
        """

        if ((domain and not domain == self.localedomain)
            or (languages and not languages == self.language)):
            if not domain:
                domain = self.localedomain
            if not languages:
                languages = self.language
            fallback = False
            if "en" in languages:
                fallback = True
            try:
                # Don't use _get_translation because we want to fall
                # back on the singleton rather than a NullTranslation
                return gettext.translation(domain, self.localedir,
                                           languages,
                                           class_ = GrampsTranslations,
                                           fallback = fallback)
            except IOError:
                logging.warning("None of the requested languages (%s) were available, using %s instead", ', '.join(languages), self.lang)
                return self.translation
        else:
            return self.translation

    def get_addon_translator(self, filename, domain="addon",
                             languages=None):
        """
        Get a translator for an addon.

        filename - filename of a file in directory with full path, or
                   None to get from running code
        domain   - the name of the .mo file under the LANG/LC_MESSAGES dir
        languages - a list of languages to force
        returns  - a gettext.translation object

        Example:
        _ = glocale.get_addon_translator(languages=["fr_BE.utf8"]).gettext

        See the python gettext documentation.
        Assumes path/filename
            path/locale/LANG/LC_MESSAGES/addon.mo.
        """
        path = self.localedir
        # If get the path of the calling module's uncompiled file. This seems a remarkably bad idea.
#        if filename is None:
#            filename = sys._getframe(1).f_code.co_filename

        gramps_translator = self._get_translation()

        path = os.path.dirname(os.path.abspath(filename))
    # Check if path is of type str. Do import and conversion if so.
    # The import cannot be done at the top as that will conflict with the translation system.

        if not isinstance(path, UNITYPE) == str:
            from .file import get_unicode_path_from_env_var
        path = get_unicode_path_from_env_var(path)
        if languages:
            addon_translator = self._get_translation(domain,
                                                     path,
                                                     languages=languages)
        else:
            addon_translator = self._get_translation(domain, path)
        gramps_translator.add_fallback(addon_translator)
        return gramps_translator # with a language fallback

    def get_available_translations(self):
        """
        Get a list of available translations.

        :returns: A list of translation languages.
        :rtype: unicode[]

        """
        languages = ["en"]

        if self.localedir is None:
            return languages

        for langdir in os.listdir(self.localedir):
            mofilename = os.path.join(self.localedir, langdir,
                                      "LC_MESSAGES",
                                      "%s.mo" % self.localedomain )
            if os.path.exists(mofilename):
                languages.append(langdir)

        languages.sort()

        return languages

    def trans_objclass(self, objclass_str):
        """
        Translates objclass_str into "... %s", where objclass_str
        is 'Person', 'person', 'Family', 'family', etc.
        """
        _ = self.translation.gettext
        objclass = objclass_str.lower()
        if objclass == "person":
            return _("the person")
        elif objclass == "family":
            return _("the family")
        elif objclass == "place":
            return _("the place")
        elif objclass == "event":
            return _("the event")
        elif objclass == "repository":
            return _("the repository")
        elif objclass == "note":
            return _("the note")
        elif objclass in ["media", "mediaobject"]:
            return _("the media")
        elif objclass == "source":
            return _("the source")
        elif objclass == "filter":
            return _("the filter")
        else:
            return _("See details")

    def getfilesystemencoding(self):
        """
        If the locale isn't configured correctly, this will return
        'ascii' or 'ANSI_X3.4-1968' or some other unfortunate
        result. Current unix systems all encode filenames in utf-8,
        and Microsoft Windows uses utf-16 (which they call mbcs). Make
        sure we return the right value.
        """
        encoding = sys.getfilesystemencoding()

        if encoding in ("utf-8", "UTF-8", "utf8", "UTF8", "mbcs", "MBCS"):
            return encoding

        return "utf-8"

#-------------------------------------------------------------------------
#
# GrampsTranslation Class
#
#-------------------------------------------------------------------------
class GrampsTranslations(gettext.GNUTranslations):
    """
    Overrides and extends gettext.GNUTranslations. See the Python gettext
    "Class API" documentation for how to use this.
    """
    def language(self):
        """
        Return the target languge of this translations object.
        """
        return self.info()["language"]

    def gettext(self, msgid):
        """
        Obtain translation of gettext, return a unicode object
        :param msgid: The string to translated.
        :type msgid: unicode
        :returns: Translation or the original.
        :rtype: unicode
        """
        # If msgid =="" then gettext will return po file header
        # and that's not what we want.
        if len(msgid.strip()) == 0:
            return msgid
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ugettext(self, msgid)
        else:
            return gettext.GNUTranslations.gettext(self, msgid)

    def ngettext(self, singular, plural, num):
        """
        The translation of singular/plural is returned unless the translation is
        not available and the singular contains the separator. In that case,
        the returned value is the singular.

        :param singular: The singular form of the string to be translated.
                         may contain a context seperator
        :type singular: unicode
        :param plural: The plural form of the string to be translated.
        :type plural: unicode
        :param num: the amount for which to decide the translation
        :type num: int
        :returns: Translation or the original.
        :rtype: unicode
        """
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ungettext(self, singular,
                                                     plural, num)
        else:
            return gettext.GNUTranslations.ngettext(self, singular,
                                                    plural, num)

    def sgettext(self, msgid, sep='|'):
        """
        Even with a null translator we need to filter out the translator hint.
        """
        msgval = self.gettext(msgid)
        if msgval == msgid:
            sep_idx = msgid.rfind(sep)
            msgval = msgid[sep_idx+1:]
        return msgval


#-------------------------------------------------------------------------
#
# Translations Classes
#
#-------------------------------------------------------------------------
class GrampsTranslations(gettext.GNUTranslations):
    """
    Overrides and extends gettext.GNUTranslations. See the Python gettext
    "Class API" documentation for how to use this.
    """
    def language(self):
        """
        Return the target languge of this translations object.
        """
        return self.info()["language"]

    def gettext(self, msgid):
        """
        Obtain translation of gettext, return a unicode object
        :param msgid: The string to translated.
        :type msgid: unicode
        :returns: Translation or the original.
        :rtype: unicode
        """
        # If msgid =="" then gettext will return po file header
        # and that's not what we want.
        if len(msgid.strip()) == 0:
            return msgid
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ugettext(self, msgid)
        else:
            return gettext.GNUTranslations.gettext(self, msgid)

    def ngettext(self, singular, plural, num):
        """
        The translation of singular/plural is returned unless the translation is
        not available and the singular contains the separator. In that case,
        the returned value is the singular.

        :param singular: The singular form of the string to be translated.
                         may contain a context seperator
        :type singular: unicode
        :param plural: The plural form of the string to be translated.
        :type plural: unicode
        :param num: the amount for which to decide the translation
        :type num: int
        :returns: Translation or the original.
        :rtype: unicode
        """
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ungettext(self, singular,
                                                     plural, num)
        else:
            return gettext.GNUTranslations.ngettext(self, singular,
                                                    plural, num)

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
        return msgval


class GrampsNullTranslations(gettext.NullTranslations):
    """
    Extends gettext.NullTranslations to provide the sgettext method.

    Note that it's necessary for msgid to be unicode. If it's not,
    neither will be the returned string.
    """
    def sgettext(self, msgid):
        msgval = self.gettext(msgid)
        if msgval == msgid:
            sep_idx = msgid.rfind(sep)
            msgval = msgid[sep_idx+1:]
        return msgval

    def language(self):
        """
        The null translation returns the raw msgids, which are in English
        """
        return "en"
