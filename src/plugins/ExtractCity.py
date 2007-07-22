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

CITY_STATE = re.compile("^(.+),\s*([\w\s\.]+),?(\s+[\d-])?")

COUNTRY = ( "United States of America", "Canada")

STATE_MAP = {
    "AL"             : ("Alabama", 0), 
    "AL."            : ("Alabama", 0), 
    "ALABAMA"        : ("Alabama", 0), 
    "AK"             : ("Alaska" , 0), 
    "AK."            : ("Alaska" , 0), 
    "ALASKA"         : ("Alaska" , 0), 
    "AS"             : ("American Samoa", 0), 
    "AS."            : ("American Samoa", 0), 
    "AMERICAN SAMOA" : ("American Samoa", 0), 
    "AZ"             : ("Arizona", 0), 
    "AZ."            : ("Arizona", 0), 
    "ARIZONA"        : ("Arizona", 0), 
    "AR"             : ("Arkansas" , 0), 
    "AR."            : ("Arkansas" , 0),
    "ARKANSAS"       : ("Arkansas" , 0),
    "ARK."           : ("Arkansas" , 0),
    "ARK"            : ("Arkansas" , 0),
    "CA"             : ("California" , 0),
    "CA."            : ("California" , 0),
    "CALIFORNIA"     : ("California" , 0),
    "CO"             : ("Colorado" , 0),
    "COLO"           : ("Colorado" , 0),
    "COLO."          : ("Colorado" , 0),
    "COLORADO"       : ("Colorado" , 0),
    "CT"             : ("Connecticut" , 0),
    "CT."            : ("Connecticut" , 0),
    "CONNECTICUT"    : ("Connecticut" , 0),
    "DE"             : ("Delaware" , 0),
    "DE."            : ("Delaware" , 0),
    "DELAWARE"       : ("Delaware" , 0),
    "DC"             : ("District of Columbia" , 0),
    "D.C."           : ("District of Columbia" , 0),
    "DC."            : ("District of Columbia" , 0),
    "DISTRICT OF COLUMBIA" : ("District of Columbia" , 0),
    "FL"             : ("Florida" , 0),
    "FL."            : ("Florida" , 0),
    "FLA"            : ("Florida" , 0),
    "FLA."           : ("Florida" , 0),
    "FLORIDA"        : ("Florida" , 0),
    "GA"             : ("Georgia" , 0),
    "GA."            : ("Georgia" , 0),
    "GEORGIA"        : ("Georgia" , 0),
    "GU"             : ("Guam" , 0),
    "GU."            : ("Guam" , 0),
    "GUAM"           : ("Guam" , 0),
    "HI"             : ("Hawaii" , 0),
    "HI."            : ("Hawaii" , 0),
    "HAWAII"         : ("Hawaii" , 0),
    "ID"             : ("Idaho" , 0),
    "ID."            : ("Idaho" , 0),
    "IDAHO"          : ("Idaho" , 0),
    "IL"             : ("Illinois" , 0),
    "IL."            : ("Illinois" , 0),
    "ILLINOIS"       : ("Illinois" , 0),
    "ILL"            : ("Illinois" , 0),
    "ILL."           : ("Illinois" , 0),
    "ILLS"           : ("Illinois" , 0),
    "ILLS."          : ("Illinois" , 0),
    "IN"             : ("Indiana" , 0),
    "IN."            : ("Indiana" , 0),
    "INDIANA"        : ("Indiana" , 0),
    "IA"             : ("Iowa" , 0),
    "IA."            : ("Iowa" , 0),
    "IOWA"           : ("Iowa" , 0),
    "KS"             : ("Kansas" , 0),
    "KS."            : ("Kansas" , 0),
    "KANSAS"         : ("Kansas" , 0),
    "KY"             : ("Kentucky" , 0),
    "KY."            : ("Kentucky" , 0),
    "KENTUCKY"       : ("Kentucky" , 0),
    "LA"             : ("Louisiana" , 0),
    "LA."            : ("Louisiana" , 0),
    "LOUISIANA"      : ("Louisiana" , 0),
    "ME"             : ("Maine" , 0),
    "ME."            : ("Maine" , 0),
    "MAINE"          : ("Maine" , 0),
    "MD"             : ("Maryland" , 0),
    "MD."            : ("Maryland" , 0),
    "MARYLAND"       : ("Maryland" , 0),
    "MA"             : ("Massachusetts" , 0),
    "MA."            : ("Massachusetts" , 0),
    "MASSACHUSETTS"  : ("Massachusetts" , 0),
    "MI"             : ("Michigan" , 0),
    "MI."            : ("Michigan" , 0),
    "MICH."          : ("Michigan" , 0),
    "MICH"           : ("Michigan" , 0),
    "MN"             : ("Minnesota" , 0),
    "MN."            : ("Minnesota" , 0),
    "MINNESOTA"      : ("Minnesota" , 0),
    "MS"             : ("Mississippi" , 0),
    "MS."            : ("Mississippi" , 0),
    "MISSISSIPPI"    : ("Mississippi" , 0),
    "MO"             : ("Missouri" , 0),
    "MO."            : ("Missouri" , 0),
    "MISSOURI"       : ("Missouri" , 0),
    "MT"             : ("Montana" , 0),
    "MT."            : ("Montana" , 0),
    "MONTANA"        : ("Montana" , 0),
    "NE"             : ("Nebraska" , 0),
    "NE."            : ("Nebraska" , 0),
    "NEBRASKA"       : ("Nebraska" , 0),
    "NV"             : ("Nevada" , 0),
    "NV."            : ("Nevada" , 0),
    "NEVADA"         : ("Nevada" , 0),
    "NH"             : ("New Hampshire" , 0),
    "NH."            : ("New Hampshire" , 0),
    "N.H."           : ("New Hampshire" , 0),
    "NEW HAMPSHIRE"  : ("New Hampshire" , 0),
    "NJ"             : ("New Jersey" , 0),
    "NJ."            : ("New Jersey" , 0),
    "N.J."           : ("New Jersey" , 0),
    "NEW JERSEY"     : ("New Jersey" , 0),
    "NM"             : ("New Mexico" , 0),
    "NM."            : ("New Mexico" , 0),
    "NEW MEXICO"     : ("New Mexico" , 0),
    "NY"             : ("New York" , 0),
    "N.Y."           : ("New York" , 0),
    "NY."            : ("New York" , 0),
    "NEW YORK"       : ("New York" , 0),
    "NC"             : ("North Carolina" , 0),
    "NC."            : ("North Carolina" , 0),
    "N.C."           : ("North Carolina" , 0),
    "NORTH CAROLINA" : ("North Carolina" , 0),
    "ND"             : ("North Dakota" , 0),
    "ND."            : ("North Dakota" , 0),
    "N.D."           : ("North Dakota" , 0),
    "NORTH DAKOTA"   : ("North Dakota" , 0),
    "OH"             : ("Ohio" , 0),
    "OH."            : ("Ohio" , 0),
    "OHIO"           : ("Ohio" , 0),
    "OK"             : ("Oklahoma" , 0),
    "OKLA"           : ("Oklahoma" , 0),
    "OKLA."          : ("Oklahoma" , 0),
    "OK."            : ("Oklahoma" , 0),
    "OKLAHOMA"       : ("Oklahoma" , 0),
    "OR"             : ("Oregon" , 0),
    "OR."            : ("Oregon" , 0),
    "OREGON"         : ("Oregon" , 0),
    "PA"             : ("Pennsylvania" , 0),
    "PA."            : ("Pennsylvania" , 0),
    "PENNSYLVANIA"   : ("Pennsylvania" , 0),
    "PR"             : ("Puerto Rico" , 0),
    "PUERTO RICO"    : ("Puerto Rico" , 0),
    "RI"             : ("Rhode Island" , 0),
    "RI."            : ("Rhode Island" , 0),
    "R.I."           : ("Rhode Island" , 0),
    "RHODE ISLAND"   : ("Rhode Island" , 0),
    "SC"             : ("South Carolina" , 0),
    "SC."            : ("South Carolina" , 0),
    "S.C."           : ("South Carolina" , 0),
    "SOUTH CAROLINA" : ("South Carolina" , 0),
    "SD"             : ("South Dakota" , 0),
    "SD."            : ("South Dakota" , 0),
    "S.D."           : ("South Dakota" , 0),
    "SOUTH DAKOTA"   : ("South Dakota" , 0),
    "TN"             : ("Tennessee" , 0),
    "TN."            : ("Tennessee" , 0),
    "TENNESSEE"      : ("Tennessee" , 0),
    "TENN."          : ("Tennessee" , 0),
    "TENN"           : ("Tennessee" , 0),
    "TX"             : ("Texas" , 0),
    "TX."            : ("Texas" , 0),
    "TEXAS"          : ("Texas" , 0),
    "UT"             : ("Utah" , 0),
    "UT."            : ("Utah" , 0),
    "UTAH"           : ("Utah" , 0),
    "VT"             : ("Vermont" , 0),
    "VT."            : ("Vermont" , 0),
    "VERMONT"        : ("Vermont" , 0),
    "VI"             : ("Virgin Islands" , 0),
    "VIRGIN ISLANDS" : ("Virgin Islands" , 0),
    "VA"             : ("Virginia" , 0),
    "VA."            : ("Virginia" , 0),
    "VIRGINIA"       : ("Virginia" , 0),
    "WA"             : ("Washington" , 0),
    "WA."            : ("Washington" , 0),
    "WASHINGTON"     : ("Washington" , 0),
    "WV"             : ("West Virginia" , 0),
    "WV."            : ("West Virginia" , 0),
    "W.V."           : ("West Virginia" , 0),
    "WEST VIRGINIA"  : ("West Virginia" , 0),
    "WI"             : ("Wisconsin" , 0),
    "WI."            : ("Wisconsin" , 0),
    "WISCONSIN"      : ("Wisconsin" , 0),
    "WY"             : ("Wyoming" , 0),
    "WY."            : ("Wyoming" , 0),
    "WYOMING"        : ("Wyoming" , 0),
    "AB"             : ("Alberta", 1),
    "AB."            : ("Alberta", 1),
    "ALBERTA"        : ("Alberta", 1),
    "BC"             : ("British Columbia", 1),
    "BC."            : ("British Columbia", 1),
    "B.C."           : ("British Columbia", 1),
    "MB"             : ("Manitoba", 1),
    "MB."            : ("Manitoba", 1),
    "MANITOBA"       : ("Manitoba", 1),
    "NB"             : ("New Brunswick", 1),
    "N.B."           : ("New Brunswick", 1),
    "NB."            : ("New Brunswick", 1),
    "NEW BRUNSWICK"  : ("New Brunswick", 1),
    "NL"             : ("Newfoundland and Labrador", 1),
    "NL."            : ("Newfoundland and Labrador", 1),
    "N.L."           : ("Newfoundland and Labrador", 1),
    "NEWFOUNDLAND"   : ("Newfoundland and Labrador", 1),
    "NEWFOUNDLAND AND LABRADOR" : ("Newfoundland and Labrador", 1),
    "LABRADOR"       : ("Newfoundland and Labrador", 1),
    "NT"             : ("Northwest Territories", 1),
    "NT."            : ("Northwest Territories", 1),
    "N.T."           : ("Northwest Territories", 1),
    "NORTHWEST TERRITORIES" : ("Northwest Territories", 1),
    "NS"             : ("Nova Scotia", 1),
    "NS."            : ("Nova Scotia", 1),
    "N.S."           : ("Nova Scotia", 1),
    "NOVA SCOTIA"    : ("Nova Scotia", 1),
    "NU"             : ("Nunavut", 1),
    "NU."            : ("Nunavut", 1),
    "NUNAVUT"        : ("Nunavut", 1),
    "ON"             : ("Ontario", 1),
    "ON."            : ("Ontario", 1),
    "ONTARIO"        : ("Ontario", 1),
    "PE"             : ("Prince Edward Island", 1),
    "PE."            : ("Prince Edward Island", 1),
    "PRINCE EDWARD ISLAND" : ("Prince Edward Island", 1),
    "QC"             : ("Quebec", 1),
    "QC."            : ("Quebec", 1),
    "QUEBEC"         : ("Quebec", 1),
    "SK"             : ("Saskatchewan", 1),
    "SK."            : ("Saskatchewan", 1),
    "SASKATCHEWAN"   : ("Saskatchewan", 1),
    "YT"             : ("Yukon", 1),
    "YT."            : ("Yukon", 1),
    "YUKON"          : ("Yukon", 1),
}

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
        
