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

import gnome.ui
import gtk

class QuestionDialog:
    def __init__(self,title,msg,blabel1,task1,blabel2,task2=None):
        title = '%s - GRAMPS' % title
        
        self.top = gnome.ui.GnomeDialog(title,blabel1,blabel2)
        label = gtk.GtkLabel(msg)
        label.show()
        self.top.vbox.pack_start(label)
        self.top.set_usize(450,150)
        self.task2 = task2
        self.task1 = task1
        self.top.button_connect(0,self.my_task1)
        self.top.button_connect(1,self.my_task2)
        self.top.set_modal(1)
        self.top.show()

    def my_task1(self,obj):
        if self.task1:
            self.task1()
        self.top.destroy()

    def my_task2(self,obj):
        if self.task2:
            self.task2()
        self.top.destroy()
        

if __name__ == '__main__':
    def task1(obj):
        print obj,'1'

    def task2(obj):
        print obj,'2'
        
    QuestionDialog('mytitle','This is my message','Abc',task1,'Def',task2)

    gtk.mainloop()
