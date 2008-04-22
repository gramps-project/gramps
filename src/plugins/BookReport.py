#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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

# Written by Alex Roitman, 
# largely based on the BaseDoc classes by Don Allingham

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".BookReport")

#-------------------------------------------------------------------------
#
# SAX interface
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser, handler, SAXParseException
    from xml.sax.saxutils import escape
except:
    from _xmlplus.sax import make_parser, handler, SAXParseException
    from _xmlplus.sax.saxutils import escape

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from gtk import glade
from gtk import RESPONSE_OK

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import ListModel
import Errors
import BaseDoc
from QuestionDialog import WarningDialog, ErrorDialog
from PluginUtils import bkitems_list, register_report, Plugins
from PluginUtils import PersonOption, FilterOption, FamilyOption
import ManagedWindow

# Import from specific modules in ReportBase
from ReportBase._Constants import CATEGORY_BOOK, MODE_GUI, MODE_CLI
from ReportBase._BookFormatComboBox import BookFormatComboBox
from ReportBase._ReportDialog import ReportDialog
from ReportBase._DocReportDialog import DocReportDialog
from ReportBase._CommandLineReport import CommandLineReport
from ReportBase._ReportOptions import ReportOptions

from BasicUtils import name_displayer as _nd

#------------------------------------------------------------------------
#
# Private Functions
#
#------------------------------------------------------------------------
def _initialize_options(options, dbstate):
    """
    Validates all options by making sure that their values are consistent with
    the database.
    
    menu: The Menu class
    dbase: the database the options will be applied to
    """
    dbase = dbstate.get_database()
    if not hasattr(options, "menu"):
        return
    menu = options.menu
    
    for name in menu.get_all_option_names():
        option = menu.get_option_by_name(name)

        if isinstance(option, PersonOption):
            person = dbstate.get_active_person()
            option.set_value(person.get_gramps_id())
        
        elif isinstance(option, FamilyOption):
            person = dbstate.get_active_person()
            family_list = person.get_family_handle_list()
            if family_list:
                family_handle = family_list[0]
            else:
                family_handle = dbase.get_family_handles()[0]
            family = dbase.get_family_from_handle(family_handle)
            option.set_value(family.get_gramps_id())

def _get_subject(options, dbase):
    """
    Attempts to determine the subject of a set of options. The subject would
    likely be a person (using a PersonOption) or a filter (using a 
    FilterOption)
    
    options: The ReportOptions class
    dbase: the database for which it corresponds
    """
    if not hasattr(options, "menu"):
        return _("Not Applicable")
    menu = options.menu
    
    option_names = menu.get_all_option_names()

    for name in option_names:
        option = menu.get_option_by_name(name)
        
        if isinstance(option, FilterOption):
            return option.get_filter().get_name()
        
        elif isinstance(option, PersonOption):
            gid = option.get_value()
            person = dbase.get_person_from_gramps_id(gid)
            return _nd.display(person)
        
        elif isinstance(option, FamilyOption):
            family = dbase.get_family_from_gramps_id(option.get_value())
            family_id = family.get_gramps_id()
            fhandle = family.get_father_handle()
            mhandle = family.get_mother_handle()
            
            if fhandle:
                father = dbase.get_person_from_handle(fhandle)
                father_name = _nd.display(father)
            else:
                father_name = _("unknown father")
                
            if mhandle:
                mother = dbase.get_person_from_handle(mhandle)
                mother_name = _nd.display(mother)
            else:
                mother_name = _("unknown mother")
                
            name = _("%s and %s (%s)") % (father_name, mother_name, family_id)
            return name
        
    return _("Not Applicable")

