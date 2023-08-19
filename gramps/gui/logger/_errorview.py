#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from ._errorreportassistant import ErrorReportAssistant
from ..display import display_help
from ..utils import get_display_size
from ..managedwindow import ManagedWindow

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = "%s_-_Error_and_Warning_Reference" % URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Error_Report", "manual")


class ErrorView(ManagedWindow):
    """
    A Dialog for displaying errors.
    """

    def __init__(self, error_detail, rotate_handler):
        """
        Initialize the handler with the buffer size.
        """
        ManagedWindow.__init__(self, None, [], self.__class__, modal=True)
        # the self.top.run() below makes Gtk make it modal, so any change to
        # the previous line's "modal" would require that line to be changed

        self._error_detail = error_detail
        self._rotate_handler = rotate_handler
        self.p_width = None  # may or may not be changed in draw_window
        self.p_height = None

        self.draw_window()
        self.set_window(self.top, None, None)
        if self.parent_window is not None:
            self.setup_configs(
                "interface.errorview",
                600,
                250,
                # these two may be None or may be real
                p_width=self.p_width,
                p_height=self.p_height,
            )
        if self.p_width is None and self.p_height is None:
            self.show()  # ManagedWindow
        else:
            self.top.show_all()
        self.run()

    def run(self):
        response = Gtk.ResponseType.HELP
        while response == Gtk.ResponseType.HELP:
            # the self.top.run() makes Gtk make it modal, so any change to that
            # line would require the ManagedWindow.__init__ to be changed also
            response = self.top.run()
            if self.parent_window is not None:
                self._save_position(save_config=False)  # the next line saves it
                self._save_size()
            if response == Gtk.ResponseType.HELP:
                self.help_clicked()
            elif response == Gtk.ResponseType.YES:
                ErrorReportAssistant(
                    error_detail=self._error_detail,
                    rotate_handler=self._rotate_handler,
                    ownthread=True,
                    parent=self.top,
                )
                self.top.destroy()
            elif response in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
                self.top.destroy()

    def close(self, *obj):
        pass  # let "run" handle it (not ManagedWindow)

    def help_clicked(self):
        """Display the relevant portion of Gramps manual"""

        display_help(WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def draw_window(self):
        title = "%s - Gramps" % _("Error Report")
        self.top = Gtk.Dialog(title=title)
        # look over the top level windows, it seems the oldest come first, so
        # the most recent still visible window appears to be a good choice for
        # a transient parent
        for win in self.top.list_toplevels():
            if win == self.top:  # not interested if this is us...
                continue
            if win.is_toplevel() and win.is_visible():
                self.parent_window = win  # for ManagedWindow
        if self.parent_window is None:  # but it is on some screen
            self.p_width, self.p_height = get_display_size(self.top)
            self.top.set_position(Gtk.WindowPosition.CENTER)
            self.top.set_urgency_hint(True)
            self.top.set_keep_above(True)
            self.top.set_default_size(600, -1)

        vbox = self.top.get_content_area()
        vbox.set_spacing(5)
        self.top.set_border_width(12)
        hbox = Gtk.Box()
        hbox.set_spacing(12)
        image = Gtk.Image()
        image.set_from_icon_name("dialog-error", Gtk.IconSize.DIALOG)
        label = Gtk.Label(
            label='<span size="larger" weight="bold">%s</span>'
            % _("Gramps has experienced an unexpected error")
        )
        label.set_use_markup(True)

        hbox.pack_start(image, False, True, 0)
        hbox.add(label)

        vbox.pack_start(hbox, False, False, 5)

        instructions_label = Gtk.Label(
            label=_(
                "Your data will be safe but it would be advisable to restart Gramps immediately. "
                "If you would like to report the problem to the Gramps team "
                "please click Report and the Error Reporting Wizard will help you "
                "to make a bug report."
            )
        )
        instructions_label.set_line_wrap(True)
        instructions_label.set_use_markup(True)

        vbox.pack_start(instructions_label, False, False, 5)

        tb_frame = Gtk.Frame(label=_("Error Detail"))
        tb_frame.set_border_width(6)
        tb_label = Gtk.TextView()
        tb_label.get_buffer().set_text(self._error_detail.get_formatted_log())
        tb_label.set_border_width(6)
        tb_label.set_editable(False)
        tb_label.set_vexpand(True)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_size_request(-1, 60)

        tb_frame.add(scroll)
        scroll.add(tb_label)

        tb_expander = Gtk.Expander(
            label='<span weight="bold">%s</span>' % _("Error Detail")
        )
        tb_expander.set_use_markup(True)
        tb_expander.add(tb_frame)

        vbox.pack_start(tb_expander, True, True, 5)

        self.top.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.top.add_button(_("Report"), Gtk.ResponseType.YES)
        self.top.add_button(_("_Help"), Gtk.ResponseType.HELP)
