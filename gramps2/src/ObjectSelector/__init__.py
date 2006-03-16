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

"""
ObjectSelector provides a collection of widgets that can be used to select
any of the Primary objects in the database.

The class hierachy is currently this:

    gtk.Window
       ObjectSelectorWindow
           PersonSelector

    gtk.Frame
        FilterFrameBase
            PersonFilterFrame
            FamilyFilterFrame
        ObjectFrameBase
            FamilyFrame
            PersonFrame
        PreviewFrameBase
            FamilyPreviewFrame
            PersonPreviewFrame
        TreeFrameBase
            FamilyTreeFrame
            PersonTreeFrame

    FilterSpecBase 
        PersonFilterSpec

    ObjectFrameFactory

To implement a selector for a new Primary RelLib type you need to implement a new
subclass of each of:

       FilterFrameBase
       ObjectFrameBase
       PreviewFrameBase
       TreeFrameBase

You must then extend ObjectFrameFactory so that it know how to create the new selector
type. The new type should also be added to the OBJECT_LIST in _ObjectSelectorWindow.py
so that it shows up in the selector. A subclass of ObjectSelectorWindow can be added to
this file as a convienience for starting a selector for just the new type.

At runtime Object selector is constructed from these widgets in the following structure:


-------------------------------------------------------------------------------
| ObjectSelectorWindow                                                        |
|
| --------------------------------------------------------------------------- |
| | Subclass of ObjectFrameBase                                             | |
| |                                                                         | |
| | -----------------------------  ---------------------------------------- | |
| | | Subclass of TreeFrameBase |  | Subclass of PreviewFrameBase         | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  ---------------------------------------- | |
| | |                           |  ---------------------------------------- | |
| | |                           |  | Subclass of FilterFrameBase          | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | |                           |  |                                      | | |
| | -----------------------------  ---------------------------------------- | |
| --------------------------------------------------------------------------- |
-------------------------------------------------------------------------------

"""
from TransUtils import sgettext as _

from _ObjectSelectorWindow import ObjectSelectorWindow
from _Constants import ObjectTypes
from _PersonFilterSpec import PersonFilterSpec

class PersonSelector(ObjectSelectorWindow):
    """Provides an ObjectSelectorWindow configured for selecting a person object."""

    def __init__(self,dbstate,uistate,track,filter_spec=None,title=_("Select Person")):
        ObjectSelectorWindow.__init__(self,dbstate,uistate,track,
                                      title=title,
                                      filter_spec=filter_spec,
                                      default_object_type = ObjectTypes.PERSON,
                                      object_list = [ObjectTypes.PERSON])
