# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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

# $Id$

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import Gramplet
from TransUtils import sgettext as _
from BasicUtils import name_displayer

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class LogGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Click name to change active\nDouble-click name to edit"))
        self.set_text(_("Log for this Session"))
        self.gui.force_update = True # will always update, even if minimized
        self.last_log = None
        self.append_text("\n")

    def db_changed(self):
        self.append_text(_("Opened data base -----------\n"))
        self.dbstate.db.connect('person-add', 
                                lambda handles: self.log(_('Person'), _('Added'), handles))
        self.dbstate.db.connect('person-delete', 
                                lambda handles: self.log(_('Person'), _('Deleted'), handles))
        self.dbstate.db.connect('person-update', 
                                lambda handles: self.log(_('Person'), _('Edited'), handles))
        self.dbstate.db.connect('family-add', 
                                lambda handles: self.log(_('Family'), _('Added'), handles))
        self.dbstate.db.connect('family-delete', 
                                lambda handles: self.log(_('Family'), _('Deleted'), handles))
        self.dbstate.db.connect('family-update', 
                                lambda handles: self.log(_('Family'), _('Added'), handles))
    
    def active_changed(self, handle):
        self.log(_('Person'), _('Selected'), [handle])

    def log(self, ltype, action, handles):
        for handle in set(handles):
            if self.last_log == (ltype, action, handle):
                continue
            self.last_log = (ltype, action, handle)
            self.append_text("%s: " % action)
            if ltype == _("Person"):
                person = self.dbstate.db.get_person_from_handle(handle)
                name = name_displayer.display(person)
            elif ltype == _("Family"):
                family = self.dbstate.db.get_family_from_handle(handle)
                father_name = _("unknown")
                mother_name = _("unknown")
                if family:
                    father_handle = family.get_father_handle()
                    if father_handle:
                        father = self.dbstate.db.get_person_from_handle(father_handle)
                        if father:
                            father_name = name_displayer.display(father)
                    mother_handle = family.get_mother_handle()
                    if mother_handle:
                        mother = self.dbstate.db.get_person_from_handle(mother_handle)
                        mother_name = name_displayer.display(mother)
                name = _("%s and %s") % (mother_name, father_name)
            self.link(name, ltype, handle)
            self.append_text("\n")
