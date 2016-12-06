#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import random
import os
from xml.sax.saxutils import escape
import collections

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import HOME_DIR, URL_WIKISTRING
from gramps.gen.datehandler import get_date_formats
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.name import NameDisplayError
from gramps.gen.utils.alive import update_constants
from gramps.gen.utils.file import media_path
from gramps.gen.utils.keyword import (get_keywords, get_translation_from_keyword,
                               get_translations, get_keyword_from_translation)
from gramps.gen.lib import Date, FamilyRelType
from gramps.gen.lib import Name, Surname, NameOriginType
from .managedwindow import ManagedWindow
from .widgets import MarkupLabel, BasicLabel
from .dialog import ErrorDialog, QuestionDialog2, OkDialog
from .glade import Glade
from gramps.gen.plug.utils import available_updates
from .plug import PluginWindows
from gramps.gen.errors import WindowActiveError
from .spell import HAVE_GTKSPELL
from gramps.gen.constfunc import win
_ = glocale.translation.gettext

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
class DisplayNameEditor(ManagedWindow):
    def __init__(self, uistate, dbstate, track, dialog):
        # Assumes that there are two methods: dialog.name_changed_check(),
        # and dialog._build_custom_name_ui()
        ManagedWindow.__init__(self, uistate, track, DisplayNameEditor)
        self.dialog = dialog
        self.dbstate = dbstate
        self.set_window(
            Gtk.Dialog(_('Display Name Editor'),
                       buttons=(_('_Close'), Gtk.ResponseType.CLOSE)),
            None, _('Display Name Editor'), None)
        grid = self.dialog._build_custom_name_ui()
        label = Gtk.Label(label=_("""The following keywords are replaced with the appropriate name parts:<tt>
  <b>Given</b>   - given name (first name)     <b>Surname</b>  - surnames (with prefix and connectors)
  <b>Title</b>   - title (Dr., Mrs.)           <b>Suffix</b>   - suffix (Jr., Sr.)
  <b>Call</b>    - call name                   <b>Nickname</b> - nick name
  <b>Initials</b>- first letters of given      <b>Common</b>   - nick name, call, or first of given
  <b>Prefix</b>  - all prefixes (von, de)
Surnames:
  <b>Rest</b>      - non primary surnames    <b>Notpatronymic</b>- all surnames, except pa/matronymic &amp; primary
  <b>Familynick</b>- family nick name        <b>Rawsurnames</b>  - surnames (no prefixes and connectors)
  <b>Primary, Primary[pre] or [sur] or [con]</b>- full primary surname, prefix, surname only, connector
  <b>Patronymic, or [pre] or [sur] or [con]</b> - full pa/matronymic surname, prefix, surname only, connector
</tt>
UPPERCASE keyword forces uppercase. Extra parentheses, commas are removed. Other text appears literally.

<b>Example</b>: Dr. Edwin Jose von der Smith and Weston Wilson Sr ("Ed") - Underhills
     <i>Edwin Jose</i>: Given, <i>von der</i>: Prefix, <i>Smith</i> and <i>Weston</i>: Primary, <i>and</i>: [con], <i>Wilson</i>: Patronymic,
     <i>Dr.</i>: Title, <i>Sr</i>: Suffix, <i>Ed</i>: Nickname, <i>Underhills</i>: Familynick, <i>Jose</i>: Call.
"""))
        label.set_use_markup(True)
        self.window.vbox.pack_start(label, False, True, 0)
        self.window.vbox.pack_start(grid, True, True, 0)
        self.window.set_default_size(600, 550)
        self.window.connect('response', self.close)
        self.show()
    def close(self, *obj):
        self.dialog.name_changed_check()
        ManagedWindow.close(self, *obj)

    def build_menu_names(self, obj):
        return (_(" Name Editor"), None)


#-------------------------------------------------------------------------
#
# ConfigureDialog
#
#-------------------------------------------------------------------------

