#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011-2013  Tim G L Lyons
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
LOG = logging.getLogger(".template")

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
from gramps.gen.lib import NoteType, Source, SrcTemplate, Citation, SrcTemplateList
from gramps.gen.db import DbTxn
from gramps.gen.utils.file import media_path_full
from ..thumbnails import get_thumbnail_image
from .editprimary import EditPrimary
from .editreference import RefTab
from .editmediaref import EditMediaRef

from .displaytabs import (NoteTab, GalleryTab, SrcAttrEmbedList,
                          SrcTemplateTab, CitedInTab,
                          CitationBackRefList, RepoEmbedList)
from .displaytabs.srctemplatetab import TemplateFields
from ..widgets import (MonitoredEntry, PrivacyButton, MonitoredTagList,
                       MonitoredMenu)
from ..dialog import ErrorDialog, QuestionDialog2
from ..utils import is_right_click, open_file_with_default_application
from ..glade import Glade

#-------------------------------------------------------------------------
#
# EditSource class
#
#-------------------------------------------------------------------------

FIRST = True
class EditSource(EditPrimary):

    def __init__(self, dbstate, uistate, track, source, citation=None,
                    callback=None,
                    callertitle = None):
        """
        Editor for source and citations of that source
        If source is not given, citation must be given, and the source of the
        citation will be used
        callback: function to call on save with the loaded citation handle. If
                    no citation is loaded, None will be used as handle. Caller
                    must handle this (corresponds to closing the editor with 
                    nothing made!)
        """
        # FIXME: Is there a cleaner place to initially load the template data?
        global FIRST
        if FIRST:
            LOG.debug("**** load csv data")
            from gramps.plugins.srctemplates.importcsv import load_srctemplates_data
            load_srctemplates_data()
            LOG.debug("**** csv data loaded\n\n")
            FIRST = False
        self.srctemp = None
        self.citation = citation
        self.template_tab = None
        self.attr_tab = None
        self.citation_loaded = True
        if not source and not citation:
            raise NotImplementedError
        elif not source:
            #citation will be used to obtain the source
            hsource = citation.get_reference_handle()
            source = dbstate.db.get_source_from_handle(hsource)
        elif citation:
            #source and citation are given, they MUST be connected or citation
            #must be a new object
            if citation.get_reference_handle() and \
                not (citation.get_reference_handle() == source.handle):
                raise Exception('Citation must be a Citation of the Source edited')
        else:
            #no citation given.
            self.citation_loaded = False
            #we put an empty base citation ready.
            self.citation = Citation()
        self.callertitle = callertitle

        self.citation_ready = False
        EditPrimary.__init__(self, dbstate, uistate, track, source, 
                             dbstate.db.get_source_from_handle, 
                             dbstate.db.get_source_from_gramps_id, callback)

    def empty_object(self):
        return Source()

    def get_menu_title(self):
        title = self.obj.get_title()
        if self.obj.get_handle():
            title = _('Source') + ": " + title
        else:
            title = _('New Source')
        if self.citation_loaded:
            citeid = self.citation.get_gramps_id()
            if self.citation.get_handle():
                if self.callertitle:
                    title = _('Citation: %(id)s - %(context)s' % {
                             'id'      : citeid,
                             'context' : self.callertitle
                             }) + ' ' + title
                else:
                    title = _('Citation') + ": " + citeid  + ' ' + title
            else:
                if self.callertitle:
                    title = _('New Citation - %(context)s' % {
                             'context' : self.callertitle
                             }) + ' ' + title
                else:     
                    title = _('New Citation') + ' ' + title
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
        self.notebook_ref = self.glade.get_object('notebook_citation')
        self.cinf = self.glade.get_object("cite_info_lbl")
        self.btnclose_cite = self.glade.get_object("btnclose_cite")
        self.tmplfields = None

        self.define_warn_box2(self.glade.get_object("warn_box2"))

    def _post_init(self):
        """
        Handle any initialization that needs to be done after the interface is
        brought up.

        Post initalization function.
        This is called by _EditPrimary's init routine, and overridden in the
        derived class (this class).

        """
        if not self.citation_loaded:
            self.unload_citation()

        self.load_source_image()
        if not self.obj.handle:
            #new source, open on template view, and focus there.
            self.notebook_src.set_current_page(self.template_page_nr)
            self.template_tab.make_active()
        elif self.citation_loaded:
            #there is a citation!
            if self.citation.handle:
                #existing citation!
                self.notebook_ref.grab_focus()
            else:
                #new citation!
                self.notebook_ref.grab_focus()
        else:
            #existing source, no citation
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
        self.define_ok_button(self.glade.get_object('ok'), self.save)
        self.define_cancel_button(self.glade.get_object('cancel'))
        self.define_help_button(self.glade.get_object('help'))
        self.btnclose_cite.connect('clicked', self.close_citation)
        self.eventbox.connect('button-press-event',
                                self._image_button_press)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('citation-rebuild', self._do_close)
        self._add_db_signal('citation-delete', self.check_for_close_cite)
        self._add_db_signal('source-rebuild', self._do_close)
        self._add_db_signal('source-delete', self.check_for_close)
        self._add_db_signal('note-delete', self.update_notes)
        self._add_db_signal('note-update', self.update_notes)
        self._add_db_signal('note-add', self.update_notes)
        self._add_db_signal('note-rebuild', self.update_notes)

    def check_for_close_cite(self, handles):
        """
        Callback method for delete signals. 
        If there is a delete signal of the citation object we are
        editing, the 
        editor (and all child windows spawned) should be closed
        """
        #citation, we only close if that citation is open
        if self.citation and self.citation.get_handle() in handles:
            self._do_close()
    
    def _setup_fields(self):
        #reference info fields of source
        self.refL = self.glade.get_object("refL")
        self.refF = self.glade.get_object("refF")
        self.refS = self.glade.get_object("refS")
        self.author = self.glade.get_object("author")
        self.pubinfo = self.glade.get_object("pubinfo")
        self.source_text =  self.glade.get_object("source_text")

        #editable source fields
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
                                    self.obj.set_name, self.obj.get_name,
                                    self.db.readonly)

        #editable citation fields
        self._setup_citation_fields()

        #trigger updates of read only fields
        self.update_attr()
        self.update_notes()

    def _setup_citation_fields(self):
        if self.citation_ready:
            raise Exception
        self.cname = MonitoredEntry(
            self.glade.get_object('cname'), self.citation.set_name,
            self.citation.get_name, self.db.readonly)

        self.gid2 = MonitoredEntry(
            self.glade.get_object('gid2'), self.citation.set_gramps_id,
            self.get_citation_gramps_id, self.db.readonly)

        self.type_mon = MonitoredMenu(
            self.glade.get_object('confidence'),
            self.citation.set_confidence_level,
            self.citation.get_confidence_level, [
            (_('Very Low'), Citation.CONF_VERY_LOW),
            (_('Low'), Citation.CONF_LOW),
            (_('Normal'), Citation.CONF_NORMAL),
            (_('High'), Citation.CONF_HIGH),
            (_('Very High'), Citation.CONF_VERY_HIGH)],
            self.db.readonly)

        self.tags2 = MonitoredTagList(
            self.glade.get_object("tag_label2"), 
            self.glade.get_object("tag_button2"), 
            self.citation.set_tag_list, 
            self.citation.get_tag_list,
            self.db,
            self.uistate, self.track,
            self.db.readonly)

        self.ref_privacy = PrivacyButton(
            self.glade.get_object('privacy'), self.citation, self.db.readonly)

    def get_citation_gramps_id(self):
        """
        Monitered entry on None does nothing, while get_gramps_id returns None
        for empty string! We convert here
        """
        val = self.citation.get_gramps_id()
        if val is None:
            return ''
        else:
            return val

    def update_attr(self):
        """
        Reaction to update on attributes
        """
        #we only construct once the template to use to format information
        if self.srctemp is None:
            self.srctemp = SrcTemplateList().get_template_from_name(self.obj.get_template())
        # FIXME: I am not sure what the code below was doing. The SrcTemplate
        # had been set from the name in the Src record, then a check was made as
        # to whether the old name from the Src record was the same as the name
        # of the template. But since the template was found from its name, this
        # must be the case.
        
