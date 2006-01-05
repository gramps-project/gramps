from gettext import gettext as _

import gtk

from _ErrorReportAssistant import ErrorReportAssistant

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
        self.response = self.top.run()
        if self.response == gtk.RESPONSE_HELP:
            self.help_clicked()
        elif self.response == gtk.RESPONSE_YES:
            ErrorReportAssistant(error_detail = self._error_detail,
                                 rotate_handler = self._rotate_handler)
        self.top.destroy()

    def draw_window(self):
        title = "%s - GRAMPS" % _("Error Report")
        self.top = gtk.Dialog(title)
        #self.top.set_default_size(400,350)
        self.top.set_has_separator(False)
        self.top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % _("An unexpected error has occured"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label,False,False,5)

        sep = gtk.HSeparator()
        self.top.vbox.pack_start(sep,False,False,5)

        instructions_label = gtk.Label('<span weight="bold">%s</span>\n'\
                                       '%s' % \
                                       ( _("Gramps has experienced an unexpected error."),
                                         _("Your data will safe but it would be advisable to restart gramps immediately. "\
                                           "If you would like to report the problem to the Gramps team "\
                                           "please click Report and the Error Reporting Wizard will help you "\
                                           "to make a bug report.")))
        instructions_label.set_line_wrap(True)
        instructions_label.set_use_markup(True)

        self.top.vbox.pack_start(instructions_label,False,False,5)
        
        tb_frame = gtk.Frame(_("Error Detail"))
        tb_label = gtk.Label(self._error_detail)
        
        tb_frame.add(tb_label)

        tb_expander = gtk.Expander('<span weight="bold">%s</span>' % _("Error Detail"))
        tb_expander.set_use_markup(True)
        tb_expander.add(tb_frame)
        
        self.top.vbox.pack_start(tb_expander,True,True,5)


        self.top.add_button(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)
        self.top.add_button(_("Report"),gtk.RESPONSE_YES)
        self.top.add_button(gtk.STOCK_HELP,gtk.RESPONSE_HELP)
        
        self.top.show_all()
