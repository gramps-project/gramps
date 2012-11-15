#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons, Nick Hall
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

"""
EditCitation class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.ggettext import gettext as _
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Citation, NoteType, Source
from gramps.gen.db import DbTxn
from .editprimary import EditPrimary

from .displaytabs import (NoteTab, GalleryTab, DataEmbedList,
                         SourceBackRefList, RepoEmbedList, CitationBackRefList)
from ..widgets import (MonitoredEntry, PrivacyButton, MonitoredMenu,
                        MonitoredDate)
from ..dialog import ErrorDialog
from .editreference import RefTab
from ..glade import Glade

#-------------------------------------------------------------------------
#
# EditCitationclass
#
#-------------------------------------------------------------------------

class EditCitation(EditPrimary):
    """
    Create an EditCitation window. Associate a citation with the window.
    
    This class is called both to edit the Citation Primary object
    and to edit references from other objects to citations.
    It is called from ..editors.__init__ for editing the primary object
    and is called from CitationEmbedList for editing references
    
    @param callertitle: Text passed by calling object to add to title 
    @type callertitle: str
    """

    def __init__(self, dbstate, uistate, track, obj, source=None, callback=None,
                 callertitle = None):
        """
        The obj parameter is mandatory. If the source parameter is not 
        provided, it will be deduced from the obj Citation object.
        """
        if not source and obj.get_reference_handle():
            source = dbstate.db.get_source_from_handle(
                                              obj.get_reference_handle())
        self.source = source
        self.callertitle = callertitle
        EditPrimary.__init__(self, dbstate, uistate, track, obj, 
                             dbstate.db.get_citation_from_handle, 
                             dbstate.db.get_citation_from_gramps_id, callback)
        # FIXME: EitPrimary calls ManagedWindow.__init__, which checks whether 
        # a window is already open which is editing obj. However, for 
        # EditCitation, not only do we need to protect obj (which will be
        # a Citation, but we also need to protect the associated Source.

    def build_window_key(self, obj):
        """
        Return a key for the edit window that is opened.
        This function overrides the build_window_key in EditPrimary.
        
        There is a problem with database object locking. The database locking is
        handled by the ManagedWindow class, which will only allow one primary
        object to be edited at a time.

        Normally, the window key is derived from the obj that is being edited.
        However, in the case of EditCitation, there are two objects being
        edited, the Citation and the Source. Both must be protected against
        against the user trying to edit them twice.
        
        What we do here is to derive the window key from the Source object, if
        one exists. A Citation always points to exactly one Source object, so if
        we try to edit the same Citation twice, the associated Source objects
        will be the same so this will be prevented. If we try to edit a Source
        object and a Citation object that refers to the same Source, then again,
        the window key will be the same and this will be prevented.
        """
        if obj and obj.get_reference_handle():
            # citation already points to source
            return obj.get_reference_handle()
        elif self.source and self.source.get_handle():
            # Citation doesn't yet point to source, but source exists and has a
            # handle
            return self.source.get_handle()
        else:
            return id(self)

    def empty_object(self):
        """
        Return an empty Citation object for comparison for changes.
        
        It is used by the base class L{EditPrimary}.
        """
        return Citation()

    def get_menu_title(self):
        """
        Construct the menu title, which may include the name of the object that
        contains a reference to this citation.
        """
        title = self.obj.get_page()
        if title:
            if self.callertitle:
                title = _('Citation') + \
                        (': %(id)s - %(context)s' % {
                         'id'      : title,
                         'context' : self.callertitle
                         })
            else:
                title = _('Citation') + ": " + title
        else:
            if self.callertitle:
                title = _('New Citation') + \
                        (': %(id)s - %(context)s' % {
                         'id'      : title,
                         'context' : self.callertitle
                         })
            else:     
                title = _('New Citation')
        return title

    # The functions define_warn_box, enable_warn_box and define_expander
    # are normally inherited from editreference,
    # but have to be defined here because this class inherits from 
    # EditPrimary instead
    def define_warn_box(self, box):
        self.warn_box = box

    def enable_warnbox(self):
        self.warn_box.show()

    def define_warn_box2(self, box):
        self.warn_box2 = box

    def enable_warnbox2(self):
        self.warn_box2.show()

    def define_expander(self, expander):
        expander.set_expanded(True)

    def _local_init(self):
        """Local initialization function.
        
        Perform basic initialization, including setting up widgets
        and the glade interface. It is called by the base class L{EditPrimary},
        and overridden here.
        
        """
        self.width_key = 'interface.citation-width'
        self.height_key = 'interface.citation-height'
        assert(self.obj)
        
        self.glade = Glade()
        self.set_window(self.glade.toplevel, None, 
                        self.get_menu_title())
        
        self.define_warn_box(self.glade.get_object("warn_box"))
        self.define_warn_box2(self.glade.get_object("warn_box2"))
        self.define_expander(self.glade.get_object("src_expander"))

        tblref =  self.glade.get_object('table67')
        notebook = self.glade.get_object('notebook_ref')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)
        tblref =  self.glade.get_object('table68')
        notebook = self.glade.get_object('notebook_src')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.primtab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)

    def _post_init(self):
        title = self.glade.get_object('title')
        volume = self.glade.get_object('volume')
        if not title.get_text_length():
            title.grab_focus();
        elif not volume.get_text_length():
            volume.grab_focus(); 

    def _connect_signals(self):
        """Connects any signals that need to be connected.
        
        Called by the init routine of the base class L{EditPrimary}.
        """
        self.define_ok_button(self.glade.get_object('ok'), self.save)
        self.define_cancel_button(self.glade.get_object('cancel'))
        self.define_help_button(self.glade.get_object('help'))

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
                
        What this code does is to check that the object edited is not deleted
        whilst editing it.  If the object is deleted we need to close the editor
        windows and clean up.  If the database emits a rebuild signal for the
        database object type we also abort the edit.

        The Citation editor edits two primary objects, and therefore we need to
        check if either have been deleted.  If the source is deleted, the
        citation must have been deleted first and will emit a signal, so we
        shouldn't have to connect to the source-delete signal.  It should not be
        necessary to connect to the source- rebuild signal for similar reasons.
        """
        
        self._add_db_signal('citation-rebuild', self._do_close)
        self._add_db_signal('citation-delete', self.check_for_close)

    def _setup_fields(self):
        """Get control widgets and attach them to Citation's attributes."""
        
        # Populate the Citation section
        
        self.date = MonitoredDate(
            self.glade.get_object("date_entry"),
            self.glade.get_object("date_stat"), 
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.glade.get_object('gid2'), self.obj.set_gramps_id,
            self.obj.get_gramps_id,self.db.readonly)

        self.volume = MonitoredEntry(
            self.glade.get_object("volume"), self.obj.set_page,
            self.obj.get_page, self.db.readonly)
        
        self.type_mon = MonitoredMenu(
            self.glade.get_object('confidence'),
            self.obj.set_confidence_level,
            self.obj.get_confidence_level, [
            (_('Very Low'), Citation.CONF_VERY_LOW),
            (_('Low'), Citation.CONF_LOW),
            (_('Normal'), Citation.CONF_NORMAL),
            (_('High'), Citation.CONF_HIGH),
            (_('Very High'), Citation.CONF_VERY_HIGH)],
            self.db.readonly)

        self.ref_privacy = PrivacyButton(
            self.glade.get_object('privacy'), self.obj, self.db.readonly)
        
        # Populate the Source section
        
        self.title = MonitoredEntry(
            self.glade.get_object('title'), 
            self.source.set_title,
            self.source.get_title,
            self.db.readonly)
        
        self.author = MonitoredEntry(
            self.glade.get_object('author'), self.source.set_author,
            self.source.get_author,self.db.readonly)
        
        self.gid = MonitoredEntry(
            self.glade.get_object('gid'), self.source.set_gramps_id,
            self.source.get_gramps_id,self.db.readonly)

        self.source_privacy = PrivacyButton(
            self.glade.get_object("private"),
            self.source, self.db.readonly)

        self.abbrev = MonitoredEntry(
            self.glade.get_object('abbrev'), self.source.set_abbreviation,
            self.source.get_abbreviation,self.db.readonly)

        self.pubinfo = MonitoredEntry(
            self.glade.get_object('pub_info'), self.source.set_publication_info,
            self.source.get_publication_info,self.db.readonly)

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """
        # create notebook tabs for Citation
        
        notebook_ref = self.glade.get_object('notebook_ref')
        self._add_tab(notebook_ref, self.reftab)

        self.comment_tab = NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_list(), self.get_menu_title(),
                    notetype=NoteType.CITATION)
        self._add_tab(notebook_ref, self.comment_tab)
        self.track_ref_for_deletion("comment_tab")

        self.gallery_tab = GalleryTab(self.dbstate, self.uistate, self.track,
                       self.obj.get_media_list())
        self._add_tab(notebook_ref, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")
            
        self.data_tab = DataEmbedList(self.dbstate, self.uistate, self.track,
                          self.obj)
        self._add_tab(notebook_ref, self.data_tab)
        self.track_ref_for_deletion("data_tab")
            
        self.citationref_list = CitationBackRefList(self.dbstate, self.uistate, 
                              self.track,
                              self.db.find_backlink_handles(self.obj.handle),
                              self.enable_warnbox2)
        self._add_tab(notebook_ref, self.citationref_list)
        self.track_ref_for_deletion("citationref_list")

        # Create notebook tabs for Source
        
        notebook_src = self.glade.get_object('notebook_src')
        
        self._add_tab(notebook_src, self.primtab)
        
        self.note_tab = NoteTab(self.dbstate, self.uistate, self.track,
                                self.source.get_note_list(), 
                                self.get_menu_title(),
                                notetype=NoteType.SOURCE)
        self._add_tab(notebook_src, self.note_tab)
        self.track_ref_for_deletion("note_tab")
            
        self.gallery_tab = GalleryTab(self.dbstate, self.uistate, self.track,
                       self.source.get_media_list())
        self._add_tab(notebook_src, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")
            
        self.data_tab = DataEmbedList(self.dbstate, self.uistate, self.track,
                          self.source)
        self._add_tab(notebook_src, self.data_tab)
        self.track_ref_for_deletion("data_tab")
            
        self.repo_tab = RepoEmbedList(self.dbstate, self.uistate, self.track,
                          self.source.get_reporef_list())
        self._add_tab(notebook_src, self.repo_tab)
        self.track_ref_for_deletion("repo_tab")
            
        self.srcref_list = SourceBackRefList(self.dbstate, self.uistate, 
                              self.track,
                              self.db.find_backlink_handles(self.source.handle),
                              self.enable_warnbox)
        self._add_tab(notebook_src, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self._setup_notebook_tabs(notebook_src)
        self._setup_notebook_tabs(notebook_ref)

    def build_menu_names(self, source):
        """
        Provide the information needed by the base class to define the
        window management menu entries.
        """
        return (_('Edit Citation'), self.get_menu_title())        

    def save(self, *obj):
        """Save the data."""
        self.ok_button.set_sensitive(False)
        if self.source_is_empty(self.source):
            ErrorDialog(_("Cannot save source"),
                        _("No data exists for this source. Please "
                          "enter data or cancel the edit."))
            self.ok_button.set_sensitive(True)
            return
        
        (uses_dupe_id, gramps_id) = self._uses_duplicate_id()
        if uses_dupe_id:
            prim_object = self.get_from_gramps_id(gramps_id)
            name = prim_object.get_page()
            msg1 = _("Cannot save citation. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                     "value %(gramps_id)s. This value is already used by '" 
                     "%(prim_object)s'. Please enter a different ID or leave "
                     "blank to get the next available ID value.") % {
                         'gramps_id' : gramps_id, 'prim_object' : name }
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, gramps_id) = self.source_uses_duplicate_id(self.source)
        if uses_dupe_id:
            prim_object = self.db.get_source_from_gramps_id(gramps_id)
            name = prim_object.get_title()
            msg1 = _("Cannot save source. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                     "value %(gramps_id)s. This value is already used by '" 
                     "%(prim_object)s'. Please enter a different ID or leave "
                     "blank to get the next available ID value.") % {
                         'gramps_id' : gramps_id, 'prim_object' : name }
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return

        with DbTxn('', self.db) as trans:
            # First commit the Source Primary object
            if not self.source.get_handle():
                self.db.add_source(self.source, trans)
                msg = _("Add Source (%s)") % self.source.get_title()
            else:
                if not self.source.get_gramps_id():
                    self.source.set_gramps_id(
                                    self.db.find_next_source_gramps_id())
                self.db.commit_source(self.source, trans)
                msg = _("Edit Source (%s)") % self.source.get_title()

            self.obj.set_reference_handle(self.source.handle)
            
            # Now commit the Citation Primary object
            if not self.obj.get_handle():
                self.db.add_citation(self.obj, trans)
                msg += "\n" + _("Add Citation (%s)") % self.obj.get_page()
            else:
                if not self.obj.get_gramps_id():
                    self.obj.set_gramps_id(
                                    self.db.find_next_citation_gramps_id())
                self.db.commit_citation(self.obj, trans)
                msg += "\n" + _("Edit Citation (%s)") % self.obj.get_page()
            trans.set_description(msg)
                        
        if self.callback:
            self.callback(self.obj.get_handle())
        self.close()

    def source_is_empty(self, obj):
        empty_object = Source()
        return obj.serialize()[1:] == empty_object.serialize()[1:]
    
    def source_uses_duplicate_id(self, obj):
        """
        Check whether a changed or added GRAMPS ID already exists in the DB.
        
        Return True if a duplicate GRAMPS ID has been detected.
        
        """
        original = self.db.get_source_from_handle(obj.get_handle())
        if original and original.get_gramps_id() == obj.get_gramps_id():
            return (False, 0)
        else:
            idval = obj.get_gramps_id()
            if self.db.get_source_from_gramps_id(idval):
                return (True, idval)
            return (False, 0)
            
    def data_has_changed(self):
        return self.citation_data_has_changed() or \
                self.source_data_has_changed()
    
    def citation_data_has_changed(self):
        """
        This checks whether the citation data has changed
        
        A date comparison can fail incorrectly because we have made the
        decision to store entered text in the date. However, there is no
        entered date when importing from a XML file, so we can get an
        incorrect fail.
        """
        if self.db.readonly:
            return False
        elif self.obj.handle:
            orig = self.get_from_handle(self.obj.handle)
            if orig:
                cmp_obj = orig
            else:
                cmp_obj = self.empty_object()
            return cmp_obj.serialize(True)[1:] != self.obj.serialize(True)[1:]
        else:
            cmp_obj = self.empty_object()
            return cmp_obj.serialize(True)[1:] != self.obj.serialize()[1:]

    def source_data_has_changed(self):
        """
        This checks whether the source data has changed
        """
        if self.db.readonly:
            return False
        elif self.source.handle:
            orig = self.db.get_source_from_handle(self.source.handle)
            if orig:
                cmp_obj = orig
            else:
                cmp_obj = Source()
            return cmp_obj.serialize()[1:] != self.source.serialize()[1:]
        else:
            cmp_obj = Source()
            return cmp_obj.serialize()[1:] != self.source.serialize()[1:]

class DeleteCitationQuery(object):
    def __init__(self, dbstate, uistate, citation, the_lists):
        self.citation = citation
        self.db = dbstate.db
        self.uistate = uistate
        self.the_lists = the_lists

    def query_response(self):
        with DbTxn(_("Delete Citation (%s)") % self.citation.get_page(),
                   self.db) as trans:
            self.db.disable_signals()
        
            (person_list, family_list, event_list, place_list, source_list, 
             media_list, repo_list) = self.the_lists

            ctn_handle_list = [self.citation.get_handle()]

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

            self.db.enable_signals()
            self.db.remove_citation(self.citation.get_handle(), trans)
