#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2017       Alois Poettker <alois.poettker@gmx.de>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Change id IDs of all the elements in the database to conform to the
scheme specified in the database's prefix_fmt ids
"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import re

from gi.repository import Gtk, Gdk

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

from gramps.gen.db import DbTxn
from gramps.gen.lib import (Person, Family, Event, Place,
                            Source, Citation, Repository,
                            Media, Note)

from gramps.gui.display import display_help
from gramps.gui.glade import Glade
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.plug import tool
from gramps.gen.updatecallback import UpdateCallback
from gramps.gui.utils import ProgressMeter
from gramps.gui.widgets import MonitoredCheckbox, MonitoredEntry

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Reorder_Gramps_ID')

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------

# gets the number specified in a format string, eg: %04d returns '04'
_parseformat = re.compile('.*%(\d+)[^\d]+')

class ReorderEntry(object):
    """ Class for internal values for every primary object """

    def __init__(self, object_fmt, quant_id, nextgramps_id):
        self.width_fmt = 4
        self.object_fmt, self.object_prefix = '', ''
        self.quant_id, self.actual_id, self.actgramps_id = 0, 0, '0'
        self.calc_id(object_fmt, quant_id)
        self.stored_fmt = object_fmt
        self.stored_prefix = self.object_prefix

        self.number_id = int(nextgramps_id.split(self.object_prefix, 1)[1])
        self.step_id = 1
        self.active_obj, self.change_obj, self.keep_obj = True, False, False

    def set_active(self, active):
        """ sets Change flag """
        self.active_obj = active

    def get_active(self):
        """ gets Change flag """
        return self.active_obj

    def set_fmt(self, object_fmt):
        """ sets primary object format """
        if object_fmt:
            self.calc_id(object_fmt, self.quant_id)

    def get_fmt(self):
        """ gets primary object format """
        return self.object_fmt

    def res_fmt(self):
        """ restore primary object format """
        return self.stored_fmt

    def set_change(self, change):
        """ sets Change flag """
        self.change_obj = change

    def get_change(self):
        """ gets Change flag """
        return self.change_obj

    def __ret_gid(self, actual):
        """ return Gramps ID in correct format """
        return '%s%s' % \
               (self.object_prefix, str(actual).zfill(self.width_fmt))

    def calc_id(self, object_fmt, quant_id):
        """ calculates identifier prefix, format & actual value """
        self.object_prefix = object_fmt.split('%', 1)[0] if '%' in object_fmt else ''
        self.object_fmt, self.quant_id = object_fmt, quant_id

        # Default values, ID counting starts with zero!
        self.width_fmt, self.actual_id = 4, 0
        formatmatch = _parseformat.match(object_fmt)
        if formatmatch:
            self.width_fmt = int(formatmatch.groups()[0])
        self.actgramps_id = self.__ret_gid(self.actual_id)

    def zero_id(self):
        """ provide zero Start ID """
        return self.__ret_gid(0)

    def set_id(self, actual):
        """ sets Start ID """
        text = ''.join([i for i in actual.strip() if i in '0123456789'])
        self.actual_id = int(text) if text else 0

    def get_id(self):
        """ gets Start ID """
        return self.__ret_gid(self.actual_id)

    def next_id(self):
        """ provide next Start ID """
        return self.__ret_gid(self.number_id)

    def succ_id(self):
        """ provide next actual Gramps ID """
        self.actual_id += self.step_id
        self.actgramps_id = self.__ret_gid(self.actual_id)

        return self.actgramps_id

    def last_id(self):
        """ provide quantities of Gramps IDs """
        if self.quant_id > 0:
            return self.__ret_gid(self.quant_id -1)
        else:
            return self.__ret_gid(0)

    def set_step(self, step):
        """ sets ID Step width """
        text = ''.join([i for i in step.strip() if i in '0123456789'])
        self.step_id = int(text) if text else 1

    def get_step(self):
        """ gets ID Step width """
        return str(self.step_id)

    def change_step(self, step_entry):
        """ change Glade Step entry """
        step_id = step_entry.get_text().strip()
        if step_id and step_id != str(self.step_id):
            step_entry.set_text(str(self.step_id))

    def set_keep(self, keep):
        """ sets Keep flag """
        self.keep_obj = keep

    def get_keep(self):
        """ gets Keep flag """
        return self.keep_obj

