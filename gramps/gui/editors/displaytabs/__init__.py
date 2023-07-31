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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#


# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger("gui.editors.displaytabs")

# first import models
from .childmodel import ChildModel

# Then import tab classes
from .grampstab import GrampsTab
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL
from .addrembedlist import AddrEmbedList
from .attrembedlist import AttrEmbedList
from .backreflist import BackRefList
from .eventattrembedlist import EventAttrEmbedList
from .eventbackreflist import EventBackRefList
from .eventembedlist import EventEmbedList
from .familyattrembedlist import FamilyAttrEmbedList
from .familyldsembedlist import FamilyLdsEmbedList
from .gallerytab import GalleryTab
from .ldsembedlist import LdsEmbedList
from .locationembedlist import LocationEmbedList
from .mediaattrembedlist import MediaAttrEmbedList
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
from .placenameembedlist import PlaceNameEmbedList
from .placerefembedlist import PlaceRefEmbedList
from .repoembedlist import RepoEmbedList
from .surnametab import SurnameTab
from .sourcebackreflist import SourceBackRefList
from .srcattrembedlist import SrcAttrEmbedList
from .webembedlist import WebEmbedList
