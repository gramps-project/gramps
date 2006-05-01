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

"""
Source object for GRAMPS
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _PrimaryObject import PrimaryObject
from _MediaBase import MediaBase
from _NoteBase import NoteBase
from _Note import Note
from _RepoRef import RepoRef

#-------------------------------------------------------------------------
#
# Source class
#
#-------------------------------------------------------------------------
class Source(PrimaryObject,MediaBase,NoteBase):
    """A record of a source of information"""
    
    def __init__(self):
        """creates a new Source instance"""
        PrimaryObject.__init__(self)
        MediaBase.__init__(self)
        NoteBase.__init__(self)
        self.title = ""
        self.author = ""
        self.pubinfo = ""
        self.note = Note()
        self.datamap = {}
        self.abbrev = ""
        self.reporef_list = []

    def serialize(self):
        return (self.handle, self.gramps_id, unicode(self.title),
                unicode(self.author), unicode(self.pubinfo),
                NoteBase.serialize(self),
                MediaBase.serialize(self), unicode(self.abbrev),
                self.change,self.datamap,
                [rr.serialize() for rr in self.reporef_list],
                self.marker.serialize(),self.private)

    def unserialize(self,data):
        """
        Converts the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle, self.gramps_id, self.title, self.author,
         self.pubinfo, note, media_list,
         self.abbrev, self.change, self.datamap, reporef_list,
         marker, self.private) = data

        self.marker.unserialize(marker)
        NoteBase.unserialize(self,note)
        MediaBase.unserialize(self,media_list)
        self.reporef_list = [RepoRef().unserialize(rr) for rr in reporef_list]
        
    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.title,self.author,self.pubinfo,self.abbrev,
                self.gramps_id] + self.datamap.keys() + self.datamap.values()
    
    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.media_list + self.reporef_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_sourcref_child_list(self):
        """
        Returns the list of child secondary objects that may refer sources.

        @return: Returns the list of child secondary child objects that may refer sources.
        @rtype: list
        """
        return self.media_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.media_list + self.reporef_list

    def has_source_reference(self,src_handle) :
        """
        Returns True if any of the child objects has reference
        to this source handle.

        @param src_handle: The source handle to be checked.
        @type src_handle: str
        @return: Returns whether any of it's child objects has reference to this source handle.
        @rtype: bool
        """
        for item in self.get_sourcref_child_list():
            if item.has_source_reference(src_handle):
                return True

        return False

    def remove_source_references(self,src_handle_list):
        """
        Removes references to all source handles in the list
        in all child objects.

        @param src_handle_list: The list of source handles to be removed.
        @type src_handle_list: list
        """
        for item in self.get_sourcref_child_list():
            item.remove_source_references(src_handle_list)

    def replace_source_references(self,old_handle,new_handle):
        """
        Replaces references to source handles in the list
        in this object and all child objects.

        @param old_handle: The source handle to be replaced.
        @type old_handle: str
        @param new_handle: The source handle to replace the old one with.
        @type new_handle: str
        """
        for item in self.get_sourcref_child_list():
            item.replace_source_references(old_handle,new_handle)

    def get_data_map(self):
        """Returns the data map of attributes for the source"""
        return self.datamap

    def set_data_map(self,datamap):
        """Sets the data map of attributes for the source"""
        self.datamap = datamap

    def set_data_item(self,key,value):
        """Sets the particular data item in the attribute data map"""
        self.datamap[key] = value

    def set_title(self,title):
        """
        Sets the descriptive title of the Source object

        @param title: descriptive title to assign to the Source
        @type title: str
        """
        self.title = title

    def get_title(self):
        """
        Returns the descriptive title of the Place object

        @returns: Returns the descriptive title of the Place
        @rtype: str
        """
        return self.title

    def set_author(self,author):
        """sets the author of the Source"""
        self.author = author

    def get_author(self):
        """returns the author of the Source"""
        return self.author

    def set_publication_info(self,text):
        """sets the publication information of the Source"""
        self.pubinfo = text

    def get_publication_info(self):
        """returns the publication information of the Source"""
        return self.pubinfo

    def set_abbreviation(self,abbrev):
        """sets the title abbreviation of the Source"""
        self.abbrev = abbrev

    def get_abbreviation(self):
        """returns the title abbreviation of the Source"""
        return self.abbrev

    def add_repo_reference(self,repo_ref):
        """
        Adds a L{RepoRef} instance to the Source's reporef list.

        @param repo_ref: L{RepoRef} instance to be added to the object's reporef list.
        @type repo_ref: L{RepoRef}
        """
        self.reporef_list.append(repo_ref)

    def get_reporef_list(self):
        """
        Returns the list of L{RepoRef} instances associated with the Source.

        @returns: list of L{RepoRef} instances associated with the Source
        @rtype: list
        """
        return self.reporef_list

    def set_reporef_list(self,reporef_list):
        """
        Sets the list of L{RepoRef} instances associated with the Source.
        It replaces the previous list.

        @param reporef_list: list of L{RepoRef} instances to be assigned to the Source.
        @type reporef_list: list
        """
        self.reporef_list = reporef_list

    def has_repo_reference(self,repo_handle):
        """
        Returns True if the Source has reference to this Repository handle.

        @param repo_handle: The Repository handle to be checked.
        @type repo_handle: str
        @return: Returns whether the Source has reference to this Repository handle.
        @rtype: bool
        """
        return repo_handle in [repo_ref.ref for repo_ref in self.reporef_list]

    def remove_repo_references(self,repo_handle_list):
        """
        Removes references to all Repository handles in the list.

        @param repo_handle_list: The list of Repository handles to be removed.
        @type repo_handle_list: list
        """
        new_reporef_list = [ repo_ref for repo_ref in self.reporef_list \
                                    if repo_ref.ref not in repo_handle_list ]
        self.reporef_list = new_reporef_list

    def replace_repo_references(self,old_handle,new_handle):
        """
        Replaces all references to old Repository handle with the new handle.

        @param old_handle: The Repository handle to be replaced.
        @type old_handle: str
        @param new_handle: The Repository handle to replace the old one with.
        @type new_handle: str
        """
        refs_list = [ repo_ref.ref for repo_ref in self.reporef_list ]
        n_replace = refs_list.count(old_handle)
        for ix_replace in xrange(n_replace):
            ix = refs_list.index(old_handle)
            self.reporef_list[ix].ref = new_handle
            refs_list.pop(ix)

