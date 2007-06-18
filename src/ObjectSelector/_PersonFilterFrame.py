#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

import gtk
import gobject
from gettext import gettext as _
from logging import getLogger

log = getLogger(".ObjectSelector")

from _FilterFrameBase import FilterFrameBase
from Filters import GenericFilter, Rules
import RelLib

class PersonFilterFrame(FilterFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    # This is used when the widgets are packed into the ObjectSelector
    # frames.
    __default_border_width = 5

    def __init__(self,filter_spec=None,label="Filter"):
	FilterFrameBase.__init__(self,filter_spec,label)

	# Build the filter widgets, the make_* methods are
	# in the FilterFrameBase base class.

        # Gramps ID
	self._id_check,self._id_label,self._id_edit = \
	    self.make_text_widget("Gramps ID")

        # Name
	self._name_check,self._name_label,self._name_edit = \
	    self.make_text_widget("Name")

        # Gender
        genders=[[_("Male"),RelLib.Person.MALE],
                 [_("Female"),RelLib.Person.FEMALE],
                 [_("Unknown"),RelLib.Person.UNKNOWN]]

	self._gender_list = gtk.ListStore(str,int)

	for entry in genders:
	    self._gender_list.append(entry)

	self._gender_check,self._gender_label, self._gender_combo = \
	    self.make_combo_widget("Gender",self._gender_list)

        # Birth
	self._birth_check, self._b_edit, \
	    self._b_before, self._b_after, \
	    self._b_unknown  = self.make_year_widget("Birth Year")

        # Death
	self._death_check, self._d_edit, \
	    self._d_before, self._d_after, \
	    self._d_unknown  = self.make_year_widget("Death Year")

        # Filter
        default_filters = [
            Rules.Person.Everyone,
            Rules.Person.IsFemale,
            Rules.Person.IsMale,
            Rules.Person.HasUnknownGender,
            Rules.Person.Disconnected,
            Rules.Person.SearchName,
            Rules.Person.HaveAltFamilies,
            Rules.Person.HavePhotos,
            Rules.Person.IncompleteNames,
            Rules.Person.HaveChildren,
            Rules.Person.NeverMarried,
            Rules.Person.MultipleMarriages,
            Rules.Person.NoBirthdate,
            Rules.Person.PersonWithIncompleteEvent,
            Rules.Person.FamilyWithIncompleteEvent,
            Rules.Person.ProbablyAlive,
            Rules.Person.PeoplePrivate,
            Rules.Person.IsWitness, 
            Rules.Person.HasTextMatchingSubstringOf, 
            Rules.Person.HasTextMatchingRegexpOf, 
            Rules.Person.HasNote, 
            Rules.Person.HasNoteMatchingSubstringOf, 
            Rules.Person.IsFemale,
            ]

	# don't currently support filters that need an attribute.	
	filters = [ filter for filter in default_filters if \
		    not hasattr(filter,'labels') or len(filter.labels) == 0 ]

        self._filter_list = gtk.ListStore(str,object)

        for filter in filters:
	    self._filter_list.append([filter.name,filter])

	self._filter_check,self._filter_label,self._filter_combo = \
	    self.make_combo_widget("Filter",self._filter_list)

        self._reset_widgets()
        
        if filter_spec is not None:
            self._set_filter(filter_spec)

    def _set_filter(self,filter_spec):
        if filter_spec.include_gramps_id():
            self._id_check.set_active(True)
            self._id_edit.set_text(filter_spec.get_gramps_id())
        else:
            self._id_check.set_active(False)
            self._id_edit.set_text("")

        if filter_spec.include_name():
            self._name_check.set_active(True)
            self._name_edit.set_text(filter_spec.get_name())
        else:
            self._name_check.set_active(False)
            self._name_edit.set_text("")

        if filter_spec.include_gender():
            self._gender_check.set_active(True)
            store = self._gender_list
            it = store.get_iter_first()
            while it:
                if store.get(it, 1)[0] == filter_spec.get_gender():
                    break
                it = store.iter_next(it)

            if it != None:
                self._gender_combo.set_active_iter(it)
        else:
            self._gender_check.set_active(False)


        if filter_spec.include_birth():
            self._birth_check.set_active(True)
            self._b_edit.set_text(filter_spec.get_birth_year())
            if filter_spec.get_birth_criteria() == filter_spec.__class__.BEFORE:
                self._b_before.set_active(True)
                self._b_after.set_active(False)
            else:
                self._b_before.set_active(False)
                self._b_after.set_active(True)
        else:
            self._birth_check.set_active(False)
            self._b_edit.set_text("")

        if filter_spec.include_death():
            self._death_check.set_active(True)
            self._d_edit.set_text(filter_spec.get_death_year())
            if filter_spec.get_death_criteria() == filter_spec.__class__.BEFORE:
                self._d_before.set_active(True)
                self._d_after.set_active(False)
            else:
                self._d_before.set_active(False)
                self._d_after.set_active(True)
        else:
            self._death_check.set_active(False)
            self._d_edit.set_text("")

    def on_apply(self,button=None):
        filter = GenericFilter()
        
        if self._id_check.get_active():
            filter.add_rule(Rules.Person.HasIdOf([self._id_edit.get_text()]))

        if self._name_check.get_active():
            filter.add_rule(Rules.Person.SearchName([self._name_edit.get_text()]))

        if self._gender_check.get_active():
            gender = self._gender_list.get_value(self._gender_combo.get_active_iter(),1)
            if gender == RelLib.Person.MALE:
                filter.add_rule(Rules.Person.IsMale([]))
            elif gender == RelLib.Person.FEMALE:
                filter.add_rule(Rules.Person.IsFemale([]))
            elif gender == RelLib.Person.UNKNOWN:
                filter.add_rule(Rules.Person.HasUnknownGender([]))
            else:
                log.warn("Received unknown gender from filter widget")

        if self._birth_check.get_active():
            date = ""
            if self._b_before.get_active():
                date = "before " + self._b_edit.get_text()
            elif self._b_after.get_active():
                date = "after " + self._b_edit.get_text()
            else:
                log.warn("neither before or after is selected, this should not happen")
            filter.add_rule(Rules.Person.HasBirth([date,'','']))
                
        if self._death_check.get_active():
            date = ""
            if self._d_before.get_active():
                date = "before " + self._d_edit.get_text()
            elif self._d_after.get_active():
                date = "after " + self._d_edit.get_text()
            else:
                log.warn("neither before or after is selected, this should not happen")
            filter.add_rule(Rules.Person.HasDeath([date,'','']))


        if self._filter_check.get_active():
            filter.add_rule(self._filter_list.get_value(self._filter_combo.get_active_iter(),1)([]))
            
	self.emit('apply-filter',filter)
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonFilterFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonFilterFrame()
    w.add(f)
    
    w.show_all()

    gtk.main()
