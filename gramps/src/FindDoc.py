#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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
# 
#
#-------------------------------------------------------------------------
from TextDoc import *
from DrawDoc import *
import gtk
import Config
import intl
_ = intl.gettext

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
_OpenOffice = _("OpenOffice")
_AbiWord    = _("AbiWord")
_PDF        = _("PDF")
_HTML       = _("HTML")

_has_tables = 1
_no_tables  = 0

_paper      = 1
_template   = 0

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
_textdoc = []
_drawdoc = []

try:
    import OpenOfficeDoc
    _textdoc.append((_OpenOffice, _has_tables, _paper))
except:
    pass

try:
    import OpenDrawDoc
    _drawdoc.append(_OpenOffice)
except:
    pass

try:
    import AbiWordDoc
    _textdoc.append((_AbiWord, _no_tables, _paper))
except:
    pass

try:
    import PdfDoc
    _textdoc.append((_PDF, _has_tables, _paper))
except:
    pass

try:
    import PdfDrawDoc
    _drawdoc.append(_PDF)
except:
    pass

try:
    import HtmlDoc
    _textdoc.append((_HTML, _has_tables, _template))
except:
    pass

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_text_doc_menu(main_menu,tables,callback,obj=None):

    index = 0
    myMenu = gtk.GtkMenu()
    for item in _textdoc:
        if tables and item[1] == 0:
            continue
        name = item[0]
        menuitem = gtk.GtkMenuItem(name)
        menuitem.set_data("name",name)
        menuitem.set_data("paper",item[2])
        menuitem.set_data("obj",obj)
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == Config.output_preference:
            myMenu.set_active(index)
            callback(menuitem)
        index = index + 1
    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def get_draw_doc_menu(main_menu,callback,obj=None):

    index = 0
    myMenu = gtk.GtkMenu()
    for item in _textdoc:
        if tables and item[1] == 0:
            continue
        name = item[0]
        menuitem = gtk.GtkMenuItem(name)
        menuitem.set_data("name",name)
        menuitem.set_data("obj",obj)
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == Config.output_preference:
            myMenu.set_active(index)
            callback(menuitem)
        index = index + 1
    main_menu.set_menu(myMenu)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def make_text_doc(styles,name,paper,orien,template):
    if name == _OpenOffice:
        return OpenOfficeDoc.OpenOfficeDoc(styles,paper,orien)
    elif name == _AbiWord:
        return AbiWordDoc.AbiWordDoc(styles,paper,orien)
    elif name == _PDF:
        return PdfDoc.PdfDoc(styles,paper,orien)
    else:
        return HtmlDoc.HtmlDoc(styles,template)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def make_draw_doc(name,paper,orien):
    if name == _OpenOffice:
        return OpenDrawDoc.OpenDrawDoc(paper,orien)
    else:
        return PdfDrawDoc.PdfDrawDoc(paper,orien)

