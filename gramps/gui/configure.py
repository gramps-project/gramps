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
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import HOME_DIR, URL_WIKISTRING, URL_MANUAL_PAGE
from gramps.gen.datehandler import get_date_formats
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.name import NameDisplayError
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.alive import update_constants
from gramps.gen.utils.file import media_path
from gramps.gen.utils.keyword import (get_keywords, get_translation_from_keyword,
                               get_translations, get_keyword_from_translation)
from gramps.gen.lib import Date, FamilyRelType
from gramps.gen.lib import Name, Surname, NameOriginType
from .managedwindow import ManagedWindow
from .widgets import MarkupLabel, BasicLabel
from .dialog import ErrorDialog, QuestionDialog2, OkDialog
from .editors.editplaceformat import EditPlaceFormat
from .display import display_help
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

WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Settings"
WIKI_HELP_SEC = _('Preferences')

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
            Gtk.Dialog(title=_('Display Name Editor')),
            None, _('Display Name Editor'), None)
        self.window.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        self.setup_configs('interface.displaynameeditor', 820, 550)
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
                 dialogtitle=_("Preferences"), on_close=None):
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
            Gtk.Dialog(title=dialogtitle),
                       None, dialogtitle, None)
        self.window.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
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
        if value == Gtk.ResponseType.HELP:
            return
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

    def update_color(self, obj, pspec, constant, color_hex_label):
        """
        Called on changing some color.
        Either on programmatically color change.
        """
        rgba = obj.get_rgba()
        hexval = "#%02x%02x%02x" % (int(rgba.red * 255),
                                    int(rgba.green * 255),
                                    int(rgba.blue * 255))
        color_hex_label.set_text(hexval)
        colors = self.__config.get(constant)
        if isinstance(colors, list):
            scheme = self.__config.get('colors.scheme')
            colors[scheme] = hexval
            self.__config.set(constant, colors)
        else:
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
        lwidget = BasicLabel(_("%s: ") % label) # needed for French, else ignore
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
            lwidget = BasicLabel(_("%s: ") % label) # translators: for French
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
        lwidget = BasicLabel(_("%s: ") % label) # needed for French, else ignore
        entry = Gtk.Entry()
        entry.set_text(str(config.get(constant)))
        entry.set_tooltip_markup(helptext)
        entry.set_hexpand(True)
        if callback:
            entry.connect('changed', callback, constant)
        grid.attach(lwidget, col_attach, index, 1, 1)
        grid.attach(entry, col_attach+1, index, 1, 1)

    def add_color(self, grid, label, index, constant, config=None, col=0):
        """
        Add color chooser widget with label to the grid.
        """
        if not config:
            config = self.__config
        lwidget = BasicLabel(_("%s: ") % label) # needed for French, else ignore
        colors = config.get(constant)
        if isinstance(colors, list):
            scheme = config.get('colors.scheme')
            hexval = colors[scheme]
        else:
            hexval = colors
        color = Gdk.color_parse(hexval)
        entry = Gtk.ColorButton(color=color)
        color_hex_label = BasicLabel(hexval)
        color_hex_label.set_hexpand(True)
        entry.connect('notify::color', self.update_color, constant,
                      color_hex_label)
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
        lwidget = BasicLabel(_("%s: ") % label) # needed for French, else ignore
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
        lwidget = BasicLabel(_("%s: ") % label) # needed for French, else ignore
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
        lwidget = BasicLabel(_("%s: ") % label) # needed for French, else ignore
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
# GrampsPreferences
#
#-------------------------------------------------------------------------
class GrampsPreferences(ConfigureDialog):

    def __init__(self, uistate, dbstate):
        page_funcs = (
            self.add_behavior_panel,
            self.add_famtree_panel,
            self.add_formats_panel,
            self.add_text_panel,
            self.add_prefix_panel,
            self.add_date_panel,
            self.add_researcher_panel,
            self.add_advanced_panel,
            self.add_color_panel
            )
        ConfigureDialog.__init__(self, uistate, dbstate, page_funcs,
                                 GrampsPreferences, config,
                                 on_close=update_constants)
        help_btn = self.window.add_button(_('_Help'), Gtk.ResponseType.HELP)
        help_btn.connect(
            'clicked', lambda x: display_help(WIKI_HELP_PAGE, WIKI_HELP_SEC))
        self.setup_configs('interface.grampspreferences', 700, 450)

    def add_researcher_panel(self, configdialog):
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self.add_text(grid, _('Enter your information so people can contact '
                              'you when you distribute your Family Tree'),
                      0, line_wrap=True)
        self.add_entry(grid, _('Name'), 1, 'researcher.researcher-name')
        self.add_entry(grid, _('Address'), 2, 'researcher.researcher-addr')
        self.add_entry(grid, _('Locality'), 3, 'researcher.researcher-locality')
        self.add_entry(grid, _('City'), 4, 'researcher.researcher-city')
        self.add_entry(grid, _('State/County'), 5, 'researcher.researcher-state')
        self.add_entry(grid, _('Country'), 6, 'researcher.researcher-country')
        self.add_entry(grid, _('ZIP/Postal Code'), 7, 'researcher.researcher-postal')
        self.add_entry(grid, _('Phone'), 8, 'researcher.researcher-phone')
        self.add_entry(grid, _('Email'), 9, 'researcher.researcher-email')
        return _('Researcher'), grid

    def add_prefix_panel(self, configdialog):
        """
        Add the ID prefix tab to the preferences.
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self.add_entry(grid, _('Person'), 0, 'preferences.iprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Family'), 1, 'preferences.fprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Place'), 2, 'preferences.pprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Source'), 3, 'preferences.sprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Citation'), 4, 'preferences.cprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Media Object'), 5, 'preferences.oprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Event'), 6, 'preferences.eprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Repository'), 7, 'preferences.rprefix',
                       self.update_idformat_entry)
        self.add_entry(grid, _('Note'), 8, 'preferences.nprefix',
                       self.update_idformat_entry)
        return _('ID Formats'), grid

    def add_color_panel(self, configdialog):
        """
        Add the tab to set defaults colors for graph boxes.
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self.add_text(grid, _('Set the colors used for boxes in the graphical views'),
                        0, line_wrap=False)

        hbox = Gtk.Box(spacing=12)
        self.color_scheme_box = Gtk.ComboBoxText()
        formats = [_("Light colors"),
                   _("Dark colors"),]
        list(map(self.color_scheme_box.append_text, formats))
        scheme = config.get('colors.scheme')
        self.color_scheme_box.set_active(scheme)
        self.color_scheme_box.connect('changed', self.color_scheme_changed)
        lwidget = BasicLabel(_("%s: ") % _('Color scheme'))
        hbox.pack_start(lwidget, False, False, 0)
        hbox.pack_start(self.color_scheme_box, False, False, 0)

        restore_btn = Gtk.Button(_('Restore to defaults'))
        restore_btn.connect('clicked', self.restore_colors)
        hbox.pack_start(restore_btn, False, False, 0)
        grid.attach(hbox, 1, 1, 6, 1)

        color_list = [
            (_('Male Alive'), 'male-alive', 2, 0),
            (_('Male Dead'), 'male-dead', 4, 0),
            (_('Female Alive'), 'female-alive', 2, 4),
            (_('Female Dead'), 'female-dead', 4, 4),
            (_('Unknown Alive'), 'unknown-alive', 6, 4),
            (_('Unknown Dead'), 'unknown-dead', 8, 4),
            (_('Family Node'), 'family', 7, 0),
            (_('Family Divorced'), 'family-divorced', 9, 0),
            (_('Home Person'), 'home-person', 6, 0),
            (_('Border Male Alive'), 'border-male-alive', 3, 0),
            (_('Border Male Dead'), 'border-male-dead', 5, 0),
            (_('Border Female Alive'), 'border-female-alive', 3, 4),
            (_('Border Female Dead'), 'border-female-dead', 5, 4),
            (_('Border Unknown Alive'), 'border-unknown-alive', 7, 4),
            (_('Border Unknown Dead'), 'border-unknown-dead', 9, 4),
            (_('Border Family'), 'border-family', 8, 0),
            (_('Border Family Divorced'), 'border-family-divorced', 10, 0),
            ]

        self.colors = {}
        for color in color_list:
            pref_name = 'colors.' + color[1]
            self.colors[pref_name] = self.add_color(grid, color[0], color[2],
                                                    pref_name, col=color[3])
        return _('Colors'), grid

    def restore_colors(self, widget=None):
        """
        Restore colors of selected scheme to default.
        """
        scheme = config.get('colors.scheme')
        for key, widget in self.colors.items():
            color = Gdk.RGBA()
            hexval = config.get_default(key)[scheme]
            Gdk.RGBA.parse(color, hexval)
            widget.set_rgba(color)

    def add_advanced_panel(self, configdialog):
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self.add_checkbox(
            grid, _('Suppress warning when adding parents to a child.'),
            0, 'preferences.family-warn')

        self.add_checkbox(
            grid, _('Suppress warning when canceling with changed data.'),
            1, 'interface.dont-ask')

        self.add_checkbox(
            grid, _('Suppress warning about missing researcher when'
                     ' exporting to GEDCOM.'),
            2, 'behavior.owner-warn')

        self.add_checkbox(
            grid, _('Show plugin status dialog on plugin load error.'),
            3, 'behavior.pop-plugin-status')

        return _('Warnings'), grid

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
        format_tree = Gtk.TreeView(model=self.fmt_model)
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

    def cb_place_fmt_changed(self, obj):
        """
        Called when the place format is changed.
        """
        config.set('preferences.place-format', obj.get_active())
        self.uistate.emit('placeformat-changed')

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

    def add_formats_panel(self, configdialog):
        row = 0
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        # Display name:
        self.examplename = Name()
        examplesurname = Surname()
        examplesurnamesecond = Surname()
        examplesurnamepat = Surname()
        self.examplename.set_title('Dr.')
        self.examplename.set_first_name('Edwin Jose')
        examplesurname.set_prefix('von der')
        examplesurname.set_surname('Smith')
        examplesurname.set_connector('and')
        self.examplename.add_surname(examplesurname)
        examplesurnamesecond.set_surname('Weston')
        self.examplename.add_surname(examplesurnamesecond)
        examplesurnamepat.set_surname('Wilson')
        examplesurnamepat.set_origintype(
                                    NameOriginType(NameOriginType.PATRONYMIC))
        self.examplename.add_surname(examplesurnamepat)
        self.examplename.set_primary_surname(0)
        self.examplename.set_suffix('Sr')
        self.examplename.set_call_name('Jose')
        self.examplename.set_nick_name('Ed')
        self.examplename.set_family_nick_name('Underhills')
        # get the model for the combo and the treeview
        active = _nd.get_default_format()
        self.fmt_model, active = self._build_name_format_model(active)
        # set up the combo to choose the preset format
        self.fmt_obox = Gtk.ComboBox()
        cell = Gtk.CellRendererText()
        cell.set_property('ellipsize', Pango.EllipsizeMode.END)
        self.fmt_obox.pack_start(cell, True)
        self.fmt_obox.add_attribute(cell, 'text', 1)
        self.fmt_obox.set_model(self.fmt_model)
        # set the default value as active in the combo
        self.fmt_obox.set_active(active)
        self.fmt_obox.connect('changed', self.cb_name_changed)
        # label for the combo
        lwidget = BasicLabel(_("%s: ") % _('Name format'))
        lwidget.set_use_underline(True)
        lwidget.set_mnemonic_widget(self.fmt_obox)
        hbox = Gtk.Box()
        btn = Gtk.Button(label=("%s..." % _('Edit')))
        btn.connect('clicked', self.cb_name_dialog)
        hbox.pack_start(self.fmt_obox, True, True, 0)
        hbox.pack_start(btn, False, False, 0)
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(hbox, 1, row, 2, 1)
        row += 1

        # Pa/Matronymic surname handling
        self.add_checkbox(grid,
                          _("Consider single pa/matronymic as surname"),
                          row, 'preferences.patronimic-surname', stop=3,
                          extra_callback=self.cb_pa_sur_changed)
        row += 1

        # Date format:
        obox = Gtk.ComboBoxText()
        formats = get_date_formats()
        list(map(obox.append_text, formats))
        active = config.get('preferences.date-format')
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect('changed', self.date_format_changed)
        lwidget = BasicLabel(_("%s: ") % _('Date format'))
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(obox, 1, row, 2, 1)
        row += 1

        # Place format:
        self.pformat = Gtk.ComboBox()
        renderer = Gtk.CellRendererText()
        self.pformat.pack_start(renderer, True)
        self.pformat.add_attribute(renderer, "text", 0)
        self.cb_place_fmt_rebuild()
        active = config.get('preferences.place-format')
        self.pformat.set_active(active)
        self.pformat.connect('changed', self.cb_place_fmt_changed)
        lwidget = BasicLabel(_("%s: ") % _('Place format'))
        lwidget.set_use_underline(True)
        lwidget.set_mnemonic_widget(obox)
        hbox = Gtk.Box()
        self.fmt_btn = Gtk.Button(label=("%s..." % _('Edit')))
        self.fmt_btn.connect('clicked', self.cb_place_fmt_dialog)
        hbox.pack_start(self.pformat, True, True, 0)
        hbox.pack_start(self.fmt_btn, False, False, 0)
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(hbox, 1, row, 2, 1)
        row += 1

        auto = self.add_checkbox(grid,
                                _("Enable automatic place title generation"),
                                row, 'preferences.place-auto',
                                extra_callback=self.auto_title_changed)
        self.auto_title_changed(auto)
        row += 1

        # Age precision:
        # precision=1 for "year", 2: "year, month" or 3: "year, month, days"
        obox = Gtk.ComboBoxText()
        age_precision = [_("Years"),
                         _("Years, Months"),
                         _("Years, Months, Days")]
        list(map(obox.append_text, age_precision))
        # Combo_box active index is from 0 to 2, we need values from 1 to 3
        active = config.get('preferences.age-display-precision') - 1
        if active >= 0 and active <= 2:
            obox.set_active(active)
        else:
            obox.set_active(0)
        obox.connect('changed',
                     lambda obj: config.set('preferences.age-display-precision',
                                            obj.get_active() + 1))
        lwidget = BasicLabel(_("%s: ")
                             % _('Age display precision (requires restart)'))
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(obox, 1, row, 2, 1)
        row += 1

        # Calendar format on report:
        obox = Gtk.ComboBoxText()
        list(map(obox.append_text, Date.ui_calendar_names))
        active = config.get('preferences.calendar-format-report')
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect('changed', self.date_calendar_changed)
        lwidget = BasicLabel(_("%s: ") % _('Calendar on reports'))
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(obox, 1, row, 2, 1)
        row += 1

        # Surname guessing:
        obox = Gtk.ComboBoxText()
        formats = _surname_styles
        list(map(obox.append_text, formats))
        obox.set_active(config.get('behavior.surname-guessing'))
        obox.connect('changed',
                     lambda obj: config.set('behavior.surname-guessing',
                                            obj.get_active()))
        lwidget = BasicLabel(_("%s: ") % _('Surname guessing'))
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(obox, 1, row, 2, 1)
        row += 1

        # Default Family Relationship
        obox = Gtk.ComboBoxText()
        formats = FamilyRelType().get_standard_names()
        list(map(obox.append_text, formats))
        obox.set_active(config.get('preferences.family-relation-type'))
        obox.connect('changed',
                     lambda obj: config.set('preferences.family-relation-type',
                                            obj.get_active()))
        lwidget = BasicLabel(_("%s: ") % _('Default family relationship'))
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(obox, 1, row, 2, 1)
        row += 1

        #height multiple surname table
        self.add_pos_int_entry(grid,
                _('Height multiple surname box (pixels)'),
                row, 'interface.surname-box-height', self.update_surn_height,
                col_attach=0)
        row += 1

        # Status bar:
        obox = Gtk.ComboBoxText()
        formats = [_("Active person's name and ID"),
                   _("Relationship to home person")]
        list(map(obox.append_text, formats))
        active = config.get('interface.statusbar')
        if active < 2:
            obox.set_active(0)
        else:
            obox.set_active(1)
        obox.connect('changed',
                     lambda obj: config.set('interface.statusbar', 2*obj.get_active()))
        lwidget = BasicLabel(_("%s: ") % _('Status bar'))
        grid.attach(lwidget, 0, row, 1, 1)
        grid.attach(obox, 1, row, 2, 1)
        row += 1

        # Text in sidebar:
        self.add_checkbox(grid,
                          _("Show text label beside Navigator buttons (requires restart)"),
                          row, 'interface.sidebar-text', stop=3)
        row += 1

        # Gramplet bar close buttons:
        self.add_checkbox(grid,
                          _("Show close button in gramplet bar tabs"),
                          row, 'interface.grampletbar-close', stop=3,
                          extra_callback=self.cb_grampletbar_close)
        row += 1
        return _('Display'), grid

    def auto_title_changed(self, obj):
        """
        Update sensitivity of place format widget.
        """
        active = config.get('preferences.place-auto')
        self.pformat.set_sensitive(active)
        self.fmt_btn.set_sensitive(active)

    def add_text_panel(self, configdialog):
        row = 0
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        self.add_entry(grid, _('Missing surname'), row,
                       'preferences.no-surname-text')
        row += 1
        self.add_entry(grid, _('Missing given name'), row,
                       'preferences.no-given-text')
        row += 1
        self.add_entry(grid, _('Missing record'), row,
                       'preferences.no-record-text')
        row += 1
        self.add_entry(grid, _('Private surname'), row,
                       'preferences.private-surname-text',
                       localized_config=False)
        row += 1
        self.add_entry(grid, _('Private given name'), row,
                       'preferences.private-given-text',
                       localized_config=False)
        row += 1
        self.add_entry(grid, _('Private record'), row,
                       'preferences.private-record-text')
        row += 1
        return _('Text'), grid

    def cb_name_dialog(self, obj):
        the_list = self.fmt_obox.get_model()
        the_iter = self.fmt_obox.get_active_iter()
        self.old_format = the_list.get_value(the_iter, COL_FMT)
        win = DisplayNameEditor(self.uistate, self.dbstate, self.track, self)

    def color_scheme_changed(self, obj):
        """
        Called on swiching color scheme.
        """
        scheme = obj.get_active()
        config.set('colors.scheme', scheme)
        for key, widget in self.colors.items():
            color = Gdk.RGBA()
            hexval = config.get(key)[scheme]
            Gdk.RGBA.parse(color, hexval)
            widget.set_rgba(color)

    def cb_place_fmt_dialog(self, button):
        """
        Called to invoke the place format editor.
        """
        EditPlaceFormat(self.uistate, self.dbstate, self.track,
                        self.cb_place_fmt_rebuild)

    def cb_place_fmt_rebuild(self):
        """
        Called to rebuild the place format list.
        """
        model = Gtk.ListStore(str)
        for fmt in _pd.get_formats():
            model.append([fmt.name])
        self.pformat.set_model(model)
        self.pformat.set_active(0)

    def check_for_type_changed(self, obj):
        active = obj.get_active()
        if active == 0:  # update
            config.set('behavior.check-for-addon-update-types', ["update"])
        elif active == 1:  # update
            config.set('behavior.check-for-addon-update-types', ["new"])
        elif active == 2:  # update
            config.set('behavior.check-for-addon-update-types', ["update", "new"])

    def toggle_hide_previous_addons(self, obj):
        active = obj.get_active()
        config.set('behavior.do-not-show-previously-seen-addon-updates',
                   bool(active))

    def toggle_tag_on_import(self, obj):
        active = obj.get_active()
        config.set('preferences.tag-on-import', bool(active))
        self.tag_format_entry.set_sensitive(bool(active))

    def check_for_updates_changed(self, obj):
        active = obj.get_active()
        config.set('behavior.check-for-addon-updates', active)

    def date_format_changed(self, obj):
        config.set('preferences.date-format', obj.get_active())
        OkDialog(_('Change is not immediate'),
                 _('Changing the date format will not take '
                   'effect until the next time Gramps is started.'),
                 parent=self.window)

    def date_calendar_changed(self, obj):
        config.set('preferences.calendar-format-report', obj.get_active())

    def autobackup_changed(self, obj):
        active = obj.get_active()
        config.set('database.autobackup', active)
        self.uistate.set_backup_timer()

    def add_date_panel(self, configdialog):
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        self.add_spinner(grid,
                _('Date about range'),
                0, 'behavior.date-about-range', (1, 9999))
        self.add_spinner(grid,
                _('Date after range'),
                1, 'behavior.date-after-range', (1, 9999))
        self.add_spinner(grid,
                _('Date before range'),
                2, 'behavior.date-before-range', (1, 9999))
        self.add_spinner(grid,
                _('Maximum age probably alive'),
                3, 'behavior.max-age-prob-alive', (80, 140))
        self.add_spinner(grid,
                _('Maximum sibling age difference'),
                4, 'behavior.max-sib-age-diff', (10, 30))
        self.add_spinner(grid,
                _('Minimum years between generations'),
                5, 'behavior.min-generation-years', (5, 20))
        self.add_spinner(grid,
                _('Average years between generations'),
                6, 'behavior.avg-generation-gap', (10, 30))
        self.add_pos_int_entry(grid,
                _('Markup for invalid date format'),
                7, 'preferences.invalid-date-format',
                self.update_markup_entry,
                helptext = _('Convenience markups are:\n'
                '<b>&lt;b&gt;Bold&lt;/b&gt;</b>\n'
                '<big>&lt;big&gt;Makes font relatively larger&lt;/big&gt;</big>\n'
                '<i>&lt;i&gt;Italic&lt;/i&gt;</i>\n'
                '<s>&lt;s&gt;Strikethrough&lt;/s&gt;</s>\n'
                '<sub>&lt;sub&gt;Subscript&lt;/sub&gt;</sub>\n'
                '<sup>&lt;sup&gt;Superscript&lt;/sup&gt;</sup>\n'
                '<small>&lt;small&gt;Makes font relatively smaller&lt;/small&gt;</small>\n'
                '<tt>&lt;tt&gt;Monospace font&lt;/tt&gt;</tt>\n'
                '<u>&lt;u&gt;Underline&lt;/u&gt;</u>\n\n'
                'For example: &lt;u&gt;&lt;b&gt;%s&lt;/b&gt;&lt;/u&gt;\n'
                'will display <u><b>Underlined bold date</b></u>.\n')
                )

        return _('Dates'), grid

    def add_behavior_panel(self, configdialog):
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        current_line = 0
        if win():
            self.add_checkbox(grid,
                    _('Use alternate Font handler for GUI and Reports '
                      '(requires restart)'),
                    current_line, 'preferences.alternate-fonthandler')

            current_line += 1
        self.add_checkbox(grid,
                _('Add default source on GEDCOM import'),
                current_line, 'preferences.default-source')

        current_line += 1
        checkbutton = Gtk.CheckButton(label=_("Add tag on import"))
        checkbutton.set_active(config.get('preferences.tag-on-import'))
        checkbutton.connect("toggled", self.toggle_tag_on_import)
        grid.attach(checkbutton, 1, current_line, 1, 1)
        self.tag_format_entry = self.add_entry(grid, None, current_line,
                                               'preferences.tag-on-import-format',
                                               col_attach=2)
        self.tag_format_entry.set_sensitive(config.get('preferences.tag-on-import'))

        current_line += 1
        obj = self.add_checkbox(grid,
                _('Enable spelling checker'),
                current_line, 'behavior.spellcheck')
        if not HAVE_GTKSPELL:
            obj.set_sensitive(False)
            spell_dict = { 'gramps_wiki_build_spell_url' :
                               URL_WIKISTRING +
                                   "GEPS_029:_GTK3-GObject_introspection"
                                   "_Conversion#Spell_Check_Install" }
            obj.set_tooltip_text(
                _("GtkSpell not loaded. "
                  "Spell checking will not be available.\n"
                  "To build it for Gramps see "
                  "%(gramps_wiki_build_spell_url)s") % spell_dict )

        current_line += 1
        self.add_checkbox(grid,
                _('Display Tip of the Day'),
                current_line, 'behavior.use-tips')

        current_line += 1
        self.add_checkbox(grid,
                _('Remember last view displayed'),
                current_line, 'preferences.use-last-view')

        current_line += 1
        self.add_spinner(grid,
                _('Max generations for relationships'),
                current_line, 'behavior.generation-depth', (5, 50), self.update_gendepth)

        current_line += 1
        self.path_entry = Gtk.Entry()
        self.add_path_box(grid,
                _('Base path for relative media paths'),
                current_line, self.path_entry, self.dbstate.db.get_mediapath(),
                self.set_mediapath, self.select_mediapath)

        current_line += 1
        # Check for addon updates:
        obox = Gtk.ComboBoxText()
        formats = [_("Never"),
                   _("Once a month"),
                   _("Once a week"),
                   _("Once a day"),
                   _("Always"), ]
        list(map(obox.append_text, formats))
        active = config.get('behavior.check-for-addon-updates')
        obox.set_active(active)
        obox.connect('changed', self.check_for_updates_changed)
        lwidget = BasicLabel(_("%s: ") % _('Check for addon updates'))
        grid.attach(lwidget, 1, current_line, 1, 1)
        grid.attach(obox, 2, current_line, 1, 1)

        current_line += 1
        self.whattype_box = Gtk.ComboBoxText()
        formats = [_("Updated addons only"),
                   _("New addons only"),
                   _("New and updated addons"),]
        list(map(self.whattype_box.append_text, formats))
        whattype = config.get('behavior.check-for-addon-update-types')
        if "new" in whattype and "update" in whattype:
            self.whattype_box.set_active(2)
        elif "new" in whattype:
            self.whattype_box.set_active(1)
        elif "update" in whattype:
            self.whattype_box.set_active(0)
        self.whattype_box.connect('changed', self.check_for_type_changed)
        lwidget = BasicLabel(_("%s: ") % _('What to check'))
        grid.attach(lwidget, 1, current_line, 1, 1)
        grid.attach(self.whattype_box, 2, current_line, 1, 1)

        current_line += 1
        self.add_entry(grid, _('Where to check'), current_line, 'behavior.addons-url', col_attach=1)

        current_line += 1
        checkbutton = Gtk.CheckButton(
            label=_("Do not ask about previously notified addons"))
        checkbutton.set_active(config.get('behavior.do-not-show-previously-seen-addon-updates'))
        checkbutton.connect("toggled", self.toggle_hide_previous_addons)

        grid.attach(checkbutton, 1, current_line, 1, 1)
        button = Gtk.Button(label=_("Check for updated addons now"))
        button.connect("clicked", self.check_for_updates)
        grid.attach(button, 3, current_line, 1, 1)

        return _('General'), grid

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
            rescan = PluginWindows.UpdateAddons(self.uistate, self.track,
                                                addon_update_list).rescan
            self.uistate.viewmanager.do_reg_plugins(self.dbstate, self.uistate,
                                                    rescan=rescan)
        else:
            check_types = config.get('behavior.check-for-addon-update-types')
            OkDialog(
                _("There are no available addons of this type"),
                _("Checked for '%s'") %
                      _("' and '").join([_(t) for t in check_types]),
                parent=self.window)

        # List of translated strings used here
        # Dead code for l10n
        _('new'), _('update')


    def database_backend_changed(self, obj):
        the_list = obj.get_model()
        the_iter = obj.get_active_iter()
        db_choice = the_list.get_value(the_iter, 2)
        config.set('database.backend', db_choice)
        self.set_connection_widgets(db_choice)

    def set_connection_widgets(self, db_choice):
        """
        Sets the connection widgets insensitive for embedded databases.
        """
        for widget in self.connection_widgets:
            if db_choice in ('bsddb', 'sqlite'):
                widget.set_sensitive(False)
            else:
                widget.set_sensitive(True)

    def add_famtree_panel(self, configdialog):
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        current_line = 0

        lwidget = BasicLabel(_("%s: ") % _('Database backend'))
        grid.attach(lwidget, 1, current_line, 1, 1)
        obox = self.__create_backend_combo()
        grid.attach(obox, 2, current_line, 1, 1)
        current_line += 1

        self.connection_widgets = []
        entry = self.add_entry(grid, _('Host'), current_line,
                               'database.host', col_attach=1)
        self.connection_widgets.append(entry)
        current_line += 1
        entry = self.add_entry(grid, _('Port'), current_line,
                               'database.port', col_attach=1)
        self.connection_widgets.append(entry)
        current_line += 1
        self.set_connection_widgets(config.get('database.backend'))

        self.dbpath_entry = Gtk.Entry()
        self.add_path_box(grid,
                _('Family Tree Database path'),
                current_line, self.dbpath_entry, config.get('database.path'),
                self.set_dbpath, self.select_dbpath)
        current_line += 1

        #self.add_entry(grid,
        #        _('Family Tree Database path'),
        #        0, 'database.path')
        self.add_checkbox(grid,
                _('Automatically load last Family Tree'),
                current_line, 'behavior.autoload')
        current_line += 1

        self.backup_path_entry = Gtk.Entry()
        self.add_path_box(grid,
                _('Backup path'),
                current_line, self.backup_path_entry,
                config.get('database.backup-path'),
                self.set_backup_path, self.select_backup_path)
        current_line += 1

        self.add_checkbox(grid,
                _('Backup on exit'),
                current_line, 'database.backup-on-exit')
        current_line += 1

        # Check for updates:
        obox = Gtk.ComboBoxText()
        formats = [_("Never"),
                   _("Every 15 minutes"),
                   _("Every 30 minutes"),
                   _("Every hour")]
        list(map(obox.append_text, formats))
        active = config.get('database.autobackup')
        obox.set_active(active)
        obox.connect('changed', self.autobackup_changed)
        lwidget = BasicLabel(_("%s: ") % _('Autobackup'))
        grid.attach(lwidget, 1, current_line, 1, 1)
        grid.attach(obox, 2, current_line, 1, 1)

        return _('Family Tree'), grid

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
                                  transient_for=self.window,
                                  action=Gtk.FileChooserAction.SELECT_FOLDER)
        f.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL,
                      _('_Apply'), Gtk.ResponseType.OK)
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

    def set_backup_path(self, *obj):
        path = self.backup_path_entry.get_text().strip()
        config.set('database.backup-path', path)

    def select_backup_path(self, *obj):
        f = Gtk.FileChooserDialog(title=_("Select backup directory"),
                                    parent=self.window,
                                    action=Gtk.FileChooserAction.SELECT_FOLDER,
                                    buttons=(_('_Cancel'),
                                                Gtk.ResponseType.CANCEL,
                                                _('_Apply'),
                                                Gtk.ResponseType.OK)
                                    )
        backup_path = config.get('database.backup-path')
        if not backup_path:
            backup_path = config.get('database.path')
        f.set_current_folder(os.path.dirname(backup_path))

        status = f.run()
        if status == Gtk.ResponseType.OK:
            val = f.get_filename()
            if val:
                self.backup_path_entry.set_text(val)
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
