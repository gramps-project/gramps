#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
# Copyright (C) 2010       Brian G. Matherly
# Copyright (C) 2014       Paul Franklin
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

"""
Class handling language-specific displaying of names.

Specific symbols for parts of a name are defined:

    ======  ===============================================================
    Symbol  Description
    ======  ===============================================================
    't'     title
    'f'     given (first names)
    'l'     full surname (lastname)
    'c'     callname
    'x'     nick name, call, or otherwise first first name (common name)
    'i'     initials of the first names
    'm'     primary surname (main)
    '0m'    primary surname prefix
    '1m'    primary surname surname
    '2m'    primary surname connector
    'y'     pa/matronymic surname (father/mother) - assumed unique
    '0y'    pa/matronymic prefix
    '1y'    pa/matronymic surname
    '2y'    pa/matronymic connector
    'o'     surnames without pa/matronymic and primary
    'r'     non primary surnames (rest)
    'p'     list of all prefixes
    'q'     surnames without prefixes and connectors
    's'     suffix
    'n'     nick name
    'g'     family nick name
    ======  ===============================================================
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import re
import logging

LOG = logging.getLogger(".gramps.gen")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import ARABIC_COMMA, ARABIC_SEMICOLON, GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from ..lib.name import Name
from ..lib.nameorigintype import NameOriginType

try:
    from ..config import config

    WITH_GRAMPS_CONFIG = True
except ImportError:
    WITH_GRAMPS_CONFIG = False


# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
_FIRSTNAME = 4
_SURNAME_LIST = 5
_SUFFIX = 6
_TITLE = 7
_TYPE = 8
_GROUP = 9
_SORT = 10
_DISPLAY = 11
_CALL = 12
_NICK = 13
_FAMNICK = 14
_SURNAME_IN_LIST = 0
_PREFIX_IN_LIST = 1
_PRIMARY_IN_LIST = 2
_TYPE_IN_LIST = 3
_CONNECTOR_IN_LIST = 4
_ORIGINPATRO = NameOriginType.PATRONYMIC
_ORIGINMATRO = NameOriginType.MATRONYMIC

_ACT = True
_INA = False

_F_NAME = 0  # name of the format
_F_FMT = 1  # the format string
_F_ACT = 2  # if the format is active
_F_FN = 3  # name format function
_F_RAWFN = 4  # name format raw function

PAT_AS_SURN = False


# -------------------------------------------------------------------------
#
# Local functions
#
# -------------------------------------------------------------------------
# Because of occurring in an exec(), this couldn't be in a lambda:
# we sort names first on longest first, then last letter first, this to
# avoid translations of shorter terms which appear in longer ones, eg
# namelast may not be mistaken with name, so namelast must first be
# converted to %k before name is converted.
##def _make_cmp(a, b): return -cmp((len(a[1]),a[1]), (len(b[1]), b[1]))
def _make_cmp_key(a):
    return (len(a[1]), a[1])  # set reverse to True!!


# -------------------------------------------------------------------------
#
# NameDisplayError class
#
# -------------------------------------------------------------------------
class NameDisplayError(Exception):
    """
    Error used to report that the name display format string is invalid.
    """

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return self.value


# -------------------------------------------------------------------------
#
# Functions to extract data from raw lists (unserialized objects)
#
# -------------------------------------------------------------------------


def _raw_full_surname(raw_surn_data_list):
    """method for the 'l' symbol: full surnames"""
    result = ""
    for raw_surn_data in raw_surn_data_list:
        result += "%s %s %s " % (
            raw_surn_data[_PREFIX_IN_LIST],
            raw_surn_data[_SURNAME_IN_LIST],
            raw_surn_data[_CONNECTOR_IN_LIST],
        )
    return " ".join(result.split()).strip()


def _raw_primary_surname(raw_surn_data_list):
    """method for the 'm' symbol: primary surname"""
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            # if there are multiple surnames, return the primary. If there
            # is only one surname, then primary has little meaning, and we
            # assume a pa/matronymic should not be given as primary as it
            # normally is defined independently
            if (
                not PAT_AS_SURN
                and nrsur == 1
                and (
                    raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
                )
            ):
                return ""
            else:
                result = "%s %s %s" % (
                    raw_surn_data[_PREFIX_IN_LIST],
                    raw_surn_data[_SURNAME_IN_LIST],
                    raw_surn_data[_CONNECTOR_IN_LIST],
                )
                return " ".join(result.split())
    return ""


def _raw_primary_surname_only(raw_surn_data_list):
    """method to obtain the raw primary surname data, so this returns a string"""
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if (
                not PAT_AS_SURN
                and nrsur == 1
                and (
                    raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
                )
            ):
                return ""
            else:
                return raw_surn_data[_SURNAME_IN_LIST]
    return ""


def _raw_primary_prefix_only(raw_surn_data_list):
    """method to obtain the raw primary surname data"""
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if (
                not PAT_AS_SURN
                and nrsur == 1
                and (
                    raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
                )
            ):
                return ""
            else:
                return raw_surn_data[_PREFIX_IN_LIST]
    return ""


def _raw_primary_conn_only(raw_surn_data_list):
    """method to obtain the raw primary surname data"""
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if (
                not PAT_AS_SURN
                and nrsur == 1
                and (
                    raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
                )
            ):
                return ""
            else:
                return raw_surn_data[_CONNECTOR_IN_LIST]
    return ""


def _raw_patro_surname(raw_surn_data_list):
    """method for the 'y' symbol: patronymic surname"""
    for raw_surn_data in raw_surn_data_list:
        if (
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
            or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
        ):
            result = "%s %s %s" % (
                raw_surn_data[_PREFIX_IN_LIST],
                raw_surn_data[_SURNAME_IN_LIST],
                raw_surn_data[_CONNECTOR_IN_LIST],
            )
            return " ".join(result.split())
    return ""


def _raw_patro_surname_only(raw_surn_data_list):
    """method for the '1y' symbol: patronymic surname only"""
    for raw_surn_data in raw_surn_data_list:
        if (
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
            or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
        ):
            result = "%s" % (raw_surn_data[_SURNAME_IN_LIST])
            return " ".join(result.split())
    return ""


def _raw_patro_prefix_only(raw_surn_data_list):
    """method for the '0y' symbol: patronymic prefix only"""
    for raw_surn_data in raw_surn_data_list:
        if (
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
            or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
        ):
            result = "%s" % (raw_surn_data[_PREFIX_IN_LIST])
            return " ".join(result.split())
    return ""


def _raw_patro_conn_only(raw_surn_data_list):
    """method for the '2y' symbol: patronymic conn only"""
    for raw_surn_data in raw_surn_data_list:
        if (
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
            or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO
        ):
            result = "%s" % (raw_surn_data[_CONNECTOR_IN_LIST])
            return " ".join(result.split())
    return ""


def _raw_nonpatro_surname(raw_surn_data_list):
    """method for the 'o' symbol: full surnames without pa/matronymic or
    primary
    """
    result = ""
    for raw_surn_data in raw_surn_data_list:
        if (
            (not raw_surn_data[_PRIMARY_IN_LIST])
            and raw_surn_data[_TYPE_IN_LIST][0] != _ORIGINPATRO
            and raw_surn_data[_TYPE_IN_LIST][0] != _ORIGINMATRO
        ):
            result += "%s %s %s " % (
                raw_surn_data[_PREFIX_IN_LIST],
                raw_surn_data[_SURNAME_IN_LIST],
                raw_surn_data[_CONNECTOR_IN_LIST],
            )
    return " ".join(result.split()).strip()


def _raw_nonprimary_surname(raw_surn_data_list):
    """method for the 'r' symbol: nonprimary surnames"""
    result = ""
    for raw_surn_data in raw_surn_data_list:
        if not raw_surn_data[_PRIMARY_IN_LIST]:
            result = "%s %s %s %s" % (
                result,
                raw_surn_data[_PREFIX_IN_LIST],
                raw_surn_data[_SURNAME_IN_LIST],
                raw_surn_data[_CONNECTOR_IN_LIST],
            )
    return " ".join(result.split())


def _raw_prefix_surname(raw_surn_data_list):
    """method for the 'p' symbol: all prefixes"""
    result = ""
    for raw_surn_data in raw_surn_data_list:
        result += "%s " % (raw_surn_data[_PREFIX_IN_LIST])
    return " ".join(result.split()).strip()


def _raw_single_surname(raw_surn_data_list):
    """method for the 'q' symbol: surnames without prefix and connectors"""
    result = ""
    for raw_surn_data in raw_surn_data_list:
        result += "%s " % (raw_surn_data[_SURNAME_IN_LIST])
    return " ".join(result.split()).strip()


def cleanup_name(namestring):
    """Remove too long white space due to missing name parts,
    so "a   b" becomes "a b" and "a , b" becomes "a, b"
    """
    parts = namestring.split()
    if not parts:
        return ""
    result = parts[0]
    for val in parts[1:]:
        if len(val) == 1 and val in [",", ";", ":", ARABIC_COMMA, ARABIC_SEMICOLON]:
            result += val
        else:
            result += " " + val

    result = result.replace(" - ", "-")
    return result


# -------------------------------------------------------------------------
#
# NameDisplay class
#
# -------------------------------------------------------------------------
class NameDisplay:
    """
    Base class for displaying of Name instances.

    Property:
      *default_format*
        the default name format to use
      *pas_as_surn*
        if only one surname, see if pa/ma should be considered as 'the' surname.
    """

    format_funcs = {}
    raw_format_funcs = {}

    def __init__(self, xlocale=glocale):
        """
        Initialize the NameDisplay class.

        If xlocale is passed in (a GrampsLocale), then
        the translated script will be returned instead.

        :param xlocale: allow selection of the displayer script
        :type xlocale: a GrampsLocale instance
        """
        global WITH_GRAMPS_CONFIG
        global PAT_AS_SURN

        # Translators: needed for Arabic, ignore otherwise
        COMMAGLYPH = xlocale.translation.gettext(",")

        self.STANDARD_FORMATS = [
            (Name.DEF, _("Default format (defined by Gramps preferences)"), "", _ACT),
            (Name.LNFN, _("Surname, Given Suffix"), "%l" + COMMAGLYPH + " %f %s", _ACT),
            (Name.FN, _("Given"), "%f", _ACT),
            (Name.FNLN, _("Given Surname Suffix"), "%f %l %s", _ACT),
            # primary name primconnector other, given pa/matronynic suffix, primprefix
            # Translators: long string, have a look at Preferences dialog
            (
                Name.LNFNP,
                _("Main Surnames, Given Patronymic Suffix Prefix"),
                "%1m %2m %o" + COMMAGLYPH + " %f %1y %s %0m",
                _ACT,
            ),
            # DEPRECATED FORMATS
            (Name.PTFN, _("Patronymic, Given"), "%y" + COMMAGLYPH + " %s %f", _INA),
        ]

        self.LNFN_STR = "%s" + COMMAGLYPH + " %s %s"

        self.name_formats = {}

        if WITH_GRAMPS_CONFIG:
            self.default_format = config.get("preferences.name-format")
            if self.default_format == 0:
                self.default_format = Name.LNFN
                config.set("preferences.name-format", self.default_format)
            # if only one surname, see if pa/ma should be considered as
            # 'the' surname.
            PAT_AS_SURN = config.get("preferences.patronimic-surname")
            config.connect("preferences.patronimic-surname", self.change_pa_sur)
        else:
            self.default_format = Name.LNFN
            PAT_AS_SURN = False

        # preinit the name formats, this should be updated with the data
        # in the database once a database is loaded
        self.set_name_format(self.STANDARD_FORMATS)

    def change_pa_sur(self, *args):
        """How to handle single patronymic as surname is changed"""
        global PAT_AS_SURN
        PAT_AS_SURN = config.get("preferences.patronimic-surname")

    def get_pat_as_surn(self):
        global PAT_AS_SURN
        return PAT_AS_SURN

    def _format_fn(self, fmt_str):
        return lambda x: self.format_str(x, fmt_str)

    def _format_raw_fn(self, fmt_str):
        return lambda x: self.format_str_raw(x, fmt_str)

    def _raw_lnfn(self, raw_data):
        result = self.LNFN_STR % (
            _raw_full_surname(raw_data[_SURNAME_LIST]),
            raw_data[_FIRSTNAME],
            raw_data[_SUFFIX],
        )
        return " ".join(result.split())

    def _raw_fnln(self, raw_data):
        result = "%s %s %s" % (
            raw_data[_FIRSTNAME],
            _raw_full_surname(raw_data[_SURNAME_LIST]),
            raw_data[_SUFFIX],
        )
        return " ".join(result.split())

    def _raw_fn(self, raw_data):
        result = raw_data[_FIRSTNAME]
        return " ".join(result.split())

    def clear_custom_formats(self):
        self.name_formats = {
            num: value for num, value in self.name_formats.items() if num >= 0
        }

    def set_name_format(self, formats):
        raw_func_dict = {
            Name.LNFN: self._raw_lnfn,
            Name.FNLN: self._raw_fnln,
            Name.FN: self._raw_fn,
        }

        for num, name, fmt_str, act in formats:
            func = self._format_fn(fmt_str)
            func_raw = raw_func_dict.get(num, self._format_raw_fn(fmt_str))
            self.name_formats[num] = (name, fmt_str, act, func, func_raw)
        self.set_default_format(self.get_default_format())

    def add_name_format(self, name, fmt_str):
        for num in self.name_formats:
            if fmt_str in self.name_formats.get(num):
                return num
        num = -1
        while num in self.name_formats:
            num -= 1
        self.set_name_format([(num, name, fmt_str, _ACT)])
        return num

    def edit_name_format(self, num, name, fmt_str):
        self.set_name_format([(num, name, fmt_str, _ACT)])
        if self.default_format == num:
            self.set_default_format(num)

    def del_name_format(self, num):
        try:
            del self.name_formats[num]
        except:
            pass

    def set_default_format(self, num):
        if num not in self.name_formats:
            num = Name.LNFN
        # if user sets default format to the Gramps default format,
        # then we select LNFN as format.
        if num == Name.DEF:
            num = Name.LNFN

        self.default_format = num

        self.name_formats[Name.DEF] = (
            self.name_formats[Name.DEF][_F_NAME],
            self.name_formats[Name.DEF][_F_FMT],
            self.name_formats[Name.DEF][_F_ACT],
            self.name_formats[num][_F_FN],
            self.name_formats[num][_F_RAWFN],
        )

    def get_default_format(self):
        return self.default_format

    def set_format_inactive(self, num):
        try:
            self.name_formats[num] = (
                self.name_formats[num][_F_NAME],
                self.name_formats[num][_F_FMT],
                _INA,
                self.name_formats[num][_F_FN],
                self.name_formats[num][_F_RAWFN],
            )
        except:
            pass

    def get_name_format(self, also_default=False, only_custom=False, only_active=True):
        """
        Returns a list of name formats as tuples on
        the form (index, name,fmt_str,act).
        The will contain standard formats followed
        by custom formats both in ascending order on
        their indices.
        """

        custom_formats = sorted(
            [
                (index, name, format_string, active)
                for index, (
                    name,
                    format_string,
                    active,
                    *rest,
                ) in self.name_formats.items()
                if index < 0 and (not only_active or active)
            ]
        )

        if only_custom:
            return custom_formats

        standard_formats = sorted(
            [
                (index, name, format_string, active)
                for index, (
                    name,
                    format_string,
                    active,
                    *rest,
                ) in self.name_formats.items()
                if index >= 0
                and (also_default or index)
                and (not only_active or active)
            ]
        )

        return standard_formats + custom_formats

    def _is_format_valid(self, num):
        try:
            if not self.name_formats[num][_F_ACT]:
                num = 0
        except:
            num = 0
        return num

    # -------------------------------------------------------------------------

    def _gen_raw_func(self, format_str):
        """The job of building the name from a format string is rather
        expensive and it is called lots and lots of times. So it is worth
        going to some length to optimise it as much as possible.

        This method constructs a new function that is specifically written
        to format a name given a particular format string. This is worthwhile
        because the format string itself rarely changes, so by caching the new
        function and calling it directly when asked to format a name to the
        same format string again we can be as quick as possible.

        The new function is of the form::

        def fn(raw_data):
            return "%s %s %s" % (raw_data[_TITLE],
                   raw_data[_FIRSTNAME],
                   raw_data[_SUFFIX])

        Specific symbols for parts of a name are defined (keywords given):
        't' : title = title
        'f' : given = given (first names)
        'l' : surname = full surname (lastname)
        'c' : call = callname
        'x' : common = nick name, call, otherwise first first name (common name)
        'i' : initials = initials of the first names
        'm' : primary = primary surname (main)
        '0m': primary[pre]= prefix primary surname (main)
        '1m': primary[sur]= surname primary surname (main)
        '2m': primary[con]= connector primary surname (main)
        'y' : patronymic = pa/matronymic surname (father/mother) - assumed unique
        '0y': patronymic[pre] = prefix      "
        '1y': patronymic[sur] = surname     "
        '2y': patronymic[con] = connector   "
        'o' : notpatronymic = surnames without pa/matronymic and primary
        'r' : rest = non primary surnames
        'p' : prefix = list of all prefixes
        'q' : rawsurnames = surnames without prefixes and connectors
        's' : suffix = suffix
        'n' : nickname = nick name
        'g' : familynick = family nick name


        """

        # we need the names of each of the variables or methods that are
        # called to fill in each format flag.
        # Dictionary is "code": ("expression", "keyword", "i18n-keyword")
        d = {
            "t": ("raw_data[_TITLE]", "title", _("title", "Person")),
            "f": ("raw_data[_FIRSTNAME]", "given", _("given")),
            "l": (
                "_raw_full_surname(raw_data[_SURNAME_LIST])",
                "surname",
                _("surname"),
            ),
            "s": ("raw_data[_SUFFIX]", "suffix", _("suffix")),
            "c": ("raw_data[_CALL]", "call", _("call", "Name")),
            "x": (
                "(raw_data[_NICK] or raw_data[_CALL] or raw_data[_FIRSTNAME].split(' ')[0])",
                "common",
                _("common", "Name"),
            ),
            "i": (
                "''.join([word[0] +'.' for word in ('. ' +"
                + " raw_data[_FIRSTNAME]).split()][1:])",
                "initials",
                _("initials"),
            ),
            "m": (
                "_raw_primary_surname(raw_data[_SURNAME_LIST])",
                "primary",
                _("primary", "Name"),
            ),
            "0m": (
                "_raw_primary_prefix_only(raw_data[_SURNAME_LIST])",
                "primary[pre]",
                _("primary[pre]"),
            ),
            "1m": (
                "_raw_primary_surname_only(raw_data[_SURNAME_LIST])",
                "primary[sur]",
                _("primary[sur]"),
            ),
            "2m": (
                "_raw_primary_conn_only(raw_data[_SURNAME_LIST])",
                "primary[con]",
                _("primary[con]"),
            ),
            "y": (
                "_raw_patro_surname(raw_data[_SURNAME_LIST])",
                "patronymic",
                _("patronymic"),
            ),
            "0y": (
                "_raw_patro_prefix_only(raw_data[_SURNAME_LIST])",
                "patronymic[pre]",
                _("patronymic[pre]"),
            ),
            "1y": (
                "_raw_patro_surname_only(raw_data[_SURNAME_LIST])",
                "patronymic[sur]",
                _("patronymic[sur]"),
            ),
            "2y": (
                "_raw_patro_conn_only(raw_data[_SURNAME_LIST])",
                "patronymic[con]",
                _("patronymic[con]"),
            ),
            "o": (
                "_raw_nonpatro_surname(raw_data[_SURNAME_LIST])",
                "notpatronymic",
                _("notpatronymic"),
            ),
            "r": (
                "_raw_nonprimary_surname(raw_data[_SURNAME_LIST])",
                "rest",
                _("rest", "Remaining names"),
            ),
            "p": (
                "_raw_prefix_surname(raw_data[_SURNAME_LIST])",
                "prefix",
                _("prefix"),
            ),
            "q": (
                "_raw_single_surname(raw_data[_SURNAME_LIST])",
                "rawsurnames",
                _("rawsurnames"),
            ),
            "n": ("raw_data[_NICK]", "nickname", _("nickname")),
            "g": ("raw_data[_FAMNICK]", "familynick", _("familynick")),
        }
        args = "raw_data"
        return self._make_fn(format_str, d, args)

    def _gen_cooked_func(self, format_str):
        """The job of building the name from a format string is rather
        expensive and it is called lots and lots of times. So it is worth
        going to some length to optimise it as much as possible.

        This method constructs a new function that is specifically written
        to format a name given a particular format string. This is worthwhile
        because the format string itself rarely changes, so by caching the new
        function and calling it directly when asked to format a name to the
        same format string again we can be as quick as possible.

        The new function is of the form::

        def fn(first, raw_surname_list, suffix, title, call,):
            return "%s %s" % (first,suffix)

        Specific symbols for parts of a name are defined (keywords given):
        't' : title = title
        'f' : given = given (first names)
        'l' : surname = full surname (lastname)
        'c' : call = callname
        'x' : common = nick name, call, or otherwise first first name (common name)
        'i' : initials = initials of the first names
        'm' : primary = primary surname (main)
        '0m': primary[pre]= prefix primary surname (main)
        '1m': primary[sur]= surname primary surname (main)
        '2m': primary[con]= connector primary surname (main)
        'y' : patronymic = pa/matronymic surname (father/mother) - assumed unique
        '0y': patronymic[pre] = prefix      "
        '1y': patronymic[sur] = surname     "
        '2y': patronymic[con] = connector   "
        'o' : notpatronymic = surnames without pa/matronymic and primary
        'r' : rest = non primary surnames
        'p' : prefix = list of all prefixes
        'q' : rawsurnames = surnames without prefixes and connectors
        's' : suffix = suffix
        'n' : nickname = nick name
        'g' : familynick = family nick name

        """

        # we need the names of each of the variables or methods that are
        # called to fill in each format flag.
        # Dictionary is "code": ("expression", "keyword", "i18n-keyword")
        d = {
            "t": ("title", "title", _("title", "Person")),
            "f": ("first", "given", _("given")),
            "l": ("_raw_full_surname(raw_surname_list)", "surname", _("surname")),
            "s": ("suffix", "suffix", _("suffix")),
            "c": ("call", "call", _("call", "Name")),
            "x": (
                "(nick or call or first.split(' ')[0])",
                "common",
                _("common", "Name"),
            ),
            "i": (
                "''.join([word[0] +'.' for word in ('. ' + first).split()][1:])",
                "initials",
                _("initials"),
            ),
            "m": (
                "_raw_primary_surname(raw_surname_list)",
                "primary",
                _("primary", "Name"),
            ),
            "0m": (
                "_raw_primary_prefix_only(raw_surname_list)",
                "primary[pre]",
                _("primary[pre]"),
            ),
            "1m": (
                "_raw_primary_surname_only(raw_surname_list)",
                "primary[sur]",
                _("primary[sur]"),
            ),
            "2m": (
                "_raw_primary_conn_only(raw_surname_list)",
                "primary[con]",
                _("primary[con]"),
            ),
            "y": (
                "_raw_patro_surname(raw_surname_list)",
                "patronymic",
                _("patronymic"),
            ),
            "0y": (
                "_raw_patro_prefix_only(raw_surname_list)",
                "patronymic[pre]",
                _("patronymic[pre]"),
            ),
            "1y": (
                "_raw_patro_surname_only(raw_surname_list)",
                "patronymic[sur]",
                _("patronymic[sur]"),
            ),
            "2y": (
                "_raw_patro_conn_only(raw_surname_list)",
                "patronymic[con]",
                _("patronymic[con]"),
            ),
            "o": (
                "_raw_nonpatro_surname(raw_surname_list)",
                "notpatronymic",
                _("notpatronymic"),
            ),
            "r": (
                "_raw_nonprimary_surname(raw_surname_list)",
                "rest",
                _("rest", "Remaining names"),
            ),
            "p": ("_raw_prefix_surname(raw_surname_list)", "prefix", _("prefix")),
            "q": (
                "_raw_single_surname(raw_surname_list)",
                "rawsurnames",
                _("rawsurnames"),
            ),
            "n": ("nick", "nickname", _("nickname")),
            "g": ("famnick", "familynick", _("familynick")),
        }
        args = "first,raw_surname_list,suffix,title,call,nick,famnick"
        return self._make_fn(format_str, d, args)

    def format_str(self, name, format_str):
        return self._format_str_base(
            name.first_name,
            name.surname_list,
            name.suffix,
            name.title,
            name.call,
            name.nick,
            name.famnick,
            format_str,
        )

    def format_str_raw(self, raw_data, format_str):
        """
        Format a name from the raw name list. To make this as fast as possible
        this uses :func:`_gen_raw_func` to generate a new method for each new
        format_string.

        Is does not call :meth:`_format_str_base` because it would introduce an
        extra method call and we need all the speed we can squeeze out of this.
        """
        func = self.__class__.raw_format_funcs.get(format_str)
        if func is None:
            func = self._gen_raw_func(format_str)
            self.__class__.raw_format_funcs[format_str] = func

        return func(raw_data)

    def _format_str_base(
        self, first, surname_list, suffix, title, call, nick, famnick, format_str
    ):
        """
        Generates name from a format string.

        The following substitutions are made:
        '%t' : title
        '%f' : given (first names)
        '%l' : full surname (lastname)
        '%c' : callname
        '%x' : nick name, call, or otherwise first first name (common name)
        '%i' : initials of the first names
        '%m' : primary surname (main)
        '%0m': prefix primary surname (main)
        '%1m': surname primary surname (main)
        '%2m': connector primary surname (main)
        '%y' : pa/matronymic surname (father/mother) - assumed unique
        '%0y': prefix      "
        '%1y': surname     "
        '%2y': connector   "
        '%o' : surnames without patronymic
        '%r' : non-primary surnames (rest)
        '%p' : list of all prefixes
        '%q' : surnames without prefixes and connectors
        '%s' : suffix
        '%n' : nick name
        '%g' : family nick name
        The capital letters are substituted for capitalized name components.
        The %% is substituted with the single % character.
        All the other characters in the fmt_str are unaffected.
        """
        func = self.__class__.format_funcs.get(format_str)
        if func is None:
            func = self._gen_cooked_func(format_str)
            self.__class__.format_funcs[format_str] = func
        try:
            s = func(
                first,
                [surn.serialize() for surn in surname_list],
                suffix,
                title,
                call,
                nick,
                famnick,
            )
        except (
            ValueError,
            TypeError,
        ):
            raise NameDisplayError("Incomplete format string")

        return s

    # -------------------------------------------------------------------------

    def primary_surname(self, name):
        global PAT_AS_SURN
        nrsur = len(name.surname_list)
        sur = name.get_primary_surname()
        if (
            not PAT_AS_SURN
            and nrsur <= 1
            and (
                sur.get_origintype().value == _ORIGINPATRO
                or sur.get_origintype().value == _ORIGINMATRO
            )
        ):
            return ""
        return sur.get_surname()

    def sort_string(self, name):
        return "%-25s%-30s%s" % (
            self.primary_surname(name),
            name.first_name,
            name.suffix,
        )

    def sorted(self, person):
        """
        Return a text string representing the :class:`~.person.Person`
        instance's :class:`~.name.Name` in a manner that should be used for
        displaying a sortedname.

        :param person: :class:`~.person.Person` instance that contains the
                       :class:`~.name.Name` that is to be displayed. The
                       primary name is used for the display.
        :type person: :class:`~.person.Person`
        :returns: Returns the :class:`~.person.Person` instance's name
        :rtype: str
        """
        name = person.get_primary_name()
        return self.sorted_name(name)

    def sorted_name(self, name):
        """
        Return a text string representing the :class:`~.name.Name` instance
        in a manner that should be used for sorting the name in a list.

        :param name: :class:`~.name.Name` instance that is to be displayed.
        :type name: :class:`~.name.Name`
        :returns: Returns the :class:`~.name.Name` string representation
        :rtype: str
        """
        num = self._is_format_valid(name.sort_as)
        return self.name_formats[num][_F_FN](name)

    def truncate(self, full_name, max_length=15, elipsis="..."):
        name_out = ""
        if len(full_name) <= max_length:
            name_out = full_name
        else:
            last_space = full_name.rfind(" ", max_length)
            if (last_space) > -1:
                name_out = full_name[:last_space]
            else:
                name_out = full_name[:max_length]
            name_out += " " + elipsis
        return name_out

    def raw_sorted_name(self, raw_data):
        """
        Return a text string representing the :class:`~.name.Name` instance
        in a manner that should be used for sorting the name in a list.

        :param name: raw unserialized data of name that is to be displayed.
        :type name: tuple
        :returns: Returns the :class:`~.name.Name` string representation
        :rtype: str
        """
        num = self._is_format_valid(raw_data[_SORT])
        return self.name_formats[num][_F_RAWFN](raw_data)

    def display(self, person):
        """
        Return a text string representing the :class:`~.person.Person`
        instance's :class:`~.name.Name` in a manner that should be used for
        normal displaying.

        :param person: :class:`~.person.Person` instance that contains the
                       :class:`~.name.Name` that is to be displayed. The
                       primary name is used for the display.
        :type person: :class:`~.person.Person`
        :returns: Returns the :class:`~.person.Person` instance's name
        :rtype: str
        """
        name = person.get_primary_name()
        return self.display_name(name)

    def display_format(self, person, num):
        """
        Return a text string representing the L{gen.lib.Person} instance's
        L{Name} using num format.

        @param person: L{gen.lib.Person} instance that contains the
        L{Name} that is to be displayed. The primary name is used for
        the display.
        @type person: L{gen.lib.Person}
        @param num: num of the format to be used, as return by
        name_displayer.add_name_format('name','format')
        @type num: int
        @returns: Returns the L{gen.lib.Person} instance's name
        @rtype: str
        """
        name = person.get_primary_name()
        return self.name_formats[num][_F_FN](name)

    def display_formal(self, person):
        """
        Return a text string representing the :class:`~.person.Person`
        instance's :class:`~.name.Name` in a manner that should be used for
        formal displaying.

        :param person: :class:`~.person.Person` instance that contains the
                       :class:`~.name.Name` that is to be displayed. The
                       primary name is used for the display.
        :type person: :class:`~.person.Person`
        :returns: Returns the :class:`~.person.Person` instance's name
        :rtype: str
        """
        # FIXME: At this time, this is just duplicating display() method
        name = person.get_primary_name()
        return self.display_name(name)

    def display_name(self, name):
        """
        Return a text string representing the :class:`~.name.Name` instance
        in a manner that should be used for normal displaying.

        :param name: :class:`~.name.Name` instance that is to be displayed.
        :type name: :class:`~.name.Name`
        :returns: Returns the :class:`~.name.Name` string representation
        :rtype: str
        """
        if name is None:
            return ""

        num = self._is_format_valid(name.display_as)
        return self.name_formats[num][_F_FN](name)

    def raw_display_name(self, raw_data):
        """
        Return a text string representing the :class:`~.name.Name` instance
        in a manner that should be used for normal displaying.

        :param name: raw unserialized data of name that is to be displayed.
        :type name: tuple
        :returns: Returns the :class:`~.name.Name` string representation
        :rtype: str
        """
        num = self._is_format_valid(raw_data[_DISPLAY])
        return self.name_formats[num][_F_RAWFN](raw_data)

    def display_given(self, person):
        return self.format_str(person.get_primary_name(), "%f")

    def name_grouping(self, db, person):
        """
        Return the name under which to group this person. This is defined as:

        1. if group name is defined on primary name, use that
        2. if group name is defined for the primary surname of the primary
           name, use that
        3. use primary surname of primary name otherwise
        """
        return self.name_grouping_name(db, person.primary_name)

    def name_grouping_name(self, db, pn):
        """
        Return the name under which to group. This is defined as:

        1. if group name is defined, use that
        2. if group name is defined for the primary surname, use that
        3. use primary surname itself otherwise

        :param pn: :class:`~.name.Name` object
        :type pn: :class:`~.name.Name` instance
        :returns: Returns the groupname string representation
        :rtype: str
        """
        if pn.group_as:
            return pn.group_as
        return db.get_name_group_mapping(pn.get_primary_surname().get_surname())

    def name_grouping_data(self, db, pn):
        """
        Return the name under which to group. This is defined as:

        1. if group name is defined, use that
        2. if group name is defined for the primary surname, use that
        3. use primary surname itself otherwise
        4. if no primary surname, do we have a ma/patronymic surname ?
           in this case, group name will be the ma/patronymic name.

        :param pn: raw unserialized data of name
        :type pn: tuple
        :returns: Returns the groupname string representation
        :rtype: str
        """
        if pn[_GROUP]:
            return pn[_GROUP]
        name = pn[_GROUP]
        if not name:
            # if we have no primary surname, perhaps we have a
            # patronymic/matronynic name ?
            srnme = pn[_ORIGINPATRO]
            surname = []
            for _surname in srnme:
                if (
                    _surname[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or _surname[_TYPE_IN_LIST][0] == _ORIGINMATRO
                ):
                    # Yes, we have one.
                    surname = [_surname]
            # name1 is the ma/patronymic name.
            name1 = _raw_patro_surname_only(surname)
            if name1 and len(srnme) == 1:
                name = db.get_name_group_mapping(name1)
        if not name:
            name = db.get_name_group_mapping(
                _raw_primary_surname_only(pn[_SURNAME_LIST])
            )
        return name

    def _make_fn(self, format_str, d, args):
        """
        Create the name display function and handles dependent
        punctuation.
        """
        # d is a dict: dict[code] = (expr, word, translated word)

        # First, go through and do internationalization-based
        # key-word replacement. Just replace ikeywords with
        # %codes (ie, replace "irstnamefay" with "%f", and
        # "IRSTNAMEFAY" for %F)

        if len(format_str) > 2 and format_str[0] == format_str[-1] == '"':
            pass
        else:
            d_keys = [(code, _tuple[2]) for code, _tuple in d.items()]
            d_keys.sort(
                key=_make_cmp_key, reverse=True
            )  # reverse on length and by ikeyword
            for code, ikeyword in d_keys:
                exp, keyword, ikeyword = d[code]
                format_str = format_str.replace(ikeyword, "%" + code)
                format_str = format_str.replace(ikeyword.title(), "%" + code)
                format_str = format_str.replace(ikeyword.upper(), "%" + code.upper())
        # Next, go through and do key-word replacement.
        # Just replace keywords with
        # %codes (ie, replace "firstname" with "%f", and
        # "FIRSTNAME" for %F)
        if len(format_str) > 2 and format_str[0] == format_str[-1] == '"':
            pass
        else:
            d_keys = [(code, _tuple[1]) for code, _tuple in d.items()]
            d_keys.sort(
                key=_make_cmp_key, reverse=True
            )  # reverse sort on length and by keyword
            # if in double quotes, just use % codes
            for code, keyword in d_keys:
                exp, keyword, ikeyword = d[code]
                format_str = format_str.replace(keyword, "%" + code)
                format_str = format_str.replace(keyword.title(), "%" + code)
                format_str = format_str.replace(keyword.upper(), "%" + code.upper())
        # Get lower and upper versions of codes:
        codes = list(d.keys()) + [c.upper() for c in d]
        # Next, list out the matching patterns:
        # If it starts with "!" however, treat the punctuation verbatim:
        if len(format_str) > 0 and format_str[0] == "!":
            patterns = [
                "%(" + ("|".join(codes)) + ")",  # %s
            ]
            format_str = format_str[1:]
        else:
            patterns = [
                ',\\W*"%(' + ("|".join(codes)) + ')"',  # ,\W*"%s"
                ",\\W*\\(%(" + ("|".join(codes)) + ")\\)",  # ,\W*(%s)
                ",\\W*%(" + ("|".join(codes)) + ")",  # ,\W*%s
                '"%(' + ("|".join(codes)) + ')"',  # "%s"
                "_%(" + ("|".join(codes)) + ")_",  # _%s_
                "\\(%(" + ("|".join(codes)) + ")\\)",  # (%s)
                "%(" + ("|".join(codes)) + ")",  # %s
            ]
        new_fmt = format_str

        # replace the specific format string flags with a
        # flag that works in standard python format strings.
        new_fmt = re.sub("|".join(patterns), "%s", new_fmt)

        # replace special meaning codes we need to have verbatim in output
        if len(new_fmt) > 2 and new_fmt[0] == new_fmt[-1] == '"':
            new_fmt = new_fmt.replace("\\", r"\\")
            new_fmt = new_fmt[1:-1].replace('"', r"\"")
        else:
            new_fmt = new_fmt.replace("\\", r"\\")
            new_fmt = new_fmt.replace('"', '\\"')

        # find each format flag in the original format string
        # for each one we find the variable name that is needed to
        # replace it and add this to a list. This list will be used to
        # generate the replacement tuple.

        # This compiled pattern should match all of the format codes.
        pat = re.compile("|".join(patterns))
        param = ()
        mat = pat.search(format_str)
        while mat:
            match_pattern = mat.group(0)  # the matching pattern
            # prefix, code, suffix:
            p, code, s = re.split("%(.)", match_pattern)
            if code in "0123456789":
                code = code + s[0]
                s = s[1:]
            field = d[code.lower()][0]
            if code.isupper():
                field += ".upper()"
            if p == "" and s == "":
                param = param + (field,)
            else:
                param = param + ("ifNotEmpty(%s,'%s','%s')" % (field, p, s),)
            mat = pat.search(format_str, mat.end())
        s = """
def fn(%s):
    def ifNotEmpty(str,p,s):
        if str == '':
            return ''
        else:
            return p + str + s
    return cleanup_name("%s" %% (%s))""" % (
            args,
            new_fmt,
            ",".join(param),
        )
        try:
            exec(s) in globals(), locals()
            return locals()["fn"]
        except:
            LOG.error(
                "\n"
                + "Wrong name format string %s" % new_fmt
                + "\n"
                + ("ERROR, Edit Name format in Preferences->Display to correct")
                + "\n"
                + _("Wrong name format string %s") % new_fmt
                + "\n"
                + ("ERROR, Edit Name format in Preferences->Display to correct")
            )

            def errfn(*arg):
                return _("ERROR, Edit Name format in Preferences")

            return errfn


displayer = NameDisplay()
