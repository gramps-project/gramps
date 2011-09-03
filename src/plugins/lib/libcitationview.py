# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
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
Citation View
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
from gui.views.listview import ListView
import Utils
import Bookmarks
import Errors
from DdTargets import DdTargets
from QuestionDialog import ErrorDialog
from gui.editors import EditCitation, DeleteCitationQuery, EditSource, \
    DeleteSrcQuery
from Filters.SideBar import SourceSidebarFilter

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# CitationView
#
#-------------------------------------------------------------------------
class BaseCitationView(ListView):
    """ citation listview class 
    """
    # The configuration parameters have been moved to CitationTreeView and
    # CitationListView, because they differ for the two different views.

    def __init__(self, pdata, dbstate, uistate, title, model, nav_group=0):

        signal_map = {
            'citation-add'     : self.row_add,
            'citation-update'  : self.row_update,
            'citation-delete'  : self.row_delete,
            'citation-rebuild' : self.object_build,
            'source-add'       : self.row_add,
            'source-update'    : self.row_update,
            'source-delete'    : self.row_delete,
            'source-rebuild'   : self.object_build,
            }

        ListView.__init__(
            self, title, pdata, dbstate, uistate, 
            self.COLUMN_NAMES, len(self.COLUMN_NAMES), 
            model, signal_map,
            dbstate.db.get_citation_bookmarks(),
            Bookmarks.CitationBookmarks, nav_group,
            multiple=True,
            filter_class=SourceSidebarFilter)

        self.func_list.update({
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            })

        self.additional_uis.append(self.additional_ui())

    def navigation_type(self):
        return 'Citation'

    def get_bookmarks(self):
        return self.dbstate.db.get_citation_bookmarks()

    def drag_info(self):
        return DdTargets.SOURCE_LINK
    
    def define_actions(self):
        """
        This defines the possible actions for the citation views.
        Possible actions are:
        add_source: Add a new source (this is also available from the
                      source view)
        add:        Add a new citation and a new source (this can also be done 
                      by source view add a source, then citation view add a new 
                      citation to an existing source)
        share:      Add a new citation to an existing source (when a source is
                      selected)
        edit:       Edit a source or a citation.
        merge:      Merge the selected sources or citations.
        remove:     Delete the selected sources or citations.
        
        
        """
        ListView.define_actions(self)

