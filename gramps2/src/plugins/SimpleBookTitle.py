# Gramps - a GTK+/GNOME based genealogy program
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

# $Id$

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import Report
import BaseDoc
import Errors
from QuestionDialog import ErrorDialog
from gettext import gettext as _
import SelectObject
import Utils
import AddMedia

import gtk

#------------------------------------------------------------------------
#
# SimpleBookTitle
#
#------------------------------------------------------------------------
class SimpleBookTitle(Report.Report):

    def __init__(self,database,
                    person,title_string,subtitle_string,object_id,image_size,
                    footer_string,doc,output,newpage=0):
        self.map = {}
        self.database = database
        self.start = person
        self.title_string = title_string
        self.object_id = object_id
        self.image_size = image_size
        self.subtitle_string = subtitle_string
        self.footer_string = footer_string
        self.doc = doc
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
            self.doc.init()
        else:
            self.standalone = 0
        self.sref_map = {}
        self.sref_index = 1
        
    def setup(self):
        pass

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

        self.doc.start_paragraph('SBT-Title')
        self.doc.write_text(self.title_string)
        self.doc.end_paragraph()

        self.doc.start_paragraph('SBT-Subtitle')
        self.doc.write_text(self.subtitle_string)
        self.doc.end_paragraph()

        if self.object_id:
            object = self.database.getObject(self.object_id)
            name = object.getPath()
            if self.image_size:
                image_size = self.image_size
            else:
                image_size = min(
                        0.8 * self.doc.get_usable_width(), 
                        0.7 * self.doc.get_usable_height() )
            self.doc.add_photo(name,'center',image_size,image_size)

        self.doc.start_paragraph('SBT-Footer')
        self.doc.write_text(self.footer_string)
        self.doc.end_paragraph()

        if self.standalone:
            self.doc.close()


def _make_default_style(default_style):
    """Make the default output style for the Simple Boot Title report."""
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(1)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set(pad=0.5)
    para.set_description(_('The style used for the title of the page.'))
    default_style.add_style("SBT-Title",para)
    
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set(pad=0.5)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set_description(_('The style used for the subtitle.'))
    default_style.add_style("SBT-Subtitle",para)

    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=10,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set(pad=0.5)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set_description(_('The style used for the footer.'))
    default_style.add_style("SBT-Footer",para)
    

#-------------------------------------------------------------------------
#
# Define pre-set image sizes
#
#-------------------------------------------------------------------------
_sizes = (
    ( _('Fit page'), 0 ),
    ( _('%d cm') % 5, 5 ),
    ( _('%d cm') % 10, 10 ),
    ( _('%d cm') % 15, 15 ),
)

#-------------------------------------------------------------------------
#
# make_paper_menu
#
#-------------------------------------------------------------------------
def make_size_menu(main_menu,def_size_index=0):

    index = 0
    myMenu = gtk.Menu()
    for size in _sizes:
        name = size[0]
        menuitem = gtk.MenuItem(name)
        menuitem.show()
        myMenu.append(menuitem)
        if index == def_size_index:
            myMenu.set_active(index)
        index = index + 1
    main_menu.set_menu(myMenu)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "simple_book_title.xml"
_style_name = "default" 

_person_id = ""
_title_string = ""
_subtitle_string = ""
_object_id = ""
_size_index = 0
_footer_string = ""

_options = ( 
    _person_id, 
    _title_string, 
    _subtitle_string, 
    _object_id, 
    _size_index, 
    _footer_string
)


