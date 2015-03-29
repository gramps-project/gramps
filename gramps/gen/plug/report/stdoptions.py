#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       John Ralls <jralls@ceridwen.us>
# Copyright (C) 2013-2015  Paul Franklin
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
Commonly used report options. Call the function, don't copy the code!
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.config import config
from gramps.gen.display.name import displayer as global_name_display
from gramps.gen.plug.menu import EnumeratedListOption, BooleanOption
from gramps.gen.proxy import PrivateProxyDb

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
    current_format = config.get('preferences.name-format')
    # if this report hasn't ever been run, start with user's current setting
    name_format.set_value(current_format)
    # if the report has been run, this line will get the user's old setting
    menu.add_option(category, "name_format", name_format)
    return name_format

def run_name_format_option(report, menu):
    """
    Run the option for changing the report's name format to a
    report-specific format instead of the user's Edit=>Preferences choice
    """
    current_format = config.get('preferences.name-format')
    name_format = menu.get_option_by_name("name_format").get_value()
    if name_format != current_format:
        report._name_display.set_default_format(name_format)
    return name_format

def add_private_data_option(menu, category, default=True):
    """
    Insert an option for deciding whether the information in the
    database marked "private" shall be included in the report

    Since historically, before this option, the entire database was
    used, including private information, the default for this option
    has been set to be True, to include such private information.
    """
    incl_private = BooleanOption(_("Include data marked private"), default)
    incl_private.set_help(_("Whether to include private data"))
    menu.add_option(category, "incl_private", incl_private)

def run_private_data_option(report, menu):
    """
    Run the option for deciding whether the information in the
    database marked "private" shall be included in the report
    """
    include_private_data = menu.get_option_by_name('incl_private').get_value()
    if not include_private_data:
        report.database = PrivateProxyDb(report.database)
