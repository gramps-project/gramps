# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
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


## Based on the normal fanchart

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug import Gramplet
from gramps.gui.widgets.fanchart2way import (
    FanChart2WayWidget,
    FanChart2WayGrampsGUI,
    ANGLE_WEIGHT,
)
from gramps.gui.widgets.fanchart import FORM_HALFCIRCLE, BACKGROUND_SCHEME1

_ = glocale.translation.gettext


class FanChart2WayGramplet(FanChart2WayGrampsGUI, Gramplet):
    """
    The Gramplet code that realizes the FanChartWidget.
    """

    def __init__(self, gui, nav_group=0):
        Gramplet.__init__(self, gui, nav_group)
        FanChart2WayGrampsGUI.__init__(self, self.on_childmenu_changed)
        self.generations_asc = 5
        self.generations_desc = 4
        self.background = BACKGROUND_SCHEME1
        self.fonttype = "Sans"
        self.grad_start = "#FF0000"
        self.grad_end = "#0000FF"
        self.dupcolor = "#888A85"  # light grey
        self.generic_filter = None
        self.alpha_filter = 0.2
        self.form = FORM_HALFCIRCLE
        self.angle_algo = ANGLE_WEIGHT
        self.flipupsidedownname = True
        self.twolinename = True
        self.showid = False
        self.childring = False
        self.background_gradient = True
        # self.filter = filter

        self.set_fan(FanChart2WayWidget(self.dbstate, self.uistate, self.on_popup))
        # Replace the standard textview with the fan chart widget:
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.fan)
        # Make sure it is visible:
        self.fan.show()

    def init(self):
        self.set_tooltip(
            _(
                "Click to expand/contract person\n"
                "Right-click for options\n"
                "Click and drag in open area to rotate"
            )
        )

    def active_changed(self, handle):
        """
        Method called when active person changes.
        """
        # Reset everything but rotation angle (leave it as is)
        self.update()

    def on_childmenu_changed(self, obj, person_handle):
        """Callback for the pulldown menu selection, changing to the person
        attached with menu item."""
        dummy_obj = obj
        self.set_active("Person", person_handle)
        return True
