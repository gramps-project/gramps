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

"""
Paragraph/Font style editor
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import libglade
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
import const
import TextDoc


class StyleListDisplay:
    """
    Shows the available paragraph/font styles. Allows the user to select,
    add, edit, and delete styles from a StyleSheet.
    """

    def __init__(self,stylesheetlist,callback):
        """
        Creates a StyleListDisplay object that displays the styles in the
        StyleSheet.

        stylesheetlist - styles that can be editied
        callback - task called with an object has been added.
        """
        self.callback = callback
        
        self.sheetlist = stylesheetlist
        self.top = libglade.GladeXML(const.stylesFile,"styles")
        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_add_clicked" : self.on_add_clicked,
            "on_delete_clicked" : self.on_delete_clicked,
            "on_edit_clicked" : self.on_edit_clicked
            })
        self.list = self.top.get_widget("list")
        self.dialog = self.top.get_widget("styles")
        self.redraw()

    def redraw(self):
        """Redraws the list of styles that are current available"""
        
        self.list.clear()
        sheet = self.sheetlist.get_style_sheet("default")
        self.list.append(["default"])
        self.list.set_row_data(0,("default",sheet))

        index = 1
        for style in self.sheetlist.get_style_names():
            if style == "default":
                continue
            sheet = self.sheetlist.get_style_sheet(style)
            self.list.append([style])
            self.list.set_row_data(index,(style,sheet))
            index = index + 1

    def on_add_clicked(self,obj):
        """Called with the ADD button is clicked. Invokes the StyleEditor to
        create a new style"""
        style = self.sheetlist.get_style_sheet("default")
        StyleEditor("New Style",style,self)

    def on_ok_clicked(self,obj):
        """Called with the OK button is clicked; Calls the callback task, then
        saves the stylesheet, and destroys the window."""
        self.callback()
        self.sheetlist.save()
        Utils.destroy_passed_object(obj)
    
    def on_edit_clicked(self,obj):
        """
        Called with the EDIT button is clicked. Calls the StyleEditor to edit the
        selected style.
        """
        if len(self.list.selection) > 0:
            (name,style) = self.list.get_row_data(self.list.selection[0])
            StyleEditor(name,style,self)

    def on_delete_clicked(self,obj):
        """Deletes teh selected style."""
        if len(self.list.selection) > 0:
            (name,style) = self.list.get_row_data(self.list.selection[0])
            self.sheetlist.delete_style_sheet(name)
            self.redraw()

class StyleEditor:
    """
    Edits the current style definition. Presents a dialog allowing the values of
    the paragraphs in the style to be altered.
    """
    
    def __init__(self,name,style,parent):
        """
        Creates the StyleEditor.

        name - name of the style that is to be edited
        style - style object that is to be edited
        parent - StyleListDisplay object that called the editor
        """
        
        self.original_style = style
        self.style = TextDoc.StyleSheet(style)
        self.parent = parent
        self.top = libglade.GladeXML(const.stylesFile,"editor")
        self.current_p = None
        
        self.top.signal_autoconnect({
            "on_save_style_clicked" : self.on_save_style_clicked,
            "destroy_passed_object" : Utils.destroy_passed_object
            })

        self.window = self.top.get_widget("editor")
        self.pnames = self.top.get_widget("name")

        # Typing CR selects OK button
        self.window.editable_enters(self.top.get_widget("rmargin"))
        self.window.editable_enters(self.top.get_widget("lmargin"))
        self.window.editable_enters(self.top.get_widget("pad"))

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
            menuitem.connect("activate",self.change_display)
            menuitem.show()
            myMenu.append(menuitem)
        self.pnames.set_menu(myMenu)

    def draw(self,p):
        """Updates the display with the selected paragraph."""
        
        self.current_p = p
        font = p.get_font()
        self.top.get_widget("size").set_value(font.get_size())
        if font.get_type_face() == TextDoc.FONT_SANS_SERIF:
            self.top.get_widget("roman").set_active(1)
        else:
            self.top.get_widget("swiss").set_active(1)
        self.top.get_widget("bold").set_active(font.get_bold())
        self.top.get_widget("italic").set_active(font.get_italic())
        self.top.get_widget("underline").set_active(font.get_underline())
        if p.get_alignment() == TextDoc.PARA_ALIGN_LEFT:
            self.top.get_widget("lalign").set_active(1)
        elif p.get_alignment() == TextDoc.PARA_ALIGN_RIGHT:
            self.top.get_widget("ralign").set_active(1)
        elif p.get_alignment() == TextDoc.PARA_ALIGN_CENTER:
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
        """Saves the current paragraph displayed on the dialog"""
        
        font = p.get_font()
        font.set_size(int(self.top.get_widget("size").get_value()))
    
        if self.top.get_widget("roman").get_active():
            font.set_type_face(TextDoc.FONT_SANS_SERIF)
        else:
            font.set_type_face(TextDoc.FONT_SERIF)

        font.set_bold(self.top.get_widget("bold").get_active())
        font.set_italic(self.top.get_widget("italic").get_active())
        font.set_underline(self.top.get_widget("underline").get_active())
        if self.top.get_widget("lalign").get_active():
            p.set_alignment(TextDoc.PARA_ALIGN_LEFT)
        elif self.top.get_widget("ralign").get_active():
            p.set_alignment(TextDoc.PARA_ALIGN_RIGHT)
        elif self.top.get_widget("calign").get_active():
            p.set_alignment(TextDoc.PARA_ALIGN_CENTER)            
        else:
            p.set_alignment(TextDoc.PARA_ALIGN_JUSTIFY)            

        p.set_right_margin(float(self.top.get_widget("rmargin").get_text()))
        p.set_left_margin(float(self.top.get_widget("lmargin").get_text()))
        p.set_padding(float(self.top.get_widget("pad").get_text()))
        p.set_top_border(self.top.get_widget("tborder").get_active())
        p.set_left_border(self.top.get_widget("lborder").get_active())
        p.set_right_border(self.top.get_widget("rborder").get_active())
        p.set_bottom_border(self.top.get_widget("bborder").get_active())

        c = self.top.get_widget("color").get_i8()
        font.set_color((c[0],c[1],c[2]))
        c = self.top.get_widget("bgcolor").get_i8()
        p.set_background_color((c[0],c[1],c[2]))

    def on_save_style_clicked(self,obj):
        """
        Saves the current style sheet and causes the parent to be updated with
        the changes.
        """
        p = self.current_p
        name = self.top.get_widget("style_name").get_text()

        self.save_paragraph(p)
        self.parent.sheetlist.set_style_sheet(name,self.style)
        self.parent.redraw()
        Utils.destroy_passed_object(obj)

    def change_display(self,obj):
        """Called when the paragraph selection has been changed. Saves the
        old paragraph, then draws the newly selected paragraph"""
        
        style = obj.get_data("o")
        self.save_paragraph(self.current_p)
        self.draw(style)

    


