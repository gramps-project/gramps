#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Utils import get_source_referents
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
# "HasTextMatchingSubstringOf"
#-------------------------------------------------------------------------
class HasTextMatchingSubstringOf(Rule):
    """Rule that checks for string matches in any textual information"""

    labels      = [ _('Substring:'),
                    _('Case sensitive:'), 
                    _('Regular-Expression matching:')]
    name        = _('People with records containing <substring>')
    description = _("Matches people whose records contain text "
                    "matching a substring")
    category    = _('General filters')

    def prepare(self,db):
        self.db = db
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.repo_map = {}
        self.family_map = {}
        self.place_map = {}
        self.media_map = {}
        try:
            if int(self.list[1]):
                self.case_sensitive = True
            else:
                self.case_sensitive = False
        except IndexError:
            self.case_sensitive = False
        try:
            if int(self.list[2]):
                self.regexp_match = True
            else:
                self.regexp_match = False
        except IndexError:
            self.regexp_match = False
        self.cache_repos()
        self.cache_sources()

    def reset(self):
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.repo_map = {}
        self.family_map = {}
        self.place_map = {}
        self.media_map = {}

    def apply(self,db,person):
        if person.handle in self.person_map:   # Cached by matching Source?
            return self.person_map[person.handle]
        if self.match_object(person):        # first match the person itself
            return True
        for event_ref in person.get_event_ref_list():
            if self.search_event(event_ref.ref): # match referenced events
                return True
        for family_handle in person.get_family_handle_list(): # match families
            if self.search_family(family_handle):
                return True
        for media_ref in person.get_media_list(): # match Media object
            if self.search_media(media_ref.get_reference_handle()):
                return True
        return False
    
    def search_family(self,family_handle):
        if not family_handle:
            return False
        # search inside the family and cache the result to not search a family twice
        if not family_handle in self.family_map:
            match = 0
            family = self.db.get_family_from_handle(family_handle)
            if self.match_object(family):
                match = 1
            else:
                for event_ref in family.get_event_ref_list():
                    if self.search_event(event_ref.ref):
                        match = 1
                        break
                for media_ref in family.get_media_list(): # match Media object
                    if self.search_media(media_ref.get_reference_handle()):
                        return True
            self.family_map[family_handle] = match
        return self.family_map[family_handle]

    def search_event(self,event_handle):
        if not event_handle:
            return False
        # search inside the event and cache the result (event sharing)
        if not event_handle in self.event_map:
            match = 0
            event = self.db.get_event_from_handle(event_handle)
            if self.match_object(event):
                match = 1
            elif event:
                place_handle = event.get_place_handle()
                if place_handle:
                    if self.search_place(place_handle):
                        match = 1
                for media_ref in event.get_media_list(): # match Media object
                    if self.search_media(media_ref.get_reference_handle()):
                        return True
            self.event_map[event_handle] = match
        return self.event_map[event_handle]

    def search_place(self,place_handle):
        if not place_handle:
            return False
        # search inside the place and cache the result
        if not place_handle in self.place_map:
            place = self.db.get_place_from_handle(place_handle)
            self.place_map[place_handle] = self.match_object(place)
        return self.place_map[place_handle]

    def search_media(self,media_handle):
        if not media_handle:
            return False
        # search inside the place and cache the result
        if not media_handle in self.media_map:
            media = self.db.get_object_from_handle(media_handle)
            self.media_map[media_handle] = self.match_object(media)
        return self.media_map[media_handle]

    def cache_repos(self):
        # search all matching repositories
        for repo_handle in self.db.get_repository_handles():
            repo = self.db.get_repository_from_handle(repo_handle)
            if( self.match_object(repo)):
                self.repo_map[repo_handle] = 1
    
    def cache_sources(self):
        # search all sources and match all referents of a matching source
        for source_handle in self.db.get_source_handles():
            source = self.db.get_source_from_handle(source_handle)
            match = self.match_object(source)
            if not match:
                for reporef in source.get_reporef_list():
                    if reporef.get_reference_handle() in self.repo_map:
                        match = 1
            if match:
                (person_list,family_list,event_list,place_list,source_list,
                     media_list,repo_list
                 ) = get_source_referents(source_handle,self.db)
                for handle in person_list:
                    self.person_map[handle] = 1
                for handle in family_list:
                    self.family_map[handle] = 1
                for handle in event_list:
                    self.event_map[handle] = 1
                for handle in place_list:
                    self.place_map[handle] = 1
                for handle in media_list:
                    self.media_map[handle] = 1
                for handle in repo_list:
                    self.media_map[handle] = 1

    def match_object(self,obj):
        if not obj:
            return False
        if self.regexp_match:
            return obj.matches_regexp(self.list[0],self.case_sensitive)
        return obj.matches_string(self.list[0],self.case_sensitive)