#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class SimpleBookTitleDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.getPerson(self.options[0])
        else:
            self.person = person

	self.style_name = stl
        Report.BareReportDialog.__init__(self,database,self.person)

        if self.options[1]:
            self.title_string = self.options[1]
        else:
            self.title_string = _('Title of the Book')
        
        if self.options[2]:
            self.subtitle_string = self.options[2]
        else:
            self.subtitle_string = _('Subtitle of the Book')

        if self.options[3]:
            self.object_id = self.options[3]
        else:
            self.object_id = ""
        
        if self.options[4]:
            self.size_index = int(self.options[4])
        else:
            self.size_index = 0

        if self.options[5]:
            self.footer_string = self.options[5]
        else:
            import time
            dateinfo = time.localtime(time.time())
            name = self.db.getResearcher().getName()
            self.footer_string = _('Copyright %d %s') % (dateinfo[0], name)

        self.title_entry.set_text(self.title_string)
        self.subtitle_entry.set_text(self.subtitle_string)
        self.footer_entry.set_text(self.footer_string)
        self.size_menu.set_history(self.size_index)
        if self.object_id:
            object = self.db.getObject(self.object_id)
            self.obj_title.set_text(object.getDescription())
            the_type = Utils.get_mime_description(object.getMimeType())
            path = object.getPath()
            thumb_path = Utils.thumb_path(self.db.getSavePath(),object)
            pexists = os.path.exists(path)
            if pexists and os.path.exists(thumb_path):
                self.preview.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(thumb_path))
            else:
                icon_image = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(the_type))
                self.preview.set_from_pixbuf(icon_image)
            self.remove_obj_button.set_sensitive(gtk.TRUE)
            self.size_menu.set_sensitive(gtk.TRUE)

        self.new_person = None

        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Title Page"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Title Page for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def setup_center_person(self): 
        pass

    def setup_report_options_frame(self):
        self.notebook = gtk.Notebook()
        self.notebook.set_border_width(6)
        self.window.vbox.add(self.notebook)

    def add_user_options(self):
        self.title_entry = gtk.Entry()
        self.subtitle_entry = gtk.Entry()
        self.footer_entry = gtk.Entry()
        self.add_frame_option(_('Text'),_('Title'),self.title_entry)
        self.add_frame_option(_('Text'),_('Subtitle'),self.subtitle_entry)
        self.add_frame_option(_('Text'),_('Footer'),self.footer_entry)
        
        frame = gtk.Frame()
        frame.set_size_request(96,96)
        self.preview = gtk.Image()
        frame.add(self.preview)
        self.obj_title = gtk.Label('')
        self.remove_obj_button = gtk.Button(None,gtk.STOCK_REMOVE)
        self.remove_obj_button.connect('clicked',self.remove_obj)
        self.remove_obj_button.set_sensitive(gtk.FALSE)
        preview_table = gtk.Table(2,1)
        preview_table.set_row_spacings(10)
        preview_table.attach(frame,0,1,1,2,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
        preview_table.attach(self.obj_title,0,1,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)

        select_obj_button = gtk.Button(_('From gallery...'))
        select_obj_button.connect('clicked',self.select_obj)
        select_file_button = gtk.Button(_('From file...'))
        select_file_button.connect('clicked',self.select_file)
        select_table = gtk.Table(1,3)
        select_table.set_col_spacings(10)
        select_table.attach(select_obj_button,
                0,1,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
        select_table.attach(select_file_button,
                1,2,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
        select_table.attach(self.remove_obj_button,
                2,3,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)

        self.size_menu = gtk.OptionMenu()
        make_size_menu(self.size_menu)
        self.size_menu.set_sensitive(gtk.FALSE)

        self.add_frame_option(_('Image'),_('Preview'),preview_table)
        self.add_frame_option(_('Image'),_('Select'),select_table)
        self.add_frame_option(_('Image'),_('Size'),self.size_menu)

    def parse_report_options_frame(self):
        """Parse the report options frame of the dialog.  Save the user selected choices for later use."""

        # call the parent task to handle normal options
        Report.BareReportDialog.parse_report_options_frame(self)

        # get values from the widgets
        self.title_string = unicode(self.title_entry.get_text())
        self.subtitle_string = unicode(self.subtitle_entry.get_text())
        self.footer_string = unicode(self.footer_entry.get_text())
        self.size_index = self.size_menu.get_history()

    def on_cancel(self, obj):
        pass

    def remove_obj(self, obj):
        self.object_id = ""
        self.obj_title.set_text('')
        self.preview.set_from_pixbuf(None)
        self.remove_obj_button.set_sensitive(gtk.FALSE)
        self.size_menu.set_sensitive(gtk.FALSE)

    def select_obj(self, obj):
        s_o = SelectObject.SelectObject(self.db,_("Select an Object"))
        object = s_o.run()
        if object:
            self.object_id = object.getId()
        else:
            return
        self.obj_title.set_text(object.getDescription())
        the_type = Utils.get_mime_description(object.getMimeType())
        path = object.getPath()
        thumb_path = Utils.thumb_path(self.db.getSavePath(),object)
        pexists = os.path.exists(path)
        if pexists and os.path.exists(thumb_path):
            self.preview.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(thumb_path))
        else:
            icon_image = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(the_type))
            self.preview.set_from_pixbuf(icon_image)
        self.remove_obj_button.set_sensitive(gtk.TRUE)
        self.size_menu.set_sensitive(gtk.TRUE)

    def select_file(self, obj):
        a_o = AddMedia.AddMediaObject(self.db)
        object = a_o.run()
        if object:
            self.object_id = object.getId()
        else:
            return
        self.obj_title.set_text(object.getDescription())
        the_type = Utils.get_mime_description(object.getMimeType())
        path = object.getPath()
        thumb_path = Utils.thumb_path(self.db.getSavePath(),object)
        pexists = os.path.exists(path)
        if pexists and os.path.exists(thumb_path):
            self.preview.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(thumb_path))
        else:
            icon_image = gtk.gdk.pixbuf_new_from_file(Utils.find_icon(the_type))
            self.preview.set_from_pixbuf(icon_image)
        self.remove_obj_button.set_sensitive(gtk.TRUE)
        self.size_menu.set_sensitive(gtk.TRUE)

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.new_person:
            self.person = self.new_person

        self.options = ( self.person.getId(), 
                    self.title_string, self.subtitle_string, 
                    self.object_id, self.size_index, self.footer_string )
        self.style_name = self.selected_style.get_name() 
   
