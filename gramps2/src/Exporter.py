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
import gtk.glade
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
        self.parent = parent
        self.parent_window = parent_window

        self.build_exports()
        
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
        self.last_page = self.build_last_page()
        d.add(self.last_page)

        d.connect('cancel',self.close)
        self.w.connect("destroy_event",self.close)
        self.w.set_transient_for(self.parent_window)
        
        self.w.show_all()

    def close(self,obj,obj2=None):
        self.w.destroy()

    def help(self,obj):
        #FIXME: point to the correct section when it exists
        gnome.help_display('gramps-manual','index')

    def build_info_page(self):
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
        p = gnome.ui.DruidPageEdge(1)
        p.set_title_color(self.fg_color)
        p.set_bg_color(self.bg_color)
        p.set_logo(self.logo)
        p.set_watermark(self.splash)
        p.connect('prepare',self.save)
        p.connect('finish',self.close)
        return p

    def save(self,obj,obj2):
        filename = self.chooser.get_filename()
        success = self.exports[self.ix][0](self.parent.db,filename)
        if success:
            self.last_page.set_title(_('Your data has been saved'))
            self.last_page.set_text(_('You may press Apply button '
                    'now to continue.'))
        else:
            self.last_page.set_title(_('Saving failed'))
            self.last_page.set_text(_('There was an error '
                    'while saving your data. Please go back and try again.'))

    def build_format_page(self):
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
            button.connect('toggled',self.on_format_toggled)
            self.format_buttons.append(button)
            table.attach(button,0,2,2*ix,2*ix+1)
            label = gtk.Label(description)
            label.set_line_wrap(gtk.TRUE)
            table.attach(label,1,2,2*ix+1,2*ix+2)
        
        box.add(table)
        box.show_all()

        return p

    def build_file_sel_page(self):
        p = gnome.ui.DruidPageStandard()
        p.set_title(_('Selecting the file name'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        self.chooser = gtk.FileChooserWidget(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.on_format_toggled(self.format_buttons[0])
        p.append_item("",self.chooser,"")
        
        return p

    def native_export(self,database,filename):
        try:
            shutil.copyfile(database.get_save_path(),filename)
            return 1
        except IOError, msg:
            QuestionDialog.ErrorDialog( _("Could not write file: %s") % filename,
                    _('System message was: %s') % msg )
            return 0

    def on_format_toggled(self,obj):
        if not obj.get_active():
            return
        self.ix = self.format_buttons.index(obj)
        ext = self.exports[self.ix][4]
        new_filename = Utils.get_new_filename(ext)
        self.chooser.set_filename(new_filename)
        self.chooser.set_current_name(os.path.split(new_filename)[1])

    def build_exports(self):
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
