#
# Gramps - a GTK+/GNOME based genealogy program
#
#
# Copyright (C) 2003  Donald N. Allingham
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

#
# Written by Alex Roitman, 
# largely based on the TextDoc classes by Don Allingham
#

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
import string

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
from intl import gettext as _

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
import GrampsCfg
import Plugins
import Report
import TextDoc

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
        """

        self.name = ""
        self.category = ""
        self.dialog = None
        self.write_item = None
        self.options = []
        self.style_file = ""
        self.style_name = "default"
        self.make_default_style = None
        if name:
            self.get_registered_item(name)
        
    def clear(self):
        self.name = ""
        self.category = ""
        self.dialog = None
        self.write_item = None
        self.options = []
        self.style_file = ""
        self.style_name = "default"
        self.make_default_style = None

    def get_registered_item(self,name):
        self.clear()
        for item in Plugins._bkitems:
            if item[0] == name:
                self.name = item[0]
                self.category = item[1]
                self.dialog = item[2]
                self.write_item = item[3]
                self.options = item[4]
                self.style_name = item[5]
                self.style_file = item[6]
                self.make_default_style = item[7]

    def get_name(self):
        return self.name

    def get_category(self):
        return self.category

    def get_dialog(self):
        return self.dialog

    def get_write_item(self):
        return self.write_item

    def set_options(self,options):
        self.options = options

    def get_options(self):
        return self.options

    def set_style_name(self,style_name):
        self.style_name = style_name

    def get_style_name(self):
        return self.style_name

    def get_style_file(self):
        return self.style_file

    def get_make_default_style(self):
        return self.make_default_style

#------------------------------------------------------------------------
#
# Book class
#
#------------------------------------------------------------------------
class Book:
    """
    Interface into the user's defined book -- a collection of book items.
    """

    def __init__(self,obj=None):
        """
        Creates a new empty Book.

        obj - if not None, creates the Book from the values in
              obj, instead of creating an empty Book.
        """

        self.name = ""
        self.dbname = ""
        if obj:
            self.item_list = obj.item_list
        else:
            self.item_list = []
        
    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name

    def get_dbname(self):
        return self.dbname

    def set_dbname(self,name):
        self.dbname = name

    def clear(self):
        self.item_list = []

    def append_item(self,item):
        self.item_list.append(item)

    def insert_item(self,index,item):
        self.item_list.insert(index,item)

    def pop_item(self,index):
        return self.item_list.pop(index)

    def get_item(self,index):
        return self.item_list[index]

    def set_item(self,index,item):
        self.item_list[index] = item

    def get_item_list(self):
        return self.item_list

#------------------------------------------------------------------------
#
# BookList class
#
#------------------------------------------------------------------------
class BookList:
    """
    Interface into the user's defined list of books.  
    BookList is loaded from a specified XML file if it exists.
    """

    def __init__(self,file):
        """
        Creates a new BookList from the books that may be defined in the 
        specified file.

        file - XML file that contains style definitions
        """

        self.bookmap = {}
        self.file = os.path.expanduser("~/.gramps/" + file)
        self.parse()
    
    def delete_book(self,name):
        """
        Removes a book from the list. Since each book must have a
        unique name, the name is used to delete the book.

        name - Name of the book to delete
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

        name - name associated with the desired Book.
        """
        return self.bookmap[name]

    def get_book_names(self):
        "Returns a list of all the book names in the BookList"
        return self.bookmap.keys()

    def set_book(self,name,book):
        """
        Adds or replaces a Book in the BookList. 

        name - name assocated with the Book to add or replace.
        book - definition of the Book
        """
        self.bookmap[name] = book

    def save(self):
        """
        Saves the current BookList to the associated file.
        """
        f = open(self.file,"w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write('<booklist>\n')

        for name in self.bookmap.keys():
            book = self.get_book(name)
            dbname = book.get_dbname()
            f.write('<book name="%s" database="%s">\n' % (name,dbname) )
            for item in book.get_item_list():
                f.write('  <item name="%s">\n' % item.get_name() )
                options = item.get_options()
                for opt_index in range(len(options)):
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

        booklist - BookList to be loaded from the file.
        """
        handler.ContentHandler.__init__(self)
        self.booklist = booklist
        self.b = None
        self.i = None
        self.o = None
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
            self.o.append(attrs['value'])
        elif tag == "style":
            self.s = attrs['name']

    def endElement(self,tag):
        "Overridden class that handles the start of a XML element"
        if tag == "item":
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
    Shows the list of available books. 
    Allows the user to selecta book from the list.
    """

    def __init__(self,booklist,nodelete=0):
        """
        Creates a BookListDisplay object that displays the books in BookList.

        booklist - books that are displayed
        """
        
        self.booklist = booklist
        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")
        self.xml = gtk.glade.XML(glade_file,"booklist")
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
            path = self.blist.model.get_path(iter)

    def on_booklist_ok_clicked(self,obj):
        """Return selected book. """
        store,iter = self.blist.get_selected()
        if iter:
            data = self.blist.get_data(iter,[0])
            self.selection = self.booklist.get_book(data[0])
        self.booklist.save()

    def on_booklist_delete_clicked(self,obj):
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

    def __init__(self,db,person):
        self.db = db
        self.person = person
        self.file = "books.xml"

        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")

        self.xml = gtk.glade.XML(glade_file,"top")
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
        self.avail_tree.connect('button-press-event',self.av_double_click)
        self.book_tree.connect('button-press-event',self.bk_double_click)

        title_label = self.xml.get_widget('title')
        Utils.set_titles(self.top,title_label,_('Book Report'))

        self.name_entry = self.xml.get_widget("name_entry")
        self.name_entry.set_text('New Book')

        avail_label = self.xml.get_widget('avail_label')
        avail_label.set_text("<b>%s</b>" % "Available items")
        avail_label.set_use_markup(gtk.TRUE)
        book_label = self.xml.get_widget('book_label')
        book_label.set_text("<b>%s</b>" % "Current book")
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
        """Draw the list with the selections available for the book."""

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
        if book.get_dbname() == self.db.getSavePath():
            same_db = 1
        else:
            same_db = 0
            WarningDialog(_('Different database'), _(
                'This book was created with the references to database %s.\n'
                'This makes references to the central person saved in the book invalid.\n\n' 
                'Therefore, the central person for each item is being set ' 
                'to the default person of the currently opened database.' )
                % book.get_dbname() )
            
        self.book.clear()
        self.bk_model.clear()
        for saved_item in book.get_item_list():
            name = saved_item.get_name()
            item = BookItem(name)
            options = saved_item.get_options()
            if not same_db or not options[0]:
                options[0] = self.person.getId()
            item.set_options(options)
            item.set_style_name(saved_item.get_style_name())
            self.book.append_item(item)
	    
            data = [ item.get_name(), item.get_category() ]
            pname = self.db.getPerson(options[0])
            data.append(pname.getPrimaryName().getRegularName())
            self.bk_model.add(data)
            

    def on_add_clicked(self,obj):
        store,iter = self.av_model.get_selected()
        if not iter:
            return
	data = self.av_model.get_data(iter,range(self.av_ncols))
        data.append(self.person.getPrimaryName().getRegularName())
        self.bk_model.add(data)
        item = BookItem(data[0])
        options = item.get_options()
        if not options[0]:
            options[0] = self.person.getId()
            item.set_options(options)
        self.book.append_item(item)

    def on_remove_clicked(self,obj):
        store,iter = self.bk_model.get_selected()
        if not iter:
            return
        row = self.bk_model.get_selected_row()
        self.book.pop_item(row)
        self.bk_model.remove(iter)

    def on_clear_clicked(self,obj):
        self.bk_model.clear()
        self.book.clear()

    def on_up_clicked(self,obj):
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
        if opt_dlg.person:
            self.bk_model.model.set_value(iter,2,
                opt_dlg.person.getPrimaryName().getRegularName())
        item.set_options(opt_dlg.options)
        item.set_style_name(opt_dlg.style_name)
        self.book.set_item(row,item)

    def bk_double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_setup_clicked(obj)

    def av_double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_add_clicked(obj)

    def on_book_ok_clicked(self,obj): 
        item_list = self.book.item_list
        if item_list:
            BookReportDialog(self.db,self.person,self.book)
        self.top.destroy()

    def on_save_clicked(self,obj):
        self.book_list = BookList(self.file)
        name = self.name_entry.get_text()
        self.book.set_name(name)
        self.book.set_dbname(self.db.getSavePath())
        self.book_list.set_book(name,self.book)
        self.book_list.save()

    def on_open_clicked(self,obj):
        self.book_list = BookList(self.file)
        booklistdisplay = BookListDisplay(self.book_list,1)
        booklistdisplay.top.destroy()
        book = booklistdisplay.selection
        if book:
            self.open_book(book)

    def on_edit_clicked(self,obj):
        self.book_list = BookList(self.file)
        booklistdisplay = BookListDisplay(self.book_list)
        booklistdisplay.top.destroy()

#------------------------------------------------------------------------
#
# The final dialog - paper, format, target, etc. 
#
#------------------------------------------------------------------------
class BookReportDialog(Report.ReportDialog):
    def __init__(self,database,person,book):
        import TextDoc
        Report.BareReportDialog.__init__(self,database,person)
        self.book = book
        self.database = database 
        self.person = person
        
        # dirty hack to use the style of the first item for the whole book
        for item in self.book.get_item_list():
            name = item.get_name()
            item = BookItem(name)
            style_file = item.get_style_file()
            make_default_style = item.get_make_default_style()
            self.default_style = TextDoc.StyleSheet()
            make_default_style(self.default_style)
            style_list = TextDoc.StyleSheetList(style_file,self.default_style)
            style_name = item.get_style_name()
            self.selected_style = style_list.get_style_sheet(style_name)
            return

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

    def make_doc_menu(self):
        """Build a menu of document types that are appropriate for
        this text report.  This menu will be generated based upon
        whether the document requires table support, etc."""
        Plugins.get_text_doc_menu(self.format_menu, self.doc_uses_tables(),
                                  self.doc_type_changed)

    def make_document(self):
        """Create a document of the type requested by the user."""
        self.doc = self.format(self.selected_style,self.paper,
            self.template_name,self.orien)
        self.doc.open(self.target_path)

    def make_report(self):
        """The actual book report. Start it out, then go through the item list 
        and call each item's write_book_item method."""
        self.doc.start_paragraph("Title")
        title = _("Book Report")
        self.doc.write_text(title)
        self.doc.end_paragraph()
        first = 1
        for item in self.book.get_item_list():
            write_book_item = item.get_write_item()
            options = item.get_options()
            if write_book_item:
                if first:
                    first = 0
                newpage = not first
                write_book_item(self.database,self.person,
                    self.doc,options,newpage)

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
def get_xpm_image():
    return [
        "48 48 33 1",
        " 	c None",
        ".	c #1A1A1A",
        "+	c #6A665E",
        "@	c #A6A6A6",
        "#	c #BABAB6",
        "$	c #D2D2D2",
        "%	c #EDE2D2",
        "&	c #7A7262",
        "*	c #F1EADF",
        "=	c #867A6E",
        "-	c #56524E",
        ";	c #868686",
        ">	c #E2CAA2",
        ",	c #F2EEE2",
        "'	c #4E4E4E",
        ")	c #B2966E",
        "!	c #FAFAFA",
        "~	c #A29E96",
        "{	c #BEA27A",
        "]	c #CECABE",
        "^	c #968A76",
        "/	c #DAD2C6",
        "(	c #423E3E",
        "_	c #BA9E72",
        ":	c #B7AC9A",
        "<	c #E9DAC3",
        "[	c #E6E2E2",
        "}	c #322E2A",
        "|	c #9E9286",
        "1	c #E6D2B6",
        "2	c #F2EEE9",
        "3	c #5E5A56",
        "4	c #F6F2EE",
        "                                                ",
        "                                                ",
        "             ^=^=====&&&+&++++333+&             ",
        "             =##############:#:~;33&            ",
        "             =#!!!!!!!!!!!!!!*[$#;;|-           ",
        "             ;#!!!!!!!!!!!!!!!2[$@&]|(          ",
        "             =#!!!!!!!!!!!!!!!!2[$-[];}         ",
        "             =#!!!!@@@@@@@@!!!!![4'![];}        ",
        "             =#!!!!!!4!!4!!!!!!!!4'!![];}       ",
        "             =#!!!!!!!!!!!!!!!!!!!'*!![];(      ",
        "             =#!!!!!!!!!!!!!!!!!!!'[*!![]|-     ",
        "             &#!!!!@@~@@@~@@~@@@@@'][4!![#|+    ",
        "             &#!4!!!!!!!!!!!!!4!!!'..}('3&=+&   ",
        "             =#!!!!@@@@@@@@@@@@@@@@##@~;=+3(+   ",
        "             &#!!!!!!!!!!!!!!!!!!!![$##~;;='(   ",
        "             &#!!!!@@@@@~@@@~@@@@~@@@@@#~~;+(   ",
        "             &#!!!!!!!!!!!!!!!!!!!!444[]#@~&}   ",
        "             &#!!!!!!!!!!!!!!!!!!4442[[$]#@=}   ",
        "             &#!!!!!!!!!!!!!!!!!!4444[[$]]:;}   ",
        "             +#!!!!@~@@@@@@@@~@@@@@~~~|;]]];}   ",
        "             +#!!!!!!!!!!!!!!!!!44444,[$/]:^}   ",
        "             +#!!!!@@@~@@@@@@@@~@~~~~~~|1>$|}   ",
        "             +#!!!!!!!!!!!!!!!44442[*%[[<$]|}   ",
        "             +#!!!!@@@@~@@@@~~@~~~~~~~~|1/>~}   ",
        "             +#!!!!!!!!!!!!!!44444**[%%</1])}   ",
        "             +#!!!!!!!!!!!!!4422******%%<1/|}   ",
        "             +#!!!!!!!!!!!!!!4,*,**2***%<1/)}   ",
        "             3#!!!!@@@@@~,442,*,*,2**,,[<1/)}   ",
        "             +#!!!!!!4!!444444**[%%%%%%<<1>~}   ",
        "             3#!!!!@@4*@@@~~~~~~~~~~||||<11)}   ",
        "             +#4!!4444444,24[[*[<%<%<<<<<11|}   ",
        "             3#!!!44,,,@~~~~~~~~~|||||||111_}   ",
        "             3#!!!!!44444[4[[%%%%%<<<<11111)}   ",
        "             3#!!!!~@,*~~~~~~~~||||||^|^1>1_}   ",
        "             3#!!!444442%**[%<%%%<<<<11111>_}   ",
        "             3#!!!4***[~~~~~~|||||||^|^^1>>{}   ",
        "             -#!444444**[%<%%%<<<<11111>1>>_}   ",
        "             -#4444~~[[~~~|||||||^)^^^^^>>>_}   ",
        "             -#4444[**[%%%%%%<<<<11111>>>>>)}   ",
        "             '#4444****%%%%%<<<111<11>>>>>>_}   ",
        "             ':44****%%%%%<<<1<1<1>>1>>>>>>)}   ",
        "             -@4******%%%<%<1<<1111>>>>>>>>)}   ",
        "             '#****%%%%<%<<<<1<11>1>>>>>>>>)}   ",
        "             ':##:::::::{{{{{{__{___))^)))))}   ",
        "             }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}   ",
        "                                                ",
        "                                                ",
        "                                                "]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Book Report"),
    category=_("Text Reports"),
    status=(_("Unstable")),
    description=_("Creates a book containg several reports."),
    xpm=get_xpm_image(),
    author_name="Alex Roitman",
    author_email="shura@alex.neuro.umn.edu"
    )
