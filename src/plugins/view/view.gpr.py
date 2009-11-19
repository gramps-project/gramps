# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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

#------------------------------------------------------------------------
#
# default views of Gramps
#
#------------------------------------------------------------------------

register(VIEW, 
id    = 'eventview',
name  = _("Event View"),
description =  _("The view showing all the events"),
version = '1.0',
status = STABLE,
fname = 'eventview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_EVENT,
viewclass = 'EventView',
order = START,
  )

register(VIEW, 
id    = 'familyview',
name  = _("Family View"),
description =  _("The view showing all families"),
version = '1.0',
status = STABLE,
fname = 'familyview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_FAMILY,
viewclass = 'FamilyView',
order = START,
  )

register(VIEW, 
id    = 'grampletview',
name  = _("Gramplet View"),
description =  _("The view allowing to see Gramplets"),
version = '1.0',
status = STABLE,
fname = 'grampletview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_MISC,
viewclass = 'GrampletView',
order = START,
  )

register(VIEW, 
id    = 'mediaview',
name  = _("Media View"),
description =  _("The view showing all the media objects"),
version = '1.0',
status = STABLE,
fname = 'mediaview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_MEDIA,
viewclass = 'MediaView',
order = START,
  )

register(VIEW, 
id    = 'noteview',
name  = _("Note View"),
description =  _("The view showing all the notes"),
version = '1.0',
status = STABLE,
fname = 'noteview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_NOTE,
viewclass = 'NoteView',
order = START,
  )

register(VIEW, 
id    = 'relview',
name  = _("Relationship View"),
description =  _("The view showing all relationships of the selected person"),
version = '1.0',
status = STABLE,
fname = 'relview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_REL,
viewclass = 'RelationshipView',
order = START,
  )

register(VIEW, 
id    = 'pedigreeview',
name  = _("Pedigree View"),
description =  _("The view showing an ancestor pedigree of the selected person"),
version = '1.0',
status = STABLE,
fname = 'pedigreeview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_PEDI,
viewclass = 'PedigreeView',
  )

register(VIEW, 
id    = 'personview',
name  = _("Person View"),
description =  _("The view showing all people in the family tree"),
version = '1.0',
status = STABLE,
fname = 'personview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_PERSON,
viewclass = 'PersonView',
order = START,
  )

register(VIEW, 
id    = 'placeview',
name  = _("Place View"),
description =  _("The view showing all the places of the family tree"),
version = '1.0',
status = STABLE,
fname = 'placeview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_PLACE,
viewclass = 'PlaceView',
order = START,
  )

register(VIEW, 
id    = 'repoview',
name  = _("Repository View"),
description =  _("The view showing all the repositories"),
version = '1.0',
status = STABLE,
fname = 'repoview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_REPO,
viewclass = 'RepositoryView',
order = START,
  )

register(VIEW, 
id    = 'sourceview',
name  = _("Source View"),
description =  _("The view showing all the sources"),
version = '1.0',
status = STABLE,
fname = 'sourceview.py',
authors = [u"The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = VIEW_SOURCE,
viewclass = 'SourceView',
order = START,
  )
