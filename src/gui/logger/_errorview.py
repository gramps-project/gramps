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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gen.const import URL_MANUAL_PAGE
from gen.ggettext import sgettext as _
from _errorreportassistant import ErrorReportAssistant
from gui.display import display_help

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_FAQ' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|General')

class ErrorView(object):
    """
    A Dialog for displaying errors.
    """
    
    def __init__(self, error_detail, rotate_handler):
        """
        Initialize the handler with the buffer size.
        """

        self._error_detail = error_detail
        self._rotate_handler = rotate_handler
        
        self.draw_window()
        self.run()

    def run(self):
        response = gtk.RESPONSE_HELP
        while response == gtk.RESPONSE_HELP:
            response = self.top.run()
            if response == gtk.RESPONSE_HELP:
                self.help_clicked()
            elif response == gtk.RESPONSE_YES:
                self.top.destroy()
                ErrorReportAssistant(error_detail = self._error_detail,
                                     rotate_handler = self._rotate_handler,
                                     ownthread=True)
            elif response == gtk.RESPONSE_CANCEL:
                self.top.destroy()

    def help_clicked(self):
        """Display the relevant portion of GRAMPS manual"""
        
        display_help(WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def draw_window(self):
        title = "%s - Gramps" % _("Error Report")
        self.top = gtk.Dialog(title)
        #self.top.set_default_size(400,350)
        self.top.set_has_separator(False)
        self.top.vbox.set_spacing(5)
        self.top.set_border_width(12)
        hbox = gtk.HBox()
        hbox.set_spacing(12)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_DIALOG)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % _("Gramps has experienced an unexpected error"))
        label.set_use_markup(True)

        hbox.pack_start(image,False)
        hbox.add(label)

        self.top.vbox.pack_start(hbox,False,False,5)

        instructions_label = gtk.Label(
            _("Your data will be safe but it would be advisable to restart Gramps immediately. "\
              "If you would like to report the problem to the Gramps team "\
              "please click Report and the Error Reporting Wizard will help you "\
              "to make a bug report."))
        instructions_label.set_line_wrap(True)
        instructions_label.set_use_markup(True)

        self.top.vbox.pack_start(instructions_label,False,False,5)
        
        tb_frame = gtk.Frame(_("Error Detail"))
        tb_frame.set_border_width(6)
        tb_label = gtk.TextView()
        tb_label.get_buffer().set_text(self._error_detail.get_formatted_log())
        tb_label.set_border_width(6)
        tb_label.set_editable(False)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_size_request(-1, 60)
        
        tb_frame.add(scroll)
        scroll.add_with_viewport(tb_label)

        tb_expander = gtk.Expander('<span weight="bold">%s</span>' % _("Error Detail"))
        tb_expander.set_use_markup(True)
        tb_expander.add(tb_frame)
        
        self.top.vbox.pack_start(tb_expander,True,True,5)


        self.top.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        self.top.add_button(_("Report"),gtk.RESPONSE_YES)
        self.top.add_button(gtk.STOCK_HELP,gtk.RESPONSE_HELP)
        
        self.top.show_all()
