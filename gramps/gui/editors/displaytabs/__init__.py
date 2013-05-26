#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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
log = logging.getLogger("gui.editors.displaytabs")

# first import models
from .childmodel import ChildModel

# Then import tab classes
from .grampstab import GrampsTab
from .embeddedlist import EmbeddedList 
from .addrembedlist import AddrEmbedList
from .attrembedlist import AttrEmbedList
from .backreflist import BackRefList
from .eventbackreflist import EventBackRefList
from .eventembedlist import EventEmbedList
from .familyattrembedlist import FamilyAttrEmbedList
from .familyldsembedlist import FamilyLdsEmbedList
from .gallerytab import GalleryTab
from .ldsembedlist import LdsEmbedList
from .locationembedlist import LocationEmbedList
from .mediabackreflist import MediaBackRefList
from .nameembedlist import NameEmbedList
from .notebackreflist import NoteBackRefList
from .notetab import NoteTab
from .citationbackreflist import CitationBackRefList
from .citationembedlist import CitationEmbedList
from .personeventembedlist import PersonEventEmbedList
from .personrefembedlist import PersonRefEmbedList
from .personbackreflist import PersonBackRefList
from .placebackreflist import PlaceBackRefList
from .repoembedlist import RepoEmbedList
from .surnametab import SurnameTab
from .sourcebackreflist import SourceBackRefList
from .srcattrembedlist import SrcAttrEmbedList
from .webembedlist import WebEmbedList
