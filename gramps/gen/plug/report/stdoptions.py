#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       John Ralls <jralls@ceridwen.us>
# Copyright (C) 2013-2016  Paul Franklin
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
from ...config import config
from ...display.name import displayer as global_name_display
from ..menu import EnumeratedListOption, BooleanOption, NumberOption
from ...proxy import PrivateProxyDb, LivingProxyDb
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value): # enable deferred translations (see Python docs 22.1.3.4)
    return value

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

def add_living_people_option(menu, category,
                             mode=LivingProxyDb.MODE_INCLUDE_ALL,
                             after_death_years=0,
                             process_names=True):
    """
    Insert an option for deciding how the information in the
    database for living people shall be handled by the report

    Because historically, before this option, the entire database was
    used, including all information on all living people, the default
    mode for this option has been set to include all such information

    The value of the "living_people" option is the same as the value
    of the "mode" argument in the call to the LivingProxyDb proxy DB

    :param menu: The menu the options should be added to.
    :type menu: :class:`.Menu`
    :param category: A label that describes the category that the option
        belongs to.
        Example: "Report Options"
    :type category: string
    :param mode:
        The method for handling living people.
        LivingProxyDb.MODE_EXCLUDE_ALL will remove living people altogether.
        LivingProxyDb.MODE_INCLUDE_LAST_NAME_ONLY will remove all
            information and change their given name to "[Living]" or whatever
            has been set in Preferences -> Text -> Private given name.
        LivingProxyDb.MODE_REPLACE_COMPLETE_NAME will remove all
            information and change their given name and surname to
            "[Living]" or whatever has been set in Preferences -> Text
            for Private surname and Private given name.
        LivingProxyDb.MODE_INCLUDE_FULL_NAME_ONLY will remove all
            information but leave the entire name intact.
        LivingProxyDb.MODE_INCLUDE_ALL will not invoke LivingProxyDb at all.
    :type mode: int
    :param after_death_years:
        The number of years after a person's death to
        still consider them as living.
    :type after_death_years: int
    :return: nothing
    :param process_names: whether to offer name-oriented option choices
    :type process_names: Boolean
    """

    def living_people_changed():
        """
        Handle a change in the living_people option
        """
        if living_people.get_value() == LivingProxyDb.MODE_INCLUDE_ALL:
            years_past_death.set_available(False)
        else:
            years_past_death.set_available(True)

    living_people = EnumeratedListOption(_("Living People"), mode)
    items = [(LivingProxyDb.MODE_INCLUDE_ALL,
              _T_("'living people'|Included, and all data"))]
    if process_names:
        items += [
            (LivingProxyDb.MODE_INCLUDE_FULL_NAME_ONLY,
             _T_("'living people'|Full names, but data removed")),
            (LivingProxyDb.MODE_INCLUDE_LAST_NAME_ONLY,
             _T_("'living people'|Given names replaced, and data removed")),
            (LivingProxyDb.MODE_REPLACE_COMPLETE_NAME,
             _T_("'living people'|Complete names replaced, and data removed"))]
    items += [(LivingProxyDb.MODE_EXCLUDE_ALL,
               _T_("'living people'|Not included"))]
    living_people.set_items(items, xml_items=True) # for deferred translation
    living_people.set_help(_("How to handle living people"))
    menu.add_option(category, "living_people", living_people)
    living_people.connect('value-changed', living_people_changed)
    years_past_death = NumberOption(_("Years from death to consider living"),
                                      after_death_years, 0, 100)
    years_past_death.set_help(
        _("Whether to restrict data on recently-dead people"))
    menu.add_option(category, "years_past_death", years_past_death)
    living_people_changed()

def run_living_people_option(report, menu, llocale=glocale):
    """
    Run the option for deciding how the information in the
    database for living people shall be handled by the report

    If llocale is passed in (a :class:`.GrampsLocale`), then (insofar as
    possible) the translated values will be returned instead.

    :param llocale: allow deferred translation of "[Living]"
    :type llocale: a :class:`.GrampsLocale` instance
    """
    option = menu.get_option_by_name('living_people')
    living_value = option.get_value()
    years_past_death = menu.get_option_by_name('years_past_death').get_value()
    if living_value != LivingProxyDb.MODE_INCLUDE_ALL:
        report.database = LivingProxyDb(report.database, living_value,
                                        years_after_death=years_past_death,
                                        llocale=llocale)
    return option
