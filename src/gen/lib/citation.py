#
# Gramps - a GTK+/GNOME based genealogy program
#
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

"""
Citation object for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.primaryobj import PrimaryObject
from gen.lib.mediabase import MediaBase
from gen.lib.notebase import NoteBase
from gen.lib.datebase import DateBase
from gen.lib.refbase import RefBase
from gen.lib.const import DIFFERENT, EQUAL, IDENTICAL

#-------------------------------------------------------------------------
#
# Citation class
#
#-------------------------------------------------------------------------
class Citation(MediaBase, NoteBase, PrimaryObject, RefBase, DateBase):
    """
    A record of a citation of a source of information.
    
    In GEDCOM this is called a SOURCE_CITATION.
    The data provided in the <<SOURCE_CITATION>> structure is source-related 
    information specific to the data being cited.
    """

    CONF_VERY_HIGH = 4
    CONF_HIGH      = 3
    CONF_NORMAL    = 2
    CONF_LOW       = 1
    CONF_VERY_LOW  = 0

    def __init__(self):
        """Create a new Citation instance."""
        PrimaryObject.__init__(self)
        MediaBase.__init__(self)                       #  7
        NoteBase.__init__(self)                        #  6
        DateBase.__init__(self)                        #  2
        RefBase.__init__(self)                         #  5
        self.page = ""                                 #  3
        self.confidence = Citation.CONF_NORMAL         #  4
        self.datamap = {}                              #  8
        
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.handle,                           #  0
                self.gramps_id,                        #  1
                DateBase.serialize(self),              #  2
                unicode(self.page),                    #  3
                self.confidence,                       #  4
                RefBase.serialize(self),               #  5
                NoteBase.serialize(self),              #  6
                MediaBase.serialize(self),             #  7
                self.datamap,                          #  8
                self.change,                           #  9
                self.private)                          # 10

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Citation structure.
        """
        (self.handle,                                  #  0
         self.gramps_id,                               #  1
         date,                                         #  2
         self.page,                                    #  3
         self.confidence,                              #  4
         ref,                                          #  5
         note_list,                                    #  6
         media_list,                                   #  7
         self.datamap,                                 #  8
         self.change,                                  #  9
         self.private                                  # 10
         ) = data

        DateBase.unserialize(self, date)
        NoteBase.unserialize(self, note_list)
        MediaBase.unserialize(self, media_list)
        RefBase.unserialize(self, ref)
        
    def _has_handle_reference(self, classname, handle):
        """
        Return True if the object has reference to a given handle of given 
        primary object type.
        
        :param classname: The name of the primary object class.
        :type classname: str
        :param handle: The handle to be checked.
        :type handle: str
        :returns: Returns whether the object has reference to this handle of 
                this object type.
        :rtype: bool
        """
        if classname == 'Note':
            return handle in [ref.ref for ref in self.note_list]
        elif classname == 'Media':
            return handle in [ref.ref for ref in self.media_list]
        elif classname == 'Source':
            return handle == self.get_reference_handle()
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str
        """
        # FIXME: Citations can refer to Notes, MediaObjects and one Source.
        # MediaObjects and dealt with in Primary object,
        # Notes do not seem to be dealt with at all !!
        if classname == 'Source' and \
           self.get_reference_handle() in handle_list:
            self.set_reference_handle(None)

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old handle with those to the new handle.

        :param classname: The name of the primary object class.
        :type classname: str
        :param old_handle: The handle to be replaced.
        :type old_handle: str
        :param new_handle: The handle to replace the old one with.
        :type new_handle: str
        """
        # FIXME: Citations can refer to Notes, MediaObjects and one Source.
        # MediaObjects and dealt with in Primary object,
        # Notes do not seem to be dealt with at all !!
        if classname == 'Source' and \
           RefBase.get_reference_handle(self) == old_handle:
            self.ref = RefBase.set_reference_handle(self, new_handle)

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        # FIXME: Presumably this does not include references to primary objects
        # (Notes, Media, Source) that contain text
        return [self.page,
                self.gramps_id] + self.datamap.keys() + self.datamap.values()
    
    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.media_list

#    def get_sourcref_child_list(self):
#    # FIXME: I think we no longer need to handle source references
#        """
#        Return the list of child secondary objects that may refer sources.
#
#        :returns: Returns the list of child secondary child objects that may 
#                refer sources.
#        :rtype: list
#        """
#        return self.media_list + self.ref

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
        :rtype: list
        """
        return self.media_list

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        
        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.media_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = self.get_referenced_note_handles()
        if self.ref:
            ret += [('Source', self.ref)]
        return ret

#    def has_source_reference(self, src_handle) :
#        """
#        Return True if any of the child objects has reference to this source 
#        handle.
#
#        :param src_handle: The source handle to be checked.
#        :type src_handle: str
#        :returns: Returns whether any of it's child objects has reference to 
#                this source handle.
#        :rtype: bool
#        """
#        for item in self.get_sourcref_child_list():
#            if item.has_source_reference(src_handle):
#                return True
#
#        return False
#
#    def remove_source_references(self, src_handle_list):
#        """
#        Remove references to all source handles in the list in all child 
#        objects.
#
#        :param src_handle_list: The list of source handles to be removed.
#        :type src_handle_list: list
#        """
#        for item in self.get_sourcref_child_list():
#            item.remove_source_references(src_handle_list)
#
#    def replace_source_references(self, old_handle, new_handle):
#        """
#        Replace references to source_handles in the list in this object and
#        all child objects and merge equivalent entries.
#
#        :param old_handle: The source handle to be replaced.
#        :type old_handle: str
#        :param new_handle: The source handle to replace the old one with.
#        :type new_handle: str
#        """
#        for item in self.get_sourcref_child_list():
#            item.replace_source_references(old_handle, new_handle)

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this source.

        :param acquisition: The source to merge with the present source.
        :rtype acquisition: Source
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)
        self._merge_media_list(acquisition)
        # merge confidence
        level_priority = [0, 4, 1, 3, 2]
        idx = min(level_priority.index(self.confidence),
                  level_priority.index(acquisition.confidence))
        self.confidence = level_priority[idx]
        my_datamap = self.get_data_map()
        acquisition_map = acquisition.get_data_map()
        for key in acquisition.get_data_map():
            if key not in my_datamap:
                self.datamap[key] = acquisition_map[key]
        # N.B. a Citation can refer to only one 'Source', so the 
        # 'Source' from acquisition cannot be merged in

    def get_data_map(self):
        """Return the data map of attributes for the source."""
        return self.datamap

    def set_data_map(self, datamap):
        """Set the data map of attributes for the source."""
        self.datamap = datamap

    def set_data_item(self, key, value):
        """Set the particular data item in the attribute data map."""
        self.datamap[key] = value

    def set_confidence_level(self, val):
        """Set the confidence level."""
        self.confidence = val

    def get_confidence_level(self):
        """Return the confidence level."""
        return self.confidence
        
    def set_page(self, page):
        """Set the page indicator of the SourceRef."""
        self.page = page

    def get_page(self):
        """Get the page indicator of the SourceRef."""
        return self.page
