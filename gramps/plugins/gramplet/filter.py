# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2011  Nick Hall
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

"""
Module providing a gramplet interface to the sidebar filters.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.filters.sidebar import (
    PersonSidebarFilter, FamilySidebarFilter, EventSidebarFilter,
    SourceSidebarFilter, CitationSidebarFilter, PlaceSidebarFilter,
    MediaSidebarFilter, RepoSidebarFilter, NoteSidebarFilter)

#-------------------------------------------------------------------------
#
# Filter class
#
#-------------------------------------------------------------------------
class Filter(Gramplet):
    """
    The base class for all filter gramplets.
    """
    FILTER_CLASS = None

    def init(self):
        self.filter = self.FILTER_CLASS(self.dbstate, self.uistate,
                                        self.__filter_clicked)
        self.widget = self.filter.get_widget()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.widget)
        self.widget.show_all()

    def __filter_clicked(self):
        """
        Called when the filter apply button is clicked.
        """
        self.gui.view.generic_filter = self.filter.get_filter()
        self.gui.view.build_tree()

#-------------------------------------------------------------------------
#
# PersonFilter class
#
#-------------------------------------------------------------------------
class PersonFilter(Filter):
    """
    A gramplet providing a Person Filter.
    """
    FILTER_CLASS = PersonSidebarFilter

#-------------------------------------------------------------------------
#
# FamilyFilter class
#
#-------------------------------------------------------------------------
class FamilyFilter(Filter):
    """
    A gramplet providing a Family Filter.
    """
    FILTER_CLASS = FamilySidebarFilter

#-------------------------------------------------------------------------
#
# EventFilter class
#
#-------------------------------------------------------------------------
class EventFilter(Filter):
    """
    A gramplet providing a Event Filter.
    """
    FILTER_CLASS = EventSidebarFilter

#-------------------------------------------------------------------------
#
# SourceFilter class
#
#-------------------------------------------------------------------------
class SourceFilter(Filter):
    """
    A gramplet providing a Source Filter.
    """
    FILTER_CLASS = SourceSidebarFilter

#-------------------------------------------------------------------------
#
# CitationFilter class
#
#-------------------------------------------------------------------------
class CitationFilter(Filter):
    """
    A gramplet providing a Citation Filter.
    """
    FILTER_CLASS = CitationSidebarFilter

#-------------------------------------------------------------------------
#
# PlaceFilter class
#
#-------------------------------------------------------------------------
class PlaceFilter(Filter):
    """
    A gramplet providing a Place Filter.
    """
    FILTER_CLASS = PlaceSidebarFilter

#-------------------------------------------------------------------------
#
# MediaFilter class
#
#-------------------------------------------------------------------------
class MediaFilter(Filter):
    """
    A gramplet providing a Media Filter.
    """
    FILTER_CLASS = MediaSidebarFilter

#-------------------------------------------------------------------------
#
# RepositoryFilter class
#
#-------------------------------------------------------------------------
class RepositoryFilter(Filter):
    """
    A gramplet providing a Repository Filter.
    """
    FILTER_CLASS = RepoSidebarFilter

#-------------------------------------------------------------------------
#
# NoteFilter class
#
#-------------------------------------------------------------------------
class NoteFilter(Filter):
    """
    A gramplet providing a Note Filter.
    """
    FILTER_CLASS = NoteSidebarFilter
