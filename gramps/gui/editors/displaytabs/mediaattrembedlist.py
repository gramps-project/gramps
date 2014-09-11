#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2014  Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from .attrembedlist import AttrEmbedList

#-------------------------------------------------------------------------
#
# MediaAttrEmbedList
#
#-------------------------------------------------------------------------
class MediaAttrEmbedList(AttrEmbedList):

    def __init__(self, dbstate, uistate, track, data):
        AttrEmbedList.__init__(self, dbstate, uistate, track, data)

    def get_editor(self):
        from .. import EditAttribute
        return EditAttribute

    def get_user_values(self):
        return self.dbstate.db.get_media_attribute_types()
