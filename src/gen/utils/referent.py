#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"""
Functions to return referents of primary objects.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".gui.utils.referents")

#-------------------------------------------------------------------------
#
# Referents functions
#
#-------------------------------------------------------------------------

def get_referents(handle, db, primary_objects):
    """ Find objects that refer to an object.
    
    This function is the base for other get_<object>_referents functions.
    
    """
    # Use one pass through the reference map to grab all the references
    object_list = list(db.find_backlink_handles(handle))
    
    # Then form the object-specific lists
    the_lists = ()

    for primary in primary_objects:
        primary_list = [item[1] for item in object_list if item[0] == primary]
        the_lists = the_lists + (primary_list, )

    return the_lists

def get_source_referents(source_handle, db):
    """ Find objects that refer the source.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given source handle in a given database.
    
    Only Citations can refer to sources, so that is all we need to check
    """
    _primaries = ('Citation',)
    
    return (get_referents(source_handle, db, _primaries))

def get_citation_referents(citation_handle, db):
    """ Find objects that refer the citation.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given citation handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 
                  'Source', 'MediaObject', 'Repository')
    
    return (get_referents(citation_handle, db, _primaries))

def get_source_and_citation_referents(source_handle, db):
    """ 
    Find all citations that refer to the sources, and recursively, all objects
    that refer to the sources.

    This function finds all primary objects that refer (directly or through
    secondary child-objects) to a given source handle in a given database.
    
    Objects -> Citations -> Source
    e.g.
    Media object M1  -> Citation C1 -> Source S1
    Media object M2  -> Citation C1 -> Source S1
    Person object P1 -> Citation C2 -> Source S1
    
    The returned structure is rather ugly, but provides all the information in
    a way that is consistent with the other Util functions.
    (
    tuple of objects that refer to the source - only first element is present
        ([C1, C2],),
    list of citations with objects that refer to them
        [
            (C1, 
                tuple of reference lists
                  P,  F,  E,  Pl, S,  M,        R
                ([], [], [], [], [], [M1, M2]. [])
            )
            (C2, 
                tuple of reference lists
                  P,    F,  E,  Pl, S,  M,  R
                ([P1], [], [], [], [], []. [])
            )
        ]
    )
#47738: DEBUG: citationtreeview.py: line 428: source referents [(['bfe59e90dbb555d0d87'],)]
#47743: DEBUG: citationtreeview.py: line 432: citation bfe59e90dbb555d0d87
#47825: DEBUG: citationtreeview.py: line 435: citation_referents_list [[('bfe59e90dbb555d0d87', ([], [], ['ba77932bf0b2d59eccb'], [], [], [], []))]]
#47827: DEBUG: citationtreeview.py: line 440: the_lists [((['bfe59e90dbb555d0d87'],), [('bfe59e90dbb555d0d87', ([], [], ['ba77932bf0b2d59eccb'], [], [], [], []))])]
    
    """
    the_lists = get_source_referents(source_handle, db)
    LOG.debug('source referents %s' % [the_lists])
    # now, for each citation, get the objects that refer to that citation
    citation_referents_list = []
    for citation in the_lists[0]:
        LOG.debug('citation %s' % citation)
        refs = get_citation_referents(citation, db)
        citation_referents_list += [(citation, refs)]
    LOG.debug('citation_referents_list %s' % [citation_referents_list])    
        
    (citation_list) = the_lists
    the_lists = (citation_list, citation_referents_list)

    LOG.debug('the_lists %s' % [the_lists])
    return the_lists 

def get_media_referents(media_handle, db):
    """ Find objects that refer the media object.

    This function finds all primary objects that refer
    to a given media handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 'Source', 'Citation')
    
    return (get_referents(media_handle, db, _primaries))

def get_note_referents(note_handle, db):
    """ Find objects that refer a note object.
    
    This function finds all primary objects that refer
    to a given note handle in a given database.
    
    """
    _primaries = ('Person', 'Family', 'Event', 'Place', 
                  'Source', 'Citation', 'MediaObject', 'Repository')
    
    return (get_referents(note_handle, db, _primaries))
