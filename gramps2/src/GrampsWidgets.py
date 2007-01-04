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

import cgi
import os
import cPickle as pickle
from gettext import gettext as _
import string

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import pango

import AutoComp
import DateHandler
import DateEdit
import const
import Errors
import Config

from DdTargets import DdTargets

_lock_path = os.path.join(const.image_dir, 'stock_lock.png')
_lock_open_path = os.path.join(const.image_dir, 'stock_lock-open.png')

hand_cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
def realize_cb(widget):
    widget.window.set_cursor(hand_cursor)

class LinkLabel(gtk.EventBox):

    def __init__(self, label, func, handle):
        gtk.EventBox.__init__(self)
        self.orig_text = cgi.escape(label[0])
        self.gender = label[1]
        self.tooltips = gtk.Tooltips()
        text = '<span underline="single">%s</span>' % self.orig_text

        msg = _('Click to make the active person\n'
                'Right click to display the edit menu')
        if not Config.get(Config.RELEDITBTN):
            msg += "\n" + _('Edit icons can be enabled in the Preferences dialog')

        self.tooltips.set_tip(self, msg)
        
        self.label = gtk.Label(text)
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)

        hbox = gtk.HBox()
        hbox.pack_start(self.label, False, False, 0)
        if label[1]:
            hbox.pack_start(GenderLabel(label[1]), False, False, 4)
        self.add(hbox)
        
        self.connect('button-press-event', func, handle)
        self.connect('enter-notify-event', self.enter_text, handle)
        self.connect('leave-notify-event', self.leave_text, handle)
        self.connect('realize', realize_cb)

    def set_padding(self, x, y):
        self.label.set_padding(x, y)
        
    def enter_text(self, obj, event, handle):
        text = '<span foreground="blue" underline="single">%s</span>' % self.orig_text
        self.label.set_text(text)
        self.label.set_use_markup(True)

    def leave_text(self, obj, event, handle):
        text = '<span underline="single">%s</span>' % self.orig_text
        self.label.set_text(text)
        self.label.set_use_markup(True)

class IconButton(gtk.Button):

    def __init__(self, func, handle, icon=gtk.STOCK_EDIT,
                 size=gtk.ICON_SIZE_MENU):
        gtk.Button.__init__(self)
        image = gtk.Image()
        image.set_from_stock(icon, size)
        image.show()
        self.add(image)
        self.set_relief(gtk.RELIEF_NONE)
        self.show()

        if func:
            self.connect('button-press-event', func, handle)

