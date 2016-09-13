#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2012       Michiel D. Nauta
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Tools/Database Repair/Check and Repair Database"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
from io import StringIO
import time
from collections import defaultdict

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging

#-------------------------------------------------------------------------
#
# gtk modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored
from gramps.gen.lib import (Citation, Event, EventType, Family, Media,
                            Name, Note, Person, Place, Repository, Source,
                            StyledText, Tag)
from gramps.gen.db import DbTxn
from gramps.gen.config import config
from gramps.gen.utils.id import create_id
from gramps.gen.utils.db import family_name
from gramps.gen.utils.unknown import make_unknown
from gramps.gen.utils.file import (media_path_full, find_file)
from gramps.gui.managedwindow import ManagedWindow
from gramps.gen.utils.file import create_checksum
from gramps.gui.plug import tool
from gramps.gui.dialog import OkDialog, MissingMediaDialog
from gramps.gen.display.name import displayer as _nd
from gramps.gui.glade import Glade
from gramps.gen.errors import HandleError

# table for handling control chars in notes.
# All except 09, 0A, 0D are replaced with space.
strip_dict = dict.fromkeys(list(range(9))+list(range(11,13))+list(range(14, 32)),  " ")

class ProgressMeter:
    def __init__(self, *args, **kwargs): pass
    def set_pass(self, *args): pass
    def step(self): pass
    def close(self): pass

