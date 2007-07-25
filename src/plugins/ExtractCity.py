# -*- coding: utf-8 -*-
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
import os
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
import GrampsDisplay

from PluginUtils import Tool, register_tool
import Utils

CITY_STATE_ZIP = re.compile("((\w|\s)+)\s*,\s*((\w|\s)+)\s*(,\s*((\d|-)+))")
CITY_STATE = re.compile("((\w|\s)+)\s*,\s*((\w|\s)+)")
STATE_ZIP = re.compile("(.+)\s+([\d-]+)")

COUNTRY = ( _(u"United States of America"), _(u"Canada"), _(u"France"))

STATE_MAP = {
    u"AL"            : (u"Alabama", 0), 
    u"AL."           : (u"Alabama", 0), 
    u"ALABAMA"       : (u"Alabama", 0), 
    u"AK"            : (u"Alaska" , 0), 
    u"AK."           : (u"Alaska" , 0), 
    u"ALASKA"        : (u"Alaska" , 0), 
    u"AS"            : (u"American Samoa", 0), 
    u"AS."           : (u"American Samoa", 0), 
    u"AMERICAN SAMOA": (u"American Samoa", 0), 
    u"AZ"            : (u"Arizona", 0), 
    u"AZ."           : (u"Arizona", 0), 
    u"ARIZONA"       : (u"Arizona", 0), 
    u"AR"            : (u"Arkansas" , 0), 
    u"AR."           : (u"Arkansas" , 0), 
    u"ARKANSAS"      : (u"Arkansas" , 0), 
    u"ARK."          : (u"Arkansas" , 0), 
    u"ARK"           : (u"Arkansas" , 0), 
    u"CA"            : (u"California" , 0), 
    u"CA."           : (u"California" , 0), 
    u"CALIFORNIA"    : (u"California" , 0), 
    u"CO"            : (u"Colorado" , 0), 
    u"COLO"          : (u"Colorado" , 0), 
    u"COLO."         : (u"Colorado" , 0), 
    u"COLORADO"      : (u"Colorado" , 0), 
    u"CT"            : (u"Connecticut" , 0), 
    u"CT."           : (u"Connecticut" , 0), 
    u"CONNECTICUT"   : (u"Connecticut" , 0), 
    u"DE"            : (u"Delaware" , 0), 
    u"DE."           : (u"Delaware" , 0), 
    u"DELAWARE"      : (u"Delaware" , 0), 
    u"DC"            : (u"District of Columbia" , 0), 
    u"D.C."          : (u"District of Columbia" , 0), 
    u"DC."           : (u"District of Columbia" , 0), 
    u"DISTRICT OF COLMBIA" : (u"District of Columbia" , 0), 
    u"FL"            : (u"Florida" , 0), 
    u"FL."           : (u"Florida" , 0), 
    u"FLA"           : (u"Florida" , 0), 
    u"FLA."          : (u"Florida" , 0), 
    u"FLORIDA"       : (u"Florida" , 0), 
    u"GA"            : (u"Georgia" , 0), 
    u"GA."           : (u"Georgia" , 0), 
    u"GEORGIA"       : (u"Georgia" , 0), 
    u"GU"            : (u"Guam" , 0), 
    u"GU."           : (u"Guam" , 0), 
    u"GUAM"          : (u"Guam" , 0), 
    u"HI"            : (u"Hawaii" , 0), 
    u"HI."           : (u"Hawaii" , 0), 
    u"HAWAII"        : (u"Hawaii" , 0), 
    u"ID"            : (u"Idaho" , 0), 
    u"ID."           : (u"Idaho" , 0), 
    u"IDAHO"         : (u"Idaho" , 0), 
    u"IL"            : (u"Illinois" , 0), 
    u"IL."           : (u"Illinois" , 0), 
    u"ILLINOIS"      : (u"Illinois" , 0), 
    u"ILL"           : (u"Illinois" , 0), 
    u"ILL."          : (u"Illinois" , 0), 
    u"ILLS"          : (u"Illinois" , 0), 
    u"ILLS."         : (u"Illinois" , 0), 
    u"IN"            : (u"Indiana" , 0), 
    u"IN."           : (u"Indiana" , 0), 
    u"INDIANA"       : (u"Indiana" , 0), 
    u"IA"            : (u"Iowa" , 0), 
    u"IA."           : (u"Iowa" , 0), 
    u"IOWA"          : (u"Iowa" , 0), 
    u"KS"            : (u"Kansas" , 0), 
    u"KS."           : (u"Kansas" , 0), 
    u"KANSAS"        : (u"Kansas" , 0), 
    u"KY"            : (u"Kentucky" , 0), 
    u"KY."           : (u"Kentucky" , 0), 
    u"KENTUCKY"      : (u"Kentucky" , 0), 
    u"LA"            : (u"Louisiana" , 0), 
    u"LA."           : (u"Louisiana" , 0), 
    u"LOUISIANA"     : (u"Louisiana" , 0), 
    u"ME"            : (u"Maine" , 0), 
    u"ME."           : (u"Maine" , 0), 
    u"MAINE"         : (u"Maine" , 0), 
    u"MD"            : (u"Maryland" , 0), 
    u"MD."           : (u"Maryland" , 0), 
    u"MARYLAND"      : (u"Maryland" , 0), 
    u"MA"            : (u"Massachusetts" , 0), 
    u"MA."           : (u"Massachusetts" , 0), 
    u"MASSACHUSETTS" : (u"Massachusetts" , 0), 
    u"MI"            : (u"Michigan" , 0), 
    u"MI."           : (u"Michigan" , 0), 
    u"MICH."         : (u"Michigan" , 0), 
    u"MICH"          : (u"Michigan" , 0), 
    u"MN"            : (u"Minnesota" , 0), 
    u"MN."           : (u"Minnesota" , 0), 
    u"MINNESOTA"     : (u"Minnesota" , 0), 
    u"MS"            : (u"Mississippi" , 0), 
    u"MS."           : (u"Mississippi" , 0), 
    u"MISSISSIPPI"   : (u"Mississippi" , 0), 
    u"MO"            : (u"Missouri" , 0), 
    u"MO."           : (u"Missouri" , 0), 
    u"MISSOURI"      : (u"Missouri" , 0), 
    u"MT"            : (u"Montana" , 0), 
    u"MT."           : (u"Montana" , 0), 
    u"MONTANA"       : (u"Montana" , 0), 
    u"NE"            : (u"Nebraska" , 0), 
    u"NE."           : (u"Nebraska" , 0), 
    u"NEBRASKA"      : (u"Nebraska" , 0), 
    u"NV"            : (u"Nevada" , 0), 
    u"NV."           : (u"Nevada" , 0), 
    u"NEVADA"        : (u"Nevada" , 0), 
    u"NH"            : (u"New Hampshire" , 0), 
    u"NH."           : (u"New Hampshire" , 0), 
    u"N.H."          : (u"New Hampshire" , 0), 
    u"NEW HAMPSHIRE" : (u"New Hampshire" , 0), 
    u"NJ"            : (u"New Jersey" , 0), 
    u"NJ."           : (u"New Jersey" , 0), 
    u"N.J."          : (u"New Jersey" , 0), 
    u"NEW JERSEY"    : (u"New Jersey" , 0), 
    u"NM"            : (u"New Mexico" , 0), 
    u"NM."           : (u"New Mexico" , 0), 
    u"NEW MEXICO"    : (u"New Mexico" , 0), 
    u"NY"            : (u"New York" , 0), 
    u"N.Y."          : (u"New York" , 0), 
    u"NY."           : (u"New York" , 0), 
    u"NEW YORK"      : (u"New York" , 0), 
    u"NC"            : (u"North Carolina" , 0), 
    u"NC."           : (u"North Carolina" , 0), 
    u"N.C."          : (u"North Carolina" , 0), 
    u"NORTH CAROLINA": (u"North Carolina" , 0), 
    u"ND"            : (u"North Dakota" , 0), 
    u"ND."           : (u"North Dakota" , 0), 
    u"N.D."          : (u"North Dakota" , 0), 
    u"NORTH DAKOTA"  : (u"North Dakota" , 0), 
    u"OH"            : (u"Ohio" , 0), 
    u"OH."           : (u"Ohio" , 0), 
    u"OHIO"          : (u"Ohio" , 0), 
    u"OK"            : (u"Oklahoma" , 0), 
    u"OKLA"          : (u"Oklahoma" , 0), 
    u"OKLA."         : (u"Oklahoma" , 0), 
    u"OK."           : (u"Oklahoma" , 0), 
    u"OKLAHOMA"      : (u"Oklahoma" , 0), 
    u"OR"            : (u"Oregon" , 0), 
    u"OR."           : (u"Oregon" , 0), 
    u"OREGON"        : (u"Oregon" , 0), 
    u"PA"            : (u"Pennsylvania" , 0), 
    u"PA."           : (u"Pennsylvania" , 0), 
    u"PENNSYLVANIA"  : (u"Pennsylvania" , 0), 
    u"PR"            : (u"Puerto Rico" , 0), 
    u"PUERTO RICO"   : (u"Puerto Rico" , 0), 
    u"RI"            : (u"Rhode Island" , 0), 
    u"RI."           : (u"Rhode Island" , 0), 
    u"R.I."          : (u"Rhode Island" , 0), 
    u"RHODE ISLAND"  : (u"Rhode Island" , 0), 
    u"SC"            : (u"South Carolina" , 0), 
    u"SC."           : (u"South Carolina" , 0), 
    u"S.C."          : (u"South Carolina" , 0), 
    u"SOUTH CAROLINA": (u"South Carolina" , 0), 
    u"SD"            : (u"South Dakota" , 0), 
    u"SD."           : (u"South Dakota" , 0), 
    u"S.D."          : (u"South Dakota" , 0), 
    u"SOUTH DAKOTA"  : (u"South Dakota" , 0), 
    u"TN"            : (u"Tennessee" , 0), 
    u"TN."           : (u"Tennessee" , 0), 
    u"TENNESSEE"     : (u"Tennessee" , 0), 
    u"TENN."         : (u"Tennessee" , 0), 
    u"TENN"          : (u"Tennessee" , 0), 
    u"TX"            : (u"Texas" , 0), 
    u"TX."           : (u"Texas" , 0), 
    u"TEXAS"         : (u"Texas" , 0), 
    u"UT"            : (u"Utah" , 0), 
    u"UT."           : (u"Utah" , 0), 
    u"UTAH"          : (u"Utah" , 0), 
    u"VT"            : (u"Vermont" , 0), 
    u"VT."           : (u"Vermont" , 0), 
    u"VERMONT"       : (u"Vermont" , 0), 
    u"VI"            : (u"Virgin Islands" , 0), 
    u"VIRGIN ISLANDS": (u"Virgin Islands" , 0), 
    u"VA"            : (u"Virginia" , 0), 
    u"VA."           : (u"Virginia" , 0), 
    u"VIRGINIA"      : (u"Virginia" , 0), 
    u"WA"            : (u"Washington" , 0), 
    u"WA."           : (u"Washington" , 0), 
    u"WASHINGTON"    : (u"Washington" , 0), 
    u"WV"            : (u"West Virginia" , 0), 
    u"WV."           : (u"West Virginia" , 0), 
    u"W.V."          : (u"West Virginia" , 0), 
    u"WEST VIRGINIA" : (u"West Virginia" , 0), 
    u"WI"            : (u"Wisconsin" , 0), 
    u"WI."           : (u"Wisconsin" , 0), 
    u"WISCONSIN"     : (u"Wisconsin" , 0), 
    u"WY"            : (u"Wyoming" , 0), 
    u"WY."           : (u"Wyoming" , 0), 
    u"WYOMING"       : (u"Wyoming" , 0), 
    u"AB"            : (u"Alberta", 1), 
    u"AB."           : (u"Alberta", 1), 
    u"ALBERTA"       : (u"Alberta", 1), 
    u"BC"            : (u"British Columbia", 1), 
    u"BC."           : (u"British Columbia", 1), 
    u"B.C."          : (u"British Columbia", 1), 
    u"MB"            : (u"Manitoba", 1), 
    u"MB."           : (u"Manitoba", 1), 
    u"MANITOBA"      : (u"Manitoba", 1), 
    u"NB"            : (u"New Brunswick", 1), 
    u"N.B."          : (u"New Brunswick", 1), 
    u"NB."           : (u"New Brunswick", 1), 
    u"NEW BRUNSWICK" : (u"New Brunswick", 1), 
    u"NL"            : (u"Newfoundland and Labrador", 1), 
    u"NL."           : (u"Newfoundland and Labrador", 1), 
    u"N.L."          : (u"Newfoundland and Labrador", 1), 
    u"NEWFOUNDLAND"  : (u"Newfoundland and Labrador", 1), 
    u"NEWFOUNDLAND AND LABRADOR" : (u"Newfoundland and Labrador", 1), 
    u"LABRADOR"      : (u"Newfoundland and Labrador", 1), 
    u"NT"            : (u"Northwest Territories", 1), 
    u"NT."           : (u"Northwest Territories", 1), 
    u"N.T."          : (u"Northwest Territories", 1), 
    u"NORTHWEST TERRITORIES" : (u"Northwest Territories", 1), 
    u"NS"            : (u"Nova Scotia", 1), 
    u"NS."           : (u"Nova Scotia", 1), 
    u"N.S."          : (u"Nova Scotia", 1), 
    u"NOVA SCOTIA"   : (u"Nova Scotia", 1), 
    u"NU"            : (u"Nunavut", 1), 
    u"NU."           : (u"Nunavut", 1), 
    u"NUNAVUT"       : (u"Nunavut", 1), 
    u"ON"            : (u"Ontario", 1), 
    u"ON."           : (u"Ontario", 1), 
    u"ONTARIO"       : (u"Ontario", 1), 
    u"PE"            : (u"Prince Edward Island", 1), 
    u"PE."           : (u"Prince Edward Island", 1), 
    u"PRINCE EDWARD ISLAND" : (u"Prince Edward Island", 1), 
    u"QC"            : (u"Quebec", 1), 
    u"QC."           : (u"Quebec", 1), 
    u"QUEBEC"        : (u"Quebec", 1), 
    u"SK"            : (u"Saskatchewan", 1), 
    u"SK."           : (u"Saskatchewan", 1), 
    u"SASKATCHEWAN"  : (u"Saskatchewan", 1), 
    u"YT"            : (u"Yukon", 1), 
    u"YT."           : (u"Yukon", 1), 
    u"YUKON"         : (u"Yukon", 1), 
    u"ALSACE"        : (u"Alsace", 2),
    u"ALS"           : (u"ALS-Alsace", 2),
    u"AQUITAINE"     : (u"Aquitaine", 2),
    u"AQU"           : (u"AQU-Aquitaine", 2),
    u"AUVERGNE"      : (u"Auvergne", 2),
    u"AUV"           : (u"AUV-Auvergne", 2),
    u"BOURGOGNE"     : (u"Bourgogne", 2),
    u"BOU"           : (u"BOU-Bourgogne", 2),
    u"BRETAGNE"      : (u"Bretagne", 2),
    u"BRE"           : (u"BRE-Bretagne", 2),
    u"CENTRE"        : (u"Centre - Val de Loire", 2),
    u"CEN"           : (u"CEN-Centre - Val de Loire", 2),
    u"CHAMPAGNE"     : (u"Champagne-Ardennes", 2),
    u"CHA"           : (u"CHA-Champagne-Ardennes", 2),
    u"CORSE"         : (u"Corse", 2),
    u"COR"           : (u"COR-Corse", 2),
    u"FRANCHE-COMTE" : (u"Franche-Comté", 2),
    u"FCO"           : (u"FCO-Franche-Comté", 2),
    u"ILE DE FRANCE" : (u"Ile de France", 2),
    u"IDF"           : (u"IDF-Ile de France", 2),
    u"LIMOUSIN"      : (u"Limousin", 2),
    u"LIM"           : (u"LIM-Limousin", 2),
    u"LORRAINE"      : (u"Lorraine", 2),
    u"LOR"           : (u"LOR-Lorraine", 2),
    u"LANGUEDOC"     : (u"Languedoc-Roussillon", 2),
    u"LRO"           : (u"LRO-Languedoc-Roussillon", 2),
    u"MIDI PYRENEE"  : (u"Midi-Pyrénée", 2),
    u"MPY"           : (u"MPY-Midi-Pyrénée", 2),
    u"HAUTE NORMANDIE": (u"Haute Normandie", 2),
    u"NOH"           : (u"NOH-Haute Normandie", 2),
    u"BASSE NORMANDIE": (u"Basse Normandie", 2),
    u"NOB"           : (u"NOB-Basse Normandie", 2),
    u"NORD PAS CALAIS": (u"Nord-Pas de Calais", 2),
    u"NPC"           : (u"NPC-Nord-Pas de Calais", 2),
    u"PROVENCE"      : (u"Provence-Alpes-Côte d'Azur", 2),
    u"PCA"           : (u"PCA-Provence-Alpes-Côte d'Azur", 2),
    u"POITOU-CHARENTES": (u"Poitou-Charentes", 2),
    u"PCH"           : (u"PCH-Poitou-Charentes", 2),
    u"PAYS DE LOIRE" : (u"Pays de Loire", 2),
    u"PDL"           : (u"PDL-Pays de Loire", 2),
    u"PICARDIE"      : (u"Picardie", 2),
    u"PIC"           : (u"PIC-Picardie", 2),
    u"RHONE-ALPES"   : (u"Rhône-Alpes", 2),
    u"RAL"           : (u"RAL-Rhône-Alpes", 2),
    u"AOM"           : (u"AOM-Autres Territoires d'Outre-Mer", 2),
    u"COM"           : (u"COM-Collectivité Territoriale d'Outre-Mer", 2),  
    u"DOM"           : (u"DOM-Départements d'Outre-Mer", 2), 
    u"TOM"           : (u"TOM-Territoires d'Outre-Mer", 2),
}