#------------------------------------------------------------------------
#
# Book Item class
#
#------------------------------------------------------------------------
class BookItem:
    """
    Interface into the book item -- a smallest element of the book.
    """

    def __init__(self, dbase, name):
        """
        Create a new empty BookItem.
        
        name:   the book item is retreived 
                from the book item registry using name for lookup
        """
        self.dbase = dbase
        self.style_name = "default"
        for item in bkitems_list:
            if item[4] == name:
                self.translated_name = item[0]
                if item[5]:
                    self.category = Plugins.UNSUPPORTED
                else:
                    self.category = item[1]
                self.write_item = item[2]
                self.name = item[4]
                self.option_class = item[3](self.name, self.dbase)
                self.option_class.load_previous_values()

    def get_name(self):
        """
        Return the name of the item.
        """
        return self.name

    def get_translated_name(self):
        """
        Return the translated name of the item.
        """
        return self.translated_name

    def get_category(self):
        """
        Return the category of the item.
        """
        return self.category

    def get_write_item(self):
        """
        Return the report-writing function of the item.
        """
        return self.write_item

    def set_style_name(self, style_name):
        """
        Set the style name for the item.
        
        style_name: name of the style to set.
        """
        self.style_name = style_name

    def get_style_name(self):
        """
        Return the style name of the item.
        """
        return self.style_name

#------------------------------------------------------------------------
#
# Book class
#
#------------------------------------------------------------------------
class Book:
    """
    Interface into the user-defined book -- a collection of book items.
    """

    def __init__(self, obj=None):
        """
        Create a new empty Book.

        obj:    if not None, creates the Book from the values in
                obj, instead of creating an empty Book.
        """

        self.name = ""
        self.dbname = ""
        if obj:
            self.item_list = obj.item_list
        else:
            self.item_list = []
        
    def set_name(self, name):
        """
        Set the name of the book.
        
        name:   the name to set.
        """
        self.name = name

    def get_name(self):
        """
        Return the name of the book.
        """
        return self.name

    def get_dbname(self):
        """
        Return the name of the database file used for the book.
        """
        return self.dbname

    def set_dbname(self, name):
        """
        Set the name of the database file used for the book.

        name:   a filename to set.
        """
        self.dbname = name

    def clear(self):
        """
        Clears the contents of the book.
        """
        self.item_list = []

    def append_item(self, item):
        """
        Add an item to the book.
        
        item:   an item to append.
        """
        self.item_list.append(item)

    def insert_item(self, index, item):
        """
        Inserts an item into the given position in the book.
        
        index:  a position index. 
        item:   an item to append.
        """
        self.item_list.insert(index, item)

    def pop_item(self, index):
        """
        Pop an item from given position in the book.
        
        index:  a position index. 
        """
        return self.item_list.pop(index)

    def get_item(self, index):
        """
        Return an item at a given position in the book.
        
        index:  a position index. 
        """
        return self.item_list[index]

    def set_item(self, index, item):
        """
        Set an item at a given position in the book.
        
        index:  a position index. 
        item:   an item to set.
        """
        self.item_list[index] = item

    def get_item_list(self):
        """
        Return list of items in the current book.
        """
        return self.item_list

