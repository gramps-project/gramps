#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004 Donald N. Allingham
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

import const
import gtk.glade
import gnome
import gnome.ui

try:
    import gconf
except ImportError:
    import gnome.gconf
    gconf = gnome.gconf

from gettext import gettext as _

_StartupEntry = "/apps/gramps/startup"

def need_to_run():
    client = gconf.client_get_default()
    client.add_dir("/apps/gramps",gconf.CLIENT_PRELOAD_NONE)
    val = client.get_int(_StartupEntry)
    if val < const.startup:
        return 1
    return 0

class StartupDialog:

    def __init__(self,task,args):

        self.task = task
        self.args = args

        self.w = gtk.Window()
        self.fg_color = gtk.gdk.color_parse('#7d684a')
        self.bg_color = gtk.gdk.color_parse('#e1dbc5')
        self.logo = gtk.gdk.pixbuf_new_from_file("%s/gramps.png" % const.rootDir)
        self.splash = gtk.gdk.pixbuf_new_from_file("%s/splash.jpg" % const.rootDir)

        self.client = gconf.client_get_default()

        d = gnome.ui.Druid()
        self.w.add(d)
        d.add(self.build_page1())
        d.add(self.build_page2())
        d.add(self.build_page3())
        d.add(self.build_page4())
        d.add(self.build_page5())
        d.add(self.build_page_last())

        d.connect('cancel',self.close)
        self.w.connect("destroy_event", self.close)
        
        self.w.show_all()

    def close(self,obj):
        self.task(self.args)

    def build_page1(self):
        p = gnome.ui.DruidPageEdge(0)
        p.set_title(_('Getting Started'))
        p.set_title_color(self.fg_color)
        p.set_bg_color(self.bg_color)
        p.set_logo(self.logo)
        p.set_watermark(self.splash)
        p.set_text(_('Welcome to GRAMPS, the Genealogical Research '
                     'and Analysis Management Programming System.\n'
                     'Several options and information need to be gathered '
                     'before GRAMPS is ready to be used. Any of this '
                     'information can be changed in the future in the '
                     'Preferences dialog under the Settings menu.'))
        return p

    def build_page_last(self):
        p = gnome.ui.DruidPageEdge(1)
        p.set_title(_('Complete'))
        p.set_title_color(self.fg_color)
        p.set_bg_color(self.bg_color)
        p.set_logo(self.logo)
        p.set_watermark(self.splash)
        p.connect('finish',self.complete)

        p.set_text(_('GRAMPS is an Open Source project. Its success '
                     'depends on the users. User feedback is important. '
                     'Please join the mailing lists, submit bug reports, '
                     'suggest improvements, and see how you can '
                     'contribute.\n\nPlease enjoy using GRAMPS.'))
        return p

    def get_string(self,key):
        val = self.client.get_string(key)
        if val == None:
            return ""
        else:
            return val

    def complete(self,obj,obj2):
        self.client.set_string('/apps/gramps/researcher-name',unicode(self.name.get_text()))
        self.client.set_string('/apps/gramps/researcher-addr',unicode(self.addr.get_text()))
        self.client.set_string('/apps/gramps/researcher-city',unicode(self.city.get_text()))
        self.client.set_string('/apps/gramps/researcher-state',unicode(self.state.get_text()))
        self.client.set_string('/apps/gramps/researcher-postal',unicode(self.postal.get_text()))
        self.client.set_string('/apps/gramps/researcher-country',unicode(self.country.get_text()))
        self.client.set_string('/apps/gramps/researcher-phone',unicode(self.phone.get_text()))
        self.client.set_string('/apps/gramps/researcher-email',unicode(self.email.get_text()))

        if self.date1.get_active():
            self.client.set_int("/apps/gramps/date-entry",0)
        elif self.date2.get_active():
            self.client.set_int("/apps/gramps/date-entry",1)
        elif self.date3.get_active():
            self.client.set_int("/apps/gramps/date-entry",2)
            
        self.client.set_bool("/apps/gramps/show-calendar",self.calendar.get_active())
        self.client.set_bool("/apps/gramps/use-lds",self.lds.get_active())
        self.client.set_int(_StartupEntry,const.startup)
        self.w.destroy()
        self.task(self.args)
        
    def build_page2(self):
        p = gnome.ui.DruidPageStandard()
        p.set_title(_('Researcher Information'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)
        
        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")
        
        label = gtk.Label(_('In order to create valid GEDCOM files, the following information '
                            'needs to be entered. If you do not plan to generate GEDCOM files, '
                            'you may leave this empty.'))
        label.set_line_wrap(gtk.TRUE)
        
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

        name = self.get_string('/apps/gramps/researcher-name')
        if name.strip() == "":
            import pwd
            import os

            try:
                name = pwd.getpwnam(os.environ['USER'])[4]
            except:
                name = ""

        self.name.set_text(name)
        self.addr.set_text(self.get_string('/apps/gramps/researcher-addr'))
        self.city.set_text(self.get_string('/apps/gramps/researcher-city'))
        self.state.set_text(self.get_string('/apps/gramps/researcher-state'))
        self.postal.set_text(self.get_string('/apps/gramps/researcher-postal'))
        self.country.set_text(self.get_string('/apps/gramps/researcher-country'))
        self.phone.set_text(self.get_string('/apps/gramps/researcher-phone'))
        self.email.set_text(self.get_string('/apps/gramps/researcher-email'))

        return p

    def build_page3(self):
        p = gnome.ui.DruidPageStandard()
        p.set_title(_('Numerical date formats'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")

        label = gtk.Label(_('There are three common formats for entering dates in a numerical\n'
                            'format. Without some type of indication, GRAMPS cannot correctly\n'
                            'tell what format you are using. Please indicate your preferred format\n'
                            'for entering numerical dates.'))
        box.add(label)
        align = gtk.Alignment(0.5,0)
        box.add(align)
        vbox = gtk.VBox()
        vbox.set_spacing(6)
        align.add(vbox)
        
        self.date1 = gtk.RadioButton(label=_("MM/DD/YYYY (United States)"))
        self.date2 = gtk.RadioButton(label=_("DD/MM/YYYY (European)"),group=self.date1)
        self.date3 = gtk.RadioButton(label=_("YYYY-MM-DD (ISO)"),group=self.date1)

        val = self.client.get_int("/apps/gramps/date-entry")
            
        if val == 0:
            self.date1.set_active(1)
        elif val == 1:
            self.date2.set_active(1)
        elif val == 2:
            self.date3.set_active(1)

        vbox.add(self.date1)
        vbox.add(self.date2)
        vbox.add(self.date3)
        
        box.show_all()
        return p

    def build_page4(self):
        p = gnome.ui.DruidPageStandard()
        p.set_title(_('Alternate calendar support'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)
        
        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")
        
        label = gtk.Label(_('By default, all dates stored by GRAMPS use the Gregorian calendar.\n'
                            'This is normally sufficient for most users. Support may be enabled\n'
                            'for the Julian, French Republican, and Hebrew calendar. If you believe\n'
                            'that you will need one or more of these alternate calendars, enable\n'
                            'alternate calendar support\n'))
        box.add(label)
        align = gtk.Alignment(0.5,0)
        box.add(align)
        vbox = gtk.VBox()
        vbox.set_spacing(6)
        
        self.calendar = gtk.CheckButton(label=_("Enable support for alternate calendars"))

        self.calendar.set_active(self.client.get_bool("/apps/gramps/show-calendar"))
        
        align.add(self.calendar)
        
        box.show_all()
        return p

    def build_page5(self):
        p = gnome.ui.DruidPageStandard()
        p.set_title(_('LDS extensions'))
        p.set_title_foreground(self.fg_color)
        p.set_background(self.bg_color)
        p.set_logo(self.logo)

        box = gtk.VBox()
        box.set_spacing(12)
        p.append_item("",box,"")
        
        label = gtk.Label(_('GRAMPS has support for LDS Ordinances, which are special event types\n'
                            'related to the Church of Jesus Christ of Latter Day Saints.\n\n'
                            'You may choose to either enable or disable this support. You may\n'
                            'change this option in the future in the Preferences dialog.'))

        box.add(label)
        align = gtk.Alignment(0.5,0)
        box.add(align)
        vbox = gtk.VBox()
        vbox.set_spacing(6)
        
        self.lds = gtk.CheckButton(label=_("Enable LDS ordinance support"))

        self.lds.set_active(self.client.get_bool("/apps/gramps/use-lds"))

        align.add(self.lds)
        
        box.show_all()
        return p

def make_label(table,val,y,x1,x2,x3,x4):
    label = gtk.Label(val)
    label.set_alignment(0,0.5)
    text = gtk.Entry()
    table.attach(label,x1,x2,y,y+1,gtk.SHRINK|gtk.FILL)
    table.attach(text,x3,x4,y,y+1,gtk.EXPAND|gtk.FILL)
    return text
