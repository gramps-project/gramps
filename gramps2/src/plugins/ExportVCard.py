#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Martin Hawlisch
# Copyright (C) 2005-2006  Donald N. Allingham
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

"Export Persons to vCard"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ExportVCard")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GenericFilter
import const
from RelLib import Date
import Errors
from gettext import gettext as _
from QuestionDialog import ErrorDialog
from PluginUtils import register_export

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class CardWriterOptionBox:
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options. 
    """
    def __init__(self,person):
        self.person = person

    def get_option_box(self):

        glade_file = "%s/vcardexport.glade" % os.path.dirname(__file__)
        if not os.path.isfile(glade_file):
            glade_file = "plugins/vcardexport.glade"

        self.topDialog = gtk.glade.XML(glade_file,"vcardExport","gramps")

        filter_obj = self.topDialog.get_widget("filter")
        self.copy = 0

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        if self.person:
            des = GenericFilter.GenericFilter()
            des.set_name(_("Descendants of %s") %
                         self.person.get_primary_name().get_name())
            des.add_rule(GenericFilter.IsDescendantOf(
                [self.person.get_gramps_id(),1]))

            ans = GenericFilter.GenericFilter()
            ans.set_name(_("Ancestors of %s") %
                         self.person.get_primary_name().get_name())
            ans.add_rule(GenericFilter.IsAncestorOf(
                [self.person.get_gramps_id(),1]))

            com = GenericFilter.GenericFilter()
            com.set_name(_("People with common ancestor with %s") %
                         self.person.get_primary_name().get_name())
            com.add_rule(GenericFilter.HasCommonAncestorWith(
                [self.person.get_gramps_id()]))

            self.filter_menu = GenericFilter.build_filter_menu(
                [all,des,ans,com])
        else:
            self.filter_menu = GenericFilter.build_filter_menu([all])
        filter_obj.set_menu(self.filter_menu)

        the_box = self.topDialog.get_widget('vbox1')
        the_parent = self.topDialog.get_widget('dialog-vbox1')
        the_parent.remove(the_box)
        self.topDialog.get_widget("vcardExport").destroy()
        return the_box

    def parse_options(self):
        self.cfilter = self.filter_menu.get_active().get_data("filter")

class CardWriter:
    def __init__(self,database,person,cl=0,filename="",option_box=None):
        self.db = database
        self.person = person
        self.option_box = option_box
        self.cl = cl
        self.filename = filename

        self.plist = {}
        
        if not option_box:
            self.cl_setup()
        else:
            self.option_box.parse_options()

            if self.option_box.cfilter == None:
                for p in self.db.get_person_handles(sort_handles=False):
                    self.plist[p] = 1
            else:
                try:
                    for p in self.option_box.cfilter.apply(self.db, self.db.get_person_handles(sort_handles=False)):
                        self.plist[p] = 1
                except Errors.FilterError, msg:
                    (m1,m2) = msg.messages()
                    ErrorDialog(m1,m2)
                    return

 
    def cl_setup(self):
        for p in self.db.get_person_handles(sort_handles=False):
            self.plist[p] = 1

    def writeln(self,text):
        self.g.write('%s\n' % (text.encode('iso-8859-1')))

    def export_data(self,filename):

        self.dirname = os.path.dirname (filename)
        try:
            self.g = open(filename,"w")
        except IOError,msg:
            msg2 = _("Could not create %s") % filename
            ErrorDialog(msg2,str(msg))
            return 0
        except:
            ErrorDialog(_("Could not create %s") % filename)
            return 0

        for key in self.plist:
            self.write_person(key)

        self.g.close()
        return 1
    
                    
    def write_person(self, person_handle):
        person = self.db.get_person_from_handle(person_handle)
        if person:
            self.writeln("BEGIN:VCARD");
            prname = person.get_primary_name()
            
            self.writeln("FN:%s" % prname.get_regular_name())
            self.writeln("N:%s;%s;%s;%s;%s" % (prname.get_surname(), prname.get_first_name(), person.get_nick_name(), prname.get_surname_prefix(), prname.get_suffix()))
            if prname.get_title():
                self.writeln("TITLE:%s" % prname.get_title())
                
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = self.db.get_event_from_handle(birth_ref.ref)
                if birth:
                    b_date = birth.get_date_object()
                    mod = b_date.get_modifier()
                    if not b_date.get_text() and not b_date.is_empty() and not mod == Date.MOD_SPAN and not mod == Date.MOD_RANGE:
                        (day,month,year,sl) = b_date.get_start_date()
                        if day > 0 and month > 0 and year > 0:
                            self.writeln("BDAY:%s-%02d-%02d" % (year,month,day))

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
                    self.writeln("ADR:%s;%s;%s;%s;%s;%s;%s" % (postbox,ext,street,city,state,zip,country))
                
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
def exportData(database,filename,person,option_box):
    ret = 0
    cw = CardWriter(database,person,0,filename,option_box)
    ret = cw.export_data(filename)
    return ret

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_title = _('vCard')
_description = _('vCard is used in many addressbook and pim applications.')
_config = (_('vCard export options'),CardWriterOptionBox)
_filename = 'vcf'

register_export(exportData,_title,_description,_config,_filename)
