#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010 Nick Hall
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

#------------------------------------------------------------------------
#
# Register default sidebars
#
#------------------------------------------------------------------------

register(SIDEBAR, 
id    = 'categorysidebar',
name  = _("Category Sidebar"),
description =  _("A sidebar to allow the selection of view categories"),
version = '1.0',
gramps_target_version = '3.5',
status = STABLE,
fname = 'categorysidebar.py',
authors = [u"Nick Hall"],
authors_email = ["nick__hall@hotmail.com"],
sidebarclass = 'CategorySidebar',
menu_label = _('Category'),
order = START
)
