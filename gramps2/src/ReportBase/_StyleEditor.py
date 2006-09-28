#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

"""
Paragraph/Font style editor
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
import logging
log = logging.getLogger(".")

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk
from gtk.gdk import Color

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
import const
import BaseDoc
import ListModel
import ManagedWindow

#------------------------------------------------------------------------
#
# StyleList class
#
#------------------------------------------------------------------------
class StyleListDisplay:
    """
    Shows the available paragraph/font styles. Allows the user to select,
    add, edit, and delete styles from a StyleSheet.
    """

    def __init__(self,stylesheetlist,callback,parent_window):
        """
        Creates a StyleListDisplay object that displays the styles in the
        StyleSheet.

        stylesheetlist - styles that can be editied
        callback - task called with an object has been added.
        """
        self.callback = callback
        
        self.sheetlist = stylesheetlist
        self.top = gtk.glade.XML(const.gladeFile,"styles","gramps")
        self.window = self.top.get_widget('styles')

        ManagedWindow.set_titles( self.window,
                                  self.top.get_widget('title'),
                                  _('Document Styles')         )
                                             
        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_add_clicked" : self.on_add_clicked,
            "on_delete_clicked" : self.on_delete_clicked,
            "on_button_press" : self.on_button_press,
            "on_edit_clicked" : self.on_edit_clicked
            })

        title_label = self.top.get_widget('title')
        title_label.set_text(Utils.title(_('Style Editor')))
        title_label.set_use_markup(True)
        
        self.list = ListModel.ListModel(self.top.get_widget("list"),
                                        [('Style',-1,10)],)
        self.redraw()
        if parent_window:
            self.window.set_transient_for(parent_window)
        self.window.run()
        self.window.destroy()

    def redraw(self):
        """Redraws the list of styles that are current available"""
        
        self.list.model.clear()
        self.list.add(["default"])

        index = 1
        for style in self.sheetlist.get_style_names():
            if style == "default":
                continue
            self.list.add([style])
            index = index + 1

    def on_add_clicked(self,obj):
        """Called with the ADD button is clicked. Invokes the StyleEditor to
        create a new style"""
        style = self.sheetlist.get_style_sheet("default")
        StyleEditor("New Style",style,self)

    def on_ok_clicked(self,obj):
        """Called with the OK button is clicked; Calls the callback task,
        then saves the stylesheet."""
        self.callback()
        try:
            self.sheetlist.save()
        except IOError,msg:
            from QuestionDialog import ErrorDialog
            ErrorDialog(_("Error saving stylesheet"),str(msg))
        except:
            log.error("Failed to save stylesheet",exc_info=True)

    def on_button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_edit_clicked(obj)
            
    def on_edit_clicked(self,obj):
        """
        Called with the EDIT button is clicked.
        Calls the StyleEditor to edit the selected style.
        """
        store,node = self.list.selection.get_selected()
        if not node:
            return
        
        name = self.list.model.get_value(node,0)
        style = self.sheetlist.get_style_sheet(name)
        StyleEditor(name,style,self)

    def on_delete_clicked(self,obj):
        """Deletes the selected style."""
        store,node = self.list.selection.get_selected()
        if not node:
            return
        name = self.list.model.get_value(node,0)
        self.sheetlist.delete_style_sheet(name)
        self.redraw()

#------------------------------------------------------------------------
#
# StyleEditor class
#
#------------------------------------------------------------------------
class StyleEditor:
    """
    Edits the current style definition. Presents a dialog allowing the values
    of the paragraphs in the style to be altered.
    """
    
    def __init__(self,name,style,parent):
        """
        Creates the StyleEditor.

        name - name of the style that is to be edited
        style - style object that is to be edited
        parent - StyleListDisplay object that called the editor
        """
        
        self.original_style = style
        self.style = BaseDoc.StyleSheet(style)
        self.parent = parent
        self.top = gtk.glade.XML(const.gladeFile,"editor","gramps")
        
        self.top.signal_autoconnect({
            "on_save_style_clicked" : self.on_save_style_clicked,
            "destroy_passed_object" : Utils.destroy_passed_object
            })

        self.window = self.top.get_widget("editor")
        self.pname = self.top.get_widget('pname')
        self.pdescription = self.top.get_widget('pdescription')
        
        ManagedWindow.set_titles( self.window, 
                                  self.top.get_widget('title'),
                                  _('Style editor'))

        self.first = 1
        
        titles = [(_('Paragraph'),0,130)]
        self.plist = ListModel.ListModel(self.top.get_widget("ptree"),titles,
                                         self.change_display)

        self.top.get_widget('color').connect('color-set',self.fg_color_set)
        self.top.get_widget('bgcolor').connect('color-set',self.bg_color_set)
        self.top.get_widget("style_name").set_text(name)

        names = self.style.get_names()
        names.reverse()
        for p_name in names:
            self.plist.add([p_name],self.style.get_style(p_name))
        self.plist.select_row(0)
        
        if self.parent:
            self.window.set_transient_for(parent.window)
        self.window.run()
        self.window.destroy()

    def draw(self,name,p):
        """Updates the display with the selected paragraph."""
        
        self.current_p = p

        self.pname.set_text('<span size="larger" weight="bold">%s</span>' % name)
        self.pname.set_use_markup(True)

        descr = p.get_description()
        if descr:
            self.pdescription.set_text(descr)
        else:
            self.pdescription.set_text(_("No description available"))
        
        font = p.get_font()
        self.top.get_widget("size").set_value(font.get_size())
        if font.get_type_face() == BaseDoc.FONT_SERIF:
            self.top.get_widget("roman").set_active(1)
        else:
            self.top.get_widget("swiss").set_active(1)
        self.top.get_widget("bold").set_active(font.get_bold())
        self.top.get_widget("italic").set_active(font.get_italic())
        self.top.get_widget("underline").set_active(font.get_underline())
        if p.get_alignment() == BaseDoc.PARA_ALIGN_LEFT:
            self.top.get_widget("lalign").set_active(1)
        elif p.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
            self.top.get_widget("ralign").set_active(1)
        elif p.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
            self.top.get_widget("calign").set_active(1)
        else:
            self.top.get_widget("jalign").set_active(1)
        self.top.get_widget("rmargin").set_value(p.get_right_margin())
        self.top.get_widget("lmargin").set_value(p.get_left_margin())
        self.top.get_widget("pad").set_value(p.get_padding())
        self.top.get_widget("tmargin").set_value(p.get_top_margin())
        self.top.get_widget("bmargin").set_value(p.get_bottom_margin())
        self.top.get_widget("indent").set_value(p.get_first_indent())
        self.top.get_widget("tborder").set_active(p.get_top_border())
        self.top.get_widget("lborder").set_active(p.get_left_border())
        self.top.get_widget("rborder").set_active(p.get_right_border())
        self.top.get_widget("bborder").set_active(p.get_bottom_border())

        self.fg_color = font.get_color()
        c = Color(self.fg_color[0],self.fg_color[1],self.fg_color[2])
        self.top.get_widget("color").set_color(c)
        self.top.get_widget('color_code').set_text("#%02X%02X%02X" % self.fg_color)

        self.bg_color = p.get_background_color()
        c = Color(self.bg_color[0],self.bg_color[1],self.bg_color[2])
        self.top.get_widget("bgcolor").set_color(c)
        self.top.get_widget('bgcolor_code').set_text("#%02X%02X%02X" % self.bg_color)

    def bg_color_set(self,x):
        c = x.get_color()
        self.bg_color = (c.red >> 8, c.green >> 8, c.blue >> 8)
        self.top.get_widget('bgcolor_code').set_text("#%02X%02X%02X" % self.bg_color)

    def fg_color_set(self,x):
        c = x.get_color()
        self.fg_color = (c.red >> 8, c.green >> 8, c.blue >> 8)
        self.top.get_widget('color_code').set_text("#%02X%02X%02X" % self.fg_color)
        
    def save_paragraph(self,p):
        """Saves the current paragraph displayed on the dialog"""
        
        font = p.get_font()
        font.set_size(self.top.get_widget("size").get_value_as_int())
    
        if self.top.get_widget("roman").get_active():
            font.set_type_face(BaseDoc.FONT_SERIF)
        else:
            font.set_type_face(BaseDoc.FONT_SANS_SERIF)

        font.set_bold(self.top.get_widget("bold").get_active())
        font.set_italic(self.top.get_widget("italic").get_active())
        font.set_underline(self.top.get_widget("underline").get_active())
        if self.top.get_widget("lalign").get_active():
            p.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        elif self.top.get_widget("ralign").get_active():
            p.set_alignment(BaseDoc.PARA_ALIGN_RIGHT)
        elif self.top.get_widget("calign").get_active():
            p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)            
        else:
            p.set_alignment(BaseDoc.PARA_ALIGN_JUSTIFY)            

        p.set_right_margin(self.top.get_widget("rmargin").get_value())
        p.set_left_margin(self.top.get_widget("lmargin").get_value())
        p.set_top_margin(self.top.get_widget("tmargin").get_value())
        p.set_bottom_margin(self.top.get_widget("bmargin").get_value())
        p.set_padding(self.top.get_widget("pad").get_value())
        p.set_first_indent(self.top.get_widget("indent").get_value())
        p.set_top_border(self.top.get_widget("tborder").get_active())
        p.set_left_border(self.top.get_widget("lborder").get_active())
        p.set_right_border(self.top.get_widget("rborder").get_active())
        p.set_bottom_border(self.top.get_widget("bborder").get_active())

        font.set_color(self.fg_color)
        p.set_background_color(self.bg_color)

    def on_save_style_clicked(self,obj):
        """
        Saves the current style sheet and causes the parent to be updated with
        the changes.
        """
        p = self.current_p
        name = unicode(self.top.get_widget("style_name").get_text())

        self.save_paragraph(p)
        self.style.set_name(name)
        self.parent.sheetlist.set_style_sheet(name,self.style)
        self.parent.redraw()
        Utils.destroy_passed_object(obj)

    def change_display(self,obj):
        """Called when the paragraph selection has been changed. Saves the
        old paragraph, then draws the newly selected paragraph"""

        objs = self.plist.get_selected_objects()
        store,node = self.plist.get_selected()
        name = store.get_value(node,0)
        if self.first == 0:
            self.save_paragraph(self.current_p)
        else:
            self.first = 0
        self.current_p = objs[0]
        self.draw(name,self.current_p)