#------------------------------------------------------------------------
#
# BookList class
#
#------------------------------------------------------------------------
class BookList:
    """
    Interface into the user-defined list of books.  

    BookList is loaded from a specified XML file if it exists.
    """

    def __init__(self, filename, dbase):
        """
        Create a new BookList from the books that may be defined in the 
        specified file.

        file:   XML file that contains book items definitions
        """
        self.dbase = dbase
        self.bookmap = {}
        self.file = os.path.join(const.HOME_DIR, filename)
        self.parse()
    
    def delete_book(self, name):
        """
        Remove a book from the list. Since each book must have a
        unique name, the name is used to delete the book.

        name:   name of the book to delete
        """
        del self.bookmap[name]

    def get_book_map(self):
        """
        Return the map of names to books.
        """
        return self.bookmap

    def get_book(self, name):
        """
        Return the Book associated with the name

        name:   name associated with the desired Book.
        """
        return self.bookmap[name]

    def get_book_names(self):
        "Return a list of all the book names in the BookList"
        return self.bookmap.keys()

    def set_book(self, name, book):
        """
        Add or replaces a Book in the BookList. 

        name:   name assocated with the Book to add or replace.
        book:   definition of the Book
        """
        self.bookmap[name] = book

    def save(self):
        """
        Saves the current BookList to the associated file.
        """
        f = open(self.file, "w")
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        f.write('<booklist>\n')

        for name in self.bookmap.keys():
            book = self.get_book(name)
            dbname = book.get_dbname()
            f.write('<book name="%s" database="%s">\n' % (name, dbname) )
            for item in book.get_item_list():
                f.write('  <item name="%s" trans_name="%s">\n' % 
                            (item.get_name(),item.get_translated_name() ) )
                options = item.option_class.handler.options_dict
                for option_name in options.keys():
                    option_value = options[option_name]
                    if type(option_value) in (type(list()), type(tuple())):
                        f.write('  <option name="%s" value="" '
                                'length="%d">\n' % (
                                    escape(option_name),
                                    len(options[option_name]) ) )
                        for list_index in range(len(options[option_name])):
                            option_type = \
                                Utils.type_name(option_value[list_index])
                            value = escape(unicode(option_value[list_index]))
                            value = value.replace('"', '&quot;')
                            f.write('    <listitem number="%d" type="%s" '
                                    'value="%s"/>\n' % (
                                    list_index,
                                    option_type,
                                    value ) )
                        f.write('  </option>\n')
                    else:
                        option_type = Utils.type_name(option_value)
                        value = escape(unicode(option_value))
                        value = value.replace('"', '&quot;')
                        f.write('  <option name="%s" type="%s" '
                                'value="%s"/>\n' % (
                                escape(option_name),
                                option_type,
                                value) )

                f.write('    <style name="%s"/>\n' % item.get_style_name() )
                f.write('  </item>\n')
            f.write('</book>\n')

        f.write('</booklist>\n')
        f.close()
        
    def parse(self):
        """
        Loads the BookList from the associated file, if it exists.
        """
        try:
            p = make_parser()
            p.setContentHandler(BookParser(self, self.dbase))
            the_file = open(self.file)
            p.parse(the_file)
            the_file.close()
        except (IOError, OSError, ValueError, SAXParseException, KeyError, \
               AttributeError):
            pass


#-------------------------------------------------------------------------
#
# BookParser
#
#-------------------------------------------------------------------------
class BookParser(handler.ContentHandler):
    """
    SAX parsing class for the Books XML file.
    """
    
    def __init__(self, booklist, dbase):
        """
        Create a BookParser class that populates the passed booklist.

        booklist:   BookList to be loaded from the file.
        """
        handler.ContentHandler.__init__(self)
        self.dbase = dbase
        self.booklist = booklist
        self.b = None
        self.i = None
        self.o = None
        self.an_o_name = None
        self.an_o_value = None
        self.s = None
        self.bname = None
        self.iname = None
        
    def startElement(self, tag, attrs):
        """
        Overridden class that handles the start of a XML element
        """
        if tag == "book":
            self.b = Book()
            self.bname = attrs['name']
            self.b.set_name(self.bname)
            self.dbname = attrs['database']
            self.b.set_dbname(self.dbname)
        elif tag == "item":
            self.i = BookItem(self.dbase, attrs['name'])
            self.o = {}
        elif tag == "option":
            self.an_o_name = attrs['name']
            if attrs.has_key('length'):
                self.an_o_value = []
            else:
                converter = Utils.get_type_converter_by_name(attrs['type'])
                self.an_o_value = converter(attrs['value'])
        elif tag == "listitem":
            converter = Utils.get_type_converter_by_name(attrs['type'])
            self.an_o_value.append(converter(attrs['value']))
        elif tag == "style":
            self.s = attrs['name']
        else:
            pass

    def endElement(self, tag):
        "Overridden class that handles the end of a XML element"
        if tag == "option":
            self.o[self.an_o_name] = self.an_o_value
        elif tag == "item":
            self.i.option_class.handler.options_dict.update(self.o)
            self.i.set_style_name(self.s)
            self.b.append_item(self.i)
        elif tag == "book":
            self.booklist.set_book(self.bname, self.b)

