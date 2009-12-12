#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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
# Standard python modules
#
#-------------------------------------------------------------------------
from cStringIO import StringIO
from gettext import gettext as _
import os

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".DisplayState")

#-------------------------------------------------------------------------
#
# GNOME python modules
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.utils
from gui.utils import process_pending_events
import config
from BasicUtils import name_displayer
import const
import ManagedWindow
import Relationship
from glade import Glade

DISABLED = -1

#-------------------------------------------------------------------------
#
# History manager
#
#-------------------------------------------------------------------------
class History(gen.utils.Callback):
    """ History manages the objects of a certain type that have been viewed, 
        with ability to go back, or forward. 
        When accessing an object, it should be pushed on the History.
    """

    __signals__ = {
        'changed'      : (list, ), 
        'menu-changed' : (list, ), 
        }

    def __init__(self):
        gen.utils.Callback.__init__(self)
        self.clear()

    def clear(self):
        """
        Clears the history, resetting the values back to their defaults
        """
        self.history = []
        self.mhistory = []
        self.index = -1
        self.lock = False

    def remove(self, handle, old_id=None):
        """
        Remove a handle from the history list
        """
        if old_id:
            del_id = old_id
        else:
            del_id = handle

        history_count = self.history.count(del_id)
        for c in range(history_count):
            self.history.remove(del_id)
            self.index -= 1
        
        mhc = self.mhistory.count(del_id)
        for c in range(mhc):
            self.mhistory.remove(del_id)
        self.emit('changed', (self.history, ))
        self.emit('menu-changed', (self.mhistory, ))

    def push(self, handle):
        """
        Pushes the handle on the history stack
        """
        self.prune()
        if len(self.history) == 0 or handle != self.history[-1]:
            self.history.append(handle)
            if handle in self.mhistory:
                self.mhistory.remove(handle)
            self.mhistory.append(handle)
            self.index += 1
        self.emit('menu-changed', (self.mhistory, ))
        self.emit('changed', (self.history, ))

    def forward(self, step=1):
        """
        Moves forward in the history list
        """
        self.index += step
        handle = self.history[self.index]
        if handle not in self.mhistory:
            self.mhistory.append(handle)
            self.emit('menu-changed', (self.mhistory, ))
        return str(self.history[self.index])

    def back(self, step=1):
        """
        Moves backward in the history list
        """
        self.index -= step
        try:
            handle = self.history[self.index]
            if handle not in self.mhistory:
                self.mhistory.append(handle)
                self.emit('menu-changed', (self.mhistory, ))
            return str(self.history[self.index])
        except IndexError:
            return u""
        
    def present(self):
        """
        return the person handle that is now active in the history
        """
        try :
            if self.history :
                return self.history[self.index]
            else:
                return u""
        except IndexError:
            return u""
        
    def at_end(self):
        """
        returns True if we are at the end of the history list
        """
        return self.index+1 == len(self.history)

    def at_front(self):
        """
        returns True if we are at the front of the history list
        """
        return self.index <= 0

    def prune(self):
        """
        Truncates the history list at the current object.
        """
        if not self.at_end():
            self.history = self.history[0:self.index+1]


#-------------------------------------------------------------------------
#
# Recent Docs Menu
#
#-------------------------------------------------------------------------

_RCT_TOP = '<ui><menubar name="MenuBar"><menu action="FileMenu"><menu action="OpenRecent">'
_RCT_BTM = '</menu></menu></menubar></ui>'

import RecentFiles
import os

class RecentDocsMenu(object):
    def __init__(self, uistate, state, fileopen):
        self.action_group = gtk.ActionGroup('RecentFiles')
        self.active = DISABLED
        self.uistate = uistate
        self.uimanager = uistate.uimanager
        self.fileopen = fileopen
        self.state = state

    def load(self, item):
        filename = item.get_path()
        self.fileopen(filename)

    def build(self):
        buf = StringIO()
        buf.write(_RCT_TOP)
        gramps_rf = RecentFiles.RecentFiles()

        count = 0
        
        if self.active != DISABLED:
            self.uimanager.remove_ui(self.active)
            self.uimanager.remove_action_group(self.action_group)
            self.action_group = gtk.ActionGroup('RecentFiles')
            self.active = DISABLED
            
        actions = []
        rfiles = gramps_rf.gramps_recent_files
        rfiles.sort(by_time)

        new_menu = gtk.Menu()

        for item in rfiles:
            try:
                title = item.get_name().replace('_', '__')
                filename = os.path.basename(item.get_path())
                action_id = "RecentMenu%d" % count
                buf.write('<menuitem action="%s"/>' % action_id)
                actions.append((action_id, None, title, None, None, 
                                make_callback(item, self.load)))
                mitem = gtk.MenuItem(title)
                mitem.connect('activate', make_callback(item, self.load))
                mitem.show()
                new_menu.append(mitem)
            except RuntimeError:
                pass    # ignore no longer existing files
            
            count += 1
        buf.write(_RCT_BTM)
        self.action_group.add_actions(actions)
        self.uimanager.insert_action_group(self.action_group, 1)
        self.active = self.uimanager.add_ui_from_string(buf.getvalue())
        self.uimanager.ensure_update()
        buf.close()

        if len(rfiles) > 0:
            new_menu.show()
            self.uistate.set_open_recent_menu(new_menu)

def make_callback(val, func):
    return lambda x: func(val)

def by_time(first, second):
    return cmp(second.get_time(), first.get_time())


from GrampsLogger import RotateHandler

