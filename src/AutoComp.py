#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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

"""
Adds autocompletion to a GtkEntry box, using the passed list of
strings as the possible completions.
"""

import string
import gtk

cnv = string.lower

class AutoComp:
    """
    Allows allow completion of the GtkEntry widget with the entries
    in the passed string list.
    """
    def __init__(self,widget,plist,source=None):
        self.entry = widget
        if source:
            self.nlist = source.nlist
        else:
            self.nlist = map((lambda n: (cnv(n),n)),plist)
            self.nlist.sort()
        self.entry.connect("insert-text",self.insert_text)

    def insert_text(self,entry,new_text,new_text_len,i_dont_care):
        """
        Sets up a delayed (0.005 sec) handler for text completion.  Text
        completion cannot be handled directly in this routine because, for
        some reason, the select_region() function doesn't work when called
        from signal handlers.  Go figure.

        Thanks to iain@nodata.demon.co.uk (in mail from 1999) for the idea
        to use a timer to get away from the problems with signal handlers
        and the select_region function.
        """
        
        # One time setup to clear selected region when user moves on
        if (not entry.get_data("signal_set")):
            entry.set_data("signal_set",1)
            entry.signal_connect("focus_out_event", self.lost_focus, entry)

        # Nuke the current timer if the user types fast enough
        timer = entry.get_data("timer");
        if (timer):
            gtk.timeout_remove(timer)

        # Setup a callback timer so we can operate outside of a signal handler
        timer = gtk.timeout_add(5, self.timer_callback, entry)
        entry.set_data("timer", timer);

    def lost_focus(self,entry,a,b):
        """
        The entry box entry field lost focus.  Go clear any selection.  Why
        this form of a select_region() call works in a signal handler and
        the other form doesn't is a mystery.
        """
        entry.select_region(0, 0)

    def timer_callback(self,entry):
        """
        The workhorse routine of file completion.  This routine grabs the
        current text of the entry box, and grubs through the list item
        looking for any case insensitive matches.  This routine relies on
        public knowledge of the GtkEntry data structure, not on any private
        data.
        """
        
        # Clear any timer
        timer = entry.get_data("timer");
        if (timer):
            gtk.timeout_remove(timer)

        # Get the user's text
        typed = entry.get_text()
        if (not typed):
            return
        typed_lc = string.lower(typed)

        # Walk the GtkList in the entry box
        for nl,n in self.nlist:
            if (not nl):
                continue

            # If equal, no need to add any text
            if (typed_lc == nl):
                return

            # If typed text is a substring of the label text, then fill in
            # the entry field with the full text (and correcting
            # capitalization), and then select all the characters that
            # don't match.  With the user's enxt keystroke these will be
            # replaced if they are incorrect.
            if (string.find(nl,typed_lc) == 0):
                entry.set_text(n)
                entry.set_position(len(typed))
                entry.select_region(len(typed), -1)
                return

