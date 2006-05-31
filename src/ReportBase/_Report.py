#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  David R. Hampton
# Copyright (C) 2001-2006  Donald N. Allingham
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

import Utils

#-------------------------------------------------------------------------
#
# Report
#
#-------------------------------------------------------------------------
class Report:
    """
    The Report base class.  This is a base class for generating
    customized reports.  It cannot be used as is, but it can be easily
    sub-classed to create a functional report generator.
    """

    def __init__(self, database, person, options_class):
        self.database = database
        self.start_person = person
        self.options_class = options_class

        self.doc = options_class.get_document()

        creator = database.get_researcher().get_name()
        self.doc.creator(creator)

        output = options_class.get_output()
        if output:
            self.standalone = True
            self.doc.open(options_class.get_output())
        else:
            self.standalone = False
        
        self.define_table_styles()
        self.define_graphics_styles()

    def begin_report(self):
        if self.options_class.get_newpage():
            self.doc.page_break()
        
    def write_report(self):
        pass

    def end_report(self):
        if self.standalone:
            self.doc.close()
            
    def define_table_styles(self):
        """
        This method MUST be used for adding table and cell styles.
        """
        pass

    def define_graphics_styles(self):
        """
        This method MUST be used for adding drawing styles.
        """
        pass

    def get_progressbar_data(self):
        """The window title for this dialog, and the header line to
        put at the top of the contents of the dialog box."""
        return ("%s - GRAMPS" % _("Progress Report"), _("Working"))

    def progress_bar_title(self,name,length):
        markup = '<span size="larger" weight="bold">%s</span>'
        self.lbl.set_text(markup % name)
        self.lbl.set_use_markup(True)
        self.pbar.set_fraction(0.0)

        progress_steps = length
        if length > 1:
            progress_steps = progress_steps+1
        progress_steps = progress_steps+1
        self.pbar_max = length
        
    def progress_bar_setup(self,total):
        """Create a progress dialog.  This routine calls a
        customization function to find out how to fill out the dialog.
        The argument to this function is the maximum number of items
        that the report will progress; i.e. what's considered 100%,
        i.e. the maximum number of times this routine will be
        called."""
        
        # Customize the dialog for this report
        (title, header) = self.get_progressbar_data()
        self.ptop = gtk.Dialog()
        self.ptop.set_has_separator(False)
        self.ptop.set_title(title)
        self.ptop.set_border_width(12)
        self.lbl = gtk.Label(header)
        self.lbl.set_use_markup(True)
        self.ptop.vbox.add(self.lbl)
        self.ptop.vbox.set_spacing(10)
        self.ptop.vbox.set_border_width(24)
        self.pbar = gtk.ProgressBar()
        self.pbar_max = total
        self.pbar_index = 0.0

        self.ptop.set_size_request(350,100)
        self.ptop.vbox.add(self.pbar)
        self.ptop.show_all()

    def progress_bar_step(self):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%."""
        self.pbar_index = self.pbar_index + 1.0
        if (self.pbar_index > self.pbar_max):
            self.pbar_index = self.pbar_max

        val = self.pbar_index/self.pbar_max
        
        self.pbar.set_text("%d of %d (%.1f%%)" % (self.pbar_index,self.pbar_max,(val*100)))
        self.pbar.set_fraction(val)
        while gtk.events_pending():
            gtk.main_iteration()

    def progress_bar_done(self):
        """Done with the progress bar.  It can be destroyed now."""
        Utils.destroy_passed_object(self.ptop)
