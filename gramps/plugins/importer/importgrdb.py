#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2012       Tim G L Lyons
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

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".Db")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.const import URL_WIKISTRING

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_MINVERSION = 9
_DBVERSION = 14


#-------------------------------------------------------------------------
#
# Importing data into the currently open database.
# Ability to import .grdb files removed in accordance with
# http://gramps.1791082.n4.nabble.com/Status-of-GEPS-023-tp4329141p4329746.html
#
#-------------------------------------------------------------------------
def importData(database, filename, user):
    migrate_dict = { 'gramps_wiki_migrate_two_to_three_url' :
                         URL_WIKISTRING +
                             "Gramps_4.2_Wiki_Manual_-_Manage_Family_Trees#"
                             "Moving_a_Gramps_2.2_databases_to_Gramps_3.x" }
    user.notify_error(_("%s could not be opened") % filename,
                      _("The Database version is not supported "
                        "by this version of Gramps."
                        "You should use an old copy of Gramps at "
                        "version 3.0.x and import your database into "
                        "that version. You should then export a copy "
                        "of your data to Gramps XML (Family Tree). "
                        "Then you should upgrade to the latest "
                        "version of Gramps (for example this version), "
                        "create a new empty database and import the "
                        "Gramps XML into that version. "
                        "Please refer to:"
                        "%(gramps_wiki_migrate_two_to_three_url)s" ) %
                                migrate_dict )
    return