COLS = [ 
    (_('Place title'), 1), 
    (_('City'), 2), 
    (_('State'), 3), 
    (_('Postal code'), 4), 
    (_('Country'), 5)
    ]

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
        self.label = _('Extract Place data')
        
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(gtk.Window(), gtk.Label(), '')

        Tool.BatchTool.__init__(self, dbstate, options_class, name)

        if not self.fail:
            uistate.set_busy_cursor(True)
            self.run(dbstate.db)
            uistate.set_busy_cursor(False)

    def run(self, db):
        """
        Performs the actual extraction of information
        """

        self.progress = Utils.ProgressMeter(_('Checking place titles'), '')
        self.progress.set_pass(_('Looking for place fields'), 
                               len(self.db.get_place_handles()))

        self.name_list = []

        for handle in db.get_place_handles():
            place = db.get_place_from_handle(handle)
            descr = place.get_title()
            loc = place.get_main_location()

            self.progress.step()

            if loc.get_street() == "" and loc.get_city() == "" \
                    and loc.get_state() == "" and \
                    loc.get_postal_code() == "":

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
                                (handle, (city, new_state[0], postal, 
                                          COUNTRY[new_state[1]])))
                    continue

                match = CITY_STATE.match(descr.strip())
                if match:
                    data = match.groups()
                    city = data[0] 
                    state = data[2]
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
                                (handle, (city, new_state[0], postal, 
                                          COUNTRY[new_state[1]])))
                    continue

                val = " ".join(descr.strip().split()).upper()
                new_state = STATE_MAP.get(val)
                if new_state:
                    self.name_list.append(
                        (handle, (None, new_state[0], None, 
                                  COUNTRY[new_state[1]])))
        self.progress.close()

        if self.name_list:
            self.display()
        else:
            self.close()
            from QuestionDialog import OkDialog
            OkDialog(_('No modifications made'), 
                     _("No place information could be extracted."))

    def display(self):

        base = os.path.dirname(__file__)
        glade_file = os.path.join(base, "changenames.glade")
        
        self.top = gtk.glade.XML(glade_file, "top", "gramps")
        window = self.top.get_widget('top')
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close, 
            "on_ok_clicked" : self.on_ok_clicked, 
            "on_help_clicked" : self.on_help_clicked, 
            })
        
        self.list = self.top.get_widget("list")
        self.set_window(window, self.top.get_widget('title'), self.label)
        lbl = self.top.get_widget('info')
        lbl.set_line_wrap(True)
        lbl.set_text(
            _('Below is a list of Places with the possible data that can '
              'be extracted from the place title. Select the places you '
              'wish GRAMPS to convert.'))

        self.model = gtk.ListStore(bool, str, str, str, str, str, str)

        r = gtk.CellRendererToggle()
        r.connect('toggled', self.toggled)
        c = gtk.TreeViewColumn(_('Select'), r, active=0)
        self.list.append_column(c)

        for (title, col) in COLS:
            render = gtk.CellRendererText()
            if col > 1:
                render.set_property('editable', True)
                render.connect('edited', self.__change_name, col)
            
            self.list.append_column(
                gtk.TreeViewColumn(title, render, text=col))
        self.list.set_model(self.model)

        self.iter_list = []
        self.progress.set_pass(_('Building display'), len(self.name_list))
        for (id, data) in self.name_list:

            place = self.db.get_place_from_handle(id)
            descr = place.get_title()

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
        path = tuple([int (i) for i in path_string.split(':')])
        row = self.model[path]
        row[0] = not row[0]

    def build_menu_names(self, obj):
        return (self.label, None)

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-db')

    def on_ok_clicked(self, obj):
        self.trans = self.db.transaction_begin("", batch=True)
        self.db.disable_signals()
        changelist = [node for node in self.iter_list
                      if self.model.get_value(node, 0)]

        for change in changelist:
            row = self.model[change]
            place = self.db.get_place_from_handle(row[6])
            (city, state, postal, country) = (row[2], row[3], row[4], row[5])

            if city:
                place.get_main_location().set_city(city)
            if state:
                place.get_main_location().set_state(state)
            if postal:
                place.get_main_location().set_postal_code(postal)
            if country:
                place.get_main_location().set_country(country)
            self.db.commit_place(place, self.trans)

        self.db.transaction_commit(self.trans, _("Extract Place data"))
        self.db.enable_signals()
        self.db.request_rebuild()
        self.close()
        
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
    translated_name = _("Extract place data from a place title"), 
    status = _("Stable"), 
    author_name = "Donald N. Allingham", 
    author_email = "don@gramps-project.org", 
    description = _("Attempts to extract city and state/province "
                    "from a place title")
    )