class ConfigureDialog(ManagedWindow):
    """
    Base class for configuration dialogs. They provide a Notebook, to which
    pages are added with configuration options, and a Cancel and Save button.
    On save, a config file on which the dialog works, is saved to disk, and
    a callback called.
    """
    def __init__(self, uistate, dbstate, configure_page_funcs, configobj,
                 configmanager,
                 dialogtitle=_("Addon Manager"), on_close=None):
        """
        Set up a configuration dialog
        :param uistate: a DisplayState instance
        :param dbstate: a DbState instance
        :param configure_page_funcs: a list of function that return a tuple
            (str, Gtk.Widget). The string is used as label for the
            configuration page, and the widget as the content of the
            configuration page
        :param configobj: the unique object that is configured, it must be
            identifiable (id(configobj)). If the configure dialog of the
            configobj is already open, a WindowActiveError will be
            raised. Grab this exception in the calling method
        :param configmanager: a configmanager object. Several convenience
            methods are present in ConfigureDialog to set up widgets that
            write changes directly via this configmanager.
        :param dialogtitle: the title of the configuration dialog
        :param on_close: callback that is called on close
        """
        self.dbstate = dbstate
        self.__config = configmanager
        ManagedWindow.__init__(self, uistate, [], configobj)
        self.set_window(
            Gtk.Dialog(dialogtitle,
                       buttons=(_('_Close'), Gtk.ResponseType.CLOSE)),
                       None, dialogtitle, None)
        self.panel = Gtk.Notebook()
        self.panel.set_scrollable(True)
        self.window.vbox.pack_start(self.panel, True, True, 0)
        self.__on_close = on_close
        self.window.connect('response', self.done)

        self.__setup_pages(configure_page_funcs)

        self.show()

    def __setup_pages(self, configure_page_funcs):
        """
        This method builds the notebookpages in the panel
        """
        if isinstance(configure_page_funcs, collections.Callable):
            pages = configure_page_funcs()
        else:
            pages = configure_page_funcs
        for func in pages:
            labeltitle, widget = func(self)
            self.panel.append_page(widget, MarkupLabel(labeltitle))

    def done(self, obj, value):
        if self.__on_close:
            self.__on_close()
        self.close()

    def update_int_entry(self, obj, constant):
        """
        :param obj: an object with get_text method that should contain an
            integer
        :param constant: the config setting to which the integer value must be
            saved
        """
        try:
            self.__config.set(constant, int(obj.get_text()))
        except:
            print("WARNING: ignoring invalid value for '%s'" % constant)

    def update_markup_entry(self, obj, constant):
        """
        :param obj: an object with get_text method
        :param constant: the config setting to which the text value must be
            saved
        """
        try:
            obj.get_text() % 'test_markup'
        except TypeError:
            print("WARNING: ignoring invalid value for '%s'" % constant)
            ErrorDialog(
                _("Invalid or incomplete format definition."),
                obj.get_text(), parent=self.window)
            obj.set_text('<b>%s</b>')
        except ValueError:
            print("WARNING: ignoring invalid value for '%s'" % constant)
            ErrorDialog(
                _("Invalid or incomplete format definition."),
                obj.get_text(), parent=self.window)
            obj.set_text('<b>%s</b>')

        self.__config.set(constant, obj.get_text())

    def update_entry(self, obj, constant):
        """
        :param obj: an object with get_text method
        :param constant: the config setting to which the text value must be
            saved
        """
        self.__config.set(constant, obj.get_text())

    def update_color(self, obj, constant, color_hex_label):
        rgba = obj.get_rgba()
        hexval = "#%02x%02x%02x" % (int(rgba.red * 255),
                                    int(rgba.green * 255),
                                    int(rgba.blue * 255))
        color_hex_label.set_text(hexval)
        self.__config.set(constant, hexval)

    def update_checkbox(self, obj, constant, config=None):
        if not config:
            config = self.__config
        config.set(constant, obj.get_active())

    def update_radiobox(self, obj, constant):
        self.__config.set(constant, obj.get_active())

    def update_combo(self, obj, constant):
        """
        :param obj: the ComboBox object
        :param constant: the config setting to which the value must be saved
        """
        self.__config.set(constant, obj.get_active())

    def update_slider(self, obj, constant):
        """
        :param obj: the HScale object
        :param constant: the config setting to which the value must be saved
        """
        self.__config.set(constant, int(obj.get_value()))

    def update_spinner(self, obj, constant):
        """
        :param obj: the SpinButton object
        :param constant: the config setting to which the value must be saved
        """
        self.__config.set(constant, int(obj.get_value()))

    def add_checkbox(self, grid, label, index, constant, start=1, stop=9,
                     config=None, extra_callback=None):
        if not config:
            config = self.__config
        checkbox = Gtk.CheckButton(label=label)
        checkbox.set_active(config.get(constant))
        checkbox.connect('toggled', self.update_checkbox, constant, config)
        if extra_callback:
            checkbox.connect('toggled', extra_callback)
        grid.attach(checkbox, start, index, stop - start, 1)
        return checkbox

    def add_radiobox(self, grid, label, index, constant, group, column,
                     config=None):
        if not config:
            config = self.__config
        radiobox = Gtk.RadioButton.new_with_mnemonic_from_widget(group, label)
        if config.get(constant) == True:
            radiobox.set_active(True)
        radiobox.connect('toggled', self.update_radiobox, constant)
        grid.attach(radiobox, column, index, 1, 1)
        return radiobox

    def add_text(self, grid, label, index, config=None, line_wrap=True):
        if not config:
            config = self.__config
        text = Gtk.Label()
        text.set_line_wrap(line_wrap)
        text.set_halign(Gtk.Align.START)
        text.set_text(label)
        grid.attach(text, 1, index, 8, 1)

    def add_path_box(self, grid, label, index, entry, path, callback_label,
                     callback_sel, config=None):
        """ Add an entry to give in path and a select button to open a
            dialog.
            Changing entry calls callback_label
            Clicking open button call callback_sel
        """
        if not config:
            config = self.__config
        lwidget = BasicLabel("%s: " %label)
        hbox = Gtk.Box()
        if path:
            entry.set_text(path)
        entry.connect('changed', callback_label)
        btn = Gtk.Button()
        btn.connect('clicked', callback_sel)
        image = Gtk.Image()
        image.set_from_icon_name('document-open', Gtk.IconSize.BUTTON)
        image.show()
        btn.add(image)
        hbox.pack_start(entry, True, True, 0)
        hbox.pack_start(btn, False, False, 0)
        hbox.set_hexpand(True)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(hbox, 2, index, 1, 1)

    def add_entry(self, grid, label, index, constant, callback=None,
                  config=None, col_attach=0, localized_config=True):
        if not config:
            config = self.__config
        if not callback:
            callback = self.update_entry
        if label:
            lwidget = BasicLabel("%s: " % label)
        entry = Gtk.Entry()
        if localized_config:
            entry.set_text(config.get(constant))
        else: # it needs localizing
            entry.set_text(_(config.get(constant)))
        entry.connect('changed', callback, constant)
        entry.set_hexpand(True)
        if label:
            grid.attach(lwidget, col_attach, index, 1, 1)
            grid.attach(entry, col_attach+1, index, 1, 1)
        else:
            grid.attach(entry, col_attach, index, 1, 1)
        return entry

    def add_pos_int_entry(self, grid, label, index, constant, callback=None,
                          config=None, col_attach=1, helptext=''):
        """ entry field for positive integers
        """
        if not config:
            config = self.__config
        lwidget = BasicLabel("%s: " % label)
        entry = Gtk.Entry()
        entry.set_text(str(config.get(constant)))
        entry.set_tooltip_markup(helptext)
        entry.set_hexpand(True)
        if callback:
            entry.connect('changed', callback, constant)
        grid.attach(lwidget, col_attach, index, 1, 1)
        grid.attach(entry, col_attach+1, index, 1, 1)

    def add_color(self, grid, label, index, constant, config=None, col=0):
        if not config:
            config = self.__config
        lwidget = BasicLabel("%s: " % label)
        hexval = config.get(constant)
        color = Gdk.color_parse(hexval)
        entry = Gtk.ColorButton(color=color)
        color_hex_label = BasicLabel(hexval)
        color_hex_label.set_hexpand(True)
        entry.connect('color-set', self.update_color, constant, color_hex_label)
        grid.attach(lwidget, col, index, 1, 1)
        grid.attach(entry, col+1, index, 1, 1)
        grid.attach(color_hex_label, col+2, index, 1, 1)
        return entry

    def add_combo(self, grid, label, index, constant, opts, callback=None,
                  config=None, valueactive=False, setactive=None):
        """
        A drop-down list allowing selection from a number of fixed options.
        :param opts: A list of options.  Each option is a tuple containing an
        integer code and a textual description.
        If valueactive = True, the constant stores the value, not the position
        in the list
        """
        if not config:
            config = self.__config
        if not callback:
            callback = self.update_combo
        lwidget = BasicLabel("%s: " % label)
        store = Gtk.ListStore(int, str)
        for item in opts:
            store.append(item)
        combo = Gtk.ComboBox(model=store)
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 1)
        if valueactive:
            val = config.get(constant)
            pos = 0
            for nr, item in enumerate(opts):
                if item[-1] == val:
                    pos = nr
                    break
            combo.set_active(pos)
        else:
            if setactive is None:
                combo.set_active(config.get(constant))
            else:
                combo.set_active(setactive)
        combo.connect('changed', callback, constant)
        combo.set_hexpand(True)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(combo, 2, index, 1, 1)
        return combo

    def add_slider(self, grid, label, index, constant, range, callback=None,
                   config=None, width=1):
        """
        A slider allowing the selection of an integer within a specified range.
        :param range: A tuple containing the minimum and maximum allowed values.
        """
        if not config:
            config = self.__config
        if not callback:
            callback = self.update_slider
        lwidget = BasicLabel("%s: " % label)
        adj = Gtk.Adjustment(value=config.get(constant), lower=range[0],
                             upper=range[1], step_increment=1,
                             page_increment=0, page_size=0)
        slider = Gtk.Scale(adjustment=adj)
        slider.set_digits(0)
        slider.set_value_pos(Gtk.PositionType.BOTTOM)
        slider.connect('value-changed', callback, constant)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(slider, 2, index, width, 1)
        return slider

    def add_spinner(self, grid, label, index, constant, range, callback=None,
                   config=None):
        """
        A spinner allowing the selection of an integer within a specified range.
        :param range: A tuple containing the minimum and maximum allowed values.
        """
        if not config:
            config = self.__config
        if not callback:
            callback = self.update_spinner
        lwidget = BasicLabel("%s: " % label)
        adj = Gtk.Adjustment(value=config.get(constant), lower=range[0],
                             upper=range[1], step_increment=1,
                             page_increment=0, page_size=0)
        spinner = Gtk.SpinButton(adjustment=adj, climb_rate=0.0, digits=0)
        spinner.connect('value-changed', callback, constant)
        spinner.set_hexpand(True)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(spinner, 2, index, 1, 1)
        return spinner

