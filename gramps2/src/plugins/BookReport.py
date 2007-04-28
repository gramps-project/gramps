#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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

from xml.sax.saxutils import escape

def escxml(d):
    return escape(d, { '"' : '&quot;' } )

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
    from xml.sax import make_parser,handler,SAXParseException
except:
    from _xmlplus.sax import make_parser,handler,SAXParseException

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import RESPONSE_OK
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import Person
import const
import Utils
import ListModel
import Errors
import BaseDoc
from QuestionDialog import WarningDialog, ErrorDialog
from PluginUtils import bkitems_list, register_report, Plugins
import ManagedWindow

# Import from specific modules in ReportBase
from ReportBase._Constants import CATEGORY_BOOK, MODE_GUI, MODE_CLI
from ReportBase._BookFormatComboBox import BookFormatComboBox
from ReportBase._BareReportDialog import BareReportDialog
from ReportBase._ReportDialog import ReportDialog
from ReportBase._CommandLineReport import CommandLineReport
from ReportBase._ReportOptions import ReportOptions

#------------------------------------------------------------------------
#
# Book Item class
#
#------------------------------------------------------------------------
class BookItem:
    """
    Interface into the book item -- a smallest element of the book.
    """

    def __init__(self,name=None):
        """
        Creates a new empty BookItem.
        
        name:   if not None then the book item is retreived 
                from the book item registry using name for lookup
        """

        if name:
            self.get_registered_item(name)
        else:
            self.clear()
        
    def clear(self):
        """
        Clear the contents of the book item.
        
        Everything gets set to empty values except for the style_name"""

        self.translated_name = ""
        self.category = ""
        self.write_item = None
        self.option_class = None
        self.style_file = ""
        self.style_name = "default"
        self.make_default_style = None
        self.name = ""

    def get_registered_item(self,name):
        """ 
        Retrieve the item from the book item registry.
        
        name:   a name used for lookup.
        """

        self.clear()
        for item in bkitems_list:
            if item[4] == name:
                self.translated_name = item[0]
                if item[5]:
                    self.category = Plugins.UNSUPPORTED
                else:
                    self.category = item[1]
                self.write_item = item[2]
                self.name = item[4]
                self.option_class = item[3](self.name)

    def get_name(self):
        """
        Returns the name of the item.
        """
        return self.name

    def get_translated_name(self):
        """
        Returns the translated name of the item.
        """
        return self.translated_name

    def get_category(self):
        """
        Returns the category of the item.
        """
        return self.category

    def get_write_item(self):
        """
        Returns the report-writing function of the item.
        """
        return self.write_item

    def set_style_name(self,style_name):
        """
        Sets the style name for the item.
        
        style_name: name of the style to set.
        """
        self.style_name = style_name

    def get_style_name(self):
        """
        Returns the style name of the item.
        """
        return self.style_name

    def get_style_file(self):
        """
        Returns the style file name for the item.
        """
        return self.style_file

    def get_make_default_style(self):
        """
        Returns the function to make default style for the item.
        """
        return self.make_default_style

