#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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

"""
The DateEdit interface provides visual feedback to the user via a pixamp
to indicate if the assocated GtkEntry box contains a valid date. Green
means complete and valid date. Yellow means a valid, but incomplete date.
Red means that the date is not valid, and will be viewed as a text string
instead of a date.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import GdkImlib

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Date

#-------------------------------------------------------------------------
#
# DateEdit
#
#-------------------------------------------------------------------------
class DateEdit:
    """Class that associates a pixmap with a text widget, providing visual
    feedback that indicates if the text widget contains a valid date"""
    
    good = GdkImlib.create_image_from_xpm([
        "10 10 24 1",
        " 	c None",
        ".	c #0EB40E",
        "+	c #11A711",
        "@	c #11A211",
        "#	c #0DA10D",
        "$	c #09CB09",
        "%	c #0BCC0B",
        "&	c #08CD08",
        "*	c #098609",
        "=	c #05E705",
        "-	c #02F502",
        ";	c #07E007",
        ">	c #0A9D0A",
        ",	c #01F901",
        "'	c #00FF00",
        ")	c #01F801",
        "!	c #05E605",
        "~	c #0AC40A",
        "{	c #0AC30A",
        "]	c #000000",
        "^	c #099209",
        "/	c #08CB08",
        "(	c #033403",
        "_	c #098509",
        " .+++@#   ",
        ".$%%%%&*  ",
        "+%===-;>  ",
        "+%=,')!~  ",
        "+%='')!{] ",
        "@%-))-;^] ",
        "#&;!!;/(  ",
        " _>~{^(]  ",
        "    ]]    ",
        "          "])
    
    bad = GdkImlib.create_image_from_xpm([
        "10 10 21 1",
        " 	c None",
        ".	c #A21818",
        "+	c #A31818",
        "@	c #9A1717",
        "#	c #C80E0E",
        "$	c #C90F0F",
        "%	c #CA0C0C",
        "&	c #E60606",
        "*	c #F40202",
        "=	c #DE0909",
        "-	c #8F0D0D",
        ";	c #F90101",
        ">	c #FF0000",
        ",	c #F80101",
        "'	c #E50707",
        ")	c #C20E0E",
        "!	c #C10E0E",
        "~	c #000000",
        "{	c #810C0C",
        "]	c #C80C0C",
        "^	c #130202",
        "  .++@    ",
        " #$$$$%   ",
        ".$&&&*=-  ",
        "+$&;>,')  ",
        "+$&>>,'!~ ",
        "@$*,,*={~ ",
        " %=''=]^  ",
        "  -)!{^~  ",
        "    ~~    ",
        "          "])
    
    caution = GdkImlib.create_image_from_xpm([
        "10 10 21 1",
        " 	c None",
        ".	c #B0AF28",
        "+	c #B2B028",
        "@	c #A9A726",
        "#	c #D1D017",
        "$	c #D2D118",
        "%	c #D2D114",
        "&	c #EAEA0B",
        "*	c #F6F604",
        "=	c #E3E30F",
        "-	c #979615",
        ";	c #F9F902",
        ">	c #FFFF00",
        ",	c #F9F903",
        "'	c #E9E90B",
        ")	c #CACA18",
        "!	c #C9C918",
        "~	c #000000",
        "{	c #898813",
        "]	c #CFCF14",
        "^	c #151504",
        "  .++@    ",
        " #$$$$%   ",
        ".$&&&*=-  ",
        "+$&;>,')  ",
        "+$&>>,'!~ ",
        "@$*,,*={~ ",
        " %=''=]^  ",
        "  -)!{^~  ",
        "    ~~    ",
        "          "])
    
    def __init__(self,text_obj,pixmap_obj):
        """Creates a connection between the text_obj and the pixmap_obj"""
        
        self.text_obj = text_obj
        self.pixmap_obj = pixmap_obj
        self.checkval = Date.Date()
        self.text_obj.connect('focus-out-event',self.check)
        self.check(None,None)

    def check(self,obj,val):
        """Called with the text box loses focus. If the string contains a
        valid date, sets the appropriate pixmap"""

        text = self.text_obj.get_text()
        self.checkval.set(text)
        if not self.checkval.isValid():
            self.pixmap_obj.load_imlib(DateEdit.bad)
        elif self.checkval.getIncomplete():
            self.pixmap_obj.load_imlib(DateEdit.caution)
        else:
            self.pixmap_obj.load_imlib(DateEdit.good)
            
        
