#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

import time
from .editors import EditFilter
from gramps.gen.const import CUSTOM_FILTERS
from gramps.gen.filters import (
    rules,
    FilterList,
    GenericFilterFactory,
    reload_custom_filters,
)
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from collections import abc


def make_filter(dbstate, uistate, objclass, gramps_ids, title=None):
    """
    Makes a Gramps Filter through dialog from a enumeration (list,
    set, etc.) of gramps_ids of type objclass.

    >>> make_filter(dbstate, uistate, 'Person', ['I0003', ...])
    """
    FilterClass = GenericFilterFactory(objclass)
    rule = getattr(getattr(rules, objclass.lower()), "RegExpIdOf")
    filter = FilterClass()
    if title is None:
        title = _("Filter %s from Clipboard") % objclass
    if isinstance(title, abc.Callable):
        title = title()
    filter.set_name(title)
    struct_time = time.localtime()
    filter.set_comment(
        _("Created on %(year)4d/%(month)02d/%(day)02d")
        % {
            "year": struct_time.tm_year,
            "month": struct_time.tm_mon,
            "day": struct_time.tm_mday,
        }
    )
    re = "|".join(["^%s$" % gid for gid in sorted(gramps_ids)])
    re_rule = rule([re])
    re_rule.use_regex = True
    filter.add_rule(re_rule)
    filterdb = FilterList(CUSTOM_FILTERS)
    filterdb.load()
    EditFilter(
        objclass,
        dbstate,
        uistate,
        [],
        filter,
        filterdb,
        lambda: edit_filter_save(uistate, filterdb, objclass),
    )


def edit_filter_save(uistate, filterdb, objclass):
    """
    If a filter changed, save them all. Reloads, and also calls callback.
    """
    filterdb.save()
    reload_custom_filters()
    uistate.emit("filters-changed", (objclass,))
