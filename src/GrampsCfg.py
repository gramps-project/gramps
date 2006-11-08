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
from NameDisplay import displayer as _nd
from RelLib import Name
import ManagedWindow
from GrampsWidgets import *
import QuestionDialog

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

# column numbers for the 'name format' model
COL_NUM  = 0
COL_NAME = 1
COL_FMT  = 2
COL_EXPL = 3

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
    def __init__(self, uistate, dbstate):

        ManagedWindow.ManagedWindow.__init__(self,uistate,[],GrampsPreferences)

        self.dbstate = dbstate
        
        self.set_window(
            gtk.Dialog(_('Preferences'),
                       flags=gtk.DIALOG_NO_SEPARATOR,
                       buttons=(gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE)),
            None, _('Preferences'), None)
        
        panel = gtk.Notebook()

        self.original = Config.get(Config.TRANSACTIONS)
        
        self.window.vbox.add(panel)
        self.window.connect('response',self.done)
        panel.append_page(self.add_behavior_panel(),
                          MarkupLabel(_('General')))
        panel.append_page(self.add_formats_panel(),
                          MarkupLabel(_('Display')))
        panel.append_page(self.add_name_panel(),
                          MarkupLabel(_('Name Display')))
        panel.append_page(self.add_prefix_panel(),
                          MarkupLabel(_('ID Formats')))
        panel.append_page(self.add_advanced_panel(),
                          MarkupLabel(_('Warnings')))
        panel.append_page(self.add_researcher_panel(),
                          MarkupLabel(_('Researcher')))
        panel.append_page(self.add_color_panel(),
                          MarkupLabel(_('Marker Colors')))

        self.window.show_all()
        self.show()

    def done(self, obj, value):
        if not self.original and Config.get(Config.TRANSACTIONS):
            Config.set(Config.PORT_WARN, True)
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
            table, _('Suppress warning when adding parents to a child'),
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
        """
        Name format settings panel
        """

        # a dummy name to be used in the examples
        self.examplename = Name()
        self.examplename.set_title('Dr.')
        self.examplename.set_first_name('Edwin')
        self.examplename.set_surname_prefix('Rev.')
        self.examplename.set_surname('Smith')
        self.examplename.set_suffix('Sr')
        self.examplename.set_patronymic('Patronymic')
        self.examplename.set_call_name('Ed')

        table = gtk.Table(2,2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        # get the model for the combo and the treeview
        active = _nd.get_default_format()
        self.fmt_model,active = self._build_name_format_model(active)

        # set up the combo to choose the preset format
        self.fmt_obox = gtk.ComboBox()
        cell = gtk.CellRendererText()
        self.fmt_obox.pack_start(cell, True)
        self.fmt_obox.add_attribute(cell, 'text', 1)
        self.fmt_obox.set_model(self.fmt_model)
        
        # set the default value as active in the combo
        self.fmt_obox.set_active(active)
        self.fmt_obox.connect('changed', self.cb_name_changed)
        # label for the combo
        lwidget = BasicLabel("%s: " % _('_Display format'))
        lwidget.set_use_underline(True)
        lwidget.set_mnemonic_widget(self.fmt_obox)

        # build the format manager ui
        custom_ui = self._build_custom_name_ui()
        name_exp = gtk.expander_new_with_mnemonic(_('C_ustom format details'))
        name_exp.add(custom_ui)
        name_exp.set_sensitive(self.dbstate.open)
        
        # put all these together
        table.attach(lwidget, 0, 1, 0, 1, yoptions=0)
        table.attach(self.fmt_obox, 1, 2, 0, 1, yoptions=0)
        table.attach(name_exp, 0, 2, 1, 2, yoptions=gtk.FILL|gtk.EXPAND)
        
        return table

    def _build_name_format_model(self,active):
        """
        Create a common model for ComboBox and TreeView
        """
        name_format_model = gtk.ListStore(int,str,str,str)

        index = 0        
        the_index = 0
        
        for num,name,fmt_str,act in _nd.get_name_format():
            self.examplename.set_display_as(num)
            name_format_model.append(
                row=[num, name, fmt_str, _nd.display_name(self.examplename)])
            if num == active: the_index = index
            index += 1
        
        return name_format_model,the_index

    def _build_custom_name_ui(self):
        """
        UI to manage the custom name formats
        """

        table = gtk.Table(2,3)
        table.set_border_width(6)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        # make a treeview for listing all the name formats
        format_tree = gtk.TreeView(self.fmt_model)
        name_renderer = gtk.CellRendererText()
        name_column = gtk.TreeViewColumn(_('Format Name'),
                                         name_renderer,
                                         text=COL_NAME)
        format_tree.append_column(name_column)
        example_renderer = gtk.CellRendererText()
        example_column = gtk.TreeViewColumn(_('Example'),
                                            example_renderer,
                                            text=COL_EXPL)
        format_tree.append_column(example_column)
        format_tree.get_selection().connect('changed',
                                            self.cb_format_tree_select)
        format_tree.set_rules_hint(True)

        # ... and put it into a scrolled win
        format_sw = gtk.ScrolledWindow()
        format_sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        format_sw.add(format_tree)
        format_sw.set_shadow_type(gtk.SHADOW_IN)
        table.attach(format_sw, 0, 3, 0, 1, yoptions=gtk.FILL|gtk.EXPAND)

        # to hold the values of the selected row of the tree and the iter
        self.selected_fmt = ()
        self.iter = None

        insert_button = gtk.Button(stock=gtk.STOCK_ADD)
        insert_button.connect('clicked',self.cb_insert_fmt_str)

        self.edit_button = gtk.Button(stock=gtk.STOCK_EDIT)
        self.edit_button.connect('clicked',self.cb_edit_fmt_str)
        self.edit_button.set_sensitive(False)

        self.remove_button = gtk.Button(stock=gtk.STOCK_REMOVE)
        self.remove_button.connect('clicked',self.cb_del_fmt_str)
        self.remove_button.set_sensitive(False)
        
        table.attach(insert_button, 0, 1, 1, 2,yoptions=0)
        table.attach(self.remove_button, 1, 2, 1, 2,yoptions=0)
        table.attach(self.edit_button,   2, 3, 1, 2,yoptions=0)

        return table

    def cb_name_changed(self,obj):
        """
        Preset name format ComboBox callback
        """
        the_list = obj.get_model()
        the_iter = obj.get_active_iter()
        new_idx = the_list.get_value(the_iter,COL_NUM)
        Config.set(Config.NAME_FORMAT,new_idx)
        _nd.set_default_format(new_idx)
        self.uistate.emit('nameformat-changed')
        
    def cb_format_tree_select(self, tree_selection):
        """
        Name format editor TreeView callback
        
        Remember the values of the selected row (self.selected_fmt, self.iter)
        and set the Remove and Edit button sensitivity
        
        """
        model,self.iter = tree_selection.get_selected()
        if self.iter == None:
            tree_selection.select_path(0)
            model,self.iter = tree_selection.get_selected()
        self.selected_fmt = model.get(self.iter, 0, 1, 2)
        idx = self.selected_fmt[COL_NUM] < 0
        self.remove_button.set_sensitive(idx)
        self.edit_button.set_sensitive(idx)

    def cb_edit_fmt_str(self,obj):
        """
        Name format editor Edit button callback
        """
        num,name,fmt = self.selected_fmt[COL_NUM:COL_EXPL]
        dlg = NameFormatEditDlg(name,fmt,self.examplename)
        dlg.dlg.set_transient_for(self.window)
        (res,name,fmt) = dlg.run()

        if name != self.selected_fmt[COL_NAME] or \
           fmt != self.selected_fmt[COL_FMT]:
            exmpl = _nd.format_str(self.examplename,fmt)
            self.fmt_model.set(self.iter,COL_NAME,name,
                               COL_FMT,fmt,
                               COL_EXPL,exmpl)
            self.selected_fmt = (num,name,fmt,exmpl)
            _nd.edit_name_format(num,name,fmt)

            self.dbstate.db.name_formats = _nd.get_name_format(only_custom=True,
                                                               only_active=False)
        
    def cb_insert_fmt_str(self,obj):
        """
        Name format editor Insert button callback
        """
        dlg = NameFormatEditDlg('','',self.examplename)
        dlg.dlg.set_transient_for(self.window)
        (res,n,f) = dlg.run()

        if res == gtk.RESPONSE_OK:
            i = _nd.add_name_format(n,f)
            self.fmt_model.append(row=[i,n,f,
                                       _nd.format_str(self.examplename,f)])

        self.dbstate.db.name_formats = _nd.get_name_format(only_custom=True,
                                                           only_active=False)
        
    def cb_del_fmt_str(self,obj):
        """
        Name format editor Remove button callback
        """
        num = self.selected_fmt[COL_NUM]

        if _nd.get_default_format() == num:
            self.fmt_obox.set_active(0)

        self.fmt_model.remove(self.iter)
        _nd.set_format_inactive(num)
        self.dbstate.db.name_formats = _nd.get_name_format(only_custom=True,
                                                           only_active=False)

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
        obox.connect('changed', self.date_format_changed)

        lwidget = BasicLabel("%s: " % _('Date format'))
        table.attach(lwidget, 0, 1, 0, 1, yoptions=0)
        table.attach(obox, 1, 3, 0, 1, yoptions=0)

        obox = gtk.combo_box_new_text()
        formats = _surname_styles
        for item in formats:
            obox.append_text(item)
        obox.set_active(Config.get(Config.SURNAME_GUESSING))
        obox.connect('changed',
                     lambda obj: Config.set(Config.SURNAME_GUESSING, 
                                            obj.get_active()))

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

    def date_format_changed(self, obj):
        from QuestionDialog import OkDialog

        Config.set(Config.DATE_FORMAT, obj.get_active())
        OkDialog(_('Change is not immediate'),
                 _('Changing the data format will not take '
                   'effect until the next time GRAMPS is started.'))

    def add_behavior_panel(self):
        table = gtk.Table(3,8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        self.add_checkbox(table, _('Automatically load last database'),
                          0, Config.AUTOLOAD)
        self.add_checkbox(table, _('Add default source on import'),
                          1, Config.DEFAULT_SOURCE)
        self.add_checkbox(table, _('Enable spelling checker'),
                          2, Config.SPELLCHECK)
        self.add_checkbox(table, _('Display Tip of the Day'),
                          3, Config.USE_TIPS)
        self.add_checkbox(table, _('Use shading in Relationship View'),
                          4, Config.RELATION_SHADE)
        self.add_checkbox(table, _('Enable database transactions'),
                          5, Config.TRANSACTIONS)
        self.add_checkbox(table, _('Display edit buttons on Relationship View'),
                          6, Config.RELEDITBTN)

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

    # FIXME: is this needed?
    def _set_button(stock):
        button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
        image.show()
        button.add(image)
        button.show()
        return button
    
class NameFormatEditDlg:
    """
    """
    
    def __init__(self,fmt_name,fmt_str,name):
        self.fmt_name = fmt_name
        self.fmt_str = fmt_str
        self.name = name

        self.top = gtk.glade.XML(const.gladeFile,'namefmt_edit','gramps')
        self.dlg = self.top.get_widget('namefmt_edit')
        ManagedWindow.set_titles(
            self.dlg,
            self.top.get_widget('title'),
            _('Name Format Editor'))
        
        self.examplelabel = self.top.get_widget('example_label')
        
        self.nameentry = self.top.get_widget('name_entry')
        self.nameentry.set_text(self.fmt_name)
        
        self.formatentry = self.top.get_widget('format_entry')
        self.formatentry.connect('changed',self.cb_format_changed)
        self.formatentry.set_text(self.fmt_str)
        
    def run(self):
        running = True
        while running:
            self.response = self.dlg.run()

            running = False
            self.fmt_name = self.nameentry.get_text()
            self.fmt_str = self.formatentry.get_text()
            
            if self.response == gtk.RESPONSE_OK:
                if self.fmt_name == '' and self.fmt_str == '':
                    self.response = gtk.RESPONSE_CANCEL
                elif (self.fmt_name == '') ^ (self.fmt_str == ''):
                    QuestionDialog.ErrorDialog(
                        _('Both Format name and definition have to be defined'),
                        parent=self.dlg)
                    running = True
                                    
        self.dlg.destroy()
        return (self.response, self.fmt_name, self.fmt_str)

    def cb_format_changed(self,obj):
        t = (_nd.format_str(self.name,obj.get_text()))
        self.examplelabel.set_text('<span weight="bold" style="italic">%s</span>' % t)
        self.examplelabel.set_use_markup(True)
        
    
