# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020       Paul Culley
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

"""
Library common to SourceView and CitationTreeView
"""
from gramps.gen.errors import HandleError


# -------------------------------------------------------------------------
#
# SourceLibView
#
# -------------------------------------------------------------------------
class LibSourceView:
    """
    This contains the common delete related methods for the views.
    It was written specifically for CitationTreeView, but works for SourceView
    as well; there just will never be an citation handles in selection.

    This must be placed before Listview in the MRO to properly override the
    included methods.  For example:
        class SourceView(LibSourceView, ListView)
    """

    def remove(self, *obj):
        """
        Method called when deleting source(s) or citations from the views.
        """
        ht_list = []
        handles = self.selected_handles()
        for hndl in handles:
            if self.dbstate.db.has_source_handle(hndl):
                ht_list.append(("Source", hndl))
            else:
                ht_list.append(("Citation", hndl))
        self.remove_selected_objects(ht_list)

    def remove_object_from_handle(
        self, obj_type, handle, trans, in_use_prompt=False, parent=None
    ):
        """
        deletes a single object from database
        """
        try:  # need this in case user selects both source and its Citations
            obj = self.dbstate.db.method("get_%s_from_handle", obj_type)(handle)
        except HandleError:
            return
        bl_list = list(self.dbstate.db.find_backlink_handles(handle))
        if in_use_prompt:
            res = self._in_use_prompt(obj, bl_list, parent=parent)
            if res != 1:  # Cancel or No
                return res
        # perfom the cleanup
        if obj_type == "Source":
            # we need to delete all back linked citations, so sort these out
            cit_list = []
            nbl_list = []
            for item in bl_list:
                if item[0] == "Citation":
                    cit_list.append(item[1])
                else:  # save any other back links for later.
                    nbl_list.append(item)
            # now lets go through citations and clean up their back-refs
            hndl_cnt = len(cit_list) / 100
            for indx, cit_hndl in enumerate(cit_list):
                # the following introduces another pass with the progressbar
                # to keep the user from wondering what is happening if there
                # are a lot of citations on the source
                self.uistate.pulse_progressbar(indx / hndl_cnt)
                cit_bl_list = list(self.dbstate.db.find_backlink_handles(cit_hndl))
                for ref_type, ref_hndl in cit_bl_list:
                    ref_obj = self.dbstate.db.method("get_%s_from_handle", ref_type)(
                        ref_hndl
                    )
                    ref_obj.remove_handle_references(obj_type, [cit_hndl])
                    self.dbstate.db.method("commit_%s", ref_type)(ref_obj, trans)
                # and delete the citation
                self.dbstate.db.remove_citation(cit_hndl, trans)
            bl_list = nbl_list  # to clean up any other back refs to source
        for ref_type, ref_hndl in bl_list:
            ref_obj = self.dbstate.db.method("get_%s_from_handle", ref_type)(ref_hndl)
            ref_obj.remove_handle_references(obj_type, [handle])
            self.dbstate.db.method("commit_%s", ref_type)(ref_obj, trans)
        # and delete the source
        self.dbstate.db.remove_source(handle, trans)
