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
from __future__ import print_function
import gettext
import sys
import os
import codecs
import locale
import logging
LOG = logging.getLogger("grampslocale")
HAVE_ICU = False
_hdlr = None
try:
    from icu import Locale, Collator
    HAVE_ICU = True
except ImportError:
    try:
        from PyICU import Locale, Collator
        HAVE_ICU = True
    except ImportError as err:
        LOG.warning("ICU not loaded because %s. Localization will be impaired. "
                    "Use your package manager to install PyICU", str(err))
ICU_LOCALES = None
if HAVE_ICU:
    ICU_LOCALES = Locale.getAvailableLocales()

        #Map our translated language codes to Microsoft Locale Names
        #Important: Maintain this list with new translations or they
        #won't work under MS Windows!
mslocales = {
    'ar': ('Arabic_Saudi Arabia', '1256'),
    'bg': ('Bulgrian_Bulgaria', '1251'),
    'br': None, #Windows has no translation for Breton
    'ca': ('Catalang_Spain', '1252'),
    'cs': ('Czech_Czech Republic', '1250'),
    'da': ('Danish_Denmark', '1252'),
    'de': ('German_Germany', '1252'),
    'en_GB': ('English_United Kingdom', '1252'),
    'eo': None, #Windows has no translation for Esperanto
    'es': ('Spanish_Spain', '1252'),
    'fi': ('Finnish_Finland', '1252'),
    'fr': ('French_France', '1252'),
    'ga': None, #Windows has no translation for Gaelic
    'he': ('Hebrew_Israel', '1255'),
    'hr': ('Croatian_Croatia', '1250'),
    'hu': ('Hungarian_Hungary', '1250'),
    'it': ('Italian_Italy', '1252'),
    'ja': ('Japanese_Japan', '932'),
    'lt': ('Lithuanian_Lithuania', '1252'),
    'mk': None, #Windows has no translation for Macedonian
    'nb': ('Norwegian_Norway', '1252'),
    'nl': ('Dutch_Netherlands', '1252'),
    'nn': ('Norwegian-Nynorsk_Norway', '1252'),
    'pl': ('Polish_Poland', '1250'),
    'pt_BR': ('Portuguese_Brazil', '1252'),
    'pt_PT': ('Portuguese_Portugal', '1252'),
    'ro': ('Romanian_Romania', '1250'),
    'ru': ('Russian_Russia', '1251'),
    'sk': ('Slovak_Slovakia', '1250'),
    'sl': ('Slovenian_Slovenia', '1250'),
    'sq': ('Albanian_Albania', '1250'),
    'sr': ('Serbian(Cyrillic)_Serbia and Montenegro', '1251'),
    'sv': ('Swedish_Sweden', '1252'),
    'tr': ('Turkish_Turkey', '1254'),
    'uk': ('Ukrainian_Ukraine', '1251'),
    'vi': ('Vietnamese_Viet Nam', '1258'),
    'zh_CN': ('Chinese_China', '936'),
    }

def _check_mswin_locale(locale):
    msloc = None
    try:
        msloc = mslocales[locale[:5]]
        locale = locale[:5]
    except KeyError:
        try:
            msloc = mslocales[locale[:2]]
            locale = locale[:2]
        except KeyError:
            return None
    return (locale, msloc)

def _check_mswin_locale_reverse(locale):
    for (loc, msloc) in mslocales.items():
        if msloc and locale == msloc[0]:
            return (loc, msloc[1])

    return None

