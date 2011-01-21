#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Douglas Blank <doug.blank@gmail.com>
# Copyright (C) 2011 Rob G. Healey <robhealey1@gmail.com>
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

# $Id: $

import os
import const
from gen.ggettext import sgettext as _

def make_css_dict(tup):
    """
    Basically, make a named tuple.
    """
    return {
        "id": tup[0],
        "user": tup[1],
        "translation": tup[2],
        "filename": tup[3],
        "navigation": tup[4],
        "images": tup[5],
        "javascript": tup[6],
        }

def load_on_reg(dbstate, uistate, plugin):
    """
    Runs when plugin is registered.
    """
    dir, fname = os.path.split(__file__)
    CSS_FILES = [

        # id, user selectable?, translated_name, fullpath, navigation target name, images, javascript
        # "default" is used as default

        # Basic Ash style sheet
        ["Basic-Ash",     1, _("Basic-Ash"),         
         os.path.join(dir, "css", 'Web_Basic-Ash.css'),     None, [], []],

        # Basic Blue style sheet with navigation menus
        ["Basic-Blue",    1, _("Basic-Blue"),        
         os.path.join(dir, "css", 'Web_Basic-Blue.css'),    "Web_Navigation-Menus.css", [], []],

        # Basic Cypress style sheet
        ["Basic-Cypress", 1, _("Basic-Cypress"),     
         os.path.join(dir, "css", 'Web_Basic-Cypress.css'), None, [], []],

        # basic Lilac style sheet
        ["Basic-Lilac",   1, _("Basic-Lilac"),       
         os.path.join(dir, "css", 'Web_Basic-Lilac.css'),   None, [], []],

        # basic Peach style sheet
        ["Basic-Peach",   1, _("Basic-Peach"),       
         os.path.join(dir, "css", 'Web_Basic-Peach.css'),   None, [], []],

        # basic Spruce style sheet
        ["Basic-Spruce",  1, _("Basic-Spruce"),      
         os.path.join(dir, "css", 'Web_Basic-Spruce.css'),  None, [], []],

        # Mainz style sheet with its images
        ["Mainz",         1, _("Mainz"),             
         os.path.join(dir, "css", 'Web_Mainz.css'),         None, 
         [os.path.join(dir, "images", "Web_Mainz_Bkgd.png"), 
          os.path.join(dir, "images", "Web_Mainz_Header.png"), 
          os.path.join(dir, "images", "Web_Mainz_Mid.png"), 
          os.path.join(dir, "images", "Web_Mainz_MidLight.png")], []],

        # Nebraska style sheet
        ["Nebraska",      1, _("Nebraska"),          
         os.path.join(dir, "css", 'Web_Nebraska.css'),      None, [], []],

        # Visually Impaired style sheet with its navigation menus
        ["Visually Impaired", 1, _("Visually Impaired"), 
         os.path.join(dir, "css", 'Web_Visually.css'),  "Web_Navigation-Menus.css", [], []],

        # no style sheet option
        ["No style sheet",1, _("No style sheet"),    [],    None, [], []],

        # ancestor tree style sheet
        ["ancestortree",  0, "ancestortree",
         os.path.join(dir, "css", "ancestortree.css"),      None, [], []],

        # media reference regions style sheet
        ["behaviour",     0, "Behaviour",            
         os.path.join(dir, "css", 'behaviour.css'),         None, [], []],

        # mapstraction style sheet for NarrativeWeb place maps
        ["mapstraction",  0, "mapstraction",
         os.path.join(dir, "css", "Mapstraction.css"),      None, [],
         [ os.path.join(dir, "js", "mapstraction", "mxn.core.js"),
           os.path.join(dir, "js", "mapstraction", "mxn.googlev3.core.js"),
           os.path.join(dir, "js", "mapstraction", "mxn.js"),
           os.path.join(dir, "js", "mapstraction", "mxn.openlayers.core.js")] ],   

        # default style sheet in the options
        ["default",       0, _("Basic-Ash"),         
         os.path.join(dir, "css", 'Web_Basic-Ash.css'),     None, [], []],

        # default printer style sheet
        ["Print-Default", 0, "Print-Default",        
         os.path.join(dir, "css", 'Web_Print-Default.css'), None, [], []],

        # vertical navigation style sheet
        ["Navigation-Vertical", 0, "Navigation-Vertical", 
         os.path.join(dir, "css", 'Web_Navigation-Vertical.css'), None, [], []],

        # horizontal navigation style sheet
        ["Navigation-Horizontal", 0, "Navigation-Horizontal", 
         os.path.join(dir, "css", 'Web_Navigation-Horizontal.css'), None, [], []],

        # GeoView style sheet with its image
        ["GeoView", 0, "GeoView", 
         os.path.join(dir, "css", "GeoView.css"), None,
         [os.path.join(dir, "images", "crosshairs.png"),
          os.path.join(dir, "images", "gramps-geo-altmap.png"),
          os.path.join(dir, "images", "gramps-geo-birth.png"),
          os.path.join(dir, "images", "gramps-geo-death.png"),
          os.path.join(dir, "images", "gramps-geo-mainmap.png"),
          os.path.join(dir, "images", "gramps-geo-marriage.png")],   
          [ os.path.join(dir, "js", "mapstraction", "mxn.core.js"),
            os.path.join(dir, "js", "mapstraction", "mxn.googlev3.core.js"),
            os.path.join(dir, "js", "mapstraction", "mxn.js"),
            os.path.join(dir, "js", "mapstraction", "mxn.openlayers.core.js")]],

        # gender symbol images for use in NarrativeWeb's Ancestor Tree
        ['Gender Images', 0, 'Gender Images', None, None, 
         [os.path.join(dir, "images", "Web_Gender_Female.png"),
          os.path.join(dir, "images", "Web_Gender_Male.png")], []],

        # all other images for use in NarrativeWeb
        ['All Images', 0, 'All Images', None, None, 
         [ os.path.join(dir, "images", "favicon2.ico"),
           os.path.join(dir, "images", "blank.gif"),
           os.path.join(dir, "images", "document.png")], []],

        # copyright image
        ['Copyright', 0, 'Copyright', os.path.join(dir, "images", "somerights20.gif"), None, [], []],

        # document image in case the media object is not an image
        ['Document', 0, 'Document', os.path.join(dir, "images", "document.png"), None, [], []],

        # Google core javascript
        [ "Google Core", 0, "Google Core", 
         os.path.join(dir, "js", "mapstraction", "mxn.google.core.js"), None, [], []],

        # Google Earth core javascript
        ["Google Earth", 0, "Google Earth",
         os.path.join(dir, "js", "mapstraction", "mxn.googleearth.core.js"), None, [], []],

        # Google GeoCoder javascript
        ["Google GeoCoder", 0, "Google GeoCoder",
         os.path.join(dir, "js", "mapstraction", "mxn.google.geocoder.js"), None, [], []],

        ]
    return CSS_FILES

def process_list(data):
    """
    Gather all of the web resources together, and allow override files
    if available.
    """
    retval = []
    for row in data:
        file = row[3]
        if file:
            path, filename = os.path.split(file)
            # is there a override file in the VERSION_DIR/webstuff?
            # eg, ~/.gramps/gramps33/webstuff/Web_Nebraska.css
            # if so, replace this one:
            override = os.path.join(const.VERSION_DIR, "webstuff", filename)
            if os.path.exists(override):
                row[3] = override
        retval.append(row)
    # {"Mainz": {"id": "Mainz", "user":1, ...}}
    retdict = {}
    for css in retval:
        if css[0] in retdict:
            retdict[css[0]]["images"].append(css[5])
        else:
            retdict[css[0]] = make_css_dict(css)
    return retdict
