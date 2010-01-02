# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Douglas S. Blank <doug.blank@gmail.com>
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

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Used to save additional information of a user, such as
    themes, bookmarks, etc.
    """
    user = models.ForeignKey(User, unique=True)
    css_theme = models.CharField(max_length=40, 
                                 default="Web_Mainz.css")

    def __unicode__(self):
        return unicode(self.user)

def save_profile(sender, instance, created, **kwargs):
    """
    Creates the profile when the user gets created.
    """
    if created:
        profile = Profile(user=instance)
        profile.save()
    else:
        print sender

post_save.connect(save_profile, sender=User)