#------------------------------------------------------------------------
#
# GrampsLocale Class
#
#------------------------------------------------------------------------
class GrampsLocale(object):
    """
    Encapsulate a locale.  This class is a sort-of-singleton: The
    first instance created will query the environment and OSX defaults
    for missing parameters (precedence is parameters passed to the
    constructor, environment variables LANG, LC_COLLATE, LC_TIME,
    etc., and LANGUAGE, OSX defaults settings when that's the
    platform).  Subsequent calls to the constructor with no or
    identical parameters will return the same Grampslocale
    object. Construction with different parameters will result in a
    new GrampsLocale instance with the specified parameters, but any
    parameters left out will be filled in from the first instance.

    @localedir: The full path to the top level directory containing
                the translation files. Defaults to sys.prefix/share/locale.

    @lang:      A single locale value which is used for unset locale.LC_FOO
                settings.

    @domain:    The name of the applicable translation file. The default is
                "gramps", indicating files in LC_MESSAGES named gramps.mo.

    @languages: A list of two or five character codes corresponding to
                subidrectries in the localedir, e.g. "fr" or "zh_CN".
    """
    __first_instance = None
    def __new__(cls, localedir=None, lang=None, domain=None, languages=None):
        if not GrampsLocale.__first_instance:
            cls.__first_instance = super(GrampsLocale, cls).__new__(cls)
            cls.__first_instance.initialized = False
            return cls.__first_instance

        if not cls.__first_instance.initialized:
            raise RuntimeError("Second GrampsLocale created before first one was initialized")
        if ((lang is None or lang == cls.__first_instance.lang)
            and (localedir is None or localedir == cls.__first_instance.localedir)
            and (domain is None or domain == cls.__first_instance.localedomain)
            and (languages is None or len(languages) == 0 or
                 languages == cls.__first_instance.languages)):
            return cls.__first_instance

        return super(GrampsLocale, cls).__new__(cls)

    def _win_init_environment(self):
        """
        The Windows implementation of Python ignores environment
        variables when setting the locale; it only pays attention to
        the control panel language settings -- which for practical
        purposes limits one to the language for which one purchased
        Windows. This function enables using alternative
        localizations.
        """

        if not (hasattr(self, 'lang') and self.lang):
            self.lang = None
            if 'LANG' in os.environ:
                (lang, loc) = _check_mswin_locale(os.environ['LANG'])
                if loc:
                    locale.setlocale(locale.LC_ALL, '.'.join(loc))
                    self.lang = lang
                    self.language = [self.lang]
                    self.encoding = loc[1]

            if not self.lang:
                locale.setlocale(locale.LC_ALL, '')
                (lang, encoding) = locale.getlocale()
                loc = _check_mswin_locale_reverse(lang)
                if loc:
                    self.lang = loc[0]
                    self.languages = [loc[0]]
                    self.encoding = loc[1]
                else:
                    (lang, loc) = _check_mswin_locale(lang)
                    if lang:
                        self.lang = lang
                        self.language = [self.lang]
                        self.encoding = loc[1]

            if not self.lang:
                self.lang = 'C'
                self.language = ['en']
                self.encoding = 'cp1252'

        if not (hasattr(self, 'language') and self.language):
            if 'LC_MESSAGES' in os.environ:
                lang = self.check_available_translations(os.environ['LC_MESSAGES'])
                if lang:
                    self.language = [lang]
            if 'LANGUAGE' in os.environ:
                language = [x for x in [self.check_available_translations(l)
                                        for l in os.environ["LANGUAGE"].split(":")]
                            if x]

                self.language = language
        if not (hasattr(self, 'language') and self.language):
            self.language = [self.lang]

        if 'LC_COLLATE' in os.environ:
            coll = os.environ['LC_COLLATE']
            if HAVE_ICU:
                if coll[:5] in ICU_LOCALES:
                    self.collation = coll
                else:
                    self.collation = self.lang
            else:
                (coll, loc) = _check_mswin_locale(coll)
                if loc:
                    locale.setlocale(locale.LC_COLLATE, '.'.join(loc))
                    self.collation = coll
                else: #can't set the collation locale if MS doesn't support it
                    self.collation = self.lang

        else:
            self.collation = self.lang

