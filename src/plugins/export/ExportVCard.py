#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Martin Hawlisch
# Copyright (C) 2005-2008  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"Export Persons to vCard."

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import sys
import os
from gen.ggettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ExportVCard")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from ExportOptions import WriterOptionBox
from Filters import GenericFilter, Rules, build_filter_model
from gen.lib import Date
import Errors
from glade import Glade

class CardWriter(object):
    def __init__(self, database, filename, msg_callback, option_box=None, callback=None):
        self.db = database
        self.filename = filename
        self.msg_callback = msg_callback
        self.option_box = option_box
        self.callback = callback
        if callable(self.callback): # callback is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        if option_box:
            self.option_box.parse_options()
            self.db = option_box.get_filtered_database(self.db)

    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100*self.count/self.total)
        if newval != self.oldval:
            self.callback(newval)
            self.oldval = newval

    def writeln(self, text):
        #self.g.write('%s\n' % (text.encode('iso-8859-1')))
        self.g.write('%s\n' % (text.encode(sys.getfilesystemencoding())))

    def export_data(self, filename):

        self.dirname = os.path.dirname (filename)
        try:
            self.g = open(filename,"w")
        except IOError,msg:
            msg2 = _("Could not create %s") % filename
            self.msg_callback(msg2, str(msg))
            return False
        except:
            self.msg_callback(_("Could not create %s") % filename)
            return False

        self.count = 0
        self.oldval = 0
        self.total = len([x for x in self.db.iter_person_handles()])
        for key in self.db.iter_person_handles():
            self.write_person(key)
            self.update()

        self.g.close()
        return True   
                    
    def write_person(self, person_handle):
        person = self.db.get_person_from_handle(person_handle)
        if person:
            self.writeln("BEGIN:VCARD");
            prname = person.get_primary_name()
            
            self.writeln("FN:%s" % prname.get_regular_name())
            self.writeln("N:%s;%s;%s;%s;%s" % 
                    (prname.get_surname(), 
                    prname.get_first_name(), 
                    person.get_nick_name(), 
                    prname.get_surname_prefix(), 
                    prname.get_suffix()
                    )
                )
            if prname.get_title():
                self.writeln("TITLE:%s" % prname.get_title())
                
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = self.db.get_event_from_handle(birth_ref.ref)
                if birth:
                    b_date = birth.get_date_object()
                    mod = b_date.get_modifier()
                    if (mod != Date.MOD_TEXTONLY and 
                        not b_date.is_empty() and 
                        not mod == Date.MOD_SPAN and 
                        not mod == Date.MOD_RANGE):
                        (day, month, year, sl) = b_date.get_start_date()
                        if day > 0 and month > 0 and year > 0:
                            self.writeln("BDAY:%s-%02d-%02d" % (year, month, 
                                                                day))

            address_list = person.get_address_list()
            for address in address_list:
                postbox = ""
                ext = ""
                street = address.get_street()
                city = address.get_city()
                state = address.get_state()
                zip = address.get_postal_code()
                country = address.get_country()
                if street or city or state or zip or country:
                    self.writeln("ADR:%s;%s;%s;%s;%s;%s;%s" % 
                        (postbox, ext, street, city,state, zip, country))
                
                phone = address.get_phone()
                if phone:
                    self.writeln("TEL:%s" % phone)
                
            url_list = person.get_url_list()
            for url in url_list:
                href = url.get_path()
                if href:
                    self.writeln("URL:%s" % href)

        self.writeln("END:VCARD");
        self.writeln("");

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename, msg_callback, option_box=None, callback=None):
    cw = CardWriter(database, filename, msg_callback, option_box, callback)
    return cw.export_data(filename)
