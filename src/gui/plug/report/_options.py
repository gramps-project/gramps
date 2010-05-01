#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Jakim Friant
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

# Written by Alex Roitman

"""
Report option handling, including saving and parsing.
"""
from gen.plug.report._options import ReportOptions
from gui.plug import GuiMenuOptions

#-------------------------------------------------------------------------
#
# MenuReportOptions
#
#-------------------------------------------------------------------------
class MenuReportOptions(GuiMenuOptions, ReportOptions):
    """

    The MenuReportOptions class implements the ReportOptions
    functionality in a generic way so that the user does not need to
    be concerned with the graphical representation of the options.

    The user should inherit the MenuReportOptions class and override the
    add_menu_options function. The user can add options to the menu and the
    MenuReportOptions class will worry about setting up the GUI.

    """
    def __init__(self, name, dbase):
        ReportOptions.__init__(self, name, dbase)
        GuiMenuOptions.__init__(self)

    def load_previous_values(self):
        ReportOptions.load_previous_values(self)
        # Pass the loaded values to the menu options so they will be displayed
        # properly.
        for optname in self.options_dict:
            menu_option = self.menu.get_option_by_name(optname)
            if menu_option:
                menu_option.set_value(self.options_dict[optname])

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Jakim Friant
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

# Written by Alex Roitman

"""
Report option handling, including saving and parsing.
"""
from gen.plug.report._options import ReportOptions
from gui.plug import GuiMenuOptions

#-------------------------------------------------------------------------
#
# MenuReportOptions
#
#-------------------------------------------------------------------------
class MenuReportOptions(GuiMenuOptions, ReportOptions):
    """

    The MenuReportOptions class implements the ReportOptions
    functionality in a generic way so that the user does not need to
    be concerned with the graphical representation of the options.

    The user should inherit the MenuReportOptions class and override the
    add_menu_options function. The user can add options to the menu and the
    MenuReportOptions class will worry about setting up the GUI.

    """
    def __init__(self, name, dbase):
        ReportOptions.__init__(self, name, dbase)
        GuiMenuOptions.__init__(self)

    def load_previous_values(self):
        ReportOptions.load_previous_values(self)
        # Pass the loaded values to the menu options so they will be displayed
        # properly.
        for optname in self.options_dict:
            menu_option = self.menu.get_option_by_name(optname)
            if menu_option:
                menu_option.set_value(self.options_dict[optname])

#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Jakim Friant
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

# Written by Alex Roitman

"""
Report option handling, including saving and parsing.
"""
from gen.plug.report._options import ReportOptions
from gui.plug import GuiMenuOptions

#-------------------------------------------------------------------------
#
# MenuReportOptions
#
#-------------------------------------------------------------------------
class MenuReportOptions(GuiMenuOptions, ReportOptions):
    """

    The MenuReportOptions class implements the ReportOptions
    functionality in a generic way so that the user does not need to
    be concerned with the graphical representation of the options.

    The user should inherit the MenuReportOptions class and override the
    add_menu_options function. The user can add options to the menu and the
    MenuReportOptions class will worry about setting up the GUI.

    """
    def __init__(self, name, dbase):
        ReportOptions.__init__(self, name, dbase)
        GuiMenuOptions.__init__(self)

    def load_previous_values(self):
        ReportOptions.load_previous_values(self)
        # Pass the loaded values to the menu options so they will be displayed
        # properly.
        for optname in self.options_dict:
            menu_option = self.menu.get_option_by_name(optname)
            if menu_option:
                menu_option.set_value(self.options_dict[optname])

