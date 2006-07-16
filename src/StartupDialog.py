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
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK+/GNOME modules
#
#-------------------------------------------------------------------------
import gtk

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
    val = Config.get(Config.STARTUP)
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
        import gconf
        
        client = gconf.client_get_default()
        client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)

        Config.set(Config.FPREFIX,client.get_string('/apps/gramps/fprefix'))
        Config.set(Config.SPREFIX,client.get_string('/apps/gramps/sprefix'))
        Config.set(Config.PPREFIX,client.get_string('/apps/gramps/pprefix'))
        Config.set(Config.OPREFIX,client.get_string('/apps/gramps/oprefix'))
        Config.set(Config.IPREFIX,client.get_string('/apps/gramps/iprefix'))

        Config.set(Config.RESEARCHER_COUNTRY,
                   client.get_string('/apps/gramps/researcher-country'))
        
        Config.set(Config.RESEARCHER_EMAIL,
                   client.get_string('/apps/gramps/researcher-email'))
        Config.set(Config.RESEARCHER_PHONE,
                   client.get_string('/apps/gramps/researcher-phone'))
        Config.set(Config.RESEARCHER_CITY,
                   client.get_string('/apps/gramps/researcher-city'))
        Config.set(Config.RESEARCHER_POSTAL,
                   client.get_string('/apps/gramps/researcher-postal'))
        Config.set(Config.RESEARCHER_ADDR,
                   client.get_string('/apps/gramps/researcher-addr'))
        Config.set(Config.RESEARCHER_STATE,
                   client.get_string('/apps/gramps/researcher-state'))
        Config.set(Config.RESEARCHER_NAME,
                   client.get_string('/apps/gramps/researcher-name'))

        Config.set(Config.AUTOLOAD,
                   client.get_bool('/apps/gramps/autoload'))
        Config.set(Config.STATUSBAR,
                   client.get_int('/apps/gramps/statusbar'))
        Config.set(Config.VIEW,
                   not client.get_bool('/apps/gramps/view'))
        Config.set(Config.SIZE_CHECKED,
                   client.get_bool('/apps/gramps/screen-size-checked'))
        Config.set(Config.SURNAME_GUESSING,
                   client.get_int('/apps/gramps/surname-guessing'))
        toolbar = client.get_int('/apps/gramps/toolbar')
        if toolbar == 5:
            toolbar = -1
        Config.set(Config.TOOLBAR_ON,
                   client.get_bool('/apps/gramps/toolbar-on'))
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
            Config.set(Config.STARTUP,const.startup)
            self.close()
            return
        self.w = Assistant.Assistant(None, self.complete)
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
        except IndexError:
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
        Config.set(Config.RESEARCHER_NAME,
                   unicode(self.name.get_text()))
        Config.set(Config.RESEARCHER_ADDR,
                   unicode(self.addr.get_text()))
        Config.set(Config.RESEARCHER_CITY,
                   unicode(self.city.get_text()))
        Config.set(Config.RESEARCHER_STATE,
                   unicode(self.state.get_text()))
        Config.set(Config.RESEARCHER_POSTAL,
                   unicode(self.postal.get_text()))
        Config.set(Config.RESEARCHER_COUNTRY,
                   unicode(self.country.get_text()))
        Config.set(Config.RESEARCHER_PHONE,
                   unicode(self.phone.get_text()))
        Config.set(Config.RESEARCHER_EMAIL,
                   unicode(self.email.get_text()))

        Config.set(Config.STARTUP,
                   const.startup)
        self.w.destroy()        
        Config.sync()
        self.task(self.args)
        
    def build_page2(self):
        
        box = gtk.VBox()
        box.set_spacing(12)
        
        label = gtk.Label(
            _('The following information is needed if you want to export '
              'your data to a GEDCOM file. A GEDCOM file can be imported '
              'into nearly all genealogy programs. A valid GEDCOM file '
              'needs this information, but most programs do not require '
              'it. You may leave this empty if you want.'))
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

        name = Config.get(Config.RESEARCHER_NAME)
        if not name or name.strip() == "":
            try:
                import pwd
                import os
                name = pwd.getpwnam(os.environ['USER'])[4]
            except:
                name = ""

        self.name.set_text(name.replace(',,,',''))

        try:
            self.addr.set_text(Config.get(Config.RESEARCHER_ADDR))
            self.city.set_text(Config.get(Config.RESEARCHER_CITY))
            self.state.set_text(Config.get(Config.RESEARCHER_STATE))
            self.postal.set_text(Config.get(Config.RESEARCHER_POSTAL))
            self.country.set_text(Config.get(Config.RESEARCHER_COUNTRY))
            self.phone.set_text(Config.get(Config.RESEARCHER_PHONE))
            self.email.set_text(Config.get(Config.RESEARCHER_EMAIL))
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

def make_label(table,val,y,x1,x2,x3,x4):
    label = gtk.Label(val)
    label.set_alignment(0,0.5)
    text = gtk.Entry()
    table.attach(label,x1,x2,y,y+1,gtk.SHRINK|gtk.FILL)
    table.attach(text,x3,x4,y,y+1,gtk.EXPAND|gtk.FILL)
    return text