# We can't import datahandler stuff or we'll get a circular
# dependency, so we rely on the available translations list
        if 'LC_TIME' in os.environ:
            self.calendar = self.check_available_translations(os.environ['LC_TIME']) or self.lang
        else:
            self.calendar = self.lang

    def _init_from_environment(self):
        try:
            locale.setlocale(locale.LC_ALL, '')
        except locale.Error as err:
            LOG.warning("Locale error %s, localization will be US English.",
                        err);
            self.lang = 'C'
            self.encoding = 'ascii'
            self.language = ['en']

        if not (hasattr(self, 'lang') and self.lang):
            (lang, encoding) = locale.getlocale()
            if self.check_available_translations(lang):
                self.lang = lang
                self.encoding = encoding
            else:
                loc = (locale.getlocale(locale.LC_MESSAGES) or
                       locale.getdefaultlocale())
                if loc and self.check_available_translations(loc[0]):
                    self.lang = loc[0]
                    self.encoding = loc[1]
                    self.language = ['en']
                else:
                    self.lang = 'C'
                    self.encoding = 'ascii'
                    self.language = ['en']

        # $LANGUAGE overrides $LANG, $LC_MESSAGES
        if not self.lang.startswith('C.') and "LANGUAGE" in os.environ:
            language = [x for x in [self.check_available_translations(l)
                                    for l in os.environ["LANGUAGE"].split(":")]
                            if x]
            if language:
                self.language = language

        if HAVE_ICU:
            self.calendar = locale.getlocale(locale.LC_TIME)[0] or self.lang[:5]
            self.collation = locale.getlocale(locale.LC_COLLATE)[0] or self.lang[:5]
        else:
            loc = locale.getlocale(locale.LC_TIME)
            if loc and loc[0]:
                self.calendar = '.'.join(loc)
            else:
                self.calendar = self.lang

            loc = locale.getlocale(locale.LC_COLLATE)
            if loc and loc[0]:
                self.collation = '.'.join(loc)
            else:
                self.collation = self.lang

    def _win_bindtextdomain(self, localedomain, localedir):
        """
        Help routine for loading and setting up libintl attributes
        Returns libintl
        """
        from ctypes import cdll
        try:
            libintl = cdll.LoadLibrary('libintl-8')
            libintl.bindtextdomain(localedomain,
                                   localedir.encode(sys.getfilesystemencoding()))
            libintl.textdomain(localedomain)
            libintl.bind_textdomain_codeset(localedomain, "UTF-8")

        except WindowsError:
            LOG.warning("Localization library libintl not on %PATH%, localization will be incomplete")

    def __init_first_instance(self, localedir):
        global _hdlr
        _hdlr = logging.StreamHandler()
        _hdlr.setFormatter(logging.Formatter(fmt="%(name)s.%(levelname)s: %(message)s"))
        LOG.addHandler(_hdlr)

#First, globally set the locale to what's in the environment:

        if not (hasattr(self, 'lang') and self.lang
                and hasattr(self, 'language') and self.language):
            if sys.platform == 'darwin':
                from . import maclocale
                maclocale.mac_setup_localization(self)
            elif sys.platform == 'win32':
                self._win_init_environment()
            else:
                self._init_from_environment()
        else:
            self.currency = self.calendar = self.collation = self.lang

        if not self.lang:
            self.lang = 'en_US.UTF-8'
        if not self.language:
            self.language.append('en')
        if not self.have_localedir and not self.lang.startswith('en'):
            LOG.warning("No translations for %s were found, setting localization to U.S. English", self.localedomain)
            self.lang = 'en_US.UTF-8'
            self.language = ['en']

#Next, we need to know what is the encoding from the native
#environment. This is used by python standard library funcions which
#localize their output, e.g. time.strftime():
        if not self.encoding:
            self.encoding = (locale.getpreferredencoding()
                             or sys.getdefaultencoding())
#Ensure that output is encoded correctly to stdout and stderr. This is
#much less cumbersome and error-prone than encoding individual outputs
#and better handles the differences between Python 2 and Python 3:
        _encoding = sys.stdout.encoding or sys.getdefaultencoding()
        if sys.version_info[0] < 3:
            sys.stdout = codecs.getwriter(_encoding)(sys.stdout,
                                                     'backslashreplace')
            sys.stderr = codecs.getwriter(_encoding)(sys.stderr,
                                                     'backslashreplace')
        else:
            sys.stdout = codecs.getwriter(_encoding)(sys.stdout.detach(),
                                                     'backslashreplace')
            sys.stderr = codecs.getwriter(_encoding)(sys.stderr.detach(),
                                                     'backslashreplace')


