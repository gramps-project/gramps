#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Donald N. Allingham
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
Provides the common export options for Exporters
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import gtk
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Config

from BasicUtils import name_displayer
from Filters import GenericFilter, Rules

#-------------------------------------------------------------------------
#
# WriterOptionBox
#
#-------------------------------------------------------------------------
class WriterOptionBox:
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options. 
    """
    def __init__(self, person):
        self.person = person
        self.private = 0
        self.restrict = 0
        self.cfilter = None
        self.restrict_check = None
        self.private_check = None
        self.filter_obj = None

    def get_option_box(self):
        """
        Builds up a gtk.Table that contains the standard options
        """
        table = gtk.Table(3, 2)
        label = gtk.Label('Filter')
        self.filter_obj = gtk.ComboBox()
        self.private_check = gtk.CheckButton(
            _('Do not include records marked private'))
        self.restrict_check = gtk.CheckButton(
            _('Restrict data on living people'))

        self.private_check.set_active(Config.get(Config.EXPORT_NO_PRIVATE))
        self.restrict_check.set_active(Config.get(Config.EXPORT_RESTRICT))
        
        table.set_border_width(12)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0)
        table.attach(self.filter_obj, 1, 2, 0, 1, yoptions=0)
        table.attach(self.private_check, 1, 2, 1, 2, yoptions=0)
        table.attach(self.restrict_check, 1, 2, 2, 3, yoptions=0)

        entire_db = GenericFilter()
        entire_db.set_name(_("Entire Database"))
        the_filters = [entire_db]

        if self.person:
            the_filters += self.__define_person_filters()

        from Filters import CustomFilters
        the_filters.extend(CustomFilters.get_filters('Person'))

        model = gtk.ListStore(str, object)
        for item in the_filters:
            model.append(row=[item.get_name(), item])

        cell = gtk.CellRendererText()
        self.filter_obj.pack_start(cell, True)
        self.filter_obj.add_attribute(cell, 'text', 0)
        self.filter_obj.set_model(model)
        self.filter_obj.set_active(0)

        table.show()
        return table

    def __define_person_filters(self):
        """
        Add person filters if the active person is defined
        """

        des = GenericFilter()
        des.set_name(_("Descendants of %s") %
                     name_displayer.display(self.person))
        des.add_rule(Rules.Person.IsDescendantOf(
                [self.person.get_gramps_id(), 1]))
        
        ans = GenericFilter()
        ans.set_name(_("Ancestors of %s")
                     % name_displayer.display(self.person))
        ans.add_rule(Rules.Person.IsAncestorOf(
                [self.person.get_gramps_id(), 1]))
        
        com = GenericFilter()
        com.set_name(_("People with common ancestor with %s") %
                     name_displayer.display(self.person))
        com.add_rule(Rules.Person.HasCommonAncestorWith(
                [self.person.get_gramps_id()]))
        return [des, ans, com]

    def parse_options(self):
        """
        Extract the common values from the GTK widgets. After this function
        is called, the following variables are defined:

           private  = privacy requested
           restrict = restrict information on living peoplel
           cfitler  = return the GenericFilter selected

        """
        self.restrict = self.restrict_check.get_active()
        self.private = self.private_check.get_active()

        Config.set(Config.EXPORT_NO_PRIVATE, self.private)
        Config.set(Config.EXPORT_RESTRICT, self.restrict)
        Config.sync()

        model = self.filter_obj.get_model()
        node = self.filter_obj.get_active_iter()
        self.cfilter = model[node][1]

