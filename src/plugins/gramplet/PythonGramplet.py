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
# Python modules
#
#------------------------------------------------------------------------
import sys

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from TransUtils import sgettext as _
import gen

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class PythonGramplet(Gramplet):
    def init(self):
        import gc
        gc.set_debug(gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_OBJECTS|gc.DEBUG_SAVEALL)
        self.prompt = ">"
        self.previous = ""
        self.set_tooltip(_("Enter Python expressions"))
        self.gc = gc
        self.env = {"dbstate": self.gui.dbstate,
                    "uistate": self.gui.uistate,
                    "gc": self.gc,
                    "self": self,
                    _("class name|Date"): gen.lib.Date,
                    }
        # GUI setup:
        self.gui.textview.set_editable(True)
        self.set_text("Python %s\n%s " % (sys.version, self.prompt))
        self.gui.textview.connect('key-press-event', self.on_key_press)

    def format_exception(self, max_tb_level=10):
        retval = ''
        cla, exc, trbk = sys.exc_info()
        retval += _("Error") + (" : %s %s" %(cla, exc))
        return retval

    def process_command(self, command):
        # update states, in case of change:
        self.env["dbstate"] = self.gui.dbstate
        self.env["uistate"] = self.gui.uistate
        _retval = None
        if "_retval" in self.env:
            del self.env["_retval"]
        if self.previous:
            if command:
                self.previous += "\n" + command
                return
            else:
                exp = self.previous
        else:
            exp = command.strip()
        try:
            _retval = eval(exp, self.env)
            self.previous = ""
        except:
            try:
                exec exp in self.env
                self.previous = ""
                self.prompt = ">"
            except SyntaxError:
                if command:
                    self.previous = exp
                    self.prompt = "-"
                else:
                    self.previous = ""
                    self.prompt = ">"
                    _retval = self.format_exception()
            except:
                self.previous = ""
                self.prompt = ">"
                _retval = self.format_exception()
        if "_retval" in self.env:
            _retval = self.env["_retval"]
        return _retval

    def on_key_press(self, widget, event):
        import gtk
        if (event.keyval == gtk.keysyms.Home or
            ((event.keyval == gtk.keysyms.a and 
              event.get_state() & gtk.gdk.CONTROL_MASK))): 
            buffer = widget.get_buffer()
            cursor_pos = buffer.get_property("cursor-position")
            iter = buffer.get_iter_at_offset(cursor_pos)
            line_cnt = iter.get_line()
            start = buffer.get_iter_at_line(line_cnt)
            start.forward_chars(2)
            buffer.place_cursor(start)
            return True
        elif (event.keyval == gtk.keysyms.End or 
              (event.keyval == gtk.keysyms.e and 
               event.get_state() & gtk.gdk.CONTROL_MASK)): 
            buffer = widget.get_buffer()
            end = buffer.get_end_iter()
            buffer.place_cursor(end)
            return True
        elif event.keyval == gtk.keysyms.Return: 
            echo = False
            buffer = widget.get_buffer()
            cursor_pos = buffer.get_property("cursor-position")
            iter = buffer.get_iter_at_offset(cursor_pos)
            line_cnt = iter.get_line()
            start = buffer.get_iter_at_line(line_cnt)
            line_len = iter.get_chars_in_line()
            buffer_cnt = buffer.get_line_count()
            if (buffer_cnt - line_cnt) > 1:
                line_len -= 1
                echo = True
            end = buffer.get_iter_at_line_offset(line_cnt, line_len)
            line = buffer.get_text(start, end)
            self.append_text("\n")
            if line.startswith(self.prompt):
                line = line[2:]
            else:
                self.append_text("%s " % self.prompt)
                end = buffer.get_end_iter()
                buffer.place_cursor(end)
                return True
            if echo:
                self.append_text(("%s " % self.prompt) + line)
                end = buffer.get_end_iter()
                buffer.place_cursor(end)
                return True
            _retval = self.process_command(line)
            if _retval is not None:
                self.append_text("%s\n" % str(_retval))
            self.append_text("%s " % self.prompt)
            end = buffer.get_end_iter()
            buffer.place_cursor(end)
            return True
        return False

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name="Python Gramplet", 
         tname=_("Python Gramplet"), 
         height=250,
         content = PythonGramplet,
         title=_("Python Shell"),
         )

