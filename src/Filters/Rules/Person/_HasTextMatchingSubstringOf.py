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

# $Id:_HasTextMatchingSubstringOf.py 9912 2008-01-22 09:17:46Z acraphae $

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

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
        self.person_map = set()
        self.event_map = set()
        self.source_map = set()
        self.repo_map = set()
        self.family_map = set()
        self.place_map = set()
        self.media_map = set()
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
        self.person_map.clear()
        self.event_map.clear()
        self.source_map.clear()
        self.repo_map.clear()
        self.family_map.clear()
        self.place_map.clear()
        self.media_map.clear()

    def apply(self,db,person):
        if person.handle in self.person_map:   # Cached by matching Source?
            return True
        if self.match_object(person):        # first match the person itself
            return True

        # Look for matching events
        if any(self.search_event(event_ref.ref)
            for event_ref in person.get_event_ref_list()):
                return True

        # Look for matching families
        if any(self.search_family(family_handle)
            for family_handle in person.get_family_handle_list()): 
                return True

        # Look for matching media objects
        if any(self.search_media(media_ref.get_reference_handle())
            for media_ref in person.get_media_list()):
                return True
        return False
    
    def search_family(self,family_handle):
        if not family_handle:
            return False
        # search inside the family and cache the result to not search a family twice
        if family_handle not in self.family_map:
            match = 0
            family = self.db.get_family_from_handle(family_handle)
            if self.match_object(family):
                match = 1
            else:
                if any(self.search_event(event_ref.ref)
                    for event_ref in family.get_event_ref_list()):
                        match = 1
                if any(self.search_media(media_ref.get_reference_handle())
                    for media_ref in family.get_media_list()):
                        return True
            if match:
                self.family_map.add(family_handle)
        return family_handle in self.family_map

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
                if place_handle and self.search_place(place_handle):
                    match = 1
                if any(self.search_media(media_ref.get_reference_handle())
                    for media_ref in event.get_media_list()):
                        return True
            if match:
                self.event_map.add(event_handle)
        return event_handle in self.event_map

    def search_place(self,place_handle):
        if not place_handle:
            return False
        # search inside the place and cache the result
        if place_handle not in self.place_map:
            place = self.db.get_place_from_handle(place_handle)
            if self.match_object(place):
                self.place_map.add(place_handle)
        return place_handle in self.place_map

    def search_media(self,media_handle):
        if not media_handle:
            return False
        # search inside the media object and cache the result
        if media_handle not in self.media_map:
            media = self.db.get_object_from_handle(media_handle)
            if self.match_object(media):
                self.media_map.add(media_handle)
        return media_handle in self.media_map

    def cache_repos(self):
        # search all matching repositories
        self.repo_map.update(

            repo.handle for repo in self.db.iter_repositories()
                if self.match_object(repo)

            )
    
    def cache_sources(self):
        # search all sources and match all referents of a matching source
        for source in self.db.iter_sources():
            match = self.match_object(source)
            if not match:
                if any(reporef.get_reference_handle() in self.repo_map
                            for reporef in source.get_reporef_list()
                      ):

                    # Update the maps to reflect the reference
                    (person_list, family_list, event_list, place_list,
                         source_list, media_list, repo_list
                    ) = get_source_referents(source.handle,self.db)
                    self.person_map.update(person_list)
                    self.family_map.update(family_list)
                    self.event_map.update(event_list)
                    self.place_map.update(place_list)
                    self.media_map.update(media_list)
                    self.repo_map.update(repo_list)

    def match_object(self, obj):
        if not obj:
            return False
        if self.regexp_match:
            return obj.matches_regexp(self.list[0],self.case_sensitive)
        return obj.matches_string(self.list[0],self.case_sensitive)
