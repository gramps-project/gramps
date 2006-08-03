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
        
        self.w = Assistant.Assistant(None,self.complete)

        self.w.add_text_page(
            _('Report a bug'),
            _("This is the Bug Reporting Assistant. It will "\
              "help you to make a bug report to the Gramps "\
              "developers that will be as detailed as possible.\n\n"\
              "The assistant will ask you a few questions and will "\
              "gather some information about the error that has "\
              "occured and the operating environment. "\
              "At the end of the assistant you will be asked to "\
              "send an email to the Gramps bug reporting mailing list. "\
              "The assistant will place the bug report on the clip board so "\
              "that you can paste it into your email programme and review "\
              "exactly what information is being sent."))


        self.w.add_page(_("Report a bug: Step 1 of 5"), self.build_page1())
        self.w.add_page(_("Report a bug: Step 2 of 5"), self.build_page2())
        self.w.add_page(_("Report a bug: Step 3 of 5"), self.build_page3())
        
        page4 = self.build_page4()
        self.w.add_page(_("Report a bug: Step 4 of 5"), page4)
        self.cb = {4:self.page4_update}
        self.w.add_page(_("Report a bug: Step 5 of 5"), self.build_page5())

        self.w.add_text_page(
            _('Complete'),
            _('GRAMPS is an Open Source project. Its success '
              'depends on its users. User feedback is important. '
              'Thank you for taking the time to submit a bug report.'))

        self.w.connect('page-changed',self.on_page_changed)

        self.w.show()

    def on_page_changed(self,obj,page,data=None):
        if self.cb.has_key(page):
            self.cb[page]()
            
    def complete(self):
        pass

    def _copy_to_clipboard(self,obj=None):
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

    def _start_email_client(self,obj=None):
        import GrampsDisplay
        GrampsDisplay.url('mailto:gramps-bugs@lists.sourceforge.net&subject="bug report"&body="%s"' \
                          % self._final_report_text_buffer.get_text(
                               self._final_report_text_buffer.get_start_iter(),
                               self._final_report_text_buffer.get_end_iter()))
        
    def _get_sys_information(self):
        if hasattr(os, "uname"):
            operatingsystem = os.uname()[0]
            distribution = os.uname()[2]
        else:
            operatingsystem = sys.platform
            distribution = " "

        return "Python version: %s \n"\
               "Gramps version: %s \n"\
               "LANG: %s\n"\
               "OS: %s\n"\
               "Distribution: %s\n"\
               % (str(sys.version).replace('\n',''),
                  str(const.version),
                  os.environ.get('LANG',''),
                  operatingsystem,
                  distribution)

    def _reset_error_details_text_buffer(self,obj=None):
        self._error_details_text_buffer.set_text(
	    "\n".join(self._rotate_handler.get_formatted_log(self._error_detail.get_record())) +
	    self._error_detail.get_formatted_log())

    def _clear_error_details_text_buffer(self,obj=None):
        self._error_details_text_buffer.delete(
            self._error_details_text_buffer.get_start_iter(),
            self._error_details_text_buffer.get_end_iter())

    def _reset_sys_information_text_buffer(self,obj=None):
        self._sys_information_text_buffer.set_text(
            self._get_sys_information())

    def _clear_sys_information_text_buffer(self,obj=None):
        self._sys_information_text_buffer.delete(
            self._sys_information_text_buffer.get_start_iter(),
            self._sys_information_text_buffer.get_end_iter())

    def _clear_user_information_text_buffer(self,obj=None):
        self._user_information_text_buffer.delete(
            self._user_information_text_buffer.get_start_iter(),
            self._user_information_text_buffer.get_end_iter())


    def build_page1(self):
        label = gtk.Label(_("If you can see that there is any personal "\
                            "information included in the error please remove it."))
        label.set_alignment(0.01,0.5)
        label.set_padding(0, 4)
        label.set_line_wrap(True)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        textview = gtk.TextView()

        self._error_details_text_buffer = textview.get_buffer()
        self._reset_error_details_text_buffer()
            
        sw.add(textview)
        sw.show()
        textview.show()

        sw_frame = gtk.Frame()
        sw_frame.add(sw)
        
        reset = gtk.Button("Reset")
        reset.connect('clicked', self._reset_error_details_text_buffer)
        clear = gtk.Button("Clear")
        clear.connect('clicked', self._clear_error_details_text_buffer)

        button_box = gtk.HButtonBox()
        button_box.set_border_width(6)
        button_box.set_spacing(6)
        button_box.set_layout(gtk.BUTTONBOX_END)

        button_box.pack_end(reset,False,False)
        button_box.pack_end(clear,False,False)

        error_details_box = gtk.VBox()
        error_details_box.pack_start(label,False,False)
        error_details_box.pack_start(sw_frame,True,True)
        error_details_box.pack_start(button_box,False,False)

        error_details_align = gtk.Alignment(0,0,1,1)
        error_details_align.set_padding(0,0,11,0)
        error_details_align.add(error_details_box)
        
        error_details_frame = gtk.Frame()
        error_details_frame.set_border_width(3)
        error_details_frame.set_label("<b>%s</b>" % _("Error Details"))
        error_details_frame.get_label_widget().set_use_markup(True)

        error_details_frame.add(error_details_align)

        side_label = gtk.Label(_("This is the detailed Gramps error information, don't worry if you "\
                                 "do not understand it. You "\
                                 "will have the opportunity to add further detail about the error "\
                                 "in the following pages of the assistant."))

        side_label.set_line_wrap(True)
        side_label.set_size_request(124, -1)

        box = gtk.HBox()

        box.pack_start(side_label,False,False,5)

        box.pack_start(error_details_frame)
        box.show_all()

        return box

    def build_page2(self):
        label = gtk.Label(_("Please check the information below and correct anything that "\
                            "you know to be wrong or remove anything that you would rather not "\
                            "have included in the bug report."))
        label.set_alignment(0.01,0.5)
        label.set_padding(0, 4)
        label.set_line_wrap(True)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        textview = gtk.TextView()

        self._sys_information_text_buffer = textview.get_buffer()
        self._reset_sys_information_text_buffer()

        sw.add(textview)
        sw.show()
        textview.show()

        sw_frame = gtk.Frame()
        sw_frame.add(sw)
        
        reset = gtk.Button("Reset")
        reset.connect('clicked', self._reset_sys_information_text_buffer)
        clear = gtk.Button("Clear")
        clear.connect('clicked', self._clear_sys_information_text_buffer)


        button_box = gtk.HButtonBox()
        button_box.set_border_width(6)
        button_box.set_spacing(6)
        button_box.set_layout(gtk.BUTTONBOX_END)

        button_box.pack_end(reset,False,False)
        button_box.pack_end(clear,False,False)

        sys_information_box = gtk.VBox()
        sys_information_box.pack_start(label,False,False)
        sys_information_box.pack_start(sw_frame,True,True)
        sys_information_box.pack_start(button_box,False,False)

        sys_information_align = gtk.Alignment(0,0,1,1)
        sys_information_align.set_padding(0,0,11,0)
        sys_information_align.add(sys_information_box)
        
        sys_information_frame = gtk.Frame()
        sys_information_frame.set_border_width(3)
        sys_information_frame.set_label("<b>%s</b>" % _("System Information"))
        sys_information_frame.get_label_widget().set_use_markup(True)

        sys_information_frame.add(sys_information_align)

        side_label = gtk.Label(_("This is the information about your system that "\
                                 "will help the developers to fix the bug."))

        side_label.set_line_wrap(True)
        side_label.set_size_request(124, -1)

        box = gtk.HBox()

        box.pack_start(side_label,False,False,5)

        box.pack_start(sys_information_frame)
        box.show_all()

        return box

    def build_page3(self):
        label = gtk.Label(_("Please provide as much information as you can "\
                             "about what you were doing when the error occured. "))
        label.set_alignment(0.01,0.5)
        label.set_padding(0, 4)
        label.set_line_wrap(True)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        textview = gtk.TextView()

        self._user_information_text_buffer = textview.get_buffer()

        sw.add(textview)
        sw.show()
        textview.show()

        sw_frame = gtk.Frame()
        sw_frame.add(sw)
        
        clear = gtk.Button("Clear")
        clear.connect('clicked',self._clear_user_information_text_buffer)

        button_box = gtk.HButtonBox()
        button_box.set_border_width(6)
        button_box.set_spacing(6)
        button_box.set_layout(gtk.BUTTONBOX_END)

        button_box.pack_end(clear,False,False)

        user_information_box = gtk.VBox()
        user_information_box.pack_start(label,False,False)
        user_information_box.pack_start(sw_frame,True,True)
        user_information_box.pack_start(button_box,False,False)

        user_information_align = gtk.Alignment(0,0,1,1)
        user_information_align.set_padding(0,0,11,0)
        user_information_align.add(user_information_box)
        
        user_information_frame = gtk.Frame()
        user_information_frame.set_border_width(3)
        user_information_frame.set_label("<b>%s</b>" % _("Further Information"))
        user_information_frame.get_label_widget().set_use_markup(True)

        user_information_frame.add(user_information_align)

        side_label = gtk.Label(_("This is your opportunity to describe what you were "\
                                 "doing when the error occured."))

        side_label.set_line_wrap(True)
        side_label.set_size_request(124, -1)

        box = gtk.HBox()

        box.pack_start(side_label,False,False,5)

        box.pack_start(user_information_frame)
        box.show_all()

        return box


    def build_page4(self):
        label = gtk.Label(_("Please check that the information is correct, do not worry if you "\
                            "don't understand the detail of the error information. Just make sure "\
                            "that it does not contain anything that you do not want to be sent "\
                            "to the developers."))
        label.set_alignment(0.01,0.5)
        label.set_padding(0, 4)
        label.set_line_wrap(True)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        textview = gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)

        self._final_report_text_buffer = textview.get_buffer()        

        sw.add(textview)
        sw.show()
        textview.show()

        sw_frame = gtk.Frame()
        sw_frame.add(sw)
        
        summary_box = gtk.VBox()
        summary_box.pack_start(label,False,False)
        summary_box.pack_start(sw_frame,True,True)

        summary_align = gtk.Alignment(0,0,1,1)
        summary_align.set_padding(0,0,11,0)
        summary_align.add(summary_box)
        
        summary_frame = gtk.Frame()
        summary_frame.set_border_width(3)
        summary_frame.set_label("<b>%s</b>" % _("Bug Report Summary"))
        summary_frame.get_label_widget().set_use_markup(True)

        summary_frame.add(summary_align)

        side_label = gtk.Label(_("This is the completed bug report. The next page "\
                                 "of the assistant will help you to send the report "\
                                 "to the bug report mailing list."))

        side_label.set_line_wrap(True)
        side_label.set_size_request(124, -1)

        box = gtk.HBox()

        box.pack_start(side_label,False,False,5)

        box.pack_start(summary_frame)
        box.show_all()

        return box

    def build_page5(self):
        label = gtk.Label(
            "%s <i>%s</i>" %
            (_("Use one of the two methods below to send the "\
               "bug report to the Gramps bug reporting mailing "\
               "list at "),
             "gramps-bugs@lists.sourceforge.net."))
        label.set_alignment(0.01,0.5)
        label.set_padding(0, 4)
        label.set_line_wrap(True)
        label.set_use_markup(True)


        url_label = gtk.Label(_("If your email client is configured correctly you may be able "\
                                "to use this button to start it with the bug report ready to send. "\
                                "(This will probably only work if you are running Gnome)"))
        url_label.set_alignment(0.01,0.5)
        url_label.set_padding(0, 4)
        url_label.set_line_wrap(True)

        url_button = gtk.Button("Start email client")
        url_button.connect('clicked', self._start_email_client)
        url_button_vbox = gtk.VBox()
        url_button_vbox.pack_start(url_button,True,False)
        
        url_box = gtk.HBox()
        url_box.pack_start(url_label,True,True)
        url_box.pack_start(url_button_vbox,False,False)


        url_align = gtk.Alignment(0,0,1,1)
        url_align.set_padding(0,0,11,0)
        url_align.add(url_box)

        url_frame = gtk.Frame()
        url_frame.add(url_align)
        
        clip_label = gtk.Label(_("If your email program fails to start you can use this button "
                                 "to copy the bug report onto the clipboard. Then start your "
                                 "email client, paste the report and send it to the address "
                                 "above."))
        clip_label.set_alignment(0.01,0.5)
        clip_label.set_padding(0, 4)
        clip_label.set_line_wrap(True)

        clip_button = gtk.Button("Copy to clipboard")
        clip_button.connect('clicked', self._copy_to_clipboard)
        clip_button_vbox = gtk.VBox()
        clip_button_vbox.pack_start(clip_button,True,False)
        
        clip_box = gtk.HBox()
        clip_box.pack_start(clip_label,True,True)
        clip_box.pack_start(clip_button_vbox,False,False)


        clip_align = gtk.Alignment(0,0,1,1)
        clip_align.set_padding(0,0,11,0)
        clip_align.add(clip_box)

        clip_frame = gtk.Frame()
        clip_frame.add(clip_align)
        

        inner_box = gtk.VBox()
        inner_box.pack_start(label,False,False)
        inner_box.pack_start(url_frame,False,False)
        inner_box.pack_start(clip_frame,False,False)

        inner_align = gtk.Alignment(0,0,1,1)
        inner_align.set_padding(0,0,11,0)
        inner_align.add(inner_box)
        
        outer_frame = gtk.Frame()
        outer_frame.set_border_width(3)
        outer_frame.set_label("<b>%s</b>" % _("Send Bug Report"))
        outer_frame.get_label_widget().set_use_markup(True)

        outer_frame.add(inner_align)

        side_label = gtk.Label(_("This is the final step. Use the buttons on this "
                                 "page to transfer the bug report to your email client."))

        side_label.set_line_wrap(True)
        side_label.set_size_request(124, -1)

        box = gtk.HBox()

        box.pack_start(side_label,False,False,5)

        box.pack_start(outer_frame)
        box.show_all()

        return box


    def page4_update(self):

        self._final_report_text_buffer.set_text(
            "User Information: \n" +
            "===================\n\n" +
            self._user_information_text_buffer.get_text(
              self._user_information_text_buffer.get_start_iter(),
              self._user_information_text_buffer.get_end_iter()) +

            "\n\n\nError Details: \n" +
            "===================\n\n" +

            self._error_details_text_buffer.get_text(
              self._error_details_text_buffer.get_start_iter(),
              self._error_details_text_buffer.get_end_iter()) +

            "\n\nSystem Information: \n" +
            "===================\n\n" +

            self._sys_information_text_buffer.get_text(
              self._sys_information_text_buffer.get_start_iter(),
              self._sys_information_text_buffer.get_end_iter())             
            )
