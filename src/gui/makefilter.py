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

