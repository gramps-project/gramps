#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"Database Processing/Check and repair database"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import cStringIO
import shutil

#-------------------------------------------------------------------------
#
# gtk modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gtk modules
#
#-------------------------------------------------------------------------
import RelLib
import Utils

from gettext import gettext as _
from QuestionDialog import OkDialog, MissingMediaDialog

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback,parent=None):

    try:
        checker = CheckIntegrity(database,parent)
        checker.check_for_broken_family_links()
        checker.cleanup_missing_photos(0)
        checker.check_parent_relationships()
        checker.cleanup_empty_families(0)
        errs = checker.build_report(0)
        if errs:
            checker.report(0)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class CheckIntegrity:
    
    def __init__(self,db,parent):
        self.db = db
        self.bad_photo = []
        self.replaced_photo = []
        self.removed_photo = []
        self.empty_family = []
        self.broken_links = []
        self.broken_parent_links = []
        self.fam_rel = []

    def check_for_broken_family_links(self):
        self.broken_links = []
        for family_id in self.db.get_family_keys():
            family = self.db.find_family_from_id(family_id)
            father_id = family.get_father_id()
            mother_id = family.get_mother_id()
            if father_id:
                father = self.db.find_person_from_id(father_id)
            if mother_id:
                mother = self.db.find_person_from_id(mother_id)

            if father_id and family_id not in father.get_family_id_list():
                self.broken_parent_links.append((father_id,family_id))
                father.add_family_id(family_id)
                self.db.commit_person(father)
            if mother_id and family_id not in mother.get_family_id_list():
                self.broken_parent_links.append((mother_id,family_id))
                mother.add_family_id(family_id)
                self.db.commit_person(mother)
            for child_id in family.get_child_id_list():
                child = self.db.find_person_from_id(child_id)
                if family_id == child.get_main_parents_family_id():
                    continue
                for family_type in child.get_parent_family_id_list():
                    if family_type[0] == family_id:
                        break
                else:
                    family.remove_child_id(child_id)
                    self.db.commit_family(family)
                    self.broken_links.append((child_id,family_id))

    def cleanup_missing_photos(self,cl=0):
        missmedia_action = 0
        #-------------------------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            for person_id in self.db.get_family_keys():
                p = self.db.find_family_from_id(person_id)
                nl = p.get_media_list()
                changed = 0
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        changed = 1
                        nl.remove(o)
                if changed:
                    p.set_media_list(nl)
                    self.db.commit_person(p)
                    
            for key in self.db.get_person_keys():
                p = self.db.find_person_from_id(key)
                nl = p.get_media_list()
                changed = 0
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        changed = 1
                        nl.remove(o)
                if changed:
                    p.set_media_list(nl)
                    self.db.commit_person(p)
                    
            for key in self.db.get_source_keys():
                p = self.db.find_source_from_id(key)
                nl = p.get_media_list()
                changed = 0
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        changed = 1
                        nl.remove(o)
                if changed:
                    p.set_media_list(nl)
                    self.db.commit_source(p)
                
            for key in self.db.get_place_id_keys():
                p = self.db.get_place_id(key)
                nl = p.get_media_list()
                changed = 0
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        changed = 1
                        nl.remove(o)
                if changed:
                    p.set_media_list(nl)
                    self.db.commit_place(p)
            self.removed_photo.append(ObjectId)
            self.db.remove_object(ObjectId) 
    
        def leave_clicked():
            self.bad_photo.append(ObjectId)

        def select_clicked():
            # File is lost => select a file to replace the lost one
            def fs_close_window(obj):
                self.bad_photo.append(ObjectId)

            def fs_ok_clicked(obj):
                name = fs_top.get_filename()
                if os.path.isfile(name):
                    shutil.copyfile(name,photo_name)
                    try:
                        shutil.copystat(name,photo_name)
                    except:
                        pass
                    self.replaced_photo.append(ObjectId)
                else:
                    self.bad_photo.append(ObjectId)

            fs_top = gtk.FileSelection("%s - GRAMPS" % _("Select file"))
            fs_top.hide_fileop_buttons()
            fs_top.ok_button.connect('clicked',fs_ok_clicked)
            fs_top.cancel_button.connect('clicked',fs_close_window)
            fs_top.run()
            fs_top.destroy()

        #-------------------------------------------------------------------------
        
        for ObjectId in self.db.get_object_keys():
            obj = self.db.find_object_from_id(ObjectId)
            photo_name = obj.get_path()
            if not os.path.isfile(photo_name):
                if cl:
                    print "Warning: media file %s was not found." \
                        % os.path.basename(photo_name)
                    self.bad_photo.append(ObjectId)
                else:
                    if missmedia_action == 0:
                        mmd = MissingMediaDialog(_("Media object could not be found"),
                        _("%(file_name)s is referenced in the database, but no longer exists. " 
                        "The file may have been deleted or moved to a different location. " 
                        "You may choose to either remove the reference from the database, " 
                        "keep the reference to the missing file, or select a new file." 
                        ) % { 'file_name' : photo_name },
                            remove_clicked, leave_clicked, select_clicked)
                        missmedia_action = mmd.default_action
                    elif missmedia_action == 1:
                        remove_clicked()
                    elif missmedia_action == 2:
                        leave_clicked()
                    elif missmedia_action == 3:
                        select_clicked()

    def cleanup_empty_families(self,automatic):
        for key in self.db.get_family_keys():
            family = self.db.find_family_from_id(key)
            if not family.get_father_id() and not family.get_mother_id():
                self.empty_family.append(family_id)
                self.delete_empty_family(family_id)

    def delete_empty_family(self,family_id):
        for key in self.db.get_person_keys():
            child = self.db.find_person_from_id(key)
            child.remove_parent_family_id(family_id)
            child.remove_family_id(family_id)
        self.db.delete_family(family_id)

    def check_parent_relationships(self):
        for key in self.db.get_family_keys():
            family = self.db.find_family_from_id(key)
            mother_id = family.get_mother_id()
            father_id = family.get_father_id()
            if father_id:
            	father = self.db.find_person_from_id(father_id)
            if mother_id:
                mother = self.db.find_person_from_id(mother_id)
            type = family.get_relationship()

            if not father_id and not mother_id:
                continue
            elif not father_id:
                if mother.get_gender() == RelLib.Person.male:
                    family.set_father_id(mother_id)
                    family.set_mother_id(None)
                    self.db.commit_family(family)
            elif not mother_id:
                if father.get_gender() == RelLib.Person.female:
                    family.set_mother_id(father_id)
                    family.set_father_id(None)
                    self.db.commit_family(family)
            else:
                fgender = father.get_gender()
                mgender = mother.get_gender()
                if type != "Partners":
                    if fgender == mgender and fgender != RelLib.Person.unknown:
                        family.set_relationship("Partners")
                        self.fam_rel.append(family_id)
                        self.db.commit_family(family)
                    elif fgender == RelLib.Person.female or mgender == RelLib.Person.male:
                        family.set_father_id(mother_id)
                        family.set_mother_id(father_id)
                        self.fam_rel.append(family_id)
                        self.db.commit_family(family)
                elif fgender != mgender:
                    family.set_relationship("Unknown")
                    self.fam_rel.append(family_id)
                    if fgender == RelLib.Person.female or mgender == RelLib.Person.male:
                        family.set_father_id(mother_id)
                        family.set_mother_id(father_id)
                    self.db.commit_family(family)

    def build_report(self,cl=0):
        bad_photos = len(self.bad_photo)
        replaced_photos = len(self.replaced_photo)
        removed_photos = len(self.removed_photo)
        photos = bad_photos + replaced_photos + removed_photos
        efam = len(self.empty_family)
        blink = len(self.broken_links)
        plink = len(self.broken_parent_links)
        rel = len(self.fam_rel)

        errors = blink + efam + photos + rel
        
        if errors == 0:
            if cl:
                print "No errors were found: the database has passed internal checks."
            else:
                OkDialog(_("No errors were found"),
                         _('The database has passed internal checks'))
            return 0

        self.text = cStringIO.StringIO()
        if blink > 0:
            if blink == 1:
                self.text.write(_("1 broken child/family link was fixed\n"))
            else:
                self.text.write(_("%d broken child/family links were found\n") % blink)
            for (person_id,family_id) in self.broken_links:
                person = self.db.find_person_from_id(person_id)
                family = self.db.find_family_from_id(family_id)
                cn = person.get_primary_name().get_name()
                f = self.db.find_person_from_id(family.get_father_id())
                m = self.db.find_person_from_id(family.get_mother_id())
                if f and m:
                    pn = _("%s and %s") % (f.get_primary_name().get_name(),\
                                           m.get_primary_name().get_name())
                elif f:
                    pn = f.get_primary_name().get_name()
                elif m:
                    pn = m.get_primary_name().get_name()
                else:
                    pn = _("unknown")
                self.text.write('\t')
                self.text.write(_("%s was removed from the family of %s\n") % (cn,pn))

        if plink > 0:
            if plink == 1:
                self.text.write(_("1 broken spouse/family link was fixed\n"))
            else:
                self.text.write(_("%d broken spouse/family links were found\n") % plink)
            for (person_id,family_id) in self.broken_parent_links:
                person = self.db.find_person_from_id(person_id)
                family = self.db.find_family_from_id(family_id)
                cn = person.get_primary_name().get_name()
                f = self.db.find_person_from_id(family.get_father_id())
                m = self.db.find_person_from_id(family.get_mother_id())
                if f and m:
                    pn = _("%s and %s") % (f.get_primary_name().get_name(),\
                                           m.get_primary_name().get_name())
                elif f:
                    pn = f.get_primary_name().get_name()
                else:
                    pn = m.get_primary_name().get_name()
                    self.text.write('\t')
                    self.text.write(_("%s was restored to the family of %s\n") % (cn,pn))

        if efam == 1:
            self.text.write(_("1 empty family was found\n"))
        elif efam > 1:
            self.text.write(_("%d empty families were found\n") % efam)
        if rel == 1:
            self.text.write(_("1 corrupted family relationship fixed\n"))
        elif rel > 1:
            self.text.write(_("%d corrupted family relationship fixed\n") % rel)
        if photos == 1:
            self.text.write(_("1 media object was referenced, but not found\n"))
        elif photos > 1:
            self.text.write(_("%d media objects were referenced, but not found\n") % photos)
        if bad_photos == 1:
            self.text.write(_("Reference to 1 missing media object was kept\n"))
        elif bad_photos > 1:
            self.text.write(_("References to %d media objects were kept\n") % bad_photos)
        if replaced_photos == 1:
            self.text.write(_("1 missing media object was replaced\n"))
        elif replaced_photos > 1:
            self.text.write(_("%d missing media objects were replaced\n") % replaced_photos)
        if removed_photos == 1:
            self.text.write(_("1 missing media object was removed\n"))
        elif removed_photos > 1:
            self.text.write(_("%d missing media objects were removed\n") % removed_photos)

        return errors

    def report(self,cl=0):
        if cl:
            print self.text.getvalue()
        else:
            base = os.path.dirname(__file__)
            glade_file = base + os.sep + "summary.glade"
            topDialog = gtk.glade.XML(glade_file,"summary","gramps")
            topDialog.signal_autoconnect({
                "destroy_passed_object" : Utils.destroy_passed_object,
                })
            title = _("Check Integrity")
            top = topDialog.get_widget("summary")
            textwindow = topDialog.get_widget("textwindow")

            Utils.set_titles(top,topDialog.get_widget("title"),title)
            textwindow.get_buffer().set_text(self.text.getvalue())
            self.text.close()
            top.show()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Check and repair database"),
    category=_("Database Processing"),
    description=_("Checks the database for integrity problems, fixing the problems that it can")
    )