class ReorderIds(ManagedWindow, UpdateCallback):
    """ Class for Reodering Gramps ID Tool """
    xobjects = (('person', 'people'), ('family', 'families'),
                ('event', 'events'), ('place', 'places'),
                ('source', 'sources'), ('citation', 'citations'),
                ('repository', 'repositories'),
                ('media', 'media'), ('note', 'notes'))

    def __init__(self, dbstate, user, options_class, name, callback=None):
        self.uistate = user.uistate
        self.dbstate = dbstate.db

        ManagedWindow.__init__(self, self.uistate, [], self.__class__)
        if not self.uistate:
            UpdateCallback.__init__(self, user.callback)

        self.object_status = True
        self.change_status = False
        self.start_zero = True
        self.step_cnt, self.step_list = 0, ['1', '2', '5', '10']
        self.keep_status = True

        self.obj_values = {}   # enable access to all internal values
        self.active_entries, self.format_entries = {}, {}
        self.change_entries = {}
        self.start_entries, self.step_entries = {}, {}
        self.keep_entries = {}

        self.prim_methods, self.obj_methods = {}, {}
        for prim_obj, prim_objs in self.xobjects:
            class_type = prim_obj.title()
            table = "self.dbstate.%s_map" % prim_obj
            get_number_obj = "self.dbstate.get_number_of_%s" % prim_objs
            prefix_fmt = "self.dbstate.%s_prefix" % prim_obj
            get_from_id = "self.dbstate.get_%s_from_gramps_id" % prim_obj
            get_from_handle = "self.dbstate.get_%s_from_handle" % prim_obj
            next_from_id = "self.dbstate.find_next_%s_gramps_id" % prim_obj
            commit = "self.dbstate.commit_%s" % prim_obj

            self.prim_methods[prim_obj] = (eval(prefix_fmt), eval(get_number_obj)(),
                                           eval(next_from_id)())
            self.obj_methods[prim_obj] = (eval(class_type), eval(table), eval(commit),
                                          eval(get_from_id), eval(get_from_handle),
                                          eval(next_from_id))

            object_fmt, quant_id, next_id = self.prim_methods[prim_obj]

            obj_value = ReorderEntry(object_fmt, quant_id, next_id)
            self.obj_values[prim_obj] = obj_value

        if self.uistate:
            self._display()
        else:
            self._execute()

    def _display(self):
        """ organize Glade 'Reorder IDs' window """
        # get the main window from glade
        self.gtk = Glade()
        window = self.gtk.toplevel

        # set gramps style title for the window
        self.set_window(window, self.gtk.get_object("title"), \
                        _("Reorder Gramps IDs"))

        # connect signals
        self.gtk.connect_signals({
            "on_warning_exp_activate" : self.__on_expander_activate,
            "on_selection_exp_activate" : self.__on_expander_activate,
            "on_object_button_clicked" : self.__on_object_button_clicked,
            "on_object_button_toggled" : self.__on_object_button_toggled,
            "on_format_button_clicked" : self.__on_format_button_clicked,
            "on_start_button_clicked" : self.__on_start_button_clicked,
            "on_step_button_clicked" : self.__on_step_button_clicked,
            "on_keep_button_clicked" : self.__on_keep_button_clicked,
            "on_change_button_clicked" : self.__on_change_button_clicked,
            "on_change_button_toggled" : self.__on_change_button_toggled,
            "on_format_entry_keyrelease" : self.__on_format_entry_keyrelease,
            "on_format_entry_focusout" : self.__on_format_entry_focusout,
            "on_start_entry_focusout" : self.__on_start_entry_focusout,
            "on_help_button_clicked" : self.__on_help_button_clicked,
            "on_cancel_button_clicked" : self.close,
            "on_ok_button_clicked" : self.__on_ok_button_clicked
        })

        # Calculate all entries and update Glade window
        for prim_obj, tmp in self.xobjects:
            # populate Object, Actual & Quantity fields with values
            obj_active = self.gtk.get_object('%s_active' % prim_obj)
            self.active_entries[prim_obj] = MonitoredCheckbox(obj_active, obj_active,
                                        self.obj_values[prim_obj].set_active,
                                        self.obj_values[prim_obj].get_active)
            obj_actual = self.gtk.get_object('%s_actual' % prim_obj)
            obj_actual.set_text('%s' % self.obj_values[prim_obj].last_id())
            obj_quant = self.gtk.get_object('%s_quant' % prim_obj)
            obj_quant.set_text('%s' % str(self.obj_values[prim_obj].quant_id))

            # connect/populate Format, Start, Step, Keep & Change fields with GTK/values
            obj_format = self.gtk.get_object('%s_format' % prim_obj)
            self.format_entries[prim_obj] = MonitoredEntry(obj_format,
                                    self.obj_values[prim_obj].set_fmt,
                                    self.obj_values[prim_obj].get_fmt)
            obj_change = self.gtk.get_object('%s_change' % prim_obj)
            self.change_entries[prim_obj] = MonitoredCheckbox(obj_change, obj_change,
                                    self.obj_values[prim_obj].set_change,
                                    self.obj_values[prim_obj].get_change)
            obj_start = self.gtk.get_object('%s_start' % prim_obj)
            self.start_entries[prim_obj] = MonitoredEntry(obj_start,
                                    self.obj_values[prim_obj].set_id,
                                    self.obj_values[prim_obj].get_id)
            obj_step = self.gtk.get_object('%s_step' % prim_obj)
            self.step_entries[prim_obj] = MonitoredEntry(obj_step,
                                    self.obj_values[prim_obj].set_step,
                                    self.obj_values[prim_obj].get_step,
                                    changed=self.obj_values[prim_obj].change_step)
            obj_keep = self.gtk.get_object('%s_keep' % prim_obj)
            self.keep_entries[prim_obj] = MonitoredCheckbox(obj_keep, obj_keep,
                                    self.obj_values[prim_obj].set_keep,
                                    self.obj_values[prim_obj].get_keep,
                                    readonly=True)

        # fetch the popup menu
        self.menu = self.gtk.get_object("popup_menu")

        # ok, let's see what we've done
        self.show()

    def __on_expander_activate(self, widget=None):
        """ de-/activate the expander's after toggle the 'Active' attribute """
        warn_exp = self.gtk.get_object('warning_exp')
        warn_state = warn_exp.get_expanded()
        select_exp = self.gtk.get_object('selection_exp')
        select_state = select_exp.get_expanded()

        if not select_state:
            warn_exp.set_expanded(False)

    def __on_object_button_clicked(self, widget=None):
        """ compute all primary objects and toggle the 'Active' attribute """
        self.object_status = not self.object_status

        for prim_obj, tmp in self.xobjects:
            obj = self.gtk.get_object('%s_active' % prim_obj)
            obj.set_active(self.object_status)

    def __on_object_button_toggled(self, widget):
        """ compute the primary object and toggle the 'Sensitive' attribute """
        obj_state = widget.get_active()
        obj_name = Gtk.Buildable.get_name(widget).split('_', 1)[0]

        self.active_entries[obj_name].set_val(obj_state)

        for obj_entry in ['actual', 'quant', 'format', 'change']:
            obj = self.gtk.get_object('%s_%s' % (obj_name, obj_entry))
            obj.set_sensitive(obj_state)

        for obj_entry in ['start', 'step', 'keep']:
            obj = self.gtk.get_object('%s_change' % obj_name)
            if obj.get_active():
                obj = self.gtk.get_object('%s_%s' % (obj_name, obj_entry))
                obj.set_sensitive(obj_state)

    def __on_format_button_clicked(self, widget=None):
        """ compute all sensitive primary objects and sets the
            'Format' scheme of identifiers """
        for prim_obj, tmp in self.xobjects:
            obj_format = self.gtk.get_object('%s_format' % prim_obj)
            if not obj_format.get_sensitive():
                continue

            obj_fmt = self.obj_values[prim_obj].res_fmt()
            self.format_entries[prim_obj].force_value(obj_fmt)
            if self.start_zero:
                obj_id = self.obj_values[prim_obj].zero_id()
            else:
                obj_id = self.obj_values[prim_obj].last_id()
            self.start_entries[prim_obj].force_value(obj_id)

    def __on_change_button_clicked(self, widget=None):
        """ compute all primary objects and toggle the 'Change' attribute """
        self.change_status = not self.change_status

        for prim_obj, tmp in self.xobjects:
            obj_change = self.gtk.get_object('%s_change' % prim_obj)
            if not obj_change.get_sensitive():
                continue

            self.change_entries[prim_obj].set_val(self.change_status)
            obj_change.set_active(self.change_status)

    def __on_change_button_toggled(self, widget):
        """ compute the primary object and toggle the 'Sensitive' attribute """
        obj_state = widget.get_active()
        obj_name = Gtk.Buildable.get_name(widget).split('_', 1)[0]

        for obj_entry in ['start', 'step', 'keep']:
            obj = self.gtk.get_object('%s_%s' % (obj_name, obj_entry))
            if obj_entry == 'keep':
                if self.obj_values[obj_name].stored_prefix != \
                   self.obj_values[obj_name].object_prefix:
                    self.keep_entries[obj_name].set_val(False)
                else:
                    obj.set_active(obj_state)
                    self.keep_entries[obj_name].set_val(obj_state)
            obj.set_sensitive(obj_state)

    def __on_start_button_clicked(self, widget=None):
        """ compute all sensitive primary objects and sets the
            'Start' values of identifiers """
        self.start_zero = not self.start_zero

        for prim_obj, tmp in self.xobjects:
            obj = self.gtk.get_object('%s_start' % prim_obj)
            if not obj.get_sensitive():
                continue

            if self.start_zero:
                obj_id = self.obj_values[prim_obj].zero_id()
            else:
                obj_id = self.obj_values[prim_obj].next_id()
            self.start_entries[prim_obj].force_value(obj_id)

    def __on_step_button_clicked(self, widget=None):
        """ compute all sensitive primary objects and sets the
            'Step' width of identifiers """
        self.step_cnt = self.step_cnt +1 if self.step_cnt < 3 else 0

        for prim_obj, tmp in self.xobjects:
            obj = self.gtk.get_object('%s_step' % prim_obj)
            if not obj.get_sensitive():
                continue

            step_val = self.step_list[self.step_cnt]
            self.step_entries[prim_obj].force_value(step_val)

    def __on_keep_button_clicked(self, widget=None):
        """ compute the primary object and toggle the 'Active' attribute """
        self.keep_status = not self.keep_status

        for prim_obj, tmp in self.xobjects:
            obj = self.gtk.get_object('%s_change' % prim_obj)
            if not obj.get_active():
                continue

            obj = self.gtk.get_object('%s_keep' % prim_obj)
            obj.set_active(self.keep_status)
            self.keep_entries[prim_obj].set_val(self.keep_status)

    def __on_format_entry_keyrelease(self, widget, event, data=None):
        """ activated on all return's of an entry """
        if event.keyval in [Gdk.KEY_Return]:
            obj_name = Gtk.Buildable.get_name(widget).split('_', 1)[0]
            obj_fmt = self.format_entries[obj_name].get_val()
            self.format_entries[obj_name].force_value(obj_fmt)

            obj_change = self.gtk.get_object('%s_change' % obj_name)
            obj_change.grab_focus()

        return False

    def __on_format_entry_focusout(self, widget, event, data=None):
        """ activated on all focus out of an entry """
        obj_name = Gtk.Buildable.get_name(widget).split('_', 1)[0]
        obj_fmt = self.format_entries[obj_name].get_val()

        self.format_entries[obj_name].set_val(obj_fmt)
        self.start_entries[obj_name].update()

        return False

    def __on_start_entry_focusout(self, widget, event, data=None):
        """ activated on all focus out of an entry """
        obj_name = Gtk.Buildable.get_name(widget).split('_', 1)[0]
        self.start_entries[obj_name].update()

        return False

    def __on_ok_button_clicked(self, widget=None):
        """ execute the reodering and close """
        self._execute()
        self.close()

    def __on_help_button_clicked(self, widget=None):
        """ display the relevant portion of Gramps manual """
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def build_menu_names_(self, widget=None):
        """ The menu name """
        return (_('Main window'), _("Reorder Gramps IDs"))

    def _execute(self):
        """ execute all primary objects and reorder if neccessary """

        # Update progress calculation
        if self.uistate:
            self.progress = ProgressMeter(_('Reorder Gramps IDs'), '')
        else:
            total_objs = 0
            for prim_obj, tmp in self.xobjects:
                if self.obj_values[prim_obj].active_obj:
                    total_objs += self.obj_values[prim_obj].quant_id
            self.set_total(total_objs)

        # Update database
        self.dbstate.disable_signals()
        for prim_obj, prim_objs in self.xobjects:
            with DbTxn(_('Reorder %s IDs ...') % prim_obj, self.dbstate, batch=True) \
            as self.trans:
                if self.obj_values[prim_obj].active_obj:
                    if self.uistate:
                        self.progress.set_pass(_('Reorder %s IDs ...') % \
                                               _(prim_objs.title()), \
                                               self.obj_values[prim_obj].quant_id)
                    # Process reordering
                    self._reorder(prim_obj)

        self.dbstate.enable_signals()
        self.dbstate.request_rebuild()

        # Update progress calculation
        if self.uistate:
            self.progress.close()
        else:
            print('\nDone.')

    # finds integer portion in a GrampsID
    _findint = re.compile('^[^\d]*(\d+)[^\d]*')
    def _reorder(self, prim_obj):
        """ reorders all selected objects with a (new) style, start & step """

        dup_ids = []   # list of duplicate identifiers
        new_ids = {}   # list of new identifiers

        class_type, table, commit, get_from_id, get_from_handle, next_from_id = \
            self.obj_methods[prim_obj]

        prefix_fmt = self.obj_values[prim_obj].get_fmt()
        prefix = prefix_fmt.split('%', 1)[0]
        new_id = self.obj_values[prim_obj].get_id()
        keep_fmt = self.obj_values[prim_obj].get_keep()
        change = self.obj_values[prim_obj].get_change()

        formatmatch = _parseformat.match(prefix_fmt)
        index_max = int("9" * int(formatmatch.groups()[0]))

        for handle in list(table.keys()):
            # Update progress
            if self.uistate:
                self.progress.step()
            else:
                self.update()

            # extract basic data out of the database
            table_data = table[handle]
            obj = class_type()
            obj.unserialize(table_data)

            act_id = obj.get_gramps_id()
            if change:
                # update the defined ID numbers into objects under consideration
                # of keeping ID if format not matches prefix
                # (implication logical boolean operator below)
                if act_id.startswith(prefix) or not keep_fmt:
                    obj.set_gramps_id(new_id)
                    commit(obj, self.trans)
                    new_id = self.obj_values[prim_obj].succ_id()
            else:
                # attempt to extract integer - if we can't, treat it as a duplicate
                try:
                    match = _findint.match(act_id)
                    if match:
                        # get the integer, build the new handle. Make sure it
                        # hasn't already been chosen. If it has, put this
                        # in the duplicate handle list

                        index = int(match.groups()[0])
                        if formatmatch:
                            if index > index_max:
                                new_id = next_from_id()
                            else:
                                new_id = prefix_fmt % index
                        else:
                            # prefix_fmt does not contain a number after %, eg I%d
                            new_id = prefix_fmt % index

                        if new_id == act_id:
                            if new_id in new_ids:
                                dup_ids.append(obj.get_handle())
                            else:
                                new_ids[new_id] = act_id
                        elif get_from_id(new_id) is not None:
                            dup_ids.append(obj.get_handle())
                        else:
                            obj.set_id(new_id)
                            commit(obj, self.trans)
                            new_ids[new_id] = act_id
                    else:
                        dup_ids.append(handle)
                except:
                    dup_ids.append(handle)

        # go through the duplicates, looking for the first available
        # handle that matches the new scheme.
        if dup_ids:
            if self.uistate:
                self.progress.set_pass(_('Finding and assigning unused IDs.'), len(dup_ids))
            for handle in dup_ids:
                obj = get_from_handle(handle)
                obj.set_gramps_id(next_from_id())
                commit(obj, self.trans)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class ReorderIdsOptions(tool.ToolOptions):
    """ Defines options and provides handling interface. """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
