#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

from intl import gettext as _

class SaveDialog:
    def __init__(self,msg1,msg2,task1,task2):
        self.xml = gtk.glade.XML(const.errdialogsFile,"savedialog")
        self.top = self.xml.get_widget('savedialog')
        self.task1 = task1
        self.task2 = task2
        
        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(gtk.TRUE)

        self.top.show()
        response = self.top.run()
        if response == gtk.RESPONSE_NO:
            self.task1()
        elif response == gtk.RESPONSE_YES:
            self.task2()
        self.top.destroy()

class QuestionDialog:
    def __init__(self,msg1,msg2,label,task):
        self.xml = gtk.glade.XML(const.errdialogsFile,"questiondialog")
        self.top = self.xml.get_widget('questiondialog')
        self.top.set_title('')

        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(gtk.TRUE)

        self.xml.get_widget('okbutton').set_label(label)

        self.top.show()
        response = self.top.run()
        if response == gtk.RESPONSE_ACCEPT:
            task()
        self.top.destroy()

class OptionDialog:
    def __init__(self,msg1,msg2,btnmsg1,task1,btnmsg2,task2):
        self.xml = gtk.glade.XML(const.errdialogsFile,"optiondialog")
        self.top = self.xml.get_widget('optiondialog')
        self.top.set_title('')

        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(gtk.TRUE)

        self.xml.get_widget('option1').set_label(btnmsg1)
        self.xml.get_widget('option2').set_label(btnmsg2)
        self.top.show()
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
    def __init__(self,msg1,msg2=""):
        
        self.xml = gtk.glade.XML(const.errdialogsFile,"errdialog")
        self.top = self.xml.get_widget('errdialog')
        
        label1 = self.xml.get_widget('label1')
        label2 = self.xml.get_widget('label2')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        label2.set_text(msg2)
        self.top.show()
        self.top.run()
        self.top.destroy()

class WarningDialog:
    def __init__(self,msg1,msg2=""):
        
        self.xml = gtk.glade.XML(const.errdialogsFile,"warndialog")
        self.top = self.xml.get_widget('warndialog')
        
        label1 = self.xml.get_widget('label1')
        label2 = self.xml.get_widget('label2')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        label2.set_text(msg2)
        self.top.show()
        self.top.run()
        self.top.destroy()

class OkDialog:
    def __init__(self,msg1,msg2=""):

        self.xml = gtk.glade.XML(const.errdialogsFile,"okdialog")
        self.top = self.xml.get_widget('okdialog')

        label1 = self.xml.get_widget('label1')
        label2 = self.xml.get_widget('label2')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        label2.set_text(msg2)
        self.top.show()
        self.top.run()
        self.top.destroy()

        
