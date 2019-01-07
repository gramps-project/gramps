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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Url
from gramps.gen.errors import WindowActiveError
from ...ddtargets import DdTargets
from .webmodel import WebModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class WebEmbedList(EmbeddedList):

    _HANDLE_COL = 4
    _DND_TYPE = DdTargets.URL

    _MSG = {
        'add'   : _('Create and add a new web address'),
        'del'   : _('Remove the existing web address'),
        'edit'  : _('Edit the selected web address'),
        'up'    : _('Move the selected web address upwards'),
        'down'  : _('Move the selected web address downwards'),
        'jump'  : _('Jump to the selected web address'),
    }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Type')       , 0, 100, TEXT_COL, -1, None),
        (_('Path')       , 1, 200, TEXT_COL, -1, None),
        (_('Description'), 2, 150, TEXT_COL, -1, None),
        (_('Private'),     3,  30, ICON_COL, -1, 'gramps-lock')
        ]

    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track, _('_Internet'),
                              WebModel, move_buttons=True, jump_button=True)

    def get_icon_name(self):
        return 'gramps-url'

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 3), (1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        from .. import EditUrl
        url = Url()
        try:
            EditUrl(self.dbstate, self.uistate, self.track,
                    '', url, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, url):
        data = self.get_data()
        data.append(url)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def edit_button_clicked(self, obj):
        from .. import EditUrl
        url = self.get_selected()
        if url:
            try:
                EditUrl(self.dbstate, self.uistate, self.track,
                        '', url, self.edit_callback)
            except WindowActiveError:
                pass

    def edit_callback(self, url):
        self.rebuild()

    def get_popup_menu_items(self):
        return [
            (True, _('_Add'), self.add_button_clicked),
            (False, _('_Edit'), self.edit_button_clicked),
            (True, _('_Remove'), self.del_button_clicked),
            (True, _('_Jump to'), self.jump_button_clicked),
            ]

    def jump_button_clicked(self, obj):
        from ...display import display_url

        url = self.get_selected()
        if url.get_path():
            display_url(url.get_path())