#------------------------------------------------------------------------
#
# Book class
#
#------------------------------------------------------------------------
class Book:
    """
    Interface into the user-defined book -- a collection of book items.
    """

    def __init__(self,obj=None):
        """
        Creates a new empty Book.

        obj:    if not None, creates the Book from the values in
                obj, instead of creating an empty Book.
        """

        self.name = ""
        self.dbname = ""
        if obj:
            self.item_list = obj.item_list
        else:
            self.item_list = []
        
    def set_name(self,name):
        """
        Sets the name of the book.
        
        name:   the name to set.
        """
        self.name = name

    def get_name(self):
        """
        Returns the name of the book.
        """
        return self.name

    def get_dbname(self):
        """
        Returns the name of the database file used for the book.
        """
        return self.dbname

    def set_dbname(self,name):
        """
        Sets the name of the database file used for the book.

        name:   a filename to set.
        """
        self.dbname = name

    def clear(self):
        """
        Clears the contents of the book.
        """
        self.item_list = []

    def append_item(self,item):
        """
        Adds an item to the book.
        
        item:   an item to append.
        """
        self.item_list.append(item)

    def insert_item(self,index,item):
        """
        Inserts an item into the given position in the book.
        
        index:  a position index. 
        item:   an item to append.
        """
        self.item_list.insert(index,item)

    def pop_item(self,index):
        """
        Pop an item from given position in the book.
        
        index:  a position index. 
        """
        return self.item_list.pop(index)

    def get_item(self,index):
        """
        Returns an item at a given position in the book.
        
        index:  a position index. 
        """
        return self.item_list[index]

    def set_item(self,index,item):
        """
        Sets an item at a given position in the book.
        
        index:  a position index. 
        item:   an item to set.
        """
        self.item_list[index] = item

    def get_item_list(self):
        """
        Returns list of items in the current book.
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

    def __init__(self,filename):
        """
        Creates a new BookList from the books that may be defined in the 
        specified file.

        file:   XML file that contains book items definitions
        """

        self.bookmap = {}
        self.file = os.path.join(const.home_dir,filename)
        self.parse()
    
    def delete_book(self,name):
        """
        Removes a book from the list. Since each book must have a
        unique name, the name is used to delete the book.

        name:   name of the book to delete
        """
        del self.bookmap[name]

    def get_book_map(self):
        """
        Returns the map of names to books.
        """
        return self.bookmap

    def get_book(self,name):
        """
        Returns the Book associated with the name

        name:   name associated with the desired Book.
        """
        return self.bookmap[name]

    def get_book_names(self):
        "Returns a list of all the book names in the BookList"
        return self.bookmap.keys()

    def set_book(self,name,book):
        """
        Adds or replaces a Book in the BookList. 

        name:   name assocated with the Book to add or replace.
        book:   definition of the Book
        """
        self.bookmap[name] = book

    def save(self):
        """
        Saves the current BookList to the associated file.
        """
        f = open(self.file,"w")
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        f.write('<booklist>\n')

        for name in self.bookmap.keys():
            book = self.get_book(name)
            dbname = book.get_dbname()
            f.write('<book name="%s" database="%s">\n' % (escxml(name), escxml(dbname)) )
            for item in book.get_item_list():
                f.write('  <item name="%s" trans_name="%s">\n' % 
                            (escxml(item.get_name()), escxml(item.get_translated_name()) ) )
                option_handler = item.option_class.handler
                for option_name in option_handler.options_dict.keys():
                    option_value = option_handler.options_dict[option_name]
                    if type(option_value) in (list,tuple):
                        f.write('    <option name="%s" length="%d">\n' % (
                                escxml(option_name), len(option_value) ) )
                        for list_index in range(len(option_value)):
                            option_type = Utils.type_name(option_value[list_index])
                            f.write('      <listitem number="%d" type="%s" value="%s"/>\n' % (
                                    list_index, escxml(option_type), escxml(option_value[list_index])) )
                        f.write('    </option>\n')
                    else:
                        option_type = Utils.type_name(option_value)
                        f.write('    <option name="%s" type="%s" value="%s"/>\n' % (
                                escxml(option_name), escxml(option_type), escxml(str(option_value))) )
                f.write('    <person gramps_id="%s"/>\n' % 
                        escxml(option_handler.get_person_id()) )
                f.write('    <style name="%s"/>\n' % escxml(item.get_style_name()) )
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
            p.setContentHandler(BookParser(self))
            p.parse(self.file)
        except (IOError,OSError,ValueError,SAXParseException):
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
    
    def __init__(self,booklist):
        """
        Creates a BookParser class that populates the passed booklist.

        booklist:   BookList to be loaded from the file.
        """
        handler.ContentHandler.__init__(self)
        self.booklist = booklist
        self.b = None
        self.i = None
        self.o = None
        self.an_o_name = None
        self.an_o_value = None
        self.s = None
        self.p = None
        self.bname = None
        self.iname = None
        
    def startElement(self,tag,attrs):
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
            self.i = BookItem(attrs['name'])
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
        elif tag == "person":
            self.p = attrs['gramps_id']

    def endElement(self,tag):
        "Overridden class that handles the end of a XML element"
        if tag == "option":
            self.o[self.an_o_name] = self.an_o_value
        elif tag == "item":
            self.i.option_class.handler.options_dict.update(self.o)
            self.i.option_class.handler.set_person_id(self.p)
            self.i.set_style_name(self.s)
            self.b.append_item(self.i)
        elif tag == "book":
            self.booklist.set_book(self.bname,self.b)

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

    def __init__(self,booklist,nodelete=0,dosave=0):
        """
        Creates a BookListDisplay object that displays the books in BookList.

        booklist:   books that are displayed
        nodelete:   if not 0 then the Delete button is hidden
        dosave:     if 1 then the book list is saved on hitting OK
        """
        
        self.booklist = booklist
        self.dosave = dosave
        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")
        self.xml = gtk.glade.XML(glade_file,"booklist","gramps")
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

    def on_booklist_ok_clicked(self,obj):
        """Returns selected book. Saves the current list into xml file."""
        store,the_iter = self.blist.get_selected()
        if the_iter:
            data = self.blist.get_data(the_iter,[0])
            self.selection = self.booklist.get_book(data[0])
        if self.dosave:
            self.booklist.save()

    def on_booklist_delete_clicked(self,obj):
        """
        Deletes selected book from the list.
        
        This change is not final. OK button has to be clicked to save the list.
        """
        store,the_iter = self.blist.get_selected()
        if not the_iter:
            return
        data = self.blist.get_data(the_iter,[0])
        self.booklist.delete_book(data[0])
        self.blist.remove(the_iter)
        self.top.run()

    def on_booklist_cancel_clicked(self,obj):
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

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'bookname'    : '',
        }
        self.options_help = {
            'bookname'    : ("=name","Name of the book. MANDATORY",
                            BookList('books.xml').get_book_names(),
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

    def __init__(self,dbstate,uistate,person):
        self.db = dbstate.db
        self.dbstate = dbstate
        self.uistate = uistate
        self.person = person
        self.title = _('Book Report')
        self.file = "books.xml"

        ManagedWindow.ManagedWindow.__init__(self,uistate, [], self.__class__)

        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")

        self.xml = gtk.glade.XML(glade_file,"top","gramps")
        window = self.xml.get_widget("top")
        title_label = self.xml.get_widget('title')
        self.set_window(window,title_label,self.title)
    
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
        self.avail_tree.connect('button-press-event',self.av_button_press)
        self.book_tree.connect('button-press-event',self.bk_button_press)

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

        av_titles = [(_('Name'),0,150),(_('Type'),1,50),('',-1,0)]
        bk_titles = [(_('Item name'),-1,150),(_('Type'),-1,50),('',-1,0),
            (_('Center person'),-1,50)]
        
        self.av_ncols = len(av_titles)
        self.bk_ncols = len(bk_titles)

        self.av_model = ListModel.ListModel(self.avail_tree,av_titles)
        self.bk_model = ListModel.ListModel(self.book_tree,bk_titles)
        self.draw_avail_list()

        self.book = Book()

    def build_menu_names(self,obj):
        return (_("Book selection list"),self.title)

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
            self.avail_tree.scroll_to_cell(path,col,1,1,0.0)

    def open_book(self,book):
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
            item = BookItem(name)
            item.option_class = saved_item.option_class
            person_id = item.option_class.handler.get_person_id()
            if not same_db or not person_id:
                person_id = self.person.get_gramps_id()
                item.option_class.handler.set_person_id(person_id)
            item.set_style_name(saved_item.get_style_name())
            self.book.append_item(item)
            
            data = [ item.get_translated_name(),
                     item.get_category(), item.get_name() ]
            if data[2] in ('simple_book_title','custom_text'):
                data[2]=(_("Not Applicable"))
            else:
                pname = self.db.get_person_from_gramps_id(person_id)
                data[2]=(pname.get_primary_name().get_regular_name())
            self.bk_model.add(data)

    def on_add_clicked(self,obj):
        """
        Add an item to the current selections. 
        
        Use the selected available item to get the item's name in the registry.
        """
        store,the_iter = self.av_model.get_selected()
        if not the_iter:
            return
        data = self.av_model.get_data(the_iter,range(self.av_ncols))
        item = BookItem(data[2])
        if data[2] in ('simple_book_title','custom_text'):
            data[2]=(_("Not Applicable"))
        else:
            data[2]=(self.person.get_primary_name().get_regular_name())
        self.bk_model.add(data)
        person_id = item.option_class.handler.get_person_id()
        if not person_id:
            person_id = self.person.get_gramps_id()
            item.option_class.handler.set_person_id(person_id)
        self.book.append_item(item)

    def on_remove_clicked(self,obj):
        """
        Remove the item from the current list of selections.
        """
        store,the_iter = self.bk_model.get_selected()
        if not the_iter:
            return
        row = self.bk_model.get_selected_row()
        self.book.pop_item(row)
        self.bk_model.remove(the_iter)

    def on_clear_clicked(self,obj):
        """
        Clear the whole current book.
        """
        self.bk_model.clear()
        self.book.clear()

    def on_up_clicked(self,obj):
        """
        Move the currently selected item one row up in the selection list.
        """
        row = self.bk_model.get_selected_row()
        if not row or row == -1:
            return
        store,the_iter = self.bk_model.get_selected()
        data = self.bk_model.get_data(the_iter,range(self.bk_ncols))
        self.bk_model.remove(the_iter)
        self.bk_model.insert(row-1,data,None,1)
        item = self.book.pop_item(row)
        self.book.insert_item(row-1,item)

    def on_down_clicked(self,obj):
        """
        Move the currently selected item one row down in the selection list.
        """
        row = self.bk_model.get_selected_row()
        if row + 1 >= self.bk_model.count or row == -1:
            return
        store,the_iter = self.bk_model.get_selected()
        data = self.bk_model.get_data(the_iter,range(self.bk_ncols))
        self.bk_model.remove(the_iter)
        self.bk_model.insert(row+1,data,None,1)
        item = self.book.pop_item(row)
        self.book.insert_item(row+1,item)

    def on_setup_clicked(self,obj):
        """
        Configure currently selected item.
        """
        store,the_iter = self.bk_model.get_selected()
        if not the_iter:
            return
        data = self.bk_model.get_data(the_iter,range(self.bk_ncols))
        row = self.bk_model.get_selected_row()
        item = self.book.get_item(row)
        option_class = item.option_class
        item_dialog = BookItemDialog(self.dbstate,self.uistate,option_class,
                                     item.get_name(),
                                     item.get_translated_name(),
                                     self.track)
        response = item_dialog.window.run()
        if (response == RESPONSE_OK) and (item_dialog.person) \
               and (data[1] != _("Title")): 
            self.bk_model.model.set_value(the_iter,2,
                item_dialog.person.get_primary_name().get_regular_name())
            self.book.set_item(row,item)
        item_dialog.close()

    def bk_button_press(self,obj,event):
        """
        Double-click on the current book selection is the same as setup.
        Right click evokes the context menu. 
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_setup_clicked(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_bk_context_menu(event)

    def av_button_press(self,obj,event):
        """
        Double-click on the available selection is the same as add.
        Right click evokes the context menu. 
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_add_clicked(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_av_context_menu(event)

    def build_bk_context_menu(self,event):
        """Builds the menu with item-centered and book-centered options."""
        
        store,the_iter = self.bk_model.get_selected()
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
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def build_av_context_menu(self,event):
        """Builds the menu with the single Add option."""
        
        store,the_iter = self.av_model.get_selected()
        if the_iter:
            sensitivity = 1 
        else:
            sensitivity = 0 
        entries = [
            (gtk.STOCK_ADD, self.on_add_clicked, sensitivity),
        ]

        menu = gtk.Menu()
        menu.set_title(_('Available Items Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def on_book_ok_clicked(self,obj): 
        """
        Run final BookReportDialog with the current book. 
        """
        if self.book.item_list:
            BookReportDialog(self.dbstate,self.uistate,self.person,
                             self.book,BookOptions)
        self.close()

    def on_save_clicked(self,obj):
        """
        Save the current book in the xml booklist file. 
        """
        self.book_list = BookList(self.file)
        name = unicode(self.name_entry.get_text())
        self.book.set_name(name)
        self.book.set_dbname(self.db.get_save_path())
        self.book_list.set_book(name,self.book)
        self.book_list.save()

    def on_open_clicked(self,obj):
        """
        Run the BookListDisplay dialog to present the choice of books to open. 
        """
        self.book_list = BookList(self.file)
        booklistdisplay = BookListDisplay(self.book_list,1,0)
        booklistdisplay.top.destroy()
        book = booklistdisplay.selection
        if book:
            self.open_book(book)
            self.name_entry.set_text(book.get_name())

    def on_edit_clicked(self,obj):
        """
        Run the BookListDisplay dialog to present the choice of books to delete. 
        """
        self.book_list = BookList(self.file)
        booklistdisplay = BookListDisplay(self.book_list,0,1)
        booklistdisplay.top.destroy()

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class BookItemDialog(BareReportDialog):

    """
    This class overrides the interface methods common for different reports
    in a way specific for this report. This is a book item dialog.
    """

    def __init__(self,dbstate,uistate,option_class,name,translated_name,
                 track=[]):

        self.database = dbstate.db
        self.option_class = option_class
        self.person = self.database.get_person_from_gramps_id(
            self.option_class.handler.get_person_id())
        self.new_person = None
        BareReportDialog.__init__(self,dbstate,uistate,self.person,
                                  option_class,name,translated_name,track)

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        self.parse_user_options()

        if self.new_person:
            self.person = self.new_person

        self.option_class.handler.set_person_id(self.person.get_gramps_id())
        self.options.handler.save_options()

#------------------------------------------------------------------------
#
# The final dialog - paper, format, target, etc. 
#
#------------------------------------------------------------------------
class BookReportDialog(ReportDialog):
    """
    A usual Report.Dialog subclass. 
    
    Creates a dialog selecting target, format, and paper/HTML options.
    """

    def __init__(self,dbstate,uistate,person,book,options):
        self.options = options
        self.page_html_added = False
        BareReportDialog.__init__(self,dbstate,uistate,person,options,
                                  'book',_("Book Report"))
        self.book = book
        self.database = dbstate.db
        self.person = person
        self.selected_style = BaseDoc.StyleSheet()

        for item in self.book.get_item_list():
            # Set up default style
            default_style = BaseDoc.StyleSheet()
            make_default_style = item.option_class.make_default_style
            make_default_style(default_style)

            # Read all style sheets available for this item
            style_file = item.option_class.handler.get_stylesheet_savefile()
            style_list = BaseDoc.StyleSheetList(style_file,default_style)

            # Get the selected stylesheet
            style_name = item.option_class.handler.get_default_stylesheet_name()
            style_sheet = style_list.get_style_sheet(style_name)

            for this_style_name in style_sheet.get_names():
                self.selected_style.add_style(
                    this_style_name,style_sheet.get_style(this_style_name))

        response = self.window.run()
        if response == RESPONSE_OK:
            try:
                self.make_report()
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))
        self.close()

    def setup_style_frame(self): pass
    def setup_report_options_frame(self): pass
    def setup_other_frames(self): pass
    def parse_style_frame(self): pass
    def parse_report_options_frame(self): pass
    def parse_other_frames(self): pass

    def doc_uses_tables(self):
        return 1

    def get_title(self):
        return _("Book Report")

    def get_header(self,name):
        return _("GRAMPS Book")

    def get_stylesheet_savefile(self):
        """Needed solely for forming sane filename for the output."""
        return "book.xml"

    def make_doc_menu(self,active=None):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        self.format_menu = BookFormatComboBox()
        self.format_menu.set(self.doc_uses_tables(),
                             self.doc_type_changed, None, active)

    def make_document(self):
        """Create a document of the type requested by the user."""
        self.doc = self.format(self.selected_style,self.paper,
            self.template_name,self.orien)

        self.rptlist = []
        newpage = 0
        for item in self.book.get_item_list():
            item.option_class.set_document(self.doc)
            item.option_class.set_newpage(newpage)
            report_class = item.get_write_item()
            obj = write_book_item(self.database,self.person,
                                  report_class,item.option_class)
            self.rptlist.append(obj)
            newpage = 1
        self.doc.open(self.target_path)
        
        if self.print_report.get_active():
            self.doc.print_requested ()

    def make_report(self):
        """The actual book report. Start it out, then go through the item list 
        and call each item's write_book_item method."""

        self.doc.init()
        for item in self.rptlist:
            item.begin_report()
            item.write_report()
        self.doc.close()

#------------------------------------------------------------------------
#
# Function to write books from command line
#
#------------------------------------------------------------------------
def cl_report(database,name,category,options_str_dict):

    clr = CommandLineReport(database,name,category,
                            BookOptions,options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    book_list = BookList('books.xml')
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
        style_list = BaseDoc.StyleSheetList(style_file,default_style)

        # Get the selected stylesheet
        style_name = item.option_class.handler.get_default_stylesheet_name()
        style_sheet = style_list.get_style_sheet(style_name)

        for this_style_name in style_sheet.get_names():
            selected_style.add_style(
                    this_style_name,style_sheet.get_style(this_style_name))

    # write report
    doc = clr.format(selected_style,clr.paper,clr.template_name,clr.orien)
    rptlist = []
    newpage = 0
    for item in book.get_item_list():
        item.option_class.set_document(doc)
        item.option_class.set_newpage(newpage)
        report_class = item.get_write_item()
        obj = write_book_item(database,clr.person,
                              report_class,item.option_class)
        rptlist.append(obj)
        newpage = 1
    doc.open(clr.option_class.get_output())
    doc.init()
    for item in rptlist:
        item.begin_report()
        item.write_report()
    doc.close()

#------------------------------------------------------------------------
#
# Generic task function for book report
#
#------------------------------------------------------------------------
def write_book_item(database,person,report_class,options_class):
    """Write the Timeline Graph using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options_class.handler.get_person_id():
            person = database.get_person_from_gramps_id(
                options_class.handler.get_person_id())
        return report_class(database,person,options_class)
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
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
    description = _("Creates a book containing several reports."),
    author_name = "Alex Roitman",
    author_email = "shura@gramps-project.org"
    )
