#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import GdkImlib
import const
import libglade
import gnome.config
import Utils

_StartupEntry = "/gramps/config/startup"

def need_to_run():
    if gnome.config.get_string(_StartupEntry) == None:
        return 1
    val  = gnome.config.get_int(_StartupEntry) 
    if val < const.startup:
        return 1
    return 0


class StartupDialog:

    def __init__(self,task,arg):
        self.task = task
        self.arg = arg

        self.druid = libglade.GladeXML(const.configFile,"initDruid")
        self.druid.signal_autoconnect({
            "on_cancel_clicked" : self.on_cancel_clicked,
            "destroy_event": self.destroy,
            "on_finish" : self.on_finish
            })

        self.rlist = ['name','addr','city','state','country',
                      'postal', 'phone', 'email']

        for tag in self.rlist:
            val = gnome.config.get_string("/gramps/researcher/%s" % tag)
            if val != None:
                self.druid.get_widget(tag).set_text(val)

    def destroy(self,obj):
        self.task(self.arg)
       
    def on_finish(self,obj,b):
        for tag in self.rlist:
            val = self.druid.get_widget(tag).get_text()
            gnome.config.set_string("/gramps/researcher/%s" % tag,val)

        if self.druid.get_widget("num_us").get_active():
            dateFormat = 0
        elif self.druid.get_widget("num_eu").get_active():
            dateFormat = 1
        else:
            dateFormat = 2
        gnome.config.set_int("/gramps/config/dateEntry",dateFormat)

        showcal = self.druid.get_widget("altcal").get_active()
        gnome.config.set_int("/gramps/config/ShowCalendar",showcal)

        lds = self.druid.get_widget("enable_lds").get_active()
        gnome.config.set_int("/gramps/config/UseLDS",lds)
        gnome.config.set_int(_StartupEntry,const.startup)
        gnome.config.sync()
        Utils.destroy_passed_object(obj)

    def on_cancel_clicked(self,obj):
        gnome.config.set_int(_StartupEntry,const.startup)
        gnome.config.sync()
        Utils.destroy_passed_object(obj)