class WarnButton(gtk.Button):
    def __init__(self):
        gtk.Button.__init__(self)
        image = gtk.Image()

        # Some versions of FreeBSD don't seem to have STOCK_INFO
        try:
            image.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        except:
            image.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_MENU)
            
        image.show()
        self.add(image)
        self.set_relief(gtk.RELIEF_NONE)
        self.show()
        self.func = None
        self.hide()

    def on_clicked(self, func):
        self.connect('button-press-event', self._button_press)
        self.func = func

    def _button_press(self, obj, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.func(obj)

class SimpleButton(gtk.Button):

    def __init__(self, image, func):
        gtk.Button.__init__(self)
        self.set_relief(gtk.RELIEF_NONE)
        self.add(gtk.image_new_from_stock(image, gtk.ICON_SIZE_BUTTON))
        self.connect('clicked', func)
        self.show()
        
class LinkBox(gtk.HBox):

    def __init__(self, link, button):
        gtk.HBox.__init__(self)
        self.set_spacing(6)
        self.pack_start(link, False)
        if button:
            self.pack_start(button, False)
        self.show()

class EditLabel(gtk.HBox):
    def __init__(self, text):
        gtk.HBox.__init__(self)
        label = BasicLabel(text)
        self.pack_start(label, False)
        self.pack_start(gtk.image_new_from_stock(gtk.STOCK_EDIT, 
                                                 gtk.ICON_SIZE_MENU), False)
        self.set_spacing(4)
        self.show_all()

class BasicLabel(gtk.Label):

    def __init__(self, text):
        gtk.Label.__init__(self, text)
        self.set_alignment(0, 0.5)
        self.show()

class GenderLabel(gtk.Label):

    def __init__(self, text):
        gtk.Label.__init__(self, text)
        self.set_alignment(0, 0.5)
        if os.sys.platform == "win32":
            pangoFont = pango.FontDescription('Arial')
            self.modify_font(pangoFont)
        self.show()

class MarkupLabel(gtk.Label):

    def __init__(self, text):
        gtk.Label.__init__(self, text)
        self.set_alignment(0, 0.5)
        self.set_use_markup(True)
        self.show_all()

class DualMarkupLabel(gtk.HBox):

    def __init__(self, text, alt):
        gtk.HBox.__init__(self)
        label = gtk.Label(text)
        label.set_alignment(0, 0.5)
        label.set_use_markup(True)

        self.pack_start(label, False, False, 0)
        b = GenderLabel(alt)
        b.set_use_markup(True)
        self.pack_start(b, False, False, 4)
        self.show()
        
class IntEdit(gtk.Entry):
    """An gtk.Edit widget that only allows integers."""
    
    def __init__(self):
        gtk.Entry.__init__(self)

        self._signal = self.connect("insert_text", self.insert_cb)

    def insert_cb(self, widget, text, length, *args):        
        # if you don't do this, garbage comes in with text
        text = text[:length]
        pos = widget.get_position()
        # stop default emission
        widget.emit_stop_by_name("insert_text")
        gobject.idle_add(self.insert, widget, text, pos)

    def insert(self, widget, text, pos):
        if len(text) > 0 and text.isdigit():            
            # the next three lines set up the text. this is done because we
            # can't use insert_text(): it always inserts at position zero.
            orig_text = widget.get_text()            
            new_text = orig_text[:pos] + text + orig_text[pos:]
            # avoid recursive calls triggered by set_text
            widget.handler_block(self._signal)
            # replace the text with some new text
            widget.set_text(new_text)
            widget.handler_unblock(self._signal)
            # set the correct position in the widget
            widget.set_position(pos + len(text))

class TypeCellRenderer(gtk.CellRendererCombo):

    def __init__(self, values):
        gtk.CellRendererCombo.__init__(self)

        model = gtk.ListStore(str, int)
        for key in values:
            model.append(row=[values[key], key])
        self.set_property('editable', True)
        self.set_property('model', model)
        self.set_property('text-column', 0)

class PrivacyButton:

    def __init__(self, button, obj, readonly=False):
        self.button = button
        self.button.connect('toggled', self._on_toggle)
        self.tooltips = gtk.Tooltips()
        self.obj = obj
        self.set_active(obj.get_privacy())
        self.button.set_sensitive(not readonly)

    def set_sensitive(self, val):
        self.button.set_sensitive(val)

    def set_active(self, val):
        self.button.set_active(val)
        self._on_toggle(self.button)

    def get_active(self):
        return self.button.get_active()

    def _on_toggle(self, obj):
        child = obj.child
        if child:
            obj.remove(child)
        image = gtk.Image()
        if obj.get_active():
#            image.set_from_icon_name('stock_lock', gtk.ICON_SIZE_MENU)
            image.set_from_file(_lock_path)
            self.tooltips.set_tip(obj, _('Record is private'))
            self.obj.set_privacy(True)
        else:
#            image.set_from_icon_name('stock_lock-open', gtk.ICON_SIZE_MENU)
            image.set_from_file(_lock_open_path)
            self.tooltips.set_tip(obj, _('Record is public'))
            self.obj.set_privacy(False)
        image.show()
        obj.add(image)

class MonitoredCheckbox:

    def __init__(self, obj, button, set_val, get_val, on_toggle=None):
        self.button = button
        self.button.connect('toggled', self._on_toggle)
        self.on_toggle = on_toggle
        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.obj.set_active(get_val())

    def _on_toggle(self, obj):
        self.set_val(obj.get_active())
        if self.on_toggle:
            self.on_toggle(self.get_val())
        
class MonitoredEntry:

    def __init__(self, obj, set_val, get_val, read_only=False,
                 autolist=None, changed=None):
        self.obj = obj
        self.set_val = set_val
        self.get_val = get_val
        self.changed = changed

        if get_val():
            self.obj.set_text(get_val())
        self.obj.connect('changed', self._on_change)
        self.obj.set_editable(not read_only)

        if autolist:
            AutoComp.fill_entry(obj,autolist)

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def set_text(self, text):
        self.obj.set_text(text)
        
    def connect(self, signal, callback):
        self.obj.connect(signal, callback)

    def _on_change(self, obj):
        self.set_val(unicode(obj.get_text()))
        if self.changed:
            self.changed(obj)

    def force_value(self, value):
        self.obj.set_text(value)

    def get_value(self, value):
        return unicode(self.obj.get_text())

    def enable(self, value):
        self.obj.set_sensitive(value)
        self.obj.set_editable(value)

    def grab_focus(self):
        self.obj.grab_focus()

    def update(self):
        if self.get_val():
            self.obj.set_text(self.get_val())

class MonitoredText:

    def __init__(self, obj, set_val, get_val, read_only=False):
        self.buf = obj.get_buffer()
        self.set_val = set_val
        self.get_val = get_val

        if get_val():
            self.buf.set_text(get_val())
        self.buf.connect('changed', self.on_change)
        obj.set_editable(not read_only)

    def on_change(self, obj):
        s, e = self.buf.get_bounds()
        self.set_val(unicode(self.buf.get_text(s, e, False)))

class MonitoredType:

    def __init__(self, obj, set_val, get_val, mapping, custom, readonly=False,
                 custom_values=None):
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj

        val = get_val()
        if val:
            default = val[0]
        else:
            default = None

        self.sel = AutoComp.StandardCustomSelector(
            mapping, obj, custom, default, additional=custom_values)

        self.set_val(self.sel.get_values())
        self.obj.set_sensitive(not readonly)
        self.obj.connect('changed', self.on_change)

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def update(self):
        if self.get_val():
            self.sel.set_values(self.get_val())

    def on_change(self, obj):
        self.set_val(self.sel.get_values())

class MonitoredDataType:

    def __init__(self, obj, set_val, get_val, readonly=False,
                 custom_values=None):
        
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj

        val = get_val()

        if val:
            default = int(val)
        else:
            default = None

        self.sel = AutoComp.StandardCustomSelector(
            get_val().get_map(),
            obj,
            get_val().get_custom(),
            default,
            additional=custom_values)

        self.sel.set_values((int(get_val()),str(get_val())))
        self.obj.set_sensitive(not readonly)
        self.obj.connect('changed', self.on_change)

    def reinit(self, set_val, get_val):
        self.set_val = set_val
        self.get_val = get_val
        self.update()

    def fix_value(self, value):
        if value[0] == self.get_val().get_custom():
            return value
        else:
            return (value[0],'')

    def update(self):
        val = self.get_val()
        if type(val) == tuple :
            self.sel.set_values(val)
        else:
            self.sel.set_values((int(val),str(val)))

    def on_change(self, obj):
        value = self.fix_value(self.sel.get_values())
        self.set_val(value)

class MonitoredMenu:

    def __init__(self, obj, set_val, get_val, mapping,
                 readonly=False, changed=None):
        self.set_val = set_val
        self.get_val = get_val

        self.changed = changed
        self.obj = obj

        self.change_menu(mapping)
        self.obj.connect('changed', self.on_change)
        self.obj.set_sensitive(not readonly)

    def force(self, value):
        self.obj.set_active(value)

    def change_menu(self, mapping):
        self.data = {}
        self.model = gtk.ListStore(str, int)
        index = 0
        for t, v in mapping:
            self.model.append(row=[t, v])
            self.data[v] = index
            index += 1
        self.obj.set_model(self.model)
        self.obj.set_active(self.data.get(self.get_val(),0))

    def on_change(self, obj):
        self.set_val(self.model.get_value(obj.get_active_iter(), 1))
        if self.changed:
            self.changed()

class MonitoredStrMenu:

    def __init__(self, obj, set_val, get_val, mapping, readonly=False):
        self.set_val = set_val
        self.get_val = get_val

        self.obj = obj
        self.model = gtk.ListStore(str)
        
        if len(mapping) > 20:
            self.obj.set_wrap_width(3)

        self.model.append(row=[''])
        index = 0
        self.data = ['']

        default = get_val()
        active = 0
        
        for t, v in mapping:
            self.model.append(row=[v])
            self.data.append(t)
            index += 1
            if t == default:
                active = index
            
        self.obj.set_model(self.model)
        self.obj.set_active(active)
        self.obj.connect('changed', self.on_change)
        self.obj.set_sensitive(not readonly)

    def on_change(self, obj):
        self.set_val(self.data[obj.get_active()])

class MonitoredDate:

    def __init__(self, field, button, value, uistate, track, readonly=False):
        self.date = value
        self.date_check = DateEdit.DateEdit(
            self.date, field, button, uistate, track)
        field.set_editable(not readonly)
        button.set_sensitive(not readonly)
            
        field.set_text(DateHandler.displayer.display(self.date))

class PlaceEntry:
    """
    Handles the selection of a existing or new Place. Supports Drag and Drop
    to select a place.
    """
    def __init__(self, dbstate, uistate, track, obj, set_val,
                 get_val, add_del, share):
        
        self.obj = obj
        self.add_del = add_del
        self.share = share
        self.dbstate = dbstate
        self.db = dbstate.db
        self.get_val = get_val
        self.set_val = set_val
        self.uistate = uistate
        self.track = track
        self.tooltips = gtk.Tooltips()

        self.obj.drag_dest_set(gtk.DEST_DEFAULT_ALL, [DdTargets.PLACE_LINK.target()], 
                               gtk.gdk.ACTION_COPY)
        self.obj.connect('drag_data_received', self.drag_data_received)

        if get_val():
            self.set_button(True)
            p = self.db.get_place_from_handle(self.get_val())
            name = "%s [%s]" % (p.get_title(),p.gramps_id)
        else:
            name = u""
            self.set_button(False)

        if self.db.readonly:
            self.add_del.set_sensitive(False)
            self.share.set_sensitive(False)
        else:
            self.add_del.set_sensitive(True)
            self.share.set_sensitive(True)

        self.add_del.connect('clicked', self.add_del_clicked)
        self.share.connect('clicked', self.share_clicked)
        
        if not self.db.readonly and not name:
            obj.set_text("<i>%s</i>" % _('To select a place, use drag-and-drop or use the buttons'))
            obj.set_use_markup(True)
        else:
            obj.set_text(name)

    def after_edit(self, place):
        name = "%s [%s]" % (place.get_title(),place.gramps_id)
        self.obj.set_text(name)

    def add_del_clicked(self, obj):
        if self.get_val():
            self.set_val(None)
            self.obj.set_text(u'')
            self.set_button(False)
        else:
            from RelLib import Place
            from Editors import EditPlace

            place = Place()
            try:
                EditPlace(self.dbstate, self.uistate, self.track,
                          place, self.place_added)
            except Errors.WindowActiveError:
                pass

    def drag_data_received(self, widget, context, x, y, selection, info, time):
        (drag_type, idval, obj, val) = pickle.loads(selection.data)
        
        data = self.db.get_place_from_handle(obj)
        self.place_added(data)
        
    def place_added(self, data):
        self.set_val(data.handle)
        self.obj.set_text("%s [%s]" % (data.get_title(),data.gramps_id))
        self.set_button(True)

    def share_clicked(self, obj):
        if self.get_val():
            from Editors import EditPlace
            
            place = self.db.get_place_from_handle(self.get_val())
            try:
                EditPlace(self.dbstate, self.uistate, self.track, place,
                          self.after_edit)
            except Errors.WindowActiveError:
                pass
        else:
            from Selectors import selector_factory
            cls = selector_factory('Place')
            select = cls(self.dbstate, self.uistate, self.track)
            place = select.run()
            if place:
                self.place_added(place)

    def set_button(self, use_add):
        for i in self.add_del.get_children():
            self.add_del.remove(i)
        for i in self.share.get_children():
            self.share.remove(i)

        if use_add:
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_REMOVE,gtk.ICON_SIZE_BUTTON)
            image.show()
            self.add_del.add(image)
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_EDIT,gtk.ICON_SIZE_BUTTON)
            image.show()
            self.share.add(image)
            self.tooltips.set_tip(self.share, _('Edit place'))
            self.tooltips.set_tip(self.add_del, _('Remove place'))
        else:
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_BUTTON)
            image.show()
            self.add_del.add(image)
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_INDEX,gtk.ICON_SIZE_BUTTON)
            image.show()
            self.share.add(image)
            self.tooltips.set_tip(self.share, _('Select an existing place'))
            self.tooltips.set_tip(self.add_del, _('Add a new place'))

