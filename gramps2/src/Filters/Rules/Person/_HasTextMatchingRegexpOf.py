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
from _HasTextMatchingSubstringOf import HasTextMatchingSubstringOf

#-------------------------------------------------------------------------
# "HasTextMatchingRegexOf"
#-------------------------------------------------------------------------
class HasTextMatchingRegexpOf(HasTextMatchingSubstringOf):
    """This is wrapping HasTextMatchingSubstringOf to enable the regex_match parameter"""
    def __init__(self,list):
        HasTextMatchingSubstringOf.__init__(self,list)

    def prepare(self,db):
        self.db = db
        self.person_map = {}
        self.event_map = {}
        self.source_map = {}
        self.repo_map = {}
        self.family_map = {}
        self.place_map = {}
        self.media_map = {}
        self.case_sensitive = False
        self.regexp_match = True
        self.cache_sources()
