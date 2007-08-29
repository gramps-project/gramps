#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  B. Malengier
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

# $Id: QuickReports.py 8857 2007-08-23 11:58:36Z bmcage $

"""
This module provides the functions to build the quick report context menu's
"""

__author__ = "B. Malengier"
__revision__ = "$Revision: 8857 $"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
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

from PluginUtils import Plugins
from ReportBase  import CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY,\
                        CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE,\
                        CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY


def create_quickreport_menu(category,dbstate,handle) :
    #import present version of the 
    from PluginUtils import quick_report_list
    ''' This functions querries the registered quick reports with 
            quick_report_list of _PluginMgr.py
        It collects the reports of the requested category, which must be one of
                        CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY,
                        CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE,
                        CATEGORY_QR_PLACE, CATEGORY_QR_REPOSITORY
        It constructs the ui string of the quick report menu, and it's actions
        The action callback function is constructed, using the dbstate and the
            handle as input method.
        A tuple is returned, containing the ui string of the quick report menu,
        and its associated actions
    '''

    actions = []
    ofile = StringIO()
    ofile.write('<menu action="QuickReport">')
    
    actions.append(('QuickReport', None, _("Quick Report"), None, None, None))
        
    menu = gtk.Menu()
    menu.show()
    
    #select the reports to show
    showlst = []
    for item in quick_report_list:
        if not item[8] and item[2] == category :
            #add tuple function, translated name, name, status
            showlst.append((item[0], item[1], item[3], item[5]))
            
    showlst.sort(by_menu_name)
    for report in showlst:
        new_key = report[2].replace(' ', '-')
        ofile.write('<menuitem action="%s"/>' % new_key)
        actions.append((new_key, None, report[1], None, None, 
                make_quick_report_callback(report, category, dbstate, handle)))
    ofile.write('</menu>')
    
    return (ofile.getvalue(), actions)

def by_menu_name(first, second):
    return cmp(first[1], second[1])

def make_quick_report_callback(lst, category, dbstate, handle):
    return lambda x: run_report(dbstate, category, handle, lst[0])
                            
def run_report(dbstate, category,handle,func):
        from TextBufDoc import TextBufDoc
        from Simple import make_basic_stylesheet

        if dbstate.active and handle:
            d = TextBufDoc(make_basic_stylesheet(), None, None)
            if category == CATEGORY_QR_PERSON :
                obj = dbstate.db.get_person_from_handle(handle)
            elif category == CATEGORY_QR_FAMILY :
                obj = dbstate.db.get_family_from_handle(handle)
            elif category == CATEGORY_QR_EVENT :
                obj = dbstate.db.get_event_from_handle(handle)
            elif category == CATEGORY_QR_SOURCE :
                obj = self.dbstate.db.get_source_from_handle(handle)
            elif category == CATEGORY_QR_PLACE :
                obj = dbstate.db.get_place_from_handle(handle)
            elif category == CATEGORY_QR_REPOSITORY :
                obj = dbstate.db.get_repository_from_handle(handle)
            else : 
                obj = None
            if obj :
                d.open("")
                func(dbstate.db, d, obj)
                d.close()