#------------------------------------------------------------------------
#
# BookList Display class
#
#------------------------------------------------------------------------
class BookListDisplay:
    """
    Interface into a dialog with the list of available books. 

    Allows the user to select and/or delete a book from the list.
    """

    def __init__(self, booklist, nodelete=0, dosave=0):
        """
        Create a BookListDisplay object that displays the books in BookList.

        booklist:   books that are displayed
        nodelete:   if not 0 then the Delete button is hidden
        dosave:     if 1 then the book list is saved on hitting OK
        """
        
        self.booklist = booklist
        self.dosave = dosave
        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")
        self.xml = glade.XML(glade_file, "booklist", "gramps")
        self.top = self.xml.get_widget('booklist')

        ManagedWindow.set_titles(self.top,
            self.xml.get_widget('title'),_('Available Books'))

        if nodelete:
            delete_button = self.xml.get_widget("delete_button")
            delete_button.hide()

        self.xml.signal_autoconnect({
            "on_booklist_cancel_clicked" : self.on_booklist_cancel_clicked,
            "on_booklist_ok_clicked" : self.on_booklist_ok_clicked,
            "on_booklist_delete_clicked" : self.on_booklist_delete_clicked
            })

        title_label = self.xml.get_widget('title')
        title_label.set_text(Utils.title(_('Book List')))
        title_label.set_use_markup(True)
        
        self.blist = ListModel.ListModel(self.xml.get_widget("list"),
                                        [('Name',-1,10)],)
        self.redraw()
        self.selection = None
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
        """Return selected book. Saves the current list into xml file."""
        store, the_iter = self.blist.get_selected()
        if the_iter:
            data = self.blist.get_data(the_iter, [0])
            self.selection = self.booklist.get_book(unicode(data[0]))
        if self.dosave:
            self.booklist.save()

    def on_booklist_delete_clicked(self, obj):
        """
        Deletes selected book from the list.
        
        This change is not final. OK button has to be clicked to save the list.
        """
        store, the_iter = self.blist.get_selected()
        if not the_iter:
            return
        data = self.blist.get_data(the_iter, [0])
        self.booklist.delete_book(unicode(data[0]))
        self.blist.remove(the_iter)
        self.top.run()

    def on_booklist_cancel_clicked(self, obj):
        pass

#------------------------------------------------------------------------
#
# 
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
        self.options_help = {
            'bookname'    : ("=name","Name of the book. MANDATORY",
                            BookList('books.xml',dbase).get_book_names(),
                            False),
        }

