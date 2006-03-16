#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
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
from TransUtils import sgettext as _
import sets

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from _GrampsBSDDB import GrampsBSDDB
from QuestionDialog import ErrorDialog
import Errors

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None,cl=0,use_trans=True):

    filename = os.path.normpath(filename)

    other_database = GrampsBSDDB()
    try:
        other_database.load(filename,callback)
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
        else:
            ErrorDialog(_("%s could not be opened") % filename)
        return
    if not other_database.version_supported():
        if cl:
            print "Error: %s could not be opened.\n%s  Exiting." \
                  % (filename,
                     _("The database version is not supported "
                       "by this version of GRAMPS.\n"\
                       "Please upgrade to the corresponding version "
                       "or use XML for porting data between different "
                       "database versions."))
        else:
            ErrorDialog(_("%s could not be opened") % filename,
                        _("The Database version is not supported "
                          "by this version of GRAMPS."))
        return
        
    # Check for duplicate handles. At the moment we simply exit here,
    # before modifying any data. In the future we will need to handle
    # this better.
    handles = sets.Set(database.person_map.keys())
    other_handles = sets.Set(other_database.person_map.keys())
    if handles.intersection(other_handles):
        raise Errors.HandleError('Personal handles in two databases overlap.')
        
    handles = sets.Set(database.family_map.keys())
    other_handles = sets.Set(other_database.family_map.keys())
    if handles.intersection(other_handles):
        raise Errors.HandleError('Family handles in two databases overlap.')

    handles = sets.Set(database.place_map.keys())
    other_handles = sets.Set(other_database.place_map.keys())
    if handles.intersection(other_handles):
        raise Errors.HandleError('Place handles in two databases overlap.')

    handles = sets.Set(database.source_map.keys())
    other_handles = sets.Set(other_database.source_map.keys())
    if handles.intersection(other_handles):
        raise Errors.HandleError('Source handles in two databases overlap.')

    handles = sets.Set(database.media_map.keys())
    other_handles = sets.Set(other_database.media_map.keys())
    if handles.intersection(other_handles):
        raise Errors.HandleError('Media handles in two databases overlap.')

    handles = sets.Set(database.event_map.keys())
    other_handles = sets.Set(other_database.event_map.keys())
    if handles.intersection(other_handles):
        raise Errors.HandleError('Event handles in two databases overlap.')

    # Proceed with preparing for import
    if use_trans:
        trans = database.transaction_begin("",batch=True)
    else:
        trans = None

    database.disable_signals()

    # copy all data from new_database to database,
    # rename gramps IDs of first-class objects when conflicts are found

    # People table
    for person_handle in other_database.person_map.keys():
        person = other_database.get_person_from_handle(person_handle)
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(person.get_gramps_id())
        if database.id_trans.has_key(gramps_id):
            gramps_id = database.find_next_person_gramps_id()
            person.set_gramps_id(gramps_id)
        database.add_person(person,trans)

    # Family table
    for family_handle in other_database.family_map.keys():
        family = other_database.get_family_from_handle(family_handle)
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(family.get_gramps_id())
        if database.fid_trans.has_key(gramps_id):
            gramps_id = database.find_next_family_gramps_id()
            family.set_gramps_id(gramps_id)
        database.add_family(family,trans)

    # Place table
    for place_handle in other_database.place_map.keys():
        place = other_database.get_place_from_handle(place_handle)
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(place.get_gramps_id())
        if database.pid_trans.has_key(gramps_id):
            gramps_id = database.find_next_place_gramps_id()
            place.set_gramps_id(gramps_id)
        database.add_place(place,trans)

    # Source table
    for source_handle in other_database.source_map.keys():
        source = other_database.get_source_from_handle(source_handle)
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(source.get_gramps_id())
        if database.sid_trans.has_key(gramps_id):
            gramps_id = database.find_next_source_gramps_id()
            source.set_gramps_id(gramps_id)
        database.add_source(source,trans)

    # Media table
    for media_handle in other_database.media_map.keys():
        media = other_database.get_object_from_handle(media_handle)
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(media.get_gramps_id())
        if database.oid_trans.has_key(gramps_id):
            gramps_id = database.find_next_object_gramps_id()
            media.set_gramps_id(gramps_id)
        database.add_object(media,trans)

    # Event table
    for event_handle in other_database.event_map.keys():
        event = other_database.get_event_from_handle(event_handle)
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(event.get_gramps_id())
        if database.eid_trans.has_key(gramps_id):
            gramps_id = database.find_next_event_gramps_id()
            event.set_gramps_id(gramps_id)
        database.add_event(event,trans)

    # close the other database and clean things up
    other_database.close()

    database.transaction_commit(trans,_("Import database"))
    database.enable_signals()
    database.request_rebuild()
