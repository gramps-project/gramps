#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008  Raphael Ackermann
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
import random
from gettext import gettext as _
import os
from xml.sax.saxutils import escape

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import config
import const
import DateHandler
from BasicUtils import name_displayer as _nd
import Utils
from gen.lib import Name
import ManagedWindow
from gui.widgets import MarkupLabel, BasicLabel
from QuestionDialog import ErrorDialog, QuestionDialog2, OkDialog
from Errors import NameDisplayError
from glade import Glade

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

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DisplayNameEditor(ManagedWindow.ManagedWindow):
    def __init__(self, uistate, dbstate, track, dialog):
        # Assumes that there are two methods: dialog.name_changed_check(), 
        # and dialog._build_custom_name_ui() 
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], DisplayNameEditor)
        self.dialog = dialog
        self.dbstate = dbstate
        self.set_window(
            gtk.Dialog(_('Display Name Editor'), 
                       flags=gtk.DIALOG_NO_SEPARATOR, 
                       buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)), 
            None, _('Display Name Editor'), None)
        table = self.dialog._build_custom_name_ui()
        label = gtk.Label(_("""The following keywords will be replaced with the name:
<tt>  
  <b>Given</b>      - given name (first name)
  <b>Surname</b>    - surname (last name)
  <b>Title</b>      - title (Dr., Mrs.)
  <b>Prefix</b>     - prefix (von, de, de la)
  <b>Suffix</b>     - suffix (Jr., Sr.)
  <b>Call</b>       - call name, or nickname
  <b>Common</b>     - call name, otherwise first part of Given
  <b>Patronymic</b> - patronymic (father's name)
  <b>Initials</b>   - persons's first letters of given names
</tt>
Use the same keyword in UPPERCASE to force to upper. Parentheses and commas
will be removed around empty fields. Other text will appear literally."""))
        label.set_use_markup(True)
        self.window.vbox.add(label)        
        self.window.vbox.add(table)
        self.window.set_default_size(600, 550)
        self.window.connect('response', self.close)
        self.show()
    def close(self, *obj):
        self.dialog.name_changed_check()
        ManagedWindow.ManagedWindow.close(self, *obj)
        
    def build_menu_names(self, obj):
        return (_(" Name Editor"), _("Preferences"))

