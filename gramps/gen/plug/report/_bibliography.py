#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
# Copyright (C) 2010  Jakim Friant
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Contain and organize bibliographic information.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import string
import math

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...lib.citation import Citation as lib_Citation


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

        :return: Source Handle
        :rtype: handle
        """
        return self.__src_handle

    def set_source_handle(self, handle):
        """
        Set the handle for the source that this citation is for.

        :param handle: Source Handle
        :type handle: handle
        """
        self.__src_handle = handle

    def get_ref_list(self):
        """
        List all the references to this citation.

        :return: a list of references
        :rtype: list of :class:`~.citation.Citation` objects
        """
        return self.__ref_list

    def add_reference(self, source_ref):
        """
        Add a reference to this citation. If a similar reference exists, don't
        add another one.

        :param source_ref: Source Reference
        :type source_ref: :class:`~.citation.Citation`
        :return: The key of the added reference among all the references.
        :rtype: char
        """
        letters = string.ascii_lowercase  # or (e.g.) "abcdef" for testing
        letter_count = len(letters)
        ref_count = len(self.__ref_list)
        x_ref_count = ref_count
        # Return "a" for ref_count = 0, otherwise log(0) does not work
        if ref_count == 0:
            self.__ref_list.append((letters[0], source_ref))
            return letters[0]
        last_letter = letters[ref_count % letter_count]
        key = ""
        # Calculate prek number of digits.
        number_of_letters = 1 + int(math.log(float(ref_count), float(letter_count)))
        # Exclude index for number_of_letters-1
        for n in range(1, number_of_letters - 1):
            ref_count -= pow(letter_count, n)
        # Adjust number_of_letters for new index
        number_of_letters = 1 + int(math.log(float(ref_count), float(letter_count)))
        for n in range(1, number_of_letters):
            x_ref_count -= pow(letter_count, n)
        for letter in range(1, number_of_letters):
            index = x_ref_count // pow(letter_count, letter) % letter_count
            key += letters[index]
        key = key + last_letter
        self.__ref_list.append((key, source_ref))
        return key


class Bibliography:
    """
    Store and organize multiple citations into a bibliography.
    """

    MODE_DATE = 2**0
    MODE_PAGE = 2**1
    MODE_CONF = 2**2
    MODE_NOTE = 2**3
    MODE_MEDIA = 2**4
    MODE_ALL = MODE_DATE | MODE_PAGE | MODE_CONF | MODE_NOTE | MODE_MEDIA

    def __init__(self, mode=MODE_ALL):
        """
        A bibliography will store citations (sources) and references to those
        citations (citations). Duplicate entries will not be added. To change
        what is considered duplicate, you can tell the bibliography what source
        ref information you are interested in by passing in the mode.

        Possible modes include:

        - MODE_DATE
        - MODE_PAGE
        - MODE_CONF
        - MODE_NOTE
        - MODE_MEDIA
        - MODE_ALL

        If you only care about pages, set "mode=MODE_PAGE".
        If you only care about dates and pages, set "mode=MODE_DATE|MODE_PAGE".
        If you care about everything, set "mode=MODE_ALL".
        """
        self.__citation_list = []
        self.mode = mode

    def add_reference(self, lib_citation):
        """
        Add a reference to a source to this bibliography. If the source already
        exists, don't add it again. If a similar reference exists, don't
        add another one.

        :param citation: Citation object
        :type citation: :class:`~.citation.Citation`
        :return: A tuple containing the index of the source among all the
                 sources and the key of the reference among all the references.
                 If there is no reference information, the second element will
                 be None.
        :rtype: (int,char) or (int,None)

        .. note::
            Within this file, the name 'citation' is used both for
            gen.lib.Citation, and for _bibliography.Citation. It is not clear
            how best to rename the concepts in this file to avoid the clash,
            so the names have been retained. In this function, lib_citation
            is used for gen.lib.Citation instances, and citation for
            _bibliography.Citation instances. Elsewhere in this file,
            source_ref is used for gen.lib.Citation instances.
        """
        source_handle = lib_citation.get_reference_handle()
        cindex = 0
        rkey = ""
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

        if self.__sref_has_info(lib_citation):
            for key, ref in citation.get_ref_list():
                if self.__srefs_are_equal(ref, lib_citation):
                    # if a reference like this already exists, don't add
                    # another one
                    return (cindex, key)
            rkey = citation.add_reference(lib_citation)

        return (cindex, rkey)

    def get_citation_count(self):
        """
        Report the number of citations in this bibliography.

        :return: number of citations
        :rtype: int
        """
        return len(self.__citation_list)

    def get_citation_list(self):
        """
        Return a list containing all the citations in this bibliography.

        :return: citation list
        :rtype: list of :class:`Citation` objects
        """
        return self.__citation_list

    def __sref_has_info(self, source_ref):
        """
        Determine if this source_ref has any useful information based on the
        current mode.
        """
        if (self.mode & self.MODE_PAGE) == self.MODE_PAGE:
            if source_ref.get_page() != "":
                return True
        if (self.mode & self.MODE_DATE) == self.MODE_DATE:
            date = source_ref.get_date_object()
            if date is not None and not date.is_empty():
                return True
        if (self.mode & self.MODE_CONF) == self.MODE_CONF:
            confidence = source_ref.get_confidence_level()
            if confidence is not None and confidence != lib_Citation.CONF_NORMAL:
                return True
        if (self.mode & self.MODE_NOTE) == self.MODE_NOTE:
            if len(source_ref.get_note_list()) != 0:
                return True
        if (self.mode & self.MODE_MEDIA) == self.MODE_MEDIA:
            if len(source_ref.get_media_list()) != 0:
                return True
        # Can't find anything interesting.
        return False

    def __srefs_are_equal(self, source_ref1, source_ref2):
        """
        Determine if two source references are equal based on the
        current mode.
        """
        # The criterion for equality (in mode==MODE_ALL) is changed for
        # citations. Previously, it was based on is_equal from SecondaryObject,
        # which does a 'cmp' on the serialised data. (Note that this might not
        # have worked properly for Dates; see comments in Date.is_equal and
        # EditCitation.data_has_changed). The comparison is now made as to
        # whether the two gen.lib.Citations have the same handle (i.e. they are
        # actually the same database objects). It is felt that this better
        # reflects the intent of Citation objects, which can be merged if they
        # are intended to represent the same citation.
        if self.mode == self.MODE_ALL:
            return source_ref1.handle == source_ref2.handle
        if (self.mode & self.MODE_PAGE) == self.MODE_PAGE:
            if source_ref1.get_page() != source_ref2.get_page():
                return False
        if (self.mode & self.MODE_DATE) == self.MODE_DATE:
            date1 = source_ref1.get_date_object()
            date2 = source_ref2.get_date_object()
            if not date1.is_equal(date2):
                return False
        if (self.mode & self.MODE_CONF) == self.MODE_CONF:
            conf1 = source_ref1.get_confidence_level()
            conf2 = source_ref2.get_confidence_level()
            if conf1 != conf2:
                return False
        if (self.mode & self.MODE_NOTE) == self.MODE_NOTE:
            nl1 = source_ref1.get_note_list()
            nl2 = source_ref2.get_note_list()
            if len(nl1) != len(nl2):
                return False
            for notehandle in nl1:
                if notehandle not in nl2:
                    return False
        if (self.mode & self.MODE_MEDIA) == self.MODE_MEDIA:
            nl1 = source_ref1.get_media_list()
            nl2 = source_ref2.get_media_list()
            if len(nl1) != len(nl2):
                return False
            for mediahandle in nl1:
                if mediahandle not in nl2:
                    return False
        # Can't find anything different. They must be equal.
        return True
