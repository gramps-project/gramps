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

        response = self.top.run()
        if response == gtk.RESPONSE_ACCEPT:
            task()
        self.top.destroy()

class OptionDialog:
    def __init__(self,msg1,msg2,label1,task1,label2,task2):
        self.xml = gtk.glade.XML(const.errdialogsFile,"optiondialog")
        self.top = self.xml.get_widget('optiondialog')
        self.top.set_title('')

        label1 = self.xml.get_widget('label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        
        label2 = self.xml.get_widget('label2')
        label2.set_text(msg2)
        label2.set_use_markup(gtk.TRUE)

        response = self.top.run()
        if response == gtk.RESPONSE_NO:
            task1()
        else:
            task2()
        self.top.destroy()

class ErrorDialog:
    def __init__(self,msg1,msg2=""):
        
        self.xml = gtk.glade.XML(const.errdialogsFile,"errdialog")
        self.top = self.xml.get_widget('errdialog')
        
        label1 = self.xml.get_widget('label1')
        label2 = self.xml.get_widget('label2')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(gtk.TRUE)
        label2.set_text(msg2)
        self.top.run()
        self.top.destroy()

class WarningDialog:
    def __init__(self,msg):
        title = '%s - GRAMPS' % _('Warning')
        
        self.top = gtk.Dialog()
        self.top.set_title(title)
        label = gtk.Label(msg)
        label.show()
        hbox = gtk.HBox()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DIALOG_WARNING,gtk.ICON_SIZE_DIALOG)
        hbox.set_spacing(10)
        hbox.pack_start(image)
        hbox.add(label)
        self.top.vbox.pack_start(hbox)
        self.top.set_default_size(300,150)
        self.top.add_button(gtk.STOCK_OK,0)
        self.top.set_response_sensitive(0,gtk.TRUE)
        self.top.show_all()
        self.top.run()
        self.top.destroy()

class OkDialog:
    def __init__(self,msg):
        title = '%s - GRAMPS' % _('Error')
        
        self.top = gtk.Dialog()
        self.top.set_title(title)
        label = gtk.Label(msg)
        label.show()
        hbox = gtk.HBox()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DIALOG_INFO,gtk.ICON_SIZE_DIALOG)
        hbox.set_spacing(10)
        hbox.pack_start(image)
        hbox.add(label)
        self.top.vbox.pack_start(hbox)
        self.top.set_default_size(300,150)
        self.top.add_button(gtk.STOCK_OK,0)
        self.top.set_response_sensitive(0,gtk.TRUE)
        self.top.show_all()
        self.top.run()
        self.top.destroy()
        
