#
# Gramps - a GTK+/GNOME based genealogy program
#
#
# Copyright (C) 2003-2004  Donald N. Allingham
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

#
# Written by Alex Roitman, 
# largely based on the BaseDoc classes by Don Allingham
#

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os

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
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
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
import Plugins
import Report
import BaseDoc

from QuestionDialog import WarningDialog
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

        self.name = ""
        self.category = ""
        self.dialog = None
        self.write_item = None
        self.options = []
        self.style_file = ""
        self.style_name = "default"
        self.make_default_style = None

    def get_registered_item(self,name):
        """ 
        Retrieve the item from the book item registry.
        
        name:   a name used for lookup.
        """

        self.clear()
        for item in Plugins._bkitems:
            if item[0] == name:
                self.name = item[0]
                self.category = item[1]
                self.dialog = item[2]
                self.write_item = item[3]
                self.options = list(item[4])
                self.style_name = item[5]
                self.style_file = item[6]
                self.make_default_style = item[7]

    def get_name(self):
        """
        Returns the name of the item.
        """
        return self.name

    def get_category(self):
        """
        Returns the category of the item.
        """
        return self.category

    def get_dialog(self):
        """
        Returns the callable cofigurator dialog.
        """
        return self.dialog

    def get_write_item(self):
        """
        Returns the report-writing function of the item.
        """
        return self.write_item

    def set_options(self,options):
        """
        Sets the options for the item.
        
        options:    list of options to set.
        """
        self.options = options

    def get_options(self):
        """
        Returns the list of options for the item.
        """
        return self.options

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

    def __init__(self,file):
        """
        Creates a new BookList from the books that may be defined in the 
        specified file.

        file:   XML file that contains book items definitions
        """

        self.bookmap = {}
        self.file = os.path.expanduser("~/.gramps/" + file)
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
            f.write('<book name="%s" database="%s">\n' % (name,dbname) )
            for item in book.get_item_list():
                f.write('  <item name="%s">\n' % item.get_name() )
                options = item.get_options()
                for opt_index in range(len(options)):
                    if type(options[opt_index]) == type([]):
                        f.write('    <option number="%d" value="" length="%d">\n' % (
                                opt_index, len(options[opt_index]) ) )
                        for list_index in range(len(options[opt_index])):
                            f.write('      <listitem number="%d" value="%s"/>\n' % (
                                    list_index, options[opt_index][list_index]) )
                        f.write('    </option>\n')
                    else:
                        f.write('    <option number="%d" value="%s"/>\n' % (
                                opt_index,options[opt_index]) )
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
            p.setContentHandler(BookParser(self))
            p.parse('file://' + self.file)
        except (IOError,OSError,SAXParseException):
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
        self.an_o = None
        self.s = None
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
            self.o = []
        elif tag == "option":
            if attrs.has_key('length'):
                self.an_o = []
            else:
                self.an_o = attrs['value']
        elif tag == "listitem":
            self.an_o.append(attrs['value'])
        elif tag == "style":
            self.s = attrs['name']

    def endElement(self,tag):
        "Overridden class that handles the end of a XML element"
        if tag == "option":
            self.o.append(self.an_o)
        elif tag == "item":
            self.i.set_options(self.o)
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

    def __init__(self,booklist,nodelete=0):
        """
        Creates a BookListDisplay object that displays the books in BookList.

        booklist:   books that are displayed
        nodelete:   if not 0 then the Delete button is hidden
        """
        
        self.booklist = booklist
        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")
        self.xml = gtk.glade.XML(glade_file,"booklist","gramps")
        self.top = self.xml.get_widget('booklist')

        Utils.set_titles(self.top,
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
        title_label.set_use_markup(gtk.TRUE)
        
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
            iter = self.blist.add([name])
        if iter:
            self.blist.selection.select_iter(iter)

    def on_booklist_ok_clicked(self,obj):
        """Returns selected book. Saves the current list into xml file."""
        store,iter = self.blist.get_selected()
        if iter:
            data = self.blist.get_data(iter,[0])
            self.selection = self.booklist.get_book(data[0])
        self.booklist.save()

    def on_booklist_delete_clicked(self,obj):
        """
        Deletes selected book from the list.
        
        This change is not final. OK button has to be clicked to save the list.
        """
        store,iter = self.blist.get_selected()
        if not iter:
            return
        data = self.blist.get_data(iter,[0])
        self.booklist.delete_book(data[0])
        self.blist.remove(iter)
        self.top.run()

    def on_booklist_cancel_clicked(self,obj):
        pass

#-------------------------------------------------------------------------
#
# Book creation dialog 
#
#-------------------------------------------------------------------------
class BookReportSelector:
    """
    Interface into a dialog setting up the book. 

    Allows the user to add/remove/reorder/setup items for the current book
    and to clear/load/save/edit whole books.
    """

    def __init__(self,db,person):
        self.db = db
        self.person = person
        self.file = "books.xml"

        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")

        self.xml = gtk.glade.XML(glade_file,"top","gramps")
        self.top = self.xml.get_widget("top")
    
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

        title_label = self.xml.get_widget('title')
        Utils.set_titles(self.top,title_label,_('Book Report'))

        self.name_entry = self.xml.get_widget("name_entry")
        self.name_entry.set_text(_('New Book'))

        avail_label = self.xml.get_widget('avail_label')
        avail_label.set_text("<b>%s</b>" % _("_Available items"))
        avail_label.set_use_markup(gtk.TRUE)
        avail_label.set_use_underline(gtk.TRUE)
        book_label = self.xml.get_widget('book_label')
        book_label.set_text("<b>%s</b>" % _("Current _book"))
        book_label.set_use_underline(gtk.TRUE)
        book_label.set_use_markup(gtk.TRUE)

        av_titles = [(_('Name'),0,150),(_('Type'),1,50)]
        bk_titles = [(_('Item name'),-1,150),(_('Type'),-1,50),
            (_('Center person'),-1,50)]
        
        self.av_ncols = len(av_titles)
        self.bk_ncols = len(bk_titles)

        self.av_model = ListModel.ListModel(self.avail_tree,av_titles)
        self.bk_model = ListModel.ListModel(self.book_tree,bk_titles)
        self.draw_avail_list()

        self.book = Book()

    def close(self,obj):
        self.top.destroy()

    def draw_avail_list(self):
        """
        Draw the list with the selections available for the book.
        
        The selections are read from the book item registry.
        """

        if not Plugins._bkitems:
            return

        for book_item in Plugins._bkitems:
            data = [ book_item[0], book_item[1] ] 
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
                'This book was created with the references to database %s.\n\n'
                'This makes references to the central person saved in the book invalid.\n\n' 
                'Therefore, the central person for each item is being set ' 
                'to the active person of the currently opened database.' )
                % book.get_dbname() )
            
        self.book.clear()
        self.bk_model.clear()
        for saved_item in book.get_item_list():
            name = saved_item.get_name()
            item = BookItem(name)
            options = saved_item.get_options()
            if not same_db or not options[0]:
                options[0] = self.person.get_handle()
            item.set_options(options)
            item.set_style_name(saved_item.get_style_name())
            self.book.append_item(item)
            
            data = [ item.get_name(), item.get_category() ]
            if data[1] == _("Title"):
                data.append(_("Not Applicable"))
            else:
                pname = self.db.try_to_find_person_from_handle(options[0])
                data.append(pname.get_primary_name().get_regular_name())
            self.bk_model.add(data)

    def on_add_clicked(self,obj):
        """
        Add an item to the current selections. 
        
        Use the selected available item to get the item's name in the registry.
        """
        store,iter = self.av_model.get_selected()
        if not iter:
            return
        data = self.av_model.get_data(iter,range(self.av_ncols))
        if data[1] == _("Title"):
            data.append(_("Not Applicable"))
        else:
            data.append(self.person.get_primary_name().get_regular_name())
        self.bk_model.add(data)
        item = BookItem(data[0])
        options = item.get_options()
        if not options[0]:
            options[0] = self.person.get_handle()
            item.set_options(options)
        self.book.append_item(item)

    def on_remove_clicked(self,obj):
        """
        Remove the item from the current list of selections.
        """
        store,iter = self.bk_model.get_selected()
        if not iter:
            return
        row = self.bk_model.get_selected_row()
        self.book.pop_item(row)
        self.bk_model.remove(iter)

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
        store,iter = self.bk_model.get_selected()
        data = self.bk_model.get_data(iter,range(self.bk_ncols))
        self.bk_model.remove(iter)
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
        store,iter = self.bk_model.get_selected()
        data = self.bk_model.get_data(iter,range(self.bk_ncols))
        self.bk_model.remove(iter)
        self.bk_model.insert(row+1,data,None,1)
        item = self.book.pop_item(row)
        self.book.insert_item(row+1,item)

    def on_setup_clicked(self,obj):
        """
        Configure currently selected item.
        """
        store,iter = self.bk_model.get_selected()
        if not iter:
            return
        data = self.bk_model.get_data(iter,range(self.bk_ncols))
        row = self.bk_model.get_selected_row()
        item = self.book.get_item(row)
        options_dialog = item.get_dialog()
        options = item.get_options()
        style_name = item.get_style_name() 
        opt_dlg = options_dialog(self.db,self.person,options,style_name)
        opt_dlg.window.destroy()
        if opt_dlg.person and data[1] != _("Title"): 
            self.bk_model.model.set_value(iter,2,
                opt_dlg.person.get_primary_name().get_regular_name())
        item.set_options(opt_dlg.options)
        item.set_style_name(opt_dlg.style_name)
        self.book.set_item(row,item)

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
        
        store,iter = self.bk_model.get_selected()
        if iter:
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
        
        store,iter = self.av_model.get_selected()
        if iter:
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
            BookReportDialog(self.db,self.person,self.book)
        self.top.destroy()

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
        booklistdisplay = BookListDisplay(self.book_list,1)
        booklistdisplay.top.destroy()
        book = booklistdisplay.selection
        if book:
            self.open_book(book)

    def on_edit_clicked(self,obj):
        """
        Run the BookListDisplay dialog to present the choice of books to delete. 
        """
        self.book_list = BookList(self.file)
        booklistdisplay = BookListDisplay(self.book_list)
        booklistdisplay.top.destroy()

