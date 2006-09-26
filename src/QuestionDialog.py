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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME/GTK+ modules
#
#-------------------------------------------------------------------------
import gtk
from gtk.gdk import pixbuf_new_from_file

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
import Config

try:
    ICON = pixbuf_new_from_file(const.icon)
except:
    ICON = None

class SaveDialog:
    def __init__(self,msg1,msg2,task1,task2,parent=None):
        self.xml = gtk.glade.XML(const.gladeFile,"savedialog","gramps")
        self.top = self.xml.get_widget('savedialog')
        self.top.set_icon(ICON)
        self.dontask = self.xml.get_widget('dontask')
        self.task1 = task1
        self.task2 = task2
        
        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)
        self.top.show()
        if parent:
            self.top.set_transient_for(parent)
        response = self.top.run()
        if response == gtk.RESPONSE_NO:
            self.task1()
        elif response == gtk.RESPONSE_YES:
            self.task2()

        Config.set(Config.DONT_ASK,self.dontask.get_active())
        self.top.destroy()

class QuestionDialog:
    def __init__(self,msg1,msg2,label,task,parent=None):
        self.xml = gtk.glade.XML(const.gladeFile,"questiondialog","gramps")
        self.top = self.xml.get_widget('questiondialog')
        self.top.set_icon(ICON)
        self.top.set_title('')

        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_widget('okbutton').set_label(label)

        self.top.show()
        if parent:
            self.top.set_transient_for(parent)
        response = self.top.run()
        if response == gtk.RESPONSE_ACCEPT:
            task()
        self.top.destroy()

class QuestionDialog2:
    def __init__(self,msg1,msg2,label_msg1,label_msg2,parent=None):
        self.xml = gtk.glade.XML(const.gladeFile,"questiondialog","gramps")
        self.top = self.xml.get_widget('questiondialog')
        self.top.set_icon(ICON)
        self.top.set_title('')

        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_widget('okbutton').set_label(label_msg1)
        self.xml.get_widget('okbutton').set_use_underline(True)
        self.xml.get_widget('no').set_label(label_msg2)
        self.xml.get_widget('no').set_use_underline(True)
        self.top.show()
        if parent:
            self.top.set_transient_for(parent)

    def run(self):
        response = self.top.run()
        self.top.destroy()
        return (response == gtk.RESPONSE_ACCEPT)

class OptionDialog:
    def __init__(self,msg1,msg2,btnmsg1,task1,btnmsg2,task2,parent=None):
        self.xml = gtk.glade.XML(const.gladeFile,"optiondialog","gramps")
        self.top = self.xml.get_widget('optiondialog')
        self.top.set_icon(ICON)
        self.top.set_title('')

        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_widget('option1').set_label(btnmsg1)
        self.xml.get_widget('option2').set_label(btnmsg2)
        self.top.show()
        if parent:
            self.top.set_transient_for(parent)
        self.response = self.top.run()
        if self.response == gtk.RESPONSE_NO:
            if task1:
                task1()
        else:
            if task2:
                task2()
        self.top.destroy()

    def get_response(self):
        return self.response

class ErrorDialog(gtk.MessageDialog):
    def __init__(self,msg1,msg2="",parent=None):
        
        gtk.MessageDialog.__init__(self, parent,
                                   flags=gtk.DIALOG_MODAL,
                                   type=gtk.MESSAGE_ERROR,
                                   buttons=gtk.BUTTONS_CLOSE)
        self.set_markup('<span weight="bold" size="larger">%s</span>' % msg1)
        self.format_secondary_text(msg2)
        self.set_icon(ICON)
        self.show()
        self.run()
        self.destroy()

class WarningDialog(gtk.MessageDialog):
    def __init__(self,msg1,msg2="",parent=None):

        gtk.MessageDialog.__init__(self, parent,
                                   flags=gtk.DIALOG_MODAL,
                                   type=gtk.MESSAGE_WARNING,
                                   buttons=gtk.BUTTONS_CLOSE)
        self.set_markup('<span weight="bold" size="larger">%s</span>' % msg1)
        self.format_secondary_markup(msg2)
        self.set_icon(ICON)
        self.show()
        self.run()
        self.destroy()

class OkDialog(gtk.MessageDialog):
    def __init__(self,msg1,msg2="",parent=None):

        gtk.MessageDialog.__init__(self, parent,
                                   flags=gtk.DIALOG_MODAL,
                                   type=gtk.MESSAGE_INFO,
                                   buttons=gtk.BUTTONS_CLOSE)
        self.set_markup('<span weight="bold" size="larger">%s</span>' % msg1)
        self.format_secondary_text(msg2)
        self.set_icon(ICON)
        self.show()
        self.run()
        self.destroy()

class MissingMediaDialog:
    def __init__(self,msg1,msg2,task1,task2,task3,parent=None):
        self.xml = gtk.glade.XML(const.gladeFile,"missmediadialog","gramps")
        self.top = self.xml.get_widget('missmediadialog')
        self.top.set_icon(ICON)

        self.task1 = task1
        self.task2 = task2
        self.task3 = task3
        
        label1 = self.xml.get_widget('label4')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        
        label2 = self.xml.get_widget('label3')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        check_button = self.xml.get_widget('use_always')

        self.top.show()
        if parent:
            self.top.set_transient_for(parent)
        self.top.connect('delete_event',self.warn)
        response = gtk.RESPONSE_DELETE_EVENT

        # Need some magic here, because an attempt to close the dialog
        # with the X button not only emits the 'delete_event' signal
        # but also exits with the RESPONSE_DELETE_EVENT
        while response == gtk.RESPONSE_DELETE_EVENT:
            response = self.top.run()

        if response == 1:
            self.task1()
        elif response == 2:
            self.task2()
        elif response == 3:
            self.task3()
        if check_button.get_active():
            self.default_action = response
        else:
            self.default_action = 0
        self.top.destroy()

    def warn(self,obj,obj2):
        WarningDialog(
            _("Attempt to force closing the dialog"),
            _("Please do not force closing this important dialog.\n"
              "Instead select one of the available options"),
            self.top)
        return True

class MessageHideDialog:
    
    def __init__(self, title, message, key, parent=None):

        glade_xml = gtk.glade.XML(const.gladeFile, "hide_dialog", "gramps")
        top = glade_xml.get_widget('hide_dialog')
        dont_show = glade_xml.get_widget('dont_show')
        dont_show.set_active(Config.get(key))
        title_label = glade_xml.get_widget('title')
        title_label.set_text(
            '<span size="larger" weight="bold">%s</span>' % title)
        title_label.set_use_markup(True)
        
        glade_xml.get_widget('message').set_text(message)
        
        dont_show.connect('toggled',self.update_checkbox, key)
        top.run()
        top.destroy()

    def update_checkbox(self, obj, constant):
        Config.set(constant, obj.get_active())
        Config.sync()
