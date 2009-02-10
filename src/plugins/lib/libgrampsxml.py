# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Brian G. Matherly
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

# $Id$

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import PluginManager, Plugin

#------------------------------------------------------------------------
#
# Public Constants
#
#------------------------------------------------------------------------
GRAMPS_XML_VERSION = "1.3.0"

#------------------------------------------------------------------------
#
# Register the plugins
#
#------------------------------------------------------------------------
PluginManager.get_instance().register_plugin( 
Plugin(
    name = __name__, 
    description = _("Provides common functionality for Gramps XML "
                    "import/export."),
    module_name = __name__ 
      )
)