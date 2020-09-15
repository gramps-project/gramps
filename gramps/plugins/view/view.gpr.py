# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2009 Nick Hall
# Copyright (C) 2011 Tim G L Lyons
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

MODULE_VERSION="5.2"

#------------------------------------------------------------------------
#
# default views of Gramps
#
#------------------------------------------------------------------------

register(VIEW,
id = 'eventview',
name = _("Events"),
description = _("The view showing all the events"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'eventview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Events", _("Events")),
viewclass = 'EventView',
order = START,
  )

register(VIEW,
id = 'familyview',
name = _("Families"),
description = _("The view showing all families"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'familyview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Families", _("Families")),
viewclass = 'FamilyView',
order = START,
  )

register(VIEW,
id = 'dashboardview',
name = _("Dashboard"),
description = _("The view showing Gramplets"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'dashboardview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Dashboard", _("Dashboard")),
viewclass = 'DashboardView',
order = START,
  )

register(VIEW,
id = 'mediaview',
name = _("Media"),
description = _("The view showing all the media objects"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'mediaview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Media", _("Media")),
viewclass = 'MediaView',
order = START,
  )

register(VIEW,
id = 'noteview',
name = _("Notes"),
description = _("The view showing all the notes"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'noteview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Notes", _("Notes")),
viewclass = 'NoteView',
order = START,
  )

register(VIEW,
id = 'relview',
name = _("Relationships"),
description = _("The view showing all relationships of the selected person"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'relview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Relationships", _("Relationships")),
viewclass = 'RelationshipView',
order = START,
  )

register(VIEW,
id = 'pedigreeview',
name = _("Pedigree"),
description = _("The view showing an ancestor pedigree of the selected person"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'pedigreeview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Ancestry", _("Charts")),
viewclass = 'PedigreeView',
order = START,
stock_icon = 'gramps-pedigree',
  )

register(VIEW,
id = 'fanchartview',
name = _("Fan Chart"),
category = ("Ancestry", _("Charts")),
description = _("A view showing parents through a fanchart"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'fanchartview.py',
authors = ["Douglas S. Blank", "B. Malengier"],
authors_email = ["doug.blank@gmail.com", "benny.malengier@gmail.com"],
viewclass = 'FanChartView',
stock_icon = 'gramps-fanchart',
  )

register(VIEW,
id = 'fanchartdescview',
name = _("Descendant Fan"),
category = ("Ancestry", _("Charts")),
description = _("Showing descendants through a fanchart"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'fanchartdescview.py',
authors = ["B. Malengier"],
authors_email = ["benny.malengier@gmail.com"],
viewclass = 'FanChartDescView',
stock_icon = 'gramps-fanchartdesc',
  )

register(VIEW,
id = 'fanchart2wayview',
name = _("2-Way Fan"),
category = ("Ancestry", _("Charts")),
description = _("Showing ascendants and descendants through a fanchart"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'fanchart2wayview.py',
authors = ["B. Jacquet"],
authors_email = ["bastien.jacquet_dev@m4x.org"],
viewclass = 'FanChart2WayView',
stock_icon = 'gramps-fanchart2way',
  )

register(VIEW,
id = 'personview',
name = _("Grouped People"),
description = _("The view showing all people in the Family Tree grouped per"
                 " family name"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'persontreeview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("People", _("People")),
viewclass = 'PersonTreeView',
order = START,
stock_icon = 'gramps-tree-group',
  )

register(VIEW,
id = 'personlistview',
name = _("People"),
description = _("The view showing all people in the Family Tree"
                 " in a flat list"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'personlistview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("People", _("People")),
viewclass = 'PersonListView',
stock_icon = 'gramps-tree-list',
  )

register(VIEW,
id = 'placelistview',
name = _("Places"),
description = _("The view showing all the places of the Family Tree"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'placelistview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Places", _("Places")),
viewclass = 'PlaceListView',
stock_icon = 'gramps-tree-list',
  )

register(VIEW,
id = 'placetreeview',
name = _("Place Tree"),
description = _("A view displaying places in a tree format."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'placetreeview.py',
authors = ["Donald N. Allingham", "Gary Burton", "Nick Hall"],
authors_email = [""],
category = ("Places", _("Places")),
viewclass = 'PlaceTreeView',
stock_icon = 'gramps-tree-group',
order = START,
  )

register(VIEW,
id = 'repoview',
name = _("Repositories"),
description = _("The view showing all the repositories"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'repoview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Repositories", _("Repositories")),
viewclass = 'RepositoryView',
order = START,
  )

register(VIEW,
id = 'sourceview',
name = _("Sources"),
description = _("The view showing all the sources"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'sourceview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Sources", _("Sources")),
viewclass = 'SourceView',
order = START,
stock_icon = 'gramps-tree-list',
  )

register(VIEW,
id = 'citationlistview',
name = _("Citations"),
description = _("The view showing all the citations"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'citationlistview.py',
authors = ["The Gramps project"],
authors_email = ["http://gramps-project.org"],
category = ("Citations", _("Citations")),
viewclass = 'CitationListView',
order = START,
  )

register(VIEW,
id = 'citationtreeview',
name = _("Citation Tree"),
description = _("A view displaying citations and sources in a tree format."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'citationtreeview.py',
authors = ["Tim G L Lyons", "Nick Hall"],
authors_email = [""],
category = ("Sources", _("Sources")),
viewclass = 'CitationTreeView',
stock_icon = 'gramps-tree-select',
  )