#-------------------------------------------------------------------------
#
# Low Level repair
#
#-------------------------------------------------------------------------
def cross_table_duplicates(db, uistate):
    """
    Function to find the presence of identical handles that occur in different
    database tables.

    Assumes there are no intable duplicates, see low_level function.

    :param db: the database to check
    :type db: :class:`gen.db.read.DbBsddbRead`
    :returns: the presence of cross table duplicate handles
    :rtype: bool
    """
    if uistate:
        parent = uistate.window
    else:
        parent = None
    progress = ProgressMeter(_('Checking Database'), '', parent)
    progress.set_pass(_('Looking for cross table duplicates'), 9)
    logging.info('Looking for cross table duplicates')
    total_nr_handles = 0
    all_handles = set([])
    for the_map in [db.person_map, db.family_map, db.event_map, db.place_map,
            db.source_map, db.citation_map, db.media_map, db.repository_map,
            db.note_map]:
        handle_list = list(the_map.keys())
        total_nr_handles += len(handle_list)
        all_handles.update(handle_list)
        progress.step()
    progress.close()
    num_errors = total_nr_handles - len(all_handles)
    if num_errors == 0:
        logging.info('    OK: No cross table duplicates')
    else:
        logging.warning('    FAIL: Found %d cross table duplicates' %
                         num_errors)
    return total_nr_handles > len(all_handles)

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
class Check(tool.BatchTool):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate

        tool.BatchTool.__init__(self, dbstate, user, options_class, name)
        if self.fail:
            return

        cli = uistate is None
        if uistate:
            from gramps.gui.utils import ProgressMeter as PM
            global ProgressMeter
            ProgressMeter = PM

        if self.db.readonly:
            # TODO: split plugin in a check and repair part to support
            # checking of a read only database
            return

        # The low-level repair is bypassing the transaction mechanism.
        # As such, we run it before starting the transaction.
        # We only do this for the dbdir backend.
        if self.db.__class__.__name__ == 'DbBsddb':
            if cross_table_duplicates(self.db, uistate):
                Report(uistate, _(
                    "Your Family Tree contains cross table duplicate handles.\n "
                    "This is bad and can be fixed by making a backup of your\n"
                    "Family Tree and importing that backup in an empty family\n"
                    "tree. The rest of the checking is skipped, the Check and\n"
                    "Repair tool should be run anew on this new Family Tree."),
                       cli)
                return
        with DbTxn(_("Check Integrity"), self.db, batch=True) as trans:
            self.db.disable_signals()
            checker = CheckIntegrity(dbstate, uistate, trans)
            # start with empty objects, broken links can be corrected below
            # then. This is done before fixing encoding and missing photos,
            # since otherwise we will be trying to fix empty records which are
            # then going to be deleted.
            checker.cleanup_empty_objects()
            checker.fix_encoding()
            checker.fix_ctrlchars_in_notes()
            checker.cleanup_missing_photos(cli)
            checker.cleanup_deleted_name_formats()

            prev_total = -1
            total = 0

            while prev_total != total:
                prev_total = total

                checker.check_for_broken_family_links()
                checker.check_parent_relationships()
                checker.cleanup_empty_families(cli)
                checker.cleanup_duplicate_spouses()

                total = checker.family_errors()

            checker.check_events()
            checker.check_person_references()
            checker.check_family_references()
            checker.check_place_references()
            checker.check_source_references()
            checker.check_citation_references()
            checker.check_media_references()
            checker.check_repo_references()
            checker.check_note_references()
            checker.check_tag_references()
            checker.check_checksum()
            checker.check_media_sourceref()
        self.db.enable_signals()
        self.db.request_rebuild()

        errs = checker.build_report(uistate)
        if errs:
            Report(uistate, checker.text.getvalue(), cli)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class CheckIntegrity:

    def __init__(self, dbstate, uistate, trans):
        self.uistate = uistate
        if self.uistate:
            self.parent_window = self.uistate.window
        else:
            self.parent_window = None
        self.db = dbstate.db
        self.trans = trans
        self.bad_photo = []
        self.replaced_photo = []
        self.removed_photo = []
        self.empty_family = []
        self.broken_links = []
        self.duplicate_links = []
        self.broken_parent_links = []
        self.fam_rel = []
        self.invalid_events = set()
        self.invalid_birth_events = set()
        self.invalid_death_events = set()
        self.invalid_person_references = set()
        self.invalid_family_references = set()
        self.invalid_place_references = set()
        self.invalid_source_references = set()
        self.invalid_citation_references = set()
        self.invalid_repo_references = set()
        self.invalid_media_references = set()
        self.invalid_note_references = set()
        self.invalid_tag_references = set()
        self.invalid_dates = []
        self.removed_name_format = []
        self.empty_objects = defaultdict(list)
        self.replaced_sourceref = []
        self.last_img_dir = config.get('behavior.addmedia-image-dir')
        self.progress = ProgressMeter(_('Checking Database'), '',
                                      parent=self.parent_window)
        self.explanation = Note(_('Objects referenced by this note '
            'were referenced but missing so that is why they have been created '
            'when you ran Check and Repair on %s.') %
            time.strftime('%x %X', time.localtime()))
        self.explanation.set_handle(create_id())

    def family_errors(self):
        return (len(self.broken_parent_links) +
               len(self.broken_links) +
               len(self.empty_family) +
               len(self.duplicate_links)
               )

    def cleanup_deleted_name_formats(self):
        """
        Permanently remove deleted name formats from db.

        When user deletes custom name format those are not removed only marked
        as "inactive". This method does the cleanup of the name format table,
        as well as fixes the display_as, sort_as values for each Name in the db.

        """
        self.progress.set_pass(_('Looking for invalid name format references'),
                               self.db.get_number_of_people())
        logging.info('Looking for invalid name format references')

        deleted_name_formats = [number for (number, name, fmt_str,act)
                                in self.db.name_formats if not act]

        # remove the invalid references from all Name objects
        for person_handle in self.db.get_person_handles():
            person = self.db.get_person_from_handle(person_handle)

            p_changed = False
            name = person.get_primary_name()
            if name.get_sort_as() in deleted_name_formats:
                name.set_sort_as(Name.DEF)
                p_changed = True
            if name.get_display_as() in deleted_name_formats:
                name.set_display_as(Name.DEF)
                p_changed = True
            if p_changed:
                person.set_primary_name(name)

            a_changed = False
            name_list = []
            for name in person.get_alternate_names():
                if name.get_sort_as() in deleted_name_formats:
                    name.set_sort_as(Name.DEF)
                    a_changed = True
                if name.get_display_as() in deleted_name_formats:
                    name.set_display_as(Name.DEF)
                    a_changed = True
                name_list.append(name)
            if a_changed:
                person.set_alternate_names(name_list)

            if p_changed or a_changed:
                self.db.commit_person(person, self.trans)
                self.removed_name_format.append(person_handle)

            self.progress.step()

        # update the custom name name format table
        for number in deleted_name_formats:
            _nd.del_name_format(number)
        self.db.name_formats = _nd.get_name_format(only_custom=True,
                                                           only_active=False)

        if len(self.removed_name_format) == 0:
            logging.info('    OK: no invalid name formats found found')

    def cleanup_duplicate_spouses(self):

        self.progress.set_pass(_('Looking for duplicate spouses'),
                               self.db.get_number_of_people())
        logging.info('Looking for duplicate spouses')
        previous_errors = len(self.duplicate_links)

        for bhandle in self.db.person_map.keys():
            handle = bhandle.decode('utf-8')
            value = self.db.person_map[bhandle]
            p = Person(value)
            splist = p.get_family_handle_list()
            if len(splist) != len(set(splist)):
                new_list = []
                for value in splist:
                    if value not in new_list:
                        new_list.append(value)
                        self.duplicate_links.append((handle, value))
                p.set_family_handle_list(new_list)
                self.db.commit_person(p, self.trans)
            self.progress.step()

        if previous_errors == len(self.duplicate_links):
            logging.info('    OK: no duplicate spouses found')

    def fix_encoding(self):
        self.progress.set_pass(_('Looking for character encoding errors'),
                               self.db.get_number_of_media())
        logging.info('Looking for character encoding errors')
        error_count = 0
        for bhandle in self.db.media_map.keys():
            handle = bhandle.decode('utf-8')
            data = self.db.media_map[bhandle]
            if not isinstance(data[2], str) or not isinstance(data[4], str):
                obj = self.db.get_media_from_handle(handle)
                if not isinstance(data[2], str):
                    obj.path = obj.path.decode('utf-8')
                    logging.warning('    FAIL: encoding error on media object '
                                    '"%(gid)s" path "%(path)s"' %
                                    {'gid' : obj.gramps_id, 'path' : obj.path})
                if not isinstance(data[4], str):
                    obj.desc = obj.desc.decode('utf-8')
                    logging.warning('    FAIL: encoding error on media object '
                                    '"%(gid)s" description "%(desc)s"' %
                                    {'gid' : obj.gramps_id, 'desc' : obj.desc})
                self.db.commit_media(obj, self.trans)
                error_count += 1
            # Once we are here, fix the mime string if not str
            if not isinstance(data[3], str):
                obj = self.db.get_media_from_handle(handle)
                try:
                    if data[3] == str(data[3]):
                        obj.mime = str(data[3])
                    else:
                        obj.mime = ""
                except:
                    obj.mime = ""
                self.db.commit_media(obj, self.trans)
                logging.warning('    FAIL: encoding error on media object '
                                '"%(desc)s" mime "%(mime)s"' %
                                {'desc' : obj.desc, 'mime' : obj.mime})
                error_count += 1
            self.progress.step()
        if error_count == 0:
            logging.info('    OK: no encoding errors found')

    def fix_ctrlchars_in_notes(self):
        self.progress.set_pass(_('Looking for ctrl characters in notes'),
                               self.db.get_number_of_notes())
        logging.info('Looking for ctrl characters in notes')
        error_count = 0
        for bhandle in self.db.note_map.keys():
            handle = bhandle.decode('utf-8')
            note = self.db.get_note_from_handle(handle)
            stext = note.get_styledtext()
            old_text = str(stext)
            new_text = old_text.translate(strip_dict)
            if old_text != new_text:
                logging.warning('    FAIL: control characters found in note "%s"' %
                    self.db.note_map[bhandle][1])
                error_count += 1
                # Commit only if ctrl char found.
                note.set_styledtext(StyledText(text=new_text,
                                               tags=stext.get_tags()))
                self.db.commit_note(note, self.trans)
            self.progress.step()
        if error_count == 0:
            logging.info('    OK: no ctrl characters in notes found')

    def check_for_broken_family_links(self):
        # Check persons referenced by the family objects

        fhandle_list = self.db.get_family_handles()
        self.progress.set_pass(_('Looking for broken family links'),
                               len(fhandle_list) +
                               self.db.get_number_of_people())
        logging.info('Looking for broken family links')
        previous_errors = len(self.broken_parent_links + self.broken_links)

        for bfamily_handle in fhandle_list:
            family_handle = bfamily_handle.decode('utf-8')
            family = self.db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            if father_handle:
                try:
                    father = self.db.get_person_from_handle(father_handle)
                except HandleError:
                    # The person referenced by the father handle does not exist
                    # in the database
                    # This is tested by TestcaseGenerator where the mother is
                    # "Broken6"
                    family.set_father_handle(None)
                    self.db.commit_family(family, self.trans)
                    self.broken_parent_links.append((father_handle, family_handle))
                    logging.warning("    FAIL: family '%(fam_gid)s' "
                                    "father handle '%(hand)s' does not exist" %
                                    {'fam_gid' : family.gramps_id,
                                     'hand' : father_handle})
                    father_handle = None
            if mother_handle:
                try:
                    mother = self.db.get_person_from_handle(mother_handle)
                except HandleError:
                    # The person referenced by the mother handle does not exist
                    # in the database
                    # This is tested by TestcaseGenerator where the mother is
                    # "Broken7"
                    family.set_mother_handle(None)
                    self.db.commit_family(family, self.trans)
                    self.broken_parent_links.append((mother_handle, family_handle))
                    logging.warning("    FAIL: family '%(fam_gid)s' "
                                    "mother handle '%(hand)s' does not exist" %
                                    {'fam_gid' : family.gramps_id,
                                     'hand' : mother_handle})
                    mother_handle = None

            if father_handle and father and \
                    family_handle not in father.get_family_handle_list():
                # The referenced father has no reference back to the family
                # This is tested by TestcaseGenerator where the father is
                # "Broken1"
                self.broken_parent_links.append((father_handle, family_handle))
                father.add_family_handle(family_handle)
                self.db.commit_person(father, self.trans)
                logging.warning("    FAIL: family '%(fam_gid)s' father "
                                "'%(hand)s' does not refer back to the family" %
                                {'fam_gid' : family.gramps_id,
                                 'hand' : father_handle})

            if mother_handle and mother and \
                    family_handle not in mother.get_family_handle_list():
                # The referenced mother has no reference back to the family.
                # This is tested by TestcaseGenerator where the father is
                # "Broken4"
                self.broken_parent_links.append((mother_handle, family_handle))
                mother.add_family_handle(family_handle)
                self.db.commit_person(mother, self.trans)
                logging.warning("    FAIL: family '%(fam_gid)s' mother "
                                "'%(hand)s' does not refer back to the family" %
                                {'fam_gid' : family.gramps_id,
                                 'hand' : mother_handle})

            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                try:
                    child = self.db.get_person_from_handle(child_handle)
                except HandleError:
                    # The person referenced by the child handle
                    # does not exist in the database
                    # This is tested by TestcaseGenerator where the father
                    # is "Broken20"
                    logging.warning("    FAIL: family '%(fam_gid)s' child "
                                    "'%(hand)s' does not exist in the database" %
                                    {'fam_gid' : family.gramps_id,
                                     'hand' : child_handle})
                    family.remove_child_ref(child_ref)
                    self.db.commit_family(family, self.trans)
                    self.broken_links.append((child_handle, family_handle))
                else:
                    if child_handle in [father_handle, mother_handle]:
                        # The child is one of the parents: impossible Remove
                        # such child from the family
                        # This is tested by TestcaseGenerator where the father
                        # is "Broken19"
                        logging.warning("    FAIL: family '%(fam_gid)s' "
                                        "child '%(child_gid)s' is one of the "
                                        "parents" %
                                        {'fam_gid' : family.gramps_id,
                                         'child_gid' : child.gramps_id})
                        family.remove_child_ref(child_ref)
                        self.db.commit_family(family, self.trans)
                        self.broken_links.append((child_handle, family_handle))
                        continue
                    if family_handle == child.get_main_parents_family_handle():
                        continue
                    if family_handle not in \
                           child.get_parent_family_handle_list():
                        # The referenced child has no reference to the family
                        # This is tested by TestcaseGenerator where the father
                        # is "Broken8"
                        logging.warning("    FAIL: family '%(fam_gid)s' "
                                        "child '%(child_gid)s' has no reference"
                                        " to the family. Reference added" %
                                        {'fam_gid' : family.gramps_id,
                                         'child_gid' : child.gramps_id})
                        child.add_parent_family_handle(family_handle)
                        self.db.commit_person(child, self.trans)

            new_ref_list = []
            new_ref_handles = []
            replace = False
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.ref
                if child_handle in new_ref_handles:
                    replace = True
                else:
                    new_ref_list.append(child_ref)
                    new_ref_handles.append(child_handle)

            if replace:
                family.set_child_ref_list(new_ref_list)
                self.db.commit_family(family, self.trans)

            self.progress.step()

        # Check persons membership in referenced families
        for bperson_handle in self.db.get_person_handles():
            person_handle = bperson_handle.decode('utf-8')
            person = self.db.get_person_from_handle(person_handle)

            phandle_list = person.get_parent_family_handle_list()
            new_list = list(set(phandle_list))
            if len(phandle_list) != len(new_list):
                person.set_parent_family_handle_list(new_list)
                self.db.commit_person(person, self.trans)

            for par_family_handle in person.get_parent_family_handle_list():
                try:
                    family = self.db.get_family_from_handle(par_family_handle)
                except HandleError:
                    person.remove_parent_family_handle(par_family_handle)
                    self.db.commit_person(person, self.trans)
                    continue
                for child_handle in [child_ref.ref for child_ref
                                     in family.get_child_ref_list()]:
                    if child_handle == person_handle:
                        break
                else:
                    # Person is not a child in the referenced parent family
                    # This is tested by TestcaseGenerator where the father
                    # is "Broken9"
                    logging.warning("    FAIL: family '%(fam_gid)s' person "
                                    "'%(pers_gid)s' is not a child in the "
                                    "referenced parent family" %
                                    {'fam_gid' : family.gramps_id,
                                     'pers_gid' :person.gramps_id})
                    person.remove_parent_family_handle(par_family_handle)
                    self.db.commit_person(person, self.trans)
                    self.broken_links.append((person_handle, family_handle))
            for family_handle in person.get_family_handle_list():
                try:
                    family = self.db.get_family_from_handle(family_handle)
                except HandleError:
                    # The referenced family does not exist in database
                    # This is tested by TestcaseGenerator where the father
                    # is "Broken20"
                    logging.warning("    FAIL: person '%(pers_gid)s' refers to "
                                    "family '%(hand)s' which is not in the "
                                    "database" %
                                    {'pers_gid' : person.gramps_id,
                                     'hand' : family_handle})
                    person.remove_family_handle(family_handle)
                    self.db.commit_person(person, self.trans)
                    self.broken_links.append((person_handle, family_handle))
                    continue
                if family.get_father_handle() == person_handle:
                    continue
                if family.get_mother_handle() == person_handle:
                    continue
                # The person is not a member of the referenced family
                # This is tested by TestcaseGenerator where the father is
                # "Broken2" and the family misses the link to the father, and
                # where the mother is "Broken3" and the family misses the link
                # to the mother
                logging.warning("    FAIL: family '%(fam_gid)s' person "
                                "'%(pers_gid)s' is not member of the referenced"
                                " family" %
                                {'fam_gid' : family.gramps_id,
                                 'pers_gid' : person.gramps_id})
                person.remove_family_handle(family_handle)
                self.db.commit_person(person, self.trans)
                self.broken_links.append((person_handle, family_handle))
            self.progress.step()

        if previous_errors == len(self.broken_parent_links + self.broken_links):
            logging.info('    OK: no broken family links found')

    def cleanup_missing_photos(self, cl=0):

        self.progress.set_pass(_('Looking for unused objects'),
                               len(self.db.get_media_handles()))
        logging.info('Looking for missing photos')

        missmedia_action = 0
        #-------------------------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself

            for handle in self.db.get_person_handles(sort_handles=False):
                person = self.db.get_person_from_handle(handle)
                if person.has_media_reference(ObjectId):
                    person.remove_media_references([ObjectId])
                    self.db.commit_person(person, self.trans)

            for handle in self.db.get_family_handles():
                family = self.db.get_family_from_handle(handle)
                if family.has_media_reference(ObjectId):
                    family.remove_media_references([ObjectId])
                    self.db.commit_family(family, self.trans)

            for handle in self.db.get_event_handles():
                event = self.db.get_event_from_handle(handle)
                if event.has_media_reference(ObjectId):
                    event.remove_media_references([ObjectId])
                    self.db.commit_event(event, self.trans)

            for handle in self.db.get_source_handles():
                source = self.db.get_source_from_handle(handle)
                if source.has_media_reference(ObjectId):
                    source.remove_media_references([ObjectId])
                    self.db.commit_source(source, self.trans)

            for handle in self.db.get_citation_handles():
                citation = self.db.get_citation_from_handle(handle)
                if citation.has_media_reference(ObjectId):
                    citation.remove_media_references([ObjectId])
                    self.db.commit_citation(citation, self.trans)

            for handle in self.db.get_place_handles():
                place = self.db.get_place_from_handle(handle)
                if place.has_media_reference(ObjectId):
                    place.remove_media_references([ObjectId])
                    self.db.commit_place(place, self.trans)

            self.removed_photo.append(ObjectId)
            self.db.remove_media(ObjectId,self.trans)
            logging.warning('        FAIL: media object and all references to '
                            'it removed')

        def leave_clicked():
            self.bad_photo.append(ObjectId)
            logging.warning('        FAIL: references to missing file kept')

        def select_clicked():
            # File is lost => select a file to replace the lost one
            def fs_close_window(obj):
                self.bad_photo.append(ObjectId)
                logging.warning('        FAIL: references to missing file kept')

            def fs_ok_clicked(obj):
                name = fs_top.get_filename()
                if os.path.isfile(name):
                    obj = self.db.get_media_from_handle(ObjectId)
                    obj.set_path(name)
                    self.db.commit_media(obj, self.trans)
                    self.replaced_photo.append(ObjectId)
                    self.last_img_dir = os.path.dirname(name)
                    logging.warning('        FAIL: media object reselected to '
                                    '"%s"' % name)
                else:
                    self.bad_photo.append(ObjectId)
                    logging.warning('    FAIL: references to missing file kept')

            fs_top = Gtk.FileChooserDialog("%s - Gramps" % _("Select file"),
                        parent=self.parent_window,
                        buttons=(_('_Cancel'), Gtk.ResponseType.CANCEL,
                                 _('_OK'), Gtk.ResponseType.OK)
                        )
            fs_top.set_current_folder(self.last_img_dir)
            response = fs_top.run()
            if response == Gtk.ResponseType.OK:
                fs_ok_clicked(fs_top)
            elif response == Gtk.ResponseType.CANCEL:
                fs_close_window(fs_top)
            fs_top.destroy()

        #-------------------------------------------------------------------------

        for bObjectId in self.db.get_media_handles():
            ObjectId = bObjectId.decode('utf-8')
            obj = self.db.get_media_from_handle(ObjectId)
            photo_name = media_path_full(self.db, obj.get_path())
            photo_desc = obj.get_description()
            if photo_name is not None and photo_name != "" and not find_file(photo_name):
                if cl:
                    fn = os.path.basename(photo_name)
                    logging.warning("    FAIL: media file %s was not found." %
                                    fn)
                    self.bad_photo.append(ObjectId)
                else:
                    if missmedia_action == 0:
                        logging.warning('    FAIL: media object "%(desc)s" '
                                        'reference to missing file "%(name)s" '
                                        'found' %
                                         {'desc' : photo_desc,
                                          'name' : photo_name})
                        mmd = MissingMediaDialog(
                            _("Media object could not be found"),
                            _("The file:\n%(file_name)s\nis referenced in "
                              "the database, but no longer exists.\n"
                              "The file may have been deleted or moved to "
                              "a different location.\n"
                              "You may choose to either remove the "
                              "reference from the database,\n"
                              "keep the reference to the missing file, "
                              "or select a new file."
                                  ) % {'file_name' : '<b>%s</b>' % photo_name},
                            remove_clicked, leave_clicked, select_clicked,
                            parent=self.uistate.window)
                        missmedia_action = mmd.default_action
                    elif missmedia_action == 1:
                        logging.warning('    FAIL: media object "%(desc)s" '
                                        'reference to missing file "%(name)s" '
                                        'found' %
                                        {'desc' : photo_desc,
                                         'name' : photo_name})
                        remove_clicked()
                    elif missmedia_action == 2:
                        logging.warning('    FAIL: media object "%(desc)s" '
                                        'reference to missing file "%(name)s" '
                                        'found' %
                                        {'desc' : photo_desc,
                                         'name' : photo_name})
                        leave_clicked()
                    elif missmedia_action == 3:
                        logging.warning('    FAIL: media object "%(desc)s" '
                                        'reference to missing file "%(name)s" '
                                        'found' %
                                        {'desc' : photo_desc,
                                         'name' : photo_name})
                        select_clicked()
            self.progress.step()
        if len(self.bad_photo + self.removed_photo) == 0:
            logging.info('    OK: no missing photos found')

    def cleanup_empty_objects(self):
        #the position of the change column in the primary objects
        CHANGE_PERSON = 17
        CHANGE_FAMILY = 12
        CHANGE_EVENT  = 10
        CHANGE_SOURCE = 8
        CHANGE_CITATION = 9
        CHANGE_PLACE  = 11
        CHANGE_MEDIA  = 8
        CHANGE_REPOS  = 7
        CHANGE_NOTE   = 5

        empty_person_data = Person().serialize()
        empty_family_data = Family().serialize()
        empty_event_data = Event().serialize()
        empty_source_data = Source().serialize()
        empty_citation_data = Citation().serialize()
        empty_place_data = Place().serialize()
        empty_media_data = Media().serialize()
        empty_repos_data = Repository().serialize()
        empty_note_data = Note().serialize()

        _db = self.db
        def _empty(empty, flag):
            ''' Closure for dispatch table, below '''
            def _f(value):
                return self._check_empty(value, empty, flag)
            return _f

        table = (

            # Dispatch table for cleaning up empty objects. Each entry is
            # a tuple containing:
            #    0. Type of object being cleaned up
            #    1. function to read the object from the database
            #    2. function returning cursor over the object type
            #    3. function returning number of objects of this type
            #    4. text identifying the object being cleaned up
            #    5. function to check if the data is empty
            #    6. function to remove the object, if empty

            ('persons',
                _db.get_person_from_handle,
                _db.get_person_cursor,
                _db.get_number_of_people,
                _('Looking for empty people records'),
                _empty(empty_person_data, CHANGE_PERSON),
                _db.remove_person,
                ),
            ('families',
                _db.get_family_from_handle,
                _db.get_family_cursor,
                _db.get_number_of_families,
                _('Looking for empty family records'),
                _empty(empty_family_data, CHANGE_FAMILY),
                _db.remove_family,
                ),
            ('events',
                _db.get_event_from_handle,
                _db.get_event_cursor,
                _db.get_number_of_events,
                _('Looking for empty event records'),
                _empty(empty_event_data, CHANGE_EVENT),
                _db.remove_event,
                ),
            ('sources',
                _db.get_source_from_handle,
                _db.get_source_cursor,
                _db.get_number_of_sources,
                _('Looking for empty source records'),
                _empty(empty_source_data, CHANGE_SOURCE),
                _db.remove_source,
                ),
            ('citations',
                _db.get_citation_from_handle,
                _db.get_citation_cursor,
                _db.get_number_of_citations,
                _('Looking for empty citation records'),
                _empty(empty_citation_data, CHANGE_CITATION),
                _db.remove_citation,
                ),
            ('places',
                _db.get_place_from_handle,
                _db.get_place_cursor,
                _db.get_number_of_places,
                _('Looking for empty place records'),
                _empty(empty_place_data, CHANGE_PLACE),
                _db.remove_place,
                ),
            ('media',
                _db.get_media_from_handle,
                _db.get_media_cursor,
                _db.get_number_of_media,
                _('Looking for empty media records'),
                _empty(empty_media_data, CHANGE_MEDIA),
                _db.remove_media,
                ),
            ('repos',
                _db.get_repository_from_handle,
                _db.get_repository_cursor,
                _db.get_number_of_repositories,
                _('Looking for empty repository records'),
                _empty(empty_repos_data, CHANGE_REPOS),
                _db.remove_repository,
                ),
            ('notes',
                _db.get_note_from_handle,
                _db.get_note_cursor,
                _db.get_number_of_notes,
                _('Looking for empty note records'),
                _empty(empty_note_data, CHANGE_NOTE),
                _db.remove_note,
                ),
            )

        # Now, iterate over the table, dispatching the functions

        for (the_type, get_func, cursor_func, total_func,
             text, check_func, remove_func) in table:

            with cursor_func() as cursor:
                total = total_func()
                self.progress.set_pass(text, total)
                logging.info(text)

                for handle, data in cursor:
                    self.progress.step()
                    if check_func(data):
                        # we cannot remove here as that would destroy cursor
                        # so save the handles for later removal
                        logging.warning('    FAIL: empty %(type)s record with '
                                        'handle "%(hand)s" was found' %
                                        {'type' : the_type, 'hand' : handle})
                        self.empty_objects[the_type].append(handle)

            #now remove
            for handle in self.empty_objects[the_type]:
                remove_func(handle, self.trans)
            if len(self.empty_objects[the_type]) == 0:
                logging.info('    OK: no empty %s found' % the_type)

    def _check_empty(self, data, empty_data, changepos):
        """compare the data with the data of an empty object
            change, handle and gramps_id are not compared """
        if changepos is not None:
            return (data[2:changepos] == empty_data[2:changepos] and
                    data[changepos+1:] == empty_data[changepos+1:]
                   )
        else :
            return data[2:] == empty_data[2:]

    def cleanup_empty_families(self, automatic):

        fhandle_list = self.db.get_family_handles()

        self.progress.set_pass(_('Looking for empty families'),
                               len(fhandle_list))
        logging.info('Looking for empty families')
        previous_errors = len(self.empty_family)
        for bfamily_handle in fhandle_list:
            family_handle = bfamily_handle.decode('utf-8')
            self.progress.step()

            family = self.db.get_family_from_handle(family_handle)
            family_id = family.get_gramps_id()
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()

            if not father_handle and not mother_handle and \
                   len(family.get_child_ref_list()) == 0:
                self.empty_family.append(family_id)
                self.delete_empty_family(family_handle)

        if previous_errors == len(self.empty_family):
            logging.info('    OK: no empty families found')

    def delete_empty_family(self, family_handle):
        for key in self.db.get_person_handles(sort_handles=False):
            child = self.db.get_person_from_handle(key)
            changed = False
            changed |= child.remove_parent_family_handle(family_handle)
            changed |= child.remove_family_handle(family_handle)
            if changed:
                self.db.commit_person(child, self.trans)
        self.db.remove_family(family_handle, self.trans)

    def check_parent_relationships(self):
        """Repair father=female or mother=male in hetero families
        """

        fhandle_list = self.db.get_family_handles()
        self.progress.set_pass(_('Looking for broken parent relationships'),
                               len(fhandle_list))
        logging.info('Looking for broken parent relationships')
        previous_errors = len(self.fam_rel)

        for bfamily_handle in fhandle_list:
            family_handle = bfamily_handle.decode('utf-8')
            self.progress.step()
            family = self.db.get_family_from_handle(family_handle)

            father_handle = family.get_father_handle()
            if father_handle:
                fgender = self.db.get_person_from_handle(father_handle
                                                         ).get_gender()
            else:
                fgender = None

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mgender = self.db.get_person_from_handle(mother_handle
                                                         ).get_gender()
            else:
                mgender = None

            if (fgender == Person.FEMALE
                    or mgender == Person.MALE) and fgender != mgender:
                # swap. note: (at most) one handle may be None
                logging.warning('    FAIL: the family "%s" has a father=female or '
                    ' mother=male in a different sex family' % family.gramps_id)
                family.set_father_handle(mother_handle)
                family.set_mother_handle(father_handle)
                self.db.commit_family(family, self.trans)
                self.fam_rel.append(family_handle)

        if previous_errors == len(self.fam_rel):
            logging.info('    OK: no broken parent relationships found')

    def check_events(self):
        self.progress.set_pass(_('Looking for event problems'),
                               self.db.get_number_of_people()
                               +self.db.get_number_of_families())
        logging.info('Looking for event problems')

        for bkey in self.db.get_person_handles(sort_handles=False):
            key = bkey.decode('utf-8')
            self.progress.step()

            person = self.db.get_person_from_handle(key)
            birth_ref = person.get_birth_ref()
            none_handle = False
            if birth_ref:
                newref = birth_ref
                if birth_ref.ref is None:
                    none_handle = True
                    birth_ref.ref = create_id()
                birth_handle = birth_ref.ref
                try:
                    birth = self.db.get_event_from_handle(birth_handle)
                except HandleError:
                    # The birth event referenced by the birth handle
                    # does not exist in the database
                    # This is tested by TestcaseGenerator person "Broken11"
                    make_unknown(birth_handle, self.explanation.handle,
                            self.class_event, self.commit_event, self.trans,
                            type=EventType.BIRTH)
                    logging.warning('    FAIL: the person "%(gid)s" refers to '
                                    'a birth event "%(hand)s" which does not '
                                    'exist in the database' %
                                    {'gid' : person.gramps_id,
                                     'hand' : birth_handle})
                    self.invalid_events.add(key)
                else:
                    if int(birth.get_type()) != EventType.BIRTH:
                        # Birth event was not of the type "Birth"
                        # This is tested by TestcaseGenerator person "Broken14"
                        logging.warning('    FAIL: the person "%(gid)s" refers '
                                        'to a birth event which is of type '
                                        '"%(type)s" instead of Birth' %
                                        {'gid' : person.gramps_id,
                                         'type' : int(birth.get_type())})
                        birth.set_type(EventType(EventType.BIRTH))
                        self.db.commit_event(birth, self.trans)
                        self.invalid_birth_events.add(key)
            if none_handle:
                person.set_birth_ref(newref)
                self.db.commit_person(person, self.trans)

            none_handle = False
            death_ref = person.get_death_ref()
            if death_ref:
                newref = death_ref
                if death_ref.ref is None:
                    none_handle = True
                    death_ref.ref = create_id()
                death_handle = death_ref.ref
                try:
                    death = self.db.get_event_from_handle(death_handle)
                except HandleError:
                    # The death event referenced by the death handle
                    # does not exist in the database
                    # This is tested by TestcaseGenerator person "Broken12"
                    logging.warning('    FAIL: the person "%(gid)s" refers to '
                                    'a death event "%(hand)s" which does not '
                                    'exist in the database' %
                                    {'gid' : person.gramps_id,
                                     'hand' : death_handle})
                    make_unknown(death_handle, self.explanation.handle,
                            self.class_event, self.commit_event, self.trans,
                            type=EventType.DEATH)
                    self.invalid_events.add(key)
                else:
                    if int(death.get_type()) != EventType.DEATH:
                        # Death event was not of the type "Death"
                        # This is tested by TestcaseGenerator person "Broken15"
                        logging.warning('    FAIL: the person "%(gid)s" refers '
                                        'to a death event which is of type '
                                        '"%(type)s" instead of Death' %
                                        {'gid' : person.gramps_id,
                                         'type' : int(death.get_type())})
                        death.set_type(EventType(EventType.DEATH))
                        self.db.commit_event(death, self.trans)
                        self.invalid_death_events.add(key)
            if none_handle:
                person.set_death_ref(newref)
                self.db.commit_person(person, self.trans)

            none_handle = False
            newlist = []
            if person.get_event_ref_list():
                for event_ref in person.get_event_ref_list():
                    newlist.append(event_ref)
                    if event_ref.ref is None:
                        none_handle = True
                        event_ref.ref = create_id()
                    event_handle = event_ref.ref
                    try:
                        event = self.db.get_event_from_handle(event_handle)
                    except HandleError:
                        # The event referenced by the person
                        # does not exist in the database
                        #TODO: There is no better way?
                        # This is tested by TestcaseGenerator person "Broken11"
                        # This is tested by TestcaseGenerator person "Broken12"
                        # This is tested by TestcaseGenerator person "Broken13"
                        logging.warning('    FAIL: the person "%(gid)s" refers '
                                        'to an event "%(hand)s" which does not '
                                        'exist in the database' %
                                        { 'gid' : person.gramps_id,
                                         'hand' : event_handle})
                        make_unknown(event_handle,
                                self.explanation.handle, self.class_event,
                                self.commit_event, self.trans)
                        self.invalid_events.add(key)
                if none_handle:
                    person.set_event_ref_list(newlist)
                    self.db.commit_person(person, self.trans)
            elif not isinstance(person.get_event_ref_list(), list):
                # event_list is None or other garbage
                logging.warning('    FAIL: the person "%s" has an event ref list'
                    ' which is invalid' % (person.gramps_id))
                person.set_event_ref_list([])
                self.db.commit_person(person, self.trans)
                self.invalid_events.add(key)

        for bkey in self.db.get_family_handles():
            key = bkey.decode('utf-8')
            self.progress.step()
            family = self.db.get_family_from_handle(key)
            if family.get_event_ref_list():
                none_handle = False
                newlist = []
                for event_ref in family.get_event_ref_list():
                    newlist.append(event_ref)
                    if event_ref.ref is None:
                        none_handle = True
                        event_ref.ref = create_id()
                    event_handle = event_ref.ref
                    try:
                        event = self.db.get_event_from_handle(event_handle)
                    except HandleError:
                        # The event referenced by the family
                        # does not exist in the database
                        logging.warning('    FAIL: the family "%(gid)s" refers '
                                        'to an event "%(hand)s" which does not '
                                        'exist in the database' %
                                        {'gid' : family.gramps_id,
                                         'hand' : event_handle})
                        make_unknown(event_handle, self.explanation.handle,
                                self.class_event, self.commit_event, self.trans)
                        self.invalid_events.add(key)
                if none_handle:
                    family.set_event_ref_list(newlist)
                    self.db.commit_family(family, self.trans)
            elif not isinstance(family.get_event_ref_list(), list):
                # event_list is None or other garbage
                logging.warning('    FAIL: the family "%s" has an event ref list'
                    ' which is invalid' % (family.gramps_id))
                family.set_event_ref_list([])
                self.db.commit_family(family, self.trans)
                self.invalid_events.add(key)

        if len (self.invalid_birth_events) + len(self.invalid_death_events) +\
                len(self.invalid_events) == 0:
            logging.info('    OK: no event problems found')

    def check_person_references(self):
        plist = self.db.get_person_handles()

        self.progress.set_pass(_('Looking for person reference problems'),
                               len(plist))
        logging.info('Looking for person reference problems')

        for bkey in plist:
            key = bkey.decode('utf-8')
            self.progress.step()
            none_handle = False
            newlist = []
            person = self.db.get_person_from_handle(key)
            for pref in person.get_person_ref_list():
                newlist.append(pref)
                if pref.ref is None:
                    none_handle = True
                    pref.ref = create_id()
                try:
                    p = self.db.get_person_from_handle( pref.ref)
                except HandleError:
                    # The referenced person does not exist in the database
                    make_unknown(pref.ref, self.explanation.handle,
                            self.class_person, self.commit_person, self.trans)
                    self.invalid_person_references.add(key)
            if none_handle:
                person.set_person_ref_list(newlist)
                self.db.commit_person(person, self.trans)

        if len (self.invalid_person_references) == 0:
            logging.info('    OK: no event problems found')

    def check_family_references(self):
        plist = self.db.get_person_handles()

        self.progress.set_pass(_('Looking for family reference problems'),
                               len(plist))
        logging.info('Looking for family reference problems')

        for bkey in plist:
            key = bkey.decode('utf-8')
            self.progress.step()
            person = self.db.get_person_from_handle(key)
            for ordinance in person.get_lds_ord_list():
                family_handle = ordinance.get_family_handle()
                if family_handle:
                    try:
                        family = self.db.get_family_from_handle(family_handle)
                    except HandleError:
                        # The referenced family does not exist in the database
                        make_unknown(family_handle,
                                self.explanation.handle, self.class_family,
                                self.commit_family, self.trans, db=self.db)
                        self.invalid_family_references.add(key)

        if len (self.invalid_family_references) == 0:
            logging.info('    OK: no event problems found')

    def check_repo_references(self):
        slist = self.db.get_source_handles()

        self.progress.set_pass(_('Looking for repository reference problems'),
                               len(slist))
        logging.info('Looking for repository reference problems')

        for bkey in slist:
            key = bkey.decode('utf-8')
            self.progress.step()
            none_handle = False
            newlist = []
            source = self.db.get_source_from_handle(key)
            for reporef in source.get_reporef_list():
                newlist.append(reporef)
                if reporef.ref is None:
                    none_handle = True
                    reporef.ref = create_id()
                try:
                    r = self.db.get_repository_from_handle(reporef.ref)
                except HandleError:
                    # The referenced repository does not exist in the database
                    make_unknown(reporef.ref, self.explanation.handle,
                            self.class_repo, self.commit_repo, self.trans)
                    self.invalid_repo_references.add(key)
            if none_handle:
                source.set_reporef_list(newlist);
                self.db.commit_source(source, self.trans)

        if len (self.invalid_repo_references) == 0:
            logging.info('    OK: no repository reference problems found')

    def check_place_references(self):
        plist = self.db.get_person_handles()
        flist = self.db.get_family_handles()
        elist = self.db.get_event_handles()
        llist = self.db.get_place_handles()
        self.progress.set_pass(_('Looking for place reference problems'),
                               len(elist)+len(plist)+len(flist)+len(llist))
        logging.info('Looking for place reference problems')

        for bkey in llist:
            key = bkey.decode('utf-8')
            self.progress.step()
            none_handle = False
            newlist = []
            place = self.db.get_place_from_handle(key)
            for placeref in place.get_placeref_list():
                newlist.append(placeref)
                if placeref.ref is None:
                    none_handle = True
                    placeref.ref = create_id()
                try:
                    parent_place = self.db.get_place_from_handle(placeref.ref)
                except HandleError:
                    # The referenced place does not exist in the database
                    make_unknown(placeref.ref,
                            self.explanation.handle, self.class_place,
                            self.commit_place, self.trans)
                    logging.warning('    FAIL: the place "%(gid)s" refers '
                                    'to a parent place "%(hand)s" which '
                                    'does not exist in the database' %
                                    {'gid' : place.gramps_id,
                                        'hand' : placeref.ref})
                    self.invalid_place_references.add(key)
            if none_handle:
                place.set_placeref_list(newlist);
                self.db.commit_place(place, self.trans)

        # check persons -> the LdsOrd references a place
        for bkey in plist:
            key = bkey.decode('utf-8')
            self.progress.step()
            person = self.db.get_person_from_handle(key)
            for ordinance in person.lds_ord_list:
                place_handle = ordinance.get_place_handle()
                if place_handle:
                    try:
                        place = self.db.get_place_from_handle(place_handle)
                    except HandleError:
                        # The referenced place does not exist in the database
                        # This is tested by TestcaseGenerator person "Broken17"
                        # This is tested by TestcaseGenerator person "Broken18"
                        make_unknown(place_handle,
                                self.explanation.handle, self.class_place,
                                self.commit_place, self.trans)
                        logging.warning('    FAIL: the person "%(gid)s" refers '
                                        'to an LdsOrd place "%(hand)s" which '
                                        'does not exist in the database' %
                                        {'gid' : person.gramps_id,
                                         'hand' : place_handle})
                        self.invalid_place_references.add(key)
        # check families -> the LdsOrd references a place
        for bkey in flist:
            key = bkey.decode('utf-8')
            self.progress.step()
            family = self.db.get_family_from_handle(key)
            for ordinance in family.lds_ord_list:
                place_handle = ordinance.get_place_handle()
                if place_handle:
                    try:
                        place = self.db.get_place_from_handle(place_handle)
                    except HandleError:
                        # The referenced place does not exist in the database
                        make_unknown(place_handle,
                                self.explanation.handle, self.class_place,
                                self.commit_place, self.trans)
                        logging.warning('    FAIL: the family "%(gid)s" refers '
                                        'to an LdsOrd place "%(hand)s" which '
                                        'does not exist in the database' %
                                        {'gid' : family.gramps_id,
                                         'hand' : place_handle})
                        self.invalid_place_references.add(key)
        # check events
        for bkey in elist:
            key = bkey.decode('utf-8')
            self.progress.step()
            event = self.db.get_event_from_handle(key)
            place_handle = event.get_place_handle()
            if place_handle:
                try:
                    place = self.db.get_place_from_handle(place_handle)
                except HandleError:
                    # The referenced place does not exist in the database
                    make_unknown(place_handle,
                            self.explanation.handle, self.class_place,
                            self.commit_place, self.trans)
                    logging.warning('    FAIL: the event "%(gid)s" refers '
                                    'to an LdsOrd place "%(hand)s" which '
                                    'does not exist in the database' %
                                    {'gid' : event.gramps_id,
                                     'hand' : place_handle})
                    self.invalid_place_references.add(key)

        if len (self.invalid_place_references) == 0:
            logging.info('    OK: no place reference problems found')

    def check_citation_references(self):
        known_handles = [key.decode('utf-8') for key in
                                self.db.get_citation_handles()]

        total = (
                self.db.get_number_of_people() +
                self.db.get_number_of_families() +
                self.db.get_number_of_events() +
                self.db.get_number_of_places() +
                self.db.get_number_of_citations() +
                self.db.get_number_of_sources() +
                self.db.get_number_of_media() +
                self.db.get_number_of_repositories()
                )

        self.progress.set_pass(_('Looking for citation reference problems'),
                               total)
        logging.info('Looking for citation reference problems')

        for bhandle in self.db.person_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.person_map[bhandle]
            person = Person()
            person.unserialize(info)
            handle_list = person.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Citation':
                    if item[1] is None:
                        new_handle = create_id()
                        person.replace_citation_references(None, new_handle)
                        self.db.commit_person(person, self.trans)
                        self.invalid_citation_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_citation_references.add(item[1])

        for bhandle in self.db.family_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.family_map[bhandle]
            family = Family()
            family.unserialize(info)
            handle_list = family.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Citation':
                    if item[1] is None:
                        new_handle = create_id()
                        family.replace_citation_references(None, new_handle)
                        self.db.commit_family(family, self.trans)
                        self.invalid_citation_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_citation_references.add(item[1])

        for bhandle in self.db.place_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.place_map[bhandle]
            place = Place()
            place.unserialize(info)
            handle_list = place.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Citation':
                    if item[1] is None:
                        new_handle = create_id()
                        place.replace_citation_references(None, new_handle)
                        self.db.commit_place(place, self.trans)
                        self.invalid_citation_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_citation_references.add(item[1])

        for bhandle in self.db.citation_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.citation_map[bhandle]
            citation = Citation()
            citation.unserialize(info)
            handle_list = citation.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Citation':
                    if item[1] is None:
                        new_handle = create_id()
                        citation.replace_citation_references(None, new_handle)
                        self.db.commit_citation(citation, self.trans)
                        self.invalid_citation_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_citation_references.add(item[1])

        for bhandle in self.db.repository_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.repository_map[bhandle]
            repository = Repository()
            repository.unserialize(info)
            handle_list = repository.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Citation':
                    if item[1] is None:
                        new_handle = create_id()
                        repository.replace_citation_references(None, new_handle)
                        self.db.commit_repository(repository, self.trans)
                        self.invalid_citation_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_citation_references.add(item[1])

        for bhandle in self.db.media_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.media_map[bhandle]
            obj = Media()
            obj.unserialize(info)
            handle_list = obj.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Citation':
                    if item[1] is None:
                        new_handle = create_id()
                        obj.replace_citation_references(None, new_handle)
                        self.db.commit_media(obj, self.trans)
                        self.invalid_citation_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_citation_references.add(item[1])

        for bhandle in self.db.event_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.event_map[bhandle]
            event = Event()
            event.unserialize(info)
            handle_list = event.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Citation':
                    if item[1] is None:
                        new_handle = create_id()
                        event.replace_citation_references(None, new_handle)
                        self.db.commit_event(event, self.trans)
                        self.invalid_citation_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_citation_references.add(item[1])

        for bad_handle in self.invalid_citation_references:
            created = make_unknown(bad_handle, self.explanation.handle,
                        self.class_citation, self.commit_citation, self.trans,
                        source_class_func=self.class_source,
                        source_commit_func=self.commit_source,
                        source_class_arg=create_id())
            self.invalid_source_references.add(created[0].handle)

        if len(self.invalid_citation_references) == 0:
            logging.info('   OK: no citation reference problems found')

    def check_source_references(self):
        clist = self.db.get_citation_handles()
        self.progress.set_pass(_('Looking for source reference problems'),
                               len(clist))
        logging.info('Looking for source reference problems')

        for bkey in clist:
            key = bkey.decode('utf-8')
            self.progress.step()
            citation = self.db.get_citation_from_handle(key)
            source_handle = citation.get_reference_handle()
            if source_handle is None:
                source_handle = create_id()
                citation.set_reference_handle(source_handle)
                self.db.commit_citation(citation, self.trans)
            if source_handle:
                try:
                    source = self.db.get_source_from_handle(source_handle)
                except HandleError:
                    # The referenced source does not exist in the database
                    make_unknown(source_handle, self.explanation.handle,
                            self.class_source, self.commit_source, self.trans)
                    logging.warning('    FAIL: the citation "%(gid)s" refers '
                                    'to source "%(hand)s" which does not exist '
                                    'in the database' %
                                    {'gid' : citation.gramps_id,
                                     'hand' : source_handle})
                    self.invalid_source_references.add(key)
        if len(self.invalid_source_references) == 0:
            logging.info('   OK: no source reference problems found')

    def check_media_references(self):
        known_handles = [key.decode('utf-8') for key in
                            self.db.get_media_handles(False)]

        total = (
                self.db.get_number_of_people() +
                self.db.get_number_of_families() +
                self.db.get_number_of_events() +
                self.db.get_number_of_places() +
                self.db.get_number_of_citations() +
                self.db.get_number_of_sources()
                )

        self.progress.set_pass(_('Looking for media object reference problems'),
                               total)
        logging.info('Looking for media object reference problems')

        for bhandle in self.db.person_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.person_map[bhandle]
            person = Person()
            person.unserialize(info)
            handle_list = person.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Media':
                    if item[1] is None:
                        new_handle = create_id()
                        person.replace_media_references(None, new_handle)
                        self.db.commit_person(person, self.trans)
                        self.invalid_media_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_media_references.add(item[1])

        for bhandle in self.db.family_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.family_map[bhandle]
            family = Family()
            family.unserialize(info)
            handle_list = family.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Media':
                    if item[1] is None:
                        new_handle = create_id()
                        family.replace_media_references(None, new_handle)
                        self.db.commit_family(family, self.trans)
                        self.invalid_media_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_media_references.add(item[1])

        for bhandle in self.db.place_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.place_map[bhandle]
            place = Place()
            place.unserialize(info)
            handle_list = place.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Media':
                    if item[1] is None:
                        new_handle = create_id()
                        place.replace_media_references(None, new_handle)
                        self.db.commit_place(place, self.trans)
                        self.invalid_media_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_media_references.add(item[1])

        for bhandle in self.db.event_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.event_map[bhandle]
            event = Event()
            event.unserialize(info)
            handle_list = event.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Media':
                    if item[1] is None:
                        new_handle = create_id()
                        event.replace_media_references(None, new_handle)
                        self.db.commit_event(event, self.trans)
                        self.invalid_media_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_media_references.add(item[1])

        for bhandle in self.db.citation_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.citation_map[bhandle]
            citation = Citation()
            citation.unserialize(info)
            handle_list = citation.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Media':
                    if item[1] is None:
                        new_handle = create_id()
                        citation.replace_media_references(None, new_handle)
                        self.db.commit_citation(citation, self.trans)
                        self.invalid_media_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_media_references.add(item[1])

        for bhandle in self.db.source_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.source_map[bhandle]
            source = Source()
            source.unserialize(info)
            handle_list = source.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Media':
                    if item[1] is None:
                        new_handle = create_id()
                        source.replace_media_references(None, new_handle)
                        self.db.commit_source(source, self.trans)
                        self.invalid_media_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_media_references.add(item[1])

        for bad_handle in self.invalid_media_references:
            make_unknown(bad_handle, self.explanation.handle,
                               self.class_media, self.commit_media, self.trans)

        if len (self.invalid_media_references) == 0:
            logging.info('    OK: no media reference problems found')

    def check_note_references(self):
        # Here I assume check note_references runs after all the next checks.
        missing_references = (len(self.invalid_person_references) +
                len(self.invalid_family_references) +
                len(self.invalid_birth_events) +
                len(self.invalid_death_events) +
                len(self.invalid_events) +
                len(self.invalid_place_references) +
                len(self.invalid_citation_references) +
                len(self.invalid_source_references) +
                len(self.invalid_repo_references) +
                len(self.invalid_media_references))
        if missing_references:
            self.db.add_note(self.explanation, self.trans, set_gid=True)

        known_handles = [key.decode('utf-8') for key in
                                    self.db.get_note_handles()]
        bad_handles = []

        total = (
                self.db.get_number_of_people() +
                self.db.get_number_of_families() +
                self.db.get_number_of_events() +
                self.db.get_number_of_places() +
                self.db.get_number_of_media() +
                self.db.get_number_of_citations() +
                self.db.get_number_of_sources() +
                self.db.get_number_of_repositories()
                )

        self.progress.set_pass(_('Looking for note reference problems'),
                               total)
        logging.info('Looking for note reference problems')

        for bhandle in self.db.person_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.person_map[bhandle]
            person = Person()
            person.unserialize(info)
            handle_list = person.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        person.replace_note_references(None, new_handle)
                        self.db.commit_person(person, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bhandle in self.db.family_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.family_map[bhandle]
            family = Family()
            family.unserialize(info)
            handle_list = family.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        family.replace_note_references(None, new_handle)
                        self.db.commit_family(family, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bhandle in self.db.place_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.place_map[bhandle]
            place = Place()
            place.unserialize(info)
            handle_list = place.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        place.replace_note_references(None, new_handle)
                        self.db.commit_place(place, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bhandle in self.db.citation_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.citation_map[bhandle]
            citation = Citation()
            citation.unserialize(info)
            handle_list = citation.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        citation.replace_note_references(None, new_handle)
                        self.db.commit_citation(citation, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bhandle in self.db.source_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.source_map[bhandle]
            source = Source()
            source.unserialize(info)
            handle_list = source.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        source.replace_note_references(None, new_handle)
                        self.db.commit_source(source, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bhandle in self.db.media_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.media_map[bhandle]
            obj = Media()
            obj.unserialize(info)
            handle_list = obj.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        obj.replace_note_references(None, new_handle)
                        self.db.commit_media(obj, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bhandle in self.db.event_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.event_map[bhandle]
            event = Event()
            event.unserialize(info)
            handle_list = event.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        event.replace_note_references(None, new_handle)
                        self.db.commit_event(event, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bhandle in self.db.repository_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.repository_map[bhandle]
            repo = Repository()
            repo.unserialize(info)
            handle_list = repo.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Note':
                    if item[1] is None:
                        new_handle = create_id()
                        repo.replace_note_references(None, new_handle)
                        self.db.commit_repository(repo, self.trans)
                        self.invalid_note_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_note_references.add(item[1])

        for bad_handle in self.invalid_note_references:
            make_unknown(bad_handle, self.explanation.handle,
                               self.class_note, self.commit_note, self.trans)

        if len (self.invalid_note_references) == 0:
            logging.info('    OK: no note reference problems found')
        else:
            if not missing_references:
                self.db.add_note(self.explanation, self.trans, set_gid=True)

    def check_checksum(self):
        self.progress.set_pass(_('Updating checksums on media'),
                               len(self.db.get_media_handles()))
        for bObjectId in self.db.get_media_handles():
            self.progress.step()
            ObjectId = bObjectId.decode('utf-8')
            obj = self.db.get_media_from_handle(ObjectId)
            full_path = media_path_full(self.db, obj.get_path())
            new_checksum = create_checksum(full_path)
            if new_checksum != obj.checksum:
                logging.info('checksum: updating ' + obj.gramps_id)
                obj.checksum = new_checksum
                self.db.commit_media(obj, self.trans)

    def check_tag_references(self):
        known_handles = [key.decode('utf-8') for key in
                                    self.db.get_tag_handles()]

        total = (
                self.db.get_number_of_people() +
                self.db.get_number_of_families() +
                self.db.get_number_of_media() +
                self.db.get_number_of_notes()
                )

        self.progress.set_pass(_('Looking for tag reference problems'),
                               total)
        logging.info('Looking for tag reference problems')

        for bhandle in self.db.person_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.person_map[bhandle]
            person = Person()
            person.unserialize(info)
            handle_list = person.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Tag':
                    if item[1] is None:
                        new_handle = create_id()
                        person.replace_tag_references(None, new_handle)
                        self.db.commit_person(person, self.trans)
                        self.invalid_tag_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_tag_references.add(item[1])

        for bhandle in self.db.family_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.family_map[bhandle]
            family = Family()
            family.unserialize(info)
            handle_list = family.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Tag':
                    if item[1] is None:
                        new_handle = create_id()
                        family.replace_tag_references(None, new_handle)
                        self.db.commit_family(family, self.trans)
                        self.invalid_tag_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_tag_references.add(item[1])

        for bhandle in self.db.media_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.media_map[bhandle]
            obj = Media()
            obj.unserialize(info)
            handle_list = obj.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Tag':
                    if item[1] is None:
                        new_handle = create_id()
                        obj.replace_tag_references(None, new_handle)
                        self.db.commit_media(obj, self.trans)
                        self.invalid_tag_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_tag_references.add(item[1])

        for bhandle in self.db.note_map.keys():
            handle = bhandle.decode('utf-8')
            self.progress.step()
            info = self.db.note_map[bhandle]
            note = Note()
            note.unserialize(info)
            handle_list = note.get_referenced_handles_recursively()
            for item in handle_list:
                if item[0] == 'Tag':
                    if item[1] is None:
                        new_handle = create_id()
                        note.replace_tag_references(None, new_handle)
                        self.db.commit_note(note, self.trans)
                        self.invalid_tag_references.add(new_handle)
                    elif item[1] not in known_handles:
                        self.invalid_tag_references.add(item[1])

        for bad_handle in self.invalid_tag_references:
            make_unknown(bad_handle, None, self.class_tag,
                               self.commit_tag, self.trans)

        if len(self.invalid_tag_references) == 0:
            logging.info('   OK: no tag reference problems found')

    def check_media_sourceref(self):
        """
        This repairs a problem with database upgrade from database schema
        version 15 to 16. Mediarefs on source primary objects can contain
        sourcerefs, and these were not converted to citations.
        """
        total = (
                self.db.get_number_of_sources()
                )

        self.progress.set_pass(_('Looking for media source reference problems'),
                               total)
        logging.info('Looking for media source reference problems')

        for handle in self.db.source_map.keys():
            self.progress.step()
            info = self.db.source_map[handle]
            source = Source()
            source.unserialize(info)
            new_media_ref_list = []
            for media_ref in source.get_media_list():
                citation_list = media_ref.get_citation_list()
                new_citation_list = []
                for citation_handle in citation_list:
                    # Either citation_handle is a handle, in which case it has
                    # been converted, or it is a 6-tuple, in which case it now
                    # needs to be converted.
                    if len(citation_handle) == 6:
                        if len(citation_handle) == 6:
                            sourceref = citation_handle
                        else:
                            sourceref = eval(citation_handle)
                        new_citation = Citation()
                        new_citation.set_date_object(sourceref[0])
                        new_citation.set_privacy(sourceref[1])
                        new_citation.set_note_list(sourceref[2])
                        new_citation.set_confidence_level(sourceref[3])
                        new_citation.set_reference_handle(sourceref[4])
                        new_citation.set_page(sourceref[5])
                        citation_handle = create_id()
                        new_citation.set_handle(citation_handle)
                        self.replaced_sourceref.append(handle)
                        logging.warning('    FAIL: the source "%s" has a media '
                                        'reference with a source citation '
                                        'which is invalid' % (source.gramps_id))
                        self.db.add_citation(new_citation, self.trans)

                    new_citation_list.append(citation_handle)

                media_ref.set_citation_list(new_citation_list)
                new_media_ref_list.append(media_ref)

            source.set_media_list(new_media_ref_list)
            self.db.commit_source(source, self.trans)

        if len(self.replaced_sourceref) > 0:
            logging.info('    OK: no broken source citations on mediarefs found')

    def class_person(self, handle):
        person = Person()
        person.set_handle(handle)
        return person

    def commit_person(self, person, trans, change):
        self.db.add_person(person, trans, set_gid=True)

    def class_family(self, handle):
        family = Family()
        family.set_handle(handle)
        return family

    def commit_family(self, family, trans, change):
        self.db.add_family(family, trans, set_gid=True)

    def class_event(self, handle):
        event = Event()
        event.set_handle(handle)
        return event

    def commit_event(self, event, trans, change):
        self.db.add_event(event, trans, set_gid=True)

    def class_place(self, handle):
        place = Place()
        place.set_handle(handle)
        return place

    def commit_place(self, place, trans, change):
        self.db.add_place(place, trans, set_gid=True)

    def class_source(self, handle):
        source = Source()
        source.set_handle(handle)
        return source

    def commit_source(self, source, trans, change):
        self.db.add_source(source, trans, set_gid=True)

    def class_citation(self, handle):
        citation = Citation()
        citation.set_handle(handle)
        return citation

    def commit_citation(self, citation, trans, change):
        self.db.add_citation(citation, trans, set_gid=True)

    def class_repo(self, handle):
        repo = Repository()
        repo.set_handle(handle)
        return repo

    def commit_repo(self, repo, trans, change):
        self.db.add_repository(repo, trans, set_gid=True)

    def class_media(self, handle):
        object = Media()
        object.set_handle(handle)
        return object

    def commit_media(self, object, trans, change):
        self.db.add_media(object, trans, set_gid=True)

    def class_note(self, handle):
        note = Note()
        note.set_handle(handle)
        return note

    def commit_note(self, note, trans, change):
        self.db.add_note(note, trans, set_gid=True)

    def class_tag(self, handle):
        tag = Tag()
        tag.set_handle(handle)
        return tag

    def commit_tag(self, tag, trans, change):
        self.db.add_tag(tag, trans)

    def build_report(self, uistate=None):
        self.progress.close()
        bad_photos = len(self.bad_photo)
        replaced_photos = len(self.replaced_photo)
        removed_photos = len(self.removed_photo)
        photos = bad_photos + replaced_photos + removed_photos
        efam = len(self.empty_family)
        blink = len(self.broken_links)
        plink = len(self.broken_parent_links)
        slink = len(self.duplicate_links)
        rel = len(self.fam_rel)
        event_invalid = len(self.invalid_events)
        birth_invalid = len(self.invalid_birth_events)
        death_invalid = len(self.invalid_death_events)
        person = birth_invalid + death_invalid
        person_references = len(self.invalid_person_references)
        family_references = len(self.invalid_family_references)
        invalid_dates = len(self.invalid_dates)
        place_references = len(self.invalid_place_references)
        citation_references = len(self.invalid_citation_references)
        source_references = len(self.invalid_source_references)
        repo_references = len(self.invalid_repo_references)
        media_references = len(self.invalid_media_references)
        note_references = len(self.invalid_note_references)
        tag_references = len(self.invalid_tag_references)
        name_format = len(self.removed_name_format)
        replaced_sourcerefs = len(self.replaced_sourceref)
        empty_objs = sum(len(obj) for obj in self.empty_objects.values())

        errors = (photos + efam + blink + plink + slink + rel +
                  event_invalid + person +
                  person_references  + family_references + place_references +
                  citation_references + repo_references + media_references  +
                  note_references + tag_references + name_format + empty_objs +
                  invalid_dates + source_references
                 )

        if errors == 0:
            if uistate:
                OkDialog(_("No errors were found"),
                         _('The database has passed internal checks'),
                         parent=uistate.window)
            else:
                print(_("No errors were found: the database has passed internal checks."))
            return 0

        self.text = StringIO()
        if blink > 0:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} broken child/family link was fixed\n",
                         "{quantity} broken child/family links were fixed\n",
                         blink).format(quantity=blink)
                )
            for (person_handle, family_handle) in self.broken_links:
                try:
                    person = self.db.get_person_from_handle(person_handle)
                except HandleError:
                    cn = _("Non existing child")
                else:
                    cn = person.get_primary_name().get_name()
                try:
                    family = self.db.get_family_from_handle(family_handle)
                except HandleError:
                    pn = _("Unknown")
                else:
                    pn = family_name(family, self.db)
                self.text.write('\t')
                self.text.write(
                    _("%(person)s was removed from the family of %(family)s\n")
                        % {'person': cn, 'family': pn}
                    )

        if plink > 0:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} broken spouse/family link was fixed\n",
                         "{quantity} broken spouse/family links were fixed\n",
                         plink).format(quantity=plink)
                )
            for (person_handle, family_handle) in self.broken_parent_links:
                try:
                    person = self.db.get_person_from_handle(person_handle)
                except HandleError:
                    cn = _("Non existing person")
                else:
                    cn = person.get_primary_name().get_name()
                try:
                    family = self.db.get_family_from_handle(family_handle)
                except HandleError:
                    pn = _("Unknown")
                else:
                    pn = family_name(family, self.db)
                self.text.write('\t')
                self.text.write(
                    _("%(person)s was restored to the family of %(family)s\n")
                        % {'person': cn, 'family': pn}
                    )

        if slink > 0:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} duplicate "
                             "spouse/family link was found\n",
                         "{quantity} duplicate "
                             "spouse/family links were found\n",
                         slink).format(quantity=slink)
                )
            for (person_handle, family_handle) in self.broken_parent_links:
                try:
                    person = self.db.get_person_from_handle(person_handle)
                except HandleError:
                    cn = _("Non existing person")
                else:
                    cn = person.get_primary_name().get_name()
                try:
                    family = self.db.get_family_from_handle(family_handle)
                except HandleError:
                    pn = _("None")
                else:
                    pn = family_name(family, self.db)
                self.text.write('\t')
                self.text.write(
                    _("%(person)s was restored to the family of %(family)s\n")
                        % {'person': cn, 'family': pn}
                    )

        if efam:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} family "
                             "with no parents or children found, removed.\n",
                         "{quantity} families "
                             "with no parents or children found, removed.\n",
                         efam).format(quantity=efam)
                )
            if efam == 1:
                self.text.write("\t%s\n" % self.empty_family[0])

        if rel:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} corrupted family relationship fixed\n",
                         "{quantity} corrupted family relationships fixed\n",
                         rel).format(quantity=rel)
                )

        if person_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext(
                    "{quantity} person was referenced but not found\n",
                    "{quantity} persons were referenced, but not found\n",
                    person_references).format(quantity=person_references)
                )

        if family_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} family was "
                             "referenced but not found\n",
                         "{quantity} families were "
                             "referenced, but not found\n",
                         family_references).format(quantity=family_references)
                )

        if invalid_dates:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} date was corrected\n",
                         "{quantity} dates were corrected\n",
                         invalid_dates).format(quantity=invalid_dates)
                )

        if repo_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext(
                    "{quantity} repository was "
                        "referenced but not found\n",
                    "{quantity} repositories were "
                        "referenced, but not found\n",
                    repo_references).format(quantity=repo_references)
                )

        if photos:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} media object was "
                             "referenced but not found\n",
                         "{quantity} media objects were "
                             "referenced, but not found\n",
                         photos).format(quantity=photos)
                )

        if bad_photos:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext(
                    "Reference to {quantity} missing media object was kept\n",
                    "References to {quantity} media objects were kept\n",
                    bad_photos).format(quantity=bad_photos)
                )

        if replaced_photos:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} missing media object was replaced\n",
                         "{quantity} missing media objects were replaced\n",
                         replaced_photos).format(quantity=replaced_photos)
                )

        if removed_photos:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} missing media object was removed\n",
                         "{quantity} missing media objects were removed\n",
                         removed_photos).format(quantity=removed_photos)
                )

        if event_invalid:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} event was referenced but not found\n",
                         "{quantity} events were referenced, but not found\n",
                         event_invalid).format(quantity=event_invalid)
                )

        if birth_invalid:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} invalid birth event name was fixed\n",
                         "{quantity} invalid birth event names were fixed\n",
                         birth_invalid).format(quantity=birth_invalid)
                )

        if death_invalid:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} invalid death event name was fixed\n",
                         "{quantity} invalid death event names were fixed\n",
                         death_invalid).format(quantity=death_invalid)
                )

        if place_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} place was referenced but not found\n",
                         "{quantity} places were referenced, but not found\n",
                         place_references).format(quantity=place_references)
                )

        if citation_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} citation was "
                             "referenced but not found\n",
                         "{quantity} citations were "
                             "referenced, but not found\n",
                         citation_references
                        ).format(quantity=citation_references)
                )

        if source_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} source was "
                             "referenced but not found\n",
                         "{quantity} sources were "
                             "referenced, but not found\n",
                         source_references).format(quantity=source_references)
                )

        if media_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} media object was "
                             "referenced but not found\n",
                         "{quantity} media objects were "
                             "referenced, but not found\n",
                         media_references).format(quantity=media_references)
                )

        if note_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} note object was "
                             "referenced but not found\n",
                         "{quantity} note objects were "
                             "referenced, but not found\n",
                         note_references).format(quantity=note_references)
                )

        if tag_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} tag object was "
                             "referenced but not found\n",
                         "{quantity} tag objects were "
                             "referenced, but not found\n",
                         tag_references).format(quantity=tag_references)
                )

        if tag_references:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} tag object was "
                             "referenced but not found\n",
                         "{quantity} tag objects were "
                             "referenced, but not found\n",
                         tag_references).format(quantity=tag_references)
                )

        if name_format:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} invalid name format "
                             "reference was removed\n",
                         "{quantity} invalid name format "
                             "references were removed\n",
                         name_format).format(quantity=name_format)
                )

        if replaced_sourcerefs:
            self.text.write(
                # translators: leave all/any {...} untranslated
                ngettext("{quantity} invalid source citation was fixed\n",
                         "{quantity} invalid source citations were fixed\n",
                         replaced_sourcerefs
                        ).format(quantity=replaced_sourcerefs)
                )

        if empty_objs > 0 :
            self.text.write(_("%(empty_obj)d empty objects removed:\n"
                              "   %(person)d person objects\n"
                              "   %(family)d family objects\n"
                              "   %(event)d event objects\n"
                              "   %(source)d source objects\n"
                              "   %(media)d media objects\n"
                              "   %(place)d place objects\n"
                              "   %(repo)d repository objects\n"
                              "   %(note)d note objects\n") % {
                                 'empty_obj' : empty_objs,
                                 'person' : len(self.empty_objects['persons']),
                                 'family' : len(self.empty_objects['families']),
                                 'event' : len(self.empty_objects['events']),
                                 'source' : len(self.empty_objects['sources']),
                                 'media' : len(self.empty_objects['media']),
                                 'place' : len(self.empty_objects['places']),
                                 'repo' : len(self.empty_objects['repos']),
                                 'note' : len(self.empty_objects['notes'])
                                 }
                            )

        return errors

#-------------------------------------------------------------------------
#
# Display the results
#
#-------------------------------------------------------------------------
class Report(ManagedWindow):

    def __init__(self, uistate, text, cl=0):
        if cl:
            print (text)

        if uistate:
            ManagedWindow.__init__(self, uistate, [], self)

            topDialog = Glade()
            topDialog.get_object("close").connect('clicked', self.close)
            window = topDialog.toplevel
            textwindow = topDialog.get_object("textwindow")
            textwindow.get_buffer().set_text(text)

            self.set_window(window,
                            #topDialog.get_widget("title"),
                            topDialog.get_object("title"),
                            _("Integrity Check Results"))

            self.show()

    def build_menu_names(self, obj):
        return (_('Check and Repair'), None)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class CheckOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
