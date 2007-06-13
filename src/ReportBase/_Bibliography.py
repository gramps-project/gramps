#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
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
# $Id: $

"""
Contain and organize bibliographic information.
"""

class Citation:
    """
    Store information about a citation and all of its references.
    """
    def __init__(self):
        """
        Initialize members.
        """
        self.__src_handle = None
        self.__ref_list = []
          
    def get_source_handle(self):
        """
        Provide the handle to the source that this citation is for.
        
        @return: Source Handle
        @rtype: handle
        """
        return self.__src_handle
    
    def set_source_handle(self,handle):
        """
        Set the handle for the source that this citation is for.

        @param handle: Source Handle
        @type handle: handle
        """
        self.__src_handle = handle
        
    def get_ref_list(self):
        """
        List all the references to this citation.

        @return: a list of references
        @rtype: list of L{Relib.SourceRef} objects
        """
        return self.__ref_list

    def add_reference(self, source_ref):
        """
        Add a reference to this citation. If a similar reference exists, don't
        add another one.

        @param source_ref: Source Reference
        @type source_ref: L{Relib.SourceRef}
        @return: The index of the added reference among all the references.
        @rtype: int
        """
        index = 0
        for ref in self.__ref_list:
            if _srefs_are_equal(ref,source_ref):
                # if a reference like this already exists, don't add another one
                return index
            index += 1
        
        self.__ref_list.append(source_ref)
        return index

class Bibliography:
    """
    Store and organize multiple citations into a bibliography.
    """
    def __init__(self):
        """
        Initialize members.
        """
        self.__citation_list = []

    def add_reference(self, source_ref):
        """
        Add a reference to a source to this bibliography. If the source already
        exists, don't add it again. If a similar reference exists, don't
        add another one.

        @param source_ref: Source Reference
        @type source_ref: L{Relib.SourceRef}
        @return: A tuple containing the index of the source among all the 
        sources and the index of the reference among all the references. If 
        there is no reference information, the second element will be None.
        @rtype: (int,int) or (int,None)
        """
        source_handle = source_ref.get_reference_handle()
        cindex = 0
        rindex = None
        citation = None
        citation_found = False
        for citation in self.__citation_list:
            if citation.get_source_handle() == source_handle:
                citation_found = True
                break
            cindex += 1
            
        if not citation_found:
            citation = Citation()
            citation.set_source_handle(source_handle)
            cindex = len(self.__citation_list)
            self.__citation_list.append(citation)

        if _sref_has_info(source_ref):
            rindex = citation.add_reference(source_ref)
        
        return (cindex,rindex)
    
    def get_citation_count(self):
        """
        Report the number of citations in this bibliography.

        @return: number of citations
        @rtype: int
        """
        return len(self.__citation_list)
    
    def get_citation_list(self):
        """
        Return a list containing all the citations in this bibliography.

        @return: citation list
        @rtype: list of L{Citation} objects
        """
        return self.__citation_list

def _sref_has_info(source_ref):
    if source_ref.get_page() == "":
        return False
    else:
        return True
    
def _srefs_are_equal(source_ref1,source_ref2):
    if source_ref1.get_page() == source_ref2.get_page():
        return True
    else:
        return False