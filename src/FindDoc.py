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
_LATEX      = _("LaTeX")
_KWord      = _("KWord")
_RTF        = _("RTF")

_has_tables = 1
_no_tables  = 0

_paper      = 1
_template   = 0

_styles     = 1
_no_styles  = 0

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
_textdoc = []
_drawdoc = []

try:
    import OpenOfficeDoc
    _textdoc.append((_OpenOffice, _has_tables, _paper, _styles))
except:
    pass

try:
    import OpenDrawDoc
    _drawdoc.append(_OpenOffice)
except:
    pass

try:
    import AbiWordDoc
    _textdoc.append((_AbiWord, _no_tables, _paper, _styles))
except:
    pass

try:
    import PdfDoc
    _textdoc.append((_PDF, _has_tables, _paper, _styles))
except:
    pass

try:
    import PdfDrawDoc
    _drawdoc.append(_PDF)
except:
    pass

try:
    import HtmlDoc
    _textdoc.append((_HTML, _has_tables, _template, _styles))
except:
    pass

try:
    import KwordDoc
    _textdoc.append((_KWord, _no_tables, _paper, _styles))
except:
    pass

try:
    import RTFDoc
    _textdoc.append((_RTF, _has_tables, _paper, _styles))
except:
    pass

try:
    import LaTeXDoc
    _textdoc.append((_LATEX, _has_tables, _paper, _no_styles))
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
        menuitem.set_data("styles",item[3])
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
def get_draw_doc_menu(main_menu,callback=None,obj=None):

    index = 0
    myMenu = gtk.GtkMenu()
    for name in _drawdoc:
        menuitem = gtk.GtkMenuItem(name)
        menuitem.set_data("name",name)
        menuitem.set_data("obj",obj)
        if callback:
            menuitem.connect("activate",callback)
        menuitem.show()
        myMenu.append(menuitem)
        if name == Config.output_preference:
            myMenu.set_active(index)
        if callback:
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
    elif name == _LATEX:
        return LaTeXDoc.LaTeXDoc(styles,paper,orien)
    elif name == _KWord:
        return KwordDoc.KwordDoc(styles,paper,orien)
    elif name == _RTF:
        return RTFDoc.RTFDoc(styles,paper,orien)
    else:
        return HtmlDoc.HtmlDoc(styles,template)

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def make_draw_doc(styles,name,paper,orien):
    if name == _OpenOffice:
        return OpenDrawDoc.OpenDrawDoc(styles,paper,orien)
    else:
        return PdfDrawDoc.PdfDrawDoc(styles,paper,orien)

