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

import libglade
import gtk
import utils
import ListColors
import const

from TextDoc import *

class StyleListDisplay:
    def __init__(self,stylesheetlist,callback,object):
        self.object = object
        self.callback = callback
        
        self.sheetlist = stylesheetlist
        self.top = libglade.GladeXML(const.stylesFile,"styles")
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_list_select_row" : on_list_select_row,
            "on_ok_clicked" : on_ok_clicked,
            "on_add_clicked" : on_add_clicked,
            "on_edit_clicked" : on_edit_clicked
            })
        self.list = self.top.get_widget("list")
        self.dialog = self.top.get_widget("styles")
        self.dialog.set_data("o",self)
        self.redraw()

    def redraw(self):
        self.list.clear()

        self.list.set_data("i",0)
        box = ListColors.ColorList(self.list,1)
        box.add_with_data(["default"],("default",self.sheetlist.get_style_sheet("default")))

        for style in self.sheetlist.get_style_names():
            if style == "default":
                continue
            box.add_with_data([style],(style,self.sheetlist.get_style_sheet(style)))

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_add_clicked(obj):
    top = obj.get_data("o")

    style = top.sheetlist.get_style_sheet("default")
    x = StyleEditor("New Style",style,top)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_ok_clicked(obj):
    top = obj.get_data("o")

    top.callback(top.object)
    top.sheetlist.save()
    utils.destroy_passed_object(obj)
    

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_list_select_row(obj,row,a,b):
    list = obj.get_data("o").list
    list.set_data("i",row)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_edit_clicked(obj):
    top = obj.get_data("o")

    index = top.list.get_data("i")
    (name,style) = top.list.get_row_data(index)
    x = StyleEditor(name,style,top)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class StyleEditor:
    def __init__(self,name,style,parent):
        self.original_style = style
        self.style = StyleSheet(style)
        self.parent = parent
        self.top = libglade.GladeXML(const.stylesFile,"editor")
        self.current_p = None
        
        self.top.signal_autoconnect({
            "on_save_style_clicked" : on_save_style_clicked,
            "destroy_passed_object" : utils.destroy_passed_object
            })

        self.window = self.top.get_widget("editor")
        self.window.set_data("obj",self)
        self.pnames = self.top.get_widget("name")

        self.top.get_widget("style_name").set_text(name)
        myMenu = gtk.GtkMenu()
        first = 0
        for p_name in self.style.get_names():
            p = self.style.get_style(p_name)
            if first == 0:
                self.draw(p)
                first = 1
            menuitem = gtk.GtkMenuItem(p_name)
            menuitem.set_data("o",p)
            menuitem.set_data("t",self)
            menuitem.connect("activate",change_display)
            menuitem.show()
            myMenu.append(menuitem)
        self.pnames.set_menu(myMenu)

    def draw(self,p):
        self.current_p = p
        font = p.get_font()
        self.top.get_widget("size").set_value(font.get_size())
        if font.get_type_face() == FONT_SANS_SERIF:
            self.top.get_widget("roman").set_active(1)
        else:
            self.top.get_widget("swiss").set_active(1)
        self.top.get_widget("bold").set_active(font.get_bold())
        self.top.get_widget("italic").set_active(font.get_italic())
        self.top.get_widget("underline").set_active(font.get_underline())
        if p.get_alignment() == PARA_ALIGN_LEFT:
            self.top.get_widget("lalign").set_active(1)
        elif p.get_alignment() == PARA_ALIGN_RIGHT:
            self.top.get_widget("ralign").set_active(1)
        elif p.get_alignment() == PARA_ALIGN_CENTER:
            self.top.get_widget("calign").set_active(1)
        else:
            self.top.get_widget("jalign").set_active(1)
        self.top.get_widget("rmargin").set_text(str(p.get_right_margin()))
        self.top.get_widget("lmargin").set_text(str(p.get_left_margin()))
        self.top.get_widget("pad").set_text(str(p.get_padding()))
        self.top.get_widget("tborder").set_active(p.get_top_border())
        self.top.get_widget("lborder").set_active(p.get_left_border())
        self.top.get_widget("rborder").set_active(p.get_right_border())
        self.top.get_widget("bborder").set_active(p.get_bottom_border())
        c = font.get_color()
        self.top.get_widget("color").set_i8(c[0],c[1],c[2],0)
        c = p.get_background_color()
        self.top.get_widget("bgcolor").set_i8(c[0],c[1],c[2],0)

    def save_paragraph(self,p):
        font = p.get_font()
        font.set_size(int(self.top.get_widget("size").get_value()))
    
        if self.top.get_widget("roman").get_active():
            font.set_type_face(FONT_SANS_SERIF)
        else:
            font.set_type_face(FONT_SERIF)

        font.set_bold(self.top.get_widget("bold").get_active())
        font.set_italic(self.top.get_widget("italic").get_active())
        font.set_underline(self.top.get_widget("underline").get_active())
        if self.top.get_widget("lalign").get_active():
            p.set_alignment(PARA_ALIGN_LEFT)
        elif self.top.get_widget("ralign").get_active():
            p.set_alignment(PARA_ALIGN_RIGHT)
        elif self.top.get_widget("calign").get_active():
            p.set_alignment(PARA_ALIGN_CENTER)            
        else:
            p.set_alignment(PARA_ALIGN_JUSTIFY)            

        p.set_right_margin(utils.txt2fl(self.top.get_widget("rmargin").get_text()))
        p.set_left_margin(utils.txt2fl(self.top.get_widget("lmargin").get_text()))
        p.set_padding(utils.txt2fl(self.top.get_widget("pad").get_text()))
        p.set_top_border(self.top.get_widget("tborder").get_active())
        p.set_left_border(self.top.get_widget("lborder").get_active())
        p.set_right_border(self.top.get_widget("rborder").get_active())
        p.set_bottom_border(self.top.get_widget("bborder").get_active())

        c = self.top.get_widget("color").get_i8()
        font.set_color((c[0],c[1],c[2]))
        c = self.top.get_widget("bgcolor").get_i8()
        p.set_background_color((c[0],c[1],c[2]))

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def change_display(obj):
    top = obj.get_data("t")
    style = obj.get_data("o")
    p = top.current_p

    top.save_paragraph(p)
    top.draw(style)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def on_save_style_clicked(obj):
    top = obj.get_data("obj")
    p = top.current_p
    name = top.top.get_widget("style_name").get_text()

    top.save_paragraph(p)
    top.parent.sheetlist.set_style_sheet(name,top.style)
    top.parent.redraw()
    utils.destroy_passed_object(obj)
    