#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Title Page using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.getPerson(options[0])
        if options[1]:
            title_string = options[1]
        else:
            title_string = _('Title of the Book')
        if options[2]:
            subtitle_string = options[2]
        else:
            subtitle_string = _('Subtitle of the Book')
        if options[3]:
            object_id = options[3]
        else:
            object_id = ""
        if options[4]:
            size_index = int(options[4])
        else:
            size_index = 0
        size = _sizes[size_index][1]
        if options[5]:
            footer_string = options[5]
        else:
            import time
            dateinfo = time.localtime(time.time())
            name = database.getResearcher().getName()
            footer_string = _('Copyright %d %s') % (dateinfo[0], name)
        return SimpleBookTitle(database, person, 
                title_string, subtitle_string, object_id, size, 
                footer_string, doc, None, newpage )
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

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
        "+	c #847B6E",
        "@	c #B7AC9C",
        "#	c #D1D1D0",
        "$	c #EEE2D0",
        "%	c #6A655C",
        "&	c #868686",
        "*	c #F1EADF",
        "=	c #5C5854",
        "-	c #B89C73",
        ";	c #E2C8A1",
        ">	c #55524C",
        ",	c #F5EEE6",
        "'	c #4F4E4C",
        ")	c #A19C95",
        "!	c #B3966E",
        "~	c #CDC8BF",
        "{	c #F6F2ED",
        "]	c #A6A5A4",
        "^	c #413F3F",
        "/	c #D8D1C5",
        "(	c #968977",
        "_	c #BAB9B6",
        ":	c #FAFAF9",
        "<	c #BEA27B",
        "[	c #E9DAC2",
        "}	c #9D9385",
        "|	c #E4E3E3",
        "1	c #7A7062",
        "2	c #E6D3B4",
        "3	c #BAA488",
        "4	c #322E2B",
        "                                                ",
        "                                                ",
        "             (+(+++++111%1%%%%===%1             ",
        "             +______________@_@)&==1            ",
        "             +_::::::::::::::*|#_&&}>           ",
        "             &_:::::::::::::::{|#]1~}^          ",
        "             +_::::::::::::::::{|#=|~&4         ",
        "             +_::::]]]]]]]]:::::|{':|~&4        ",
        "             +_::::::::::::::::::{'::|~&4       ",
        "             +_:::::::::::::::::::'*::|~&^      ",
        "             +_:::::::::::::::::::'|*::|~}>     ",
        "             1_::::]]]]]]]]]]]]:::'~|{::|_}%    ",
        "             1_:::::::::::::::::::'..4^'=1+%1   ",
        "             +_::::]]]]]]]]]]]]:::|__])&+%=^%   ",
        "             1_::::::::::::::::::::|#__)&&+'^   ",
        "             1_::::]]]]]]]]]::::::::|#~_])&%^   ",
        "             1_::::::::::::::::::::{||#~_])14   ",
        "             1_::::]]]]]]]]]]]]]]]]]]&}#~_]+4   ",
        "             1_::::::::::::::::::{{{{||#~~@&4   ",
        "             %_::::]]]]]]]]]]]]]]]])))}(~~~&4   ",
        "             %_:::::::::::::::::{{{{{*|#/~_(4   ",
        "             %_::::]]]]]]]]]]]]]]])))))}2;/}4   ",
        "             %_:::::::::::::::{{{{{***||[#~}4   ",
        "             %_::::]]]]]]]]]])]))))))))}2/;)4   ",
        "             %_::::::::::::::{{{{{**|$$[/2~!4   ",
        "             %_::::]]]]]]]]){{{{******$$[2/}4   ",
        "             %_::::::::::::{{{{****$$$$$[2/!4   ",
        "             =_::::]]]]]]])]))))))))})}}[2/!4   ",
        "             %_:::::::::{{{{{{**|$$$$$$[[2;)4   ",
        "             =_::::]]]])]]))))))))))}}}}[22!4   ",
        "             %_::::::::{{{{{|**|$$[$[[[[[22}4   ",
        "             =_::::]]])])))))))))}}}}}}}222-4   ",
        "             =_:::::{{{{{|{*|$$$$$[[[[22222!4   ",
        "             =_::::)]])))))))))}}}}}}(}(2;2-4   ",
        "             =_:::{{{{{{***|$$$$$[[[[22222;-4   ",
        "             =_:::{])))))))))}}}}}}}(}((2;;<4   ",
        "             >_:{{{{{{**|$$$$$[[[[22222;2;;-4   ",
        "             >_{{{{)))))))}}}}}}}(!(((((;;;-4   ",
        "             >_{{{{|**|*$$$$$[[[[22222;;;;;!4   ",
        "             '_{{{{****$$$$$2[[222222;2;;;;-4   ",
        "             '@{{****$$$$$[[[2[222;;2;;;;;;!4   ",
        "             >]{******$$$[$[2[[2222;;;;;;;;!4   ",
        "             '_****$$$$[$[[[[2222;2;;;;;;;;!4   ",
        "             '@__@@@@@@@33<3<<<<<<-<-!!!!!!!4   ",
        "             44444444444444444444444444444444   ",
        "                                                ",
        "                                                ",
        "                                                "]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_book_item

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Title Page"), 
    _("Title"),
    SimpleBookTitleDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
   )