class WarnHandler(RotateHandler):

    def __init__(self, capacity, button):
        RotateHandler.__init__(self, capacity)
        self.setLevel(logging.WARN)
        self.button = button
        button.on_clicked(self.display)
        self.timer = None

    def emit(self, record):
        if self.timer:
            gobject.source_remove(self.timer)
        gobject.timeout_add(180*1000, self._clear)
        RotateHandler.emit(self, record)
        self.button.show()

    def _clear(self):
        self.button.hide()
        self.set_capacity(self._capacity)
        self.timer = None
        return False

    def display(self, obj):
        obj.hide()
        self.glade = Glade()
        top = self.glade.toplevel
        msg = self.glade.get_object('msg')
        buf = msg.get_buffer()
        for i in self.get_formatted_log():
            buf.insert_at_cursor(i + '\n')
        self.set_capacity(self._capacity)
        top.run()
        top.destroy()

class DisplayState(gen.utils.Callback):

    __signals__ = {
        'filters-changed' : (str, ), 
        'filter-name-changed' : (str, unicode, unicode), 
        'nameformat-changed' : None, 
        }

    def __init__(self, window, status, progress, warnbtn, uimanager, 
                 progress_monitor, viewmanager=None):

        self.busy = False
        self.viewmanager = viewmanager
        self.uimanager = uimanager
        self.progress_monitor = progress_monitor
        self.window = window
        gen.utils.Callback.__init__(self)
        self.status = status
        self.status_id = status.get_context_id('GRAMPS')
        self.progress = progress
        self.phistory = History()
        self.gwm = ManagedWindow.GrampsWindowManager(uimanager)
        self.widget = None
        self.disprel_old = ''
        self.disprel_defpers = None
        self.disprel_active = None
        self.warnbtn = warnbtn
        self.last_bar = self.status.insert(min_width=15, ralign=True)
        self.set_relationship_class()

        formatter = logging.Formatter('%(levelname)s %(name)s: %(message)s')
        self.rhandler = WarnHandler(capacity=400, button=warnbtn)
        self.rhandler.setFormatter(formatter)
        self.rhandler.setLevel(logging.WARNING)
        self.log = logging.getLogger()
        self.log.addHandler(self.rhandler)
        # This call has been moved one level up, 
        # but this connection is still made!
        # self.dbstate.connect('database-changed', self.db_changed)

    def set_sensitive(self, state):
        self.window.set_sensitive(state)
        
    def db_changed(self, db):
        db.connect('long-op-start', self.progress_monitor.add_op)

    def set_relationship_class(self):
        """method that rebinds the relationship to the current rel calc
           Should be called after load or reload of plugins
        """
        self.relationship = Relationship.get_relationship_calculator(reinit=True)

    def set_gendepth(self, value):
        """ Set the generations we search back for showing relationships
            on GRAMPS interface. Value must be integer > 0
            This method will be used by the preference editor when user changes
            the generations. 
        """
        self.relationship.set_depth(value)
        
    def display_relationship(self, dbstate):
        """ Construct the relationship in order to show it in the statusbar
            This can be a time intensive calculation, so we only want to do
            it if persons are different than before.
            Eg: select a person, then double click, will result in calling
                three times to construct build the statusbar. We only want
                to obtain relationship once!
            This means the relationship part of statusbar only changes on
            change of row.
        """
        self.relationship.connect_db_signals(dbstate)
        default_person = dbstate.db.get_default_person()
        active = dbstate.get_active_person()
        if default_person is None or active is None:
            return u''
        if default_person.handle == self.disprel_defpers and \
                active.handle == self.disprel_active :
            return self.disprel_old
        
        name = self.relationship.get_one_relationship(
                                            dbstate.db, default_person, active)
        #store present call data
        self.disprel_old = name
        self.disprel_defpers = default_person.handle
        self.disprel_active = active.handle
        if name:
            return name
        else:
            return u""

    def clear_history(self, handle=None):
        """Clear the history. If handle is given, then the history is 
            immediately initialized with a first entry 
            (you'd eg want active person you view there as History contains the 
             present object too!)
        """
        self.phistory.clear()
        if handle :
            self.phistory.push(handle)

    def set_busy_cursor(self, value):
        if value == self.busy:
            return
        else:
            self.busy = value
        if value:
            self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        else:
            self.window.window.set_cursor(None)
        process_pending_events()

    def set_open_widget(self, widget):
        self.widget = widget

    def set_open_recent_menu(self, menu):
        self.widget.set_menu(menu)

    def push_message(self, dbstate, text):
        self.status_text(text)
        gobject.timeout_add(5000, self.modify_statusbar, dbstate)

    def show_filter_results(self, dbstate, matched, total):
        text = "%d/%d" % (matched, total)
        self.status.pop(1, self.last_bar)
        self.status.push(1, text, self.last_bar)

    def clear_filter_results(self):
        self.status.pop(1, self.last_bar)
        self.status.push(1, '', self.last_bar)

    def modify_statusbar(self, dbstate, active=None):
        self.status.pop(self.status_id)
        if dbstate.active is None:
            self.status.push(self.status_id, "")
        else:
            person = dbstate.get_active_person()
            if person:
                pname = name_displayer.display(person)
                name = "[%s] %s" % (person.get_gramps_id(), pname)
                if config.get('interface.statusbar') > 1:
                    if person.handle != dbstate.db.get_default_handle():
                        msg = self.display_relationship(dbstate)
                        if msg:
                            name = "%s (%s)" % (name, msg.strip())
            else:
                name = _("No active person")
            self.status.push(self.status_id, name)
        process_pending_events()

    def pulse_progressbar(self, value):
        self.progress.set_fraction(min(value/100.0, 1.0))
        self.progress.set_text("%d%%" % value)
        process_pending_events()

    def status_text(self, text):
        self.status.pop(self.status_id)
        self.status.push(self.status_id, text)
        process_pending_events()
