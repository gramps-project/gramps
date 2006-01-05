from gettext import gettext as _

import sys,os
import const

import gtk
import Assistant

class ErrorReportAssistant:

    def __init__(self,error_detail,rotate_handler):
        self._error_detail = error_detail
        self._rotate_handler = rotate_handler

        self._sys_information_text_buffer = None
        self._user_information_text_buffer = None
        self._error_details_text_buffer = None
        self._final_report_text_buffer = None
        
        self.w = Assistant.Assistant(_('Report a bug'),self.complete)

        self.w.set_intro(_("This is the Bug Reporting Assistant. It will "\
                           "help you to make a bug report to the Gramps "\
                           "developers that will be as detailed as possible.\n"\
                           "The assistant will ask you a few questions and will "\
                           "gather some information about the error that has "\
                           "occured and the operating environment. "\
                           "At then end of the assistent you will be asked to "\
                           "send an email to the Gramps bug reporting mailing list "\
                           "and the bug report will be placed on the clip board so "\
                           "that you can paste it into your email programme and review "\
                           "exactly what information is being sent."))


        self.w.add_page(_("Error Details"), self.build_page2())
        self.w.add_page(_("System Information"), self.build_page3())
        self.w.add_page(_("Further Information"), self.build_page4())
        self.w.add_page(_("Summary"), self.build_page5(),self.page5_update)

        self.w.set_conclusion(_('Complete'),
                              _('The error report will be copied to your clipboard when you click OK. \n'
                                'Please paste the report into your favourite email client and send it to: \n\n'
                                'gramps-bugs@lists.sourceforge.net\n\n'
                                'GRAMPS is an Open Source project. Its success '
                                'depends on the users. User feedback is important. '
                                'Thankyou for taking the time to submit a bug report.'))

        self.w.show()

    def complete(self):
        clipboard = gtk.Clipboard()
        clipboard.set_text(
            self._final_report_text_buffer.get_text(
              self._final_report_text_buffer.get_start_iter(),
              self._final_report_text_buffer.get_end_iter()))
        
        clipboard = gtk.Clipboard(selection="PRIMARY")
        clipboard.set_text(
            self._final_report_text_buffer.get_text(
              self._final_report_text_buffer.get_start_iter(),
              self._final_report_text_buffer.get_end_iter()))

    def _get_sys_information(self):
        return "Python version: %s \n"\
               "Gramps version: %s \n"\
               "OS: %s\n"\
               "Distribution: %s\n"\
               % (str(sys.version).replace('\n',''),
                  str(const.version),
                  os.uname()[0],
                  os.uname()[2])

    def build_page2(self):

        box = gtk.VBox()

        label = gtk.Label(_("This is the detail Gramps error information, don't worry if you "\
                            "do not understand it. If you can see that there is any personal "\
                            "informatin included in the error details please remove it, you "\
                            "will have the opportunity to add further detail about the error "\
                            "in the following pages of the assistant."))

        label.set_line_wrap(True)

        box.pack_start(label,False,False,5)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()

        self._error_details_text_buffer = textview.get_buffer()
        self._error_details_text_buffer.set_text(self._error_detail)
            
        sw.add(textview)
        sw.show()
        textview.show()
        
        box.pack_start(sw)
        box.show_all()

        return box

    def build_page3(self):

        box = gtk.VBox()

        label = gtk.Label(_("Please check the information below and correct anything that "\
                            "you know to be wrong or remove anything that you would rather not "\
                            "have included in the bug report."))

        label.set_line_wrap(True)

        box.pack_start(label,False,False,5)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()

        self._sys_information_text_buffer = textview.get_buffer()
        self._sys_information_text_buffer.set_text(self._get_sys_information())
            
        sw.add(textview)
        sw.show()
        textview.show()
        
        box.pack_start(sw)
        box.show_all()

        return box

    def build_page4(self):

        box = gtk.VBox()

        label = gtk.Label(_("Please provide as much information as you can "\
                            "about what you were doing when the error occured. "))

        label.set_line_wrap(True)

        box.pack_start(label,False,False,5)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        
        self._user_information_text_buffer = textview.get_buffer()
        
        sw.add(textview)
        sw.show()
        textview.show()
        
        box.pack_start(sw)
        box.show_all()

        return box


    def build_page5(self):

        box = gtk.VBox()

        label = gtk.Label(_("The complete bug report is shown below. When you click Forward it will "\
                            "be copied onto the clickboard and you will be asked to email it.\n"\
                            "Please check that the information is correct, do not worry if you "\
                            "don't understand the detail of the error information. Just make sure "\
                            "that it does not contain anything that you do not want to be sent "\
                            "to the developers."))

        label.set_line_wrap(True)

        box.pack_start(label,False,False,5)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        
        self._final_report_text_buffer = textview.get_buffer()        
        
        sw.add(textview)
        sw.show()
        textview.show()
        
        box.pack_start(sw)
        box.show_all()

        return box

    def page5_update(self):

        self._final_report_text_buffer.set_text(
            "System Information: \n\n" +
            self._sys_information_text_buffer.get_text(
              self._sys_information_text_buffer.get_start_iter(),
              self._sys_information_text_buffer.get_end_iter()) +
            "Additional Information: \n\n" +
            self._user_information_text_buffer.get_text(
              self._user_information_text_buffer.get_start_iter(),
              self._user_information_text_buffer.get_end_iter()) +
            "\nError Details: \n\n" +
            self._error_details_text_buffer.get_text(
              self._error_details_text_buffer.get_start_iter(),
              self._error_details_text_buffer.get_end_iter())            
            )
