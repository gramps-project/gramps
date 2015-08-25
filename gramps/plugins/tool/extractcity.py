# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"""Tools/Database Processing/Extract Place Data from a Place Title"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import re
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.display import display_help
from gramps.plugins.lib.libplaceimport import PlaceImport
from gramps.gen.utils.location import get_main_location
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.lib import PlaceType, PlaceName

from gramps.gui.plug import tool
from gramps.gui.utils import ProgressMeter
from gramps.gui.glade import Glade

CITY_STATE_ZIP = re.compile("((\w|\s)+)\s*,\s*((\w|\s)+)\s*(,\s*((\d|-)+))", re.UNICODE)
CITY_STATE = re.compile("((?:\w|\s)+(?:-(?:\w|\s)+)*),((?:\w|\s)+)", re.UNICODE)
CITY_LAEN =  re.compile("((?:\w|\s)+(?:-(?:\w|\s)+)*)\(((?:\w|\s)+)", re.UNICODE)
STATE_ZIP = re.compile("(.+)\s+([\d-]+)", re.UNICODE)

COUNTRY = ( _("United States of America"), _("Canada"), _("France"),_("Sweden"))

STATE_MAP = {
    "AL"            : ("Alabama", 0), 
    "AL."           : ("Alabama", 0), 
    "ALABAMA"       : ("Alabama", 0), 
    "AK"            : ("Alaska" , 0), 
    "AK."           : ("Alaska" , 0), 
    "ALASKA"        : ("Alaska" , 0), 
    "AS"            : ("American Samoa", 0), 
    "AS."           : ("American Samoa", 0), 
    "AMERICAN SAMOA": ("American Samoa", 0), 
    "AZ"            : ("Arizona", 0), 
    "AZ."           : ("Arizona", 0), 
    "ARIZONA"       : ("Arizona", 0), 
    "AR"            : ("Arkansas" , 0), 
    "AR."           : ("Arkansas" , 0), 
    "ARKANSAS"      : ("Arkansas" , 0), 
    "ARK."          : ("Arkansas" , 0), 
    "ARK"           : ("Arkansas" , 0), 
    "CA"            : ("California" , 0), 
    "CA."           : ("California" , 0), 
    "CALIFORNIA"    : ("California" , 0), 
    "CO"            : ("Colorado" , 0), 
    "COLO"          : ("Colorado" , 0), 
    "COLO."         : ("Colorado" , 0), 
    "COLORADO"      : ("Colorado" , 0), 
    "CT"            : ("Connecticut" , 0), 
    "CT."           : ("Connecticut" , 0), 
    "CONNECTICUT"   : ("Connecticut" , 0), 
    "DE"            : ("Delaware" , 0), 
    "DE."           : ("Delaware" , 0), 
    "DELAWARE"      : ("Delaware" , 0), 
    "DC"            : ("District of Columbia" , 0), 
    "D.C."          : ("District of Columbia" , 0), 
    "DC."           : ("District of Columbia" , 0), 
    "DISTRICT OF COLUMBIA" : ("District of Columbia" , 0), 
    "FL"            : ("Florida" , 0), 
    "FL."           : ("Florida" , 0), 
    "FLA"           : ("Florida" , 0), 
    "FLA."          : ("Florida" , 0), 
    "FLORIDA"       : ("Florida" , 0), 
    "GA"            : ("Georgia" , 0), 
    "GA."           : ("Georgia" , 0), 
    "GEORGIA"       : ("Georgia" , 0), 
    "GU"            : ("Guam" , 0), 
    "GU."           : ("Guam" , 0), 
    "GUAM"          : ("Guam" , 0), 
    "HI"            : ("Hawaii" , 0), 
    "HI."           : ("Hawaii" , 0), 
    "HAWAII"        : ("Hawaii" , 0), 
    "ID"            : ("Idaho" , 0), 
    "ID."           : ("Idaho" , 0), 
    "IDAHO"         : ("Idaho" , 0), 
    "IL"            : ("Illinois" , 0), 
    "IL."           : ("Illinois" , 0), 
    "ILLINOIS"      : ("Illinois" , 0), 
    "ILL"           : ("Illinois" , 0), 
    "ILL."          : ("Illinois" , 0), 
    "ILLS"          : ("Illinois" , 0), 
    "ILLS."         : ("Illinois" , 0), 
    "IN"            : ("Indiana" , 0), 
    "IN."           : ("Indiana" , 0), 
    "INDIANA"       : ("Indiana" , 0), 
    "IA"            : ("Iowa" , 0), 
    "IA."           : ("Iowa" , 0), 
    "IOWA"          : ("Iowa" , 0), 
    "KS"            : ("Kansas" , 0), 
    "KS."           : ("Kansas" , 0), 
    "KANSAS"        : ("Kansas" , 0), 
    "KY"            : ("Kentucky" , 0), 
    "KY."           : ("Kentucky" , 0), 
    "KENTUCKY"      : ("Kentucky" , 0), 
    "LA"            : ("Louisiana" , 0), 
    "LA."           : ("Louisiana" , 0), 
    "LOUISIANA"     : ("Louisiana" , 0), 
    "ME"            : ("Maine" , 0), 
    "ME."           : ("Maine" , 0), 
    "MAINE"         : ("Maine" , 0), 
    "MD"            : ("Maryland" , 0), 
    "MD."           : ("Maryland" , 0), 
    "MARYLAND"      : ("Maryland" , 0), 
    "MA"            : ("Massachusetts" , 0), 
    "MA."           : ("Massachusetts" , 0), 
    "MASSACHUSETTS" : ("Massachusetts" , 0), 
    "MI"            : ("Michigan" , 0), 
    "MI."           : ("Michigan" , 0), 
    "MICH."         : ("Michigan" , 0), 
    "MICH"          : ("Michigan" , 0), 
    "MN"            : ("Minnesota" , 0), 
    "MN."           : ("Minnesota" , 0), 
    "MINNESOTA"     : ("Minnesota" , 0), 
    "MS"            : ("Mississippi" , 0), 
    "MS."           : ("Mississippi" , 0), 
    "MISSISSIPPI"   : ("Mississippi" , 0), 
    "MO"            : ("Missouri" , 0), 
    "MO."           : ("Missouri" , 0), 
    "MISSOURI"      : ("Missouri" , 0), 
    "MT"            : ("Montana" , 0), 
    "MT."           : ("Montana" , 0), 
    "MONTANA"       : ("Montana" , 0), 
    "NE"            : ("Nebraska" , 0), 
    "NE."           : ("Nebraska" , 0), 
    "NEBRASKA"      : ("Nebraska" , 0), 
    "NV"            : ("Nevada" , 0), 
    "NV."           : ("Nevada" , 0), 
    "NEVADA"        : ("Nevada" , 0), 
    "NH"            : ("New Hampshire" , 0), 
    "NH."           : ("New Hampshire" , 0), 
    "N.H."          : ("New Hampshire" , 0), 
    "NEW HAMPSHIRE" : ("New Hampshire" , 0), 
    "NJ"            : ("New Jersey" , 0), 
    "NJ."           : ("New Jersey" , 0), 
    "N.J."          : ("New Jersey" , 0), 
    "NEW JERSEY"    : ("New Jersey" , 0), 
    "NM"            : ("New Mexico" , 0), 
    "NM."           : ("New Mexico" , 0), 
    "NEW MEXICO"    : ("New Mexico" , 0), 
    "NY"            : ("New York" , 0), 
    "N.Y."          : ("New York" , 0), 
    "NY."           : ("New York" , 0), 
    "NEW YORK"      : ("New York" , 0), 
    "NC"            : ("North Carolina" , 0), 
    "NC."           : ("North Carolina" , 0), 
    "N.C."          : ("North Carolina" , 0), 
    "NORTH CAROLINA": ("North Carolina" , 0), 
    "ND"            : ("North Dakota" , 0), 
    "ND."           : ("North Dakota" , 0), 
    "N.D."          : ("North Dakota" , 0), 
    "NORTH DAKOTA"  : ("North Dakota" , 0), 
    "OH"            : ("Ohio" , 0), 
    "OH."           : ("Ohio" , 0), 
    "OHIO"          : ("Ohio" , 0), 
    "OK"            : ("Oklahoma" , 0), 
    "OKLA"          : ("Oklahoma" , 0), 
    "OKLA."         : ("Oklahoma" , 0), 
    "OK."           : ("Oklahoma" , 0), 
    "OKLAHOMA"      : ("Oklahoma" , 0), 
    "OR"            : ("Oregon" , 0), 
    "OR."           : ("Oregon" , 0), 
    "OREGON"        : ("Oregon" , 0), 
    "PA"            : ("Pennsylvania" , 0), 
    "PA."           : ("Pennsylvania" , 0), 
    "PENNSYLVANIA"  : ("Pennsylvania" , 0), 
    "PR"            : ("Puerto Rico" , 0), 
    "PUERTO RICO"   : ("Puerto Rico" , 0), 
    "RI"            : ("Rhode Island" , 0), 
    "RI."           : ("Rhode Island" , 0), 
    "R.I."          : ("Rhode Island" , 0), 
    "RHODE ISLAND"  : ("Rhode Island" , 0), 
    "SC"            : ("South Carolina" , 0), 
    "SC."           : ("South Carolina" , 0), 
    "S.C."          : ("South Carolina" , 0), 
    "SOUTH CAROLINA": ("South Carolina" , 0), 
    "SD"            : ("South Dakota" , 0), 
    "SD."           : ("South Dakota" , 0), 
    "S.D."          : ("South Dakota" , 0), 
    "SOUTH DAKOTA"  : ("South Dakota" , 0), 
    "TN"            : ("Tennessee" , 0), 
    "TN."           : ("Tennessee" , 0), 
    "TENNESSEE"     : ("Tennessee" , 0), 
    "TENN."         : ("Tennessee" , 0), 
    "TENN"          : ("Tennessee" , 0), 
    "TX"            : ("Texas" , 0), 
    "TX."           : ("Texas" , 0), 
    "TEXAS"         : ("Texas" , 0), 
    "UT"            : ("Utah" , 0), 
    "UT."           : ("Utah" , 0), 
    "UTAH"          : ("Utah" , 0), 
    "VT"            : ("Vermont" , 0), 
    "VT."           : ("Vermont" , 0), 
    "VERMONT"       : ("Vermont" , 0), 
    "VI"            : ("Virgin Islands" , 0), 
    "VIRGIN ISLANDS": ("Virgin Islands" , 0), 
    "VA"            : ("Virginia" , 0), 
    "VA."           : ("Virginia" , 0), 
    "VIRGINIA"      : ("Virginia" , 0), 
    "WA"            : ("Washington" , 0), 
    "WA."           : ("Washington" , 0), 
    "WASHINGTON"    : ("Washington" , 0), 
    "WV"            : ("West Virginia" , 0), 
    "WV."           : ("West Virginia" , 0), 
    "W.V."          : ("West Virginia" , 0), 
    "WEST VIRGINIA" : ("West Virginia" , 0), 
    "WI"            : ("Wisconsin" , 0), 
    "WI."           : ("Wisconsin" , 0), 
    "WISCONSIN"     : ("Wisconsin" , 0), 
    "WY"            : ("Wyoming" , 0), 
    "WY."           : ("Wyoming" , 0), 
    "WYOMING"       : ("Wyoming" , 0), 
    "AB"            : ("Alberta", 1), 
    "AB."           : ("Alberta", 1), 
    "ALBERTA"       : ("Alberta", 1), 
    "BC"            : ("British Columbia", 1), 
    "BC."           : ("British Columbia", 1), 
    "B.C."          : ("British Columbia", 1), 
    "MB"            : ("Manitoba", 1), 
    "MB."           : ("Manitoba", 1), 
    "MANITOBA"      : ("Manitoba", 1), 
    "NB"            : ("New Brunswick", 1), 
    "N.B."          : ("New Brunswick", 1), 
    "NB."           : ("New Brunswick", 1), 
    "NEW BRUNSWICK" : ("New Brunswick", 1), 
    "NL"            : ("Newfoundland and Labrador", 1), 
    "NL."           : ("Newfoundland and Labrador", 1), 
    "N.L."          : ("Newfoundland and Labrador", 1), 
    "NEWFOUNDLAND"  : ("Newfoundland and Labrador", 1), 
    "NEWFOUNDLAND AND LABRADOR" : ("Newfoundland and Labrador", 1), 
    "LABRADOR"      : ("Newfoundland and Labrador", 1), 
    "NT"            : ("Northwest Territories", 1), 
    "NT."           : ("Northwest Territories", 1), 
    "N.T."          : ("Northwest Territories", 1), 
    "NORTHWEST TERRITORIES" : ("Northwest Territories", 1), 
    "NS"            : ("Nova Scotia", 1), 
    "NS."           : ("Nova Scotia", 1), 
    "N.S."          : ("Nova Scotia", 1), 
    "NOVA SCOTIA"   : ("Nova Scotia", 1), 
    "NU"            : ("Nunavut", 1), 
    "NU."           : ("Nunavut", 1), 
    "NUNAVUT"       : ("Nunavut", 1), 
    "ON"            : ("Ontario", 1), 
    "ON."           : ("Ontario", 1), 
    "ONTARIO"       : ("Ontario", 1), 
    "PE"            : ("Prince Edward Island", 1), 
    "PE."           : ("Prince Edward Island", 1), 
    "PRINCE EDWARD ISLAND" : ("Prince Edward Island", 1), 
    "QC"            : ("Quebec", 1), 
    "QC."           : ("Quebec", 1), 
    "QUEBEC"        : ("Quebec", 1), 
    "SK"            : ("Saskatchewan", 1), 
    "SK."           : ("Saskatchewan", 1), 
    "SASKATCHEWAN"  : ("Saskatchewan", 1), 
    "YT"            : ("Yukon", 1), 
    "YT."           : ("Yukon", 1), 
    "YUKON"         : ("Yukon", 1), 
    "ALSACE"        : ("Alsace", 2),
    "ALS"           : ("ALS-Alsace", 2),
    "AQUITAINE"     : ("Aquitaine", 2),
    "AQU"           : ("AQU-Aquitaine", 2),
    "AUVERGNE"      : ("Auvergne", 2),
    "AUV"           : ("AUV-Auvergne", 2),
    "BOURGOGNE"     : ("Bourgogne", 2),
    "BOU"           : ("BOU-Bourgogne", 2),
    "BRETAGNE"      : ("Bretagne", 2),
    "BRE"           : ("BRE-Bretagne", 2),
    "CENTRE"        : ("Centre - Val de Loire", 2),
    "CEN"           : ("CEN-Centre - Val de Loire", 2),
    "CHAMPAGNE"     : ("Champagne-Ardennes", 2),
    "CHA"           : ("CHA-Champagne-Ardennes", 2),
    "CORSE"         : ("Corse", 2),
    "COR"           : ("COR-Corse", 2),
    "FRANCHE-COMTE" : ("Franche-Comté", 2),
    "FCO"           : ("FCO-Franche-Comté", 2),
    "ILE DE FRANCE" : ("Ile de France", 2),
    "IDF"           : ("IDF-Ile de France", 2),
    "LIMOUSIN"      : ("Limousin", 2),
    "LIM"           : ("LIM-Limousin", 2),
    "LORRAINE"      : ("Lorraine", 2),
    "LOR"           : ("LOR-Lorraine", 2),
    "LANGUEDOC"     : ("Languedoc-Roussillon", 2),
    "LRO"           : ("LRO-Languedoc-Roussillon", 2),
    "MIDI PYRENEE"  : ("Midi-Pyrénée", 2),
    "MPY"           : ("MPY-Midi-Pyrénée", 2),
    "HAUTE NORMANDIE": ("Haute Normandie", 2),
    "NOH"           : ("NOH-Haute Normandie", 2),
    "BASSE NORMANDIE": ("Basse Normandie", 2),
    "NOB"           : ("NOB-Basse Normandie", 2),
    "NORD PAS CALAIS": ("Nord-Pas de Calais", 2),
    "NPC"           : ("NPC-Nord-Pas de Calais", 2),
    "PROVENCE"      : ("Provence-Alpes-Côte d'Azur", 2),
    "PCA"           : ("PCA-Provence-Alpes-Côte d'Azur", 2),
    "POITOU-CHARENTES": ("Poitou-Charentes", 2),
    "PCH"           : ("PCH-Poitou-Charentes", 2),
    "PAYS DE LOIRE" : ("Pays de Loire", 2),
    "PDL"           : ("PDL-Pays de Loire", 2),
    "PICARDIE"      : ("Picardie", 2),
    "PIC"           : ("PIC-Picardie", 2),
    "RHONE-ALPES"   : ("Rhône-Alpes", 2),
    "RAL"           : ("RAL-Rhône-Alpes", 2),
    "AOM"           : ("AOM-Autres Territoires d'Outre-Mer", 2),
    "COM"           : ("COM-Collectivité Territoriale d'Outre-Mer", 2),  
    "DOM"           : ("DOM-Départements d'Outre-Mer", 2), 
    "TOM"           : ("TOM-Territoires d'Outre-Mer", 2),
    "GUA"           : ("GUA-Guadeloupe", 2),
    "GUADELOUPE"    : ("Guadeloupe", 2),
    "MAR"           : ("MAR-Martinique", 2),
    "MARTINIQUE"    : ("Martinique", 2),    
    "GUY"           : ("GUY-Guyane", 2),
    "GUYANE"        : ("Guyane", 2),  
    "REU"           : ("REU-Réunion", 2),
    "REUNION"       : ("Réunion", 2),
    "MIQ"           : ("MIQ-Saint-Pierre et Miquelon", 2),
    "MIQUELON"      : ("Saint-Pierre et Miquelon", 2),
    "MAY"           : ("MAY-Mayotte", 2),
    "MAYOTTE"       : ("Mayotte", 2),
    "(A)"           : ("Stockholms stad", 3),
    "(AB)"          : ("Stockholms stad/län", 3),
    "(B)"           : ("Stockholms län", 3),
    "(C)"           : ("Uppsala län", 3),
    "(D)"           : ("Södermanlands län", 3),
    "(E)"           : ("Östergötlands län", 3),
    "(F)"           : ("Jönköpings län", 3),
    "(G)"           : ("Kronobergs län", 3),
    "(H)"           : ("Kalmar län", 3),
    "(I)"           : ("Gotlands län", 3),
    "(K)"           : ("Blekinge län", 3),
    "(L)"           : ("Kristianstads län", 3),
    "(M)"           : ("Malmöhus län", 3),
    "(N)"           : ("Hallands län", 3),
    "(O)"           : ("Göteborgs- och Bohuslän", 3),
    "(P)"           : ("Älvsborgs län", 3),
    "(R)"           : ("Skaraborg län", 3),
    "(S)"           : ("Värmlands län", 3),
    "(T)"           : ("Örebro län", 3),
    "(U)"           : ("Västmanlands län", 3),
    "(W)"           : ("Kopparbergs län", 3),
    "(X)"           : ("Gävleborgs län", 3),
    "(Y)"           : ("Västernorrlands län", 3),
    "(AC)"          : ("Västerbottens län", 3),
    "(BD)"          : ("Norrbottens län", 3),
}