# gtk stock icons are at http://www.pygtk.org/docs/pygtk/gtk-stock-items.html
        self._add_action('Add source', 'gramps-source', _("Add source..."), 
                         accel=None, 
                         tip=self.ADD_SOURCE_MSG, 
                         callback=self.add_source)
        self._add_action('Add citation', 'gramps-source', _("Add citation..."), 
                         accel=None, 
                         tip=self.ADD_CITATION_MSG, 
                         callback=self.share)
        
        self.all_action = gtk.ActionGroup(self.title + "/CitationAll")
        self.edit_action = gtk.ActionGroup(self.title + "/CitationEdit")

        self._add_action('FilterEdit', None, _('Citation Filter Editor'),
                         callback=self.filter_editor,)
        self._add_action('QuickReport', None, _("Quick View"), None, None, None)
        self._add_action('Dummy', None, '  ', None, None, self.dummy_report)

        self._add_action_group(self.edit_action)
        self._add_action_group(self.all_action)

    def get_stock(self):
        return 'gramps-citation'

    def additional_ui(self):
        """
        Defines the UI string for UIManager
        
        This is overridden in citationtreeview because that has additional 
        popup items for open and close all nodes
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Add source"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
                <menuitem action="Merge"/>
              </placeholder>
              <menuitem action="FilterEdit"/>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Add source"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
              <toolitem action="Merge"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <menuitem action="Merge"/>
            <separator/>
            <menu name="QuickReport" action="QuickReport">
              <menuitem action="Dummy"/>
            </menu>
          </popup>
        </ui>'''

    def dummy_report(self, obj):
        """ For the xml UI definition of popup to work, the submenu 
            Quick Report must have an entry in the xml
            As this submenu will be dynamically built, we offer a dummy action
        """
        pass

    def add_source(self, obj):
        """
        add_source: Add a new source (this is also available from the
                      source view)
        
        Create a new Source instance and call the EditSource editor with the
        new source. 
        
        Called when the Add_source button is clicked. 
        If the window already exists (Errors.WindowActiveError), we ignore it. 
        This prevents the dialog from coming up twice on the same object.
        
        However, since the window is identified by the Source object, and
        we have just created a new one, it seems to be impossible for the 
        window to already exist, so this is just an extra safety measure.
        """
        try:
            EditSource(self.dbstate, self.uistate, [], gen.lib.Source())
        except Errors.WindowActiveError:
            pass

    def add(self, obj):
        """
        add:        Add a new citation and a new source (this can also be done 
                      by source view add a source, then citation view add a new 
                      citation to an existing source)
        
        Create a new Source instance and Citation instance and call the 
        EditSource editor with the new source. 
        
        Called when the Add button is clicked. 
        If the window already exists (Errors.WindowActiveError), we ignore it. 
        This prevents the dialog from coming up twice on the same object.
        
        However, since the window is identified by the Source object, and
        we have just created a new one, it seems to be impossible for the 
        window to already exist, so this is just an extra safety measure.
        """
        try:
            EditCitation(self.dbstate, self.uistate, [], gen.lib.Citation(),
                         gen.lib.Source())
        except Errors.WindowActiveError:
            pass

    def share(self, obj):
        """
        share:      Add a new citation to an existing source (when a source is
                      selected)
        """
        for handle in self.selected_handles():
            # The handle will either be a Source handle or a Citation handle
            source = self.dbstate.db.get_source_from_handle(handle)
            citation = self.dbstate.db.get_citation_from_handle(handle)
            if (not source and not citation) or (source and citation):
                raise ValueError("selection must be either source or citation")
            if source:
                try:
                    EditCitation(self.dbstate, self.uistate, [], 
                                 gen.lib.Citation(), source)
                except Errors.WindowActiveError:
                    from QuestionDialog import WarningDialog
                    WarningDialog(_("Cannot share this reference"),
                                  self.__blocked_text())
            else:
                msg = _("Cannot add citation.")
                msg2 = _("In order to add a citation to an existing source, "
                         " you must select a source.")
                ErrorDialog(msg, msg2)
#    
    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        # The handle will either be a Source handle or a Citation handle
        source = self.dbstate.db.get_source_from_handle(handle)
        citation = self.dbstate.db.get_citation_from_handle(handle)
        if (not source and not citation) or (source and citation):
            raise ValueError("selection must be either source or citation")
        if citation:
            the_lists = Utils.get_citation_referents(handle, self.dbstate.db)
            object = self.dbstate.db.get_citation_from_handle(handle)
            query = DeleteCitationQuery(self.dbstate, self.uistate, object, 
                                        the_lists)
            is_used = any(the_lists)
            return (query, is_used, object)
        else:
            # FIXME: this is copied from SourceView, because import with
            # from plugins.view.sourceview import SourceView doesn't 
            # seem to work!
            the_lists = Utils.get_source_referents(handle, self.dbstate.db)
            LOG.debug('source referents %s' % [the_lists])
            citation_referents_list = []
            for citation in the_lists[7]:
                LOG.debug('citation %s' % citation)
                refs = Utils.get_citation_referents(citation, self.dbstate.db)
                citation_referents_list += [(citation, refs)]
            LOG.debug('citation_referents_list %s' % [citation_referents_list])
                
            (person_list, family_list, event_list, place_list, source_list, 
             media_list, repo_list, citation_list) = the_lists
            the_lists = (person_list, family_list, event_list, place_list, 
                         source_list, media_list, repo_list, citation_list, 
                         citation_referents_list)
            
            LOG.debug('the_lists %s' % [the_lists])    
    
            object = self.dbstate.db.get_source_from_handle(handle)
            query = DeleteSrcQuery(self.dbstate, self.uistate, object, 
                                   the_lists)
            is_used = any(the_lists)
            return (query, is_used, object)

    def edit(self, obj):
        """
        Edit either a Source or a Citation, depending on user selection
        """
        for handle in self.selected_handles():
            # The handle will either be a Source handle or a Citation handle
            source = self.dbstate.db.get_source_from_handle(handle)
            citation = self.dbstate.db.get_citation_from_handle(handle)
            if (not source and not citation) or (source and citation):
                raise ValueError("selection must be either source or citation")
            if citation:
                LOG.debug("citation handle %s page %s" % 
                          (handle, citation.page))
                try:
                    EditCitation(self.dbstate, self.uistate, [], citation)
                except Errors.WindowActiveError:
                    pass
            else:
                LOG.debug("source handle %s title %s " % 
                          (source, source.title))
                EditSource(self.dbstate, self.uistate, [], source)

    def __blocked_text(self):
        """
        Return the common text used when citation cannot be edited
        """
        return _("This citation cannot be edited at this time. "
                    "Either the associated citation is already being "
                    "edited or another object that is associated with "
                    "the same citation is being edited.\n\nTo edit this "
                    "citation, you need to close the object.")

    def merge(self, obj):
        """
        Merge the selected citations.
        """
        mlist = self.selected_handles()
        
        if len(mlist) != 2:
            msg = _("Cannot merge citations.")
            msg2 = _("Exactly two citations must be selected to perform a "
                     "merge. A second citation can be selected by holding "
                     "down the control key while clicking on the desired "
                     "citation.")
            ErrorDialog(msg, msg2)
        else:
            source1 = self.dbstate.db.get_source_from_handle(mlist[0])
            citation1 = self.dbstate.db.get_citation_from_handle(mlist[0])
            if (not source1 and not citation1) or (source1 and citation1):
                raise ValueError("selection must be either source or citation")
            
            source2 = self.dbstate.db.get_source_from_handle(mlist[1])
            citation2 = self.dbstate.db.get_citation_from_handle(mlist[1])
            if (not source2 and not citation2) or (source2 and citation2):
                raise ValueError("selection must be either source or citation")
            
            if citation1 and citation2:
                if not citation1.get_reference_handle()  == \
                                citation2.get_reference_handle():         
                    msg = _("Cannot merge citations.")
                    msg2 = _("The two selected citations must have the same "
                             "source to perform a merge. If you want to merge "
                             "these two citations, then you must merge the "
                             "sources first.")
                    ErrorDialog(msg, msg2)
                else:
                    import Merge
                    Merge.MergeCitations(self.dbstate, self.uistate, 
                                         mlist[0], mlist[1])
            elif source1 and source2:
                import Merge
                Merge.MergeSources(self.dbstate, self.uistate, 
                                     mlist[0], mlist[1])
            else:
                msg = _("Cannot perform merge.")
                msg2 = _("Both objects must be of the same type, either "
                         "both must be sources, or both must be "
                         "citations.")
                ErrorDialog(msg, msg2)

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_citation_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Source Filter",),
                ("Citation Gallery",
                 "Citation Notes",
                 "Citation Backlinks"))