#============================================================================
#
# MaskedEntry and ValidatableMaskedEntry copied and merged from the Kiwi
# project's ValidatableProxyWidgetMixin, KiwiEntry and ProxyEntry.
#
# http://www.async.com.br/projects/kiwi
#
#============================================================================

class MaskError(Exception):
    pass

class ValidationError(Exception):
    pass

class FadeOut(gobject.GObject):
    """I am a helper class to draw the fading effect of the background
    Call my methods start() and stop() to control the fading.
    """
    __gsignals__ = {
        'done': (gobject.SIGNAL_RUN_FIRST,
                 gobject.TYPE_NONE,
                 ()),
        'color-changed': (gobject.SIGNAL_RUN_FIRST,
                          gobject.TYPE_NONE,
                          (gtk.gdk.Color,)),
    }
    
    # How long time it'll take before we start (in ms)
    COMPLAIN_DELAY = 500

    MERGE_COLORS_DELAY = 100

    ERROR_COLOR = "#ffd5d5"

    def __init__(self, widget):
        gobject.GObject.__init__(self)
        self._widget = widget
        self._start_color = None
        self._background_timeout_id = -1
        self._countdown_timeout_id = -1
        ##self._log = Logger('fade')
        self._done = False

    def _merge_colors(self, src_color, dst_color, steps=10):
        """
        Change the background of widget from src_color to dst_color
        in the number of steps specified
        """

        ##self._log.debug('_merge_colors: %s -> %s' % (src_color, dst_color))

        rs, gs, bs = src_color.red, src_color.green, src_color.blue
        rd, gd, bd = dst_color.red, dst_color.green, dst_color.blue
        rinc = (rd - rs) / float(steps)
        ginc = (gd - gs) / float(steps)
        binc = (bd - bs) / float(steps)
        for dummy in xrange(steps):
            rs += rinc
            gs += ginc
            bs += binc
            col = gtk.gdk.color_parse("#%02X%02X%02X" % (int(rs) >> 8,
                                                         int(gs) >> 8,
                                                         int(bs) >> 8))
            self.emit('color-changed', col)
            yield True

        self.emit('done')
        self._background_timeout_id = -1
        self._done = True
        yield False

    def _start_merging(self):
        # If we changed during the delay
        if self._background_timeout_id != -1:
            ##self._log.debug('_start_merging: Already running')
            return

        ##self._log.debug('_start_merging: Starting')
        func = self._merge_colors(self._start_color,
                                  gtk.gdk.color_parse(FadeOut.ERROR_COLOR)).next
        self._background_timeout_id = (
            gobject.timeout_add(FadeOut.MERGE_COLORS_DELAY, func))
        self._countdown_timeout_id = -1

    def start(self, color):
        """Schedules a start of the countdown.
        @param color: initial background color
        @returns: True if we could start, False if was already in progress
        """
        if self._background_timeout_id != -1:
            ##self._log.debug('start: Background change already running')
            return False
        if self._countdown_timeout_id != -1:
            ##self._log.debug('start: Countdown already running')
            return False
        if self._done:
            ##self._log.debug('start: Not running, already set')
            return False

        self._start_color = color
        ##self._log.debug('start: Scheduling')
        self._countdown_timeout_id = gobject.timeout_add(
            FadeOut.COMPLAIN_DELAY, self._start_merging)

        return True

    def stop(self):
        """Stops the fadeout and restores the background color"""
        ##self._log.debug('Stopping')
        if self._background_timeout_id != -1:
            gobject.source_remove(self._background_timeout_id)
            self._background_timeout_id = -1
        if self._countdown_timeout_id != -1:
            gobject.source_remove(self._countdown_timeout_id)
            self._countdown_timeout_id = -1

        self._widget.update_background(self._start_color)
        self._done = False

if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FadeOut)

class Tooltip(gtk.Window):
    '''Tooltip for the Icon in the MaskedEntry'''
    
    DEFAULT_DELAY = 500
    BORDER_WIDTH = 4

    def __init__(self, widget):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        # from gtktooltips.c:gtk_tooltips_force_window
        self.set_app_paintable(True)
        self.set_resizable(False)
        self.set_name("gtk-tooltips")
        self.set_border_width(Tooltip.BORDER_WIDTH)
        self.connect('expose-event', self._on__expose_event)

        self._label = gtk.Label()
        self.add(self._label)
        self._show_timeout_id = -1

    # from gtktooltips.c:gtk_tooltips_draw_tips
    def _calculate_pos(self, widget):
        screen = widget.get_screen()

        w, h = self.size_request()

        x, y = widget.window.get_origin()

        if widget.flags() & gtk.NO_WINDOW:
            x += widget.allocation.x
            y += widget.allocation.y

        x = screen.get_root_window().get_pointer()[0]
        x -= (w / 2 + Tooltip.BORDER_WIDTH)

        pointer_screen, px, py, _ = screen.get_display().get_pointer()
        if pointer_screen != screen:
            px = x
            py = y

        monitor_num = screen.get_monitor_at_point(px, py)
        monitor = screen.get_monitor_geometry(monitor_num)

        if (x + w) > monitor.x + monitor.width:
            x -= (x + w) - (monitor.x + monitor.width);
        elif x < monitor.x:
            x = monitor.x

        if ((y + h + widget.allocation.height + Tooltip.BORDER_WIDTH) >
            monitor.y + monitor.height):
            y = y - h - Tooltip.BORDER_WIDTH
        else:
            y = y + widget.allocation.height + Tooltip.BORDER_WIDTH

        return x, y

    # from gtktooltips.c:gtk_tooltips_paint_window
    def _on__expose_event(self, window, event):
        w, h = window.size_request()
        window.style.paint_flat_box(window.window,
                                    gtk.STATE_NORMAL, gtk.SHADOW_OUT,
                                    None, window, "tooltip",
                                    0, 0, w, h)
        return False

    def _real_display(self, widget):
        x, y = self._calculate_pos(widget)

        self.move(x, y)
        self.show_all()

    # Public API

    def set_text(self, text):
        self._label.set_text(text)

    def hide(self):
        gtk.Window.hide(self)
        gobject.source_remove(self._show_timeout_id)
        self._show_timeout_id = -1

    def display(self, widget):
        if not self._label.get_text():
            return

        if self._show_timeout_id != -1:
            return

        self._show_timeout_id = gobject.timeout_add(Tooltip.DEFAULT_DELAY,
                                                    self._real_display,
                                                    widget)

