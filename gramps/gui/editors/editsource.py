#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
import logging
log = logging.getLogger(".")
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk, Gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import NoteType, Source, SrcTemplate
from gramps.gen.db import DbTxn
from gramps.gen.utils.file import media_path_full
from ..thumbnails import get_thumbnail_image
from .editprimary import EditPrimary
from .editreference import RefTab
from .editmediaref import EditMediaRef

from .displaytabs import (NoteTab, GalleryTab, SrcAttrEmbedList,
                          SrcTemplateTab, CitedInTab,
                          CitationBackRefList, RepoEmbedList)
from ..widgets import MonitoredEntry, PrivacyButton, MonitoredTagList
from ..dialog import ErrorDialog
from ..utils import is_right_click, open_file_with_default_application
from ..glade import Glade

#-------------------------------------------------------------------------
#
# EditSource class
#
#-------------------------------------------------------------------------

class EditSource(EditPrimary):

    def __init__(self, dbstate, uistate, track, source):
        self.srctemp = None
        self.citation = None
        EditPrimary.__init__(self, dbstate, uistate, track, source, 
                             dbstate.db.get_source_from_handle, 
                             dbstate.db.get_source_from_gramps_id)

    def empty_object(self):
        return Source()

    def get_menu_title(self):
        title = self.obj.get_title()
        if title:
            title = _('Source') + ": " + title
        else:
            title = _('New Source')
        return title

    def _local_init(self):
        self.width_key = 'interface.source-width'
        self.height_key = 'interface.source-height'
        assert(self.obj)
        
        self.glade = Glade()
        self.set_window(self.glade.toplevel, None, 
                        self.get_menu_title())

        self.obj_photo = self.glade.get_object("sourcePix")
        self.frame_photo = self.glade.get_object("frame5")
        self.eventbox = self.glade.get_object("eventbox1")

    def _post_init(self):
        """
        Handle any initialization that needs to be done after the interface is
        brought up.

        Post initalization function.
        This is called by _EditPrimary's init routine, and overridden in the
        derived class (this class).

        """
        self.load_source_image()
        self.title.grab_focus()

    def load_source_image(self):
        """
        Load the primary image into the main form if it exists.

        Used as callback on Gallery Tab too.

        """
        media_list = self.obj.get_media_list()
        if media_list:
            ref = media_list[0]
            handle = ref.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(handle)
            if obj is None :
                #notify user of error
                from ..dialog import RunDatabaseRepair
                RunDatabaseRepair(
                            _('Non existing media found in the Gallery'))
            else:
                self.load_photo(ref, obj)
        else:
            self.obj_photo.hide()
            self.frame_photo.hide()

    def load_photo(self, ref, obj):
        """
        Load the source's main photo using the Thumbnailer.
        """
        pixbuf = get_thumbnail_image(
                        media_path_full(self.dbstate.db, obj.get_path()), 
                        obj.get_mime_type(),
                        ref.get_rectangle())

        self.obj_photo.set_from_pixbuf(pixbuf)
        self.obj_photo.show()
        self.frame_photo.show_all()

    def _connect_signals(self):
        self.define_ok_button(self.glade.get_object('ok'),self.save)
        self.define_cancel_button(self.glade.get_object('cancel'))
        self.define_help_button(self.glade.get_object('help'))
        self.eventbox.connect('button-press-event',
                                self._image_button_press)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('source-rebuild', self._do_close)
        self._add_db_signal('source-delete', self.check_for_close)
        self._add_db_signal('note-delete', self.update_notes)
        self._add_db_signal('note-update', self.update_notes)
        self._add_db_signal('note-add', self.update_notes)
        self._add_db_signal('note-rebuild', self.update_notes)

    def _setup_fields(self):
