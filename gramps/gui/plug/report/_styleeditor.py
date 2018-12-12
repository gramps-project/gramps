#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2008       Peter Landgren
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012,2017  Paul Franklin
# Copyright (C) 2014       Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Paragraph/Font style editor
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".")
import re

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
from gi.repository import Gtk, Gdk

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.plug.docgen import (StyleSheet, FONT_SERIF, FONT_SANS_SERIF,
            PARA_ALIGN_RIGHT, PARA_ALIGN_CENTER, PARA_ALIGN_LEFT,
            PARA_ALIGN_JUSTIFY, ParagraphStyle, TableStyle, TableCellStyle,
            GraphicsStyle)
from ...listmodel import ListModel
from ...managedwindow import ManagedWindow
from ...glade import Glade
from ...dialog import ErrorDialog
from ...display import display_help
from gramps.gen.const import URL_MANUAL_PAGE

WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Settings"

#------------------------------------------------------------------------
#
# StyleListDisplay class
#
#------------------------------------------------------------------------
class StyleListDisplay(ManagedWindow):
    """
    Shows the available paragraph/font styles. Allows the user to select,
    add, edit, and delete styles from a StyleSheetList.
    """

    def __init__(self, stylesheetlist, uistate, track, callback=None):
        """
        Create a StyleListDisplay object that displays the styles in the
        StyleSheetList.

        stylesheetlist - styles for editing: a :class:`.StyleSheetList` instance
        callback - task called when an object has been added.
        """

        ManagedWindow.__init__(self, uistate, track, self.__class__, modal=True)
        # the self.window.run() below makes Gtk make it modal, so any change
        # to the previous line's "modal" would require that line to be changed

        self.callback = callback

        self.sheetlist = stylesheetlist

        self.top = Glade(toplevel='styles')
        self.set_window(self.top.toplevel, self.top.get_object('title'),
                        _('Document Styles'))
        self.setup_configs('interface.stylelistdisplay', 400, 300)
        self.show()

        self.top.connect_signals({
            "on_ok_clicked" : self.on_ok_clicked,
            "on_add_clicked" : self.on_add_clicked,
            "on_delete_clicked" : self.on_delete_clicked,
            "on_button_press" : self.on_button_press,
            "on_edit_clicked" : self.on_edit_clicked,
            "on_cancel_clicked" : self.__cancel,
            "on_help_btn_clicked" : lambda x: display_help(
                WIKI_HELP_PAGE, _('manual|Document_Styles_dialog')),
            "on_cancel_style_clicked" : dummy_callback,
            "on_save_style_clicked" : dummy_callback,
            "on_help_btn_style_clicked" : dummy_callback,
            })

        self.list = ListModel(self.top.get_object("list"),
                                        [(_('Style'), -1, 10)], )
        self.redraw()
        # the self.window.run() makes Gtk make it modal, so any change to that
        # line would require the ManagedWindow.__init__ to be changed also
        self.window.run()
        if self.opened:
            self.close()

    def build_menu_names(self, obj): # meaningless while it's modal
        """Override :class:`.ManagedWindow` method."""
        return (_('Document Styles'), ' ')

    def __cancel(self, obj):
        pass

    def redraw(self):
        """Redraws the list of styles that are currently available"""

        self.list.model.clear()
        self.list.add([_("default")])

        index = 1
        for style in sorted(self.sheetlist.get_style_names()):
            if style == "default":
                continue
            self.list.add([style])
            index += 1

    def on_add_clicked(self, obj):
        """Called when the ADD button is clicked. Invokes the StyleEditor to
        create a new style"""
        style = self.sheetlist.get_style_sheet("default")
        StyleEditor(_("New Style"), style, self)

    def on_ok_clicked(self, obj):
        """Called when the OK button is clicked; Calls the callback task,
        then saves the stylesheet."""
        if self.callback is not None:
            self.callback()
        try:
            self.sheetlist.save()
        except IOError as msg:
            ErrorDialog(_("Error saving stylesheet"), str(msg),
                        parent=self.window)
        except:
            log.error("Failed to save stylesheet", exc_info=True)

    def on_button_press(self, obj, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            self.on_edit_clicked(obj)

    def on_edit_clicked(self, obj):
        """
        Called when the EDIT button is clicked.
        Calls the StyleEditor to edit the selected style.
        """
        store, node = self.list.selection.get_selected()
        if not node:
            ErrorDialog(_("Missing information"), _("Select a style"),
                        parent=self.window)
            return

        name = str(self.list.model.get_value(node, 0))
        if name == _('default'): # the default style cannot be edited
            return
        style = self.sheetlist.get_style_sheet(name)
        StyleEditor(name, style, self)

    def on_delete_clicked(self, obj):
        """Deletes the selected style."""
        store, node = self.list.selection.get_selected()
        if not node:
            ErrorDialog(_("Missing information"), _("Select a style"),
                        parent=self.window)
            return
        name = str(self.list.model.get_value(node, 0))
        if name == _('default'): # the default style cannot be removed
            return
        self.sheetlist.delete_style_sheet(name)
        self.redraw()

#------------------------------------------------------------------------
#
# StyleEditor class
#
#------------------------------------------------------------------------
class StyleEditor(ManagedWindow):
    """
    Edits the current style definition.
    Presents a dialog allowing the values in the style to be altered.
    """

    def __init__(self, name, style, parent):
        """
        Create the StyleEditor.

        name - name of the style that is to be edited
        style - style object to be edited: a :class:`.StyleSheet` instance
        parent - StyleListDisplay object that called the editor
        """

        ManagedWindow.__init__(self, parent.uistate, parent.track,
                               self.__class__, modal=True)
        # the self.window.run() below makes Gtk make it modal, so any change
        # to the previous line's "modal" would require that line to be changed

        self.current_style = None
        self.current_name = None

        self.style = StyleSheet(style)
        self.parent = parent
        self.top = Glade(
            toplevel='editor',
            also_load=[
                "adjustment1", "adjustment2", "adjustment3", "adjustment4",
                "adjustment5", "adjustment6", "adjustment7", "adjustment8",
                "adjustment9", "adjustment10", "adjustment11"])
        self.set_window(self.top.toplevel, self.top.get_object('title'),
                        _('Style editor'))
        self.setup_configs('interface.styleeditor', 550, 610)
        self.show()

        self.top.connect_signals({
            "on_save_style_clicked" : self.on_save_style_clicked,
            "on_cancel_style_clicked" : self.__cancel,
            "on_help_btn_style_clicked" : lambda x: display_help(
                WIKI_HELP_PAGE, _('manual|Style_editor_dialog')),
            "on_cancel_clicked" : dummy_callback,
            "on_ok_clicked" : dummy_callback,
            "on_add_clicked" : dummy_callback,
            "on_delete_clicked" : dummy_callback,
            "on_button_press" : dummy_callback,
            "on_edit_clicked" : dummy_callback,
            "on_help_btn_clicked" : dummy_callback,
            })

        self.pname = self.top.get_object('pname')
        self.pdescription = self.top.get_object('pdescription')

        self.notebook = self.top.get_object('notebook1')
        self.vbox = self.top.get_object('column_widths')

        self.line_style = self.top.get_object('line_style')
        line_styles = Gtk.ListStore(int, str)
        line_styles.append([0, "Solid"])
        line_styles.append([1, "Dashed"])
        line_styles.append([2, "Dotted"])
        self.line_style.set_model(line_styles)
        renderer_text = Gtk.CellRendererText()
        self.line_style.pack_start(renderer_text, True)
        self.line_style.add_attribute(renderer_text, "text", 1)

        self.top.get_object("label6").set_text(_("point size|pt"))

        titles = [(_('Style'), 0, 130)]
        self.plist = ListModel(self.top.get_object("ptree"), titles,
                                         self.change_display)

        for widget_name in ('color', 'bgcolor', 'line_color', 'fill_color'):
            color = self.top.get_object(widget_name)
            label = self.top.get_object(widget_name + '_code')
            color.connect('notify::color', self.color_changed, label)

        self.top.get_object("style_name").set_text(name)

        def _alphanumeric_sort(iterable):
            """ sort the given iterable in the way that humans expect """
            convert = lambda text: int(text) if text.isdigit() else text
            sort_key = lambda k: [convert(c) for c in re.split('([0-9]+)', k)]
            return sorted(iterable, key=sort_key)

        names = _alphanumeric_sort(self.style.get_paragraph_style_names())
        for p_name in names:
            self.plist.add([p_name], self.style.get_paragraph_style(p_name))
        names = _alphanumeric_sort(self.style.get_table_style_names())
        for t_name in names:
            self.plist.add([t_name], self.style.get_table_style(t_name))
        names = _alphanumeric_sort(self.style.get_cell_style_names())
        for c_name in names:
            self.plist.add([c_name], self.style.get_cell_style(c_name))
        names = _alphanumeric_sort(self.style.get_draw_style_names())
        for d_name in names:
            self.plist.add([d_name], self.style.get_draw_style(d_name))
        self.plist.select_row(0)

        # the self.window.run() makes Gtk make it modal, so any change to that
        # line would require the ManagedWindow.__init__ to be changed also
        self.window.run()
        if self.opened:
            self.close()

    def build_menu_names(self, obj): # meaningless while it's modal
        """Override :class:`.ManagedWindow` method."""
        return (_('Style editor'), None)

    def __cancel(self, obj):
        pass

    def show_pages(self, show_pages):
        """
        Make the given pages visible.
        """
        for page_num in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(page_num)
            if page_num in show_pages:
                page.show()
            else:
                page.hide()

    def draw(self):
        """
        Updates the display with the selected style.
        """
        if isinstance(self.current_style, ParagraphStyle):
            self.show_pages([0, 1, 2])
            self.draw_paragraph()
        elif isinstance(self.current_style, TableStyle):
            self.show_pages([0, 3])
            self.draw_table()
        elif isinstance(self.current_style, TableCellStyle):
            self.show_pages([0, 4])
            self.draw_cell()
        elif isinstance(self.current_style, GraphicsStyle):
            self.show_pages([0, 5])
            self.draw_graphics()

    def draw_graphics(self):
        """
        Updates the display with the selected graphics style.
        """
        g = self.current_style
        self.pname.set_text( '<span size="larger" weight="bold">%s</span>' %
                             self.current_name)
        self.pname.set_use_markup(True)

        descr = g.get_description()
        descr = descr or _("No description available")
        p_style = g.get_paragraph_style()
        if p_style:
            para_note = _("(Embedded style '%s' must be edited separately)")
            descr += '\n\n' + para_note % p_style
        self.pdescription.set_text(descr)

        self.top.get_object("line_style").set_active(g.get_line_style())
        self.top.get_object("line_width").set_value(g.get_line_width())

        self.line_color = rgb2color(g.get_color())
        self.top.get_object("line_color").set_color(self.line_color)
        self.fill_color = rgb2color(g.get_fill_color())
        self.top.get_object("fill_color").set_color(self.fill_color)

        self.top.get_object("shadow").set_active(g.get_shadow())
        self.top.get_object("shadow_space").set_value(g.get_shadow_space())

    def draw_cell(self):
        """
        Updates the display with the selected cell style.
        """
        c = self.current_style
        self.pname.set_text( '<span size="larger" weight="bold">%s</span>' %
                             self.current_name)
        self.pname.set_use_markup(True)

        descr = c.get_description()
        self.pdescription.set_text(descr or _("No description available"))

        self.top.get_object("cell_lborder").set_active(c.get_left_border())
        self.top.get_object("cell_rborder").set_active(c.get_right_border())
        self.top.get_object("cell_tborder").set_active(c.get_top_border())
        self.top.get_object("cell_bborder").set_active(c.get_bottom_border())
        self.top.get_object("cell_padding").set_value(c.get_padding())

    def draw_table(self):
        """
        Updates the display with the selected table style.
        """
        t = self.current_style
        self.pname.set_text( '<span size="larger" weight="bold">%s</span>' %
                             self.current_name)
        self.pname.set_use_markup(True)

        descr = t.get_description()
        self.pdescription.set_text(descr or _("No description available"))

        self.top.get_object("table_width").set_value(t.get_width())

        self.column = []
        for widget in self.vbox.get_children():
            self.vbox.remove(widget)

        for i in range(t.get_columns()):
            hbox = Gtk.Box()
            label = Gtk.Label(label=_('Column %d:') % (i + 1))
            hbox.pack_start(label, False, False, 6)
            spin = Gtk.SpinButton()
            spin.set_range(0, 100)
            spin.set_increments(1, 10)
            spin.set_numeric(True)
            spin.set_value(t.get_column_width(i))
            self.column.append(spin)
            hbox.pack_start(spin, False, False, 6)
            hbox.pack_start(Gtk.Label('%'), False, False, 6)
            hbox.show_all()
            self.vbox.pack_start(hbox, False, False, 3)

    def draw_paragraph(self):
        """
        Updates the display with the selected paragraph style.
        """
        p = self.current_style
        self.pname.set_text( '<span size="larger" weight="bold">%s</span>' %
                             self.current_name)
        self.pname.set_use_markup(True)

        descr = p.get_description()
        self.pdescription.set_text(descr or _("No description available") )

        font = p.get_font()
        self.top.get_object("size").set_value(font.get_size())
        if font.get_type_face() == FONT_SERIF:
            self.top.get_object("roman").set_active(1)
        else:
            self.top.get_object("swiss").set_active(1)
        self.top.get_object("bold").set_active(font.get_bold())
        self.top.get_object("italic").set_active(font.get_italic())
        self.top.get_object("underline").set_active(font.get_underline())
        if p.get_alignment() == PARA_ALIGN_LEFT:
            self.top.get_object("lalign").set_active(1)
        elif p.get_alignment() == PARA_ALIGN_RIGHT:
            self.top.get_object("ralign").set_active(1)
        elif p.get_alignment() == PARA_ALIGN_CENTER:
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

        color = rgb2color(font.get_color())
        self.top.get_object("color").set_color(color)
        bg_color = rgb2color(p.get_background_color())
        self.top.get_object("bgcolor").set_color(bg_color)

    def color_changed(self, color, name, label):
        """
        Called to set the color code when a color is changed.
        """
        rgb = color2rgb(color.get_color())
        label.set_text("#%02X%02X%02X" % color2rgb(color.get_color()))

    def save(self):
        """
        Saves the current style displayed on the dialog.
        """
        if isinstance(self.current_style, ParagraphStyle):
            self.save_paragraph()
        elif isinstance(self.current_style, TableStyle):
            self.save_table()
        elif isinstance(self.current_style, TableCellStyle):
            self.save_cell()
        elif isinstance(self.current_style, GraphicsStyle):
            self.save_graphics()

    def save_graphics(self):
        """
        Saves the current graphics style displayed on the dialog.
        """
        g = self.current_style
        g.set_line_style(self.top.get_object("line_style").get_active())
        g.set_line_width(self.top.get_object("line_width").get_value())
        line_color = self.top.get_object("line_color").get_color()
        g.set_color(color2rgb(line_color))
        fill_color = self.top.get_object("fill_color").get_color()
        g.set_fill_color(color2rgb(fill_color))
        shadow = self.top.get_object("shadow").get_active()
        shadow_space = self.top.get_object("shadow_space").get_value()
        g.set_shadow(shadow, shadow_space)

        self.style.add_draw_style(self.current_name, self.current_style)

    def save_cell(self):
        """
        Saves the current cell style displayed on the dialog.
        """
        c = self.current_style
        c.set_left_border(self.top.get_object("cell_lborder").get_active())
        c.set_right_border(self.top.get_object("cell_rborder").get_active())
        c.set_top_border(self.top.get_object("cell_tborder").get_active())
        c.set_bottom_border(self.top.get_object("cell_bborder").get_active())
        c.set_padding(self.top.get_object("cell_padding").get_value())

        self.style.add_cell_style(self.current_name, self.current_style)

    def save_table(self):
        """
        Saves the current table style displayed on the dialog.
        """
        t = self.current_style
        t.set_width(self.top.get_object("table_width").get_value_as_int())
        for i in range(t.get_columns()):
            t.set_column_width(i, self.column[i].get_value_as_int())

        self.style.add_table_style(self.current_name, self.current_style)

    def save_paragraph(self):
        """
        Saves the current paragraph style displayed on the dialog.
        """
        p = self.current_style
        font = p.get_font()
        font.set_size(self.top.get_object("size").get_value_as_int())

        if self.top.get_object("roman").get_active():
            font.set_type_face(FONT_SERIF)
        else:
            font.set_type_face(FONT_SANS_SERIF)

        font.set_bold(self.top.get_object("bold").get_active())
        font.set_italic(self.top.get_object("italic").get_active())
        font.set_underline(self.top.get_object("underline").get_active())
        if self.top.get_object("lalign").get_active():
            p.set_alignment(PARA_ALIGN_LEFT)
        elif self.top.get_object("ralign").get_active():
            p.set_alignment(PARA_ALIGN_RIGHT)
        elif self.top.get_object("calign").get_active():
            p.set_alignment(PARA_ALIGN_CENTER)
        else:
            p.set_alignment(PARA_ALIGN_JUSTIFY)

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

        color = self.top.get_object("color").get_color()
        font.set_color(color2rgb(color))
        bg_color = self.top.get_object("bgcolor").get_color()
        p.set_background_color(color2rgb(bg_color))

        self.style.add_paragraph_style(self.current_name, self.current_style)

    def on_save_style_clicked(self, obj):
        """
        Saves the current style sheet and causes the parent to be updated with
        the changes.
        """
        name = str(self.top.get_object("style_name").get_text())

        self.save()
        self.style.set_name(name)
        self.parent.sheetlist.set_style_sheet(name, self.style)
        self.parent.redraw()

    def change_display(self, obj):
        """
        Called when the paragraph selection has been changed. Saves the
        old paragraph, then draws the newly selected paragraph.
        """
        # Don't save until current_name is defined
        # If it's defined, save under the current paragraph name
        if self.current_name:
            self.save()
        # Then change to new paragraph
        objs = self.plist.get_selected_objects()
        store, node = self.plist.get_selected()
        self.current_name =  store.get_value(node, 0)
        self.current_style = objs[0]
        self.draw()


def rgb2color(rgb):
    """
    Convert a tuple containing RGB values into a Gdk Color.
    """
    return Gdk.Color(rgb[0] << 8, rgb[1] << 8, rgb[2] << 8)

def color2rgb(color):
    """
    Convert a Gdk Color into a tuple containing RGB values.
    """
    return (color.red >> 8, color.green >> 8, color.blue >> 8)

def dummy_callback(obj):
    """Dummy callback to satisfy gtkbuilder on connect of signals.
    There are two widgets in the glade file, although only one is needed,
    the signals of the other must be connected too
    """
    pass
