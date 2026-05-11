#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

from __future__ import annotations

import logging

from gramps.gen.plug.menu import FilterOption, NumberOption, BooleanOption
from gramps.gen.filters import CustomFilters, GenericFilterFactory, rules
from gramps.gui.plug import MenuToolOptions
from gramps.gen.const import GRAMPS_LOCALE as glocale

logger = logging.getLogger(__name__)

_ = glocale.translation.gettext


class CompareOptions(MenuToolOptions):
    def __init__(self, name, person_id=None, dbstate=None):
        logger.debug("CompareOptions.__init__(name=%s, person_id=%s)", name, person_id)
        self.db = dbstate.get_database() if dbstate else None
        super().__init__(name, person_id, dbstate)

    def add_menu_options(self, menu):
        logger.debug("CompareOptions.add_menu_options")
        self._add_general_options(menu)

    def _add_general_options(self, menu):
        logger.debug("CompareOptions._add_general_options")
        category_name = _("FamilySearch Compare Options")

        # days between runs
        self._opt_days_between = NumberOption(_("Days between comparisons"), 0, 0, 99)
        self._opt_days_between.set_help(_("Number of days between two comparisons."))
        menu.add_option(category_name, "gui_days", self._opt_days_between)

        # force compare
        self._opt_force = BooleanOption(_("Force comparison"), True)
        self._opt_force.set_help(
            _("Compare regardless of the number of days since the last run.")
        )
        menu.add_option(category_name, "gui_needed", self._opt_force)

        # person Filter
        all_persons_rule = rules.person.Everyone([])
        filter_option = FilterOption(_("Person Filter"), 0)
        menu.add_option(category_name, "Person", filter_option)

        filter_list = CustomFilters.get_filters("Person")
        GenericFilter = GenericFilterFactory("Person")
        all_filter = GenericFilter()
        all_filter.set_name(_("All %s") % (_("Persons")))
        all_filter.add_rule(all_persons_rule)

        # only add the generic filter if it isn't already in the menu
        if not any(fltr.get_name() == all_filter.get_name() for fltr in filter_list):
            filter_list.insert(0, all_filter)
        filter_option.set_filters(filter_list)