#-------------------------------------------------------------------------
#
# AddonManagerPreferences
#
#-------------------------------------------------------------------------
class AddonManagerPreferences(ConfigureDialog):

    def __init__(self, uistate, dbstate):
        page_funcs = (
            self.add_addoncheckupdates_panel,
            self.addon_listing,
            )
        ConfigureDialog.__init__(self, uistate, dbstate, page_funcs,
                                 AddonManagerPreferences, config,
                                 on_close=update_constants)


    def _build_name_format_model(self, active):
        """
        Create a common model for ComboBox and TreeView
        """
        name_format_model = Gtk.ListStore(GObject.TYPE_INT,
                                          GObject.TYPE_STRING,
                                          GObject.TYPE_STRING,
                                          GObject.TYPE_STRING)
        index = 0
        the_index = 0
        for num, name, fmt_str, act in _nd.get_name_format():
            translation = fmt_str
            for key in get_keywords():
                if key in translation:
                    translation = translation.replace(key, get_translation_from_keyword(key))
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
                                    _("Nickname")),
                "%s, %s %s (%s)" % (_("Surname"), _("Name|Common"), _("Suffix"),
                                    _("Nickname")),
                "%s, %s %s" % (_("Surname"), _("Name|Common"), _("Suffix")),
                "%s, %s %s (%s)" % (_("SURNAME"), _("Given"), _("Suffix"),
                                    _("Call")),
                "%s, %s (%s)" % (_("Surname"), _("Given"), _("Name|Common")),
                "%s, %s (%s)" % (_("Surname"), _("Name|Common"), _("Nickname")),
                "%s %s" % (_("Given"), _("Surname")),
                "%s %s, %s" % (_("Given"), _("Surname"), _("Suffix")),
                "%s %s %s" % (_("Given"), _("NotPatronymic"), _("Patronymic")),
                "%s, %s %s (%s)" % (_("SURNAME"), _("Given"), _("Suffix"),
                                    _("Common")),
                "%s, %s (%s)" % (_("SURNAME"), _("Given"), _("Name|Common")),
                "%s, %s (%s)" % (_("SURNAME"), _("Given"), _("Nickname")),
                "%s %s" % (_("Given"), _("SURNAME")),
                "%s %s, %s" % (_("Given"), _("SURNAME"), _("Suffix")),
                "%s /%s/" % (_("Given"), _("SURNAME")),
                "%s %s, %s" % (_("Given"), _("Rawsurnames"), _("Suffix")),
                ]
        #repeat above list, but not translated.
        fmtlyst = ["%s, %s %s (%s)" % (("Surname"), ("Given"), ("Suffix"),
                                    ("Common")),
                "%s, %s %s (%s)" % (("Surname"), ("Given"), ("Suffix"),
                                    ("Nickname")),
                "%s, %s %s (%s)" % (("Surname"), ("Name|Common"), ("Suffix"),
                                    ("Nickname")),
                "%s, %s %s" % (("Surname"), ("Name|Common"), ("Suffix")),
                "%s, %s %s (%s)" % (("SURNAME"), ("Given"), ("Suffix"),
                                    ("Call")),
                "%s, %s (%s)" % (("Surname"), ("Given"), ("Name|Common")),
                "%s, %s (%s)" % (("Surname"), ("Name|Common"), ("Nickname")),
                "%s %s" % (("Given"), ("Surname")),
                "%s %s, %s" % (("Given"), ("Surname"), ("Suffix")),
                "%s %s %s" % (("Given"), ("NotPatronymic"), ("Patronymic")),
                "%s, %s %s (%s)" % (("SURNAME"), ("Given"), ("Suffix"),
                                    ("Common")),
                "%s, %s (%s)" % (("SURNAME"), ("Given"), ("Name|Common")),
                "%s, %s (%s)" % (("SURNAME"), ("Given"), ("Nickname")),
                "%s %s" % (("Given"), ("SURNAME")),
                "%s %s, %s" % (("Given"), ("SURNAME"), ("Suffix")),
                "%s /%s/" % (("Given"), ("SURNAME")),
                "%s %s, %s" % (("Given"), ("Rawsurnames"), ("Suffix")),
                   ]
        rand = int(random.random() * len(lyst))
        f = lyst[rand]
        fmt = fmtlyst[rand]
        i = _nd.add_name_format(f, fmt)
        node = self.fmt_model.append(row=[i, f, fmt,
                                   _nd.format_str(self.examplename, fmt)])
        path = self.fmt_model.get_path(node)
        self.format_list.set_cursor(path, self.name_column, True)
        self.edit_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.insert_button.set_sensitive(False)

    def __edit_name(self, obj):
        store, node = self.format_list.get_selection().get_selected()
        path = self.fmt_model.get_path(node)
        self.edit_button.set_sensitive(False)
        self.remove_button.set_sensitive(False)
        self.insert_button.set_sensitive(False)
        self.format_list.set_cursor(path, self.name_column, True)

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

    def __start_name_editing(self, dummy_renderer, dummy_editable, dummy_path):
        """
        Method called at the start of editing a name format.
        """
        self.format_list.set_tooltip_text(_("Enter to save, Esc to cancel "
                                            "editing"))

    def __cancel_change(self, dummy_renderer):
        """
        Break off the editing of a name format.
        """
        self.format_list.set_tooltip_text('')
        num = self.selected_fmt[COL_NUM]
        if any(fmt[COL_NUM] == num for fmt in self.dbstate.db.name_formats):
            return
        else: # editing a new format not yet in db, cleanup is needed
            self.fmt_model.remove(self.iter)
            _nd.del_name_format(num)
            self.insert_button.set_sensitive(True)

    def __change_name(self, text, path, new_text):
        """
        Called when a name format changed and needs to be stored in the db.
        """
        self.format_list.set_tooltip_text('')
        if len(new_text) > 0 and text != new_text:
            # build a pattern from translated pattern:
            pattern = new_text
            if (len(new_text) > 2 and
                new_text[0] == '"' and
                new_text[-1] == '"'):
                pass
            else:
                for key in get_translations():
                    if key in pattern:
                        pattern = pattern.replace(key, get_keyword_from_translation(key))
            # now build up a proper translation:
            translation = pattern
            if (len(new_text) > 2 and
                new_text[0] == '"' and
                new_text[-1] == '"'):
                pass
            else:
                for key in get_keywords():
                    if key in translation:
                        translation = translation.replace(key, get_translation_from_keyword(key))
            num, name, fmt = self.selected_fmt[COL_NUM:COL_EXPL]
            node = self.fmt_model.get_iter(path)
            oldname = self.fmt_model.get_value(node, COL_NAME)
            # check to see if this pattern already exists
            if self.__check_for_name(translation, node):
                ErrorDialog(_("This format exists already."),
                            translation, parent=self.window)
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

        grid = Gtk.Grid()
        grid.set_border_width(6)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        # make a treeview for listing all the name formats
        format_tree = Gtk.TreeView(self.fmt_model)
        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn(_('Format'),
                                         name_renderer,
                                         text=COL_NAME)
        name_renderer.set_property('editable', False)
        name_renderer.connect('editing-started', self.__start_name_editing)
        name_renderer.connect('edited', self.__change_name)
        name_renderer.connect('editing-canceled', self.__cancel_change)
        self.name_renderer = name_renderer
        format_tree.append_column(name_column)
        example_renderer = Gtk.CellRendererText()
        example_column = Gtk.TreeViewColumn(_('Example'),
                                            example_renderer,
                                            text=COL_EXPL)
        format_tree.append_column(example_column)
        format_tree.get_selection().connect('changed',
                                            self.cb_format_tree_select)

        # ... and put it into a scrolled win
        format_sw = Gtk.ScrolledWindow()
        format_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        format_sw.add(format_tree)
        format_sw.set_shadow_type(Gtk.ShadowType.IN)
        format_sw.set_hexpand(True)
        format_sw.set_vexpand(True)
        grid.attach(format_sw, 0, 0, 3, 1)

        # to hold the values of the selected row of the tree and the iter
        self.selected_fmt = ()
        self.iter = None

        self.insert_button = Gtk.Button.new_with_mnemonic(_('_Add'))
        self.insert_button.connect('clicked', self.__new_name)

        self.edit_button = Gtk.Button.new_with_mnemonic(_('_Edit'))
        self.edit_button.connect('clicked', self.__edit_name)
        self.edit_button.set_sensitive(False)

        self.remove_button = Gtk.Button.new_with_mnemonic(_('_Remove'))
        self.remove_button.connect('clicked', self.cb_del_fmt_str)
        self.remove_button.set_sensitive(False)

        grid.attach(self.insert_button, 0, 1, 1, 1)
        grid.attach(self.remove_button, 1, 1, 1, 1)
        grid.attach(self.edit_button,   2, 1, 1, 1)
        self.format_list = format_tree
        self.name_column = name_column
        return grid

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

    def cb_pa_sur_changed(self,*args):
        """
        checkbox patronymic as surname changed, propagate to namedisplayer
        """
        _nd.change_pa_sur()
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

    def cb_grampletbar_close(self, obj):
        """
        Gramplet bar close button preference callback
        """
        self.uistate.emit('grampletbar-close-changed')


    def auto_title_changed(self, obj):
        """
        Update sensitivity of place configuration widgets.
        """
        active = obj.get_active()
        for widget in self.place_widgets:
            widget.set_sensitive(active)

    def cb_name_dialog(self, obj):
        the_list = self.fmt_obox.get_model()
        the_iter = self.fmt_obox.get_active_iter()
        self.old_format = the_list.get_value(the_iter, COL_FMT)
        win = DisplayNameEditor(self.uistate, self.dbstate, self.track, self)

    def check_for_type_changed(self, obj):
        active = obj.get_active()
        if active == 0:  # update
            config.set('behavior.check-for-update-types', ["update"])
        elif active == 1:  # update
            config.set('behavior.check-for-update-types', ["new"])
        elif active == 2:  # update
            config.set('behavior.check-for-update-types', ["update", "new"])

    def toggle_hide_previous_addons(self, obj):
        active = obj.get_active()
        config.set('behavior.do-not-show-previously-seen-updates',
                   bool(active))

    def toggle_tag_on_import(self, obj):
        active = obj.get_active()
        config.set('preferences.tag-on-import', bool(active))
        self.tag_format_entry.set_sensitive(bool(active))

    def check_for_updates_changed(self, obj):
        active = obj.get_active()
        config.set('behavior.check-for-updates', active)

    def place_restrict_changed(self, obj):
        active = obj.get_active()
        config.set('preferences.place-restrict', active)

    def date_format_changed(self, obj):
        config.set('preferences.date-format', obj.get_active())
        OkDialog(_('Change is not immediate'),
                 _('Changing the date format will not take '
                   'effect until the next time Gramps is started.'),
                 parent=self.window)

    def date_calendar_changed(self, obj):
        config.set('preferences.calendar-format-report', obj.get_active())

    def addon_listing(self, configdialog):
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        current_line = 0
        self.add_text(grid, _('**Placeholder***  Listing here for Third-party Addons. (display all third-party addons. Installed addons could be marked with a tick.) \n \n'
                              ), 0, line_wrap=False)
        current_line += 1

        return _('Listing'), grid

    def add_addoncheckupdates_panel(self, configdialog):
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        current_line = 0
        self.add_text(grid, _('Have Gramps check for and download Third-party Addon updates. \n \n'
                              'Third-party Addons unless stated are not officially part of Gramps \n \n'
                              'Please use carefully on Family Trees that are backed up. \n \n'
                              'Note: Some Addons have prerequisites that need to be installed '
                              'before they can be used.\n \n'
                              'https://gramps-project.org/wiki/index.php?title=Third-party_Plugins'
                              ), 0, line_wrap=False)
        current_line += 9

        # Check for addon updates:
        obox = Gtk.ComboBoxText()
        formats = [_("Never"),
                   _("Once a month"),
                   _("Once a week"),
                   _("Once a day"),
                   _("Always"), ]
        list(map(obox.append_text, formats))
        active = config.get('behavior.check-for-updates')  #TODO change this key to ??? and upgrade older keys that reference "behavior.check-for-updates"
        obox.set_active(active)
        obox.connect('changed', self.check_for_updates_changed)
        lwidget = BasicLabel("%s: " % _('Check for addon updates')) # TODO Because we don't have a check for new Gramps release yet
        grid.attach(lwidget, 1, current_line, 1, 1)
        grid.attach(obox, 2, current_line, 1, 1)

        current_line += 1
        self.whattype_box = Gtk.ComboBoxText()
        formats = [_("Updated addons only"),
                   _("New addons only"),
                   _("New and updated addons"),]
        list(map(self.whattype_box.append_text, formats))
        whattype = config.get('behavior.check-for-update-types')   #TODO change this key to ??? and upgrade older keys that reference "behavior.check-for-update-types"
        if "new" in whattype and "update" in whattype:
            self.whattype_box.set_active(2)
        elif "new" in whattype:
            self.whattype_box.set_active(1)
        elif "update" in whattype:
            self.whattype_box.set_active(0)
        self.whattype_box.connect('changed', self.check_for_type_changed)
        lwidget = BasicLabel("%s: " % _('What to check'))
        grid.attach(lwidget, 1, current_line, 1, 1)
        grid.attach(self.whattype_box, 2, current_line, 1, 1)

        current_line += 1
        self.add_entry(grid, _('Where to check'), current_line, 'behavior.addons-url', col_attach=1)

        current_line += 1
        checkbutton = Gtk.CheckButton(
            label=_("Do not ask about previously notified addons"))
        checkbutton.set_active(config.get('behavior.do-not-show-previously-seen-updates'))  #TODO change this key to ???
        checkbutton.connect("toggled", self.toggle_hide_previous_addons)

        grid.attach(checkbutton, 1, current_line, 1, 1)
        button = Gtk.Button(label=_("Check now"))
        button.connect("clicked", self.check_for_updates)
        grid.attach(button, 3, current_line, 1, 1)

        return _('Updates'), grid

    def check_for_updates(self, button):
        try:
            addon_update_list = available_updates()
        except:
            OkDialog(_("Checking Addons Failed"),
                     _("The addon repository appears to be unavailable. "
                       "Please try again later."),
                     parent=self.window)
            return

        if len(addon_update_list) > 0:
            PluginWindows.UpdateAddons(addon_update_list, self.window)
        else:
            check_types = config.get('behavior.check-for-update-types')
            OkDialog(
                _("There are no available addons of this type"),
                _("Checked for '%s'") %
                      _("' and '").join([_(t) for t in check_types]),
                parent=self.window)

        # List of translated strings used here
        # Dead code for l10n
        _('new'), _('update')

        self.uistate.viewmanager.do_reg_plugins(self.dbstate, self.uistate)

    def database_backend_changed(self, obj):
        the_list = obj.get_model()
        the_iter = obj.get_active_iter()
        db_choice = the_list.get_value(the_iter, 2)
        config.set('database.backend', db_choice)

    def __create_backend_combo(self):
        """
        Create backend selection widget.
        """
        backend_plugins = self.uistate.viewmanager._pmgr.get_reg_databases()
        obox = Gtk.ComboBox()
        cell = Gtk.CellRendererText()
        obox.pack_start(cell, True)
        obox.add_attribute(cell, 'text', 1)
        # Build model:
        model = Gtk.ListStore(GObject.TYPE_INT,
                              GObject.TYPE_STRING,
                              GObject.TYPE_STRING)
        count = 0
        active = 0
        default = config.get('database.backend')
        for plugin in sorted(backend_plugins, key=lambda plugin: plugin.name):
            if plugin.id == default:
                active = count
            model.append(row=[count, plugin.name, plugin.id])
            count += 1
        obox.set_model(model)
        # set the default value as active in the combo
        obox.set_active(active)
        obox.connect('changed', self.database_backend_changed)
        return obox

    def set_mediapath(self, *obj):
        if self.path_entry.get_text().strip():
            self.dbstate.db.set_mediapath(self.path_entry.get_text())
        else:
            self.dbstate.db.set_mediapath(None)

    def select_mediapath(self, *obj):
        f = Gtk.FileChooserDialog(title=_("Select media directory"),
                                  parent=self.window,
                                  action=Gtk.FileChooserAction.SELECT_FOLDER,
                                  buttons=(_('_Cancel'),
                                           Gtk.ResponseType.CANCEL,
                                           _('_Apply'),
                                           Gtk.ResponseType.OK)
                                  )
        mpath = media_path(self.dbstate.db)
        f.set_current_folder(os.path.dirname(mpath))

        status = f.run()
        if status == Gtk.ResponseType.OK:
            val = f.get_filename()
            if val:
                self.path_entry.set_text(val)
        f.destroy()

    def set_dbpath(self, *obj):
        path = self.dbpath_entry.get_text().strip()
        config.set('database.path', path)

    def select_dbpath(self, *obj):
        f = Gtk.FileChooserDialog(title=_("Select database directory"),
                                    parent=self.window,
                                    action=Gtk.FileChooserAction.SELECT_FOLDER,
                                    buttons=(_('_Cancel'),
                                                Gtk.ResponseType.CANCEL,
                                                _('_Apply'),
                                                Gtk.ResponseType.OK)
                                    )
        dbpath = config.get('database.path')
        if not dbpath:
            dbpath = os.path.join(HOME_DIR,'grampsdb')
        f.set_current_folder(os.path.dirname(dbpath))

        status = f.run()
        if status == Gtk.ResponseType.OK:
            val = f.get_filename()
            if val:
                self.dbpath_entry.set_text(val)
        f.destroy()

    def update_idformat_entry(self, obj, constant):
        config.set(constant, obj.get_text())
        self.dbstate.db.set_prefixes(
            config.get('preferences.iprefix'),
            config.get('preferences.oprefix'),
            config.get('preferences.fprefix'),
            config.get('preferences.sprefix'),
            config.get('preferences.cprefix'),
            config.get('preferences.pprefix'),
            config.get('preferences.eprefix'),
            config.get('preferences.rprefix'),
            config.get('preferences.nprefix') )

    def update_gendepth(self, obj, constant):
        """
        Called when the generation depth setting is changed.
        """
        intval = int(obj.get_value())
        config.set(constant, intval)
        #immediately use this value in displaystate.
        self.uistate.set_gendepth(intval)

    def update_surn_height(self, obj, constant):
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
        else:
            obj.set_text(str(intval))

    def build_menu_names(self, obj):
        return (_('Preferences'), _('Preferences'))
