#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"""
GRAMPS plugin that will convert all Surnames (Last Names) in a
database to all capital letters. Many genealogy program deal
with last names in all uppercase, and many genealogists prefer
to work in this manner.
"""

import string

# Load the GRAMPS i18n (internationalization) library
import intl
_ = intl.gettext

# Load the GRAMPS utility library
import Utils

def runTool(database,active_person,callback):
    """
    The GRAMPS plugin system requires a plugin task to take three
    arguments. These are the database, the currently active
    person, and a callback task to be called to update the display.

    This plugin task creates a CapitalizeNames instance to convert all
    names in the database to all capital letters. Since we are working
    on the entire database, the active_person has no context, and is
    not used.
    """
    
    try:
        CapitalizeNames(database,callback)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

class CapitalizeNames:
    """
    Creates a class that loops through all people in the database,
    converting the last name to all capitals. All work is done in
    the __init__ task, simply because it is easy to do so.
    """
    def __init__(self,db,callback):

        # Loop through the keys off all people in the database

        changed = 0
        for key in db.getPersonKeys():

            # from the key, get the person associated with the key
            person = db.getPerson(key)

            # Each person can have a primary name and a list of
            # alternate names. Make sure that we get both. getPrimaryName
            # returns a name while getAlternateNames returns a list of
            # names.
            #
            # If the capitalized version is not the same as the original
            # value, the name needs to be updated. The changed flag is set
            # so that we know that we changed data.
            #
            # One additional wart is that in order to make the ZODB implementation
            # not drag to a complete halt, we need to rebuild the display
            # entry for the person who has changed.
            
            for name in [person.getPrimaryName()] + person.getAlternateNames():
                surname = name.getSurname()
                capital_surname = string.upper(surname)
                if surname != capital_surname:
                    changed = 1
                    name.setSurname(capital_surname)
                    db.buildPersonDisplay(key)

        # GRAMPS also keeps a list of surnames for drop down menus. We need
        # to alter this as well.

        surname_list = db.getSurnames()
        
        for name in surname_list:
            new_name = string.upper(name)
            surname_list.remove(name)
            surname_list.append(new_name)
        surname_list.sort()

        # If any of the data was changed, we need to notify GRAMPS of this
        # so that it knows to prompt the user if an attempt is made to
        # exit without saving the changes.
        if changed:
            Utils.modified()
            
        # Call the callback function to allow GRAMPS to update its displays
        # Passing a value of 1 indicates tells GRAMPS to draw its windows
        # because data has changed.

        callback(changed)

        
#------------------------------------------------------------------------
#
# Handle the plugin registration
#
#------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    task=runTool,
    name=_("Convert surnames to all capital letters"),
    category=_("Database Processing"),
    description=_("Searches the entire database and converts all surnames to capital letters")
    )



