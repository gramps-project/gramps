# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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

# $Id$

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import Gramplet
from BasicUtils import name_displayer
from ReportBase import ReportUtils
import DateHandler
import Errors
import gen.lib
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class DataEntryGramplet(Gramplet):
    NO_REL     = 0
    AS_PARENT  = 1
    AS_SPOUSE  = 2
    AS_SIBLING = 3
    AS_CHILD   = 4
    def init(self):
        self.de_column_width = 20
        import gtk
        rows = gtk.VBox()
        self.dirty = False
        self.dirty_person = None
        self.dirty_family = None
        self.de_widgets = {}
        for items in [("Active person", _("Active person"), None, True, 
                       [("Edit person", "", self.edit_person), ("Edit family", _("Family:"), self.edit_family)], 
                       False, 0), 
                      ("APName", _("Surname, Given"), None, False, [], True, 0), 
                      ("APGender", _("Gender"), [_("female"), _("male"), _("unknown")], False, [], True, 2),
                      ("APBirth", _("Birth"), None, False, [], True, 0), 
                      ("APDeath", _("Death"), None, False, [], True, 0)
                     ]:
            pos, text, choices, readonly, callback, dirty, default = items
            row = self.make_row(pos, text, choices, readonly, callback, dirty, default)
            rows.pack_start(row, False)

        # Save and Abandon
        row = gtk.HBox()
        button = gtk.Button(_("Save"))
        button.connect("clicked", self.save_data_edit)
        row.pack_start(button, True)
        button = gtk.Button(_("Abandon"))
        button.connect("clicked", self.abandon_data_edit)
        row.pack_start(button, True)
        rows.pack_start(row, False)

        for items in [("New person", _("New person"), None, True, 0), 
                      ("NPRelation", _("Add relation"), 
                       [_("No relation to active person"),
                        _("Add as a Parent"), 
                        _("Add as a Spouse"), 
                        _("Add as a Sibling"), 
                        _("Add as a Child")],
                       False, 0),
                      ("NPName", _("Surname, Given"), None, False, 0), 
                      ("NPGender", _("Gender"), [_("female"), _("male"), _("unknown")], False, 2),
                      ("NPBirth", _("Birth"), None, False, 0), 
                      ("NPDeath", _("Death"), None, False, 0)
                     ]:
            pos, text, choices, readonly, default = items
            row = self.make_row(pos, text, choices, readonly, default=default)
            rows.pack_start(row, False)

        # Save, Abandon, Clear
        row = gtk.HBox()
        button = gtk.Button(_("Add"))
        button.connect("clicked", self.add_data_entry)
        row.pack_start(button, True)
        button = gtk.Button(_("Copy Active Data"))
        button.connect("clicked", self.copy_data_entry)
        row.pack_start(button, True)
        button = gtk.Button(_("Clear"))
        button.connect("clicked", self.clear_data_entry)
        row.pack_start(button, True)
        rows.pack_start(row, False)

        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(rows)
        rows.show_all()
        self.clear_data_entry(None)

    def main(self): # return false finishes
        if self.dirty:
            return
        self.de_widgets["Active person:Edit family"].hide()
        self.de_widgets["Active person:Edit family:Label"].hide()
        active_person = self.dbstate.get_active_person()
        self.dirty_person = active_person
        self.dirty_family = None
        if active_person:
            self.de_widgets["Active person:Edit person"].show()
            self.de_widgets["Active person:Edit family"].hide()
            self.de_widgets["Active person:Edit family:Label"].hide()
            # Fill in current person edits:
            name = name_displayer.display(active_person)
            self.de_widgets["Active person"].set_text("<i>%s</i> " % name)
            self.de_widgets["Active person"].set_use_markup(True)
            # Name:
            name_obj = active_person.get_primary_name()
            if name_obj:
                self.de_widgets["APName"].set_text("%s, %s" %
                   (name_obj.get_surname(), name_obj.get_first_name()))
            self.de_widgets["APGender"].set_active(active_person.get_gender()) # gender
            # Birth:
            birth = ReportUtils.get_birth_or_fallback(self.dbstate.db, active_person)
            birth_text = ""
            if birth:
                sdate = DateHandler.get_date(birth)
                birth_text += sdate + " "
                place_handle = birth.get_place_handle()
                if place_handle:
                    place = self.dbstate.db.get_place_from_handle(place_handle)
                    place_text = place.get_title()
                    if place_text:
                        birth_text += _("in") + " " + place_text

            self.de_widgets["APBirth"].set_text(birth_text)
            # Death:
            death = ReportUtils.get_death_or_fallback(self.dbstate.db, active_person)
            death_text = ""
            if death:
                sdate = DateHandler.get_date(death)
                death_text += sdate + " "
                place_handle = death.get_place_handle()
                if place_handle:
                    place = self.dbstate.db.get_place_from_handle(place_handle)
                    place_text = place.get_title()
                    if place_text:
                        death_text += _("in") + " " + place_text
            self.de_widgets["APDeath"].set_text(death_text)
            family_list = active_person.get_family_handle_list()
            if len(family_list) > 0:
                self.dirty_family = self.dbstate.db.get_family_from_handle(family_list[0])
                self.de_widgets["Active person:Edit family"].show()
                self.de_widgets["Active person:Edit family:Label"].show()
            else:
                family_list = active_person.get_parent_family_handle_list()
                if len(family_list) > 0:
                    self.dirty_family = self.dbstate.db.get_family_from_handle(family_list[0])
                    self.de_widgets["Active person:Edit family"].show()
                    self.de_widgets["Active person:Edit family:Label"].show()
        else:
            self.clear_data_edit(None)
            self.de_widgets["Active person:Edit person"].hide()
            self.de_widgets["Active person:Edit family"].hide()
            self.de_widgets["Active person:Edit family:Label"].hide()
        self.dirty = False

    def make_row(self, pos, text, choices=None, readonly=False, callback_list=[],
                 mark_dirty=False, default=0):
        import gtk
        # Data Entry: Active Person
        row = gtk.HBox()
        label = gtk.Label()
        if readonly:
            label.set_text("<b>%s</b>" % text)
            label.set_width_chars(self.de_column_width)
            label.set_use_markup(True)
            self.de_widgets[pos] = gtk.Label()
            self.de_widgets[pos].set_alignment(0.0, 0.5)
            self.de_widgets[pos].set_use_markup(True)
            label.set_alignment(0.0, 0.5)
            row.pack_start(label, False)
            row.pack_start(self.de_widgets[pos], False)
        else:
            label.set_text("%s: " % text)
            label.set_width_chars(self.de_column_width)
            label.set_alignment(1.0, 0.5) 
            if choices is None:
                self.de_widgets[pos] = gtk.Entry()
                if mark_dirty:
                    self.de_widgets[pos].connect("changed", self.mark_dirty)
                row.pack_start(label, False)
                row.pack_start(self.de_widgets[pos], True)
            else:
                eventBox = gtk.EventBox()
                self.de_widgets[pos] = gtk.combo_box_new_text()
                eventBox.add(self.de_widgets[pos])
                for add_type in choices:
                    self.de_widgets[pos].append_text(add_type)
                self.de_widgets[pos].set_active(default) 
                if mark_dirty:
                    self.de_widgets[pos].connect("changed", self.mark_dirty)
                row.pack_start(label, False)
                row.pack_start(eventBox, True, True)
        for name, text, callback in callback_list:
            label = gtk.Label()
            label.set_text(text)
            self.de_widgets[pos + ":" + name + ":Label"] = label
            row.pack_start(label, False)
            icon = gtk.STOCK_EDIT
            size = gtk.ICON_SIZE_MENU
            button = gtk.Button()
            image = gtk.Image()
            image.set_from_stock(icon, size)
            button.add(image)
            button.set_relief(gtk.RELIEF_NONE)
            button.connect("clicked", callback)
            self.de_widgets[pos + ":" + name] = button
            row.pack_start(button, False)
        row.show_all()
        return row

    def mark_dirty(self, obj):
        self.dirty = True

    def abandon_data_edit(self, obj):
        self.dirty = False
        self.update()

    def edit_callback(self, person):
        self.dirty = False
        self.update()

    def edit_person(self, obj):
        from Editors import EditPerson
        try:
            EditPerson(self.gui.dbstate, 
                       self.gui.uistate, [], 
                       self.dirty_person,
                       callback=self.edit_callback)
        except Errors.WindowActiveError:
            pass

    def edit_family(self, obj):
        from Editors import EditFamily
        try:
            EditFamily(self.gui.dbstate, 
                       self.gui.uistate, [], 
                       self.dirty_family)
        except Errors.WindowActiveError:
            pass
    
    def process_dateplace(self, text):
        if text == "": return None, None
        prep_in = _("in") # word or phrase that separates date from place
        text = text.strip()
        if (" %s "  % prep_in) in text:
            date, place = text.split((" %s "  % prep_in), 1)
        elif text.startswith("%s "  % prep_in):
            date, place = text.split(("%s "  % prep_in), 1)
        else:
            date, place = text, ""
        date = date.strip()
        place = place.strip()
        if date != "":
            date = DateHandler.parser.parse(date)
        else:
            date = None
        if place != "":
            newq, place = self.get_or_create_place(place)
        else:
            place = None
        return date, place

    def get_or_create_place(self, place_name):
        if place_name == "": return (-1, None)
        for place in self.dbstate.db.iter_places():
            if place.get_title().strip() == place_name:
                return (0, place) # (old, object)
        place = gen.lib.Place()
        place.set_title(place_name)
        self.dbstate.db.add_place(place,self.trans)
        return (1, place) # (new, object)

    def get_or_create_event(self, object, type, date, place):
        """ Add or find a type event on object """
        if date is place is None: return (-1, None)
        # first, see if it exists
        ref_list = object.get_event_ref_list()
        # look for a match, and possible correction
        for ref in ref_list:
            event = self.dbstate.db.get_event_from_handle(ref.ref)
            if event is not None:
                if int(event.get_type()) == type:
                    # Match! Let's update
                    if date:
                        event.set_date_object(date)
                    if place:
                        event.set_place_handle(place.get_handle())
                    self.dbstate.db.commit_event(event, self.trans)
                    return (0, event)
        # else create it:
        event = gen.lib.Event()
        if type:
            event.set_type(gen.lib.EventType(type))
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        self.dbstate.db.add_event(event, self.trans)
        return (1, event)

    def make_event(self, type, date, place):
        if date is place is None: return None
        event = gen.lib.Event()
        event.set_type(gen.lib.EventType(type))
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        self.dbstate.db.add_event(event, self.trans)
        return event

    def make_person(self, firstname, surname, gender):
        person = gen.lib.Person()
        name = gen.lib.Name()
        name.set_type(gen.lib.NameType(gen.lib.NameType.BIRTH))
        name.set_first_name(firstname)
        name.set_surname(surname)
        person.set_primary_name(name)
        person.set_gender(gender)
        return person

    def save_data_edit(self, obj):
        if self.dirty:
            # Save the edits ----------------------------------
            person = self.dirty_person
            # First, get the data:
            gender = self.de_widgets["APGender"].get_active()
            if "," in self.de_widgets["APName"].get_text():
                surname, firstname = self.de_widgets["APName"].get_text().split(",", 1)
            else:
                surname, firstname = self.de_widgets["APName"].get_text(), ""
            surname = surname.strip()
            firstname = firstname.strip()
            name = person.get_primary_name()
            # Now, edit it:
            self.trans = self.dbstate.db.transaction_begin()
            name.set_surname(surname)
            name.set_first_name(firstname)
            person.set_gender(gender)
            birthdate, birthplace = self.process_dateplace(self.de_widgets["APBirth"].get_text().strip())
            new, birthevent = self.get_or_create_event(person, gen.lib.EventType.BIRTH, birthdate, birthplace)
            # reference it, if need be:
            birthref = person.get_birth_ref()
            if birthevent:
                if birthref is None:
                    # need new
                    birthref = gen.lib.EventRef()
                birthref.set_reference_handle(birthevent.get_handle())
                person.set_birth_ref(birthref)
            deathdate, deathplace = self.process_dateplace(self.de_widgets["APDeath"].get_text().strip())
            new, deathevent = self.get_or_create_event(person, gen.lib.EventType.DEATH, deathdate, deathplace)
            # reference it, if need be:
            deathref = person.get_death_ref()
            if deathevent:
                if deathref is None:
                    # need new
                    deathref = gen.lib.EventRef()
                deathref.set_reference_handle(deathevent.get_handle())
                person.set_death_ref(deathref)
            self.dbstate.db.commit_person(person,self.trans)
            self.dbstate.db.transaction_commit(self.trans,
                    (_("Gramplet Data Edit: %s") %  name_displayer.display(person)))
        self.dirty = False
        self.update()

    def add_data_entry(self, obj):
        from QuestionDialog import ErrorDialog
        # First, get the data:
        if "," in self.de_widgets["NPName"].get_text():
            surname, firstname = self.de_widgets["NPName"].get_text().split(",", 1)
        else:
            surname, firstname = self.de_widgets["NPName"].get_text(), ""
        surname = surname.strip()
        firstname = firstname.strip()
        gender = self.de_widgets["NPGender"].get_active()
        if self.dirty:
            current_person = self.dirty_person
        else:
            current_person = self.dbstate.get_active_person()
        # Pre-check to make sure everything is ok: -------------------------------------------
        if surname == "" and firstname == "":
            ErrorDialog(_("Please provide a name."), _("Can't add new person."))
            return
        if self.de_widgets["NPRelation"].get_active() == self.NO_REL:
            # "No relation to active person"
            pass
        elif self.de_widgets["NPRelation"].get_active() == self.AS_PARENT:
            # "Add as a Parent"
            if current_person is None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a parent."))
                return
            elif gender == gen.lib.Person.UNKNOWN: # unknown
                ErrorDialog(_("Please set the new person's gender."), _("Can't add new person as a parent."))
                return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SPOUSE:
            # "Add as a Spouse"
            if current_person is None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a spouse."))
                return
            elif (gender == gen.lib.Person.UNKNOWN and 
                  current_person.get_gender() == gen.lib.Person.UNKNOWN): # both genders unknown
                ErrorDialog(_("Please set the new person's gender."), _("Can't add new person as a spouse."))
                return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SIBLING:
            # "Add as a Sibling"
            if current_person is None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a sibling."))
                return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_CHILD:
            # "Add as a Child"
            if current_person is None:
                ErrorDialog(_("Please set an active person."), _("Can't add new person as a child."))
                return
        # Start the transaction: ------------------------------------------------------------
        self.trans = self.dbstate.db.transaction_begin()
        # New person --------------------------------------------------
        # Add birth
        new_birth_date, new_birth_place = self.process_dateplace(self.de_widgets["NPBirth"].get_text().strip())
        birth_event = self.make_event(gen.lib.EventType.BIRTH, new_birth_date, new_birth_place)
        # Add death
        new_death_date, new_death_place = self.process_dateplace(self.de_widgets["NPDeath"].get_text())
        death_event = self.make_event(gen.lib.EventType.DEATH, new_death_date, new_death_place)
        # Now, create the person and events:
        person = self.make_person(firstname, surname, gender)
        # New birth for person:
        if birth_event:
            birth_ref = gen.lib.EventRef()
            birth_ref.set_reference_handle(birth_event.get_handle())
            person.set_birth_ref(birth_ref)
        # New death for person:
        if death_event:
            death_ref = gen.lib.EventRef()
            death_ref.set_reference_handle(death_event.get_handle())
            person.set_death_ref(death_ref)
        self.dbstate.db.add_person(person, self.trans)
        # All error checking done; just add relation:
        if self.de_widgets["NPRelation"].get_active() == self.NO_REL:
            # "No relation to active person"
            pass
        elif self.de_widgets["NPRelation"].get_active() == self.AS_PARENT:
            # "Add as a Parent"
            # Go through current_person parent families
            added = False
            for family_handle in current_person.get_parent_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    # find one that person would fit as a parent
                    fam_husband_handle = family.get_father_handle()
                    fam_wife_handle = family.get_mother_handle()
                    # can we add person as wife?
                    if fam_wife_handle is None and person.get_gender() == gen.lib.Person.FEMALE:
                        # add the person
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        added = True
                        break
                    elif fam_husband_handle is None and person.get_gender() == gen.lib.Person.MALE:
                        # add the person
                        family.set_father_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        added = True
                        break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                family = gen.lib.Family()
                self.dbstate.db.add_family(family, self.trans)
                if person.get_gender() == gen.lib.Person.MALE:
                    family.set_father_handle(person.get_handle())
                elif person.get_gender() == gen.lib.Person.FEMALE:
                    family.set_mother_handle(person.get_handle())
                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                # add curent_person as child
                childref = gen.lib.ChildRef()
                childref.set_reference_handle(current_person.get_handle())
                family.add_child_ref( childref)
                current_person.add_parent_family_handle(family.get_handle())
                # finalize
                person.add_family_handle(family.get_handle())
                self.dbstate.db.commit_family(family, self.trans)
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SPOUSE:
            # "Add as a Spouse"
            added = False
            family = None
            for family_handle in current_person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    fam_husband_handle = family.get_father_handle()
                    fam_wife_handle = family.get_mother_handle()
                    if current_person.get_handle() == fam_husband_handle:
                        # can we add person as wife?
                        if fam_wife_handle is None:
                            if person.get_gender() == gen.lib.Person.FEMALE:
                                # add the person
                                family.set_mother_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.add_family_handle(family.get_handle())
                                added = True
                                break
                            elif person.get_gender() == gen.lib.Person.UNKNOWN:
                                family.set_mother_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.set_gender(gen.lib.Person.FEMALE)
                                self.de_widgets["NPGender"].set_active(gen.lib.Person.FEMALE)
                                person.add_family_handle(family.get_handle())
                                added = True
                                break
                    elif current_person.get_handle() == fam_wife_handle:
                        # can we add person as husband?
                        if fam_husband_handle is None:
                            if person.get_gender() == gen.lib.Person.MALE:
                                # add the person
                                family.set_father_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.add_family_handle(family.get_handle())
                                added = True
                                break
                            elif person.get_gender() == gen.lib.Person.UNKNOWN:
                                family.set_father_handle(person.get_handle())
                                family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                                person.add_family_handle(family.get_handle())
                                person.set_gender(gen.lib.Person.MALE)
                                self.de_widgets["NPGender"].set_active(gen.lib.Person.MALE)
                                added = True
                                break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                if person.get_gender() == gen.lib.Person.UNKNOWN:
                    if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                        ErrorDialog(_("Please set gender on Active or new person."), 
                                    _("Can't add new person as a spouse."))
                        return
                    elif current_person.get_gender() == gen.lib.Person.MALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(current_person.get_handle())
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.set_gender(gen.lib.Person.FEMALE)
                        self.de_widgets["NPGender"].set_active(gen.lib.Person.FEMALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.FEMALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(person.get_handle())
                        family.set_mother_handle(current_person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.set_gender(gen.lib.Person.MALE)
                        self.de_widgets["NPGender"].set_active(gen.lib.Person.MALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                elif person.get_gender() == gen.lib.Person.MALE:
                    if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(person.get_handle())
                        family.set_mother_handle(current_person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        current_person.set_gender(gen.lib.Person.FEMALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.MALE:
                        ErrorDialog(_("Same genders on Active and new person."), 
                                    _("Can't add new person as a spouse."))
                        return
                    elif current_person.get_gender() == gen.lib.Person.FEMALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(person.get_handle())
                        family.set_mother_handle(current_person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                elif person.get_gender() == gen.lib.Person.FEMALE:
                    if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(current_person.get_handle())
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        current_person.set_gender(gen.lib.Person.MALE)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.MALE:
                        family = gen.lib.Family()
                        self.dbstate.db.add_family(family, self.trans)
                        family.set_father_handle(current_person.get_handle())
                        family.set_mother_handle(person.get_handle())
                        family.set_relationship(gen.lib.FamilyRelType.MARRIED)
                        person.add_family_handle(family.get_handle())
                        current_person.add_family_handle(family.get_handle())
                        self.dbstate.db.commit_family(family, self.trans)
                    elif current_person.get_gender() == gen.lib.Person.FEMALE:
                        ErrorDialog(_("Same genders on Active and new person."), 
                                    _("Can't add new person as a spouse."))
                        return
        elif self.de_widgets["NPRelation"].get_active() == self.AS_SIBLING:
            # "Add as a Sibling"
            added = False
            for family_handle in current_person.get_parent_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    childref = gen.lib.ChildRef()
                    childref.set_reference_handle(person.get_handle())
                    family.add_child_ref( childref)
                    person.add_parent_family_handle(family.get_handle())
                    added = True
                    break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                family = gen.lib.Family()
                self.dbstate.db.add_family(family, self.trans)
                childref = gen.lib.ChildRef()
                childref.set_reference_handle(person.get_handle())
                family.add_child_ref( childref)
                childref = gen.lib.ChildRef()
                childref.set_reference_handle(current_person.get_handle())
                family.add_child_ref( childref)
                person.add_parent_family_handle(family.get_handle())
                current_person.add_parent_family_handle(family.get_handle())
                self.dbstate.db.commit_family(family, self.trans)
        elif self.de_widgets["NPRelation"].get_active() == self.AS_CHILD:
            # "Add as a Child"
            added = False
            family = None
            for family_handle in current_person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family:
                    childref = gen.lib.ChildRef()
                    childref.set_reference_handle(person.get_handle())
                    family.add_child_ref( childref)
                    person.add_parent_family_handle(family.get_handle())
                    added = True
                    break
            if added:
                self.dbstate.db.commit_family(family, self.trans)
            else:
                if current_person.get_gender() == gen.lib.Person.UNKNOWN:
                    ErrorDialog(_("Please set gender on Active person."), 
                                _("Can't add new person as a child."))
                    return
                else:
                    family = gen.lib.Family()
                    self.dbstate.db.add_family(family, self.trans)
                    childref = gen.lib.ChildRef()
                    childref.set_reference_handle(person.get_handle())
                    family.add_child_ref( childref)
                    person.add_parent_family_handle(family.get_handle())
                    current_person.add_family_handle(family.get_handle())
                    if gen.lib.Person.FEMALE:
                        family.set_mother_handle(current_person.get_handle())
                    else:
                        family.set_father_handle(current_person.get_handle())
                    self.dbstate.db.commit_family(family, self.trans)
        # Commit changes -------------------------------------------------
        if current_person:
            self.dbstate.db.commit_person(current_person, self.trans)
        if person:
            self.dbstate.db.commit_person(person, self.trans)
        self.dbstate.db.transaction_commit(self.trans,
                 (_("Gramplet Data Entry: %s") %  name_displayer.display(person)))

    def copy_data_entry(self, obj):
        self.de_widgets["NPName"].set_text(self.de_widgets["APName"].get_text())
        self.de_widgets["NPBirth"].set_text(self.de_widgets["APBirth"].get_text())
        self.de_widgets["NPDeath"].set_text(self.de_widgets["APDeath"].get_text())
        self.de_widgets["NPGender"].set_active(self.de_widgets["APGender"].get_active())
        # FIXME: put cursor in add surname

    def clear_data_edit(self, obj):
        self.de_widgets["Active person"].set_text("")
        self.de_widgets["APName"].set_text("")
        self.de_widgets["APBirth"].set_text("")
        self.de_widgets["APDeath"].set_text("")
        self.de_widgets["APGender"].set_active(gen.lib.Person.UNKNOWN) 

    def clear_data_entry(self, obj):
        self.de_widgets["NPName"].set_text("")
        self.de_widgets["NPBirth"].set_text("")
        self.de_widgets["NPDeath"].set_text("")
        self.de_widgets["NPRelation"].set_active(self.NO_REL) 
        self.de_widgets["NPGender"].set_active(gen.lib.Person.UNKNOWN) 

    def db_changed(self):
        """
        If person or family changes, the relatives of active person might have
        changed
        """
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('person-edit', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)
        self.dirty = False
        self.dirty_person = None
        self.clear_data_entry(None)

    def active_changed(self, handle):
        self.update()
