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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# gui/makefilter.py
# $Id$

import time
import Filters 
from gui.filtereditor import EditFilter
import const
from Filters import reload_custom_filters
from gen.ggettext import sgettext as _

def make_filter(dbstate, uistate, objclass, gramps_ids, title=None):
    """
    Makes a Gramps Filter through dialog from a enumeration (list,
    set, etc.) of gramps_ids of type objclass.

    >>> make_filter(dbstate, uistate, 'Person', ['I0003', ...])
    """
    if objclass == "Media":
        objclass = "MediaObject"
    FilterClass = Filters.GenericFilterFactory(objclass)
    rule = getattr(getattr(Filters.Rules, objclass),'RegExpIdOf')
    filter = FilterClass()
    if title is None:
        title = _("Filter %s from Clipboard") % objclass
    if callable(title):
        title = title()
    filter.set_name(title)
    struct_time = time.localtime()
    filter.set_comment( _("Created on %4d/%02d/%02d") % 
        (struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday))
    re = "|".join(["^%s$" % gid for gid in sorted(gramps_ids)])
    filter.add_rule(rule([re]))
    filterdb = Filters.FilterList(const.CUSTOM_FILTERS)
    filterdb.load()
    EditFilter(objclass, dbstate, uistate, [],
               filter, filterdb,
               lambda : edit_filter_save(uistate, filterdb, objclass))

def edit_filter_save(uistate, filterdb, objclass):
    """
    If a filter changed, save them all. Reloads, and also calls callback.
    """
    filterdb.save()
    reload_custom_filters()
    uistate.emit('filters-changed', (objclass,))

