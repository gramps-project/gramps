#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-      Serge Noiraud
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

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import random
import os
from xml.sax.saxutils import escape
from collections import abc

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import USER_DATA, URL_WIKISTRING, URL_MANUAL_PAGE
from gramps.gen.datehandler import get_date_formats
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.name import NameDisplayError
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.alive import update_constants
from gramps.gen.utils.file import media_path
from gramps.gen.utils.place import coord_formats, coord_formats_desc
from gramps.gen.utils.keyword import (
    get_keywords,
    get_translations,
    get_translation_from_keyword,
    get_keyword_from_translation,
)
from gramps.gen.lib import Date, FamilyRelType
from gramps.gen.lib import Name, Surname, NameOriginType
from .managedwindow import ManagedWindow
from .widgets import MarkupLabel, BasicLabel
from .dialog import ErrorDialog, OkDialog
from .editors.editplaceformat import EditPlaceFormat
from .display import display_help
from gramps.gen.plug.utils import available_updates
from .plug import PluginWindows

# from gramps.gen.errors import WindowActiveError
from .spell import HAVE_GSPELL
from gramps.gen.constfunc import win

_ = glocale.translation.gettext
from gramps.gen.utils.symbols import Symbols
from gramps.gen.constfunc import get_env_var

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

_surname_styles = [
    _("Father's surname"),
    _("None"),
    _("Combination of mother's and father's surname"),
    _("Icelandic style"),
]

# column numbers for the 'name format' model
COL_NUM = 0
COL_NAME = 1
COL_FMT = 2
COL_EXPL = 3

WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Settings"
WIKI_HELP_SEC = _("Preferences")


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
class DisplayNameEditor(ManagedWindow):
    def __init__(self, uistate, dbstate, track, dialog):
        # Assumes that there are two methods: dialog.name_changed_check(),
        # and dialog._build_custom_name_ui()
        ManagedWindow.__init__(self, uistate, track, DisplayNameEditor)
        self.dialog = dialog
        self.dbstate = dbstate
        self.set_window(
            Gtk.Dialog(title=_("Display Name Editor")),
            None,
            _("Display Name Editor"),
            None,
        )
        self.window.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.setup_configs("interface.displaynameeditor", 820, 550)
        grid = self.dialog._build_custom_name_ui()
        label = Gtk.Label(
            label=_(
                """The following keywords are replaced with the appropriate name parts:<tt>
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
"""
            )
        )
        label.set_use_markup(True)
        self.window.vbox.pack_start(label, False, True, 0)
        self.window.vbox.pack_start(grid, True, True, 0)
        self.window.connect("response", self.close)
        self.show()

    def close(self, *obj):
        self.dialog.name_changed_check()
        ManagedWindow.close(self, *obj)

    def build_menu_names(self, obj):
        return (_(" Name Editor"), None)


# -------------------------------------------------------------------------
#
# ConfigureDialog
#
# -------------------------------------------------------------------------


class ConfigureDialog(ManagedWindow):
    """
    Base class for configuration dialogs. They provide a Notebook, to which
    pages are added with configuration options, and a Cancel and Save button.
    On save, a config file on which the dialog works, is saved to disk, and
    a callback called.
    """

    def __init__(
        self,
        uistate,
        dbstate,
        configure_page_funcs,
        configobj,
        configmanager,
        dialogtitle=_("Preferences"),
        on_close=None,
    ):
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
        self.set_window(Gtk.Dialog(title=dialogtitle), None, dialogtitle, None)
        self.window.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.panel = Gtk.Notebook()
        self.panel.set_scrollable(True)
        self.window.vbox.pack_start(self.panel, True, True, 0)
        self.__on_close = on_close
        self.window.connect("response", self.done)
        if not config.get("behavior.immediate-warn"):
            self.window.set_tooltip_text(_("Any changes are saved immediately"))

        self.__setup_pages(configure_page_funcs)

        self.show()

    def __setup_pages(self, configure_page_funcs):
        """
        This method builds the notebook pages in the panel
        """
        if isinstance(configure_page_funcs, abc.Callable):
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
            obj.get_text() % "test_markup"
        except TypeError:
            print("WARNING: ignoring invalid value for '%s'" % constant)
            ErrorDialog(
                _("Invalid or incomplete format definition."),
                obj.get_text(),
                parent=self.window,
            )
            obj.set_text("<b>%s</b>")
        except ValueError:
            print("WARNING: ignoring invalid value for '%s'" % constant)
            ErrorDialog(
                _("Invalid or incomplete format definition."),
                obj.get_text(),
                parent=self.window,
            )
            obj.set_text("<b>%s</b>")

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
        hexval = "#%02x%02x%02x" % (
            int(rgba.red * 255),
            int(rgba.green * 255),
            int(rgba.blue * 255),
        )
        color_hex_label.set_text(hexval)
        colors = self.__config.get(constant)
        if isinstance(colors, list):
            scheme = self.__config.get("colors.scheme")
            colors[scheme] = hexval
            self.__config.set(constant, colors)
        else:
            self.__config.set(constant, hexval)

    def update_checkbox(self, obj, constant, config=None):
        """
        :param obj: the CheckButton object
        :param constant: the config setting to which the value must be saved
        """
        if not config:
            config = self.__config
        config.set(constant, obj.get_active())

    def update_radiobox(self, obj, constant):
        """
        :param obj: the RadioButton object
        :param constant: the config setting to which the value must be saved
        """
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

    def add_checkbox(
        self,
        grid,
        label,
        index,
        constant,
        start=1,
        stop=9,
        config=None,
        extra_callback=None,
        tooltip="",
    ):
        """
        Adds checkbox option with tooltip.
        """
        if not config:
            config = self.__config
        checkbox = Gtk.CheckButton(label=label)
        checkbox.set_active(config.get(constant))
        checkbox.connect("toggled", self.update_checkbox, constant, config)
        if extra_callback:
            checkbox.connect("toggled", extra_callback)
        if tooltip:
            checkbox.set_tooltip_text(tooltip)
        grid.attach(checkbox, start, index, stop - start, 1)
        return checkbox

    def add_radiobox(self, grid, label, index, constant, group, column, config=None):
        """
        Adds radiobox option.
        """
        if not config:
            config = self.__config
        radiobox = Gtk.RadioButton.new_with_mnemonic_from_widget(group, label)
        if config.get(constant):
            radiobox.set_active(True)
        radiobox.connect("toggled", self.update_radiobox, constant)
        grid.attach(radiobox, column, index, 1, 1)
        return radiobox

    def add_text(
        self,
        grid,
        label,
        index,
        config=None,
        line_wrap=True,
        start=1,
        stop=9,
        justify=Gtk.Justification.LEFT,
        align=Gtk.Align.START,
        bold=False,
    ):
        """
        Adds text with specified parameters.
        """
        if not config:
            config = self.__config
        text = Gtk.Label()
        text.set_line_wrap(line_wrap)
        text.set_halign(Gtk.Align.START)
        if bold:
            text.set_markup("<b>%s</b>" % label)
        else:
            text.set_text(label)
        text.set_halign(align)
        text.set_justify(justify)
        grid.attach(text, start, index, stop - start, 1)
        return text

    def add_button(
        self, grid, label, index, constant, extra_callback=None, config=None
    ):
        if not config:
            config = self.__config
        button = Gtk.Button(label=label)
        button.connect("clicked", extra_callback)
        grid.attach(button, 1, index, 1, 1)
        return button

    def add_path_box(
        self, grid, label, index, entry, path, callback_label, callback_sel, config=None
    ):
        """
        Add an entry to give in path and a select button to open a dialog.
        Changing entry calls callback_label
        Clicking open button call callback_sel
        """
        if not config:
            config = self.__config
        lwidget = BasicLabel(_("%s: ") % label)  # needed for French
        hbox = Gtk.Box()
        if path:
            entry.set_text(path)
        entry.connect("changed", callback_label)
        btn = Gtk.Button()
        btn.connect("clicked", callback_sel)
        image = Gtk.Image()
        image.set_from_icon_name("document-open", Gtk.IconSize.BUTTON)
        image.show()
        btn.add(image)
        hbox.pack_start(entry, True, True, 0)
        hbox.pack_start(btn, False, False, 0)
        hbox.set_hexpand(True)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(hbox, 2, index, 1, 1)

    def add_entry(
        self,
        grid,
        label,
        index,
        constant,
        callback=None,
        config=None,
        col_attach=0,
        localized_config=True,
    ):
        """
        Adds entry field.
        """
        if not config:
            config = self.__config
        if not callback:
            callback = self.update_entry
        if label:
            lwidget = BasicLabel(_("%s: ") % label)  # Translators: for French
        entry = Gtk.Entry()
        if localized_config:
            entry.set_text(config.get(constant))
        else:  # it needs localizing
            entry.set_text(_(config.get(constant)))
        entry.connect("changed", callback, constant)
        entry.set_hexpand(True)
        if label:
            grid.attach(lwidget, col_attach, index, 1, 1)
            grid.attach(entry, col_attach + 1, index, 1, 1)
        else:
            grid.attach(entry, col_attach, index, 1, 1)
        return entry

    def add_pos_int_entry(
        self,
        grid,
        label,
        index,
        constant,
        callback=None,
        config=None,
        col_attach=1,
        helptext="",
    ):
        """
        Adds entry field for positive integers.
        """
        if not config:
            config = self.__config
        lwidget = BasicLabel(_("%s: ") % label)  # needed for French
        entry = Gtk.Entry()
        entry.set_text(str(config.get(constant)))
        entry.set_tooltip_markup(helptext)
        entry.set_hexpand(True)
        if callback:
            entry.connect("changed", callback, constant)
        grid.attach(lwidget, col_attach, index, 1, 1)
        grid.attach(entry, col_attach + 1, index, 1, 1)

    def add_color(self, grid, label, index, constant, config=None, col=0):
        """
        Add color chooser widget with label and hex value to the grid.
        """
        if not config:
            config = self.__config
        lwidget = BasicLabel(_("%s: ") % label)  # needed for French
        colors = config.get(constant)
        if isinstance(colors, list):
            scheme = config.get("colors.scheme")
            hexval = colors[scheme]
        else:
            hexval = colors
        rgba = Gdk.RGBA()
        rgba.parse(hexval)
        entry = Gtk.ColorButton.new_with_rgba(rgba)
        color_hex_label = BasicLabel(hexval)
        color_hex_label.set_hexpand(True)
        entry.connect("notify::color", self.update_color, constant, color_hex_label)
        grid.attach(lwidget, col, index, 1, 1)
        grid.attach(entry, col + 1, index, 1, 1)
        grid.attach(color_hex_label, col + 2, index, 1, 1)
        return entry

    def add_combo(
        self,
        grid,
        label,
        index,
        constant,
        opts,
        callback=None,
        config=None,
        valueactive=False,
        setactive=None,
    ):
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
        lwidget = BasicLabel(_("%s: ") % label)  # needed for French
        store = Gtk.ListStore(int, str)
        for item in opts:
            store.append(item)
        combo = Gtk.ComboBox(model=store)
        cell = Gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, "text", 1)
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
        combo.connect("changed", callback, constant)
        combo.set_hexpand(True)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(combo, 2, index, 1, 1)
        return combo

    def add_slider(
        self, grid, label, index, constant, range, callback=None, config=None, width=1
    ):
        """
        Slider allowing the selection of an integer within a specified range.
        :param range: Tuple containing the minimum and maximum allowed values.
        """
        if not config:
            config = self.__config
        if not callback:
            callback = self.update_slider
        lwidget = BasicLabel(_("%s: ") % label)  # needed for French
        adj = Gtk.Adjustment(
            value=config.get(constant),
            lower=range[0],
            upper=range[1],
            step_increment=1,
            page_increment=0,
            page_size=0,
        )
        slider = Gtk.Scale(adjustment=adj)
        slider.set_digits(0)
        slider.set_value_pos(Gtk.PositionType.BOTTOM)
        slider.connect("value-changed", callback, constant)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(slider, 2, index, width, 1)
        return slider

    def add_spinner(
        self, grid, label, index, constant, range, callback=None, config=None
    ):
        """
        Spinner allowing the selection of an integer within a specified range.
        :param range: Tuple containing the minimum and maximum allowed values.
        """
        if not config:
            config = self.__config
        if not callback:
            callback = self.update_spinner
        lwidget = BasicLabel(_("%s: ") % label)  # needed for French
        adj = Gtk.Adjustment(
            value=config.get(constant),
            lower=range[0],
            upper=range[1],
            step_increment=1,
            page_increment=0,
            page_size=0,
        )
        spinner = Gtk.SpinButton(adjustment=adj, climb_rate=0.0, digits=0)
        spinner.connect("value-changed", callback, constant)
        spinner.set_hexpand(True)
        grid.attach(lwidget, 1, index, 1, 1)
        grid.attach(spinner, 2, index, 1, 1)
        return spinner