#------------------------------------------------------------------------
#
# The final dialog - paper, format, target, etc. 
#
#------------------------------------------------------------------------
class BookReportDialog(Report.ReportDialog):
    """
    A usual Report.Dialog subclass. 
    
    Creates a dialog selecting target, format, and paper/HTML options.
    """

    def __init__(self,database,person,book):
        Report.BareReportDialog.__init__(self,database,person)
        self.book = book
        self.database = database 
        self.person = person
        self.selected_style = BaseDoc.StyleSheet()

        for item in self.book.get_item_list():
            # Set up default style
            default_style = BaseDoc.StyleSheet()
            make_default_style = item.get_make_default_style()
            make_default_style(default_style)

            # Read all style sheets available for this item
            style_file = item.get_style_file()
            style_list = BaseDoc.StyleSheetList(style_file,default_style)

            # Get the selected stylesheet
            style_name = item.get_style_name()
            style_sheet = style_list.get_style_sheet(style_name)

            for this_style_name in style_sheet.get_names():
                self.selected_style.add_style(
                    this_style_name,style_sheet.get_style(this_style_name))

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

    def make_doc_menu(self):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        Plugins.get_book_menu(self.format_menu, self.doc_uses_tables(),
                              self.doc_type_changed)

    def make_document(self):
        """Create a document of the type requested by the user."""
        self.doc = self.format(self.selected_style,self.paper,
            self.template_name,self.orien)

        self.rptlist = []
        newpage = 0
        for item in self.book.get_item_list():
            write_book_item = item.get_write_item()
            options = item.get_options()
            if write_book_item:
                obj = write_book_item(self.database,self.person,
                        self.doc,options,newpage)
                self.rptlist.append(obj)
                newpage = 1
        self.doc.open(self.target_path)

    def make_report(self):
        """The actual book report. Start it out, then go through the item list 
        and call each item's write_book_item method."""

        self.doc.init()
        for item in self.rptlist:
            item.write_report()
        self.doc.close()

#------------------------------------------------------------------------
#
# Function to register the overall book report
#
#------------------------------------------------------------------------
def report(database,person):
    BookReportSelector(database,person)
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

Plugins.register_report(
    report,
    _("Book Report"),
    category=_("Books"),
    status=(_("Unstable")),
    description=_("Creates a book containing several reports."),
    author_name="Alex Roitman",
    author_email="shura@alex.neuro.umn.edu"
    )
