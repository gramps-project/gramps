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
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
import Errors
from QuestionDialog import WarningDialog, ErrorDialog

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
    
    def __init__(self, title, header=''):
        """
        Specify the title and the current pass header.
        """
        self.__mode = ProgressMeter.MODE_FRACTION
        self.__pbar_max = 100.0
        self.__pbar_index = 0.0
        self.__old_val = -1
        
        self.__dialog = gtk.Dialog()
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
        
        self.__dialog.show_all()
        if header == '':
            self.__lbl.hide()

    def set_pass(self, header="", total=100, mode=MODE_FRACTION):
        """
        Reset for another pass. Provide a new header and define number
        of steps to be used.
        """
        self.__mode = mode
        self.__pbar_max = total
        self.__pbar_index = 0.0
        
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

    def set_header(self, text):
        self.__lbl.set_text(text)
        while gtk.events_pending():
	    gtk.main_iteration()
	
    def __warn(self, *obj):
        """
        Don't let the user close the progress dialog.
        """
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
