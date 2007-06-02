#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
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
import sets

#-------------------------------------------------------------------------
#
# GTK+ Modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from GrampsDb._GrampsBSDDB import GrampsBSDDB
from QuestionDialog import ErrorDialog
from Errors import HandleError
from BasicUtils import UpdateCallback
from BasicUtils import NameDisplay
from PluginUtils import register_import

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

    # If other_database contains its custom name formats,
    # we need to do tricks to remap the format numbers
    if len(other_database.name_formats) > 0:
        formats_map = remap_name_formats(database,other_database)
        NameDisplay.displayer.set_name_format(database.name_formats)
        get_person = make_peron_name_remapper(other_database,formats_map)
    else:
        # No remapping necessary, proceed as usual
        get_person = other_database.get_person_from_handle

    # Prepare table and method definitions
    tables = {
        'Person' : {'table' :  database.person_map,
                    'id_table' : database.id_trans,
                    'add_obj' : database.add_person,
                    'find_next_gramps_id' :database.find_next_person_gramps_id,
                    'other_get_from_handle':
                    get_person,
                    'other_table': other_database.person_map,                  
                    },
        'Family' : {'table' :  database.family_map,
                    'id_table' : database.fid_trans,
                    'add_obj' : database.add_family,
                    'find_next_gramps_id' :database.find_next_family_gramps_id,
                    'other_get_from_handle':
                    other_database.get_family_from_handle,
                    'other_table': other_database.family_map,                  
                    },

        'Event' : {'table' :  database.event_map,
                   'id_table' : database.eid_trans,
                   'add_obj' : database.add_event,
                   'find_next_gramps_id' : database.find_next_event_gramps_id,
                   'other_get_from_handle':
                   other_database.get_event_from_handle,
                   'other_table': other_database.event_map,                  
                    },
        'Source' : {'table' :  database.source_map,
                    'id_table' : database.sid_trans,
                    'add_obj' : database.add_source,
                    'find_next_gramps_id': database.find_next_source_gramps_id,
                    'other_get_from_handle':
                    other_database.get_source_from_handle,
                    'other_table': other_database.source_map,                  
                    },
        'Place' : {'table' :  database.place_map,
                   'id_table' : database.pid_trans,
                   'add_obj' : database.add_place,
                   'find_next_gramps_id' :database.find_next_place_gramps_id,
                   'other_get_from_handle':
                   other_database.get_place_from_handle,
                   'other_table': other_database.place_map,                  
                   },
        'Media' : {'table' :  database.media_map,
                   'id_table' : database.oid_trans,
                   'add_obj' : database.add_object,
                   'find_next_gramps_id' : database.find_next_object_gramps_id,
                   'other_get_from_handle':
                   other_database.get_object_from_handle,
                   'other_table': other_database.media_map,                  
                   },
        'Repository' : {'table' :  database.repository_map,
                        'id_table' : database.rid_trans,
                        'add_obj' : database.add_repository,
                        'find_next_gramps_id' :
                        database.find_next_repository_gramps_id,
                        'other_get_from_handle':
                        other_database.get_repository_from_handle,
                        'other_table': other_database.repository_map,
                        },
        'Note' : {'table':  database.note_map,
                    'id_table': database.nid_trans,
                    'add_obj': database.add_note,
                    'find_next_gramps_id': database.find_next_note_gramps_id,
                    'other_get_from_handle':
                    other_database.get_note_from_handle,
                    'other_table': other_database.note_map,                  
                    },
        }

    uc = UpdateCallback(callback)
    uc.set_total(len(tables.keys()))

    the_len = 0

    # Check for duplicate handles.
    for key in tables:
        table_dict = tables[key]
        table = table_dict['table']
        other_table = table_dict['other_table']
        msg = '%s handles in two databases overlap.' % key
        the_len += check_common_handles(table,other_table,msg)
        uc.update()
        
    # Proceed with preparing for import
    if use_trans:
        trans = database.transaction_begin("",batch=True)
    else:
        print "Transaction is None! This is no way to go!"
        trans = None

    database.disable_signals()

    # copy all data from new_database to database,
    # rename gramps IDs of first-class objects when conflicts are found
    uc.set_total(the_len)

    for key in tables:
        table_dict = tables[key]
        id_table = table_dict['id_table']
        add_obj = table_dict['add_obj']
        find_next_gramps_id = table_dict['find_next_gramps_id']
        other_table = table_dict['other_table']
        other_get_from_handle = table_dict['other_get_from_handle']
        import_table(id_table,add_obj,find_next_gramps_id,
                     other_table,other_get_from_handle,trans,uc)

    # Copy bookmarks over:
    # we already know that there's no overlap in handles anywhere
    database.bookmarks.append_list(other_database.bookmarks.get())
    database.family_bookmarks.append_list(other_database.family_bookmarks.get())
    database.event_bookmarks.append_list(other_database.event_bookmarks.get())
    database.source_bookmarks.append_list(other_database.source_bookmarks.get())
    database.place_bookmarks.append_list(other_database.place_bookmarks.get())
    database.media_bookmarks.append_list(other_database.media_bookmarks.get())
    database.repo_bookmarks.append_list(other_database.repo_bookmarks.get())
    database.note_bookmarks.append_list(other_database.note_bookmarks.get())

    # close the other database and clean things up
    other_database.close()

    database.transaction_commit(trans,_("Import database"))
    database.enable_signals()
    database.request_rebuild()

def check_common_handles(table,other_table,msg):
    # Check for duplicate handles. At the moment we simply exit here,
    # before modifying any data. In the future we will need to handle
    # this better. How?
    handles = sets.Set(table.keys())
    other_handles = sets.Set(other_table.keys())
    if handles.intersection(other_handles):
        raise HandleError(msg)
    return len(other_handles)
    
def import_table(id_table,add_obj,find_next_gramps_id,
                other_table,other_get_from_handle,trans,uc):

    for handle in other_table.keys():
        obj = other_get_from_handle(handle)
        
        # Then we check gramps_id for conflicts and change it if needed
        gramps_id = str(obj.gramps_id)
        if id_table.has_key(gramps_id):
            gramps_id = find_next_gramps_id()
            obj.gramps_id = gramps_id
        add_obj(obj,trans)
        uc.update()

def remap_name_formats(database,other_database):
    formats_map = {}
    taken_numbers = [num for (num,name,fmt_str,active)
                     in database.name_formats]
    for (number,name,fmt_str,act) in other_database.name_formats:
        if number in taken_numbers:
            new_number = -1
            while new_number in taken_numbers:
                new_number -= 1
            taken_numbers.append(new_number)
            formats_map[number] = new_number
        else:
            new_number = number
        database.name_formats.append((new_number,name,fmt_str,act))
    return formats_map

def remap_name(person,formats_map):
    for name in [person.primary_name] + person.alternate_names:
        try:
            name.sort_as = formats_map[name.sort_as]
        except KeyError:
            pass
        try:
            name.display_as = formats_map[name.display_as]
        except KeyError:
            pass

def make_peron_name_remapper(other_database,formats_map):
    def new_get_person(handle):
        person = other_database.get_person_from_handle(handle)
        remap_name(person,formats_map)
        return person
    return new_get_person

#------------------------------------------------------------------------
#
# Register with the plugin system
#
#------------------------------------------------------------------------
_mime_type = 'application/x-gramps'
_filter = gtk.FileFilter()
_filter.set_name(_('GRAMPS 2.x database'))
_filter.add_mime_type(_mime_type)
_format_name = _('GRAMPS 2.x database')

register_import(importData,_filter,_mime_type,0,_format_name)
