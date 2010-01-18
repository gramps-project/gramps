#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  B. Malengier
# Copyright (C) 2008  Brian G. Matherly
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
This module provides the functions to build the quick report context menu's
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gen.ggettext import gettext as _
from cStringIO import StringIO

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".QuickReports")

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

from gen.plug import (CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY, CATEGORY_QR_MEDIA,
                      CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE, CATEGORY_QR_MISC,
                      CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY, CATEGORY_QR_NOTE)
from gui.pluginmanager import GuiPluginManager

def create_quickreport_menu(category,dbstate,uistate, handle) :
    """ This functions querries the registered quick reports with 
            quick_report_list of _PluginMgr.py
        It collects the reports of the requested category, which must be one of
                        CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY,
                        CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE, CATEGORY_QR_MEDIA,
                        CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY
        It constructs the ui string of the quick report menu, and it's actions
        The action callback function is constructed, using the dbstate and the
            handle as input method.
        A tuple is returned, containing the ui string of the quick report menu,
        and its associated actions
    """

    actions = []
    ofile = StringIO()
    ofile.write('<menu action="QuickReport">')
    
    actions.append(('QuickReport', None, _("Quick View"), None, None, None))
        
    menu = gtk.Menu()
    menu.show()
    
    #select the reports to show
    showlst = []
    pmgr = GuiPluginManager.get_instance()
    for pdata in pmgr.get_reg_quick_reports():
        if pdata.supported and pdata.category == category :
            #add tuple function, translated name, name, status
            showlst.append(pdata)
            
    showlst.sort(by_menu_name)
    for pdata in showlst:
        new_key = pdata.id.replace(' ', '-')
        ofile.write('<menuitem action="%s"/>' % new_key)
        actions.append((new_key, None, pdata.name, None, None, 
                make_quick_report_callback(pdata, category, 
                                           dbstate, uistate, handle)))
    ofile.write('</menu>')
    
    return (ofile.getvalue(), actions)

def by_menu_name(first, second):
    return cmp(first.name, second.name)

def make_quick_report_callback(pdata, category, dbstate, uistate, handle):
    return lambda x: run_report(dbstate, uistate, category, handle, pdata)

def get_quick_report_list(qv_category=None):
    """
    Returns a list of PluginData of quick views of category qv_category
    CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY, CATEGORY_QR_EVENT, 
    CATEGORY_QR_SOURCE, CATEGORY_QR_MISC, CATEGORY_QR_PLACE, 
    CATEGORY_QR_REPOSITORY, CATEGORY_QR_MEDIA or None for all
    """
    names = []
    pmgr = GuiPluginManager.get_instance()
    for pdata in pmgr.get_reg_quick_reports():
        if qv_category == pdata.category or qv_category is None:
            names.append(pdata) # (see below for item struct)
    return names

def run_quick_report_by_name(dbstate, uistate, report_name, handle, 
                             container=None, **kwargs):
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
                          handle, report, container=container, **kwargs)
    else:
        raise AttributeError, ("No such quick report '%s'" % report_name)

def run_quick_report_by_name_direct(report_name, database, document, handle):
    """
    Useful for running one quick report from another
    """
    from docgen import TextBufDoc
    from Simple import make_basic_stylesheet
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
            reportfunc = eval('mod.' +  report.runfunc)
            retval = reportfunc(database, d, handle)
            d.close()
            return retval
        else:
            raise ImportError, ("Quick report id = '%s' could not be loaded" 
                                % report_name)
    else:
        raise AttributeError, ("No such quick report id = '%s'" % report_name)
                            
def run_report(dbstate, uistate, category, handle, pdata, container=None, 
               **kwargs):
        """
        Run a Quick Report.
        Optionally container can be passed, rather than putting the report 
        in a new window. 
        **kwargs are only used for special quick views that allow additional
        arguments, and that are run by run_quick_report_by_name().
        """
        from docgen import TextBufDoc
        from Simple import make_basic_stylesheet
        pmgr = GuiPluginManager.get_instance()
        mod = pmgr.load_plugin(pdata)
        if not mod:
            print "QuickView Error: plugin does not load"
            return
        func =  eval('mod.' +  pdata.runfunc)
        if handle:
            d = TextBufDoc(make_basic_stylesheet(), None)
            d.dbstate = dbstate
            d.uistate = uistate
            if isinstance(handle, basestring): # a handle
                if category == CATEGORY_QR_PERSON :
                    obj = dbstate.db.get_person_from_handle(handle)
                elif category == CATEGORY_QR_FAMILY :
                    obj = dbstate.db.get_family_from_handle(handle)
                elif category == CATEGORY_QR_EVENT :
                    obj = dbstate.db.get_event_from_handle(handle)
                elif category == CATEGORY_QR_SOURCE :
                    obj = dbstate.db.get_source_from_handle(handle)
                elif category == CATEGORY_QR_PLACE :
                    obj = dbstate.db.get_place_from_handle(handle)
                elif category == CATEGORY_QR_MEDIA :
                    obj = dbstate.db.get_object_from_handle(handle)
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
                print "QuickView Error: failed to run report: no obj"
        else:
            print "QuickView Error: handle is not set"
