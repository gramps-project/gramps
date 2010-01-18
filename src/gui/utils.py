#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"""
Utility functions that depend on GUI components or for GUI components
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
from gen.ggettext import gettext as _
# gtk is not included here, because this file is currently imported
# by code that needs to run without the DISPLAY variable (eg, in
# the cli only).

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
import Errors

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def add_menuitem(menu, msg, obj, func):
    """
    add a menuitem to menu with label msg, which activates func, and has data
    obj
    """
    import gtk
    item = gtk.MenuItem(msg)
    item.set_data('o', obj)
    item.connect("activate", func)
    item.show()
    menu.append(item)
    
#-------------------------------------------------------------------------
#
#  Progress meter class
#
#-------------------------------------------------------------------------

class ProgressMeter(object):
    """
    Progress meter class for GRAMPS.
    
    The progress meter has two modes:
    
    MODE_FRACTION is used when you know the number of steps that will be taken.
    Set the total number of steps, and then call step() that many times. 
    The progress bar will progress from left to right.
    
    MODE_ACTIVITY is used when you don't know the number of steps that will be
    taken. Set up the total number of steps for the bar to get from one end of
    the bar to the other. Then, call step() as many times as you want. The bar
    will move from left to right until you stop calling step. 
    """
    
    MODE_FRACTION = 0
    MODE_ACTIVITY = 1
    
    def __init__(self, title, header='', can_cancel=False, 
                 cancel_callback=None):
        """
        Specify the title and the current pass header.
        """
        import gtk
        self.__mode = ProgressMeter.MODE_FRACTION
        self.__pbar_max = 100.0
        self.__pbar_index = 0.0
        self.__old_val = -1
        self.__can_cancel = can_cancel
        self.__cancelled = False
        if cancel_callback:
            self.__cancel_callback = cancel_callback
        else:
            self.__cancel_callback = self.handle_cancel
        
        self.__dialog = gtk.Dialog()
        if self.__can_cancel:
            self.__dialog.connect('delete_event', self.__cancel_callback)
        else:
            self.__dialog.connect('delete_event', self.__warn)
        self.__dialog.set_has_separator(False)
        self.__dialog.set_title(title)
        self.__dialog.set_border_width(12)
        self.__dialog.vbox.set_spacing(10)
        self.__dialog.vbox.set_border_width(24)
        self.__dialog.set_size_request(350, 125)
        
        tlbl = gtk.Label('<span size="larger" weight="bold">%s</span>' % title)
        tlbl.set_use_markup(True)
        self.__dialog.vbox.add(tlbl)
        
        self.__lbl = gtk.Label(header)
        self.__lbl.set_use_markup(True)
        self.__dialog.vbox.add(self.__lbl)
 
        self.__pbar = gtk.ProgressBar()
        self.__dialog.vbox.add(self.__pbar)

        if self.__can_cancel:
            self.__dialog.set_size_request(350, 170)
            self.__cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
            self.__cancel_button.connect('clicked', self.__cancel_callback)
            self.__dialog.vbox.add(self.__cancel_button)
        
        self.__dialog.show_all()
        if header == '':
            self.__lbl.hide()

    def handle_cancel(self, *args, **kwargs):
        """
        Default cancel handler (if enabled).
        """
        self.__cancel_button.set_sensitive(False)
        self.__lbl.set_label(_("Cancelling..."))
        self.__cancelled = True

    def get_cancelled(self):
        """
        Returns cancelled setting. True if progress meter has been
        cancelled.
        """
        return self.__cancelled

    def set_pass(self, header="", total=100, mode=MODE_FRACTION):
        """
        Reset for another pass. Provide a new header and define number
        of steps to be used.
        """
        import gtk
        self.__mode = mode
        self.__pbar_max = total
        self.__pbar_index = 0.0
        
        # If it is cancelling, don't overwite that message:
        if not self.__cancelled:
            self.__lbl.set_text(header)
            if header == '':
                self.__lbl.hide()
            else:
                self.__lbl.show()

        if self.__mode is ProgressMeter.MODE_FRACTION:
            self.__pbar.set_fraction(0.0)
        else: # ProgressMeter.MODE_ACTIVITY
            self.__pbar.set_pulse_step(1.0/self.__pbar_max)
        
        while gtk.events_pending():
            gtk.main_iteration()

    def step(self):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%."""
        import gtk
        if self.__mode is ProgressMeter.MODE_FRACTION:
            self.__pbar_index = self.__pbar_index + 1.0
            
            if self.__pbar_index > self.__pbar_max:
                self.__pbar_index = self.__pbar_max
    
            try:
                val = int(100*self.__pbar_index/self.__pbar_max)
            except ZeroDivisionError:
                val = 0
    
            if val != self.__old_val:
                self.__pbar.set_text("%d%%" % val)
                self.__pbar.set_fraction(val/100.0)
                self.__old_val = val
        else: # ProgressMeter.MODE_ACTIVITY
            self.__pbar.pulse()
            
        while gtk.events_pending():
            gtk.main_iteration()

        return self.__cancelled

    def set_header(self, text):
        import gtk
        self.__lbl.set_text(text)
        while gtk.events_pending():
	    gtk.main_iteration()
	
    def __warn(self, *obj):
        """
        Don't let the user close the progress dialog.
        """
        from QuestionDialog import WarningDialog
        WarningDialog(
            _("Attempt to force closing the dialog"), 
            _("Please do not force closing this important dialog."), 
            self.__dialog)
        return True

    def close(self):
        """
        Close the progress meter
        """
        self.__dialog.destroy()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def open_file_with_default_application( file_path ):
    """
    Launch a program to open an arbitrary file. The file will be opened using 
    whatever program is configured on the host as the default program for that 
    type of file.
    
    @param file_path: The path to the file to be opened.
        Example: "c:\foo.txt"
    @type file_path: string
    @return: nothing
    """
    from QuestionDialog import ErrorDialog
    norm_path = os.path.normpath( file_path )
    
    if not os.path.exists(norm_path):
        ErrorDialog(_("Error Opening File"), _("File does not exist"))
        return
        
    if os.sys.platform == 'win32':
        try:
            os.startfile(norm_path)
        except WindowsError, msg:
            ErrorDialog(_("Error Opening File"), str(msg))
    else:
        if os.sys.platform == 'darwin':
            utility = 'open'
        else:
            utility = 'xdg-open'
        search = os.environ['PATH'].split(':')
        for lpath in search:
            prog = os.path.join(lpath, utility)
            if os.path.isfile(prog):
                os.spawnvpe(os.P_NOWAIT, prog, [prog, norm_path], os.environ)
                return

def process_pending_events(max_count=10):
    """
    Process pending events, but don't get into an infinite loop.
    """
    import gtk
    count = 0
    while gtk.events_pending():
        gtk.main_iteration()
        count += 1
        if count >= max_count:
            break
