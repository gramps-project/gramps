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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
import string

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

#-------------------------------------------------------------------------
#
# Book creation dialog class
#
#-------------------------------------------------------------------------
class BookReportSelector:

    def __init__(self,db,person):
        self.db = db
        self.person = person

        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"book.glade")

        self.xml = gtk.glade.XML(glade_file,"top")
        self.top = self.xml.get_widget("top")
    
        if person:
            self.default_name = person.getPrimaryName().getSurname().upper()
        else:
            self.default_name = ""

        self.xml.signal_autoconnect({
            "on_add_clicked"        : self.on_add_clicked,
            "on_remove_clicked"     : self.on_remove_clicked,
            "on_up_clicked"         : self.on_up_clicked,
            "on_down_clicked"       : self.on_down_clicked,
            "on_setup_clicked"      : self.on_setup_clicked,
            "on_clear_clicked"      : self.on_clear_clicked,
            "on_book_ok_clicked"    : self.on_book_ok_clicked,
            "destroy_passed_object" : self.close
            })

        self.avail_tree = self.xml.get_widget("avail_tree")
        self.book_tree = self.xml.get_widget("book_tree")
        self.avail_tree.connect('button-press-event',self.av_double_click)
        self.book_tree.connect('button-press-event',self.bk_double_click)

        title_label = self.xml.get_widget('title')
        Utils.set_titles(self.top,title_label,_('Book Report'))

        avail_label = self.xml.get_widget('avail_label')
        avail_label.set_text("<b>%s</b>" % "Available items")
        avail_label.set_use_markup(gtk.TRUE)
        book_label = self.xml.get_widget('book_label')
        book_label.set_text("<b>%s</b>" % "Current book")
        book_label.set_use_markup(gtk.TRUE)

        self.item_storage = {}
        self.max_key = 0

        av_titles = [(_('Name'),2,150),(_('Type'),1,50)]
        bk_titles = [(_('Item name'),-1,150),(_('Type'),1,50),('',-1,0)] #,('',-1,0)
	
	self.av_ncols = len(av_titles)
	self.bk_ncols = len(bk_titles)

        self.av_model = ListModel.ListModel(self.avail_tree,av_titles)
        self.bk_model = ListModel.ListModel(self.book_tree,bk_titles)
        self.draw_avail_list()

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

    def on_add_clicked(self,obj):
        store,iter = self.av_model.get_selected()
        if not iter:
            return
	data = self.av_model.get_data(iter,range(self.av_ncols))
        self.max_key = self.max_key + 1
        newkey = str(self.max_key)
        data.append(newkey)
        self.bk_model.add(data)
        for book_item in Plugins._bkitems:
            if book_item[0] == data[0]:
                self.item_storage[newkey] = list(book_item)

    def on_remove_clicked(self,obj):
        store,iter = self.bk_model.get_selected()
        if not iter:
            return
	data = self.bk_model.get_data(iter,range(self.bk_ncols))
        key = data[2]
        del self.item_storage[key]
        self.bk_model.remove(iter)

    def on_clear_clicked(self,obj):
        self.bk_model.clear()
        self.item_storage.clear()

    def on_up_clicked(self,obj):
        row = self.bk_model.get_selected_row()
        if not row or row == -1:
            return
        store,iter = self.bk_model.get_selected()
	data = self.bk_model.get_data(iter,range(self.bk_ncols))
        self.bk_model.remove(iter)
        self.bk_model.insert(row-1,data,None,1)

    def on_down_clicked(self,obj):
        row = self.bk_model.get_selected_row()
        if row + 1 >= self.bk_model.count or row == -1:
	    return
	store,iter = self.bk_model.get_selected()
	data = self.bk_model.get_data(iter,range(self.bk_ncols))
        self.bk_model.remove(iter)
        self.bk_model.insert(row+1,data,None,1)

    def on_setup_clicked(self,obj):
        store,iter = self.bk_model.get_selected()
        if not iter:
            return
	data = self.bk_model.get_data(iter,range(self.bk_ncols))
        key = data[2]
        book_item = self.item_storage[key]
        options_dialog =  book_item[2]
        get_opt = book_item[4]
        get_stl = book_item[5] 
        opt_dlg = options_dialog(self.db,self.person,get_opt,get_stl)
        book_item[4] = opt_dlg.get_options
        book_item[5] = opt_dlg.get_style
        self.item_storage[key] = book_item
        self.person = opt_dlg.person
        #print opt_dlg.person.getPrimaryName().getRegularName()

    def bk_double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_setup_clicked(obj)

    def av_double_click(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.on_add_clicked(obj)

    def on_book_ok_clicked(self,obj): 
        if self.bk_model.count:
            item_list = []
            for row in range(self.bk_model.count):
                self.bk_model.select_row(row)
                store,iter = self.bk_model.get_selected()
                data = self.bk_model.get_data(iter,range(self.bk_ncols))
                key = data[2]
                book_item = self.item_storage[key]
                item_list.append(book_item)
            BookReportDialog(self.db,self.person,item_list)
        self.top.destroy()

#------------------------------------------------------------------------
#
# The final dialog - paper, format, target, etc. 
#
#------------------------------------------------------------------------
class BookReportDialog(Report.ReportDialog):
    def __init__(self,database,person,item_list):
        Report.BareReportDialog.__init__(self,database,person)
        self.item_list = item_list
        book_item = item_list[0]
        get_style = book_item[5]
        self.selected_style = get_style()
        self.database = database 
        self.person = person

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
        return _("Book Report")

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
        """Create the contents of the report.  This is a simple
        default implementation suitable for testing.  Is should be
        overridden to produce a real report."""
        self.doc.start_paragraph("Title")
        title = _("Book Report")
        self.doc.write_text(title)
        self.doc.end_paragraph()
        first = 1
        for book_item in self.item_list:
            write_book_item = book_item[3]
            get_options = book_item[4]
            item_options = get_options()
            if write_book_item:
                if first:
                    first = 0
                newpage = not first
                write_book_item(self.database,self.person,
                    self.doc,item_options,newpage)

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