#        #if source template changed, reinit template
#        if self.obj.get_template() != self.srctemp.get_template_key():
#            self.srctemp.set_template_key(self.obj.get_template())
        #set new attrlist in template
        if self.citation_loaded:
            citeattr = self.citation.get_attribute_list()
            citedate = self.citation.get_date_object()
        else:
            citeattr = None
            citedate = None
        self.srctemp.set_attr_list(self.obj.get_attribute_list(), citeattr,
                                   citedate)
        
        #set fields with the template
        self.refL.set_text(self.srctemp.reference_L())
        if self.citation_loaded:
            self.refF.set_text(self.srctemp.reference_F())
            self.refS.set_text(self.srctemp.reference_S())
        else:
            self.refF.set_text(_("<no citation loaded>"))
            self.refS.set_text(_("<no citation loaded>"))
        self.author.set_text(self.srctemp.author_gedcom())
        self.pubinfo.set_text(self.srctemp.pubinfo_gedcom())
        if self.template_tab and self.template_tab.autoset_title:
            title = self.srctemp.title_gedcom()
            self.obj.set_name(title)
            self.title.update()
        #lastly update the window title
        self.update_title(self.get_menu_title())

    def update_template_data(self, templatechanged=False):
        """
        Change in the template tab of source must be reflected in other places.
        If template itself changed, templatechanged==True must be passed
        """
        if templatechanged and self.tmplfields:
            #the citation template fields must be changed!
            self.tmplfields.reset_template_fields(self.obj.get_template())
        if self.attr_tab:
            self.attr_tab.rebuild_callback()
        self.update_attr()

    def callback_cite_changed(self):
        """
        Change in the citation part might lead to changes needed in the src GUI
        section
        """
        self.update_template_data(False)

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
        self.notebook_src = self.glade.get_object('notebook')
        notebook = self.notebook_src
        gridsrc =  self.glade.get_object('gridsrc')
        #recreate start page as GrampsTab
        notebook.remove_page(1)
        notebook.remove_page(0)
        self.overviewtab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('Overview'), gridsrc)
        self._add_tab(notebook, self.overviewtab)

        #recreate second page as GrampsTab
        self.template_page_nr = 1
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
                                self.track, self.obj, self.cite_apply_callback,
                                self.cite_add_callback)
        self._add_tab(notebook, self.citedin_tab)
        self.track_ref_for_deletion("citedin_tab")