# This is tricky and contains quite a few hacks:
# An entry contains 2 GdkWindows, one for the background and one for
# the text area. The normal one, on which the (normally white) background
# is drawn can be accessed through entry.window (after realization)
# The other window is the one where the cursor and the text is drawn upon,
# it's refered to as "text area" inside the GtkEntry code and it is called
# the same here. It can only be accessed through window.get_children()[0],
# since it's considered private to the entry.
#
# +-------------------------------------+
# |                 (1)                 |  (1) parent widget (grey)
# |+----------------(2)----------------+|
# || |-- /-\  |                        ||  (2) entry.window (white)
# || |-  | |  |(4)  (3)                ||
# || |   \-/  |                        ||  (3) text area (transparent)
# |+-----------------------------------+|
# |-------------------------------------|  (4) cursor, black
# |                                     |
# +-------------------------------------|
#
# So, now we want to put an icon in the edge:
# An earlier approached by Lorzeno drew the icon directly on the text area,
# which is not desired since if the text is using the whole width of the
# entry the icon will be drawn on top of the text.
# Now what we want to do is to resize the text area and create a
# new window upon which we can draw the icon.
#
# +-------------------------------------+
# |                                     |  (5) icon window
# |+----------------------------++-----+|
# || |-- /-\  |                 ||     ||
# || |-  | |  |                 || (5) ||
# || |   \-/  |                 ||     ||
# |+----------------------------++-----+|
# |-------------------------------------|
# |                                     |
# +-------------------------------------+
#
# When resizing the text area the cursor and text is not moved into the
# correct position, it'll still be off by the width of the icon window
# To fix this we need to call a private function, gtk_entry_recompute,
# a workaround is to call set_visiblity() which calls recompute()
# internally.
#

class IconEntry(object):
    """
    Helper object for rendering an icon in a GtkEntry
    """

    def __init__(self, entry):
        if not isinstance(entry, gtk.Entry):
            raise TypeError("entry must be a gtk.Entry")
        self._constructed = False
        self._pixbuf = None
        self._pixw = 1
        self._pixh = 1
        self._text_area = None
        self._text_area_pos = (0, 0)
        self._icon_win = None
        self._entry = entry
        self._tooltip = Tooltip(self)
        entry.connect('enter-notify-event',
                      self._on_entry__enter_notify_event)
        entry.connect('leave-notify-event',
                      self._on_entry__leave_notify_event)
        entry.connect('notify::xalign',
                      self._on_entry__notify_xalign)
        self._update_position()

    def _on_entry__notify_xalign(self, entry, pspec):
        self._update_position()

    def _on_entry__enter_notify_event(self, entry, event):
        icon_win = self.get_icon_window()
        if event.window != icon_win:
            return

        self._tooltip.display(entry)

    def _on_entry__leave_notify_event(self, entry, event):
        if event.window != self.get_icon_window():
            return

        self._tooltip.hide()

    def set_tooltip(self, text):
        self._tooltip.set_text(text)

    def get_icon_window(self):
        return self._icon_win

    def set_pixbuf(self, pixbuf):
        """
        @param pixbuf: a gdk.Pixbuf or None
        """
        entry = self._entry
        if not isinstance(entry.get_toplevel(), gtk.Window):
            # For widgets in SlaveViews, wait until they're attached
            # to something visible, then set the pixbuf
            entry.connect_object('realize', self.set_pixbuf, pixbuf)
            return

        if pixbuf:
            if not isinstance(pixbuf, gtk.gdk.Pixbuf):
                raise TypeError("pixbuf must be a GdkPixbuf")
        else:
            # Turning of the icon should also restore the background
            entry.modify_base(gtk.STATE_NORMAL, None)
            if not self._pixbuf:
                return
        self._pixbuf = pixbuf

        if pixbuf:
            self._pixw = pixbuf.get_width()
            self._pixh = pixbuf.get_height()
        else:
            self._pixw = self._pixh = 0

        win = self._icon_win
        if not win:
            self.construct()
            win = self._icon_win

        self.resize_windows()

        # XXX: Why?
        if win:
            if not pixbuf:
                win.hide()
            else:
                win.show()

        # Hack: This triggers a .recompute() which is private
        entry.set_visibility(entry.get_visibility())
        entry.queue_draw()

    def construct(self):
        if self._constructed:
            return

        entry = self._entry
        if not entry.flags() & gtk.REALIZED:
            entry.realize()

        # Hack: Save a reference to the text area, now when its created
        self._text_area = entry.window.get_children()[0]
        self._text_area_pos = self._text_area.get_position()

        # PyGTK should allow default values for most of the values here.
        win = gtk.gdk.Window(entry.window,
                             self._pixw, self._pixh,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'icon window',
                             0, 0,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gtk.gdk.LEFT_PTR),
                             '', '', True)
        self._icon_win = win
        win.set_user_data(entry)
        win.set_background(entry.style.base[entry.state])
        self._constructed = True

    def deconstruct(self):
        if self._icon_win:
            # This is broken on PyGTK 2.6.x
            try:
                self._icon_win.set_user_data(None)
            except:
                pass
            # Destroy not needed, called by the GC.
            self._icon_win = None

    def update_background(self, color):
        if not self._icon_win:
            return

        self._entry.modify_base(gtk.STATE_NORMAL, color)

        self.draw_pixbuf()

    def get_background(self):
        return self._entry.style.base[gtk.STATE_NORMAL]

    def resize_windows(self):
        if not self._pixbuf:
            return

        icony = iconx = 4

        # Make space for the icon, both windows
        winw = self._entry.window.get_size()[0]
        textw, texth = self._text_area.get_size()
        textw = winw - self._pixw - (iconx + icony)

        if self._pos == gtk.POS_LEFT:
            textx, texty = self._text_area_pos
            textx += iconx + self._pixw

            # FIXME: Why is this needed. Focus padding?
            #        The text jumps without this
            textw -= 2
            self._text_area.move_resize(textx, texty, textw, texth)
        elif self._pos == gtk.POS_RIGHT:
            self._text_area.resize(textw, texth)
            iconx += textw

        icon_win = self._icon_win
        # XXX: Why?
        if not icon_win:
            return

        # If the size of the window is large enough, resize and move it
        # Otherwise just move it to the right side of the entry
        if icon_win.get_size() != (self._pixw, self._pixh):
            icon_win.move_resize(iconx, icony, self._pixw, self._pixh)
        else:
            icon_win.move(iconx, icony)

    def draw_pixbuf(self):
        if not self._pixbuf:
            return

        win = self._icon_win
        # XXX: Why?
        if not win:
            return

        # Draw background first
        color = self._entry.style.base_gc[self._entry.state]
        win.draw_rectangle(color, True,
                           0, 0, self._pixw, self._pixh)

        # If sensitive draw the icon, regardless of the window emitting the
        # event since makes it a bit smoother on resize
        if self._entry.flags() & gtk.SENSITIVE:
            win.draw_pixbuf(None, self._pixbuf, 0, 0, 0, 0,
                            self._pixw, self._pixh)

    def _update_position(self):
        if self._entry.get_property('xalign') > 0.5:
            self._pos = gtk.POS_LEFT
        else:
            self._pos = gtk.POS_RIGHT

