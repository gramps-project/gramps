# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008 - 2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2009         B. Malengier <benny.malengier@gmail.com>
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
#

"""
Import from the Django dji on the configured database backend

"""

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import time
import sys
import os

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".ImportDjango")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.lib
from QuestionDialog import ErrorDialog
from Utils import create_id
import const

from TransUtils import get_addon_translator
translator = get_addon_translator(__file__)
_ = translator.gettext
ngettext = translator.ngettext

from django.conf import settings
import web.settings as default_settings
try:
    settings.configure(default_settings)
except:
    pass

from web.libdjango import DjangoInterface

#-------------------------------------------------------------------------
#
# Django Reader
#
#-------------------------------------------------------------------------
class DjangoReader(object):
    def __init__(self, db, filename, callback):
        if not callable(callback): 
            callback = lambda (percent): None # dummy
        self.db = db
        self.dji = DjangoInterface()
        self.filename = filename
        self.callback = callback
        self.debug = 0

    def process(self):
        sql = None
        total = (self.dji.Note.count() + 
                 self.dji.Person.count() + 
                 self.dji.Event.count() +
                 self.dji.Family.count() +
                 self.dji.Repository.count() +
                 self.dji.Place.count() +
                 self.dji.Media.count() +
                 self.dji.Source.count())
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        count = 0.0
        self.t = time.time()

        # ---------------------------------
        # Process note
        # ---------------------------------
        notes = self.dji.Note.all()
        for note in notes:
            data = self.dji.get_note(note)
            self.db.note_map[str(note.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process event
        # ---------------------------------
        events = self.dji.Event.all()
        for event in events:
            data = self.dji.get_event(event)
            self.db.event_map[str(event.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process person
        # ---------------------------------
        ## Do this after Events to get the birth/death data
        people = self.dji.Person.all()
        for person in people:
            data = self.dji.get_person(person)
            self.db.person_map[str(person.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process family
        # ---------------------------------
        families = self.dji.Family.all()
        for family in families:
            data = self.dji.get_family(family)
            self.db.family_map[str(family.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process repository
        # ---------------------------------
        repositories = self.dji.Repository.all()
        for repo in repositories:
            data = self.dji.get_repository(repo)
            self.db.repository_map[str(repo.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process place
        # ---------------------------------
        places = self.dji.Place.all()
        for place in places:
            data = self.dji.get_place(place)
            self.db.place_map[str(place.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process source
        # ---------------------------------
        sources = self.dji.Source.all()
        for source in sources:
            data = self.dji.get_source(source)
            self.db.source_map[str(source.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process media
        # ---------------------------------
        media = self.dji.Media.all()
        for med in media:
            data = self.dji.get_media(med)
            self.db.media_map[str(med.handle)] = data
            count += 1
            self.callback(100 * count/total)


        return None

    def cleanup(self):
        self.t = time.time() - self.t
        msg = ngettext('Import Complete: %d second','Import Complete: %d seconds', self.t ) % self.t
        self.db.transaction_commit(self.trans, _("Django import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        LOG.debug(msg)

def import_data(db, filename, callback=None):
    g = DjangoReader(db, filename, callback)
    g.process()
    g.cleanup()