#GtkBuilder depends on reading Glade files as UTF-8 and crashes if it
#doesn't, so set $LANG to have a UTF-8 locale. NB: This does *not*
#affect locale.getpreferredencoding() or sys.getfilesystemencoding()
#which are set by python long before we get here.
        check_lang = self.lang.split('.')
        if len(check_lang) < 2  or check_lang[1] not in ["utf-8", "UTF-8"]:
            self.lang = '.'.join((check_lang[0], 'UTF-8'))
            if self.lang == 'C.UTF-8':
                os.environ["LANG"] = 'C'
            else:
                os.environ["LANG"] = self.lang
        os.environ["LANGUAGE"] = ':'.join(['C' if l.startswith('en') else l for l in self.language])

        # GtkBuilder uses GLib's g_dgettext wrapper, which oddly is bound
        # with locale instead of gettext. Win32 doesn't support bindtextdomain.
        if self.have_localedir:
            if not sys.platform == 'win32':
                locale.bindtextdomain(self.localedomain, self.localedir)
            else:
                self._win_bindtextdomain(self.localedomain, self.localedir)


    def __init__(self, localedir=None, lang=None, domain=None, languages=None):
        """
        Init a GrampsLocale. Run __init_first_instance() to set up the
        environement if this is the first run. Return __first_instance
        otherwise if called without arguments.
        """
        global _hdlr

        if hasattr(self, 'initialized') and self.initialized:
            return

        _first = self._GrampsLocale__first_instance
        self.have_localedir = True

        if domain:
            self.localedomain = domain
        elif hasattr(_first, 'localedomain'):
            self.localedomain = _first.localedomain
        else:
            self.localedomain = "gramps"
        if localedir and os.path.exists(localedir):
            self.localedir = localedir
        elif hasattr(_first, 'localedir'):
            self.localedir = _first.localedir
        else:
            self.localedir = None
            if localedir:
                LOG.warning("Localedir %s doesn't exist, unable to set localization", localedir);
            else:
                LOG.warning("No Localedir provided, unable to set localization")
            self.have_localedir = False

        if lang:
            self.lang = lang
        elif hasattr(_first, 'lang'):
            self.lang = _first.lang

        self.language = []
        if languages:
            self.language = [x for x in [self.check_available_translations(l)
                                         for l in languages]
                             if x]
        elif hasattr(self, 'lang') and self.lang:
            trans = self.check_available_translations(lang)
            if trans:
                self.language.append(trans)

        if not self.language and hasattr(_first, 'language'):
            self.language = _first.language

        if self == _first:
            self._GrampsLocale__init_first_instance(localedir)
        else:
            self.calendar = self.collation = self.lang


        self.icu_locales = {}
        self.collator = None
        if HAVE_ICU:
            self.icu_locales["default"] = Locale.createFromName(self.lang)
            if self.collation and self.collation != self.lang:
                self.icu_locales["collation"] = Locale.createFromName(self.collation)
            else:
                self.icu_locales["collation"] = self.icu_locales["default"]
            try:
                self.collator = Collator.createInstance(self.icu_locales["collation"])
            except ICUError as err:
                LOG.warning("Unable to create collator: %s", str(err))
                self.collator = None

        self.translation = self._get_translation(self.localedomain,
                                                 self.localedir, self.language)
        if _hdlr:
            LOG.removeHandler(_hdlr)

        self.initialized = True

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

        for lang in languages:
            if gettext.find(domain, localedir, [lang]):
                translator = gettext.translation(domain, localedir,
                                                 [lang],
                                                 class_ = GrampsTranslations)
                translator._language = lang
                return translator

            elif lang.startswith("en") or lang.startswith("C"):
                translator = GrampsNullTranslations()
                translator._language = "en"
                return translator

        if not languages or len(languages) == 0:
            LOG.warning("No language provided, using US English")
        else:
            LOG.warning("No usable languages found in list for %s, using US English", os.path.basename(os.path.dirname(localedir)))
        translator = GrampsNullTranslations()
        translator._language = "en"
        return translator

    def _set_dictionaries(self):
        """
        Create a dictionary of language names localized to the
        GrampsLocale's primary language, keyed by language and
        country code.
        """
        _ = self.translation.gettext
        self.lang_map = {
            "bg" : _("Bulgarian"),
            "ca" : _("Catalan"),
            "cs" : _("Czech"),
            "da" : _("Danish"),
            "de" : _("German"),
            "el" : _("Greek"),
            "en" : _("English"),
            "eo" : _("Esperanto"),
            "es" : _("Spanish"),
            "fi" : _("Finnish"),
            "fr" : _("French"),
            "he" : _("Hebrew"),
            "hr" : _("Croatian"),
            "hu" : _("Hungarian"),
            "it" : _("Italian"),
            "ja" : _("Japanese"),
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
            "uk" : _("Ukrainian"),
            "vi" : _("Vietnamese"),
            "zh" : _("Chinese")
            }

        self.country_map = {
            "BR" : _("Brazil"),
            "CN" : _("China"),
            "PT" : _("Portugal")
            }

    def _get_language_string(self, lang_code):
        """
        Given a language code of the form "lang_region", return a text string
        representing that language.
        """
        code_parts = lang_code.rsplit("_")

        lang = code_parts[0]
        if not hasattr(self, 'lang_map'):
            self._set_dictionaries()

        if lang in self.lang_map:
            lang = self.lang_map[lang]

        country = None
        if len(code_parts) > 1:
            country = code_parts[1]
        if country in self.country_map:
            country = self.country_map[country]
            lang = "%(language)s (%(country)s)" % \
                { 'language' : lang, 'country'  : country  }

        return lang

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
                LOG.warning("None of the requested languages (%s) were available, using %s instead", ', '.join(languages), self.lang)
                return self.translation
        else:
            return self.translation

    def get_addon_translator(self, filename, domain="addon",
                             languages=None):
        """
        Get a translator for an addon.

        filename - filename of a file in directory with full path, or
                   None to get from self.
        domain   - the name of the .mo file under the LANG/LC_MESSAGES dir
        languages - a list of languages to force
        returns  - a gettext.translation object

        Example:
        _ = glocale.get_addon_translator(languages=["fr_BE.utf8"]).gettext

        See the python gettext documentation.
        Assumes path/filename
            path/locale/LANG/LC_MESSAGES/addon.mo.
        """
        gramps_translator = self._get_translation()

        path = self.localedir
        if filename:
            path = os.path.join(os.path.dirname(os.path.abspath(filename)), "locale")
        if languages:
            addon_translator = self._get_translation(domain,
                                                     path,
                                                     languages=languages)
        else:
            addon_translator = self._get_translation(domain, path)
        gramps_translator.add_fallback(addon_translator)
        return gramps_translator # with a language fallback

    def get_available_translations(self, localedir = None, localedomain = None):
        """
        Get a list of available translations.

        :returns: A list of translation languages.
        :rtype: unicode[]

        """
        languages = ["en"]

        if not localedir and hasattr(self, 'localedir'):
            localedir = self.localedir

        if localedir is None:
            return languages

        if not localedomain and hasattr(self, 'localedomain'):
            localedomain = self.localedomain

        for langdir in os.listdir(self.localedir):
            mofilename = os.path.join(localedir, langdir,
                                      "LC_MESSAGES",
                                      "%s.mo" % localedomain )
            if os.path.exists(mofilename):
                languages.append(langdir)

        languages.sort()

        return languages

    def check_available_translations(self, locale):
        """
        Test a locale for having a translation available
        locale -- string with standard language code, locale code, or name
        """
        if not self.have_localedir:
            return None
        if not hasattr(self, 'languages'):
            self.languages = self.get_available_translations()

        if not locale:
            return None

        if locale[:2] in self.languages:
            return locale[:2]
        if locale[:5] in self.languages:
            return locale[:5]

        return None

    def get_language_dict(self):
        '''
        return a dictionary of language names : codes for use by language
        pickers.
        '''
        langs = {}
        for code in self.get_available_translations():
            langs[self._get_language_string(code)] = code

        return langs


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

    def sort_key(self, string):
        """
        Return a value suitable to pass to the "key" parameter of sorted()
        """

        if HAVE_ICU and self.collator:
            #ICU can digest strings and unicode
            return self.collator.getCollationKey(string).getByteArray()
        else:
            try:
                base_locale = locale.getlocale(locale.LC_COLLATE)
                locale.setlocale(locale.LC_COLLATE, self.collation)
            except Exception as err:
                LOG.warn("Failed to set temporary locale with %s: %s",
                         self.lang, err)
                return string
            #locale in Python2 can't.
            try:
                if sys.version_info[0] < 3 and isinstance(string, unicode):
                    key = locale.strxfrm(string.encode("utf-8", "replace"))
                else:
                    key = locale.strxfrm(string)

            except Exception as err:
                LOG.warn("Failed to obtain key for %s because %s",
                         self.collation, str(err))
                return string
            try:
                locale.setlocale(locale.LC_COLLATE, base_locale)
            except Exception as err:
                LOG.warn("Failed to restore locale %s", err)
                return key
            return key

    def strcoll(self, string1, string2):
        """
        Given two localized strings, compare them and return -1 if
        string1 would sort first, 1 if string2 would, and 0 if
        they are the same.
        """
        key1 = self.sort_key(string1)
        key2 = self.sort_key(string2)
        return (-1 if key1 < key2 else (1 if key1 > key2 else 0))

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
        return self._language

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
    def sgettext(self, msgid, sep='|'):
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
