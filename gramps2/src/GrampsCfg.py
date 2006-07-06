#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Config
import DateHandler
import NameDisplay
from RelLib import Name
import ManagedWindow
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# Constants 
#
#-------------------------------------------------------------------------

_surname_styles = [
    _("Father's surname"),
    _("None"),
    _("Combination of mother's and father's surname"),
    _("Icelandic style"),
    ]

def set_calendar_date_format():
    format_list = DateHandler.get_date_formats()
    DateHandler.set_format(Config.get_date_format(format_list))

def get_researcher():
    import RelLib
    
    n  = Config.get(Config.RESEARCHER_NAME)
    a  = Config.get(Config.RESEARCHER_ADDR)
    c  = Config.get(Config.RESEARCHER_CITY)
    s  = Config.get(Config.RESEARCHER_STATE)
    ct = Config.get(Config.RESEARCHER_COUNTRY)
    p  = Config.get(Config.RESEARCHER_POSTAL)
    ph = Config.get(Config.RESEARCHER_PHONE)
    e  = Config.get(Config.RESEARCHER_EMAIL)

    owner = RelLib.Researcher()
    owner.set(n,a,c,s,ct,p,ph,e)
    return owner

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class GrampsPreferences(ManagedWindow.ManagedWindow):
    def __init__(self, uistate):

        ManagedWindow.ManagedWindow.__init__(self,uistate,[],GrampsPreferences)

        tlabel = gtk.Label()
        self.set_window(
            gtk.Dialog(_('Preferences'),
                       flags=gtk.DIALOG_NO_SEPARATOR,
                       buttons=(gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE)),
            tlabel, _('Preferences'), None)

        panel = gtk.Notebook()
        self.window.vbox.pack_start(tlabel, padding=12)
        self.window.vbox.add(panel)
        self.window.connect('response',self.done)
        panel.append_page(self.add_behavior_panel(),
                          MarkupLabel("<b>%s</b>" % _('General')))
        panel.append_page(self.add_formats_panel(),
                          MarkupLabel("<b>%s</b>" % _('Display')))
        panel.append_page(self.add_name_panel(),
                          MarkupLabel("<b>%s</b>" % _('Name Display')))
        panel.append_page(self.add_prefix_panel(),
                          MarkupLabel("<b>%s</b>" % _('ID Formats')))
        panel.append_page(self.add_advanced_panel(),
                          MarkupLabel("<b>%s</b>" % _('Warnings')))
        panel.append_page(self.add_researcher_panel(),
                          MarkupLabel("<b>%s</b>" % _('Researcher')))
        panel.append_page(self.add_color_panel(),
                          MarkupLabel("<b>%s</b>" % _('Marker Colors')))

        self.window.show_all()
        self.show()

    def done(self, obj, value):
        self.close()

    def add_researcher_panel(self):
        table = gtk.Table(3,8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        self.add_entry(table, _('Name'), 0, Config.RESEARCHER_NAME)
        self.add_entry(table, _('Address'), 1, Config.RESEARCHER_ADDR)
        self.add_entry(table, _('City'), 2, Config.RESEARCHER_CITY)
        self.add_entry(table, _('State/Province'), 3, Config.RESEARCHER_STATE)
        self.add_entry(table, _('Country'), 4, Config.RESEARCHER_COUNTRY)
        self.add_entry(table, _('ZIP/Postal Code'), 5, Config.RESEARCHER_POSTAL)
        self.add_entry(table, _('Phone'), 6, Config.RESEARCHER_PHONE)
        self.add_entry(table, _('Email'), 7, Config.RESEARCHER_EMAIL)
        return table

    def add_prefix_panel(self):
        table = gtk.Table(3,8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        self.add_entry(table, _('Person'), 0, Config.IPREFIX)
        self.add_entry(table, _('Family'), 1, Config.FPREFIX)
        self.add_entry(table, _('Place'), 2, Config.PPREFIX)
        self.add_entry(table, _('Source'), 3, Config.SPREFIX)
        self.add_entry(table, _('Media Object'), 4, Config.OPREFIX)
        self.add_entry(table, _('Event'), 5, Config.EPREFIX)
        self.add_entry(table, _('Repository'), 6, Config.RPREFIX)
        return table

    def add_advanced_panel(self):
        table = gtk.Table(3,8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        self.add_checkbox(
            table, _('Warn when adding parents to a child'),
            0, Config.FAMILY_WARN)
        
        self.add_checkbox(
            table, _('Suppress warning when cancelling with changed data'),
            1, Config.DONT_ASK)
        
        self.add_checkbox(
            table, _('Show plugin status dialog on plugin load error'),
            2, Config.POP_PLUGIN_STATUS)
        
        return table

    def add_color_panel(self):
        table = gtk.Table(3,8)
        table.set_border_width(12)
        table.set_col_spacings(12)
        table.set_row_spacings(6)

        self.comp_color = self.add_color(table, _("Complete"), 0,
                                         Config.COMPLETE_COLOR)
        self.todo_color = self.add_color(table, _("ToDo"), 1,
                                         Config.TODO_COLOR)
        self.custom_color = self.add_color(table, _("Custom"), 2,
                                           Config.CUSTOM_MARKER_COLOR)
        
        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', self.reset_colors)
        table.attach(button, 1, 2, 3, 4, yoptions=0, xoptions=0)
        return table

    def reset_colors(self, obj):

        def_comp = Config.get_default(Config.COMPLETE_COLOR,'')
        def_todo = Config.get_default(Config.TODO_COLOR,'')
        def_cust = Config.get_default(Config.CUSTOM_MARKER_COLOR,'')
        
        Config.set(Config.COMPLETE_COLOR, def_comp)
        Config.set(Config.TODO_COLOR, def_todo)
        Config.set(Config.CUSTOM_MARKER_COLOR, def_cust)

        self.comp_color.set_color(gtk.gdk.color_parse(def_comp))
        self.todo_color.set_color(gtk.gdk.color_parse(def_todo))
        self.custom_color.set_color(gtk.gdk.color_parse(def_cust))
        for widget in [self.comp_color,self.todo_color,self.custom_color]:
            widget.emit('color-set')

    def add_name_panel(self):
        table = gtk.Table(3,3)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        self.name_exp = gtk.expander_new_with_mnemonic(
            _('C_ustom format details'))
        self.name_exp.set_sensitive(False)


        format_list = []
        format_list += [(name,number) for (number,name,fmt_str)
                        in Name.STANDARD_FORMATS]
        format_list += [(name,number) for (number,name,fmt_str)
                        in NameDisplay.CUSTOM_FORMATS]
        
        obox = gtk.ComboBox()
        obox_data = {}
        obox_model = gtk.ListStore(str, int)
        cell = gtk.CellRendererText()
        obox.pack_start(cell, True)
        obox.add_attribute(cell, 'text', 0)  
        index = 0
        for t, v in format_list:
            obox_model.append(row=[t, v])
            obox_data[v] = index
            index += 1

        obox.set_model(obox_model)

        active = int(Config.get(Config.NAME_FORMAT))
        obox.set_active(active)
#        obox.connect('changed', self.name_changed)
        lwidget = BasicLabel("%s: " % _('Preset format'))

#        custom_ui = self.build_custom_name_ui()
#        self.name_exp.add(custom_ui)

        table.attach(lwidget, 0, 1, 0, 1, yoptions=0)
        table.attach(obox, 1,3,0, 1, yoptions=0)
#        table.attach(self.name_exp, 0,3,1, 2, yoptions=0)
        return table

##     def build_custom_name_ui(self):
##         table = gtk.Table(2,3)
##         table.set_border_width(6)
##         table.set_col_spacings(6)
##         table.set_row_spacings(6)

##         avail_sw = gtk.ScrolledWindow()
##         avail_sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_NEVER)
##         avail_tree = gtk.TreeView()
##         avail_sw.add(avail_tree)

##         use_sw = gtk.ScrolledWindow()
##         use_sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_NEVER)
##         use_tree = gtk.TreeView()
##         use_sw.add(use_tree)

##         button_table = gtk.Table(3,3)

##         up_button = _set_button(gtk.STOCK_GO_UP)
##         down_button = _set_button(gtk.STOCK_GO_DOWN)
##         add_button = _set_button(gtk.STOCK_ADD)
##         remove_button = _set_button(gtk.STOCK_REMOVE)
##         button_table.attach(up_button, 1, 2, 0, 1, xoptions = 0, yoptions=0)
##         button_table.attach(remove_button, 2, 3, 1, 2, xoptions = 0,yoptions=0)
##         button_table.attach(down_button, 1, 2, 2, 3, xoptions = 0, yoptions=0)
##         button_table.attach(add_button, 0, 1, 1, 2, xoptions = 0,yoptions=0)

##         example_label = gtk.Label('<b>%s</b>' % _('Example'))
##         example_label.set_use_markup(True)

##         table.attach(example_label,0,3,0,1,xoptions = 0,yoptions=0)
##         table.attach(avail_sw, 0,1,1,2, yoptions=gtk.FILL)
##         table.attach(button_table, 1, 2, 1, 2, xoptions = 0, yoptions=0)
##         table.attach(use_sw, 2,3,1,2, yoptions=gtk.FILL)
        
##         return table

##     def name_changed(self,obj):
##         custom_text = NameDisplay.formats[Name.CUSTOM]
##         if obj.get_active_text() == custom_text:
##             pass
##             #self.name_exp.set_sensitive(True)
##             #self.name_exp.set_expanded(True)
##         else:
##             Config.set(Config.NAME_FORMAT,obj.get_active())
##             #self.name_exp.set_expanded(False)
##             #self.name_exp.set_sensitive(False)

    def add_formats_panel(self):
        table = gtk.Table(3,8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        obox = gtk.combo_box_new_text()
        formats = DateHandler.get_date_formats()
        for item in formats:
            obox.append_text(item)

        active = Config.get(Config.DATE_FORMAT)
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect('changed',
                     lambda obj: Config.set(Config.DATE_FORMAT, obj.get_active()))

        lwidget = BasicLabel("%s: " % _('Date format'))
        table.attach(lwidget, 0, 1, 0, 1, yoptions=0)
        table.attach(obox, 1, 3, 0, 1, yoptions=0)

        obox = gtk.combo_box_new_text()
        formats = _surname_styles
        for item in formats:
            obox.append_text(item)
        obox.set_active(Config.get(Config.SURNAME_GUESSING))
        obox.connect('changed',
                     lambda obj: Config.set(Config.SURNAME_GUESSING, obj.get_active()))

        lwidget = BasicLabel("%s: " % _('Surname Guessing'))
        table.attach(lwidget, 0, 1, 1, 2, yoptions=0)
        table.attach(obox, 1, 3, 1, 2, yoptions=0)

        obox = gtk.combo_box_new_text()
        formats = [_("Active person's name and ID"),
                   _("Relationship to home person")]
        
        for item in formats:
            obox.append_text(item)
        active = Config.get(Config.STATUSBAR)
        
        if active < 2:
            obox.set_active(0)
        else:
            obox.set_active(1)
        obox.connect('changed',
                     lambda obj: Config.set(Config.STATUSBAR, 2*obj.get_active()))

        lwidget = BasicLabel("%s: " % _('Status bar'))
        table.attach(lwidget, 0, 1, 2, 3, yoptions=0)
        table.attach(obox, 1, 3, 2, 3, yoptions=0)

        self.add_checkbox(table, _("Show text in sidebar buttons (takes effect on restart)"),
                          4, Config.SIDEBAR_TEXT)
                     
        return table

    # status bar

    def add_behavior_panel(self):
        table = gtk.Table(3,8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        self.add_checkbox(table, _('Automatically load last database'), 0, Config.AUTOLOAD)
        self.add_checkbox(table, _('Enable spelling checker'), 1, Config.SPELLCHECK)
        self.add_checkbox(table, _('Display Tip of the Day'), 2, Config.USE_TIPS)
        self.add_checkbox(table, _('Download maps online'), 3, Config.ONLINE_MAPS)
        self.add_checkbox(table, _('Use shading in Relationship View'), 4, Config.RELATION_SHADE)

        return table

    def add_checkbox(self, table, label, index, constant):
        checkbox = gtk.CheckButton(label)
        checkbox.set_active(Config.get(constant))
        checkbox.connect('toggled',self.update_checkbox, constant)
        table.attach(checkbox, 1, 3, index, index+1, yoptions=0)
        
    def add_entry(self, table, label, index, constant):
        lwidget = BasicLabel("%s: " % label)
        entry = gtk.Entry()
        entry.set_text(Config.get(constant))
        entry.connect('changed', self.update_entry, constant)
        table.attach(lwidget, 0, 1, index, index+1, yoptions=0,
                     xoptions=gtk.FILL)
        table.attach(entry, 1, 2, index, index+1, yoptions=0)

    def add_color(self, table, label, index, constant):
        lwidget = BasicLabel("%s: " % label)
        hexval = Config.get(constant)
        color = gtk.gdk.color_parse(hexval)
        entry = gtk.ColorButton(color=color)
        color_hex_label = BasicLabel(hexval)
        entry.connect('color-set',self.update_color,constant,color_hex_label)
        table.attach(lwidget, 0, 1, index, index+1, yoptions=0,
                     xoptions=gtk.FILL)
        table.attach(entry, 1, 2, index, index+1, yoptions=0, xoptions=0)
        table.attach(color_hex_label, 2, 3, index, index+1, yoptions=0)
        return entry

    def update_entry(self, obj, constant):
        Config.set(constant, unicode(obj.get_text()))

    def update_color(self, obj, constant, color_hex_label):
        color = obj.get_color()
        hexval = "#%02x%02x%02x" % (color.red/256,
                                    color.green/256,
                                    color.blue/256)
        color_hex_label.set_text(hexval)
        Config.set(constant, hexval)

    def update_checkbox(self, obj, constant):
        Config.set(constant, obj.get_active())

    def build_menu_names(self,obj):
        return (_('Preferences'),None)

def _set_button(stock):
    button = gtk.Button()
    image = gtk.Image()
    image.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
    image.show()
    button.add(image)
    button.show()
    return button
