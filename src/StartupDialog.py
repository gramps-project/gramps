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

import const
import libglade
import gnome.config
import utils

class StartupDialog:

    def __init__(self,task,arg):
        self.task = task
        self.arg = arg

        self.druid = libglade.GladeXML(const.configFile,"initDruid")
        self.druid.signal_autoconnect({
            "destroy_passed_object" : self.on_cancel_clicked,
            "on_initDruid_finish" : self.on_finish
            })

    def on_finish(self,obj,b):
        
        name = self.druid.get_widget("dresname").get_text()
        addr = self.druid.get_widget("dresaddr").get_text()
        city = self.druid.get_widget("drescity").get_text()
        state = self.druid.get_widget("dresstate").get_text()
        country = self.druid.get_widget("drescountry").get_text()
        postal = self.druid.get_widget("drespostal").get_text()
        phone = self.druid.get_widget("dresphone").get_text()
        email = self.druid.get_widget("dresemail").get_text()
        
        gnome.config.set_string("/gramps/researcher/name",name)
        gnome.config.set_string("/gramps/researcher/addr",addr)
        gnome.config.set_string("/gramps/researcher/city",city)
        gnome.config.set_string("/gramps/researcher/state",state)
        gnome.config.set_string("/gramps/researcher/country",country)
        gnome.config.set_string("/gramps/researcher/postal",postal)
        gnome.config.set_string("/gramps/researcher/phone",phone)
        gnome.config.set_string("/gramps/researcher/email",email)
        gnome.config.sync()
        utils.destroy_passed_object(obj)
        self.task(self.arg)

    def on_cancel_clicked(self,obj,a):
        self.task(self.arg)
        utils.destroy_passed_object(obj)
