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

    
#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DisplayTabs")

# first import models
from _ChildModel import ChildModel

# Then import tab classes
from _EmbeddedList import EmbeddedList 
from _AddrEmbedList import AddrEmbedList
from _AttrEmbedList import AttrEmbedList
from _BackRefList import BackRefList
from _DataEmbedList import DataEmbedList
from _EventBackRefList import EventBackRefList
from _EventEmbedList import EventEmbedList
from _FamilyAttrEmbedList import FamilyAttrEmbedList
from _FamilyLdsEmbedList import FamilyLdsEmbedList
from _GalleryTab import GalleryTab
from _LdsEmbedList import LdsEmbedList
from _LocationEmbedList import LocationEmbedList
from _MediaBackRefList import MediaBackRefList
from _NameEmbedList import NameEmbedList
from _NoteTab import NoteTab
from _TextTab import TextTab
from _PersonEventEmbedList import PersonEventEmbedList
from _PersonRefEmbedList import PersonRefEmbedList
from _PersonBackRefList import PersonBackRefList
from _PlaceBackRefList import PlaceBackRefList
from _RepoEmbedList import RepoEmbedList
from _SourceBackRefList import SourceBackRefList
from _SourceEmbedList import SourceEmbedList
from _WebEmbedList import WebEmbedList
