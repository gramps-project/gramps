#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004 Donald N. Allingham
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

#
# Written by Alex Roitman, 2004
#

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
import shutil
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import Plugins
import QuestionDialog

#-------------------------------------------------------------------------
#
# Exporter
#
#-------------------------------------------------------------------------
class Exporter:
    """
    This class creates Gnome Druid to guide the user through the various
    Save as/Export options. The overall goal is to keep things simple by
    presenting few choice options on each druid page.
    
    The export formats and options are obtained from the plugins, with the
    exception of a native save. Native save as just copies file to another 
    name. 
    """

    def __init__(self,parent,parent_window):
        """
        Set up the window, the druid, and build all the druid's pages. 
        Some page elements are left empty, since their contents depends
        on the user choices and on the success of the attempted save. 
        """
        self.parent = parent
        self.parent_window = parent_window
        if self.parent.active_person:
            self.active_person = self.parent.active_person
        else:
            self.active_person = self.parent.find_initial_person()

        self.build_exports()
        self.confirm_label = gtk.Label()

        self.w = gtk.Window()

        self.fg_color = gtk.gdk.color_parse('#7d684a')
        self.bg_color = gtk.gdk.color_parse('#e1dbc5')
        self.logo = gtk.gdk.pixbuf_new_from_file("%s/gramps.png" % const.rootDir)
        self.splash = gtk.gdk.pixbuf_new_from_file("%s/splash.jpg" % const.rootDir)

        d = gnome.ui.Druid()
        self.w.add(d)
        d.add(self.build_info_page())
        d.add(self.build_format_page())
        d.add(self.build_file_sel_page())
        d.add(self.build_confirm_page())
        self.last_page = self.build_last_page()
        d.add(self.last_page)

        d.set_show_help(gtk.TRUE)
        d.connect('cancel',self.close)
        d.connect('help',self.help)
        self.w.connect("destroy_event",self.close)
        self.w.set_transient_for(self.parent_window)
        
        self.w.show_all()

    def close(self,obj,obj2=None):
        """
        Close and delete handler.
        """
        self.w.destroy()

    def help(self,obj):
        """
        Help handler.
        """
        #FIXME: point to the correct section when it exists
        gnome.help_display('gramps-manual','index')

    def build_info_page(self):
        """
        Build initial druid page with the overall information about the process.
        This is a static page, nothing fun here :-)
        """
        p = gnome.ui.DruidPageEdge(0)
        p.set_title(_('Saving your data'))
        p.set_title_color(self.fg_color)
        p.set_bg_color(self.bg_color)
        p.set_logo(self.logo)
        p.set_watermark(self.splash)
        p.set_text(_('Under normal circumstances, GRAMPS does not require you '
                    'to directly save your changes. All changes you make are '
                    'immediately saved to the database.\n\n'
                    'This process will help you save a copy of your data '
                    'in any of the several formats supported by GRAMPS. '
                    'This can be used to make a copy of your data, backup '
                    'your data, or convert it to a format that will allow '
                    'you to trasnfer it to a different program.\n\n'
                    'If you change your mind during this process, you '
                    'can safely press Cancel button at any time and your '
                    'present database will still be intact.'))
        return p

    def build_last_page(self):
        """
        Build the last druid page. The actual text will be added after the
        save is performed and the success status us known. 
        """
        p = gnome.ui.DruidPageEdge(1)
        p.set_title_color(self.fg_color)
        p.set_bg_color(self.bg_color)
        p.set_logo(self.logo)
        p.set_watermark(self.splash)
        p.connect('finish',self.close)
        return p

    def build_confirm_page(self):
        """
        Build a save confirmation page. Setting up the actual label 
        text is deferred until the page is being prepared. This
        is necessary, because no choice is made by the user when this
        page is set up. 
        """
        p = gnome.ui.DruidPageStandard()
        p.set_title(_('Final save confirmation'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)
        
        p.append_item("",self.confirm_label,"")

        p.connect('prepare',self.build_confirm_label)
        p.connect('next',self.save)
        return p

    def build_confirm_label(self,obj,obj2):
        """
        Build the text of the confirmation label. This should query
        the selected options (format, filename) and present the summary
        of the proposed action.
        """
        filename = self.chooser.get_filename()
        name = os.path.split(filename)[1]
        folder = os.path.split(filename)[0]
        ix = self.get_selected_format_index()
        format = self.exports[ix][1].replace('_','')

        self.confirm_label.set_text(
                _('The data will be saved as follows:\n\n'
                'Format:\t%s\nName:\t%s\nFolder:\t%s\n\n'
                'Press Forward to proceed, Cancel to abort, or Back to '
                'revisit your options.') % (format, name, folder))
        self.confirm_label.set_line_wrap(gtk.TRUE)

    def save(self,obj,obj2):
        """
        Perform the actual Save As/Export operation. 
        Depending on the success status, set the text for the final page.
        """
        filename = self.chooser.get_filename()
        ix = self.get_selected_format_index()
        success = self.exports[ix][0](self.parent.db,filename)
        if success:
            self.last_page.set_title(_('Your data has been saved'))
            self.last_page.set_text(_('The copy of your data has been '
                    'successfully saved. You may press Apply button '
                    'now to continue.\n\n'
                    'Note: the database currently opened in your GRAMPS '
                    'window is NOT the file you have just saved. '
                    'Future editing of the currently opened database will '
                    'not alter the copy you have just made. '))
        else:
            self.last_page.set_title(_('Saving failed'))
            self.last_page.set_text(_('There was an error '
                    'while saving your data. Please go back and try again.\n\n'
                    'Your currently opened database is safe, it is a copy '
                    'of your data that failed to save.'))

    def build_format_page(self):
        """
        Build a page with the table of format radio buttons and 
        their descriptions.
        """
        self.format_buttons = []

        p = gnome.ui.DruidPageStandard()
        p.set_title(_('Choosing the format to save'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")
        
        table = gtk.Table(2*len(self.exports),2)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        
        group = None
        for ix in range(len(self.exports)):
            title = self.exports[ix][1]
            description= self.exports[ix][2]

            button = gtk.RadioButton(group,title)
            if not group:
                group = button
            self.format_buttons.append(button)
            table.attach(button,0,2,2*ix,2*ix+1)
            label = gtk.Label(description)
            label.set_line_wrap(gtk.TRUE)
            table.attach(label,1,2,2*ix+1,2*ix+2)
        
        box.add(table)
        box.show_all()
        return p

    def build_file_sel_page(self):
        """
        Build a druid page embedding the FileChooserWidget.
        """
        p = gnome.ui.DruidPageStandard()
        p.set_title(_('Selecting the file name'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        self.chooser = gtk.FileChooserWidget(gtk.FILE_CHOOSER_ACTION_SAVE)
        p.append_item("",self.chooser,"")
        p.connect('prepare',self.suggest_filename)
        return p

    def suggest_filename(self,obj,obj2):
        """
        Prepare suggested filename and set it in the file chooser. 
        """
        ix = self.get_selected_format_index()
        ext = self.exports[ix][4]
        if ext == 'gramps':
            new_filename = os.path.expanduser('~/data.gramps')
        else:
            new_filename = Utils.get_new_filename(ext)
        self.chooser.set_filename(new_filename)
        self.chooser.set_current_name(os.path.split(new_filename)[1])

    def get_selected_format_index(self):
        """
        Query the format radiobuttons and return the index number 
        of the selected one. 
        """
        for ix in range(len(self.format_buttons)):
            button = self.format_buttons[ix]
            if button.get_active():
                return ix
        else:
            return 0
    
    def native_export(self,database,filename):
        """
        Native database export. For now, just stupid copying of the present
        grdb file under another name. In the future, filter and other
        options may be added.
        """
        try:
            shutil.copyfile(database.get_save_path(),filename)
            return 1
        except IOError, msg:
            QuestionDialog.ErrorDialog( _("Could not write file: %s") % filename,
                    _('System message was: %s') % msg )
            return 0

    def build_exports(self):
        """
        This method builds its own list of available exports. 
        The list is built from the Plugins._exports list 
        and from the locally defined exports (i.e. native export defined here).
        """
        native_title = _('GRAMPS _GRDB database')
        native_description =_('The GRAMPS GRDB database is a format '
                'that GRAMPS uses to store information. '
                'Selecting this option will allow you to '
                'make a copy of the current database.') 
        native_config = None
        native_ext = 'grdb'
        native_export = self.native_export

        self.exports = [ (native_export,native_title,native_description,
                    native_config,native_ext) ]
        self.exports = self.exports + [ item for item in Plugins._exports ]
