#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       John Ralls <jralls@ceridwen.us>
# Copyright (C) 2013       Paul Franklin
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
Commonly used report options. Call the function, don't copy the code!
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.display.name import displayer as global_name_display
from gramps.gen.plug.menu import EnumeratedListOption

#-------------------------------------------------------------------------
#
# StandardReportOptions
#
#-------------------------------------------------------------------------

def add_localization_option(menu, category):
    """
    Insert an option for localizing the report into a different locale
    from the UI locale.
    """
    trans = EnumeratedListOption(_("Translation"),
                                 glocale.DEFAULT_TRANSLATION_STR)
    trans.add_item(glocale.DEFAULT_TRANSLATION_STR, _("Default"))
    languages = glocale.get_language_dict()
    for language in sorted(languages, key=glocale.sort_key):
        trans.add_item(languages[language], language)
    trans.set_help(_("The translation to be used for the report."))
    menu.add_option(category, "trans", trans)

def add_name_format_option(menu, category):
    """
    Insert an option for changing the report's name format to a
    report-specific format instead of the user's Edit=>Preferences choice
    """
    name_format = EnumeratedListOption(_("Name format"), 0)
    name_format.add_item(0, _("Default"))
    format_list = global_name_display.get_name_format()
    for number, name, format_string, whether_active in format_list:
        name_format.add_item(number, name)
    name_format.set_help(_("Select the format to display names"))
    menu.add_option(category, "name_format", name_format)