HAVE_2_6 = gtk.pygtk_version[:2] == (2, 6)

(DIRECTION_LEFT, DIRECTION_RIGHT) = (1, -1)

(INPUT_ASCII_LETTER,
 INPUT_ALPHA,
 INPUT_ALPHANUMERIC,
 INPUT_DIGIT) = range(4)

INPUT_FORMATS = {
    '0': INPUT_DIGIT,
    'L': INPUT_ASCII_LETTER,
    'A': INPUT_ALPHANUMERIC,
    'a': INPUT_ALPHANUMERIC,
    '&': INPUT_ALPHA,
    }

# Todo list: Other usefull Masks
#  9 - Digit, optional
#  ? - Ascii letter, optional
#  C - Alpha, optional

INPUT_CHAR_MAP = {
    INPUT_ASCII_LETTER:     lambda text: text in string.ascii_letters,
    INPUT_ALPHA:            unicode.isalpha,
    INPUT_ALPHANUMERIC:     unicode.isalnum,
    INPUT_DIGIT:            unicode.isdigit,
    }

(COL_TEXT,
 COL_OBJECT) = range(2)

class MaskedEntry(gtk.Entry):
    """
    The MaskedEntry is a Entry subclass with the following additions:

      - Mask, force the input to meet certain requirements
      - IconEntry, allows you to have an icon inside the entry
    """
    __gtype_name__ = 'MaskedEntry'

    def __init__(self):
        gtk.Entry.__init__(self)

        self.connect('insert-text', self._on_insert_text)
        self.connect('delete-text', self._on_delete_text)
        self.connect_after('grab-focus', self._after_grab_focus)

        self.connect('changed', self._on_changed)

        self.connect('focus', self._on_focus)
        self.connect('focus-out-event', self._on_focus_out_event)
        self.connect('move-cursor', self._on_move_cursor)
        self.connect('button-press-event', self._on_button_press_event)
        self.connect('notify::cursor-position',
                     self._on_notify_cursor_position)

        self._completion = None
        self._exact_completion = False
        self._block_changed = False
        self._icon = IconEntry(self)

        # List of validators
        #  str -> static characters
        #  int -> dynamic, according to constants above
        self._mask_validators = []
        self._mask = None
        # Fields defined by mask
        # each item is a tuble, containing the begining and the end of the
        # field in the text
        self._mask_fields = []
        self._current_field = -1
        self._pos = 0
        self._selecting = False

        self._block_insert = False
        self._block_delete = False

    # Virtual methods
    # PyGTK 2.6 does not support the virtual method do_size_allocate so
    # we have to use the signal instead
    # PyGTK 2.9.0 and later (bug #327715) does not work using the old code,
    # so we have to make this conditionally
    if HAVE_2_6:
        gsignal('size-allocate', 'override')
        def do_size_allocate(self, allocation):
            self.chain(allocation)

            if self.flags() & gtk.REALIZED:
                self._icon.resize_windows()
    else:
        def do_size_allocate(self, allocation):
            gtk.Entry.do_size_allocate(self, allocation)

            if self.flags() & gtk.REALIZED:
                self._icon.resize_windows()

    def do_expose_event(self, event):
        gtk.Entry.do_expose_event(self, event)

        if event.window == self.window:
            self._icon.draw_pixbuf()

    def do_realize(self):
        gtk.Entry.do_realize(self)
        self._icon.construct()

    def do_unrealize(self):
        self._icon.deconstruct()
        gtk.Entry.do_unrealize(self)

    # Mask & Fields

    def set_mask(self, mask):
        """
        Sets the mask of the Entry.
        Supported format characters are:
          - '0' digit
          - 'L' ascii letter (a-z and A-Z)
          - '&' alphabet, honors the locale
          - 'a' alphanumeric, honors the locale
          - 'A' alphanumeric, honors the locale

        This is similar to MaskedTextBox: 
        U{http://msdn2.microsoft.com/en-us/library/system.windows.forms.maskedtextbox.mask(VS.80).aspx}

        Example mask for a ISO-8601 date
        >>> entry.set_mask('0000-00-00')

        @param mask: the mask to set
        """

        if not mask:
            self.modify_font(pango.FontDescription("sans"))
            self._mask = mask
            return

        # First, reset
        self._mask_validators = []
        self._mask_fields = []
        self._current_field = -1

        mask = unicode(mask)
        input_length = len(mask)
        lenght = 0
        pos = 0
        field_begin = 0
        field_end = 0
        while True:
            if pos >= input_length:
                break
            if mask[pos] in INPUT_FORMATS:
                self._mask_validators += [INPUT_FORMATS[mask[pos]]]
                field_end += 1
            else:
                self._mask_validators.append(mask[pos])
                if field_begin != field_end:
                    self._mask_fields.append((field_begin, field_end))
                field_end += 1
                field_begin = field_end
            pos += 1

        self._mask_fields.append((field_begin, field_end))
        self.modify_font(pango.FontDescription("monospace"))

        self._really_delete_text(0, -1)
        self._insert_mask(0, input_length)
        self._mask = mask

    def get_mask(self):
        """
        @returns: the mask
        """
        return self._mask

    def get_field_text(self, field):
        if not self._mask:
            raise MaskError("a mask must be set before calling get_field_text")
        #assert self._mask
        text = self.get_text()
        start, end = self._mask_fields[field]
        return text[start: end].strip()

    def get_fields(self):
        """
        Get the fields assosiated with the entry.
        A field is dynamic content separated by static.
        For example, the format string 000-000 has two fields
        separated by a dash.
        if a field is empty it'll return an empty string
        otherwise it'll include the content

        @returns: fields
        @rtype: list of strings
        """
        if not self._mask:
            raise MaskError("a mask must be set before calling get_fields")
        #assert self._mask

        fields = []

        text = unicode(self.get_text())
        for start, end in self._mask_fields:
            fields.append(text[start:end].strip())

        return fields

    def get_empty_mask(self, start=None, end=None):
        """
        Gets the empty mask between start and end

        @param start:
        @param end:
        @returns: mask
        @rtype: string
        """

        if start is None:
            start = 0
        if end is None:
            end = len(self._mask_validators)

        s = ''
        for validator in self._mask_validators[start:end]:
            if isinstance(validator, int):
                s += ' '
            elif isinstance(validator, unicode):
                s += validator
            else:
                raise AssertionError
        return s

    def get_field_pos(self, field):
        """
        Get the position at the specified field.
        """
        if field >= len(self._mask_fields):
            return None

        start, end = self._mask_fields[field]

        return start

    def _get_field_ideal_pos(self, field):
        start, end = self._mask_fields[field]
        text = self.get_field_text(field)
        pos = start+len(text)
        return pos

    def get_field(self):
        if self._current_field >= 0:
            return self._current_field
        else:
            return None

    def set_field(self, field, select=False):
        if field >= len(self._mask_fields):
            return

        pos = self._get_field_ideal_pos(field)
        self.set_position(pos)

        if select:
            field_text = self.get_field_text(field)
            start, end = self._mask_fields[field]
            self.select_region(start, pos)

        self._current_field = field

    def get_field_length(self, field):
        if 0 <= field < len(self._mask_fields):
            start, end = self._mask_fields[field]
            return end - start

    def _shift_text(self, start, end, direction=DIRECTION_LEFT,
                    positions=1):
        """
        Shift the text, to the right or left, n positions. Note that this
        does not change the entry text. It returns the shifted text.

        @param start:
        @param end:
        @param direction:   see L{kiwi.enums.Direction}
        @param positions:   the number of positions to shift.

        @return:        returns the text between start and end, shifted to
                        the direction provided.
        """
        text = self.get_text()
        new_text = ''
        validators = self._mask_validators

        if direction == DIRECTION_LEFT:
            i = start
        else:
            i = end - 1

        # When shifting a text, we wanna keep the static chars where they
        # are, and move the non-static chars to the right position.
        while start <= i < end:
            if isinstance(validators[i], int):
                # Non-static char shoud be here. Get the next one (depending
                # on the direction, and the number of positions to skip.)
                #
                # When shifting left, the next char will be on the right,
                # so, it will be appended, to the new text.
                # Otherwise, when shifting right, the char will be
                # prepended.
                next_pos = self._get_next_non_static_char_pos(i, direction,
                                                              positions-1)

                # If its outside the bounds of the region, ignore it.
                if not start <= next_pos <= end:
                    next_pos = None

                if next_pos is not None:
                    if direction == DIRECTION_LEFT:
                        new_text = new_text + text[next_pos]
                    else:
                        new_text = text[next_pos] + new_text
                else:
                    if direction == DIRECTION_LEFT:
                        new_text = new_text + ' '
                    else:
                        new_text = ' ' + new_text

            else:
                # Keep the static char where it is.
                if direction == DIRECTION_LEFT:
                   new_text = new_text + text[i]
                else:
                   new_text = text[i] + new_text
            i += direction

        return new_text

    def _get_next_non_static_char_pos(self, pos, direction=DIRECTION_LEFT,
                                      skip=0):
        """
        Get next non-static char position, skiping some chars, if necessary.
        @param skip:        skip first n chars
        @param direction:   direction of the search.
        """
        text = self.get_text()
        validators = self._mask_validators
        i = pos+direction+skip
        while 0 <= i < len(text):
            if isinstance(validators[i], int):
                return i
            i += direction

        return None

    def _get_field_at_pos(self, pos, dir=None):
        """
        Return the field index at position pos.
        """
        for p in self._mask_fields:
            if p[0] <= pos <= p[1]:
                return self._mask_fields.index(p)

        return None

    def set_exact_completion(self, value):
        """
        Enable exact entry completion.
        Exact means it needs to start with the value typed
        and the case needs to be correct.

        @param value: enable exact completion
        @type value:  boolean
        """

        if value:
            match_func = self._completion_exact_match_func
        else:
            match_func = self._completion_normal_match_func
        completion = self._get_completion()
        completion.set_match_func(match_func)

    def is_empty(self):
        text = self.get_text()
        if self._mask:
            empty = self.get_empty_mask()
        else:
            empty = ''

        return text == empty

    # Private

    def _really_delete_text(self, start, end):
        # A variant of delete_text() that never is blocked by us
        self._block_delete = True
        self.delete_text(start, end)
        self._block_delete = False

    def _really_insert_text(self, text, position):
        # A variant of insert_text() that never is blocked by us
        self._block_insert = True
        self.insert_text(text, position)
        self._block_insert = False

    def _insert_mask(self, start, end):
        text = self.get_empty_mask(start, end)
        self._really_insert_text(text, position=start)

    def _confirms_to_mask(self, position, text):
        validators = self._mask_validators
        if position < 0 or position >= len(validators):
            return False

        validator = validators[position]
        if isinstance(validator, int):
            if not INPUT_CHAR_MAP[validator](text):
                return False
        if isinstance(validator, unicode):
            if validator == text:
                return True
            return False

        return True

    def _get_completion(self):
        # Check so we have completion enabled, not this does not
        # depend on the property, the user can manually override it,
        # as long as there is a completion object set
        completion = self.get_completion()
        if completion:
            return completion

        completion = gtk.EntryCompletion()
        self.set_completion(completion)
        return completion

    def get_completion(self):
        return self._completion

    def set_completion(self, completion):
        gtk.Entry.set_completion(self, completion)
        # FIXME objects not supported yet, should it be at all?
        #completion.set_model(gtk.ListStore(str, object))
        completion.set_model(gtk.ListStore(str))
        completion.set_text_column(0)
        self._completion = gtk.Entry.get_completion(self)
        self.set_exact_completion(self._exact_completion)
        return

    def _completion_exact_match_func(self, completion, key, iter):
        model = completion.get_model()
        if not len(model):
            return

        content = model[iter][COL_TEXT]
        return key.startswith(content)

    def _completion_normal_match_func(self, completion, key, iter):
        model = completion.get_model()
        if not len(model):
            return

        content = model[iter][COL_TEXT].lower()
        return key.lower() in content

    def _appers_later(self, char, start):
        """
        Check if a char appers later on the mask. If it does, return
        the field it appers at. returns False otherwise.
        """
        validators = self._mask_validators
        i = start
        while i < len(validators):
            if self._mask_validators[i] == char:
                field = self._get_field_at_pos(i)
                if field is None:
                    return False

                return field

            i += 1

        return False

    def _can_insert_at_pos(self, new, pos):
        """
        Check if a chararcter can be inserted at some position

        @param new: The char that wants to be inserted.
        @param pos: The position where it wants to be inserted.

        @return: Returns None if it can be inserted. If it cannot be,
                 return the next position where it can be successfuly
                 inserted.
        """
        validators = self._mask_validators

        # Do not let insert if the field is full
        field = self._get_field_at_pos(pos)
        if field is not None:
            text = self.get_field_text(field)
            length = self.get_field_length(field)
            if len(text) == length:
                gtk.gdk.beep()
                return pos

        # If the char confirms to the mask, but is a static char, return the
        # position after that static char.
        if (self._confirms_to_mask(pos, new) and
            not isinstance(validators[pos], int)):
            return pos+1

        # If does not confirms to mask:
        #  - Check if the char the user just tried to enter appers later.
        #  - If it does, Jump to the start of the field after that
        if not self._confirms_to_mask(pos, new):
            field = self._appers_later(new, pos)
            if field is not False:
                pos = self.get_field_pos(field+1)
                if pos is not None:
                    gobject.idle_add(self.set_position, pos)
            return pos

        return None