##        self.author = MonitoredEntry(self.glade.get_object("author"),
##                                     self.obj.set_author, self.obj.get_author,
##                                     self.db.readonly)
##
##        self.pubinfo = MonitoredEntry(self.glade.get_object("pubinfo"),
##                                      self.obj.set_publication_info,
##                                      self.obj.get_publication_info,
##                                      self.db.readonly)
        #reference info fields
        self.refL = self.glade.get_object("refL")
        self.refF = self.glade.get_object("refF")
        self.refS = self.glade.get_object("refS")
        self.author = self.glade.get_object("author")
        self.pubinfo = self.glade.get_object("pubinfo")
        self.source_text =  self.glade.get_object("source_text")

        self.gid = MonitoredEntry(self.glade.get_object("gid"),
                                  self.obj.set_gramps_id, 
                                  self.obj.get_gramps_id, self.db.readonly)

        self.tags = MonitoredTagList(self.glade.get_object("tag_label"), 
                                     self.glade.get_object("tag_button"), 
                                     self.obj.set_tag_list, 
                                     self.obj.get_tag_list,
                                     self.db,
                                     self.uistate, self.track,
                                     self.db.readonly)

        self.priv = PrivacyButton(self.glade.get_object("private"), self.obj, 
                                  self.db.readonly)

        self.abbrev = MonitoredEntry(self.glade.get_object("abbrev"),
                                     self.obj.set_abbreviation,
                                     self.obj.get_abbreviation, 
                                     self.db.readonly)

        self.title = MonitoredEntry(self.glade.get_object("source_title"),
                                    self.obj.set_title, self.obj.get_title,
                                    self.db.readonly)

        self.update_attr()
        self.update_notes()

    def update_attr(self):
        """
        Reaction to update on attributes
        """
        #we only construct once the template to use to format information
        if self.srctemp is None:
            self.srctemp = SrcTemplate(self.obj.get_source_template()[0])
        #if source template changed, reinit template
        if self.obj.get_source_template()[0] != self.srctemp.get_template_key():
            self.srctemp.set_template_key(self.obj.get_source_template()[0])
        #set new attrlist in template
        self.srctemp.set_attr_list(self.obj.get_attribute_list())
        
        #set fields with the template
        self.refL.set_text(self.srctemp.reference_L())
        if self.citation:
            self.refF.set_text(self.srctemp.reference_F())
            self.refS.set_text(self.srctemp.reference_S())
        else:
            self.refF.set_text(_("<no citation loaded>"))
            self.refS.set_text(_("<no citation loaded>"))
        self.author.set_text(self.srctemp.author_gedcom())
        self.pubinfo.set_text(self.srctemp.pubinfo_gedcom())

    def update_template_data(self):
        """
        Change in the template tab must be reflected in other places
        """
        if self.attr_tab:
            self.attr_tab.rebuild_callback()
        self.update_attr()

    def update_notes(self, *par):
        """
        Change the source text on the overview page when notebase of the source
        changed
        """
        note_list = [ self.db.get_note_from_handle(h) 
                      for h in self.obj.get_note_list() ]
        note_list = [ n for n in note_list 
                      if n.get_type() == NoteType.SOURCE_TEXT]
        ref_text = ""
        for note in note_list:
            ref_text += note_list[0].get() + "\n"
        self.source_text.get_buffer().set_text(ref_text)

    def _create_tabbed_pages(self):
        notebook = self.glade.get_object('notebook')
        gridsrc =  self.glade.get_object('gridsrc')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.overviewtab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('Overview'), gridsrc)
        self._add_tab(notebook, self.overviewtab)

        #recreate second page as GrampsTab
        notebook.remove_page(0)
        self.attr_tab = None
        self.template_tab = SrcTemplateTab(self.dbstate, self.uistate,
                                self.track, self.obj, self.glade,
                                self.update_template_data
                                )
        self._add_tab(notebook, self.template_tab)
        self.track_ref_for_deletion("template_tab")

        self.note_tab = NoteTab(self.dbstate,
                                self.uistate,
                                self.track,
                                self.obj.get_note_list(),
                                self.get_menu_title(),
                                NoteType.SOURCE,
                                callback_notebase_changed=self.update_notes)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.gallery_tab = GalleryTab(self.dbstate,
                                      self.uistate,
                                      self.track,
                                      self.obj.get_media_list(),
                                      self.load_source_image)
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")

        self.repo_tab = RepoEmbedList(self.dbstate,
                                      self.uistate,
                                      self.track,
                                      self.obj.get_reporef_list())
        self._add_tab(notebook, self.repo_tab)
        self.track_ref_for_deletion("repo_tab")

        self.attr_tab = SrcAttrEmbedList(self.dbstate,
                                         self.uistate,
                                         self.track,
                                         self.obj.get_attribute_list())
        self._add_tab(notebook, self.attr_tab)
        self.track_ref_for_deletion("attr_tab")

        self.citedin_tab = CitedInTab(self.dbstate, self.uistate,
                                 self.track, self.obj)
        self._add_tab(notebook, self.citedin_tab)
        self.track_ref_for_deletion("citedin_tab")

        self.backref_list = CitationBackRefList(self.dbstate,
                                              self.uistate,
                                              self.track,
                              self.db.find_backlink_handles(self.obj.handle))
        self.backref_tab = self._add_tab(notebook, self.backref_list)
        self.track_ref_for_deletion("backref_tab")
        self.track_ref_for_deletion("backref_list")
        
        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.glade.get_object('vbox').pack_start(notebook, True, True, 0)

    def build_menu_names(self, source):
        return (_('Edit Source'), self.get_menu_title())        

    def _image_button_press(self, obj, event):
        """
        Button press event that is caught when a button has been pressed while
        on the image on the main form.

        This does not apply to the images in galleries, just the image on the
        main form.
        """
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:

            media_list = self.obj.get_media_list()
            if media_list:
                media_ref = media_list[0]
                object_handle = media_ref.get_reference_handle()
                media_obj = self.db.get_object_from_handle(object_handle)

                try:
                    EditMediaRef(self.dbstate, self.uistate, self.track,
                                 media_obj, media_ref, self.load_photo)
                except WindowActiveError:
                    pass

        elif is_right_click(event):
            media_list = self.obj.get_media_list()
            if media_list:
                photo = media_list[0]
                self._show_popup(photo, event)
        #do not propagate further:
        return True

    def _show_popup(self, photo, event):
        """
        Look for right-clicks on a picture and create a popup menu of the
        available actions.
        """
        self.imgmenu = Gtk.Menu()
        menu = self.imgmenu
        menu.set_title(_("Media Object"))
        obj = self.db.get_object_from_handle(photo.get_reference_handle())
        if obj:
            add_menuitem(menu, _("View"), photo,
                                   self._popup_view_photo)
        add_menuitem(menu, _("Edit Object Properties"), photo,
                               self._popup_change_description)
        menu.popup(None, None, None, None, event.button, event.time)

    def _popup_view_photo(self, obj):
        """
        Open this picture in the default picture viewer.
        """
        media_list = self.obj.get_media_list()
        if media_list:
            photo = media_list[0]
            object_handle = photo.get_reference_handle()
            ref_obj = self.db.get_object_from_handle(object_handle)
            photo_path = media_path_full(self.db, ref_obj.get_path())
            open_file_with_default_application(photo_path)

    def _popup_change_description(self, obj):
        """
        Bring up the EditMediaRef dialog for the image on the main form.
        """
        media_list = self.obj.get_media_list()
        if media_list:
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            media_obj = self.db.get_object_from_handle(object_handle)
            EditMediaRef(self.dbstate, self.uistate, self.track,
                         media_obj, media_ref, self.load_photo)

    def save(self, *obj):
        self.ok_button.set_sensitive(False)
        if self.object_is_empty():
            ErrorDialog(_("Cannot save source"),
                        _("No data exists for this source. Please "
                          "enter data or cancel the edit."))
            self.ok_button.set_sensitive(True)
            return
        
        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(id)
            name = prim_object.get_title()
            msg1 = _("Cannot save source. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(id)s. This value is already used by '" 
                         "%(prim_object)s'. Please enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id, 'prim_object' : name }
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return

        with DbTxn('', self.db) as trans:
            if not self.obj.get_handle():
                self.db.add_source(self.obj, trans)
                msg = _("Add Source (%s)") % self.obj.get_title()
            else:
                if not self.obj.get_gramps_id():
                    self.obj.set_gramps_id(self.db.find_next_source_gramps_id())
                self.db.commit_source(self.obj, trans)
                msg = _("Edit Source (%s)") % self.obj.get_title()
            trans.set_description(msg)
                        
        self.close()

class DeleteSrcQuery(object):
    def __init__(self, dbstate, uistate, source, the_lists):
        self.source = source
        self.db = dbstate.db
        self.uistate = uistate
        self.the_lists = the_lists

    def query_response(self):
        with DbTxn(_("Delete Source (%s)") % self.source.get_title(),
                   self.db) as trans:
            self.db.disable_signals()
            
            # we can have:
            # object(CitationBase) -> Citation(source_handle) -> Source
            # We first have to remove the CitationBase references to the 
            # Citation. Then we remove the Citations. (We don't need to 
            # remove the source_handle references to the Source, because we are
            # removing the whole Citation). Then we can remove the Source
        
            (citation_list, citation_referents_list) = self.the_lists
            # citation_list is a tuple of lists. Only the first, for Citations,
            # exists.
            citation_list = citation_list[0]

            # (1) delete the references to the citation
            for (citation_handle, refs) in citation_referents_list:
                LOG.debug('delete citation %s references %s' % 
                          (citation_handle, refs))
                (person_list, family_list, event_list, place_list, source_list, 
                 media_list, repo_list) = refs
                 
                ctn_handle_list = [citation_handle]
                
                for handle in person_list:
                    person = self.db.get_person_from_handle(handle)
                    person.remove_citation_references(ctn_handle_list)
                    self.db.commit_person(person, trans)
    
                for handle in family_list:
                    family = self.db.get_family_from_handle(handle)
                    family.remove_citation_references(ctn_handle_list)
                    self.db.commit_family(family, trans)
    
                for handle in event_list:
                    event = self.db.get_event_from_handle(handle)
                    event.remove_citation_references(ctn_handle_list)
                    self.db.commit_event(event, trans)
    
                for handle in place_list:
                    place = self.db.get_place_from_handle(handle)
                    place.remove_citation_references(ctn_handle_list)
                    self.db.commit_place(place, trans)
    
                for handle in source_list:
                    source = self.db.get_source_from_handle(handle)
                    source.remove_citation_references(ctn_handle_list)
                    self.db.commit_source(source, trans)
    
                for handle in media_list:
                    media = self.db.get_object_from_handle(handle)
                    media.remove_citation_references(ctn_handle_list)
                    self.db.commit_media_object(media, trans)
    
                for handle in repo_list:
                    repo = self.db.get_repository_from_handle(handle)
                    repo.remove_citation_references(ctn_handle_list)
                    self.db.commit_repository(repo, trans)

            # (2) delete the actual citations
            LOG.debug('remove the actual citations %s' % citation_list)
            for citation_handle in citation_list:
                LOG.debug("remove_citation %s" % citation_handle)
                self.db.remove_citation(citation_handle, trans)
            
            # (3) delete the source
            self.db.enable_signals()
            self.db.remove_source(self.source.get_handle(), trans)