# -------------------------------------------------------------------------
#
# GrampsPreferences
#
# -------------------------------------------------------------------------
class GrampsPreferences(ConfigureDialog):
    def __init__(self, uistate, dbstate):
        page_funcs = (
            self.add_data_panel,
            self.add_general_panel,
            self.add_famtree_panel,
            self.add_import_panel,
            self.add_limits_panel,
            self.add_color_panel,
            self.add_symbols_panel,
            self.add_idformats_panel,
            self.add_text_panel,
            self.add_warnings_panel,
            self.add_researcher_panel,
        )
        ConfigureDialog.__init__(
            self,
            uistate,
            dbstate,
            page_funcs,
            GrampsPreferences,
            config,
            on_close=update_constants,
        )
        help_btn = self.window.add_button(_("_Help"), Gtk.ResponseType.HELP)
        help_btn.connect(
            "clicked", lambda x: display_help(WIKI_HELP_PAGE, WIKI_HELP_SEC)
        )
        self.setup_configs("interface.grampspreferences", 700, 450)

    def create_grid(self):
        """
        Gtk.Grid for config panels (tabs).
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        return grid

    def add_researcher_panel(self, configdialog):
        """
        Add the Researcher tab to the preferences.
        """
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = self.create_grid()
        scroll_window.add(grid)

        label = self.add_text(
            grid, _("Researcher"), 0, line_wrap=True, bold=True, start=0, stop=7
        )
        label.set_margin_top(10)

        row = 1
        self.add_entry(grid, _("Name"), row, "researcher.researcher-name", col_attach=1)
        row += 1
        self.add_entry(
            grid, _("Address"), row, "researcher.researcher-addr", col_attach=1
        )
        row += 1
        self.add_entry(
            grid, _("Locality"), row, "researcher.researcher-locality", col_attach=1
        )
        row += 1
        self.add_entry(grid, _("City"), row, "researcher.researcher-city", col_attach=1)
        row += 1
        self.add_entry(
            grid, _("State/County"), row, "researcher.researcher-state", col_attach=1
        )
        row += 1
        self.add_entry(
            grid, _("Country"), row, "researcher.researcher-country", col_attach=1
        )
        row += 1
        self.add_entry(
            grid,
            _("ZIP/Postal Code"),
            row,
            "researcher.researcher-postal",
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid, _("Phone"), row, "researcher.researcher-phone", col_attach=1
        )
        row += 1
        self.add_entry(
            grid, _("Email"), row, "researcher.researcher-email", col_attach=1
        )

        row += 1
        label = self.add_text(
            grid,
            _(
                "Enter information about yourself so people can contact "
                "you when you distribute your Family Tree."
            ),
            row,
            line_wrap=True,
            start=0,
            stop=9,
        )
        label.set_margin_top(10)

        return _("Researcher"), scroll_window

    def add_idformats_panel(self, configdialog):
        """
        Add the ID prefix tab to the preferences.
        """
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = self.create_grid()
        scroll_window.add(grid)

        label = self.add_text(
            grid, _("ID Formats"), 0, line_wrap=True, bold=True, start=0, stop=7
        )
        label.set_margin_top(10)

        row = 1
        self.add_entry(
            grid,
            _("Person"),
            row,
            "preferences.iprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Family"),
            row,
            "preferences.fprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Place"),
            row,
            "preferences.pprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Source"),
            row,
            "preferences.sprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Citation"),
            row,
            "preferences.cprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Media Object"),
            row,
            "preferences.oprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Event"),
            row,
            "preferences.eprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Repository"),
            row,
            "preferences.rprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid,
            _("Note"),
            row,
            "preferences.nprefix",
            self.update_idformat_entry,
            col_attach=1,
        )
        row += 1
        label = self.add_text(
            grid,
            _(
                "Default Gramps ID formats containing a letter prefix"
                ' followed by a numerical string. "I%04d" creates IDs'
                " from I0000 to I9999. Large databases may need larger"
                ' IDs. "I%06d" creates IDs from I000000 to I999999.\n'
            ),
            row,
            line_wrap=True,
            start=0,
            stop=9,
        )
        label.set_margin_top(10)

        return _("ID Formats"), scroll_window

    def add_color_panel(self, configdialog):
        """
        Add the tab to set defaults colors for graph boxes.
        """
        grid = self.create_grid()

        label = self.add_text(
            grid,
            _("Colors used for boxes in the graphical views"),
            0,
            line_wrap=True,
            start=0,
            stop=7,
            bold=True,
        )
        label.set_margin_top(10)

        hbox = Gtk.Box(spacing=12)
        self.color_scheme_box = Gtk.ComboBoxText()
        formats = [_("Light colors"), _("Dark colors")]
        list(map(self.color_scheme_box.append_text, formats))
        scheme = config.get("colors.scheme")
        self.color_scheme_box.set_active(scheme)
        self.color_scheme_box.connect("changed", self.color_scheme_changed)
        lwidget = BasicLabel(_("%s: ") % _("Color scheme"))
        hbox.pack_start(lwidget, False, False, 0)
        hbox.pack_start(self.color_scheme_box, False, False, 0)

        restore_btn = Gtk.Button(label=_("Restore to defaults"))
        restore_btn.set_tooltip_text(_("Restore colors for current theme to default."))
        restore_btn.connect("clicked", self.restore_colors)
        hbox.pack_start(restore_btn, False, False, 0)
        hbox.set_margin_start(6)
        grid.attach(hbox, 0, 1, 7, 1)

        color_type = {
            "Male": _("Colors for Male persons"),
            "Female": _("Colors for Female persons"),
            "Other": _("Colors for people who are neither male nor female"),
            "Unknown": _("Colors for Unknown persons"),
            "Family": _("Colors for Family nodes"),
            "Misc": _("Other colors"),
        }

        bg_alive_text = _("Background for Alive")
        bg_dead_text = _("Background for Dead")
        brd_alive_text = _("Border for Alive")
        brd_dead_text = _("Border for Dead")

        # color label, config constant, group grid row, column, color type
        color_list = [
            # for male
            (bg_alive_text, "male-alive", 1, 1, "Male"),
            (bg_dead_text, "male-dead", 2, 1, "Male"),
            (brd_alive_text, "border-male-alive", 1, 4, "Male"),
            (brd_dead_text, "border-male-dead", 2, 4, "Male"),
            # for female
            (bg_alive_text, "female-alive", 1, 1, "Female"),
            (bg_dead_text, "female-dead", 2, 1, "Female"),
            (brd_alive_text, "border-female-alive", 1, 4, "Female"),
            (brd_dead_text, "border-female-dead", 2, 4, "Female"),
            # for other
            (bg_alive_text, "other-alive", 1, 1, "Other"),
            (bg_dead_text, "other-dead", 2, 1, "Other"),
            (brd_alive_text, "border-other-alive", 1, 4, "Other"),
            (brd_dead_text, "border-other-dead", 2, 4, "Other"),
            # for unknown
            (bg_alive_text, "unknown-alive", 1, 1, "Unknown"),
            (bg_dead_text, "unknown-dead", 2, 1, "Unknown"),
            (brd_alive_text, "border-unknown-alive", 1, 4, "Unknown"),
            (brd_dead_text, "border-unknown-dead", 2, 4, "Unknown"),
            # for family
            (_("Default background"), "family", 1, 1, "Family"),
            (_("Background for Married"), "family-married", 3, 1, "Family"),
            (_("Background for Unmarried"), "family-unmarried", 4, 1, "Family"),
            (_("Background for Civil union"), "family-civil-union", 5, 1, "Family"),
            (_("Background for Unknown"), "family-unknown", 6, 1, "Family"),
            (_("Background for Divorced"), "family-divorced", 7, 1, "Family"),
            (_("Default border"), "border-family", 1, 4, "Family"),
            (_("Border for Divorced"), "border-family-divorced", 7, 4, "Family"),
            # for other
            (_("Background for Home Person"), "home-person", 1, 1, "Misc"),
        ]

        # prepare scrolled window for colors settings
        scroll_window = Gtk.ScrolledWindow()
        colors_grid = self.create_grid()
        colors_grid.set_border_width(0)
        scroll_window.add(colors_grid)
        scroll_window.set_vexpand(True)
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid.attach(scroll_window, 0, 3, 7, 1)

        # add color settings to scrolled window by groups
        row = 0
        self.colors = {}
        for key, frame_lbl in color_type.items():
            group_label = Gtk.Label()
            group_label.set_halign(Gtk.Align.START)
            group_label.set_margin_top(12)
            group_label.set_markup(_("<b>%s</b>") % frame_lbl)
            colors_grid.attach(group_label, 0, row, 6, 1)

            row_added = 0
            for color in color_list:
                if color[4] == key:
                    pref_name = "colors." + color[1]
                    self.colors[pref_name] = self.add_color(
                        colors_grid, color[0], row + color[2], pref_name, col=color[3]
                    )
                    row_added += 1
            row += row_added + 1

        return _("Colors"), grid

    def restore_colors(self, widget=None):
        """
        Restore colors of selected scheme to default.
        """
        scheme = config.get("colors.scheme")
        for key, widget in self.colors.items():
            color = Gdk.RGBA()
            hexval = config.get_default(key)[scheme]
            Gdk.RGBA.parse(color, hexval)
            widget.set_rgba(color)

    def add_warnings_panel(self, configdialog):
        """
        Config tab for Warnings and Error dialogs.
        """
        grid = self.create_grid()

        label = self.add_text(
            grid,
            _("Warnings and Error dialogs"),
            0,
            line_wrap=True,
            bold=True,
            start=0,
            stop=9,
        )
        label.set_margin_top(10)

        row = 1
        self.add_checkbox(
            grid,
            _("Suppress warning when adding parents to a child"),
            row,
            "preferences.family-warn",
            start=1,
        )
        row += 1
        self.add_checkbox(
            grid,
            _("Suppress warning when canceling with changed data"),
            row,
            "interface.dont-ask",
            start=1,
        )
        row += 1
        self.add_checkbox(
            grid,
            _("Suppress warning about missing researcher when" " exporting to GEDCOM"),
            row,
            "behavior.owner-warn",
            start=1,
        )
        row += 1
        self.add_checkbox(
            grid,
            _("Suppress tooltip warnings about data being saved" " immediately"),
            row,
            "behavior.immediate-warn",
            start=1,
        )
        row += 1
        self.add_checkbox(
            grid,
            _("Show plugin status dialog on plugin load error"),
            row,
            "behavior.pop-plugin-status",
            start=1,
        )

        return _("Warnings"), grid

    def _build_name_format_model(self, active):
        """
        Create a common model for ComboBox and TreeView
        """
        name_format_model = Gtk.ListStore(
            GObject.TYPE_INT,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
        )
        index = 0
        the_index = 0
        for num, name, fmt_str, act in _nd.get_name_format():
            translation = fmt_str
            for key in get_keywords():
                if key in translation:
                    translation = translation.replace(
                        key, get_translation_from_keyword(key)
                    )
            self.examplename.set_display_as(num)
            name_format_model.append(
                row=[num, translation, fmt_str, _nd.display_name(self.examplename)]
            )
            if num == active:
                the_index = index
            index += 1
        return name_format_model, the_index

    def __new_name(self, obj):
        lyst = [
            "%s, %s %s (%s)"
            % (_("Surname"), _("Given"), _("Suffix"), _("Common", "Name")),
            "%s, %s %s (%s)" % (_("Surname"), _("Given"), _("Suffix"), _("Nickname")),
            "%s, %s %s (%s)"
            % (_("Surname"), _("Common", "Name"), _("Suffix"), _("Nickname")),
            "%s, %s %s" % (_("Surname"), _("Common", "Name"), _("Suffix")),
            "%s, %s %s (%s)" % (_("SURNAME"), _("Given"), _("Suffix"), _("Call")),
            "%s, %s (%s)" % (_("Surname"), _("Given"), _("Common", "Name")),
            "%s, %s (%s)" % (_("Surname"), _("Common", "Name"), _("Nickname")),
            "%s %s" % (_("Given"), _("Surname")),
            "%s %s, %s" % (_("Given"), _("Surname"), _("Suffix")),
            "%s %s %s" % (_("Given"), _("NotPatronymic"), _("Patronymic")),
            "%s, %s %s (%s)"
            % (_("SURNAME"), _("Given"), _("Suffix"), _("Common", "Name")),
            "%s, %s (%s)" % (_("SURNAME"), _("Given"), _("Common", "Name")),
            "%s, %s (%s)" % (_("SURNAME"), _("Given"), _("Nickname")),
            "%s %s" % (_("Given"), _("SURNAME")),
            "%s %s, %s" % (_("Given"), _("SURNAME"), _("Suffix")),
            "%s /%s/" % (_("Given"), _("SURNAME")),
            "%s %s, %s" % (_("Given"), _("Rawsurnames"), _("Suffix")),
        ]
        # repeat above list, but not translated.
        fmtlyst = [
            "%s, %s %s (%s)" % (("Surname"), ("Given"), ("Suffix"), ("Common")),
            "%s, %s %s (%s)" % (("Surname"), ("Given"), ("Suffix"), ("Nickname")),
            "%s, %s %s (%s)" % (("Surname"), ("Common"), ("Suffix"), ("Nickname")),
            "%s, %s %s" % (("Surname"), ("Common"), ("Suffix")),
            "%s, %s %s (%s)" % (("SURNAME"), ("Given"), ("Suffix"), ("Call")),
            "%s, %s (%s)" % (("Surname"), ("Given"), ("Common")),
            "%s, %s (%s)" % (("Surname"), ("Common"), ("Nickname")),
            "%s %s" % (("Given"), ("Surname")),
            "%s %s, %s" % (("Given"), ("Surname"), ("Suffix")),
            "%s %s %s" % (("Given"), ("NotPatronymic"), ("Patronymic")),
            "%s, %s %s (%s)" % (("SURNAME"), ("Given"), ("Suffix"), ("Common")),
            "%s, %s (%s)" % (("SURNAME"), ("Given"), ("Common")),
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
        fmt_str = _nd.format_str(self.examplename, fmt)
        node = self.fmt_model.append(row=[i, f, fmt, fmt_str])
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
                pass  # skip comparison with self
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
        self.format_list.set_tooltip_text(_("Enter to save, Esc to cancel " "editing"))

    def __cancel_change(self, dummy_renderer):
        """
        Break off the editing of a name format.
        """
        self.format_list.set_tooltip_text("")
        num = self.selected_fmt[COL_NUM]
        if any(fmt[COL_NUM] == num for fmt in self.dbstate.db.name_formats):
            return
        else:  # editing a new format not yet in db, cleanup is needed
            self.fmt_model.remove(self.iter)
            _nd.del_name_format(num)
            self.insert_button.set_sensitive(True)

    def __change_name(self, text, path, new_text):
        """
        Called when a name format changed and needs to be stored in the db.
        """
        self.format_list.set_tooltip_text("")
        if len(new_text) > 0 and text != new_text:
            # build a pattern from translated pattern:
            pattern = new_text
            if len(new_text) > 2 and new_text[0] == '"' and new_text[-1] == '"':
                pass
            else:
                for key in get_translations():
                    if key in pattern:
                        pattern = pattern.replace(
                            key, get_keyword_from_translation(key)
                        )
            # now build up a proper translation:
            translation = pattern
            if len(new_text) > 2 and new_text[0] == '"' and new_text[-1] == '"':
                pass
            else:
                for key in get_keywords():
                    if key in translation:
                        translation = translation.replace(
                            key, get_translation_from_keyword(key)
                        )
            num, name, fmt = self.selected_fmt[COL_NUM:COL_EXPL]
            node = self.fmt_model.get_iter(path)
            oldname = self.fmt_model.get_value(node, COL_NAME)
            # check to see if this pattern already exists
            if self.__check_for_name(translation, node):
                ErrorDialog(
                    _("This format exists already."), translation, parent=self.window
                )
                self.edit_button.emit("clicked")
                return
            # else, change the name
            self.edit_button.set_sensitive(True)
            self.remove_button.set_sensitive(True)
            self.insert_button.set_sensitive(True)
            exmpl = _nd.format_str(self.examplename, pattern)
            self.fmt_model.set(
                self.iter, COL_NAME, translation, COL_FMT, pattern, COL_EXPL, exmpl
            )
            self.selected_fmt = (num, translation, pattern, exmpl)
            _nd.edit_name_format(num, translation, pattern)
            name_format = _nd.get_name_format(only_custom=True, only_active=False)
            self.dbstate.db.name_formats = name_format

    def __format_change(self, obj):
        try:
            t = _nd.format_str(self.name, escape(obj.get_text()))
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
        name_column = Gtk.TreeViewColumn(_("Format"), name_renderer, text=COL_NAME)
        name_renderer.set_property("editable", False)
        name_renderer.connect("editing-started", self.__start_name_editing)
        name_renderer.connect("edited", self.__change_name)
        name_renderer.connect("editing-canceled", self.__cancel_change)
        self.name_renderer = name_renderer
        format_tree.append_column(name_column)
        example_renderer = Gtk.CellRendererText()
        example_column = Gtk.TreeViewColumn(
            _("Example"), example_renderer, text=COL_EXPL
        )
        format_tree.append_column(example_column)
        format_tree.get_selection().connect("changed", self.cb_format_tree_select)

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

        self.insert_button = Gtk.Button.new_with_mnemonic(_("_Add"))
        self.insert_button.connect("clicked", self.__new_name)

        self.edit_button = Gtk.Button.new_with_mnemonic(_("_Edit"))
        self.edit_button.connect("clicked", self.__edit_name)
        self.edit_button.set_sensitive(False)

        self.remove_button = Gtk.Button.new_with_mnemonic(_("_Remove"))
        self.remove_button.connect("clicked", self.cb_del_fmt_str)
        self.remove_button.set_sensitive(False)

        grid.attach(self.insert_button, 0, 1, 1, 1)
        grid.attach(self.remove_button, 1, 1, 1, 1)
        grid.attach(self.edit_button, 2, 1, 1, 1)
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
        config.set("preferences.name-format", new_idx)
        _nd.set_default_format(new_idx)
        self.uistate.emit("nameformat-changed")

    def cb_place_fmt_changed(self, obj):
        """
        Called when the place format is changed.
        """
        config.set("preferences.place-format", obj.get_active())
        self.uistate.emit("placeformat-changed")

    def cb_coord_fmt_changed(self, obj):
        """
        Called when the coordinates format is changed.
        """
        config.set("preferences.coord-format", obj.get_active())
        self.uistate.emit("placeformat-changed")  # Do we need to add a new signal ?

    def cb_coord_fmt_rebuild(self):
        """
        Called to rebuild the coordinates format list.
        """
        model = Gtk.ListStore(str)
        for number, fmt in enumerate(coord_formats):
            model.append([fmt + "\t" + coord_formats_desc[number]])
        self.cformat.set_model(model)
        self.cformat.set_active(0)

    def cb_pa_sur_changed(self, *args):
        """
        Checkbox patronymic as surname changed, propagate to namedisplayer
        """
        _nd.change_pa_sur()
        self.uistate.emit("nameformat-changed")

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
        self.name_renderer.set_property("editable", idx)

    def cb_del_fmt_str(self, obj):
        """
        Name format editor Remove button callback
        """
        num = self.selected_fmt[COL_NUM]

        if _nd.get_default_format() == num:
            self.fmt_obox.set_active(0)

        self.fmt_model.remove(self.iter)
        _nd.set_format_inactive(num)
        self.dbstate.db.name_formats = _nd.get_name_format(
            only_custom=True, only_active=False
        )

    def cb_grampletbar_close(self, obj):
        """
        Gramplet bar close button preference callback
        """
        self.uistate.emit("grampletbar-close-changed")

    def cb_toolbar_changed(self, obj):
        """
        Called when the toolbar is changed.
        """
        self.uistate.emit("toolbar-changed")

    def add_data_panel(self, configdialog):
        """
        Config tab with user Appearance and format settings.
        """
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = self.create_grid()
        scroll_window.add(grid)

        label = self.add_text(
            grid, _("Display Options"), 0, line_wrap=True, bold=True, start=0, stop=3
        )
        label.set_margin_top(10)

        row = 1
        # Place format:
        self.pformat = Gtk.ComboBox()
        self.pformat.set_hexpand(True)
        renderer = Gtk.CellRendererText()
        self.pformat.pack_start(renderer, True)
        self.pformat.add_attribute(renderer, "text", 0)
        self.cb_place_fmt_rebuild()
        active = config.get("preferences.place-format")
        self.pformat.set_active(active)
        self.pformat.connect("changed", self.cb_place_fmt_changed)
        hbox = Gtk.Box()
        self.fmt_btn = Gtk.Button(label=("%s..." % _("Edit")))
        self.fmt_btn.connect("clicked", self.cb_place_fmt_dialog)
        cb_widget = self.add_checkbox(
            grid,
            _("%s: ") % _("Automate Place format"),
            row,
            "preferences.place-auto",
            start=1,
            stop=2,
            extra_callback=self.auto_title_changed,
            tooltip=_(
                "Enables automatic place title generation " "using specified format."
            ),
        )
        self.auto_title_changed(cb_widget)
        hbox.pack_start(self.pformat, True, True, 0)
        hbox.pack_start(self.fmt_btn, False, False, 0)
        grid.attach(hbox, 2, row, 2, 1)

        row += 1
        # Coordinates display format:
        self.cformat = Gtk.ComboBox()
        self.cformat.set_hexpand(True)
        renderer = Gtk.CellRendererText()
        self.cformat.pack_start(renderer, True)
        self.cformat.add_attribute(renderer, "text", 0)
        self.cb_coord_fmt_rebuild()
        active = config.get("preferences.coord-format")
        self.cformat.set_active(active)
        self.cformat.connect("changed", self.cb_coord_fmt_changed)
        hbox = Gtk.Box()
        lwidget = BasicLabel(_("%s: ") % _("Coordinates format"))
        lwidget.set_use_underline(True)
        lwidget.set_mnemonic_widget(self.cformat)
        hbox.pack_start(self.cformat, True, True, 0)
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(hbox, 2, row, 2, 1)

        row += 1
        # Display name:
        self.examplename = Name()
        examplesurname = Surname()
        examplesurnamesecond = Surname()
        examplesurnamepat = Surname()
        self.examplename.set_title("Dr.")
        self.examplename.set_first_name("Edwin Jose")
        examplesurname.set_prefix("von der")
        examplesurname.set_surname("Smith")
        examplesurname.set_connector("and")
        self.examplename.add_surname(examplesurname)
        examplesurnamesecond.set_surname("Weston")
        self.examplename.add_surname(examplesurnamesecond)
        examplesurnamepat.set_surname("Wilson")
        examplesurnamepat.set_origintype(NameOriginType(NameOriginType.PATRONYMIC))
        self.examplename.add_surname(examplesurnamepat)
        self.examplename.set_primary_surname(0)
        self.examplename.set_suffix("Sr")
        self.examplename.set_call_name("Jose")
        self.examplename.set_nick_name("Ed")
        self.examplename.set_family_nick_name("Underhills")
        # get the model for the combo and the treeview
        active = _nd.get_default_format()
        self.fmt_model, active = self._build_name_format_model(active)
        # set up the combo to choose the preset format
        self.fmt_obox = Gtk.ComboBox()
        cell = Gtk.CellRendererText()
        cell.set_property("ellipsize", Pango.EllipsizeMode.END)
        self.fmt_obox.pack_start(cell, True)
        self.fmt_obox.add_attribute(cell, "text", 1)
        self.fmt_obox.set_model(self.fmt_model)
        # set the default value as active in the combo
        self.fmt_obox.set_active(active)
        self.fmt_obox.connect("changed", self.cb_name_changed)
        # label for the combo
        lwidget = BasicLabel(_("%s: ") % _("Name format"))
        lwidget.set_use_underline(True)
        lwidget.set_mnemonic_widget(self.fmt_obox)
        hbox = Gtk.Box()
        btn = Gtk.Button(label=("%s..." % _("Edit")))
        btn.connect("clicked", self.cb_name_dialog)
        hbox.pack_start(self.fmt_obox, True, True, 0)
        hbox.pack_start(btn, False, False, 0)
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(hbox, 2, row, 2, 1)

        row += 1
        label = self.add_text(
            grid,
            _("Custom name display options are unique to" " each family tree."),
            row,
            line_wrap=True,
            start=2,
            stop=9,
        )
        # label.set_margin_top(6)

        row += 1
        # Pa/Matronymic surname handling
        self.add_checkbox(
            grid,
            _("Consider single pa/matronymic as surname"),
            row,
            "preferences.patronimic-surname",
            start=2,
            stop=3,
            extra_callback=self.cb_pa_sur_changed,
        )

        row += 1
        # Date format:
        obox = Gtk.ComboBoxText()
        formats = get_date_formats()
        list(map(obox.append_text, formats))
        active = config.get("preferences.date-format")
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect("changed", self.date_format_changed)
        lwidget = BasicLabel(_("%s: ") % _("Date format *"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        # Age precision:
        # precision=1 for "year", 2: "year, month" or 3: "year, month, days"
        obox = Gtk.ComboBoxText()
        age_precision = [_("Years"), _("Years, Months"), _("Years, Months, Days")]
        list(map(obox.append_text, age_precision))
        # Combo_box active index is from 0 to 2, we need values from 1 to 3
        active = config.get("preferences.age-display-precision") - 1
        if active >= 0 and active <= 2:
            obox.set_active(active)
        else:
            obox.set_active(0)
        obox.connect(
            "changed",
            lambda obj: config.set(
                "preferences.age-display-precision", obj.get_active() + 1
            ),
        )
        lwidget = BasicLabel(_("%s: ") % _("Age display precision *"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        # Display rounded year
        self.add_checkbox(
            grid,
            _("Round the year"),
            row,
            "preferences.age-rounded-year",
            start=2,
            stop=3,
        )

        row += 1
        # Display ages for events after death
        self.add_checkbox(
            grid,
            _("Display ages for events after death *"),
            row,
            "preferences.age-after-death",
            start=2,
            stop=3,
        )

        row += 1
        # Calendar format on report:
        obox = Gtk.ComboBoxText()
        list(map(obox.append_text, Date.ui_calendar_names))
        active = config.get("preferences.calendar-format-report")
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect("changed", self.date_calendar_changed)
        lwidget = BasicLabel(_("%s: ") % _("Calendar on reports"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        # Calendar format on input:
        obox = Gtk.ComboBoxText()
        list(map(obox.append_text, Date.ui_calendar_names))
        active = config.get("preferences.calendar-format-input")
        if active >= len(formats):
            active = 0
        obox.set_active(active)
        obox.connect("changed", self.date_calendar_for_input_changed)
        lwidget = BasicLabel(_("%s: ") % _("Calendar on input"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        # Birthday on february 29
        feb29 = Gtk.ComboBoxText()
        show_on = [
            _("On the previous day"),
            _("On the next day"),
            _("Only on leap years"),
        ]
        list(map(feb29.append_text, show_on))
        active = config.get("preferences.february-29")
        feb29.set_active(active)
        feb29.connect("changed", self.date_february_29_display_on)
        ttip = _(
            "For non leap years, anniversaries are displayed on either "
            "February 28, March 1 or not at all in Gregorian calendars"
        )
        feb29.set_tooltip_text(ttip)
        lwidget = BasicLabel(_("%s: ") % _("Show leap day anniversaries"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(feb29, 2, row, 2, 1)

        row += 1
        # Status bar:
        obox = Gtk.ComboBoxText()
        formats = [_("Active person's name and ID"), _("Relationship to home person")]
        list(map(obox.append_text, formats))
        active = config.get("interface.statusbar")
        if active < 2:
            obox.set_active(0)
        else:
            obox.set_active(1)
        obox.connect(
            "changed",
            lambda obj: config.set("interface.statusbar", 2 * obj.get_active()),
        )
        lwidget = BasicLabel(_("%s: ") % _("Status bar"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        lwidget = BasicLabel(_("%s: ") % _("Citation formatter"))
        grid.attach(lwidget, 1, row, 1, 1)
        obox = self.__create_cite_combo()
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        label = self.add_text(
            grid, _("\nInput Options"), row, line_wrap=True, bold=True, start=0, stop=3
        )
        label.set_margin_top(10)

        row += 1
        # Surname guessing:
        obox = Gtk.ComboBoxText()
        formats = _surname_styles
        list(map(obox.append_text, formats))
        obox.set_active(config.get("behavior.surname-guessing"))
        obox.connect(
            "changed",
            lambda obj: config.set("behavior.surname-guessing", obj.get_active()),
        )
        lwidget = BasicLabel(_("%s: ") % _("Surname guessing"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        # Default Family Relationship
        obox = Gtk.ComboBoxText()
        formats = FamilyRelType().get_standard_names()
        list(map(obox.append_text, formats))
        obox.set_active(config.get("preferences.family-relation-type"))
        obox.connect(
            "changed",
            lambda obj: config.set(
                "preferences.family-relation-type", obj.get_active()
            ),
        )
        lwidget = BasicLabel(_("%s: ") % _("Default family relationship"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 2, 1)

        row += 1
        self.add_checkbox(
            grid,
            _("Hide LDS tab in person and family editors"),
            row,
            "interface.hide-lds",
        )

        row += 1
        label = self.add_text(
            grid,
            _("* Requires Restart"),
            row,
            line_wrap=True,
            bold=True,
            start=0,
            stop=3,
        )
        label.set_margin_top(10)

        return _("Data"), scroll_window

    def auto_title_changed(self, obj):
        """
        Update sensitivity of place format widget.
        """
        state = obj.get_active()
        self.pformat.set_sensitive(state)
        self.fmt_btn.set_sensitive(state)

    def add_text_panel(self, configdialog):
        """
        Config tab for Text settings.
        """
        grid = self.create_grid()

        label = self.add_text(
            grid,
            _("Conditional Text Replacements"),
            0,
            line_wrap=True,
            bold=True,
            start=0,
            stop=7,
        )
        label.set_margin_top(10)

        row = 1
        self.add_entry(
            grid, _("Missing surname"), row, "preferences.no-surname-text", col_attach=1
        )
        row += 1
        self.add_entry(
            grid,
            _("Missing given name"),
            row,
            "preferences.no-given-text",
            col_attach=1,
        )
        row += 1
        self.add_entry(
            grid, _("Missing record"), row, "preferences.no-record-text", col_attach=1
        )
        row += 1
        self.add_entry(
            grid,
            _("Private surname"),
            row,
            "preferences.private-surname-text",
            col_attach=1,
            localized_config=False,
        )
        row += 1
        self.add_entry(
            grid,
            _("Private given name"),
            row,
            "preferences.private-given-text",
            col_attach=1,
            localized_config=False,
        )
        row += 1
        self.add_entry(
            grid,
            _("Private record"),
            row,
            "preferences.private-record-text",
            col_attach=1,
        )
        row += 1
        return _("Text"), grid

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
        config.set("colors.scheme", scheme)
        for key, widget in self.colors.items():
            color = Gdk.RGBA()
            hexval = config.get(key)[scheme]
            Gdk.RGBA.parse(color, hexval)
            widget.set_rgba(color)

    def cb_place_fmt_dialog(self, button):
        """
        Called to invoke the place format editor.
        """
        EditPlaceFormat(
            self.uistate, self.dbstate, self.track, self.cb_place_fmt_rebuild
        )

    def cb_place_fmt_rebuild(self):
        """
        Called to rebuild the place format list.
        """
        model = Gtk.ListStore(str)
        for fmt in _pd.get_formats():
            model.append([fmt.name])
        self.pformat.set_model(model)
        self.pformat.set_active(0)

    def toggle_tag_on_import(self, obj):
        """
        Update Entry sensitive for tag on import.
        """
        self.tag_format_entry.set_sensitive(obj.get_active())

    def date_format_changed(self, obj):
        """
        Save "Date format" option.
        And show notify message to restart Gramps.
        """
        config.set("preferences.date-format", obj.get_active())
        OkDialog(
            _("Change is not immediate"),
            _(
                "Changing the date format will not take "
                "effect until the next time Gramps is started."
            ),
            parent=self.window,
        )

    def date_calendar_changed(self, obj):
        """
        Save "Date calendar" option.
        """
        config.set("preferences.calendar-format-report", obj.get_active())

    def date_calendar_for_input_changed(self, obj):
        """
        Save "Date calendar for input" option.
        """
        config.set("preferences.calendar-format-input", obj.get_active())

    def date_february_29_display_on(self, obj):
        """
        Save "February 29 display on " option.
        """
        config.set("preferences.february-29", obj.get_active())

    def autobackup_changed(self, obj):
        """
        Save "Autobackup" option on change.
        """
        active = obj.get_active()
        config.set("database.autobackup", active)
        self.uistate.set_backup_timer()

    def add_limits_panel(self, configdialog):
        """
        Config tab with 'about, before, after' limitation settings.
        """
        grid = self.create_grid()

        label = self.add_text(
            grid, _("Calculation limits"), 0, line_wrap=True, bold=True, start=0, stop=7
        )
        label.set_margin_top(10)

        row = 1
        self.add_spinner(
            grid,
            _("Date 'about' year range: (date ± #)"),
            row,
            "behavior.date-about-range",
            (1, 9999),
        )
        row += 1
        self.add_spinner(
            grid,
            _("Date 'after' year range:  (date + #)"),
            row,
            "behavior.date-after-range",
            (1, 9999),
        )
        row += 1
        self.add_spinner(
            grid,
            _("Date 'before' year range: (date - #)"),
            row,
            "behavior.date-before-range",
            (1, 9999),
        )
        row += 1
        self.add_spinner(
            grid,
            _("Maximum age probably alive"),
            row,
            "behavior.max-age-prob-alive",
            (80, 140),
        )
        row += 1
        self.add_spinner(
            grid,
            _("Maximum sibling age difference"),
            row,
            "behavior.max-sib-age-diff",
            (10, 30),
        )
        row += 1
        self.add_spinner(
            grid,
            _("Minimum years between generations"),
            row,
            "behavior.min-generation-years",
            (5, 20),
        )
        row += 1
        self.add_spinner(
            grid,
            _("Average years between generations"),
            row,
            "behavior.avg-generation-gap",
            (10, 30),
        )
        row += 1
        self.add_spinner(
            grid,
            _("Max generations for relationships"),
            row,
            "behavior.generation-depth",
            (5, 50),
            self.update_gendepth,
        )

        return _("Limits"), grid

    def add_general_panel(self, configdialog):
        """
        Config tab with 'General' Gramps settings.
        """
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = self.create_grid()
        scroll_window.add(grid)

        label = self.add_text(
            grid,
            _("Environment Settings"),
            0,
            line_wrap=True,
            bold=True,
            start=0,
            stop=7,
        )
        label.set_margin_top(10)

        row = 1
        self.add_checkbox(
            grid,
            _("Display Tip of the Day"),
            row,
            "behavior.use-tips",
            start=1,
            stop=3,
            tooltip=_("Show useful information about using " "Gramps on startup."),
        )
        row += 1
        self.add_checkbox(
            grid,
            _("Remember last Family Tree"),
            row,
            "behavior.autoload",
            start=1,
            stop=3,
            tooltip=_(
                "Don't open dialog to choose family "
                "tree to load on startup, "
                "just load last used."
            ),
        )
        row += 1
        self.add_checkbox(
            grid,
            _("Remember last view displayed"),
            row,
            "preferences.use-last-view",
            start=1,
            stop=3,
            tooltip=_("Remember last view displayed " "and open it next time."),
        )
        row += 1
        obj = self.add_checkbox(
            grid,
            _("Enable spell checker"),
            row,
            "behavior.spellcheck",
            start=1,
            stop=3,
            tooltip=_("Enable the spelling checker" " for notes."),
        )
        if not HAVE_GSPELL:
            obj.set_sensitive(False)
            spell_dict = {
                "gramps_wiki_build_spell_url": URL_WIKISTRING
                + "GEPS_029:_GTK3-GObject_introspection"
                "_Conversion#Spell_Check_Install"
            }
            obj.set_tooltip_text(
                _(
                    "Gspell not loaded. "
                    "Spell checking will not be available.\n"
                    "To build it for Gramps see "
                    "%(gramps_wiki_build_spell_url)s"
                )
                % spell_dict
            )

        row += 1
        # Text in sidebar:
        self.add_checkbox(
            grid,
            _("Show text label beside Navigator buttons *"),
            row,
            "interface.sidebar-text",
            start=1,
            stop=3,
            tooltip=_(
                "Show or hide text beside Navigator buttons "
                "(People, Families, Events...).\n"
                "Requires Gramps restart to apply."
            ),
        )

        row += 1
        # Show Tools Icon:
        self.add_checkbox(
            grid,
            _("Show Clipboard icon on toolbar"),
            row,
            "interface.toolbar-clipboard",
            start=1,
            stop=3,
            tooltip=_("Show or hide the Clipboard icon on the toolbar."),
            extra_callback=self.cb_toolbar_changed,
        )

        row += 1
        # Show Tools Icon:
        self.add_checkbox(
            grid,
            _("Show Reports icon on toolbar"),
            row,
            "interface.toolbar-reports",
            start=1,
            stop=3,
            tooltip=_("Show or hide the Reports icon on the toolbar."),
            extra_callback=self.cb_toolbar_changed,
        )

        row += 1
        # Show Tools Icon:
        self.add_checkbox(
            grid,
            _("Show Tools icon on toolbar"),
            row,
            "interface.toolbar-tools",
            start=1,
            stop=3,
            tooltip=_("Show or hide the Tools icon on the toolbar."),
            extra_callback=self.cb_toolbar_changed,
        )

        row += 1
        # Show Addons Icon:
        self.add_checkbox(
            grid,
            _("Show Addons icon on toolbar"),
            row,
            "interface.toolbar-addons",
            start=1,
            stop=3,
            tooltip=_("Show or hide the Addons icon on the toolbar."),
            extra_callback=self.cb_toolbar_changed,
        )

        row += 1
        # Show Preferences icon:
        self.add_checkbox(
            grid,
            _("Show Preferences icon on toolbar"),
            row,
            "interface.toolbar-preference",
            start=1,
            stop=3,
            tooltip=_("Show or hide the Preferences icon on the toolbar."),
            extra_callback=self.cb_toolbar_changed,
        )

        row += 1
        # Gramplet bar close buttons:
        self.add_checkbox(
            grid,
            _("Show close button in gramplet bar tabs"),
            row,
            "interface.grampletbar-close",
            start=1,
            stop=3,
            extra_callback=self.cb_grampletbar_close,
            tooltip=_("Show close button to simplify removing gramplets " "from bars."),
        )

        row += 1
        # Markup for invalid date format
        self.add_pos_int_entry(
            grid,
            _("Markup for invalid date format"),
            row,
            "preferences.invalid-date-format",
            self.update_markup_entry,
            col_attach=1,
            helptext=_(
                "Convenience markups are:\n"
                "<b>&lt;b&gt;Bold&lt;/b&gt;</b>\n"
                "<big>&lt;big&gt;"
                "Makes font relatively larger&lt;/big&gt;</big>\n"
                "<i>&lt;i&gt;Italic&lt;/i&gt;</i>\n"
                "<s>&lt;s&gt;Strikethrough&lt;/s&gt;</s>\n"
                "<sub>&lt;sub&gt;Subscript&lt;/sub&gt;</sub>\n"
                "<sup>&lt;sup&gt;Superscript&lt;/sup&gt;</sup>\n"
                "<small>&lt;small&gt;"
                "Makes font relatively smaller&lt;/small&gt;</small>\n"
                "<tt>&lt;tt&gt;Monospace font&lt;/tt&gt;</tt>\n"
                "<u>&lt;u&gt;Underline&lt;/u&gt;</u>\n\n"
                "For example: &lt;u&gt;&lt;b&gt;%s&lt;/b&gt;&lt;/u&gt;\n"
                "will display <u><b>Underlined bold date</b></u>.\n"
            ),
        )

        row += 1
        # height multiple surname table
        self.add_pos_int_entry(
            grid,
            _("Multiple surname box height"),
            row,
            "interface.surname-box-height",
            self.update_surn_height,
            col_attach=1,
            helptext=_(
                "Enter height in pixels. When multiple surnames are"
                " entered, these names display in a box. This"
                " setting sets the size of this box."
            ),
        )

        row += 1
        label = self.add_text(
            grid,
            _("* Requires Restart"),
            row,
            line_wrap=True,
            bold=True,
            start=0,
            stop=3,
        )
        label.set_margin_top(10)

        return _("General"), scroll_window

    def database_backend_changed(self, obj):
        """
        Update Database Backend.
        """
        the_list = obj.get_model()
        the_iter = obj.get_active_iter()
        db_choice = the_list.get_value(the_iter, 2)
        config.set("database.backend", db_choice)
        self.set_connection_widgets(db_choice)

    def set_connection_widgets(self, db_choice):
        """
        Sets the connection widgets insensitive for embedded databases.
        """
        for widget in self.connection_widgets:
            if db_choice in ("bsddb", "sqlite"):
                widget.set_sensitive(False)
            else:
                widget.set_sensitive(True)

    def cite_changed(self, obj):
        """
        Update Database Backend.
        """
        the_list = obj.get_model()
        the_iter = obj.get_active_iter()
        cite_choice = the_list.get_value(the_iter, 2)
        config.set("preferences.cite-plugin", cite_choice)

    def add_famtree_panel(self, configdialog):
        """
        Config tab for family tree, backup and Media path settings.
        """
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = self.create_grid()
        scroll_window.add(grid)

        label = self.add_text(
            grid, _("Database Setting"), 0, line_wrap=True, bold=True, start=0, stop=7
        )
        label.set_margin_top(10)

        row = 1
        lwidget = BasicLabel(_("%s: ") % _("Database backend"))
        grid.attach(lwidget, 1, row, 1, 1)
        obox = self.__create_backend_combo()
        grid.attach(obox, 2, row, 1, 1)

        row += 1
        label = self.add_text(
            grid,
            _("\nDatabase Location"),
            row,
            line_wrap=True,
            bold=True,
            start=0,
            stop=7,
        )
        label.set_margin_top(10)

        row += 1
        self.connection_widgets = []
        entry = self.add_entry(grid, _("Host"), row, "database.host", col_attach=1)
        self.connection_widgets.append(entry)

        row += 1
        entry = self.add_entry(grid, _("Port"), row, "database.port", col_attach=1)
        self.connection_widgets.append(entry)

        row += 1
        self.set_connection_widgets(config.get("database.backend"))

        self.dbpath_entry = Gtk.Entry()
        self.add_path_box(
            grid,
            _("Database path"),
            row,
            self.dbpath_entry,
            config.get("database.path"),
            self.set_dbpath,
            self.select_dbpath,
        )

        row += 1
        label = self.add_text(
            grid,
            _("\nBackup Management"),
            row,
            line_wrap=True,
            bold=True,
            start=0,
            stop=7,
        )
        label.set_margin_top(10)

        row += 1
        self.backup_path_entry = Gtk.Entry()
        self.add_path_box(
            grid,
            _("Backup path"),
            row,
            self.backup_path_entry,
            config.get("database.backup-path"),
            self.set_backup_path,
            self.select_backup_path,
        )
        row += 1
        self.add_checkbox(
            grid,
            _("Backup on exit"),
            row,
            "database.backup-on-exit",
            stop=3,
            tooltip=_(
                "Backup Your family tree on exit " "to Backup path specified above."
            ),
        )
        row += 1
        # Check for updates:
        obox = Gtk.ComboBoxText()
        formats = [
            _("Never"),
            _("Every 15 minutes"),
            _("Every 30 minutes"),
            _("Every hour"),
            _("Every 12 hours"),
            _("Every day"),
        ]
        list(map(obox.append_text, formats))
        active = config.get("database.autobackup")
        obox.set_active(active)
        obox.connect("changed", self.autobackup_changed)
        lwidget = BasicLabel(_("%s: ") % _("Autobackup"))
        grid.attach(lwidget, 1, row, 1, 1)
        grid.attach(obox, 2, row, 1, 1)

        row += 1
        label = self.add_text(
            grid,
            _("\nFamily Tree's Media path"),
            row,
            line_wrap=True,
            bold=True,
            start=0,
            stop=7,
        )
        label.set_margin_top(10)

        row += 1
        self.path_entry = Gtk.Entry()
        self.add_path_box(
            grid,
            _("Base media path"),
            row,
            self.path_entry,
            self.dbstate.db.get_mediapath(),
            self.set_mediapath,
            self.select_mediapath,
        )

        row += 1
        label = self.add_text(
            grid,
            _(
                "The base relative media path is specific to the active"
                " family tree. It is not a global setting. Each family"
                " tree is able to have a unique relative media path that"
                " is stored with the database."
            ),
            row,
            line_wrap=True,
            start=1,
            stop=3,
        )
        label.set_margin_top(10)

        return _("Family Tree"), scroll_window

    def add_import_panel(self, configdialog):
        """
        Config tab for Import settings.
        """
        grid = self.create_grid()

        label = self.add_text(
            grid, _("Tag Records"), 0, line_wrap=True, bold=True, start=0, stop=7
        )
        label.set_margin_top(10)

        row = 1
        cb_const = "preferences.tag-on-import"
        # tag Entry
        self.tag_format_entry = Gtk.Entry()
        tag_const = "preferences.tag-on-import-format"
        tag_data = _(config.get(tag_const))
        if not tag_data:
            # set default value if Entry is empty
            tag_data = config.get_default(tag_const)
            config.set(cb_const, False)
            config.set(tag_const, tag_data)
        self.tag_format_entry.set_text(tag_data)
        self.tag_format_entry.connect("changed", self.update_entry, tag_const)
        self.tag_format_entry.set_hexpand(True)
        self.tag_format_entry.set_sensitive(config.get(cb_const))

        self.add_checkbox(
            grid,
            _("Add tag on import"),
            row,
            cb_const,
            start=1,
            stop=2,
            extra_callback=self.toggle_tag_on_import,
            tooltip=_(
                "Specified tag will be added to all records on import.\n"
                "Clear to set default value."
            ),
        )
        grid.attach(self.tag_format_entry, 2, row, 1, 1)

        row += 1
        label = self.add_text(
            grid,
            _("\nSource GEDCOM import"),
            row,
            line_wrap=True,
            bold=True,
            start=0,
            stop=7,
        )
        label.set_margin_top(10)

        row += 1
        self.add_checkbox(
            grid,
            _("Add default source on GEDCOM import"),
            row,
            "preferences.default-source",
            start=1,
            stop=3,
        )

        return _("Import"), grid

    def __create_backend_combo(self):
        """
        Create backend selection widget.
        """
        backend_plugins = self.uistate.viewmanager._pmgr.get_reg_databases()
        obox = Gtk.ComboBox()
        cell = Gtk.CellRendererText()
        obox.pack_start(cell, True)
        obox.add_attribute(cell, "text", 1)
        # Build model:
        model = Gtk.ListStore(
            GObject.TYPE_INT, GObject.TYPE_STRING, GObject.TYPE_STRING
        )
        count = 0
        active = 0
        default = config.get("database.backend")
        for plugin in sorted(backend_plugins, key=lambda plugin: plugin.name):
            if plugin.id == default:
                active = count
            if plugin.id == "bsddb":
                continue  # dsddb is deprecated, so don't allow setting
            model.append(row=[count, plugin.name, plugin.id])
            count += 1
        obox.set_model(model)
        # set the default value as active in the combo
        obox.set_active(active)
        obox.connect("changed", self.database_backend_changed)
        return obox

    def __create_cite_combo(self):
        """
        Create cite selection widget.
        """
        backend_plugins = self.uistate.viewmanager._pmgr.get_reg_cite()
        obox = Gtk.ComboBox()
        cell = Gtk.CellRendererText()
        obox.pack_start(cell, True)
        obox.add_attribute(cell, "text", 1)
        # Build model:
        model = Gtk.ListStore(
            GObject.TYPE_INT, GObject.TYPE_STRING, GObject.TYPE_STRING
        )
        count = 0
        active = 0
        default = config.get("preferences.cite-plugin")
        for plugin in sorted(backend_plugins, key=lambda plugin: plugin.name):
            if plugin.id == default:
                active = count
            model.append(row=[count, plugin.name, plugin.id])
            count += 1
        obox.set_model(model)
        # set the default value as active in the combo
        obox.set_active(active)
        obox.connect("changed", self.cite_changed)
        return obox

    def set_mediapath(self, *obj):
        if self.path_entry.get_text().strip():
            self.dbstate.db.set_mediapath(self.path_entry.get_text())
        else:
            self.dbstate.db.set_mediapath(None)

    def select_mediapath(self, *obj):
        """
        Show dialog to choose media directory.
        """
        f = Gtk.FileChooserDialog(
            title=_("Select media directory"),
            parent=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(
                _("_Cancel"),
                Gtk.ResponseType.CANCEL,
                _("_Apply"),
                Gtk.ResponseType.OK,
            ),
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
        config.set("database.path", path)

    def select_dbpath(self, *obj):
        """
        Show dialog to choose database directory.
        """
        f = Gtk.FileChooserDialog(
            title=_("Select database directory"),
            transient_for=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        f.add_buttons(
            _("_Cancel"), Gtk.ResponseType.CANCEL, _("_Apply"), Gtk.ResponseType.OK
        )
        dbpath = config.get("database.path")
        if not dbpath:
            dbpath = os.path.join(USER_DATA, "grampsdb")
        f.set_current_folder(os.path.dirname(dbpath))

        status = f.run()
        if status == Gtk.ResponseType.OK:
            val = f.get_filename()
            if val:
                self.dbpath_entry.set_text(val)
        f.destroy()

    def set_backup_path(self, *obj):
        path = self.backup_path_entry.get_text().strip()
        config.set("database.backup-path", path)

    def select_backup_path(self, *obj):
        """
        Show dialog to choose backup directory.
        """
        f = Gtk.FileChooserDialog(
            title=_("Select backup directory"),
            parent=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(
                _("_Cancel"),
                Gtk.ResponseType.CANCEL,
                _("_Apply"),
                Gtk.ResponseType.OK,
            ),
        )
        backup_path = config.get("database.backup-path")
        if not backup_path:
            backup_path = config.get("database.path")
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
            config.get("preferences.iprefix"),
            config.get("preferences.oprefix"),
            config.get("preferences.fprefix"),
            config.get("preferences.sprefix"),
            config.get("preferences.cprefix"),
            config.get("preferences.pprefix"),
            config.get("preferences.eprefix"),
            config.get("preferences.rprefix"),
            config.get("preferences.nprefix"),
        )

    def update_gendepth(self, obj, constant):
        """
        Called when the generation depth setting is changed.
        """
        intval = int(obj.get_value())
        config.set(constant, intval)
        # immediately use this value in displaystate.
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
        if intval < 0:
            intval = config.get(constant)
            ok = False
        if ok:
            config.set(constant, intval)
        else:
            obj.set_text(str(intval))

    def build_menu_names(self, obj):
        return (_("Preferences"), _("Preferences"))

    def add_symbols_panel(self, configdialog):
        self.grid = Gtk.Grid()
        self.grid.set_border_width(12)
        self.grid.set_column_spacing(6)
        self.grid.set_row_spacing(6)
        self.combo = None
        self.choosefont = None
        self.symbols_grid = self.create_grid()

        message = _(
            "If checked, use the standard genealogic symbols (death "
            "symbol is user selectable).\n"
            "If not checked, you can use the lower panel to customize "
            "the symbols yourself."
        )
        message += "\n\n"
        message += _(
            "This can be useful if you want to add phonetic in "
            "a note to show how to pronounce a name or if you mix"
            " multiple languages like greek and russian."
        )
        self.add_checkbox(
            self.grid,
            _("Use symbols"),
            0,
            "utf8.in-use",
            extra_callback=self.activate_change_font,
            tooltip=message,
        )
        symbols = Symbols()
        all_sbls = symbols.get_death_symbols()
        all_symbols = []
        for symbol in all_sbls:
            all_symbols.append(symbol[1] + " " + symbol[0])
        self.all_death_symbols = list(enumerate(all_symbols))
        self.combo = self.add_combo(
            self.grid,
            _("Select default death symbol"),
            4,
            "utf8.death-symbol",
            self.all_death_symbols,
            callback=self.utf8_update_death_symbol,
            valueactive=False,
        )
        self.utf8_show_example()
        self.show_default_symbols()

        return _("Genealogical Symbols"), self.grid

    def activate_change_font(self, obj=None):
        self.uistate.reload_symbols()
        self.show_default_symbols()
        self.uistate.emit("font-changed")

    def utf8_show_example(self):
        try:
            # remove the old messages with old font
            self.grid.remove_row(7)
            self.grid.remove_row(6)
            self.grid.remove_row(5)
        except:
            pass
        font = config.get("utf8.selected-font")
        symbols = Symbols()

        self.sym_buf = Gtk.TextBuffer()
        self.sym_text = Gtk.TextView.new_with_buffer(self.sym_buf)
        self.sym_text.set_has_tooltip(True)
        self.sym_text.props.halign = Gtk.Align.START
        self.sym_text.connect("query_tooltip", self.sym_tooltip)
        for tooltip, text, _tsym in symbols.all_symbols:
            text = " " + text + " "
            tag = self.sym_buf.create_tag(tag_name=tooltip, font=font, size_points=16.0)
            _iter = self.sym_buf.get_end_iter()
            self.sym_buf.insert_with_tags(_iter, text, tag)

        death_symbl = config.get("utf8.death-symbol")
        text = " " + symbols.get_death_symbol_for_char(death_symbl) + " "
        tooltip = _("Death:") + "\n" + symbols.get_death_symbol_name(death_symbl)
        tag = self.sym_buf.create_tag(tag_name=tooltip, font=font, size_points=14.0)
        _iter = self.sym_buf.get_end_iter()
        self.sym_buf.insert_with_tags(_iter, text, tag)
        self.sym_text.set_editable(False)
        self.grid.attach(self.sym_text, 1, 6, 8, 1)
        self.sym_text.show()
        self.show_default_symbols()

    def sym_tooltip(self, widget, w_x, w_y, key_mode, tooltip):
        """show a tooltip for each genealogic symbol"""
        if key_mode:
            offset = self.sym_buf.props.cursor_position
            iter_ = self.sym_buf.get_iter_at_offset(offset)
        else:
            # x. y are valid
            b_x, b_y = self.sym_text.window_to_buffer_coords(
                Gtk.TextWindowType.TEXT, w_x, w_y
            )
            iter_ = self.sym_text.get_iter_at_position(b_x, b_y)
            if isinstance(iter_, tuple):
                iter_ = iter_.iter
        tags = iter_.get_tags()
        if tags:
            tooltip.set_text(tags[0].props.name)
            return True  # if tooltip is to be shown
        return False

    def utf8_update_death_symbol(self, obj, constant):
        entry = obj.get_active()
        config.set(constant, entry)
        self.utf8_show_example()
        self.uistate.emit("font-changed")

    def symbol_value_change(self, obj, constant):
        entry = obj.get_text()
        config.set(constant, entry)
        idx = 0
        for symbol in self.symbols:
            if obj == self.symbols[symbol]:
                self.set_substitution_symbol(self.symbol_list[idx][1], entry)
            idx += 1

    def reset_substitution_symbol(self, *args):
        """reset the substitution symbol to the default"""
        self.set_substitution_symbol("utf8.birth-symbol", "*")
        self.set_substitution_symbol("utf8.baptism-symbol", "~")
        self.set_substitution_symbol("utf8.marriage-symbol", "oo")
        self.set_substitution_symbol("utf8.engaged-symbol", "o")
        self.set_substitution_symbol("utf8.divorce-symbol", "o|o")
        self.set_substitution_symbol("utf8.partner-symbol", "o-o")
        self.set_substitution_symbol("utf8.dead-symbol", "+")
        self.set_substitution_symbol("utf8.buried-symbol", "[]")
        self.set_substitution_symbol("utf8.cremated-symbol", "⚱")
        self.set_substitution_symbol("utf8.killed-symbol", "x")
        self.show_default_symbols()

    def show_default_symbols(self):
        # prepare scrolled window for symbols
        try:
            self.grid.remove_row(7)
            self.symbols_grid.remove_row(5)
            self.symbols_grid.remove_row(4)
            self.symbols_grid.remove_row(3)
            self.symbols_grid.remove_row(2)
            self.symbols_grid.remove_row(1)
            self.symbols_grid.remove_row(0)
        except:
            pass

        scroll_window = Gtk.ScrolledWindow()
        scroll_window.add(self.symbols_grid)
        scroll_window.set_vexpand(True)
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.grid.attach(scroll_window, 0, 7, 5, 1)
        if self.symbols_grid and self.uistate.symbols:
            self.symbols_grid.set_sensitive(False)
        else:
            self.symbols_grid.set_sensitive(True)
        self.symbol_list = [
            (_("Birth"), "utf8.birth-symbol", 1, 1),
            (_("Baptism"), "utf8.baptism-symbol", 1, 3),
            (_("Engaged"), "utf8.engaged-symbol", 2, 1),
            (_("Marriage"), "utf8.marriage-symbol", 2, 3),
            (_("Partner"), "utf8.partner-symbol", 3, 1),
            (_("Divorce"), "utf8.divorce-symbol", 3, 3),
            (_("Death"), "utf8.dead-symbol", 4, 1),
            (_("Killed"), "utf8.killed-symbol", 4, 3),
            (_("Buried"), "utf8.buried-symbol", 5, 1),
            (_("Cremated/Funeral urn"), "utf8.cremated-symbol", 5, 3),
        ]
        symbol_title = _("Default genealogy symbols replacement")

        symbol_label = Gtk.Label()
        symbol_label.set_halign(Gtk.Align.START)
        symbol_label.set_markup(_("<b>%s</b>") % symbol_title)
        self.symbols_grid.attach(symbol_label, 0, 0, 3, 1)

        symbol_reset = _("Restore to defaults")
        button = Gtk.Button(label=symbol_reset)
        button.connect("clicked", self.reset_substitution_symbol)
        self.symbols_grid.attach(button, 4, 0, 4, 1)

        symbol_tooltip = _(
            "You can set any text you want for this field."
            "\nYou can drag and drop a symbol from the symbol "
            "list above.\nIt will be visible only if your font "
            "contains this glyph."
        )

        # add symbols values to scrolled window
        self.symbols = {}
        for symbol in self.symbol_list:
            self.symbols[symbol[0]] = entry = self.add_entry(
                self.symbols_grid,
                symbol[0],
                symbol[2],
                symbol[1],
                self.symbol_value_change,
                col_attach=symbol[3],
            )
            entry.set_tooltip_text(symbol_tooltip)
            entry.set_max_width_chars(12)
            entry.set_width_chars(12)
            entry.set_halign(Gtk.Align.START)
        scroll_window.show_all()

    def set_substitution_symbol(self, symbol, value):
        """set the substitution symbol to string"""
        config.set(symbol, value)
        self.uistate.emit("font-changed")