#   When inserting new text, supose, the entry, at some time is like this,
#   ahd the user presses '0', for instance:
#   --------------------------------
#   | ( 1 2 )   3 4 5   - 6 7 8 9  |
#   --------------------------------
#              ^ ^     ^
#              S P     E
#
#   S - start of the field (start)
#   E - end of the field (end)
#   P - pos - where the new text is being inserted. (pos)
#
#   So, the new text will be:
#
#     the old text, from 0 until P
#   + the new text
#   + the old text, from P until the end of the field, shifted to the
#     right
#   + the old text, from the end of the field, to the end of the text.
#
#   After inserting, the text will be this:
#   --------------------------------
#   | ( 1 2 )   3 0 4 5 - 6 7 8 9  |
#   --------------------------------
#              ^   ^   ^
#              S   P   E
#

    def _insert_at_pos(self, text, new, pos):
        """
        Inserts the character at the give position in text. Note that the
        insertion won't be applied to the entry, but to the text provided.

        @param text:    Text that it will be inserted into.
        @param new:     New text to insert.
        @param pos:     Positon to insert at

        @return:    Returns a tuple, with the position after the insetion
                    and the new text.
        """
        field = self._get_field_at_pos(pos)
        length = len(new)
        new_pos = pos
        start, end = self._mask_fields[field]

        # Shift Right
        new_text = (text[:pos] + new +
                    self._shift_text(pos, end, DIRECTION_RIGHT)[1:] +
                    text[end:])

        # Overwrite Right
