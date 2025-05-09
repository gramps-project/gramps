# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program - Records plugin
#
# Copyright (C) 2020      Paul Culley
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

# ------------------------------------------------------------------------
#
# Standard Python modules
#
# ------------------------------------------------------------------------
import logging

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.lib.placegrouptype import PlaceGroupType as P_G
from gramps.gen.lib.placetype import PlaceType
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
LOG = logging.getLogger()


# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value, context=""):  # enable deferred translations
    return "%s\x04%s" % (context, value) if context else value


try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.sgettext

_report_trans = None
_report_lang = None


def translate_func(ptype, locale=None, pt_id=None):
    """
    This function provides translations for the locally defined place types.
    It is called by the place type display code for the GUI and reports.

    The locale parameter is an instance of a GrampsLocale.  This is used to
    determine the language for tranlations. (locale.lang)  It is also used
    as a backup translation if no local po/mo file is present.

    :param ptype: the placetype translatable string
    :type ptype: str
    :param locale: the backup locale
    :type locale: GrampsLocale instance
    :returns: display string of the place type
    :rtype: str
    """
    global _report_lang, _report_trans
    if locale is None or locale is glocale:
        # using GUI language.
        return _(ptype)
    if locale.lang == _report_lang:
        # We already created this locale, so use the previous version
        # this will speed up reports in an alternate language
        return _report_trans(ptype)
    # We need to create a new language specific addon translator instance
    try:
        _r_trans = glocale.get_addon_translator(__file__, languages=(locale.lang,))
    except ValueError:
        _r_trans = glocale.translation
    _report_trans = _r_trans.sgettext
    _report_lang = locale.lang
    return _report_trans(ptype)


# The data map (dict) contains a tuple with key as a handle and data as tuple;
#   translatable name
#   native name
#   color (used for map markers, I suggest picking by probable group)
#   probable group (used for legacy XML import and preloading Group in place
#                   editor)
#   gettext method (or None if standard method)
DATAMAP = {
    # add the common "Country" to the NL menu
    "Country": (_T_("Country"), "Country", "#FFFF00000000", P_G(P_G.COUNTRY), None),
    "nl_Province": (
        _T_("Province", "nl"),
        "Provincie",
        "#0000FFFFFFFF",
        P_G(P_G.REGION),
        translate_func,
    ),
    "nl_Municipality": (
        _T_("Municipality", "nl"),
        "Gemeente",
        "#0000FFFFFFFF",
        P_G(P_G.REGION),
        translate_func,
    ),
    "nl_City": (
        _T_("City", "nl"),
        "Stad",
        "#0000FFFF0000",
        P_G(P_G.PLACE),
        translate_func,
    ),
    "nl_Place": (
        _T_("Place", "nl"),
        "Plaats",
        "#0000FFFF0000",
        P_G(P_G.PLACE),
        translate_func,
    ),
    "nl_Village": (
        _T_("Village", "nl"),
        "Dorp",
        "#0000FFFF0000",
        P_G(P_G.PLACE),
        translate_func,
    ),
}


def load_on_reg(_dbstate, _uistate, _plugin):
    """
    Runs when plugin is registered.
    """
    for hndl, tup in DATAMAP.items():
        # for these Netherlands elements, the category is 'NL'
        # For larger regions of several countries, any descriptive text can be
        # used (Holy Roman Empire)
        # the register function returns True if the handle is a duplcate
        # good idea to check this.
        duplicate = PlaceType.register_placetype(hndl.capitalize(), tup, "NL")
        if duplicate and hndl.startswith("nl_"):
            LOG.debug("Duplicate handle %s detected; please fix", hndl)
    PlaceType.update_name_map()
