#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005  Donald N. Allingham
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

# Written by Alex Roitman,
# largely based on ReadXML by Don Allingham

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import GrampsBSDDB
from QuestionDialog import ErrorDialog
import Errors

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None,cl=0,use_trans=True):

    filename = os.path.normpath(filename)

    other_database = GrampsBSDDB.GrampsBSDDB()
    try:
        other_database.load(filename,callback)
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
        else:
            ErrorDialog(_("%s could not be opened") % filename)
        return
    
    trans = database.transaction_begin()
    # copy all data from new_database to database,
    # rename gramps IDs of first-class objects when conflicts are found

    # People table
    for person_handle in other_database.person_map.keys():
        person = other_database.get_person_from_handle(person_handle)
        
        # First, check whether this handle is a duplicate, and do something
        if person_handle in database.person_map.keys():
            raise Errors.HandleError(
                    'Handle %s is already present in the opened database.\n'
                    'Name: %s' % (person_handle,person.get_primary_name().get_regular_name())
                    )
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(person.get_gramps_id())
        if database.id_trans.has_key(gramps_id):
            gramps_id = database.find_next_person_gramps_id()
            person.set_gramps_id(gramps_id)
        database.add_person(person,trans)

    # Family table
    for family_handle in other_database.family_map.keys():
        family = other_database.get_family_from_handle(family_handle)
        
        # First, check whether this handle is a duplicate, and do something
        if family_handle in database.family_map.keys():
            raise Errors.HandleError(
                    'Handle %s is already present in the opened database.' % family_handle
                    )
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(family.get_gramps_id())
        if database.fid_trans.has_key(gramps_id):
            gramps_id = database.find_next_family_gramps_id()
            family.set_gramps_id(gramps_id)
        database.add_family(family,trans)

    # Place table
    for place_handle in other_database.place_map.keys():
        place = other_database.get_place_from_handle(place_handle)
        
        # First, check whether this handle is a duplicate, and do something
        if place_handle in database.place_map.keys():
            raise Errors.HandleError(
                    'Handle %s is already present in the opened database.' % place_handle
                    )
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(place.get_gramps_id())
        if database.pid_trans.has_key(gramps_id):
            gramps_id = database.find_next_place_gramps_id()
            place.set_gramps_id(gramps_id)
        database.add_place(place,trans)

    # Source table
    for source_handle in other_database.source_map.keys():
        source = other_database.get_source_from_handle(source_handle)
        
        # First, check whether this handle is a duplicate, and do something
        if source_handle in database.source_map.keys():
            raise Errors.HandleError(
                    'Handle %s is already present in the opened database.' % source_handle
                    )
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(source.get_gramps_id())
        if database.sid_trans.has_key(gramps_id):
            gramps_id = database.find_next_source_gramps_id()
            source.set_gramps_id(gramps_id)
        database.add_source(source,trans)

    # Media table
    for media_handle in other_database.media_map.keys():
        media = other_database.get_object_from_handle(media_handle)
        
        # First, check whether this handle is a duplicate, and do something
        if media_handle in database.media_map.keys():
            raise Errors.HandleError(
                    'Handle %s is already present in the opened database.' % media_handle
                    )
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(media.get_gramps_id())
        if database.oid_trans.has_key(gramps_id):
            gramps_id = database.find_next_object_gramps_id()
            media.set_gramps_id(gramps_id)
        database.add_object(media,trans)

    # Event table
    for event_handle in other_database.event_map.keys():
        event = other_database.get_event_from_handle(event_handle)
        
        # First, check whether this handle is a duplicate, and do something
        if event_handle in database.event_map.keys():
            raise Errors.HandleError(
                    'Handle %s is already present in the opened database.' % event_handle
                    )
        
        # Events don't have gramps IDs, so we don't need to check here
        database.add_event(event,trans)

    database.transaction_commit(trans,_("Import database"))
