#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

import gtk
import gtk.glade
import const
import GrampsKeys

from gettext import gettext as _

class SaveDialog:
    def __init__(self,msg1,msg2,task1,task2,parent=None):
        self.xml = gtk.glade.XML(const.errdialogsFile,"savedialog","gramps")
        self.top = self.xml.get_widget('savedialog')
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

        GrampsKeys.save_dont_ask(self.dontask.get_active())
        self.top.destroy()

class QuestionDialog:
    def __init__(self,msg1,msg2,label,task,parent=None):
        self.xml = gtk.glade.XML(const.errdialogsFile,"questiondialog","gramps")
        self.top = self.xml.get_widget('questiondialog')
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
        self.xml = gtk.glade.XML(const.errdialogsFile,"questiondialog","gramps")
        self.top = self.xml.get_widget('questiondialog')
        self.top.set_title('')

        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_widget('okbutton').set_label(label_msg1)
        self.xml.get_widget('no').set_label(label_msg2)
        self.top.show()
        if parent:
            self.top.set_transient_for(parent)

    def run(self):
        response = self.top.run()
        self.top.destroy()
        return (response == gtk.RESPONSE_ACCEPT)

class OptionDialog:
    def __init__(self,msg1,msg2,btnmsg1,task1,btnmsg2,task2,parent=None):
        self.xml = gtk.glade.XML(const.errdialogsFile,"optiondialog","gramps")
        self.top = self.xml.get_widget('optiondialog')
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

class ErrorDialog:
    def __init__(self,msg1,msg2="",parent=None):
        
        self.xml = gtk.glade.XML(const.errdialogsFile,"errdialog","gramps")
        self.top = self.xml.get_widget('errdialog')
        
        label1 = self.xml.get_widget('label1')
        label2 = self.xml.get_widget('label2')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % str(msg1))
        label1.set_use_markup(True)
        label2.set_text(str(msg2))
        self.top.show()
        if parent:
            self.top.set_transient_for(parent)
        self.top.run()
        self.top.destroy()

class WarningDialog:
    def __init__(self,msg1,msg2="",parent=None):
        
        self.xml = gtk.glade.XML(const.errdialogsFile,"warndialog","gramps")
        self.top = self.xml.get_widget('warndialog')
        
        label1 = self.xml.get_widget('label1')
        label2 = self.xml.get_widget('label2')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        label2.set_text(msg2)
        self.top.show()
        if parent:
            self.top.set_transient_for(parent)
        self.top.run()
        self.top.destroy()

class OkDialog:
    def __init__(self,msg1,msg2="",parent=None):

        self.xml = gtk.glade.XML(const.errdialogsFile,"okdialog","gramps")
        self.top = self.xml.get_widget('okdialog')

        label1 = self.xml.get_widget('label1')
        label2 = self.xml.get_widget('label2')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)
        label2.set_text(msg2)
        self.top.show()
        if parent:
            self.top.set_transient_for(parent)
        self.top.run()
        self.top.destroy()

class MissingMediaDialog:
    def __init__(self,msg1,msg2,task1,task2,task3,parent=None):
        self.xml = gtk.glade.XML(const.errdialogsFile,"missmediadialog","gramps")
        self.top = self.xml.get_widget('missmediadialog')
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
