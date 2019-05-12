#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011    John Ralls, Fremont, CA
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
###
# Mac Localization Functions
###
"""
There is something of a mismatch between native Mac localization and
that of Gtk applications like Gramps because Apple chose to use IBM's
more modern and more complete International Components for Unicode
(ICU) for the purpose rather than the older POSIX and gettext based
localization used by Gtk (and most other Linux applications).

For Gramps, the system defaults settings will be used only if the user
hasn't set the corresponding environment variable already.

Apple's language list maps nicely to gettext's LANGUAGE environment
variable, so we use that if it's set. There's an additional
MULTI-TRANSLATION environment variable which the user can set to allow
incomplete translations to be supplemented from other translations on
the list before resorting to the default english. Many users find this
disconcerting, though, so it's not enabled by default. If the user
hasn't set a translation list (this happens occasionally), we'll check
the locale and collation settings and use either to set $LANGUAGE if
it's set to a non-english locale.

Similarly, Apple provides an "Order for sorted lists" which maps
directly to LC_COLLATE, and a Format>Region which maps to LANG. (Those
are the names of the controls in System Preferences; the names in the
defaults system are AppleCollationOrder and AppleLocale,
respectively.)

The user can override the currency and calendar, and those values are
appended to AppleLocale and parsed below. But Gramps makes no use of
currency and sets the calendar in its own preferences, so they're
ignored.

Where the mismatch becomes a problem is in date and number
formatting. POSIX specifies a locale for this, but ICU uses format
strings, and there is no good way to map those strings into one of the
available locales. Users who whan to specify particular ways of
formatting different from their base locales will have to figure out
the appropriate locale on their own and set LC_TIME and LC_NUMERIC
appropriately. The "Formats" page on the Languages & Text
(International in Leopard) System Preferences pane is a good way to
quickly assess the formats in various locales.

Neither Gramps nor Gtk supply a separate English translation, so if we
encounter English in the language list we substitute "C"; if we must
set $LANGUAGE from either locale or collation, we ignore an English
locale, leaving $LANGUAGE unset (which is the same as setting it to
"C".

"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------

import os, subprocess, locale
import logging
LOG = logging.getLogger(".gramps.gen.utils.grampslocale.mac")
LOG.propagate = True
#LOG.setLevel(logging.DEBUG)

def mac_setup_localization(glocale):
    """
    Set up the localization parameters from OSX's "defaults" system,
    permitting environment variables to override the settings.
    """
    def _mac_get_gramps_defaults(domain, key):
        try:
            if domain == "Global":
                args = ('/usr/bin/defaults', 'read', '-g', key)
            else:
                args = ('/usr/bin/defaults', 'read', 'org.gramps-project.gramps', key)

            answer = subprocess.Popen(
                args,
                stderr=open("/dev/null"),
                stdout=subprocess.PIPE).communicate()[0]
            if not answer:
                LOG.debug("No prefs found for %s:%s", domain, key)
                return None
            answer = answer.decode("utf-8")
            LOG.debug("Found %s for defaults %s:%s", answer.strip(), domain, key)
            return answer
        except OSError as err:
            LOG.warning("Failed to read %s from System Preferences: %s",
                        key, str(err))
            return None

    def _mac_check_languages(languages):
        if not languages:
            return None
        languages = map(lambda x: x.strip(),
                    languages.strip("()\n").split(",\n"))
        usable = []
        for lang in languages:
            lang = lang.strip().strip('"').replace("-", "_", 1)
            if lang == "cn_Hant": #Traditional; Gettext uses cn_TW
                lang = "cn_TW"
            if lang == "cn_Hans": #Simplified; Gettext uses cn_CN
                lang = "cn_CN"
            lang = glocale.check_available_translations(lang)
            if lang:
                usable.append(lang)

        return usable

    def _mac_language_list():
        """
        Extract the languages list from defaults.
        """
        languages = _mac_get_gramps_defaults("Gramps", "AppleLanguages")
        if languages:
            translations = _mac_check_languages(languages)
            if translations:
                return translations
            LOG.debug("No suitable translations found in language list on Gramps defaults")
        languages = _mac_get_gramps_defaults("Global", "AppleLanguages")
        if languages:
            translations = _mac_check_languages(languages)
            if translations:
                return translations
            LOG.debug("No suitable translations found in language list on Global defaults")
        LOG.debug("No translations found in System Preferences")
        return None

    def _mac_check_locale(locale_string):
        locale = None
        calendar = None
        currency = None
        div = locale_string.strip().split("@")
        LOG.debug("Checking Locale %s", ' '.join(div))
        locale = glocale.check_available_translations(div[0])
        if len(div) > 1:
            div = div[1].split(";")
            for phrase in div:
                (name, value) = phrase.split("=")
                if name == "calendar":
                    calendar = glocale.check_available_translations(value)
                elif name == "currency":
                    currency = value

        return (locale, calendar, currency)

    def _mac_get_locale():
        """
        Get the locale and specifiers from defaults.
        """
#Note that numeric separators are encoded in AppleICUNumberSymbols,
#with [0] being the decimal separator and [1] the thousands
#separator. This obviously won't translate into a locale without
#searching the locales database for a match.
        locale = _mac_get_gramps_defaults("Gramps", "AppleLocale")
        if locale:
            locale_values = _mac_check_locale(locale)
            if (locale_values[0]):
                return locale_values
            LOG.debug("Gramps defaults locale %s isn't supported", locale)

        locale = _mac_get_gramps_defaults("Global", "AppleLocale")
        if locale:
            locale_values = _mac_check_locale(locale)
            if (locale_values[0]):
                return locale_values
            LOG.debug("Global defaults locale %s isn't supported", locale)

        return (None, None, None)

    def _mac_get_collation():
        """
        Extract the collation (sort order) locale from the defaults string.
        """
        # The locale module can't deal with collation-qualified
        # locales and setting one blows up setlocale, so we use
        # $COLLATION directly instead.
        if ('COLLATION') in os.environ:
            apple_collation = os.environ['COLLATION']
        else:
            apple_collation = _mac_get_gramps_defaults("Gramps",
                                                       "AppleCollationOrder")
        if not apple_collation:
            apple_collation = _mac_get_gramps_defaults("Global",
                                                       "AppleCollationOrder")

        if not apple_collation:
            return None
        apple_collation = apple_collation.strip()
        if not apple_collation or apple_collation.startswith("root"):
            return None
        return apple_collation

#The action starts here
    _locale = None
    _failure = False
    glocale.calendar = None
    glocale.currency = None
    try:
        locale.setlocale(locale.LC_ALL, '')
        _locale = locale.getlocale()
    except locale.Error as err:
        LOG.warning("Environment locale not usable: %s", str(err))

    if not glocale.lang and _locale:
        if glocale.check_available_translations(_locale[0]):
            glocale.lang = '.'.join(_locale)
        else:
            LOG.debug("Environment locale %s not supported", _locale)

    if not glocale.lang:
        LOG.debug("Setting from the environment didn't work out, checking defaults")
        (glocale.lang, glocale.currency, glocale.calendar) = _mac_get_locale()

    glocale.coll_qualifier = None
    glocale.collation = _mac_get_collation()

    if not glocale.lang and glocale.collation:
        coll_parts = glocale.collation.split('@')
        glocale.lang = glocale.check_available_translations(coll_parts[0])

    if not glocale.lang:
        glocale.lang = "en_US.UTF-8"

    glocale.lang = locale.normalize(glocale.lang)
    if not glocale.lang.split('.')[1].lower() in ['utf8', 'utf-8']:
        LOG.debug('Forcing locale encoding to UTF-8')
        glocale.lang = '.'.join([glocale.lang.split('.')[0], 'UTF-8'])
        try:
            locale.setlocale(locale.LC_ALL, glocale.lang)
        except locale.Error:
            LOG.debug('Attempt failed, locale %s unsupported', glocale.lang)
    glocale.encoding = glocale.lang.split('.')[1]
    if not glocale.language:
        lang = locale.getlocale(locale.LC_MESSAGES)[0]
        language = [glocale.check_available_translations(lang)]
        if not language:
            LOG.debug("Environment LC_MESSAGES value %s not supported", lang)

        if "LANGUAGE" in os.environ:
            lang = [x for x in [glocale.check_available_translations(l)
                                 for l in os.environ["LANGUAGE"].split(":")]
                     if x]
            if lang and lang[0]:
                language = lang
            else:
                LOG.debug("No supported languages found in $LANGUAGE")
        if not (language and language[0]):
            translations = _mac_language_list()
            if translations and len(translations) > 0:
                language = translations
                LOG.debug("Returning Translations %s", ':'.join(translations))

        if not (language and language[0]):
            if glocale.lang:
                glocale.language = [glocale.lang[:5]]
            else:
                LOG.warning("No locale settings matching available translations found, using US English")
                glocale.lang = 'C'
                glocale.language = ['en']
                glocale.encoding = 'utf-8'
        else:
            glocale.language = language
            if not glocale.lang:
                glocale.lang = locale.normalize(glocale.language[0])
                glocale.encoding = glocale.lang.split('.')[1]
    LOG.debug("Ended check for languages with glocale.language %s", glocale.language)

    if not glocale.collation:
        glocale.collation = locale.getlocale(locale.LC_COLLATE)[0] or glocale.lang
    if not glocale.calendar:
        time = locale.getlocale(locale.LC_TIME)[0]
        if glocale.check_available_translations(time):
            glocale.calendar = time
        else:
            glocale.calendar = glocale.lang[:5]

    if not glocale.currency:
        glocale.currency = locale.getlocale(locale.LC_MONETARY)[0] or glocale.lang

    glocale.numeric = locale.getlocale(locale.LC_NUMERIC)[0] or glocale.lang