COLS = [ 
    (_('Place title'), 1), 
    (_('City'), 2), 
    (_('State'), 3), 
    (_('ZIP/Postal Code'), 4), 
    (_('Country'), 5)
    ]

#-------------------------------------------------------------------------
#
# ExtractCity
#
#-------------------------------------------------------------------------
class ExtractCity(tool.BatchTool, ManagedWindow):
    """
    Extracts city, state, and zip code information from an place description
    if the title is empty and the description falls into the category of:

       New York, NY 10000

    Sorry for those not in the US or Canada. I doubt this will work for any
    other locales.
    Works for Sweden if the decriptions is like
        Stockholm (A)
    where the letter A is the abbreviation letter for laen.
    Works for France if the description is like
        Paris, IDF 75000, FRA
    or  Paris, ILE DE FRANCE 75000, FRA
    """

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.label = _('Extract Place data')
        
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(Gtk.Window(), Gtk.Label(), '')

        tool.BatchTool.__init__(self, dbstate, user, options_class, name)

        if not self.fail:
            uistate.set_busy_cursor(True)
            self.run(dbstate.db)
            uistate.set_busy_cursor(False)

    def run(self, db):
        """
        Performs the actual extraction of information
        """

        self.progress = ProgressMeter(_('Checking Place Titles'), '')
        self.progress.set_pass(_('Looking for place fields'), 
                               self.db.get_number_of_places())

        self.name_list = []
        self.place_import = PlaceImport(db)

        for place in db.iter_places():
            descr = place_displayer.display(db, place)
            self.progress.step()

            loc = get_main_location(db, place)
            location = ((loc.get(PlaceType.STREET, '')),
                        (loc.get(PlaceType.LOCALITY, '')),
                        (loc.get(PlaceType.PARISH, '')),
                        (loc.get(PlaceType.CITY, '')),
                        (loc.get(PlaceType.COUNTY, '')),
                        (loc.get(PlaceType.STATE, '')),
                        (loc.get(PlaceType.COUNTRY, '')))
            self.place_import.store_location(location, place.handle)           

            if len(place.get_placeref_list()) == 0:

                match = CITY_STATE_ZIP.match(descr.strip())
                if match:
                    data = match.groups()
                    city = data[0] 
                    state = data[2]
                    postal = data[5]
                    
                    val = " ".join(state.strip().split()).upper()
                    if state:
                        new_state = STATE_MAP.get(val.upper())
                        if new_state:
                            self.name_list.append(
                                (place.handle, (city, new_state[0], postal, 
                                          COUNTRY[new_state[1]])))
                    continue

                # Check if there is a left parant. in the string, might be Swedish laen.
                match = CITY_LAEN.match(descr.strip().replace(","," "))
                if match:
                    data = match.groups()
                    city = data[0] 
                    state = '(' + data[1] + ')'
                    postal = None
                    val = " ".join(state.strip().split()).upper()
                    if state:
                        new_state = STATE_MAP.get(val.upper())
                        if new_state:
                            self.name_list.append(
                                (place.handle, (city, new_state[0], postal, 
                                          COUNTRY[new_state[1]])))
                    continue
                match = CITY_STATE.match(descr.strip())
                if match:
                    data = match.groups()
                    city = data[0] 
                    state = data[1]
                    postal = None
                    if state:
                        m0 = STATE_ZIP.match(state)
                        if m0:
                            (state, postal) = m0.groups() 

                    val = " ".join(state.strip().split()).upper()
                    if state:
                        new_state = STATE_MAP.get(val.upper())
                        if new_state:
                            self.name_list.append(
                                (place.handle, (city, new_state[0], postal, 
                                          COUNTRY[new_state[1]])))
                    continue

                val = " ".join(descr.strip().split()).upper()
                new_state = STATE_MAP.get(val)
                if new_state:
                    self.name_list.append(
                        (place.handle, (None, new_state[0], None, 
                                  COUNTRY[new_state[1]])))
        self.progress.close()

        if self.name_list:
            self.display()
        else:
            self.close()
            from gramps.gui.dialog import OkDialog
            OkDialog(_('No modifications made'), 
                     _("No place information could be extracted."))

    def display(self):

        self.top = Glade("changenames.glade")
        window = self.top.toplevel
        self.top.connect_signals({
            "destroy_passed_object" : self.close, 
            "on_ok_clicked" : self.on_ok_clicked, 
            "on_help_clicked" : self.on_help_clicked, 
            "on_delete_event"   : self.close,
            })
        
        self.list = self.top.get_object("list")
        self.set_window(window, self.top.get_object('title'), self.label)
        lbl = self.top.get_object('info')
        lbl.set_line_wrap(True)
        lbl.set_text(
            _('Below is a list of Places with the possible data that can '
              'be extracted from the place title. Select the places you '
              'wish Gramps to convert.'))

        self.model = Gtk.ListStore(GObject.TYPE_BOOLEAN, GObject.TYPE_STRING, 
                                   GObject.TYPE_STRING, GObject.TYPE_STRING, 
                                   GObject.TYPE_STRING, GObject.TYPE_STRING, 
                                   GObject.TYPE_STRING)

        r = Gtk.CellRendererToggle()
        r.connect('toggled', self.toggled)
        c = Gtk.TreeViewColumn(_('Select'), r, active=0)
        self.list.append_column(c)

        for (title, col) in COLS:
            render = Gtk.CellRendererText()
            if col > 1:
                render.set_property('editable', True)
                render.connect('edited', self.__change_name, col)
            
            self.list.append_column(
                Gtk.TreeViewColumn(title, render, text=col))
        self.list.set_model(self.model)

        self.iter_list = []
        self.progress.set_pass(_('Building display'), len(self.name_list))
        for (id, data) in self.name_list:

            place = self.db.get_place_from_handle(id)
            descr = place_displayer.display(self.db, place)

            handle = self.model.append()
            self.model.set_value(handle, 0, True)
            self.model.set_value(handle, 1, descr)
            if data[0]:
                self.model.set_value(handle, 2, data[0])
            if data[1]:
                self.model.set_value(handle, 3, data[1])
            if data[2]:
                self.model.set_value(handle, 4, data[2])
            if data[3]:
                self.model.set_value(handle, 5, data[3])
            self.model.set_value(handle, 6, id)
            self.iter_list.append(handle)
            self.progress.step()
        self.progress.close()
            
        self.show()

    def __change_name(self, text, path, new_text, col):
        self.model[path][col] = new_text
        return

    def toggled(self, cell, path_string):
        path = tuple(map(int, path_string.split(':')))
        row = self.model[path]
        row[0] = not row[0]

    def build_menu_names(self, obj):
        return (self.label, None)

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        display_help()

    def on_ok_clicked(self, obj):
        with DbTxn(_("Extract Place data"), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            changelist = [node for node in self.iter_list
                          if self.model.get_value(node, 0)]

            for change in changelist:
                row = self.model[change]
                place = self.db.get_place_from_handle(row[6])
                location = ('', '', '', row[2], '', row[3], row[5])
                self.place_import.store_location(location, place.handle)
                if row[2]:
                    place.set_name(PlaceName(value=row[2]))
                place.set_type(PlaceType.CITY)
                if row[4]:
                    place.set_code(row[4])
                self.db.commit_place(place, self.trans)

            self.place_import.generate_hierarchy(self.trans)

        self.db.enable_signals()
        self.db.request_rebuild()
        self.close()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ExtractCityOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