#        new_text = (text[:pos] + new +
#                    text[pos+length:end]+
#                    text[end:])
        new_pos = pos+1
        gobject.idle_add(self.set_position, new_pos)

        # If the field is full, jump to the next field
        if len(self.get_field_text(field)) == self.get_field_length(field)-1:
            gobject.idle_add(self.set_field, field+1, True)
            self.set_field(field+1)

        return new_pos, new_text

    # Callbacks
    def _on_insert_text(self, editable, new, length, position):
        if not self._mask or self._block_insert:
            return
        new = unicode(new)
        pos = self.get_position()

        self.stop_emission('insert-text')

        text = self.get_text()
        # Insert one char at a time
        for c in new:
            _pos = self._can_insert_at_pos(c, pos)
            if _pos is None:
                pos, text = self._insert_at_pos(text, c, pos)
            else:
                pos = _pos

        # Change the text with the new text.
        self._block_changed = True
        self._really_delete_text(0, -1)
        self._block_changed = False

        self._really_insert_text(text, 0)

#   When deleting some text, supose, the entry, at some time is like this:
#   --------------------------------
#   | ( 1 2 )   3 4 5 6 - 7 8 9 0  |
#   --------------------------------
#              ^ ^ ^   ^
#              S s e   E
#
#   S - start of the field (_start)
#   E - end of the field (_end)
#   s - start of the text being deleted (start)
#   e - end of the text being deleted (end)
#
#   end - start -> the number of characters being deleted.
#
#   So, the new text will be:
#
#     the old text, from 0 until the start of the text being deleted.
#   + the old text, from the start of where the text is being deleted, until
#     the end of the field, shifted to the left, end-start positions
#   + the old text, from the end of the field, to the end of the text.
#
#   So, after the text is deleted, the entry will look like this:
#
#   --------------------------------
#   | ( 1 2 )   3 5 6   - 7 8 9 0  |
#   --------------------------------
#                ^
#                P
#
#   P = the position of the cursor after the deletion, witch is equal to
#   start (s at the previous ilustration)

    def _on_delete_text(self, editable, start, end):
        if not self._mask or self._block_delete:
            return

        self.stop_emission('delete-text')

        pos = self.get_position()
        # Trying to delete an static char. Delete the char before that
        if (0 < start < len(self._mask_validators)
            and not isinstance(self._mask_validators[start], int)
            and pos != start):
            self._on_delete_text(editable, start-1, start)
            return

        field = self._get_field_at_pos(end-1)
        # Outside a field. Cannot delete.
        if field is None:
            self.set_position(end-1)
            return
        _start, _end = self._mask_fields[field]

        # Deleting from outside the bounds of the field.
        if start < _start or end > _end:
            _start, _end = start, end

        # Change the text
        text = self.get_text()

        # Shift Left
        new_text = (text[:start] +
                    self._shift_text(start, _end, DIRECTION_LEFT,
                                     end-start) +
                    text[_end:])

        # Overwrite Left
#        empty_mask = self.get_empty_mask()
#        new_text = (text[:_start] +
#                    text[_start:start] +
#                    empty_mask[start:start+(end-start)] +
#                    text[start+(end-start):_end] +
#                    text[_end:])

        new_pos = start

        self._block_changed = True
        self._really_delete_text(0, -1)
        self._block_changed = False
        self._really_insert_text(new_text, 0)

        # Position the cursor on the right place.
        self.set_position(new_pos)

        if self.is_empty():
            pos = self.get_field_pos(0)
            self.set_position(pos)

    def _after_grab_focus(self, widget):
        # The text is selectet in grab-focus, so this needs to be done after
        # that:
        if self.is_empty():
            if self._mask:
                self.set_field(0)
            else:
                self.set_position(0)

    def _on_focus(self, widget, direction):
        if not self._mask:
            return

        if (direction == gtk.DIR_TAB_FORWARD or
            direction == gtk.DIR_DOWN):
            inc = 1
        if (direction == gtk.DIR_TAB_BACKWARD or
            direction == gtk.DIR_UP):
            inc = -1

        field = self._current_field

        field += inc
        # Leaving the entry
        if field == len(self._mask_fields) or field == -1:
            self.select_region(0, 0)
            self._current_field = -1
            return False

        if field < 0:
            field = len(self._mask_fields)-1

        # grab_focus changes the selection, so we need to grab_focus before
        # making the selection.
        self.grab_focus()
        self.set_field(field, select=True)

        return True

    def _on_notify_cursor_position(self, widget, pspec):
        if not self._mask:
            return

        if not self.is_focus():
            return

        if self._selecting:
            return

        pos = self.get_position()
        field = self._get_field_at_pos(pos)

        if pos == 0:
            self.set_position(self.get_field_pos(0))
            return

        text = self.get_text()
        field = self._get_field_at_pos(pos)

        # Humm, the pos is not inside any field. Get the next pos inside
        # some field, depending on the direction that the cursor is
        # moving
        diff = pos - self._pos
        _field = field
        while _field is None and (len(text) > pos > 0) and diff:
            pos += diff
            _field = self._get_field_at_pos(pos)
            self._pos = pos

        if field is None:
            self.set_position(self._pos)
        else:
            self._current_field = field
            self._pos = pos

    def _on_changed(self, widget):
        if self._block_changed:
            self.stop_emission('changed')

    def _on_focus_out_event(self, widget, event):
        if not self._mask:
            return

        self._current_field = -1

    def _on_move_cursor(self, entry, step, count, extend_selection):
        self._selecting = extend_selection

    def _on_button_press_event(self, entry, event ):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self._selecting = True
        elif event.type == gtk.gdk.BUTTON_RELEASE and event.button == 1:
            self._selecting = True

    # IconEntry

    def set_tooltip(self, text):
        self._icon.set_tooltip(text)

    def set_pixbuf(self, pixbuf):
        self._icon.set_pixbuf(pixbuf)

    def set_stock(self, stock_name):
        pixbuf = self.render_icon(stock_name, gtk.ICON_SIZE_MENU)
        self._icon.set_pixbuf(pixbuf)

    def update_background(self, color):
        self._icon.update_background(color)

    def get_background(self):
        return self._icon.get_background()

    def get_icon_window(self):
        return self._icon.get_icon_window()

    # Combo
    
    def prefill(self, itemdata, sort=False):
        if not isinstance(itemdata, (list, tuple)):
            raise TypeError("'data' parameter must be a list or tuple of item "
                            "descriptions, found %s") % type(itemdata)

        completion = self._get_completion()
        model = completion.get_model()

        if len(itemdata) == 0:
            model.clear()
            return

        values = {}
        if sort:
            itemdata.sort()

        for item in itemdata:
            if item in values:
                raise KeyError("Tried to insert duplicate value "
                                   "%r into the entry" % item)
            else:
                values[item] = None

            model.append((item,))
            
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(MaskedEntry)

#number = (int, float, long)

VALIDATION_ICON_WIDTH = 16
MANDATORY_ICON = gtk.STOCK_INFO
ERROR_ICON = gtk.STOCK_STOP

