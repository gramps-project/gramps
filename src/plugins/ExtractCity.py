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

# $Id: ExtractCity.py 8023 2007-02-01 17:26:51Z rshura $

"Database Processing/Fix capitalization of family names"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import re
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import ManagedWindow

from PluginUtils import Tool, register_tool

CITY_STATE = re.compile("^(.+), \s*(\S\S)(\s+[\d-])?")

#-------------------------------------------------------------------------
#
# ExtractCity
#
#-------------------------------------------------------------------------
class ExtractCity(Tool.BatchTool, ManagedWindow.ManagedWindow):
    """
    Extracts city, state, and zip code information from an place description
    if the title is empty and the description falls into the category of:

       New York, NY 10000

    Sorry for those not in the US or Canada. I doubt this will work for any
    other locales.
    """

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.label = _('Capitalization changes')
        
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(gtk.Window(), gtk.Label(), '')

        Tool.BatchTool.__init__(self, dbstate, options_class, name)
        if self.fail:
            uistate.set_busy_cursor(True)
            self.run()
            uistate.set_busy_cursor(False)

    def run(self):
        """
        Performs the actual extraction of information
        """
        trans = self.db.transaction_begin("", batch=True)
        self.db.disable_signals()
        
        for handle in self.db.get_place_handles():
            place = self.db.get_place_from_handle(handle)
            descr = place.get_title()
            loc = place.get_main_location()
            
            if loc.get_street() == "" and loc.get_city() == "" \
                    and loc.get_state() == "" and \
                    loc.get_postal_code() == "":
                match = CITY_STATE.match(descr)
                if match:
                    (city, state, postal) = match.groups()
                    if city:
                        loc.set_city(city)
                    if state:
                        loc.set_state(state)
                    if postal:
                        loc.set_postal_code(postal)
                    self.db.commit_place(place, trans)
        self.db.transaction_commit(trans, _("Place changes"))
        self.db.enable_signals()
        self.db.request_rebuild()
            
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ExtractCityOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, person_id=None):
        Tool.ToolOptions.__init__(self, name, person_id)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_tool(
    name = 'chname', 
    category = Tool.TOOL_DBPROC, 
    tool_class = ExtractCity, 
    options_class = ExtractCityOptions, 
    modes = Tool.MODE_GUI, 
    translated_name = _("Extract city and state information from a place"), 
    status = _("Stable"), 
    author_name = "Donald N. Allingham", 
    author_email = "don@gramps-project.org", 
    description = _("Attempts to extract city and state/province "
                    "from a place name")
    )
