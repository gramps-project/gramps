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
import gtk
from gettext import gettext as _

import RelLib
from BasicUtils import name_displayer
from Filters import GenericFilter, Rules, build_filter_menu

def restrict_living(person):
    newperson = RelLib.Person()
    name = RelLib.Name()

    # copy name info
    source = person.get_primary_name()
    name.first_name = _(u'Living')
    name.surname = source.surname
    name.title = source.title
    name.type = source.type
    name.prefix = source.prefix
    name.patronymic = source.patronymic
    name.group_as = source.group_as
    name.sort_as = source.sort_as
    name.display_as = source.display_as
    name.call = ""
    newperson.set_primary_name(name)

    newperson.parent_family_list = person.parent_family_list[:]
    newperson.family_list = person.family_list[:]
    newperson.gender = person.gender

    return newperson

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class WriterOptionBox:
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options. 
    """
    def __init__(self, person):
        self.person = person

    def get_option_box(self):
        self.restrict = True

        table = gtk.Table(3, 2)
        label = gtk.Label('Filter')
        self.filter_obj = gtk.OptionMenu()
        self.private_check = gtk.CheckButton(_('Do not include records marked private'))
        self.restrict_check = gtk.CheckButton(_('Restrict data on living people'))

        table.set_border_width(12)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0)
        table.attach(self.filter_obj, 1, 2, 0, 1, yoptions=0)
        table.attach(self.private_check, 1, 2, 1, 2, yoptions=0)
        table.attach(self.restrict_check, 1, 2, 2, 3, yoptions=0)

        #filter_obj = self.topDialog.get_widget("filter")

        all = GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(Rules.Person.Everyone([]))

        the_filters = [all]

        if self.person:
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

            the_filters += [des, ans, com]

        from Filters import CustomFilters
        the_filters.extend(CustomFilters.get_filters('Person'))
        self.filter_menu = build_filter_menu(the_filters)
        self.filter_obj.set_menu(self.filter_menu)

        table.show()
        return table

    def parse_options(self):

        self.restrict = self.restrict_check.get_active()
        self.private = self.private_check.get_active()
        self.cfilter = self.filter_menu.get_active().get_data("filter")

