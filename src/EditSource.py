#! /usr/bin/python -O
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
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import string
import utils

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gtk import *
from gnome.ui import *
import gnome.mime

import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import intl
import const
import utils
import Config
from RelLib import *
import RelImage

_ = intl.gettext

class EditSource:

    def __init__(self,source,db,func):
        self.source = source
        self.db = db
        self.callback = func

        self.top_window = libglade.GladeXML(const.gladeFile,"sourceEditor")
        self.title = self.top_window.get_widget("source_title")
        self.author = self.top_window.get_widget("author")
        self.pubinfo = self.top_window.get_widget("pubinfo")
        self.pubinfo = self.top_window.get_widget("pubinfo")
        self.note = self.top_window.get_widget("source_note")

        self.title.set_text(source.getTitle())
        self.author.set_text(source.getAuthor())
        self.pubinfo.set_text(source.getPubInfo())

        self.note.set_point(0)
        self.note.insert_defaults(source.getNote())
        self.note.set_word_wrap(1)

        self.top_window.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_sourceapply_clicked" : on_source_apply_clicked
            })

        self.top = self.top_window.get_widget("sourceEditor")
        self.top.set_data("o",self)

def on_source_apply_clicked(obj):

    edit = obj.get_data("o")
    title = edit.title.get_text()
    author = edit.author.get_text()
    pubinfo = edit.pubinfo.get_text()
    note = edit.note.get_chars(0,-1)
    
    if author != edit.source.getAuthor():
        edit.source.setAuthor(author)
        utils.modified()
        
    if title != edit.source.getTitle():
        edit.source.setAuthor(title)
        utils.modified()
        
    if pubinfo != edit.source.getPubInfo():
        edit.source.setAuthor(pubinfo)
        utils.modified()
        
    if note != edit.source.getNote():
        edit.source.setNote(note)
        utils.modified()

    utils.destroy_passed_object(edit.top)
    edit.callback(1)

    
