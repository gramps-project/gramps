#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006 Donald N. Allingham
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
# Standard python modules
#
#-------------------------------------------------------------------------
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# GTK+/GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Assistant
import const

import Config
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------

def need_to_run():
    val = Config.get_startup()
    if val < const.startup:
        return True
    return False

def upgrade_prefs():
    """
    Get the preferences from the older keys, store them in the new keys.
    On success, print message and return True.
    On failure, print message and return False.
    """
    try:
        client = gconf.client_get_default()
        client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)

        Config.save_fprefix(client.get_string('/apps/gramps/fprefix'))
        Config.save_sprefix(client.get_string('/apps/gramps/sprefix'))
        Config.save_pprefix(client.get_string('/apps/gramps/pprefix'))
        Config.save_oprefix(client.get_string('/apps/gramps/oprefix'))
        Config.save_iprefix(client.get_string('/apps/gramps/iprefix'))

        Config.save_researcher_country(client.get_string('/apps/gramps/researcher-country'))
        Config.save_researcher_email(client.get_string('/apps/gramps/researcher-email'))
        Config.save_researcher_phone(client.get_string('/apps/gramps/researcher-phone'))
        Config.save_researcher_city(client.get_string('/apps/gramps/researcher-city'))
        Config.save_researcher_postal(client.get_string('/apps/gramps/researcher-postal'))
        Config.save_researcher_addr(client.get_string('/apps/gramps/researcher-addr'))
        Config.save_researcher_state(client.get_string('/apps/gramps/researcher-state'))
        Config.save_researcher_name(client.get_string('/apps/gramps/researcher-name'))

        Config.save_family_view(client.get_int('/apps/gramps/familyview'))
        Config.save_default_view(client.get_int('/apps/gramps/defaultview'))
        Config.save_autoload(client.get_bool('/apps/gramps/autoload'))
        Config.save_uselds(client.get_bool('/apps/gramps/use-lds'))
        Config.save_statusbar(client.get_int('/apps/gramps/statusbar'))
        Config.save_view(not client.get_bool('/apps/gramps/view'))
        Config.save_screen_size_checked(client.get_bool('/apps/gramps/screen-size-checked'))
        Config.save_lastnamegen(client.get_int('/apps/gramps/surname-guessing'))
        toolbar = client.get_int('/apps/gramps/toolbar')
        if toolbar == 5:
            toolbar = -1
        Config.save_toolbar(toolbar)
        Config.save_toolbar_on(client.get_bool('/apps/gramps/toolbar-on'))
        return True
    except:
        return False

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class StartupDialog:

    def __init__(self,task,args):

        self.task = task
        self.args = args

        if not const.no_gconf and upgrade_prefs():
            Config.save_startup(const.startup)
            self.close(None)
            return
        self.w = Assistant.Assistant(self.complete)
        self.w.add_text_page(
            _('Getting started'),
            _('Welcome to GRAMPS, the Genealogical Research '
              'and Analysis Management Programming System.\n'
              'Several options and information need to be gathered '
              'before GRAMPS is ready to be used. Any of this '
              'information can be changed in the future in the '
              'Preferences dialog under the Settings menu.'))
        try:
            self.w.add_page(_('Researcher information'),self.build_page2())
            self.w.add_page(_('LDS support'), self.build_page5())
        except:
            ErrorDialog(_("Configuration error"),
                        _("\n\nPossibly the installation of GRAMPS was incomplete."
                          " Make sure the GConf schema of GRAMPS is properly installed."))
            gtk.main_quit()
            return
            
        self.w.add_text_page(
            _('Complete'),
            _('GRAMPS is an Open Source project. Its success '
              'depends on the users. User feedback is important. '
              'Please join the mailing lists, submit bug reports, '
              'suggest improvements, and see how you can '
              'contribute.\n\nPlease enjoy using GRAMPS.'))

        self.w.show()

    def close(self):
        self.task(self.args)

    def complete(self):
        Config.save_researcher_name(unicode(self.name.get_text()))
        Config.save_researcher_addr(unicode(self.addr.get_text()))
        Config.save_researcher_city(unicode(self.city.get_text()))
        Config.save_researcher_state(unicode(self.state.get_text()))
        Config.save_researcher_postal(unicode(self.postal.get_text()))
        Config.save_researcher_country(unicode(self.country.get_text()))
        Config.save_researcher_phone(unicode(self.phone.get_text()))
        Config.save_researcher_email(unicode(self.email.get_text()))

        Config.save_uselds(self.lds.get_active())
        Config.save_startup(const.startup)
        self.w.destroy()        
        Config.sync()
        self.task(self.args)
        
    def build_page2(self):
        
        box = gtk.VBox()
        box.set_spacing(12)
        
        label = gtk.Label(
            _('In order to create valid GEDCOM files, the following '
              'information needs to be entered. If you do not plan to '
              'generate GEDCOM files, you may leave this empty.'))
        label.set_line_wrap(True)
        
        box.pack_start(label)
        
        table = gtk.Table(8,4)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        
        self.name  = make_label(table,_('Name:'),0,0,1,1,4)
        self.addr  = make_label(table,_('Address:'),1,0,1,1,4)
        self.city  = make_label(table,_('City:'),2,0,1,1,2)
        self.state = make_label(table,_('State/Province:'),2,2,3,3,4)
        self.country = make_label(table,_('Country:'),3,0,1,1,2)
        self.postal = make_label(table,_('ZIP/Postal code:'),3,2,3,3,4)
        self.phone = make_label(table,_('Phone:'),4,0,1,1,4)
        self.email = make_label(table,_('Email:'),5,0,1,1,4)
        
        box.add(table)
        box.show_all()

        name = Config.get_researcher_name()
        if not name or name.strip() == "":
            try:
                import pwd
                import os
                name = pwd.getpwnam(os.environ['USER'])[4]
            except:
                name = ""

        self.name.set_text(name)

        try:
            self.addr.set_text(Config.get_researcher_addr())
            self.city.set_text(Config.get_researcher_city())
            self.state.set_text(Config.get_researcher_state())
            self.postal.set_text(Config.get_researcher_postal())
            self.country.set_text(Config.get_researcher_country())
            self.phone.set_text(Config.get_researcher_phone())
            self.email.set_text(Config.get_researcher_email())
        except:
            ErrorDialog(_("Configuration/Installation error"),
                        _("The gconf schemas were not found. First, try "
                          "executing 'pkill gconfd' and try starting gramps "
                          "again. If this does not help then the schemas "
                          "were not properly installed. If you have not "
                          "done 'make install' or if you installed without "
                          "being a root, this is most likely a cause of the "
                          "problem. Please read the INSTALL file in the "
                          "top-level source directory."))
            gtk.main_quit()
        return box

    def build_page5(self):
        box = gtk.VBox()
        box.set_spacing(12)
        
        label = gtk.Label(
            _('GRAMPS has support for LDS Ordinances, which are special '
              'event types\nrelated to the Church of Jesus Christ of '
              'Latter Day Saints.\n\nYou may choose to either enable '
              'or disable this support. You may\nchange this option in '
              'the future in the Preferences dialog.'))

        box.add(label)
        align = gtk.Alignment(0.5,0)
        box.add(align)
        vbox = gtk.VBox()
        vbox.set_spacing(6)
        
        self.lds = gtk.CheckButton(label=_("Enable LDS ordinance support"))

        self.lds.set_active(Config.get_uselds())

        align.add(self.lds)
        
        box.show_all()
        return box

def make_label(table,val,y,x1,x2,x3,x4):
    label = gtk.Label(val)
    label.set_alignment(0,0.5)
    text = gtk.Entry()
    table.attach(label,x1,x2,y,y+1,gtk.SHRINK|gtk.FILL)
    table.attach(text,x3,x4,y,y+1,gtk.EXPAND|gtk.FILL)
    return text