#-------------------------------------------------------------------------
#
# Book creation dialog 
#
#-------------------------------------------------------------------------
class BookReportSelector(ManagedWindow.ManagedWindow):
    """
    Interface into a dialog setting up the book. 

    Allows the user to add/remove/reorder/setup items for the current book
    and to clear/load/save/edit whole books.
    """

    def __init__(self, dbstate, uistate):
        self.db = dbstate.db
        self.dbstate = dbstate
        self.uistate = uistate
        self.title = _('Book Report')
        self.file = "books.xml"

        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)

        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")

        self.xml = glade.XML(glade_file, "top", "gramps")
        window = self.xml.get_widget("top")
        title_label = self.xml.get_widget('title')
        self.set_window(window, title_label, self.title)
    
        self.xml.signal_autoconnect({
            "on_add_clicked"        : self.on_add_clicked,
            "on_remove_clicked"     : self.on_remove_clicked,
            "on_up_clicked"         : self.on_up_clicked,
            "on_down_clicked"       : self.on_down_clicked,
            "on_setup_clicked"      : self.on_setup_clicked,
            "on_clear_clicked"      : self.on_clear_clicked,
            "on_save_clicked"       : self.on_save_clicked,
            "on_open_clicked"       : self.on_open_clicked,
            "on_edit_clicked"       : self.on_edit_clicked,
            "on_book_ok_clicked"    : self.on_book_ok_clicked,
            "destroy_passed_object" : self.close
            })

        self.avail_tree = self.xml.get_widget("avail_tree")
        self.book_tree = self.xml.get_widget("book_tree")
        self.avail_tree.connect('button-press-event', self.av_button_press)
        self.book_tree.connect('button-press-event', self.bk_button_press)

        self.name_entry = self.xml.get_widget("name_entry")
        self.name_entry.set_text(_('New Book'))

        avail_label = self.xml.get_widget('avail_label')
        avail_label.set_text("<b>%s</b>" % _("_Available items"))
        avail_label.set_use_markup(True)
        avail_label.set_use_underline(True)
        book_label = self.xml.get_widget('book_label')
        book_label.set_text("<b>%s</b>" % _("Current _book"))
        book_label.set_use_underline(True)
        book_label.set_use_markup(True)

        av_titles = [ (_('Name'), 0, 150),
                      (_('Type'), 1, 50 ),
                      (  '' ,    -1, 0  ) ]
        
        bk_titles = [ (_('Item name'), -1, 150),
                      (_('Type'),      -1, 50 ),
                      (  '',           -1, 0  ),
                      (_('Subject'),   -1, 50 ) ]
        
        self.av_ncols = len(av_titles)
        self.bk_ncols = len(bk_titles)

        self.av_model = ListModel.ListModel(self.avail_tree, av_titles)
        self.bk_model = ListModel.ListModel(self.book_tree, bk_titles)
        self.draw_avail_list()

        self.book = Book()

    def build_menu_names(self, obj):
        return (_("Book selection list"), self.title)

    def draw_avail_list(self):
        """
        Draw the list with the selections available for the book.
        
        The selections are read from the book item registry.
        """

        if not bkitems_list:
            return

        for book_item in bkitems_list:
            if book_item[5]:
                category = Plugins.UNSUPPORTED
            else:
                category = book_item[1]
            
            data = [ book_item[0], category, book_item[4] ] 
            new_iter = self.av_model.add(data)

        self.av_model.connect_model()

        if new_iter:
            self.av_model.selection.select_iter(new_iter)
            path = self.av_model.model.get_path(new_iter)
            col = self.avail_tree.get_column(0)
            self.avail_tree.scroll_to_cell(path, col, 1, 1, 0.0)

    def open_book(self, book):
        """
        Open the book: set the current set of selections to this book's items.
        
        book:   the book object to load.
        """
        if book.get_dbname() == self.db.get_save_path():
            same_db = 1
        else:
            same_db = 0
            WarningDialog(_('Different database'), _(
                'This book was created with the references to database '
                '%s.\n\n This makes references to the central person '
                'saved in the book invalid.\n\n' 
                'Therefore, the central person for each item is being set ' 
                'to the active person of the currently opened database.' )
                % book.get_dbname() )
            
        self.book.clear()
        self.bk_model.clear()
        for saved_item in book.get_item_list():
            name = saved_item.get_name()
            item = BookItem(self.db, name)
            item.option_class = saved_item.option_class
            _initialize_options(item.option_class, self.dbstate)
            item.set_style_name(saved_item.get_style_name())
            self.book.append_item(item)
            
            data = [ item.get_translated_name(),
                     item.get_category(), item.get_name() ]
            
            data[2] = _get_subject(item.option_class, self.db)
            self.bk_model.add(data)

    def on_add_clicked(self, obj):
        """
        Add an item to the current selections. 
        
        Use the selected available item to get the item's name in the registry.
        """
        store, the_iter = self.av_model.get_selected()
        if not the_iter:
            return
        data = self.av_model.get_data(the_iter, range(self.av_ncols))
        item = BookItem(self.db, data[2])
        _initialize_options(item.option_class, self.dbstate)
        data[2] = _get_subject(item.option_class, self.db)
        self.bk_model.add(data)
        self.book.append_item(item)

    def on_remove_clicked(self, obj):
        """
        Remove the item from the current list of selections.
        """
        store, the_iter = self.bk_model.get_selected()
        if not the_iter:
            return
        row = self.bk_model.get_selected_row()
        self.book.pop_item(row)
        self.bk_model.remove(the_iter)

    def on_clear_clicked(self, obj):
        """
        Clear the whole current book.
        """
        self.bk_model.clear()
        self.book.clear()

    def on_up_clicked(self, obj):
        """
        Move the currently selected item one row up in the selection list.
        """
        row = self.bk_model.get_selected_row()
        if not row or row == -1:
            return
        store, the_iter = self.bk_model.get_selected()
        data = self.bk_model.get_data(the_iter, range(self.bk_ncols))
        self.bk_model.remove(the_iter)
        self.bk_model.insert(row-1, data, None, 1)
        item = self.book.pop_item(row)
        self.book.insert_item(row-1, item)

    def on_down_clicked(self, obj):
        """
        Move the currently selected item one row down in the selection list.
        """
        row = self.bk_model.get_selected_row()
        if row + 1 >= self.bk_model.count or row == -1:
            return
        store, the_iter = self.bk_model.get_selected()
        data = self.bk_model.get_data(the_iter, range(self.bk_ncols))
        self.bk_model.remove(the_iter)
        self.bk_model.insert(row+1, data, None, 1)
        item = self.book.pop_item(row)
        self.book.insert_item(row+1, item)

    def on_setup_clicked(self, obj):
        """
        Configure currently selected item.
        """
        store, the_iter = self.bk_model.get_selected()
        if not the_iter:
            return
        data = self.bk_model.get_data(the_iter, range(self.bk_ncols))
        row = self.bk_model.get_selected_row()
        item = self.book.get_item(row)
        option_class = item.option_class
        item_dialog = BookItemDialog(self.dbstate, self.uistate, option_class,
                                     item.get_name(),
                                     item.get_translated_name(),
                                     self.track)
        response = item_dialog.window.run()
        if response == RESPONSE_OK:
            subject = _get_subject(option_class, self.db)
            self.bk_model.model.set_value(the_iter, 2, subject)
            self.book.set_item(row, item)
        item_dialog.close()

    def bk_button_press(self, obj, event):
        """
        Double-click on the current book selection is the same as setup.
        Right click evokes the context menu. 
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_setup_clicked(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_bk_context_menu(event)

    def av_button_press(self, obj, event):
        """
        Double-click on the available selection is the same as add.
        Right click evokes the context menu. 
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_add_clicked(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_av_context_menu(event)

    def build_bk_context_menu(self, event):
        """Builds the menu with item-centered and book-centered options."""
        
        store, the_iter = self.bk_model.get_selected()
        if the_iter:
            sensitivity = 1 
        else:
            sensitivity = 0 
        entries = [
            (gtk.STOCK_GO_UP, self.on_up_clicked, sensitivity),
            (gtk.STOCK_GO_DOWN, self.on_down_clicked, sensitivity),
            (_("Setup"), self.on_setup_clicked, sensitivity),
            (gtk.STOCK_REMOVE, self.on_remove_clicked, sensitivity),
            (None,None,0),
            (gtk.STOCK_CLEAR, self.on_clear_clicked, 1),
            (gtk.STOCK_SAVE, self.on_save_clicked, 1),
            (gtk.STOCK_OPEN, self.on_open_clicked, 1),
            (_("Edit"), self.on_edit_clicked,1 ),
        ]

        menu = gtk.Menu()
        menu.set_title(_('Book Menu'))
        for stock_id, callback, sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate", callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)

    def build_av_context_menu(self, event):
        """Builds the menu with the single Add option."""
        
        store, the_iter = self.av_model.get_selected()
        if the_iter:
            sensitivity = 1 
        else:
            sensitivity = 0 
        entries = [
            (gtk.STOCK_ADD, self.on_add_clicked, sensitivity),
        ]

        menu = gtk.Menu()
        menu.set_title(_('Available Items Menu'))
        for stock_id, callback, sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate", callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)

    def on_book_ok_clicked(self, obj): 
        """
        Run final BookReportDialog with the current book. 
        """
        if self.book.item_list:
            BookReportDialog(self.dbstate, self.uistate,
                             self.book, BookOptions)
        self.close()

    def on_save_clicked(self, obj):
        """
        Save the current book in the xml booklist file. 
        """
        self.book_list = BookList(self.file, self.db)
        name = unicode(self.name_entry.get_text())
        self.book.set_name(name)
        self.book.set_dbname(self.db.get_save_path())
        self.book_list.set_book(name, self.book)
        self.book_list.save()

    def on_open_clicked(self, obj):
        """
        Run the BookListDisplay dialog to present the choice of books to open. 
        """
        self.book_list = BookList(self.file, self.db)
        booklistdisplay = BookListDisplay(self.book_list, 1, 0)
        booklistdisplay.top.destroy()
        book = booklistdisplay.selection
        if book:
            self.open_book(book)
            self.name_entry.set_text(book.get_name())

    def on_edit_clicked(self, obj):
        """
        Run the BookListDisplay dialog to present the choice of books to delete. 
        """
        self.book_list = BookList(self.file, self.db)
        booklistdisplay = BookListDisplay(self.book_list, 0, 1)
        booklistdisplay.top.destroy()

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

    def __init__(self, dbstate, uistate, option_class, name, translated_name,
                 track=[]):
        self.category = CATEGORY_BOOK
        self.database = dbstate.db
        self.option_class = option_class
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

#------------------------------------------------------------------------
#
# The final dialog - paper, format, target, etc. 
#
#------------------------------------------------------------------------
class BookReportDialog(DocReportDialog):
    """
    A usual Report.Dialog subclass. 
    
    Create a dialog selecting target, format, and paper/HTML options.
    """

    def __init__(self, dbstate, uistate, book, options):
        self.options = options
        self.page_html_added = False
        DocReportDialog.__init__(self, dbstate, uistate, options,
                                  'book', _("Book Report"))
        self.book = book
        self.database = dbstate.db
        self.selected_style = BaseDoc.StyleSheet()

        for item in self.book.get_item_list():
            # Set up default style
            default_style = BaseDoc.StyleSheet()
            make_default_style = item.option_class.make_default_style
            make_default_style(default_style)

            # Read all style sheets available for this item
            style_file = item.option_class.handler.get_stylesheet_savefile()
            style_list = BaseDoc.StyleSheetList(style_file, default_style)

            # Get the selected stylesheet
            style_name = item.option_class.handler.get_default_stylesheet_name()
            style_sheet = style_list.get_style_sheet(style_name)

            for this_style_name in style_sheet.get_paragraph_style_names():
                self.selected_style.add_paragraph_style(
                    this_style_name,style_sheet.get_paragraph_style(this_style_name))

            for this_style_name in style_sheet.get_draw_style_names():
                self.selected_style.add_draw_style(
                    this_style_name,style_sheet.get_draw_style(this_style_name))

            for this_style_name in style_sheet.get_table_style_names():
                self.selected_style.add_table_style(
                    this_style_name,style_sheet.get_table_style(this_style_name))

            for this_style_name in style_sheet.get_cell_style_names():
                self.selected_style.add_cell_style(
                    this_style_name,style_sheet.get_cell_style(this_style_name))

        response = self.window.run()
        if response == RESPONSE_OK:
            try:
                self.make_report()
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))
        self.close()

    def setup_style_frame(self): pass
    def setup_other_frames(self): pass
    def parse_style_frame(self): pass

    def doc_uses_tables(self):
        return 1

    def get_title(self):
        return _("Book Report")

    def get_header(self, name):
        return _("GRAMPS Book")

    def get_stylesheet_savefile(self):
        """Needed solely for forming sane filename for the output."""
        return "book.xml"

    def make_doc_menu(self, active=None):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        self.format_menu = BookFormatComboBox()
        self.format_menu.set(self.doc_uses_tables(),
                             self.doc_type_changed, None, active)

    def make_document(self):
        """Create a document of the type requested by the user."""
        pstyle = self.paper_frame.get_paper_style()
        self.doc = self.format(self.selected_style, pstyle, self.template_name)

        self.rptlist = []
        for item in self.book.get_item_list():
            item.option_class.set_document(self.doc)
            report_class = item.get_write_item()
            obj = write_book_item(self.database,
                                  report_class, item.option_class)
            self.rptlist.append(obj)
        self.doc.open(self.target_path)
        
        if self.print_report.get_active():
            self.doc.print_requested ()

    def make_report(self):
        """The actual book report. Start it out, then go through the item list 
        and call each item's write_book_item method."""

        self.doc.init()
        newpage = 0
        for item in self.rptlist:
            if newpage:
                self.doc.page_break()
            newpage = 1
            item.begin_report()
            item.write_report()
        self.doc.close()

