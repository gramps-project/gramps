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

try:
    import pygtk; pygtk.require('2.0')
except ImportError: # not set up for parallel install
    pass 

import gtk
import gnome.ui
from intl import gettext as _

class QuestionDialog:
    def __init__(self,title,msg,task1,task2=None):
        title = '%s - GRAMPS' % title
        
        self.top = gtk.Dialog()
        self.top.set_title(title)
        label = gtk.Label(msg)
        label.show()
        hbox = gtk.HBox()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DIALOG_QUESTION,gtk.ICON_SIZE_DIALOG)
        hbox.set_spacing(10)
        hbox.pack_start(image)
        hbox.add(label)
        self.top.vbox.pack_start(hbox)
        self.top.set_default_size(300,150)
        self.task2 = task2
        self.task1 = task1
        self.top.add_button(gtk.STOCK_YES,0)
        self.top.add_button(gtk.STOCK_NO,1)
        self.top.set_response_sensitive(1,gtk.TRUE)
        self.top.set_response_sensitive(0,gtk.TRUE)
        self.top.show_all()
        if self.top.run():
            self.my_task2()
        else:
            self.my_task1()

    def my_task1(self):
        if self.task1:
            self.task1()
        self.top.destroy()

    def my_task2(self):
        if self.task2:
            self.task2()
        self.top.destroy()

class ErrorDialog:
    def __init__(self,msg):
        title = '%s - GRAMPS' % _('Error')
        
        self.top = gtk.Dialog()
        self.top.set_title(title)
        label = gtk.Label(msg)
        label.show()
        hbox = gtk.HBox()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DIALOG_ERROR,gtk.ICON_SIZE_DIALOG)
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
        
