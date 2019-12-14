#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  B. Malengier
# Copyright (C) 2008  Brian G. Matherly
# Copyright (C) 2011       Tim G L Lyons
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
This module provides the functions to build the quick report context menu's
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from io import StringIO

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
from collections import abc
log = logging.getLogger(".quickreports")

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ...pluginmanager import GuiPluginManager
from ...uimanager import valid_action_name
from gramps.gen.plug import (CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY, CATEGORY_QR_MEDIA,
                      CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE, CATEGORY_QR_MISC,
                      CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY,
                      CATEGORY_QR_NOTE,  CATEGORY_QR_CITATION,
                      CATEGORY_QR_SOURCE_OR_CITATION)
from ._textbufdoc import TextBufDoc
from gramps.gen.simple import make_basic_stylesheet

MENUITEM = ('<item>\n'
            '<attribute name="action">{prefix}.{action}</attribute>\n'
            '<attribute name="label">'
            '{label}</attribute>\n'
            '</item>\n')

def flatten(L):
    """
    Flattens a possibly nested list. Removes None results, too.
    """
    retval = []
    if isinstance(L, (list, tuple)):
        for item in L:
            fitem = flatten(item)
            if fitem is not None:
                retval.extend(fitem)
    elif L is not None:
        retval.append(L)
    return retval

def create_web_connect_menu(dbstate, uistate, nav_group, handle, prefix):
    """
    This functions querries the registered web connects.  It collects
    the connects of the requested category, which must be one of
    nav_group.

    It constructs the ui string of the menu, and it's actions. The
    action callback function is constructed, using the dbstate and the
    handle as input method.  A tuple is returned, containing the ui
    string of the menu, and its associated actions.
    """
    top = ("<placeholder id='WebConnect'><submenu>\n"
           '<attribute name="label" translatable="yes">'
           'Web Connection</attribute>\n')
    ofile = StringIO()
    ofile.write(top)
    #select the web connects to show
    pmgr = GuiPluginManager.get_instance()
    plugins = pmgr.process_plugin_data('WebConnect')
    try:
        connections = [plug(nav_group) if isinstance(plug, abc.Callable) else
                       plug for plug in plugins]
    except BaseException:
        import traceback
        traceback.print_exc()
        connections = []
    connections = flatten(connections)
    connections.sort(key=lambda plug: plug.name)
    actions = []
    for indx, connect in enumerate(connections):
        # action would be better with "connect.key", but it seems to be
        # non-ASCII sometimes.  So we use an action number instead.
        action = "web-con-%d" % indx
        ofile.write(MENUITEM.format(prefix=prefix, action=action,
                                    label=connect.name))
        callback = connect(dbstate, uistate, nav_group, handle)
        actions.append((action, make_web_connect_callback(callback)))
    ofile.write('</submenu></placeholder>\n')
    return (ofile.getvalue(), actions)

def make_web_connect_callback(func):
    return lambda x, y: func(x)

def create_quickreport_menu(category, dbstate, uistate, handle, prefix, track=[]):
    """ This functions querries the registered quick reports with
            quick_report_list of _PluginMgr.py
        It collects the reports of the requested category, which must be one of
                        CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY,
                        CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE, CATEGORY_QR_MEDIA,
                        CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY,
                        CATEGORY_QR_CITATION, CATEGORY_QR_SOURCE_OR_CITATION
        It constructs the ui string of the quick report menu, and it's actions
        The action callback function is constructed, using the dbstate and the
            handle as input method.
        A tuple is returned, containing the ui string of the quick report menu,
        and its associated actions
    """
    top = ("<submenu>\n"
           '<attribute name="label" translatable="yes">'
           'Quick View</attribute>\n')
    actions = []
    ofile = StringIO()
    ofile.write(top)

    #select the reports to show
    showlst = []
    pmgr = GuiPluginManager.get_instance()
    for pdata in pmgr.get_reg_quick_reports():
        if pdata.supported and pdata.category == category :
            showlst.append(pdata)

    showlst.sort(key=lambda x: x.name)
    for pdata in showlst:
        new_key = valid_action_name("qr-%s" % pdata.id)
        ofile.write(MENUITEM.format(prefix=prefix, action=new_key,
                                    label=pdata.name))
        actions.append((new_key, make_quick_report_callback(
            pdata, category, dbstate, uistate, handle, track=track)))
    ofile.write('</submenu>\n')

    return (ofile.getvalue(), actions)

def make_quick_report_callback(pdata, category, dbstate, uistate, handle,
                               track=[]):
    return lambda x, y: run_report(dbstate, uistate, category, handle, pdata,
                                   track=track)