#------------------------------------------------------------------------
#
# Function to write books from command line
#
#------------------------------------------------------------------------
def cl_report(database, name, category, options_str_dict):

    clr = CommandLineReport(database, name, category,
                            BookOptions, options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return
    
    if not clr.options_dict.has_key('bookname'):
        print "Please Specify a book name"
        return

    book_list = BookList('books.xml', database)
    book_name = clr.options_dict['bookname']
    book = book_list.get_book(book_name)
    selected_style = BaseDoc.StyleSheet()

    for item in book.get_item_list():
        # Set up default style
        default_style = BaseDoc.StyleSheet()
        make_default_style = item.option_class.make_default_style
        make_default_style(default_style)

        # Read all style sheets available for this item
        style_file = item.option_class.handler.get_stylesheet_savefile()
        style_list = BaseDoc.StyleSheetList(style_file, default_style)

        # Get the selected stylesheet
        style_name = item.option_class.handler.get_default_stylesheet_name()
        style_sheet = style_list.get_style_sheet(style_name)

        for this_style_name in style_sheet.get_paragraph_style_names():
            selected_style.add_paragraph_style(
                    this_style_name, 
                    style_sheet.get_paragraph_style(this_style_name))

    # write report
    doc = clr.format(selected_style, clr.paper, clr.template_name, clr.orien)
    rptlist = []
    for item in book.get_item_list():
        item.option_class.set_document(doc)
        report_class = item.get_write_item()
        obj = write_book_item(database,
                              report_class, item.option_class)
        rptlist.append(obj)

    doc.open(clr.option_class.get_output())
    doc.init()
    newpage = 0
    for item in rptlist:
        if newpage:
            doc.page_break()
        newpage = 1
        item.begin_report()
        item.write_report()
    doc.close()

#------------------------------------------------------------------------
#
# Generic task function for book report
#
#------------------------------------------------------------------------
def write_book_item(database, report_class, options_class):
    """Write the Timeline Graph using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        return report_class(database, options_class)
    except Errors.ReportError, msg:
        (m1, m2) = msg.messages()
        ErrorDialog(m1, m2)
    except Errors.FilterError, msg:
        (m1, m2) = msg.messages()
        ErrorDialog(m1, m2)
    except:
        log.error("Failed to write book item.", exc_info=True)
    return None

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'book',
    category = CATEGORY_BOOK,
    report_class = BookReportSelector,
    options_class = cl_report,
    modes = MODE_GUI | MODE_CLI,
    translated_name = _("Book Report"),
    status = _("Stable"),
    description = _("Produces a book containing several reports."),
    author_name = "Alex Roitman",
    author_email = "shura@gramps-project.org"
    )
