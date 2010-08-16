#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Douglas Blank <doug.blank@gmail.com>
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
        }

def load_on_reg(dbstate, uistate, plugin):
    """
    Runs when plugin is registered.
    """
    dir, fname = os.path.split(__file__)
    CSS_FILES = [
        # id, user selectable?, translated_name, fullpath, navigation target name, additional files
        # "default" is used as default
        ["Basic-Ash",     1, _("Basic-Ash"),         
         os.path.join(dir, "css", 'Web_Basic-Ash.css'),     None, []],
        ["Basic-Blue",    1, _("Basic-Blue"),        
         os.path.join(dir, "css", 'Web_Basic-Blue.css'),    "Web_Navigation-Menus.css", []],
        ["Basic-Cypress", 1, _("Basic-Cypress"),     
         os.path.join(dir, "css", 'Web_Basic-Cypress.css'), None, []],
        ["Basic-Lilac",   1, _("Basic-Lilac"),       
         os.path.join(dir, "css", 'Web_Basic-Lilac.css'),   None, []],
        ["Basic-Peach",   1, _("Basic-Peach"),       
         os.path.join(dir, "css", 'Web_Basic-Peach.css'),   None, []],
        ["Basic-Spruce",  1, _("Basic-Spruce"),      
         os.path.join(dir, "css", 'Web_Basic-Spruce.css'),  None, []],
        ["Mainz",         1, _("Mainz"),             
         os.path.join(dir, "css", 'Web_Mainz.css'),         None, 
         [os.path.join(dir, "images", "Web_Mainz_Bkgd.png"), 
          os.path.join(dir, "images", "Web_Mainz_Header.png"), 
          os.path.join(dir, "images", "Web_Mainz_Mid.png"), 
          os.path.join(dir, "images", "Web_Mainz_MidLight.png")]],
        ["Nebraska",      1, _("Nebraska"),          
         os.path.join(dir, "css", 'Web_Nebraska.css'),      None, []],
        ["Visually Impaired", 1, _("Visually Impaired"), 
         os.path.join(dir, "css", 'Web_Visually.css'),  "Web_Navigation-Menus.css", []],
        ["No style sheet",1, _("No style sheet"),    '',    None, []],
        ["behaviour",     0, "Behaviour",            
         os.path.join(dir, "css", 'behaviour.css'),         None, []],
        ["mapstraction",  0, "",
         os.path.join(dir, "css", "Mapstraction.css"),      None, []],
        ["default",       0, _("Basic-Ash"),         
         os.path.join(dir, "css", 'Web_Basic-Ash.css'),     None, []],
        ["Print-Default", 0, "Print-Default",        
         os.path.join(dir, "css", 'Web_Print-Default.css'), None, []],
        ["Navigation-Vertical", 0, "Navigation-Vertical", 
         os.path.join(dir, "css", 'Web_Navigation-Vertical.css'), None, []],
        ["Navigation-Horizontal", 0, "Navigation-Horizontal", 
         os.path.join(dir, "css", 'Web_Navigation-Horizontal.css'), None, []],
        ['Gender Images', 0, 'Gender Images', None, None, 
         [os.path.join(dir, "images", "Web_Gender_Female.png"),
          os.path.join(dir, "images", "Web_Gender_Male.png"),
          ]],
        ['All Images', 0, 'All Images', None, None, 
         [os.path.join(dir, "images", "favicon2.ico"),
          os.path.join(dir, "images", "blank.gif"),
          os.path.join(dir, "images", "document.png")]],
        ['Copyright', 0, 'Copyright', os.path.join(dir, "images", "somerights20.gif"), None, []],
        ['Document', 0, 'Document', os.path.join(dir, "images", "document.png"), None, []],
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
