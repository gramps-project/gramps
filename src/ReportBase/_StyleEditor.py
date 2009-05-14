#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2008       Peter Landgren
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

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from TransUtils import sgettext as _
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
from glade import Glade

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_GLADE_FILE = "styleeditor.glade"

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

    def __init__(self, stylesheetlist, callback, parent_window):
        """
        Create a StyleListDisplay object that displays the styles in the
        StyleSheet.

        stylesheetlist - styles that can be editied
        callback - task called with an object has been added.
        """
        self.callback = callback
        
        self.sheetlist = stylesheetlist
        
        self.top = Glade(toplevel='styles')
        self.window = self.top.toplevel

        ManagedWindow.set_titles( self.window, 
                                  self.top.get_object('title'), 
                                  _('Document Styles')         )
                                             
        self.top.connect_signals({
            "destroy_passed_object" : self.__close, 
            "on_ok_clicked" : self.on_ok_clicked, 
            "on_add_clicked" : self.on_add_clicked, 
            "on_delete_clicked" : self.on_delete_clicked, 
            "on_button_press" : self.on_button_press, 
            "on_edit_clicked" : self.on_edit_clicked
            })

        title_label = self.top.get_object('title')
        title_label.set_text(Utils.title(_('Style Editor')))
        title_label.set_use_markup(True)
        
        self.list = ListModel.ListModel(self.top.get_object("list"), 
                                        [(_('Style'), -1, 10)], )
        self.redraw()
        if parent_window:
            self.window.set_transient_for(parent_window)
        self.window.run()
        self.window.destroy()

    def __close(self, obj):
        self.top.destroy()

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

    def on_add_clicked(self, obj):
        """Called with the ADD button is clicked. Invokes the StyleEditor to
        create a new style"""
        style = self.sheetlist.get_style_sheet("default")
        StyleEditor("New Style", style, self)

    def on_ok_clicked(self, obj):
        """Called with the OK button is clicked; Calls the callback task, 
        then saves the stylesheet."""
        if self.callback is not None:
            self.callback()
        try:
            self.sheetlist.save()
        except IOError, msg:
            from QuestionDialog import ErrorDialog
            ErrorDialog(_("Error saving stylesheet"), str(msg))
        except:
            log.error("Failed to save stylesheet", exc_info=True)

    def on_button_press(self, obj, event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_edit_clicked(obj)
            
    def on_edit_clicked(self, obj):
        """
        Called with the EDIT button is clicked.
        Calls the StyleEditor to edit the selected style.
        """
        store, node = self.list.selection.get_selected()
        if not node:
            return
        
        name = unicode(self.list.model.get_value(node, 0))
        style = self.sheetlist.get_style_sheet(name)
        StyleEditor(name, style, self)

    def on_delete_clicked(self, obj):
        """Deletes the selected style."""
        store, node = self.list.selection.get_selected()
        if not node:
            return
        name = unicode(self.list.model.get_value(node, 0))
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
    
    def __init__(self, name, style, parent):
        """
        Create the StyleEditor.

        name - name of the style that is to be edited
        style - style object that is to be edited
        parent - StyleListDisplay object that called the editor
        """
        self.current_p = None
        self.current_name = None
        
        self.style = BaseDoc.StyleSheet(style)
        self.parent = parent
        self.top = Glade(toplevel='editor')
        self.window = self.top.toplevel
        
        self.top.connect_signals({
            "on_save_style_clicked" : self.on_save_style_clicked, 
            "destroy_passed_object" : self.__close, 
            })

        self.pname = self.top.get_object('pname')
        self.pdescription = self.top.get_object('pdescription')

        ManagedWindow.set_titles( self.window, 
                                  self.top.get_object('title'), 
                                  _('Style editor'))
        self.top.get_object("label6").set_text(_("point size|pt"))
        
        titles = [(_('Paragraph'), 0, 130)]
        self.plist = ListModel.ListModel(self.top.get_object("ptree"), titles, 
                                         self.change_display)

        self.top.get_object('color').connect('color-set', self.fg_color_set)
        self.top.get_object('bgcolor').connect('color-set', self.bg_color_set)
        self.top.get_object("style_name").set_text(name)

        names = self.style.get_paragraph_style_names()
        names.reverse()
        for p_name in names:
            self.plist.add([p_name], self.style.get_paragraph_style(p_name))
        self.plist.select_row(0)
        
        if self.parent:
            self.window.set_transient_for(parent.window)
        self.window.run()
        self.window.destroy()

    def __close(self, obj):
        self.window.destroy()

    def draw(self):
        """Updates the display with the selected paragraph."""

        p = self.current_p
        self.pname.set_text( '<span size="larger" weight="bold">%s</span>' %
                             self.current_name                              )
        self.pname.set_use_markup(True)

        descr = p.get_description()
        self.pdescription.set_text(descr or _("No description available") )
        
        font = p.get_font()
        self.top.get_object("size").set_value(font.get_size())
        if font.get_type_face() == BaseDoc.FONT_SERIF:
            self.top.get_object("roman").set_active(1)
        else:
            self.top.get_object("swiss").set_active(1)
        self.top.get_object("bold").set_active(font.get_bold())
        self.top.get_object("italic").set_active(font.get_italic())
        self.top.get_object("underline").set_active(font.get_underline())
        if p.get_alignment() == BaseDoc.PARA_ALIGN_LEFT:
            self.top.get_object("lalign").set_active(1)
        elif p.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
            self.top.get_object("ralign").set_active(1)
        elif p.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
            self.top.get_object("calign").set_active(1)
        else:
            self.top.get_object("jalign").set_active(1)
        self.top.get_object("rmargin").set_value(p.get_right_margin())
        self.top.get_object("lmargin").set_value(p.get_left_margin())
        self.top.get_object("pad").set_value(p.get_padding())
        self.top.get_object("tmargin").set_value(p.get_top_margin())
        self.top.get_object("bmargin").set_value(p.get_bottom_margin())
        self.top.get_object("indent").set_value(p.get_first_indent())
        self.top.get_object("tborder").set_active(p.get_top_border())
        self.top.get_object("lborder").set_active(p.get_left_border())
        self.top.get_object("rborder").set_active(p.get_right_border())
        self.top.get_object("bborder").set_active(p.get_bottom_border())

        self.fg_color = font.get_color()
        c = Color(self.fg_color[0] << 8, 
                  self.fg_color[1] << 8, 
                  self.fg_color[2] << 8)
        self.top.get_object("color").set_color(c)
        self.top.get_object('color_code').set_text(
                                               "#%02X%02X%02X" % self.fg_color)

        self.bg_color = p.get_background_color()
        c = Color(self.bg_color[0] << 8, 
                  self.bg_color[1] << 8, 
                  self.bg_color[2] << 8)
        self.top.get_object("bgcolor").set_color(c)
        self.top.get_object('bgcolor_code').set_text(
                                                "#%02X%02X%02X" % self.bg_color)

    def bg_color_set(self, x):
        c = x.get_color()
        self.bg_color = (c.red >> 8, c.green >> 8, c.blue >> 8)
        self.top.get_object('bgcolor_code').set_text(
                                                "#%02X%02X%02X" % self.bg_color)

    def fg_color_set(self, x):
        c = x.get_color()
        self.fg_color = (c.red >> 8, c.green >> 8, c.blue >> 8)
        self.top.get_object('color_code').set_text(
                                                "#%02X%02X%02X" % self.fg_color)
        
    def save_paragraph(self):
        """Saves the current paragraph displayed on the dialog"""
        p = self.current_p
        font = p.get_font()
        font.set_size(self.top.get_object("size").get_value_as_int())
    
        if self.top.get_object("roman").get_active():
            font.set_type_face(BaseDoc.FONT_SERIF)
        else:
            font.set_type_face(BaseDoc.FONT_SANS_SERIF)

        font.set_bold(self.top.get_object("bold").get_active())
        font.set_italic(self.top.get_object("italic").get_active())
        font.set_underline(self.top.get_object("underline").get_active())
        if self.top.get_object("lalign").get_active():
            p.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        elif self.top.get_object("ralign").get_active():
            p.set_alignment(BaseDoc.PARA_ALIGN_RIGHT)
        elif self.top.get_object("calign").get_active():
            p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)            
        else:
            p.set_alignment(BaseDoc.PARA_ALIGN_JUSTIFY)            

        p.set_right_margin(self.top.get_object("rmargin").get_value())
        p.set_left_margin(self.top.get_object("lmargin").get_value())
        p.set_top_margin(self.top.get_object("tmargin").get_value())
        p.set_bottom_margin(self.top.get_object("bmargin").get_value())
        p.set_padding(self.top.get_object("pad").get_value())
        p.set_first_indent(self.top.get_object("indent").get_value())
        p.set_top_border(self.top.get_object("tborder").get_active())
        p.set_left_border(self.top.get_object("lborder").get_active())
        p.set_right_border(self.top.get_object("rborder").get_active())
        p.set_bottom_border(self.top.get_object("bborder").get_active())

        font.set_color(self.fg_color)
        p.set_background_color(self.bg_color)
        
        self.style.add_paragraph_style(self.current_name, self.current_p)

    def on_save_style_clicked(self, obj):
        """
        Saves the current style sheet and causes the parent to be updated with
        the changes.
        """
        name = unicode(self.top.get_object("style_name").get_text())

        self.save_paragraph()
        self.style.set_name(name)
        self.parent.sheetlist.set_style_sheet(name, self.style)
        self.parent.redraw()
        self.window.destroy()

    def change_display(self, obj):
        """Called when the paragraph selection has been changed. Saves the
        old paragraph, then draws the newly selected paragraph"""
        # Don't save until current_name is defined
        # If it's defined, save under the current paragraph name
        if self.current_name:
            self.save_paragraph()
        # Then change to new paragraph
        objs = self.plist.get_selected_objects()
        store, node = self.plist.get_selected()
        self.current_name =  store.get_value(node, 0)
        self.current_p = objs[0]
        self.draw()
