#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import const
import Spell
import Config
from _EditPrimary import EditPrimary
from MarkupText import EditorBuffer
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class EditNote(EditPrimary):

    def __init__(self, state, uistate, track, note, callback=None):
        """
        Creates an EditPerson window.  Associates a person with the window.
        """
        EditPrimary.__init__(self, state, uistate, track, note, 
                             state.db.get_note_from_handle, callback)

    def empty_object(self):
        """
        Returns an empty Person object for comparison for changes. This
        is used by the base class (EditPrimary)
        """
        return RelLib.Note()

    def get_menu_title(self):
	if self.obj.get_handle():
	    title = _('Note') + ': %s' % self.obj.get_gramps_id()
	else:
	    title = _('New Note')
        return title

    def _local_init(self):
        """
        Local initialization function. Performs basic initialization,
        including setting up widgets and the glade interface. This is called
        by the base class of EditPrimary, and overridden here.
        """
        self.top = gtk.glade.XML(const.gladeFile, "edit_note", "gramps")
        win = self.top.get_widget("edit_note")
        self.set_window(win, None, self.get_menu_title())

        width = Config.get(Config.NOTE_WIDTH)
        height = Config.get(Config.NOTE_HEIGHT)
        self.window.set_default_size(width, height)

        self.type = self.top.get_widget('type')
        self.format = self.top.get_widget('format')

        container = self.top.get_widget('container')
        container.pack_start(self.build_interface())
        container.show_all()

    def _setup_fields(self):

        self.type_selector = MonitoredDataType(
            self.top.get_widget("type"),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly)

        self.check = MonitoredCheckbox(
            self.obj,
            self.format,
            self.obj.set_format,
            self.obj.get_format,
            readonly = self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_widget('id'),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        self.marker = MonitoredDataType(
            self.top.get_widget('marker'), 
            self.obj.set_marker, 
            self.obj.get_marker, 
            self.db.readonly,
            self.db.get_marker_types())
        
    def _connect_signals(self):
        """
        Connects any signals that need to be connected. Called by the
        init routine of the base class (_EditPrimary).
        """
        self.define_ok_button(self.top.get_widget('ok'),self.save)
        self.define_cancel_button(self.top.get_widget('cancel'))

    def build_interface(self):
        BUTTON = [(_('Italic'),gtk.STOCK_ITALIC,'<i>i</i>','<Control>I'),
                  (_('Bold'),gtk.STOCK_BOLD,'<b>b</b>','<Control>B'),
                  (_('Underline'),gtk.STOCK_UNDERLINE,'<u>u</u>','<Control>U'),
                  #('Separator', None, None, None),
              ]

        vbox = gtk.VBox()

        self.text = gtk.TextView()
        self.text.set_accepts_tab(True)

        if self.obj and self.obj.get_format():
            self.format.set_active(True)
            self.text.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.format.set_active(False)
            self.text.set_wrap_mode(gtk.WRAP_WORD)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.text)

        self.buf = EditorBuffer()
        self.text.set_buffer(self.buf)

        if self.obj:
            self.empty = False
            self.buf.set_text(self.obj.get(markup=True))
        else:
            self.empty = True

        if not self.dbstate.db.readonly:
            self.accelerator = {}
            hbox = gtk.HBox()
            hbox.set_spacing(0)
            hbox.set_border_width(0)
            vbox.pack_start(hbox, False)

            tooltips = gtk.Tooltips()
            for tip, stock, markup, accel in BUTTON:
                if markup:
                    button = gtk.ToggleButton()
                    image = gtk.Image()
                    image.set_from_stock(stock, gtk.ICON_SIZE_MENU)
                    button.set_image(image)
                    button.set_relief(gtk.RELIEF_NONE)
                    tooltips.set_tip(button, tip)
                    self.buf.setup_widget_from_xml(button, markup)
                    key, mod = gtk.accelerator_parse(accel)
                    self.accelerator[(key, mod)] = button
                    hbox.pack_start(button, False)
                else:
                    hbox.pack_start(gtk.VSeparator(), False)

        vbox.pack_start(scroll, True)
        vbox.set_spacing(6)
        vbox.set_border_width(6)

        if self.dbstate.db.readonly:
            self.text.set_editable(False)
            return vbox

        # Accelerator dictionary used for formatting shortcuts
        #  key: tuple(key, modifier)
        #  value: widget, to emit 'activate' signal on
        self.text.connect('key-press-event', self._on_key_press_event)

        self.spellcheck = Spell.Spell(self.text)

        self.format.connect('toggled', self.flow_changed)

        self.buf.connect('changed', self.update)
        self.buf.connect_after('apply-tag', self.update)
        self.buf.connect_after('remove-tag', self.update)
        #self.rebuild()
        return vbox

    def _on_key_press_event(self, widget, event):
        #log.debug("Key %s (%d) was pressed on %s" %
        #(gtk.gdk.keyval_name(event.keyval), event.keyval, widget))
        key = event.keyval
        mod = event.state
        if self.accelerator.has_key((key, mod)):
            self.accelerator[(key, mod)].emit('activate')
            return True

    def update(self, obj, *args):
        if self.obj:
            start = self.buf.get_start_iter()
            stop = self.buf.get_end_iter()
            text = self.buf.get_text(start, stop)
            self.obj.set(text)
        else:
            print "NOTE OBJ DOES NOT EXIST"
        return False

    def flow_changed(self, obj):
        if obj.get_active():
            self.text.set_wrap_mode(gtk.WRAP_NONE)
            self.obj.set_format(True)
        else:
            self.text.set_wrap_mode(gtk.WRAP_WORD)
            self.obj.set_format(False)

    def save(self, *obj):
        """
        Save the data.
        """
        trans = self.db.transaction_begin()
        if self.obj.get_handle():
            self.db.commit_note(self.obj,trans)
        else:
            self.db.add_note(self.obj,trans)
        self.db.transaction_commit(trans, _("Edit Note"))
        
        if self.callback:
            self.callback(self.obj)
        self.close()

    def _cleanup_on_exit(self):
        (width, height) = self.window.get_size()
        Config.set(Config.NOTE_WIDTH, width)
        Config.set(Config.NOTE_HEIGHT, height)
        Config.sync()
