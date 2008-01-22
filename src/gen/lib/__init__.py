#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id$

"""The core library of GRAMPS objects"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision: 9101 $"
__revision__ = "$Revision: 9101 $"

# Dates
from date import Date, DateError

# Secondary objects
from secondaryobj import SecondaryObject
from address import Address
from location import Location
from attribute import Attribute
from eventref import EventRef
from ldsord import LdsOrd
from mediaref import MediaRef 
from name import Name
from note import Note
from reporef import RepoRef
from srcref import SourceRef
from url import Url
from witness import Witness
from childref import ChildRef

# Primary objects
from primaryobj import PrimaryObject
from person import Person
from personref import PersonRef
from family import Family
from event import Event
from place import Place
from src import Source
from mediaobj import MediaObject
from repo import Repository

# These are actually metadata
from genderstats import GenderStats
from researcher import Researcher

# Type classes
from grampstype import GrampsType
from nametype import NameType
from attrtype import AttributeType
from urltype import UrlType
from childreftype import ChildRefType
from repotype import RepositoryType
from eventtype import EventType
from familyreltype import FamilyRelType
from srcmediatype import SourceMediaType
from eventroletype import EventRoleType
from markertype import MarkerType
from notetype import NoteType
