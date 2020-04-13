#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
# Copyright (C) 2011       Tim G L Lyons
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
from gramps.gen.plug._pluginreg import *
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

MODULE_VERSION="5.2"

#------------------------------------------------------------------------
#
# Age on Date
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'ageondate',
name = _("Age on Date"),
description = _("Display people and ages on a particular date"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'ageondate.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_DATE,
runfunc = 'run'
  )

#------------------------------------------------------------------------
#
# Attribute Match
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'attribute_match',
name = _("Attribute Match"),
description = _("Display people with same attribute."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'attributematch.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_MISC,
runfunc = 'run'
  )

#------------------------------------------------------------------------
#
# All Events
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'all_events',
name = _("All Events"),
description = _("Display a person's events, both personal and family."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'all_events.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )


register(QUICKREPORT,
id = 'all_events_fam',
name = _("All Family Events"),
description = _("Display the family and family members events."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'all_events.py',
authors = ["B. Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
category = CATEGORY_QR_FAMILY,
runfunc = 'run_fam'
  )

#------------------------------------------------------------------------
#
# Relation to Home Person
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'all_relations',
name = _("Relation to Home Person"),
description = _("Display all relationships between person and home person."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'all_relations.py',
authors = ["B. Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )

#------------------------------------------------------------------------
#
# Filter
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'filterbyname',
name = _("Filter"),
description = _("Display filtered data"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'filterbyname.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_MISC,
runfunc = 'run'
  )

#------------------------------------------------------------------------
#
# Father/mother lineage
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'father_lineage',
name = _("Father lineage"),
description = _("Display father lineage"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'lineage.py',
authors = ["B. Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run_father'
  )

register(QUICKREPORT,
id = 'mother_lineage',
name = _("Mother lineage"),
description = _("Display mother lineage"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'lineage.py',
authors = ["B. Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run_mother'
  )

#------------------------------------------------------------------------
#
# On This Day
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'onthisday',
name = _("On This Day"),
description = _("Display events on a particular day"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'onthisday.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_EVENT,
runfunc = 'run'
  )

#------------------------------------------------------------------------
#
# References
#
#------------------------------------------------------------------------

refitems = [(CATEGORY_QR_PERSON, 'person', _("Person")),
            (CATEGORY_QR_FAMILY,'family', _("Family")),
            (CATEGORY_QR_EVENT, 'event', _("Event")),
            (CATEGORY_QR_SOURCE, 'source', _("Source")),
            (CATEGORY_QR_PLACE, 'place', _("Place")),
            (CATEGORY_QR_MEDIA, 'media', _("Media")),
            (CATEGORY_QR_NOTE, 'note', _("Note")),
            (CATEGORY_QR_CITATION, 'citation', _("Citation")),
            (CATEGORY_QR_SOURCE_OR_CITATION, 'source_or_citation',
                    _("Source or Citation"))
            ]

for (category, item, trans) in refitems:
    register(QUICKREPORT,
        id = item + 'references',
        name = _("%s References") % trans,
        description = _("Display references for a %s") % trans,
        version = '1.0',
        gramps_target_version = MODULE_VERSION,
        status = STABLE,
        fname = 'references.py',
        authors = ["Douglas Blank"],
        authors_email = ["dblank@cs.brynmawr.edu"],
        category = category,
        runfunc = 'run_%s' % item
        )

register(QUICKREPORT,
  id = 'link_references',
  name = _("Link References"),
  description = _("Display link references for a note"),
  version = '1.0',
  gramps_target_version = MODULE_VERSION,
  status = STABLE,
  fname = 'linkreferences.py',
  authors = ["Douglas Blank"],
  authors_email = ["doug.blank@gmail.com"],
  category = CATEGORY_QR_NOTE,
  runfunc = 'run'
)

#------------------------------------------------------------------------
#
# Show Repository Reference
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'RepoRef',
name = _("Repository References"),
description = _("Display the repository reference for sources related to"
                 " the active repository"),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'reporef.py',
authors = ["Jerome Rapinat"],
authors_email = ["romjerome@yahoo.fr"],
category = CATEGORY_QR_REPOSITORY,
runfunc = 'run'
  )

#------------------------------------------------------------------------
#
# Same Surnames/Given names
#
#------------------------------------------------------------------------

register(QUICKREPORT,
id = 'samesurnames',
name = _("Same Surnames"),
description = _("Display people with the same surname as a person."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'samesurnames.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )

register(QUICKREPORT,
id = 'samegivens',
name = _("Same Given Names"),
description = _("Display people with the same given name as a person."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'samesurnames.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_PERSON,
runfunc = 'run_given'
  )

register(QUICKREPORT,
id = 'samegivens_misc',
name = _("Same Given Names - stand-alone"),
description = _("Display people with the same given name as a person."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'samesurnames.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_MISC,
runfunc = 'run_given'
  )

#------------------------------------------------------------------------
#
# siblings
#
#------------------------------------------------------------------------
register(QUICKREPORT,
id = 'siblings',
name = _("Siblings"),
description = _("Display a person's siblings."),
version = '1.0',
gramps_target_version = MODULE_VERSION,
status = STABLE,
fname = 'siblings.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )
