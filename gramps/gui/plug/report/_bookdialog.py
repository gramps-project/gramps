#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
# Copyright (C) 2007-2012  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012       Nick Hall
# Copyright (C) 2011-2016  Paul Franklin
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

""" GUI dialog for creating and managing books """

# Written by Alex Roitman,
# largely based on the BaseDoc classes by Don Allingham

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".Book")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from ...listmodel import ListModel
from gramps.gen.errors import FilterError, ReportError
from gramps.gen.const import URL_MANUAL_PAGE
from ...display import display_help
from ...pluginmanager import GuiPluginManager
from ...dialog import WarningDialog, ErrorDialog, QuestionDialog2
from gramps.gen.plug.menu import PersonOption, FamilyOption
from gramps.gen.plug.docgen import StyleSheet
from ...managedwindow import ManagedWindow, set_titles
from ...glade import Glade
from ...utils import is_right_click, open_file_with_default_application
from ...user import User
from .. import make_gui_option

# Import from specific modules in ReportBase
from gramps.gen.plug.report import BookList, Book, BookItem, append_styles
from gramps.gen.plug.report import CATEGORY_BOOK, book_categories
from gramps.gen.plug.report._options import ReportOptions
from ._reportdialog import ReportDialog
from ._docreportdialog import DocReportDialog

#------------------------------------------------------------------------
#
# Private Constants
#
#------------------------------------------------------------------------
_UNSUPPORTED = _("Unsupported")

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Reports_-_part_3"
WIKI_HELP_SEC = _('Books')
GENERATE_WIKI_HELP_SEC = _('Generate_Book_dialog')

#------------------------------------------------------------------------
#
# Private Functions
#
#------------------------------------------------------------------------
def _initialize_options(options, dbstate, uistate):
    """
    Validates all options by making sure that their values are consistent with
    the database.

    menu: The Menu class
    dbase: the database the options will be applied to
    """
    if not hasattr(options, "menu"):
        return
    dbase = dbstate.get_database()
    if dbase.get_total() == 0:
        return
    menu = options.menu

    for name in menu.get_all_option_names():
        option = menu.get_option_by_name(name)
        value = option.get_value()

        if isinstance(option, PersonOption):
            if not dbase.get_person_from_gramps_id(value):
                person_handle = uistate.get_active('Person')
                person = dbase.get_person_from_handle(person_handle)
                option.set_value(person.get_gramps_id())

        elif isinstance(option, FamilyOption):
            if not dbase.get_family_from_gramps_id(value):
                person_handle = uistate.get_active('Person')
                person = dbase.get_person_from_handle(person_handle)
                if person is None:
                    continue
                family_list = person.get_family_handle_list()
                if family_list:
                    family_handle = family_list[0]
                else:
                    try:
                        family_handle = next(dbase.iter_family_handles())
                    except StopIteration:
                        family_handle = None
                if family_handle:
                    family = dbase.get_family_from_handle(family_handle)
                    option.set_value(family.get_gramps_id())
                else:
                    print("No family specified for ", name)

#------------------------------------------------------------------------
#
# BookListDisplay class
#
#------------------------------------------------------------------------
class BookListDisplay:
    """
    Interface into a dialog with the list of available books.

    Allows the user to select and/or delete a book from the list.
    """

    def __init__(self, booklist, nodelete=False, dosave=False, parent=None):
        """
        Create a BookListDisplay object that displays the books in BookList.

        booklist:   books that are displayed -- a :class:`.BookList` instance
        nodelete:   if True then the Delete button is hidden
        dosave:     if True then the book list is flagged to be saved if needed
        """

        self.booklist = booklist
        self.dosave = dosave
        self.xml = Glade('book.glade', toplevel='book')
        self.top = self.xml.toplevel
        self.unsaved_changes = False

        set_titles(self.top, self.xml.get_object('title2'),
                   _('Available Books'))

        if nodelete:
            delete_button = self.xml.get_object("delete_button")
            delete_button.hide()
        self.xml.connect_signals({
            "on_booklist_cancel_clicked" : self.on_booklist_cancel_clicked,
            "on_booklist_ok_clicked"     : self.on_booklist_ok_clicked,
            "on_booklist_delete_clicked" : self.on_booklist_delete_clicked,
            "on_book_ok_clicked"         : self.do_nothing,
            "on_book_help_clicked"       : self.do_nothing,
            "destroy_passed_object"      : self.do_nothing,
            "on_setup_clicked"           : self.do_nothing,
            "on_down_clicked"            : self.do_nothing,
            "on_up_clicked"              : self.do_nothing,
            "on_remove_clicked"          : self.do_nothing,
            "on_add_clicked"             : self.do_nothing,
            "on_edit_clicked"            : self.do_nothing,
            "on_open_clicked"            : self.do_nothing,
            "on_save_clicked"            : self.do_nothing,
            "on_clear_clicked"           : self.do_nothing
            })
        self.guilistbooks = self.xml.get_object('list')
        self.guilistbooks.connect('button-press-event', self.on_button_press)
        self.guilistbooks.connect('key-press-event', self.on_key_pressed)
        self.blist = ListModel(self.guilistbooks, [('Name', -1, 10)],)

        self.redraw()
        self.selection = None
        self.top.set_transient_for(parent)
        self.top.run()

    def redraw(self):
        """Redraws the list of currently available books"""

        self.blist.model.clear()
        names = self.booklist.get_book_names()
        if not len(names):
            return
        for name in names:
            the_iter = self.blist.add([name])
        if the_iter:
            self.blist.selection.select_iter(the_iter)

    def on_booklist_ok_clicked(self, obj):
        """
        Return selected book.
        Also marks the current list to be saved into the xml file, if needed.
        """
        store, the_iter = self.blist.get_selected()
        if the_iter:
            data = self.blist.get_data(the_iter, [0])
            self.selection = self.booklist.get_book(str(data[0]))
        if self.dosave and self.unsaved_changes:
            self.booklist.set_needs_saving(True)

    def on_booklist_delete_clicked(self, obj):
        """
        Deletes selected book from the list.

        This change is not final. OK button has to be clicked to save the list.
        """
        store, the_iter = self.blist.get_selected()
        if not the_iter:
            return
        data = self.blist.get_data(the_iter, [0])
        self.booklist.delete_book(str(data[0]))
        self.blist.remove(the_iter)
        self.unsaved_changes = True
        self.top.run()

    def on_booklist_cancel_clicked(self, *obj):
        """ cancel the booklist dialog """
        if self.unsaved_changes:
            qqq = QuestionDialog2(
                _('Discard Unsaved Changes'),
                _('You have made changes which have not been saved.'),
                _('Proceed'),
                _('Cancel'),
                parent=self.top)
            if not qqq.run():
                self.top.run()

    def on_button_press(self, obj, event):
        """
        Checks for a double click event. In the list, we want to
        treat a double click as if it was OK button press.
        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            store, the_iter = self.blist.get_selected()
            if not the_iter:
                return False
            self.on_booklist_ok_clicked(obj)
            #emit OK response on dialog to close it automatically
            self.top.response(-5)
            return True
        return False

    def on_key_pressed(self, obj, event):
        """
        Handles the return key being pressed on list. If the key is pressed,
        the Edit button handler is called
        """
        if event.type == Gdk.EventType.KEY_PRESS:
            if  event.keyval in (_RETURN, _KP_ENTER):
                self.on_booklist_ok_clicked(obj)
                #emit OK response on dialog to close it automatically
                self.top.response(-5)
                return True
        return False

    def do_nothing(self, obj):
        """ do nothing """
        pass

#------------------------------------------------------------------------
#
# Book Options
#
#------------------------------------------------------------------------
class BookOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        ReportOptions.__init__(self, name, dbase)

        # Options specific for this report
        self.options_dict = {
            'bookname'    : '',
        }
        # TODO since the CLI code for the "book" generates its own "help" now,
        # the GUI code would be faster if it didn't list all the possible books
        self.options_help = {
            'bookname'    : ("=name", _("Name of the book. MANDATORY"),
                             BookList('books.xml', dbase).get_book_names(),
                             False),
        }

#-------------------------------------------------------------------------
#
# Book creation dialog
#
#-------------------------------------------------------------------------
class BookSelector(ManagedWindow):
    """
    Interface into a dialog setting up the book.

    Allows the user to add/remove/reorder/setup items for the current book
    and to clear/load/save/edit whole books.
    """

    def __init__(self, dbstate, uistate):
        self._db = dbstate.db
        self.dbstate = dbstate
        self.uistate = uistate
        self.title = _('Manage Books')
        self.file = "books.xml"

        ManagedWindow.__init__(self, uistate, [], self.__class__)

        self.xml = Glade('book.glade', toplevel="top")
        window = self.xml.toplevel

        title_label = self.xml.get_object('title')
        self.set_window(window, title_label, self.title)
        self.setup_configs('interface.bookselector', 700, 600)
        self.show()
        self.xml.connect_signals({
            "on_add_clicked"        : self.on_add_clicked,
            "on_remove_clicked"     : self.on_remove_clicked,
            "on_up_clicked"         : self.on_up_clicked,
            "on_down_clicked"       : self.on_down_clicked,
            "on_setup_clicked"      : self.on_setup_clicked,
            "on_clear_clicked"      : self.on_clear_clicked,
            "on_save_clicked"       : self.on_save_clicked,
            "on_open_clicked"       : self.on_open_clicked,
            "on_edit_clicked"       : self.on_edit_clicked,
            "on_book_help_clicked"  : lambda x: display_help(WIKI_HELP_PAGE,
                                                             WIKI_HELP_SEC),
            "on_book_ok_clicked"    : self.on_book_ok_clicked,
            "destroy_passed_object" : self.on_close_clicked,

            # Insert dummy handlers for second top level in the glade file
            "on_booklist_ok_clicked"     : lambda _: None,
            "on_booklist_delete_clicked" : lambda _: None,
            "on_booklist_cancel_clicked" : lambda _: None,
            "on_booklist_ok_clicked"     : lambda _: None,
            "on_booklist_ok_clicked"     : lambda _: None,
            })

        self.avail_tree = self.xml.get_object("avail_tree")
        self.book_tree = self.xml.get_object("book_tree")
        self.avail_tree.connect('button-press-event', self.avail_button_press)
        self.book_tree.connect('button-press-event', self.book_button_press)

        self.name_entry = self.xml.get_object("name_entry")
        self.name_entry.set_text(_('New Book'))

        avail_label = self.xml.get_object('avail_label')
        avail_label.set_text("<b>%s</b>" % _("_Available items"))
        avail_label.set_use_markup(True)
        avail_label.set_use_underline(True)
        book_label = self.xml.get_object('book_label')
        book_label.set_text("<b>%s</b>" % _("Current _book"))
        book_label.set_use_underline(True)
        book_label.set_use_markup(True)

        avail_titles = [(_('Name'), 0, 230),
                        (_('Type'), 1, 80),
                        ('', -1, 0)]

        book_titles = [(_('Item name'), -1, 230),
                       (_('Type'), -1, 80),
                       ('', -1, 0),
                       (_('Subject'), -1, 50)]

        self.avail_nr_cols = len(avail_titles)
        self.book_nr_cols = len(book_titles)

        self.avail_model = ListModel(self.avail_tree, avail_titles)
        self.book_model = ListModel(self.book_tree, book_titles)
        self.draw_avail_list()

        self.book = Book()
        self.book_list = BookList(self.file, self._db)
        self.book_list.set_needs_saving(False) # just read in: no need to save

    def build_menu_names(self, obj):
        return (_("Book selection list"), self.title)

    def draw_avail_list(self):
        """
        Draw the list with the selections available for the book.

        The selections are read from the book item registry.
        """
        pmgr = GuiPluginManager.get_instance()
        regbi = pmgr.get_reg_bookitems()
        if not regbi:
            return

        available_reports = []
        for pdata in regbi:
            category = _UNSUPPORTED
            if pdata.supported and pdata.category in book_categories:
                category = book_categories[pdata.category]
            available_reports.append([pdata.name, category, pdata.id])
        for data in sorted(available_reports):
            new_iter = self.avail_model.add(data)

        self.avail_model.connect_model()

        if new_iter:
            self.avail_model.selection.select_iter(new_iter)
            path = self.avail_model.model.get_path(new_iter)
            col = self.avail_tree.get_column(0)
            self.avail_tree.scroll_to_cell(path, col, 1, 1, 0.0)

    def open_book(self, book):
        """
        Open the book: set the current set of selections to this book's items.

        book:   the book object to load.
        """
        if book.get_paper_name():
            self.book.set_paper_name(book.get_paper_name())
        if book.get_orientation() is not None: # 0 is legal
            self.book.set_orientation(book.get_orientation())
        if book.get_paper_metric() is not None: # 0 is legal
            self.book.set_paper_metric(book.get_paper_metric())
        if book.get_custom_paper_size():
            self.book.set_custom_paper_size(book.get_custom_paper_size())
        if book.get_margins():
            self.book.set_margins(book.get_margins())
        if book.get_format_name():
            self.book.set_format_name(book.get_format_name())
        if book.get_output():
            self.book.set_output(book.get_output())
        if book.get_dbname() != self._db.get_save_path():
            WarningDialog(
                _('Different database'),
                _('This book was created with the references to database '
                  '%s.\n\n This makes references to the central person '
                  'saved in the book invalid.\n\n'
                  'Therefore, the central person for each item is being set '
                  'to the active person of the currently opened database.'
                 ) % book.get_dbname(),
                parent=self.window)

        self.book.clear()
        self.book_model.clear()
        for saved_item in book.get_item_list():
            name = saved_item.get_name()
            item = BookItem(self._db, name)

            # The option values were loaded magically by the book parser.
            # But they still need to be applied to the menu options.
            opt_dict = item.option_class.handler.options_dict
            orig_opt_dict = saved_item.option_class.handler.options_dict
            menu = item.option_class.menu
            for optname in opt_dict:
                opt_dict[optname] = orig_opt_dict[optname]
                menu_option = menu.get_option_by_name(optname)
                if menu_option:
                    menu_option.set_value(opt_dict[optname])

            _initialize_options(item.option_class, self.dbstate, self.uistate)
            item.set_style_name(saved_item.get_style_name())
            self.book.append_item(item)

            data = [item.get_translated_name(),
                    item.get_category(), item.get_name()]

            data[2] = item.option_class.get_subject()
            self.book_model.add(data)

    def on_add_clicked(self, obj):
        """
        Add an item to the current selections.

        Use the selected available item to get the item's name in the registry.
        """
        store, the_iter = self.avail_model.get_selected()
        if not the_iter:
            return
        data = self.avail_model.get_data(the_iter,
                                         list(range(self.avail_nr_cols)))
        item = BookItem(self._db, data[2])
        _initialize_options(item.option_class, self.dbstate, self.uistate)
        data[2] = item.option_class.get_subject()
        self.book_model.add(data)
        self.book.append_item(item)

    def on_remove_clicked(self, obj):
        """
        Remove the item from the current list of selections.
        """
        store, the_iter = self.book_model.get_selected()
        if not the_iter:
            return
        row = self.book_model.get_selected_row()
        self.book.pop_item(row)
        self.book_model.remove(the_iter)

    def on_clear_clicked(self, obj):
        """
        Clear the whole current book.
        """
        self.book_model.clear()
        self.book.clear()

    def on_up_clicked(self, obj):
        """
        Move the currently selected item one row up in the selection list.
        """
        row = self.book_model.get_selected_row()
        if not row or row == -1:
            return
        store, the_iter = self.book_model.get_selected()
        data = self.book_model.get_data(the_iter,
                                        list(range(self.book_nr_cols)))
        self.book_model.remove(the_iter)
        self.book_model.insert(row-1, data, None, 1)
        item = self.book.pop_item(row)
        self.book.insert_item(row-1, item)

    def on_down_clicked(self, obj):
        """
        Move the currently selected item one row down in the selection list.
        """
        row = self.book_model.get_selected_row()
        if row + 1 >= self.book_model.count or row == -1:
            return
        store, the_iter = self.book_model.get_selected()
        data = self.book_model.get_data(the_iter,
                                        list(range(self.book_nr_cols)))
        self.book_model.remove(the_iter)
        self.book_model.insert(row+1, data, None, 1)
        item = self.book.pop_item(row)
        self.book.insert_item(row+1, item)

    def on_setup_clicked(self, obj):
        """
        Configure currently selected item.
        """
        store, the_iter = self.book_model.get_selected()
        if not the_iter:
            WarningDialog(_('No selected book item'),
                          _('Please select a book item to configure.'),
                          parent=self.window)
            return
        row = self.book_model.get_selected_row()
        item = self.book.get_item(row)
        option_class = item.option_class
        option_class.handler.set_default_stylesheet_name(item.get_style_name())
        item.is_from_saved_book = bool(self.book.get_name())
        item_dialog = BookItemDialog(self.dbstate, self.uistate,
                                     item, self.track)

        while True:
            response = item_dialog.window.run()
            if response == Gtk.ResponseType.OK:
                # dialog will be closed by connect, now continue work while
                # rest of dialog is unresponsive, release when finished
                style = option_class.handler.get_default_stylesheet_name()
                item.set_style_name(style)
                subject = option_class.get_subject()
                self.book_model.model.set_value(the_iter, 2, subject)
                self.book.set_item(row, item)
                item_dialog.close()
                break
            elif response == Gtk.ResponseType.CANCEL:
                item_dialog.close()
                break
            elif response == Gtk.ResponseType.DELETE_EVENT:
                #just stop, in ManagedWindow, delete-event is already coupled to
                #correct action.
                break
        opt_dict = option_class.handler.options_dict
        for optname in opt_dict:
            menu_option = option_class.menu.get_option_by_name(optname)
            if menu_option:
                menu_option.set_value(opt_dict[optname])

    def book_button_press(self, obj, event):
        """
        Double-click on the current book selection is the same as setup.
        Right click evokes the context menu.
        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            self.on_setup_clicked(obj)
        elif is_right_click(event):
            self.build_book_context_menu(event)

    def avail_button_press(self, obj, event):
        """
        Double-click on the available selection is the same as add.
        Right click evokes the context menu.
        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            self.on_add_clicked(obj)
        elif is_right_click(event):
            self.build_avail_context_menu(event)

    def build_book_context_menu(self, event):
        """Builds the menu with item-centered and book-centered options."""

        store, the_iter = self.book_model.get_selected()
        if the_iter:
            sensitivity = 1
        else:
            sensitivity = 0
        entries = [
            (_('_Up'), self.on_up_clicked, sensitivity),
            (_('_Down'), self.on_down_clicked, sensitivity),
            (_("Setup"), self.on_setup_clicked, sensitivity),
            (_('_Remove'), self.on_remove_clicked, sensitivity),
            ('', None, 0),
            (_('Clear the book'), self.on_clear_clicked, 1),
            (_('_Save'), self.on_save_clicked, 1),
            (_('_Open'), self.on_open_clicked, 1),
            (_("_Edit"), self.on_edit_clicked, 1),
        ]

        self.menu1 = Gtk.Menu() # TODO could this be just a local "menu ="?
        self.menu1.set_reserve_toggle_size(False)
        for title, callback, sensitivity in entries:
            item = Gtk.MenuItem.new_with_mnemonic(title)
            Gtk.Label.new_with_mnemonic
            if callback:
                item.connect("activate", callback)
            else:
                item = Gtk.SeparatorMenuItem()
            item.set_sensitive(sensitivity)
            item.show()
            self.menu1.append(item)
        self.menu1.popup(None, None, None, None, event.button, event.time)

    def build_avail_context_menu(self, event):
        """Builds the menu with the single Add option."""

        store, the_iter = self.avail_model.get_selected()
        if the_iter:
            sensitivity = 1
        else:
            sensitivity = 0
        entries = [
            (_('_Add'), self.on_add_clicked, sensitivity),
        ]

        self.menu2 = Gtk.Menu() # TODO could this be just a local "menu ="?
        self.menu2.set_reserve_toggle_size(False)
        for title, callback, sensitivity in entries:
            item = Gtk.MenuItem.new_with_mnemonic(title)
            if callback:
                item.connect("activate", callback)
            item.set_sensitive(sensitivity)
            item.show()
            self.menu2.append(item)
        self.menu2.popup(None, None, None, None, event.button, event.time)

    def on_close_clicked(self, obj):
        """
        close the BookSelector dialog, saving any changes if needed
        """
        if self.book_list.get_needs_saving():
            self.book_list.save()
        ManagedWindow.close(self, *obj)

    def on_book_ok_clicked(self, obj):
        """
        Run final BookDialog with the current book.
        """
        if self.book.get_item_list():
            old_paper_name = self.book.get_paper_name() # from books.xml
            old_orientation = self.book.get_orientation()
            old_paper_metric = self.book.get_paper_metric()
            old_custom_paper_size = self.book.get_custom_paper_size()
            old_margins = self.book.get_margins()
            old_format_name = self.book.get_format_name()
            old_output = self.book.get_output()
            BookDialog(self.dbstate, self.uistate, self.book, BookOptions, track=self.track)
            new_paper_name = self.book.get_paper_name()
            new_orientation = self.book.get_orientation()
            new_paper_metric = self.book.get_paper_metric()
            new_custom_paper_size = self.book.get_custom_paper_size()
            new_margins = self.book.get_margins()
            new_format_name = self.book.get_format_name()
            new_output = self.book.get_output()
            # only books in the booklist have a name (not "ad hoc" ones)
            if (self.book.get_name() and
                    (old_paper_name != new_paper_name or
                     old_orientation != new_orientation or
                     old_paper_metric != new_paper_metric or
                     old_custom_paper_size != new_custom_paper_size or
                     old_margins != new_margins or
                     old_format_name != new_format_name or
                     old_output != new_output)):
                self.book.set_dbname(self._db.get_save_path())
                self.book_list.set_book(self.book.get_name(), self.book)
                self.book_list.set_needs_saving(True)
            if self.book_list.get_needs_saving():
                self.book_list.save()
        else:
            WarningDialog(_('No items'),
                          _('This book has no items.'),
                          parent=self.window)
            return
        self.close()

    def on_save_clicked(self, obj):
        """
        Save the current book in the xml booklist file.
        """
        if not self.book.get_item_list():
            WarningDialog(_('No items'),
                          _('This book has no items.'),
                          parent=self.window)
            return
        name = str(self.name_entry.get_text())
        if not name:
            WarningDialog(
                _('No book name'),
                _('You are about to save away a book with no name.\n\n'
                  'Please give it a name before saving it away.'),
                parent=self.window)
            return
        if name in self.book_list.get_book_names():
            qqq = QuestionDialog2(
                _('Book name already exists'),
                _('You are about to save away a '
                  'book with a name which already exists.'),
                _('Proceed'),
                _('Cancel'),
                parent=self.window)
            if not qqq.run():
                return

        # previously, the same book could be added to the booklist
        # under multiple names, which became different books once the
        # booklist was saved into a file so everything was fine, but
        # this created a problem once the paper settings were added
        # to the Book object in the BookDialog, since those settings
        # were retrieved from the Book object in BookList.save, so mutiple
        # books (differentiated by their names) were assigned the
        # same paper values, so the solution is to make each Book be
        # unique in the booklist, so if multiple copies are saved away
        # only the last one will get the paper values assigned to it
        # (although when the earlier books are then eventually run,
        # they'll be assigned paper values also)
        self.book.set_name(name)
        self.book.set_dbname(self._db.get_save_path())
        self.book_list.set_book(name, self.book)
        self.book_list.set_needs_saving(True) # user clicked on save
        self.book = Book(self.book, exact_copy=False) # regenerate old items
        self.book.set_name(name)
        self.book.set_dbname(self._db.get_save_path())

    def on_open_clicked(self, obj):
        """
        Run the BookListDisplay dialog to present the choice of books to open.
        """
        booklistdisplay = BookListDisplay(self.book_list, nodelete=True,
                                          dosave=False, parent=self.window)
        booklistdisplay.top.destroy()
        book = booklistdisplay.selection
        if book:
            self.open_book(book)
            self.name_entry.set_text(book.get_name())
            self.book.set_name(book.get_name())

    def on_edit_clicked(self, obj):
        """
        Run the BookListDisplay dialog to present the choice of books to delete.
        """
        booklistdisplay = BookListDisplay(self.book_list, nodelete=False,
                                          dosave=True, parent=self.window)
        booklistdisplay.top.destroy()
        book = booklistdisplay.selection
        if book:
            self.open_book(book)
            self.name_entry.set_text(book.get_name())
            self.book.set_name(book.get_name())

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class BookItemDialog(ReportDialog):

    """
    This class overrides the interface methods common for different reports
    in a way specific for this report. This is a book item dialog.
    """

    def __init__(self, dbstate, uistate, item, track=[]):
        option_class = item.option_class
        name = item.get_name()
        translated_name = item.get_translated_name()
        self.category = CATEGORY_BOOK
        self.database = dbstate.db
        self.option_class = option_class
        self.is_from_saved_book = item.is_from_saved_book
        ReportDialog.__init__(self, dbstate, uistate,
                              option_class, name, translated_name, track)

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_user_options()

        self.options.handler.save_options()

    def setup_target_frame(self):
        """Target frame is not used."""
        pass

    def parse_target_frame(self):
        """Target frame is not used."""
        return 1

    def init_options(self, option_class):
        try:
            if issubclass(option_class, object):
                self.options = option_class(self.raw_name, self.database)
        except TypeError:
            self.options = option_class
        if not self.is_from_saved_book:
            self.options.load_previous_values()

    def add_user_options(self):
        """
        Generic method to add user options to the gui.
        """
        if not hasattr(self.options, "menu"):
            return
        menu = self.options.menu
        options_dict = self.options.options_dict
        for category in menu.get_categories():
            for name in menu.get_option_names(category):
                option = menu.get_option(category, name)

                # override option default with xml-saved value:
                if name in options_dict:
                    option.set_value(options_dict[name])

                widget, label = make_gui_option(option, self.dbstate,
                                                self.uistate, self.track,
                                                self.is_from_saved_book)
                if widget is not None:
                    if label:
                        self.add_frame_option(category,
                                              option.get_label(),
                                              widget)
                    else:
                        self.add_frame_option(category, "", widget)

#-------------------------------------------------------------------------
#
# _BookFormatComboBox
#
#-------------------------------------------------------------------------
class _BookFormatComboBox(Gtk.ComboBox):
    """
    Build a menu of report types that are appropriate for a book
    """

    def __init__(self, active):

        Gtk.ComboBox.__init__(self)

        pmgr = GuiPluginManager.get_instance()
        self.__bookdoc_plugins = []
        for plugin in pmgr.get_docgen_plugins():
            if plugin.get_text_support() and plugin.get_draw_support():
                self.__bookdoc_plugins.append(plugin)

        self.store = Gtk.ListStore(GObject.TYPE_STRING)
        self.set_model(self.store)
        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        index = 0
        active_index = 0
        for plugin in self.__bookdoc_plugins:
            name = plugin.get_name()
            self.store.append(row=[name])
            if plugin.get_extension() == active:
                active_index = index
            index += 1
        self.set_active(active_index)

    def get_active_plugin(self):
        """
        Get the plugin represented by the currently active selection.
        """
        return self.__bookdoc_plugins[self.get_active()]

#------------------------------------------------------------------------
#
# The final dialog - paper, format, target, etc.
#
#------------------------------------------------------------------------
class BookDialog(DocReportDialog):
    """
    A usual Report.Dialog subclass.

    Create a dialog selecting target, format, and paper/HTML options.
    """

    def __init__(self, dbstate, uistate, book, options, track=[]):
        self.format_menu = None
        self.options = options
        self.page_html_added = False
        self.book = book
        self.title = _('Generate Book')
        self.database = dbstate.db
        DocReportDialog.__init__(self, dbstate, uistate, options,
                                 'book', self.title, track=track)
        self.options.options_dict['bookname'] = self.book.get_name()

        while True:
            response = self.window.run()
            if response != Gtk.ResponseType.HELP:
                break
        if response == Gtk.ResponseType.OK:
            handler = self.options.handler
            if self.book.get_paper_name() != handler.get_paper_name():
                self.book.set_paper_name(handler.get_paper_name())
            if self.book.get_orientation() != handler.get_orientation():
                self.book.set_orientation(handler.get_orientation())
            if self.book.get_paper_metric() != handler.get_paper_metric():
                self.book.set_paper_metric(handler.get_paper_metric())
            if (self.book.get_custom_paper_size() !=
                    handler.get_custom_paper_size()):
                self.book.set_custom_paper_size(handler.get_custom_paper_size())
            if self.book.get_margins() != handler.get_margins():
                self.book.set_margins(handler.get_margins())
            if self.book.get_format_name() != handler.get_format_name():
                self.book.set_format_name(handler.get_format_name())
            if self.book.get_output() != self.options.get_output():
                self.book.set_output(self.options.get_output())
            try:
                self.make_book()
            except (IOError, OSError) as msg:
                ErrorDialog(str(msg), parent=self.window)
        if response != Gtk.ResponseType.DELETE_EVENT:  # already closed
            self.close()

    def setup_style_frame(self):
        pass
    def setup_other_frames(self):
        pass
    def parse_style_frame(self):
        pass

    def get_title(self):
        """ get the title """
        return self.title

    def get_header(self, name):
        """ get the header """
        return _("Gramps Book")

    def make_doc_menu(self, active=None):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        self.format_menu = _BookFormatComboBox(active)

    def on_help_clicked(self, *obj):
        display_help(WIKI_HELP_PAGE, GENERATE_WIKI_HELP_SEC)

    def make_document(self):
        """Create a document of the type requested by the user."""
        user = User(uistate=self.uistate)
        self.rptlist = []
        selected_style = StyleSheet()

        pstyle = self.paper_frame.get_paper_style()
        self.doc = self.format(None, pstyle)

        for item in self.book.get_item_list():
            item.option_class.set_document(self.doc)
            report_class = item.get_write_item()
            obj = (write_book_item(self.database, report_class,
                                   item.option_class, user),
                   item.get_translated_name())
            self.rptlist.append(obj)
            append_styles(selected_style, item)

        self.doc.set_style_sheet(selected_style)
        self.doc.open(self.target_path)

    def make_book(self):
        """
        The actual book. Start it out, then go through the item list
        and call each item's write_book_item method (which were loaded
        by the previous make_document method).
        """

        try:
            self.doc.init()
            newpage = 0
            for (rpt, name) in self.rptlist:
                if newpage:
                    self.doc.page_break()
                newpage = 1
                if rpt:
                    rpt.begin_report()
                    rpt.write_report()
            self.doc.close()
        except ReportError as msg:
            (msg1, msg2) = msg.messages()
            msg2 += ' (%s)' % name # which report has the error?
            ErrorDialog(msg1, msg2, parent=self.uistate.window)
            return
        except FilterError as msg:
            (msg1, msg2) = msg.messages()
            ErrorDialog(msg1, msg2, parent=self.uistate.window)
            return

        if self.open_with_app.get_active():
            open_file_with_default_application(self.target_path, self.uistate)

    def init_options(self, option_class):
        try:
            if issubclass(option_class, object):
                self.options = option_class(self.raw_name, self.database)
        except TypeError:
            self.options = option_class
        self.options.load_previous_values()
        handler = self.options.handler
        if self.book.get_paper_name():
            handler.set_paper_name(self.book.get_paper_name())
        if self.book.get_orientation() is not None: # 0 is legal
            handler.set_orientation(self.book.get_orientation())
        if self.book.get_paper_metric() is not None: # 0 is legal
            handler.set_paper_metric(self.book.get_paper_metric())
        if self.book.get_custom_paper_size():
            handler.set_custom_paper_size(self.book.get_custom_paper_size())
        if self.book.get_margins():
            handler.set_margins(self.book.get_margins())
        if self.book.get_format_name():
            handler.set_format_name(self.book.get_format_name())
        if self.book.get_output():
            self.options.set_output(self.book.get_output())

#------------------------------------------------------------------------
#
# Generic task function for book
#
#------------------------------------------------------------------------
def write_book_item(database, report_class, options, user):
    """
    Write the report using options set.
    All user dialog has already been handled and the output file opened.
    """
    try:
        return report_class(database, options, user)
    except ReportError as msg:
        (msg1, msg2) = msg.messages()
        ErrorDialog(msg1, msg2, parent=user.uistate.window)
    except FilterError as msg:
        (msg1, msg2) = msg.messages()
        ErrorDialog(msg1, msg2, parent=user.uistate.window)
    except:
        LOG.error("Failed to write book item.", exc_info=True)
    return None