def get_quick_report_list(qv_category=None):
    """
    Returns a list of PluginData of quick views of category qv_category
    CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY, CATEGORY_QR_EVENT,
    CATEGORY_QR_SOURCE, CATEGORY_QR_MISC, CATEGORY_QR_PLACE,
    CATEGORY_QR_REPOSITORY, CATEGORY_QR_MEDIA,
    CATEGORY_QR_CITATION, CATEGORY_QR_SOURCE_OR_CITATION or None for all
    """
    names = []
    pmgr = GuiPluginManager.get_instance()
    for pdata in pmgr.get_reg_quick_reports():
        if qv_category == pdata.category or qv_category is None:
            names.append(pdata) # (see below for item struct)
    return names

def run_quick_report_by_name(dbstate, uistate, report_name, handle,
                             container=None, track=[], **kwargs):
    """
    Run a QuickView by name.
    **kwargs provides a way of passing special quick views additional
    arguments.
    """
    report = None
    pmgr = GuiPluginManager.get_instance()
    for pdata in pmgr.get_reg_quick_reports():
        if pdata.id == report_name:
            report = pdata
            break
    if report:
        return run_report(dbstate, uistate, report.category,
                          handle, report, container=container,
                          track=track, **kwargs)
    else:
        raise AttributeError("No such quick report '%s'" % report_name)

def run_quick_report_by_name_direct(report_name, database, document, handle):
    """
    Useful for running one quick report from another
    """
    report = None
    pmgr = GuiPluginManager.get_instance()
    for pdata in pmgr.get_reg_quick_reports():
        if pdata.id == report_name:
            report = pdata
            break
    if report:
        # FIXME: allow auto lookup of obj like below?
        d = TextBufDoc(make_basic_stylesheet(), None)
        d.dbstate = document.dbstate
        d.uistate = document.uistate
        d.open("")
        mod = pmgr.load_plugin(report)
        if mod:
            reportfunc = getattr(mod, report.runfunc)
            retval = reportfunc(database, d, handle)
            d.close()
            return retval
        else:
            raise ImportError("Quick report id = '%s' could not be loaded"
                                % report_name)
    else:
        raise AttributeError("No such quick report id = '%s'" % report_name)

def run_report(dbstate, uistate, category, handle, pdata, container=None,
               track=[], **kwargs):
        """
        Run a Quick Report.
        Optionally container can be passed, rather than putting the report
        in a new window.
        **kwargs are only used for special quick views that allow additional
        arguments, and that are run by run_quick_report_by_name().
        """
        pmgr = GuiPluginManager.get_instance()
        mod = pmgr.load_plugin(pdata)
        if not mod:
            print("QuickView Error: plugin does not load")
            return
        func = getattr(mod, pdata.runfunc)
        if handle:
            d = TextBufDoc(make_basic_stylesheet(), None, track=track)
            d.dbstate = dbstate
            d.uistate = uistate
            if isinstance(handle, str): # a handle
                if category == CATEGORY_QR_PERSON :
                    obj = dbstate.db.get_person_from_handle(handle)
                elif category == CATEGORY_QR_FAMILY :
                    obj = dbstate.db.get_family_from_handle(handle)
                elif category == CATEGORY_QR_EVENT :
                    obj = dbstate.db.get_event_from_handle(handle)
                elif category == CATEGORY_QR_SOURCE :
                    obj = dbstate.db.get_source_from_handle(handle)
                elif category == CATEGORY_QR_CITATION :
                    obj = dbstate.db.get_citation_from_handle(handle)
                elif category == CATEGORY_QR_SOURCE_OR_CITATION :
                    if dbstate.db.has_source_handle(handle):
                        obj = dbstate.db.get_source_from_handle(handle)
                    elif dbstate.db.has_citation_handle(handle):
                        obj = dbstate.db.get_citation_from_handle(handle)
                    else:
                        raise ValueError("selection must be either source or citation")
                elif category == CATEGORY_QR_PLACE :
                    obj = dbstate.db.get_place_from_handle(handle)
                elif category == CATEGORY_QR_MEDIA :
                    obj = dbstate.db.get_media_from_handle(handle)
                elif category == CATEGORY_QR_REPOSITORY :
                    obj = dbstate.db.get_repository_from_handle(handle)
                elif category == CATEGORY_QR_NOTE :
                    obj = dbstate.db.get_note_from_handle(handle)
                elif category == CATEGORY_QR_MISC:
                    obj = handle
                else:
                    obj = None
            else: # allow caller to send object directly
                obj = handle
            if obj:
                if container:
                    result = d.open("", container=container)
                    func(dbstate.db, d, obj, **kwargs)
                    return result
                else:
                    d.open("")
                    retval = func(dbstate.db, d, obj, **kwargs)
                    d.close()
                    return retval
            else:
                print("QuickView Error: failed to run report: no obj")
        else:
            print("QuickView Error: handle is not set")