class ValidatableMaskedEntry(MaskedEntry):
    """It extends the MaskedEntry with validation feature.

    Merged from Kiwi's ValidatableProxyWidgetMixin and ProxyEntry
    """

    __gtype_name__ = 'ValidatableMaskedEntry'

    __gsignals__ = {
        'content-changed': (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            ()),
        'validation-changed': (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (gobject.TYPE_BOOLEAN,)),
        'validate': (gobject.SIGNAL_RUN_LAST,
                     gobject.TYPE_PYOBJECT,
                     (gobject.TYPE_PYOBJECT,)),
        'changed': 'override',
    }

    __gproperties__ = {
        'data-type': (gobject.TYPE_PYOBJECT,
                       'Data Type of the widget',
                       'Type object',
                       gobject.PARAM_READWRITE),
        'mandatory': (gobject.TYPE_BOOLEAN,
                      'Mandatory',
                      'Mandatory',
                      False,
                      gobject.PARAM_READWRITE),
    }
                            
    # FIXME put the data type support back
    #allowed_data_types = (basestring, datetime.date, datetime.time,
                          #datetime.datetime, object) + number

    def __init__(self, data_type=None):
        self.data_type = None
        self.mandatory = False
        
        MaskedEntry.__init__(self)
        
        self._block_changed = False
        self._valid = True
        self._fade = FadeOut(self)
        self._fade.connect('color-changed', self._on_fadeout__color_changed)
        
        # FIXME put data type support back
        #self.set_property('data-type', data_type)

    # Virtual methods
    def do_changed(self):
        if self._block_changed:
            self.emit_stop_by_name('changed')
            return
        self.emit('content-changed')
        self.validate()

    def do_get_property(self, prop):
        '''Return the gproperty's value.'''
        
        if prop.name == 'data-type':
            return self.data_type
        elif prop.name == 'mandatory':
            return self.mandatory
        else:
            raise AttributeError, 'unknown property %s' % prop.name

    def do_set_property(self, prop, value):
        '''Set the property of writable properties.'''
        
        if prop.name == 'data-type':
            if value is None:
                self.data_type = value
                return
        
            # FIXME put the data type support back
            #if not issubclass(value, self.allowed_data_types):
                #raise TypeError(
                    #"%s only accept %s types, not %r"
                    #% (self,
                       #' or '.join([t.__name__ for t in self.allowed_data_types]),
                       #value))
            self.data_type = value
        elif prop.name == 'mandatory':
            self.mandatory = value
        else:
            raise AttributeError, 'unknown or read only property %s' % prop.name

    # Public API

    def is_valid(self):
        """
        @returns: True if the widget is in validated state
        """
        return self._valid

    def validate(self, force=False):
        """Checks if the data is valid.
        Validates data-type and custom validation.

        @param force: if True, force validation
        @returns:     validated data or ValueUnset if it failed
        """

        # If we're not visible or sensitive return a blank value, except
        # when forcing the validation
        if not force and (not self.get_property('visible') or
                          not self.get_property('sensitive')):
            return None

        try:
            text = self.get_text()
            ##log.debug('Read %r for %s' %  (data, self.model_attribute))

            # check if we should draw the mandatory icon
            # this need to be done before any data conversion because we
            # we don't want to end drawing two icons
            if self.mandatory and self.is_empty():
                self.set_blank()
                return None
            else:
                if self._completion:
                    for row in self.get_completion().get_model():
                        if row[COL_TEXT] == text:
                            break
                    else:
                        if text:
                            raise ValidationError()
                else:
                    if not self.is_empty():
                        # this signal calls the on_widgetname__validate method
                        # of the view class and gets the exception (if any).
                        error = self.emit("validate", text)
                        if error:
                            raise error

            self.set_valid()
            return text
        except ValidationError, e:
            self.set_invalid(str(e))
            return None

    def set_valid(self):
        """Changes the validation state to valid, which will remove icons and
        reset the background color
        """

        ##log.debug('Setting state for %s to VALID' % self.model_attribute)
        self._set_valid_state(True)

        self._fade.stop()
        self.set_pixbuf(None)

    def set_invalid(self, text=None, fade=True):
        """Changes the validation state to invalid.
        @param text: text of tooltip of None
        @param fade: if we should fade the background
        """
        ##log.debug('Setting state for %s to INVALID' % self.model_attribute)

        self._set_valid_state(False)

        # If there is no error text, set a generic one so the error icon
        # still have a tooltip
        if not text:
            text = _("'%s' is not a valid value "
                     "for this field") % self.get_text()

        self.set_tooltip(text)

        if not fade:
            self.set_stock(ERROR_ICON)
            self.update_background(gtk.gdk.color_parse(self._fade.ERROR_COLOR))
            return

        # When the fading animation is finished, set the error icon
        # We don't need to check if the state is valid, since stop()
        # (which removes this timeout) is called as soon as the user
        # types valid data.
        def done(fadeout, c):
            self.set_stock(ERROR_ICON)
            self.queue_draw()
            fadeout.disconnect(c.signal_id)

        class SignalContainer:
            pass
        c = SignalContainer()
        c.signal_id = self._fade.connect('done', done, c)

        if self._fade.start(self.get_background()):
            self.set_pixbuf(None)

    def set_blank(self):
        """Changes the validation state to blank state, this only applies
        for mandatory widgets, draw an icon and set a tooltip"""

        ##log.debug('Setting state for %s to BLANK' % self.model_attribute)

        if self.mandatory:
            self.set_stock(MANDATORY_ICON)
            self.queue_draw()
            self.set_tooltip(_('This field is mandatory'))
            self._fade.stop()
            valid = False
        else:
            valid = True

        self._set_valid_state(valid)

    def set_text(self, text):
        """
        Sets the text of the entry

        @param text:
        """

        # If content isn't empty set_text emitts changed twice.
        # Protect content-changed from being updated and issue
        # a manual emission afterwards
        self._block_changed = True
        MaskedEntry.set_text(self, text)
        self._block_changed = False
        self.emit('content-changed')

        self.set_position(-1)

    # Private

    def _set_valid_state(self, state):
        """Updates the validation state and emits a signal if it changed"""

        if self._valid == state:
            return

        self.emit('validation-changed', state)
        self._valid = state

    # Callbacks

    def _on_fadeout__color_changed(self, fadeout, color):
        self.update_background(color)

if gtk.pygtk_version < (2,8,0):
    gobject.type_register(ValidatableMaskedEntry)


def main(args):
    from RelLib import Date
    from DateHandler import parser
    
    def on_validate(widget, text):
        myDate = parser.parse(text)
        if not myDate.is_regular():
            return ValidationError("This is not a proper date value")
        
    win = gtk.Window()
    win.set_title('ValidatableMaskedEntry test window')
    win.set_position(gtk.WIN_POS_CENTER)
    def cb(window, event):
        gtk.main_quit()
    win.connect('delete-event', cb)

    vbox = gtk.VBox()
    win.add(vbox)
    
    label = gtk.Label('Pre-filled entry validated against the given list:')
    vbox.pack_start(label)
    
    widget1 = ValidatableMaskedEntry(str)
    widget1.prefill(('Birth', 'Death', 'Conseption'))
    vbox.pack_start(widget1, fill=False)
    
    label = gtk.Label('Mandatory masked entry validated against user function:')
    vbox.pack_start(label)
    
    widget2 = ValidatableMaskedEntry(str)
    widget2.set_mask('00/00/0000')
    widget2.connect('validate', on_validate)
    widget2.mandatory = True
    vbox.pack_start(widget2, fill=False)

    win.show_all()
    gtk.main()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