#        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)
#        self.set_window(gtk.Window(), gtk.Label(), '')

        Tool.BatchTool.__init__(self, dbstate, options_class, name)
        if not self.fail:
            uistate.set_busy_cursor(True)
            self.run(dbstate.db)
            uistate.set_busy_cursor(False)

    def run(self, db):
        """
        Performs the actual extraction of information
        """
        trans = db.transaction_begin("", batch=True)
        db.disable_signals()
        
        for handle in db.get_place_handles():
            place = db.get_place_from_handle(handle)
            descr = place.get_title()
            loc = place.get_main_location()
            
            if loc.get_street() == "" and loc.get_city() == "" \
                    and loc.get_state() == "" and \
                    loc.get_postal_code() == "":
                match = CITY_STATE.match(descr.strip())
                if match:
                    (city, state, postal) = match.groups()
                    if state:
                        new_state = STATE_MAP.get(state.upper())
                        if new_state:
                            loc.set_state(new_state[0])
                            loc.set_country(COUNTRY[new_state[1]])
                            if city:
                                loc.set_city(" ".join(city.split()))
                            if postal:
                                loc.set_postal_code(postal)
                    db.commit_place(place, trans)
                else:
                    val = " ".join(descr.strip().split()).upper()
                    new_state = STATE_MAP.get(val)
                    if new_state:
                        loc.set_state(new_state[0])
                        loc.set_country(COUNTRY[new_state[1]])
                    db.commit_place(place, trans)

        db.transaction_commit(trans, _("Place changes"))
        db.enable_signals()
        db.request_rebuild()
            
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
    name = 'excity', 
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