##        self.backref_list = CitationBackRefList(self.dbstate,
##                                              self.uistate,
##                                              self.track,
##                              self.db.find_backlink_handles(self.obj.handle))
##        self.backref_tab = self._add_tab(notebook, self.backref_list)
##        self.track_ref_for_deletion("backref_tab")
##        self.track_ref_for_deletion("backref_list")
        
        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        self.glade.get_object('vbox').pack_start(notebook, True, True, 0)
        
        #now create citation tabbed pages
        self._create_citation_tabbed_pages()

    def _create_citation_tabbed_pages(self):
        if self.citation_ready:
            raise Exception
        self.citation_ready = True
        
        tblref =  self.glade.get_object('grid1')
        notebook_ref = self.notebook_ref
        #recreate start page as GrampsTab
        notebook_ref.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)
        self._add_tab(notebook_ref, self.reftab)
        self.track_ref_for_deletion("reftab")
        #reftab contains the citation template fields
        self.tmplfields = TemplateFields(self.dbstate.db, self.uistate,
                self.track, self.glade.get_object('grid_citefields'),
                self.obj, self.citation, None, self.callback_cite_changed)
        self.tmplfields.reset_template_fields(self.obj.get_template())

        self.comment_tab = NoteTab(self.dbstate, self.uistate, self.track,
                    self.citation.get_note_list(), self.get_menu_title(),
                    notetype=NoteType.CITATION)
        self._add_tab(notebook_ref, self.comment_tab)
        self.track_ref_for_deletion("comment_tab")

        self.gallery_tab = GalleryTab(self.dbstate, self.uistate, self.track,
                       self.citation.get_media_list())
        self._add_tab(notebook_ref, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")
            
        self.attr_tab = SrcAttrEmbedList(self.dbstate, self.uistate, self.track,
                          self.citation.get_attribute_list())
        self._add_tab(notebook_ref, self.attr_tab)
        self.track_ref_for_deletion("attr_tab")
            
        self.citationref_list = CitationBackRefList(self.dbstate, self.uistate, 
                              self.track,
                              self.db.find_backlink_handles(self.citation.handle),
                              self.enable_warnbox2)
        self._add_tab(notebook_ref, self.citationref_list)
        self.track_ref_for_deletion("citationref_list")

    def define_warn_box2(self, box):
        self.warn_box2 = box

    def enable_warnbox2(self):
        self.warn_box2.show()
        
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

    def close_citation(self, *obj):
        """
        Callback on close citation button clicked
        """
        if not self.citation_loaded:
            return
        
        self.ok_button.set_sensitive(False)
        self.btnclose_cite.set_sensitive(False)
        
        #ask if ok to save the citation if needed
        save_citation = False
        if not self.citation.get_handle():
            #new citation, ask if we should save.
            qd = QuestionDialog2(_("Closing New Citation"), 
                _("Should the new citation be saved to your family tree?"), 
                _("Save Citation"),
                _("Don't Save Citation"), parent=self.window)
            ok = qd.run()
            if ok:
                save_citation = True
        elif self.citation_data_has_changed():
            #if citation changed, ask if user does not want to save it first
            qd = QuestionDialog2(_('Save Changes?'),
                _('If you close without saving, the changes you '
                  'have made will be lost'), 
                _("Save Citation"),
                _("Don't Save Citation"), parent=self.window)
            ok = qd.run()
            if ok:
                save_citation = True
        
        if save_citation:
            #we save the citation. If new source, this means the source must
            #be saved too!
            res = self.__base_save_source_test()
            if not res:
                return
            res = self.__base_save_citation_test()
            if not res:
                return
            self.__base_save(only_cite=True)
            #as a citation changed, we need to update some fields in source
            #section
            self.citedin_tab.rebuild()
            
        #now close the citation part
        self.unload_citation()
        #make safe button active again
        self.ok_button.set_sensitive(True)

    def __base_save_source_test(self):
        if self.object_is_empty():
            ErrorDialog(_("Cannot save source"),
                        _("No data exists for this source. Please "
                          "enter data or cancel the edit."))
            self.ok_button.set_sensitive(True)
            if self.citation_loaded:
                self.btnclose_cite.set_sensitive(True)
            return False
        
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
            if self.citation_loaded:
                self.btnclose_cite.set_sensitive(True)
            return False
        return True


    def __base_save_citation_test(self):
        #tests on the citation if needed:
        if self.citation_loaded:
            (uses_dupe_id, gramps_id) = self._citation_uses_duplicate_id(
                                            self.citation)
            if uses_dupe_id:
                prim_object = self.db.get_citation_from_gramps_id(gramps_id)
                name = prim_object.get_page()
                msg1 = _("Cannot save citation. ID already exists.")
                msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(gramps_id)s. This value is already used by '" 
                         "%(prim_object)s'. Please enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                             'gramps_id' : gramps_id, 'prim_object' : name }
                ErrorDialog(msg1, msg2)
                self.ok_button.set_sensitive(True)
                if self.citation_loaded:
                    self.btnclose_cite.set_sensitive(True)
                return False
        return True

    def __base_save(self, only_cite=False):
        """
        Save to database. If only_cite, the idea is to only save the citation
        part. If the source does not exist, sourse will be saved anyway
        """
        with DbTxn('', self.db) as trans:
            # First commit the Source Primary object
            if not self.obj.get_handle():
                self.db.add_source(self.obj, trans)
                msg = _("Add Source (%s)") % self.obj.get_title()
            elif not only_cite:
                #a changed source is not saved if only_cite
                if not self.obj.get_gramps_id():
                    self.obj.set_gramps_id(self.db.find_next_source_gramps_id())
                self.db.commit_source(self.obj, trans)
                msg = _("Edit Source (%s)") % self.obj.get_title()
            else:
                msg = ''
            # Make sure citation references this source
            if self.citation:
                self.citation.set_reference_handle(self.obj.handle)
            # Now commit the Citation Primary object if needed
            if self.citation_loaded:
                if not self.citation.get_handle():
                    self.db.add_citation(self.citation, trans)
                    msg += "\n" + _("Add Citation (%s)") % self.citation.get_page()
                else:
                    if not self.citation.get_gramps_id():
                        self.citation.set_gramps_id(
                                        self.db.find_next_citation_gramps_id())
                    self.db.commit_citation(self.citation, trans)
                    msg += "\n" + _("Edit Citation (%s)") % self.citation.get_page()
            # set transaction description
            trans.set_description(msg)

    def save(self, *obj):
        self.ok_button.set_sensitive(False)
        self.btnclose_cite.set_sensitive(False)
        
        res = self.__base_save_source_test()
        if not res:
            return
        res = self.__base_save_citation_test()
        if not res:
            return
        
        self.__base_save()

        if self.callback and self.citation_loaded:
            #callback only returns the citation handle. Source can be determined
            # of this if needed.
            self.callback(self.citation.get_handle())

        self.close()

    def _citation_uses_duplicate_id(self, obj):
        """
        Check whether a changed or added GRAMPS ID already exists in the DB.
        
        Return True if a duplicate GRAMPS ID has been detected.
        
        """
        original = self.db.get_citation_from_handle(obj.get_handle())
        if original and original.get_gramps_id() == obj.get_gramps_id():
            #id did not change, so all is good
            return (False, 0)
        else:
            idval = obj.get_gramps_id()
            if self.db.get_citation_from_gramps_id(idval):
                return (True, idval)
            return (False, 0)

    # CITATION PART 
    def cite_apply_callback(self, citation_handle):
        if self.citation_loaded:
            self.close_citation()
        self.load_citation(citation_handle)

    def cite_add_callback(self):
        """
        User wants to add a new citation to the source.
        """
        if self.citation_loaded:
            self.close_citation()
        self.load_citation(None)

    def unload_citation(self):
        self.cinf.set_visible(False)
        self.btnclose_cite.set_sensitive(False)
        self.notebook_ref.set_visible(False)
        self.citation_loaded = False
        if self.citation:
            #there is a citation, we clear it
            self.citation.unserialize(Citation().serialize())

    def load_citation(self, chandle):
        """
        Loading a citation in the top view
        """
        #we switch current citatoin for the new one
        if not self.citation:
            #there is no citation yet, put an empty one
            self.citation = Citation()
        if chandle:
            newcite = self.db.get_citation_from_handle(chandle)
        else:
            newcite = Citation()
        if not newcite:
            #error in database, link to citation handle that does not exist
            raise Exception
        self.citation.unserialize(newcite.serialize())
        #we have a citation:
        self.citation_loaded = True
        if not self.citation_ready:
            self._setup_citation_fields()
            self._create_citation_tabbed_pages()
        else:
            self.citation_changed()
        #the citation template fields must be changed!
        self.tmplfields.reset_template_fields(self.obj.get_template())
        self.cinf.set_visible(True)
        self.btnclose_cite.set_sensitive(True)
        self.notebook_ref.set_visible(True)

    def citation_changed(self):
        """
        The citation part of the editor changed, we need to update all
        GUI fields showing data of it
        """
        #update source part that uses citation
        self.update_attr()
        #trigger update of the monitored fields
        for field in [self.gid2, self.type_mon, self.tags2, self.ref_privacy]:
            field.update()
        #trigger update of the tab fields
        self.comment_tab.rebuild_callback(self.citation.get_note_list())
        self.gallery_tab.rebuild_callback(self.citation.get_media_list())
        self.attr_tab.rebuild_callback(self.citation.get_attribute_list())
        self.citationref_list.rebuild_callback(
                        self.db.find_backlink_handles(self.citation.handle))

    def data_has_changed(self):
        return self.citation_data_has_changed() or \
                 EditPrimary.data_has_changed(self)

    def citation_data_has_changed(self):
        """
        This checks whether the citation data has changed
        
        A date comparison can fail incorrectly because we have made the
        decision to store entered text in the date. However, there is no
        entered date when importing from a XML file, so we can get an
        incorrect fail.
        """
        if not self.citation_loaded:
            return False
        if self.db.readonly:
            return False
        if self.citation.handle:
            orig = self.db.get_citation_from_handle(self.citation.handle)
            if orig:
                cmp_obj = orig
            else:
                cmp_obj = Citation()
            return cmp_obj.serialize(True)[1:] != self.citation.serialize(True)[1:]
        else:
            cmp_obj = Citation()
            return cmp_obj.serialize(True)[1:] != self.citation.serialize()[1:]


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