class GrampsPreferences(ManagedWindow.ManagedWindow):

    def __init__(self, uistate, dbstate):
        self.dbstate = dbstate
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], GrampsPreferences)
        self.set_window(
            gtk.Dialog(_('Preferences'), 
                       flags=gtk.DIALOG_NO_SEPARATOR, 
                       buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)), 
            None, _('Preferences'), None)
        panel = gtk.Notebook()
        self.window.vbox.add(panel)
        self.window.connect('response', self.done)
        panel.append_page(self.add_behavior_panel(), 
                          MarkupLabel(_('General')))
        panel.append_page(self.add_database_panel(), 
                          MarkupLabel(_('Database')))
        panel.append_page(self.add_formats_panel(), 
                          MarkupLabel(_('Display')))
        panel.append_page(self.add_text_panel(), 
                          MarkupLabel(_('Text')))
        panel.append_page(self.add_prefix_panel(), 
                          MarkupLabel(_('ID Formats')))
        panel.append_page(self.add_date_panel(), 
                          MarkupLabel(_('Dates')))
        panel.append_page(self.add_advanced_panel(), 
                          MarkupLabel(_('Warnings')))
        panel.append_page(self.add_researcher_panel(), 
                          MarkupLabel(_('Researcher')))
        panel.append_page(self.add_color_panel(), 
                          MarkupLabel(_('Marker Colors')))
        self.window.show_all()
        self.show()

    def done(self, obj, value):
        Utils.update_constants()
        self.close()

    def add_researcher_panel(self):
        table = gtk.Table(3, 8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        self.add_entry(table, _('Name'), 0, 'researcher.researcher-name')
        self.add_entry(table, _('Address'), 1, 'researcher.researcher-addr')
        self.add_entry(table, _('City'), 2, 'researcher.researcher-city')
        self.add_entry(table, _('State/Province'), 3, 'researcher.researcher-state')
        self.add_entry(table, _('Country'), 4, 'researcher.researcher-country')
        self.add_entry(table, _('ZIP/Postal Code'), 5, 'researcher.researcher-postal')
        self.add_entry(table, _('Phone'), 6, 'researcher.researcher-phone')
        self.add_entry(table, _('Email'), 7, 'researcher.researcher-email')
        return table

    def add_prefix_panel(self):
        """
        Add the ID prefix tab to the preferences.
        """
        table = gtk.Table(3, 8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        self.add_entry(table, _('Person'), 0, 'preferences.iprefix', 
                       self.update_idformat_entry)
        self.add_entry(table, _('Family'), 1, 'preferences.fprefix',
                       self.update_idformat_entry)
        self.add_entry(table, _('Place'), 2, 'preferences.pprefix',
                       self.update_idformat_entry)
        self.add_entry(table, _('Source'), 3, 'preferences.sprefix',
                       self.update_idformat_entry)
        self.add_entry(table, _('Media Object'), 4, 'preferences.oprefix',
                       self.update_idformat_entry)
        self.add_entry(table, _('Event'), 5, 'preferences.eprefix',
                       self.update_idformat_entry)
        self.add_entry(table, _('Repository'), 6, 'preferences.rprefix',
                       self.update_idformat_entry)
        self.add_entry(table, _('Note'), 7, 'preferences.nprefix',
                       self.update_idformat_entry)
        return table

    def add_advanced_panel(self):
        table = gtk.Table(4, 8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        self.add_checkbox(
            table, _('Suppress warning when adding parents to a child.'), 
            0, 'preferences.family-warn')
        
        self.add_checkbox(
            table, _('Suppress warning when cancelling with changed data.'), 
            1, 'interface.dont-ask')
        
        self.add_checkbox(
            table, _('Suppress warning about missing researcher when'
                     ' exporting to GEDCOM.'), 
            2, 'behavior.owner-warn')

        self.add_checkbox(
            table, _('Show plugin status dialog on plugin load error.'), 
            3, 'behavior.pop-plugin-status')
        
        return table

    def add_color_panel(self):
        table = gtk.Table(3, 8)
        table.set_border_width(12)
        table.set_col_spacings(12)
        table.set_row_spacings(6)

        self.comp_color = self.add_color(table, _("Complete"), 0, 
                                         'preferences.complete-color')
        self.todo_color = self.add_color(table, _("ToDo"), 1, 
                                         'preferences.todo-color')
        self.custom_color = self.add_color(table, _("Custom"), 2, 
                                           'preferences.custom-marker-color')
        
        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', self.reset_colors)
        table.attach(button, 1, 2, 3, 4, yoptions=0, xoptions=0)
        return table

    def reset_colors(self, obj):

        def_comp = config.get_default('preferences.complete-color')
        def_todo = config.get_default('preferences.todo-color')
        def_cust = config.get_default('preferences.custom-marker-color')
        
        config.set('preferences.complete-color', def_comp)
        config.set('preferences.todo-color', def_todo)
        config.set('preferences.custom-marker-color', def_cust)

        self.comp_color.set_color(gtk.gdk.color_parse(def_comp))
        self.todo_color.set_color(gtk.gdk.color_parse(def_todo))
        self.custom_color.set_color(gtk.gdk.color_parse(def_cust))
        for widget in [self.comp_color, self.todo_color, self.custom_color]:
            widget.emit('color-set')

    def add_name_panel(self):
        """
        Name format settings panel
        """

        # a dummy name to be used in the examples
        self.examplename = Name()
        self.examplename.set_title('Dr.')
        self.examplename.set_first_name('Edwin Jose')
        self.examplename.set_surname_prefix('von der')
        self.examplename.set_surname('Smith')
        self.examplename.set_suffix('Sr')
        self.examplename.set_patronymic('Wilson')
        self.examplename.set_call_name('Ed')

        table = gtk.Table(2, 2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        # get the model for the combo and the treeview
        active = _nd.get_default_format()
        self.fmt_model, active = self._build_name_format_model(active)

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

    def _build_name_format_model(self, active):
        """
        Create a common model for ComboBox and TreeView
        """
        name_format_model = gtk.ListStore(gobject.TYPE_INT, 
                                          gobject.TYPE_STRING, 
                                          gobject.TYPE_STRING, 
                                          gobject.TYPE_STRING)
        index = 0        
        the_index = 0
        for num, name, fmt_str, act in _nd.get_name_format():
            translation = fmt_str
            for key in Utils.get_keywords():
                if key in translation:
                    translation = translation.replace(key, Utils.get_translation_from_keyword(key))
            self.examplename.set_display_as(num)
            name_format_model.append(
                row=[num, translation, fmt_str, _nd.display_name(self.examplename)])
            if num == active: the_index = index
            index += 1
        return name_format_model, the_index

    def __new_name(self, obj):
        lyst = ["%s, %s %s (%s)" % (_("Surname"), _("Given"), _("Suffix"), 
                                    _("Common")),
                "%s, %s %s (%s)" % (_("Surname"), _("Given"), _("Suffix"), 
                                    _("Call")),
                "%s, %s %s (%s)" % (_("SURNAME"), _("Given"), _("Suffix"), 
                                    _("Call")),
                "%s, %s (%s)" % (_("Surname"), _("Given"), _("Common")),
                "%s, %s (%s)" % (_("Surname"), _("Given"), _("Call")),
                "%s %s" % (_("Given"), _("Surname")),
                "%s %s, %s" % (_("Given"), _("Surname"), _("Suffix")),
                "%s %s %s" % (_("Given"), _("Surname"), _("Patronymic")),
                "%s, %s %s (%s)" % (_("SURNAME"), _("Given"), _("Suffix"), 
                                    _("Common")),
                "%s, %s (%s)" % (_("SURNAME"), _("Given"), _("Common")),
                "%s, %s (%s)" % (_("SURNAME"), _("Given"), _("Call")),
                "%s %s" % (_("Given"), _("SURNAME")),
                "%s %s, %s" % (_("Given"), _("SURNAME"), _("Suffix")),
                "%s /%s/" % (_("Given"), _("SURNAME")),
                ]
        fmtlyst = ["%s, %s %s (%s)" % ("Surname", "Given", "Suffix", 
                                       "Common"),
                   "%s, %s %s (%s)" % ("Surname", "Given", "Suffix", 
                                       "Call"),
                   "%s, %s %s (%s)" % ("SURNAME", "Given", "Suffix", 
                                       "Call"),
                   "%s, %s (%s)" % ("Surname", "Given", "Common"),
                   "%s, %s (%s)" % ("Surname", "Given", "Call"),
                   "%s %s" % ("Given", "Surname"),
                   "%s %s, %s" % ("Given", "Surname", "Suffix"),
                   "%s %s %s" % ("Given", "Surname", "Patronymic"),
                   "%s, %s %s (%s)" % ("SURNAME", "Given", "Suffix", 
                                       "Common"),
                   "%s, %s (%s)" % ("SURNAME", "Given", "Common"),
                   "%s, %s (%s)" % ("SURNAME", "Given", "Call"),
                   "%s %s" % ("Given", "SURNAME"),
                   "%s %s, %s" % ("Given", "SURNAME", "Suffix"),
                   "%s /%s/" % ("Given", "SURNAME"),
                   ]
        rand = int(random.random() * len(lyst))
        f = lyst[rand]
        fmt = fmtlyst[rand]
        i = _nd.add_name_format(f, fmt)
        node = self.fmt_model.append(row=[i, f, fmt, 
                                   _nd.format_str(self.examplename, fmt)])
        path = self.fmt_model.get_path(node)
        self.format_list.set_cursor(path, 
                                    focus_column=self.name_column, 
                                    start_editing=True)
        self.edit_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.insert_button.set_sensitive(False)
        self.__current_path = path
        self.__current_text = f

    def __edit_name(self, obj):
        store, node = self.format_list.get_selection().get_selected()
        path = self.fmt_model.get_path(node)
        self.__current_path = path
        self.edit_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.insert_button.set_sensitive(False)
        self.format_list.set_cursor(path, 
                                    focus_column=self.name_column, 
                                    start_editing=True)

    def __check_for_name(self, name, oldnode):
        """
        Check to see if there is another name the same as name
        in the format list. Don't compare with self (oldnode).
        """
        model = self.fmt_obox.get_model()
        iter = model.get_iter_first()
        while iter is not None:
            othernum = model.get_value(iter, COL_NUM)
            oldnum = model.get_value(oldnode, COL_NUM)
            if othernum == oldnum: 
                pass# skip comparison with self
            else:
                othername = model.get_value(iter, COL_NAME)
                if othername == name:
                    return True
            iter = model.iter_next(iter)
        return False

    def __cancel_change(self, obj):
        self.__change_name("", self.__current_path, self.__current_text)

    def __change_name(self, text, path, new_text):
        """
        If the new string is empty, do nothing. Otherwise, renaming the
        database is simply changing the contents of the name file.
        """
        if len(new_text) > 0 and text != new_text:
            # build a pattern from translated pattern:
            pattern = new_text
            if (len(new_text) > 2 and 
                new_text[0] == '"' and 
                new_text[-1] == '"'):
                pass
            else:
                for key in Utils.get_translations():
                    if key in pattern:
                        pattern = pattern.replace(key, Utils.get_keyword_from_translation(key))
            # now build up a proper translation:
            translation = pattern
            if (len(new_text) > 2 and 
                new_text[0] == '"' and 
                new_text[-1] == '"'):
                pass
            else:
                for key in Utils.get_keywords():
                    if key in translation:
                        translation = translation.replace(key, Utils.get_translation_from_keyword(key))
            num, name, fmt = self.selected_fmt[COL_NUM:COL_EXPL]
            node = self.fmt_model.get_iter(path)
            oldname = self.fmt_model.get_value(node, COL_NAME)
            # check to see if this pattern already exists
            if self.__check_for_name(translation, node):
                ErrorDialog(_("This format exists already."), 
                                           translation)
                self.edit_button.emit('clicked')
                return
            # else, change the name
            self.edit_button.set_sensitive(True)
            self.remove_button.set_sensitive(True)
            self.insert_button.set_sensitive(True)
            exmpl = _nd.format_str(self.examplename, pattern)
            self.fmt_model.set(self.iter, COL_NAME, translation, 
                               COL_FMT, pattern, 
                               COL_EXPL, exmpl)
            self.selected_fmt = (num, translation, pattern, exmpl)
            _nd.edit_name_format(num, translation, pattern)
            self.dbstate.db.name_formats = _nd.get_name_format(only_custom=True, 
                                                               only_active=False)

    def __format_change(self, obj):
        try:
            t = (_nd.format_str(self.name, escape(obj.get_text())))
            self.valid = True
        except NameDisplayError:
            t = _("Invalid or incomplete format definition.")
            self.valid = False
        self.fmt_model.set(self.iter, COL_EXPL, t)

    def _build_custom_name_ui(self):
        """
        UI to manage the custom name formats
        """

        table = gtk.Table(2, 3)
        table.set_border_width(6)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        # make a treeview for listing all the name formats
        format_tree = gtk.TreeView(self.fmt_model)
        name_renderer = gtk.CellRendererText()
        name_column = gtk.TreeViewColumn(_('Format'), 
                                         name_renderer, 
                                         text=COL_NAME)
        name_renderer.set_property('editable', False)
        name_renderer.connect('edited', self.__change_name)
        name_renderer.connect('editing-canceled', self.__cancel_change)
        self.name_renderer = name_renderer
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
        format_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        format_sw.add(format_tree)
        format_sw.set_shadow_type(gtk.SHADOW_IN)
        table.attach(format_sw, 0, 3, 0, 1, yoptions=gtk.FILL|gtk.EXPAND)

        # to hold the values of the selected row of the tree and the iter
        self.selected_fmt = ()
        self.iter = None

        self.insert_button = gtk.Button(stock=gtk.STOCK_ADD)
        self.insert_button.connect('clicked', self.__new_name)
                              #self.cb_insert_fmt_str)

        self.edit_button = gtk.Button(stock=gtk.STOCK_EDIT)
        self.edit_button.connect('clicked', self.__edit_name)
                                 #self.cb_edit_fmt_str)
        self.edit_button.set_sensitive(False)

        self.remove_button = gtk.Button(stock=gtk.STOCK_REMOVE)
        self.remove_button.connect('clicked', self.cb_del_fmt_str)
        self.remove_button.set_sensitive(False)
        
        table.attach(self.insert_button, 0, 1, 1, 2, yoptions=0)
        table.attach(self.remove_button, 1, 2, 1, 2, yoptions=0)
        table.attach(self.edit_button,   2, 3, 1, 2, yoptions=0)
        self.format_list = format_tree
        self.name_column = name_column
        return table

    def name_changed_check(self):
        """
        Method to check for a name change. Called by Name Edit Dialog.
        """
        obj = self.fmt_obox
        the_list = obj.get_model()
        the_iter = obj.get_active_iter()
        format = the_list.get_value(the_iter, COL_FMT)
        if format != self.old_format:
            # Yes a change; call the callback
            self.cb_name_changed(obj)

    def cb_name_changed(self, obj):
        """
        Preset name format ComboBox callback
        """
        the_list = obj.get_model()
        the_iter = obj.get_active_iter()
        new_idx = the_list.get_value(the_iter, COL_NUM)
        config.set('preferences.name-format', new_idx)
        _nd.set_default_format(new_idx)
        self.uistate.emit('nameformat-changed')
        
    def cb_format_tree_select(self, tree_selection):
        """
        Name format editor TreeView callback
        
        Remember the values of the selected row (self.selected_fmt, self.iter)
        and set the Remove and Edit button sensitivity
        
        """
        model, self.iter = tree_selection.get_selected()
        if self.iter is None:
            tree_selection.select_path(0)
            model, self.iter = tree_selection.get_selected()
        self.selected_fmt = model.get(self.iter, 0, 1, 2)
        idx = self.selected_fmt[COL_NUM] < 0
        self.remove_button.set_sensitive(idx)
        self.edit_button.set_sensitive(idx)
        self.name_renderer.set_property('editable', idx)


    def cb_edit_fmt_str(self, obj):
        """
        Name format editor Edit button callback
        """
        num, name, fmt = self.selected_fmt[COL_NUM:COL_EXPL]
        dlg = NameFormatEditDlg(name, fmt, self.examplename)
        dlg.dlg.set_transient_for(self.window)
        (res, name, fmt) = dlg.run()

        if res == gtk.RESPONSE_OK and (name != self.selected_fmt[COL_NAME] or 
                                       fmt != self.selected_fmt[COL_FMT]):
            exmpl = _nd.format_str(self.examplename, fmt)
            self.fmt_model.set(self.iter, COL_NAME, name, 
                               COL_FMT, fmt, 
                               COL_EXPL, exmpl)
            self.selected_fmt = (num, name, fmt, exmpl)
            _nd.edit_name_format(num, name, fmt)

            self.dbstate.db.name_formats = _nd.get_name_format(only_custom=True, 
                                                               only_active=False)
        
    def cb_insert_fmt_str(self, obj):
        """
        Name format editor Insert button callback
        """
        dlg = NameFormatEditDlg('', '', self.examplename)
        dlg.dlg.set_transient_for(self.window)
        (res, n, f) = dlg.run()

        if res == gtk.RESPONSE_OK:
            i = _nd.add_name_format(n, f)
            self.fmt_model.append(row=[i, n, f, 
                                       _nd.format_str(self.examplename, f)])

        self.dbstate.db.name_formats = _nd.get_name_format(only_custom=True, 
                                                           only_active=False)
        
    def cb_del_fmt_str(self, obj):
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
        row = 0
        table = gtk.Table(4, 4)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        # Display name:
        self.examplename = Name()
        self.examplename.set_title('Dr.')
        self.examplename.set_first_name('Edwin Jose')
        self.examplename.set_surname_prefix('von der')
        self.examplename.set_surname('Smith')
        self.examplename.set_suffix('Sr')
        self.examplename.set_patronymic('Wilson')
        self.examplename.set_call_name('Ed')
        # get the model for the combo and the treeview
        active = _nd.get_default_format()
        self.fmt_model, active = self._build_name_format_model(active)
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
        lwidget = BasicLabel("%s: " % _('Name format'))
        lwidget.set_use_underline(True)
        lwidget.set_mnemonic_widget(self.fmt_obox)
        hbox = gtk.HBox()
        btn = gtk.Button("%s..." % _('Edit') )
        btn.connect('clicked', self.cb_name_dialog)
        hbox.pack_start(self.fmt_obox, expand=True, fill=True)
        hbox.pack_start(btn, expand=False, fill=False)
        table.attach(lwidget, 0, 1, row, row+1, yoptions=0)
        table.attach(hbox,    1, 3, row, row+1, yoptions=0)
        row += 1

        # Date format:
        obox = gtk.combo_box_new_text()
        formats = DateHandler.get_date_formats()
        for item in formats:
            obox.append_text(item)
        active = config.get('preferences.date-format')
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect('changed', self.date_format_changed)
        lwidget = BasicLabel("%s: " % _('Date format'))
        table.attach(lwidget, 0, 1, row, row+1, yoptions=0)
        table.attach(obox, 1, 3, row, row+1, yoptions=0)
        row += 1
        
        # Calendar format on report:
        obox = gtk.combo_box_new_text()
        formats = DateHandler.get_calendar_formats()
        for item in formats:
            obox.append_text(item)
        active = config.get('preferences.calendar-format-report')
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect('changed', self.date_calendar_changed)
        lwidget = BasicLabel("%s: " % _('Calendar format on reports'))
        table.attach(lwidget, 0, 1, row, row+1, yoptions=0)
        table.attach(obox, 1, 3, row, row+1, yoptions=0)
        row += 1

        # Surname guessing:
        obox = gtk.combo_box_new_text()
        formats = _surname_styles
        for item in formats:
            obox.append_text(item)
        obox.set_active(config.get('behavior.surname-guessing'))
        obox.connect('changed', 
                     lambda obj: config.set('behavior.surname-guessing', 
                                            obj.get_active()))
        lwidget = BasicLabel("%s: " % _('Surname guessing'))
        table.attach(lwidget, 0, 1, row, row+1, yoptions=0)
        table.attach(obox, 1, 3, row, row+1, yoptions=0)
        row += 1

        # Status bar:
        obox = gtk.combo_box_new_text()
        formats = [_("Active person's name and ID"), 
                   _("Relationship to home person")]
        for item in formats:
            obox.append_text(item)
        active = config.get('interface.statusbar')
        if active < 2:
            obox.set_active(0)
        else:
            obox.set_active(1)
        obox.connect('changed', 
                     lambda obj: config.set('interface.statusbar', 2*obj.get_active()))
        lwidget = BasicLabel("%s: " % _('Status bar'))
        table.attach(lwidget, 0, 1, row, row+1, yoptions=0)
        table.attach(obox,    1, 3, row, row+1, yoptions=0)
        row += 1

        # Text in sidebar:
        self.add_checkbox(table, 
                          _("Show text in sidebar buttons (requires restart)"), 
                          row, 'interface.sidebar-text', stop=3)
        row += 1
        return table

    def add_text_panel(self):
        row = 0
        table = gtk.Table(6, 8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)
        self.add_entry(table, _('Missing surname'), row, 
                       'preferences.no-surname-text')
        row += 1
        self.add_entry(table, _('Missing given name'), row, 
                       'preferences.no-given-text')
        row += 1
        self.add_entry(table, _('Missing record'), row, 
                       'preferences.no-record-text')
        row += 1
        self.add_entry(table, _('Private surname'), row, 
                       'preferences.private-surname-text')
        row += 1
        self.add_entry(table, _('Private given name'), row, 
                       'preferences.private-given-text')
        row += 1
        self.add_entry(table, _('Private record'), row, 
                       'preferences.private-record-text')
        row += 1
        return table

    def cb_name_dialog(self, obj):
        the_list = self.fmt_obox.get_model()
        the_iter = self.fmt_obox.get_active_iter()
        self.old_format = the_list.get_value(the_iter, COL_FMT)
        win = DisplayNameEditor(self.uistate, self.dbstate, self.track, self)

    def date_format_changed(self, obj):

        config.set('preferences.date-format', obj.get_active())
        OkDialog(_('Change is not immediate'), 
                 _('Changing the data format will not take '
                   'effect until the next time Gramps is started.'))

    def date_calendar_changed(self, obj):
 
        config.set('preferences.calendar-format-report', obj.get_active())
        OkDialog(_('Change is not immediate'), 
                 _('Changing the data format will not take '
                   'effect until the next time Gramps is started.'))
    
    def add_date_panel(self):
        table = gtk.Table(2, 7)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        self.add_pos_int_entry(table, 
                _('Date about range'),
                0, 'behavior.date-about-range', self.update_int_entry)
        self.add_pos_int_entry(table, 
                _('Date after range'),
                1, 'behavior.date-after-range', self.update_int_entry)
        self.add_pos_int_entry(table, 
                _('Date before range'),
                2, 'behavior.date-before-range', self.update_int_entry)
        self.add_pos_int_entry(table, 
                _('Maximum age probably alive'),
                3, 'behavior.max-age-prob-alive', self.update_int_entry)
        self.add_pos_int_entry(table, 
                _('Maximum sibling age difference'),
                4, 'behavior.max-sib-age-diff', self.update_int_entry)
        self.add_pos_int_entry(table, 
                _('Minimum years between generations'),
                5, 'behavior.min-generation-years', self.update_int_entry)
        self.add_pos_int_entry(table, 
                _('Average years between generations'),
                6, 'behavior.avg-generation-gap', self.update_int_entry)
        self.add_pos_int_entry(table,
                _('Markup for invalid date format'), 
                7, 'preferences.invalid-date-format', self.update_entry)

        return table
        
    def add_behavior_panel(self):
        table = gtk.Table(3, 8)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        self.add_checkbox(table, 
                _('Add default source on import'), 
                0, 'preferences.default-source')
        self.add_checkbox(table, 
                _('Enable spelling checker'), 
                1, 'behavior.spellcheck')
        self.add_checkbox(table, 
                _('Display Tip of the Day'), 
                2, 'behavior.use-tips')
        self.add_checkbox(table, 
                _('Use shading in Relationship View'), 
                3, 'preferences.relation-shade')
        self.add_checkbox(table, 
                _('Display edit buttons on Relationship View'), 
                4, 'interface.releditbtn')
        self.add_checkbox(table, 
                _('Remember last view displayed'), 
                5, 'preferences.use-last-view')
        self.add_pos_int_entry(table, 
                _('Max generations for relationships'),
                6, 'behavior.generation-depth', self.update_gen_depth)
        self.path_entry = gtk.Entry()
        self.add_path_box(table, 
                _('Base path for relative media paths'),
                7, self.path_entry, self.dbstate.db.get_mediapath(),
                self.set_mediapath, self.select_mediapath)

        return table

    def add_database_panel(self):
        table = gtk.Table(2, 2)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        self.add_entry(table, 
                _('Database path'), 
                0, 'behavior.database-path')
        self.add_checkbox(table, 
                _('Automatically load last database'), 
                1, 'behavior.autoload')
                
        return table
        
    def add_checkbox(self, table, label, index, constant, start=1, stop=9):
        checkbox = gtk.CheckButton(label)
        checkbox.set_active(config.get(constant))
        checkbox.connect('toggled', self.update_checkbox, constant)
        table.attach(checkbox, start, stop, index, index+1, yoptions=0)

    def add_radiobox(self, table, label, index, constant, group, column):
        radiobox = gtk.RadioButton(group,label)
        if config.get(constant) == True:
            radiobox.set_active(True)
        radiobox.connect('toggled', self.update_radiobox, constant)
        table.attach(radiobox, column, column+1, index, index+1, yoptions=0)
        return radiobox

    def add_text(self, table, label, index):
        text = gtk.Label()
        text.set_line_wrap(True)
        text.set_alignment(0.,0.)
        text.set_text(label)
        table.attach(text, 1, 9, index, index+1, yoptions=0)

    def add_path_box(self, table, label, index, entry, path, callback_label, 
                     callback_sel):
        """ Add an entry to give in path and a select button to open a 
            dialog. 
            Changing entry calls callback_label
            Clicking open button call callback_sel
        """
        lwidget = BasicLabel("%s: " %label)
        hbox = gtk.HBox()
        if path:
            entry.set_text(path)
        entry.connect('changed', callback_label)
        btn = gtk.Button()
        btn.connect('clicked', callback_sel)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
        image.show()
        btn.add(image)
        hbox.pack_start(entry, expand=True, fill=True)
        hbox.pack_start(btn, expand=False, fill=False)
        table.attach(lwidget, 1, 2, index, index+1, yoptions=0, 
                     xoptions=gtk.FILL)
        table.attach(hbox, 2, 3, index, index+1, yoptions=0)

    def add_entry(self, table, label, index, constant, callback=None):
        if not callback:
            callback = self.update_entry
        lwidget = BasicLabel("%s: " % label)
        entry = gtk.Entry()
        entry.set_text(config.get(constant))
        entry.connect('changed', callback, constant)
        table.attach(lwidget, 0, 1, index, index+1, yoptions=0, 
                     xoptions=gtk.FILL)
        table.attach(entry, 1, 2, index, index+1, yoptions=0)

    def add_pos_int_entry(self, table, label, index, constant, callback=None):
        """ entry field for positive integers
        """
        lwidget = BasicLabel("%s: " % label)
        entry = gtk.Entry()
        entry.set_text(str(config.get(constant)))
        if callback:
            entry.connect('changed', callback, constant)
        table.attach(lwidget, 1, 2, index, index+1, yoptions=0, 
                     xoptions=gtk.FILL)
        table.attach(entry, 2, 3, index, index+1, yoptions=0)

    def add_color(self, table, label, index, constant):
        lwidget = BasicLabel("%s: " % label)
        hexval = config.get(constant)
        color = gtk.gdk.color_parse(hexval)
        entry = gtk.ColorButton(color=color)
        color_hex_label = BasicLabel(hexval)
        entry.connect('color-set', self.update_color, constant, color_hex_label)
        table.attach(lwidget, 0, 1, index, index+1, yoptions=0, 
                     xoptions=gtk.FILL)
        table.attach(entry, 1, 2, index, index+1, yoptions=0, xoptions=0)
        table.attach(color_hex_label, 2, 3, index, index+1, yoptions=0)
        return entry

    def set_mediapath(self, *obj):
        if self.path_entry.get_text().strip():
            self.dbstate.db.set_mediapath(self.path_entry.get_text())
        else:
            self.dbstate.db.set_mediapath(None)

    def select_mediapath(self, *obj):
        f = gtk.FileChooserDialog(
            _("Select media directory"),
            action=gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER,
            buttons=(gtk.STOCK_CANCEL,
                     gtk.RESPONSE_CANCEL,
                     gtk.STOCK_APPLY,
                     gtk.RESPONSE_OK))
        mpath = self.dbstate.db.get_mediapath()
        if not mpath:
            mpath = const.HOME_DIR
        f.set_current_folder(os.path.dirname(mpath))

        status = f.run()
        if status == gtk.RESPONSE_OK:
            val = Utils.get_unicode_path(f.get_filename())
            if val:
                self.path_entry.set_text(val)
        f.destroy()

    def update_int_entry(self, obj, constant):
        try:
            config.set(constant, int(obj.get_text()))
        except:
            print "WARNING: ignoring invalid value for '%s'" % constant

    def update_entry(self, obj, constant):
        config.set(constant, unicode(obj.get_text()))

    def update_idformat_entry(self, obj, constant):
        config.set(constant, unicode(obj.get_text()))
        self.dbstate.db.set_prefixes(
            config.get('preferences.iprefix'),
            config.get('preferences.oprefix'),
            config.get('preferences.fprefix'),
            config.get('preferences.sprefix'),
            config.get('preferences.pprefix'),
            config.get('preferences.eprefix'),
            config.get('preferences.rprefix'),
            config.get('preferences.nprefix') )

    def update_gen_depth(self, obj, constant):
        ok = True
        if not obj.get_text():
            return
        try:
            intval = int(obj.get_text())
        except:
            intval = config.get(constant)
            ok = False
        if intval < 0 :
            intval = config.get(constant)
            ok = False
        if ok:
            config.set(constant, intval)
            #immediately use this value in displaystate.
            self.uistate.set_gendepth(intval)
        else:
            obj.set_text(str(intval))

    def update_color(self, obj, constant, color_hex_label):
        color = obj.get_color()
        hexval = "#%02x%02x%02x" % (color.red/256, 
                                    color.green/256, 
                                    color.blue/256)
        color_hex_label.set_text(hexval)
        config.set(constant, hexval)

    def update_checkbox(self, obj, constant):
        config.set(constant, obj.get_active())

    def update_radiobox(self, obj, constant):
        config.set(constant, obj.get_active())

    def build_menu_names(self, obj):
        return (_('Preferences'), None)

    # FIXME: is this needed?
    def _set_button(self, stock):
        button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
        image.show()
        button.add(image)
        button.show()
        return button
    
class NameFormatEditDlg(object):
    """
    """
    
    def __init__(self, fmt_name, fmt_str, name):
        self.fmt_name = fmt_name
        self.fmt_str = fmt_str
        self.name = name
        self.valid = True
        self.top = Glade()
        
        self.dlg = self.top.get_object('namefmt_edit')
        ManagedWindow.set_titles(self.dlg, None, _('Name Format Editor'))
        
        self.examplelabel = self.top.get_object('example_label')
        
        self.nameentry = self.top.get_object('name_entry')
        self.nameentry.set_text('<span weight="bold">%s</span>' % self.fmt_name)
        self.nameentry.set_use_markup(True)
        
        self.formatentry = self.top.get_object('format_entry')
        self.formatentry.connect('changed', self.cb_format_changed)
        self.formatentry.set_text(self.fmt_str)
        
    def run(self):
        running = True
        while running:
            self.response = self.dlg.run()

            running = False
            self.fmt_name = self.nameentry.get_text()
            self.fmt_str = self.formatentry.get_text()
            
            if self.response == gtk.RESPONSE_OK:
                if not self.valid:
                    q = QuestionDialog2(
                        _('The format definition is invalid'), 
                        _('What would you like to do?'), 
                        _('_Continue anyway'), _('_Modify format'), 
                        parent=self.dlg)
                    running = not q.run()
                    self.response = gtk.RESPONSE_CANCEL
                elif self.fmt_name == '' and self.fmt_str == '':
                    self.response = gtk.RESPONSE_CANCEL
                elif (self.fmt_name == '') ^ (self.fmt_str == ''):
                    ErrorDialog(
                        _('Both Format name and definition have to be defined.'), 
                        parent=self.dlg)
                    running = True
                                    
        self.dlg.destroy()
        return (self.response, self.fmt_name, self.fmt_str)

    def cb_format_changed(self, obj):
        try:
            t = (_nd.format_str(self.name, escape(obj.get_text())))
            sample = '<span weight="bold" style="italic">%s</span>' % t
            self.valid = True
        except NameDisplayError:
            t = _("Invalid or incomplete format definition.")
            sample = '<span foreground="#FF0000">%s</span>' % t
            self.valid = False

        self.examplelabel.set_text(sample)
        self.examplelabel.set_use_markup(True)
        self.nameentry.set_text('<span weight="bold">%s</span>' % obj.get_text())
        self.nameentry.set_use_markup(True)
