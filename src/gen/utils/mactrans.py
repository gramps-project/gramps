#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011	John Ralls, Fremont, CA
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

import os, subprocess

def get_available_translations(dir, domain):
    """
    Get a list of available translations.

    :returns: A list of translation languages.
    :rtype: unicode[]

    """
    languages = ["en"]

    if dir is None:
        return languages

    for langdir in os.listdir(dir):
        mofilename = os.path.join( dir, langdir,
                                   "LC_MESSAGES", "%s.mo" % domain )
        if os.path.exists(mofilename):
            languages.append(langdir)

    languages.sort()

    return languages

def mac_setup_localization(dir, domain):
    defaults = "/usr/bin/defaults"
    find = "/usr/bin/find"
    locale_dir = "/usr/share/locale"
    available = get_available_translations(dir, domain)

    def mac_language_list():
        languages = []
        try:
            languages = subprocess.Popen(
                [defaults,  "read", "-app", "Gramps", "AppleLanguages"],
                stderr=open("/dev/null"),
                stdout=subprocess.PIPE).communicate()[0].strip("()\n").split(",\n")
        except OSError:
            pass

        if len(languages) == 0 or (len(languages) == 1 and languages[0] == ""):
#            try:
            languages = subprocess.Popen(
                    [defaults, "read", "-g", "AppleLanguages"],
                    stderr=open("/dev/null"),
                    stdout=subprocess.PIPE).communicate()[0].strip("()\n").split(",\n")
#            except OSError:
#                pass
        usable = []
        for lang in languages:
            lang = lang.strip().strip('"').replace("-", "_", 1)
            if lang == "cn_Hant": #Traditional; Gettext uses cn_TW
                lang = "cn_TW"
            if lang == "cn_Hans": #Simplified; Gettext uses cn_CN
                lang = "cn_CN"

            if lang.startswith("en"): # Gramps doesn't have explicit
                usable.append("C")    # English translation, use C
                continue
            if lang in available or lang[:2] in available:
                usable.append(lang)

        return usable

    def mac_get_locale():
        locale = ""
        calendar = ""
        currency = ""
        default_locale = ""
        try:
            default_locale = subprocess.Popen(
                [defaults, "read", "-app", "Gramps", "AppleLocale"],
                stderr = open("/dev/null"),
                stdout = subprocess.PIPE).communicate()[0]
        except OSError:
            pass
        if not default_locale:
            try:
                default_locale = subprocess.Popen(
                    [defaults, "read", "-g", "AppleLocale"],
                    stderr = open("/dev/null"),
                    stdout = subprocess.PIPE).communicate()[0]
            except OSError:
                return (locale, calendar, currency)

        div = default_locale.split("@")
        locale = div[0]
        if len(div) > 1:
            div = div[1].split(";")
            for phrase in div:
                try:
                    (name, value) = phrase.split("=")
                    if name == "calendar":
                        calendar = value
                    elif name == "currency":
                        currency = value
                except OSError:
                    pass

        return (locale, calendar, currency)

    def mac_get_collation():
        collation = ""
        try:
            collation = subprocess.Popen(
                [defaults, "read", "-app", "Gramps", "AppleCollationOrder"],
                stderr = open("/dev/null"),
                stdout = subprocess.PIPE).communicate()[0]
        except OSError:
            pass
        if not collation:
            try:
                collation = subprocess.Popen(
                    [defaults, "read", "-g", "AppleCollationOrder"],
                    stderr = open("/dev/null"),
                    stdout = subprocess.PIPE).communicate()[0]
            except OSError:
                pass

        return collation

# Locale.setlocale() will throw if any LC_* environment variable isn't
# a fully qualified one present in
# /usr/share/locale. mac_resolve_locale ensures that a locale meets
# that requirement.
    def mac_resolve_locale(loc):
        if len(loc) < 2:
            return None
        if len(loc) >= 5 and os.path.exists(os.path.join(locale_dir, loc[:5])):
            return loc[:5]
        if len(loc) > 2:
            loc = loc[:2]
    # First see if it matches lang
        if (lang.startswith(loc)
            and os.path.exists(os.path.join(locale_dir, lang[:5]))):
            return lang[:5]
        else:
    # OK, no, look through the translation list, but that's not likely
    # to be 5 letters long either
            for l in translations:
                if (l.startswith(loc) and len(l) >= 5
                    and os.path.exists(os.path.join(locale_dir, l[:5]))):
                    return l[:5]
                    break

            else:
    # so as a last resort, pick the first one for that language.
                locale_list = subprocess.Popen(
                    [find, locale_dir, "-name", loc + "_[A-Z][A-Z]"],
                    stderr = open("/dev/null"),
                    stdout = subprocess.PIPE).communicate()[0].strip("()\n").split(",\n")
                if len(locale_list) > 0:
                    return os.path.basename(locale_list[0])
                else:
                    return None

# The action starts here

    (loc, currency, calendar)  = mac_get_locale()
    collation = mac_get_collation()
    translations = mac_language_list()

    if not os.environ.has_key("LANGUAGE"):
        if len(translations) > 0:
            if os.environ.has_key("MULTI_TRANSLATION"):
                os.environ["LANGUAGE"] = ":".join(translations)
            else:
                os.environ["LANGUAGE"] = translations[0]
        elif (len(loc) > 0 and loc in available
              and not locale.starts_with("en")):
            os.environ["LANGUAGE"] = locale
        elif (len(collation) > 0 and collation in available
              and not collation.starts_with("en")):
            os.environ["LANGUAGE"] = collation

    if not os.environ.has_key("LANG"):
        lang = "en_US"
        loc = mac_resolve_locale(loc)
        if loc != None:
            lang = loc
            collation = mac_resolve_locale(collation)
            if not os.environ.has_key("LC_COLLATE") and collation != None:
                os.environ["LC_COLLATE"] = collation

        elif len(collation) > 0:
            lang = mac_resolve_locale(collation)
        if lang != None:
            os.environ["LANG"] = lang
            os.environ["LC_CTYPE"] = lang + ".UTF-8"
