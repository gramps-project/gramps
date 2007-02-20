#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007 Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------

if os.environ.has_key('USERPROFILE'):
    user_home = os.environ['USERPROFILE'] 
    home_dir = os.path.join(user_home,'gramps')
else:
    user_home = os.environ['HOME'] 
    home_dir = os.path.join(user_home,'.gramps')

bsddbenv_dir   = os.path.join(home_dir,"bsddbenv")
env_dir        = os.path.join(home_dir,"env")


app_gramps          = "application/x-gramps"
app_gramps_xml      = "application/x-gramps-xml"
app_gedcom          = "application/x-gedcom"
app_gramps_package  = "application/x-gramps-package"
app_geneweb         = "application/x-geneweb"
app_vcard           = ["text/x-vcard","text/x-vcalendar"]


PERSON_KEY     = 0
FAMILY_KEY     = 1
SOURCE_KEY     = 2
EVENT_KEY      = 3
MEDIA_KEY      = 4
PLACE_KEY      = 5
REPOSITORY_KEY = 6
REFERENCE_KEY  = 7
NOTE_KEY       = 8

PERSON_COL_KEY      = 'columns'
CHILD_COL_KEY       = 'child_columns'
PLACE_COL_KEY       = 'place_columns'
SOURCE_COL_KEY      = 'source_columns'
MEDIA_COL_KEY       = 'media_columns'
REPOSITORY_COL_KEY  = 'repository_columns'
EVENT_COL_KEY       = 'event_columns'
FAMILY_COL_KEY      = 'family_columns'
NOTE_COL_KEY        = 'note_columns'
