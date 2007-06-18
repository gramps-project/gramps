from gettext import gettext as _

import gtk

from _ErrorReportAssistant import ErrorReportAssistant
import GrampsDisplay

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
                ErrorReportAssistant(error_detail = self._error_detail,
                                     rotate_handler = self._rotate_handler)
        self.top.destroy()

    def help_clicked(self):
        """Display the relevant portion of GRAMPS manual"""
        # FIXME: replace tag when relevant help page is available
        GrampsDisplay.help('faq')

    def draw_window(self):
        title = "%s - GRAMPS" % _("Error Report")
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
                          % _("GRAMPS has experienced an unexpected error"))
        label.set_use_markup(True)

        hbox.pack_start(image,False)
        hbox.add(label)

        self.top.vbox.pack_start(hbox,False,False,5)

        instructions_label = gtk.Label(
            _("Your data will be safe but it would be advisable to restart GRAMPS immediately. "\
              "If you would like to report the problem to the GRAMPS team "\
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
