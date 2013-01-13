#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010       Nick Hall
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
# BaseSidebar class
#
#-------------------------------------------------------------------------
class BaseSidebar(object):
    """
    The base class for all sidebar plugins.
    """
    def __init__(self, dbstate, uistate):
        raise NotImplementedError

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        raise NotImplementedError

    def view_changed(self, cat_num, view_num):
        """
        Called when the active view is changed.
        """
        raise NotImplementedError

    def active(self, cat_num, view_num):
        """
        Called when the sidebar is made visible.
        """
        pass

    def inactive(self):
        """
        Called when the sidebar is hidden.
        """
        pass
