
#------------------------------------------------------------------------
#
# Age on Date
#
#------------------------------------------------------------------------

register(QUICKREPORT, 
id    = 'ageondate',
name  = _("Age on Date"),
description =  _("Display people and ages on a particular date"),
version = '1.0',
status = STABLE,
fname = 'AgeOnDate.py',
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
id    = 'attribute_match',
name  = _("Attribute Match"),
description =  _("Display people with same attribute."),
version = '1.0',
status = STABLE,
fname = 'AttributeMatch.py',
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
id    = 'all_events',
name  = _("All Events"),
description =  _("Display a person's events, both personal and family."),
version = '1.0',
status = STABLE,
fname = 'all_events.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )


register(QUICKREPORT, 
id    = 'all_events_fam',
name  = _("All Events"),
description =  _("Display the family and family members events."),
version = '1.0',
status = STABLE,
fname = 'all_events.py',
authors = ["B. Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
category = CATEGORY_QR_FAMILY,
runfunc = 'run_fam'
  )

#------------------------------------------------------------------------
#
# All Names of All People
#
#------------------------------------------------------------------------

register(QUICKREPORT, 
id    = 'allnames',
name  = _("All Names of All People"),
description =  _("All names of all people"),
version = '1.0',
status = STABLE,
fname = 'AllNames.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )
  
#------------------------------------------------------------------------
#
# Relation to Home Person
#
#------------------------------------------------------------------------

register(QUICKREPORT, 
id    = 'all_relations',
name  = _("Relation to Home Person"),
description =  _("Display all relationships between person and home person."),
version = '1.0',
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
id    = 'filterbyname',
name  = _("Filter"),
description =  _("Display filtered data"),
version = '1.0',
status = STABLE,
fname = 'FilterByName.py',
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
id    = 'father_lineage',
name  = _("Father lineage"),
description =  _("Display father lineage"),
version = '1.0',
status = STABLE,
fname = 'lineage.py',
authors = ["B. Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run_father'
  )

register(QUICKREPORT, 
id    = 'mother_lineage',
name  = _("Mother lineage"),
description =  _("Display mother lineage"),
version = '1.0',
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
id    = 'onthisday',
name  = _("On This Day"),
description =  _("Display events on a particular day"),
version = '1.0',
status = STABLE,
fname = 'OnThisDay.py',
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
            ]

for (category, item, trans) in refitems:
    register(QUICKREPORT, 
        id    = item + 'references',
        name  = _("%s References") % trans,
        description =  _("Display references for a %s") % trans,
        version = '1.0',
        status = STABLE,
        fname = 'References.py',
        authors = ["Douglas Blank"],
        authors_email = ["dblank@cs.brynmawr.edu"],
        category = category,
        runfunc = 'run_%s' % item
        )

#------------------------------------------------------------------------
#
# Show Repository Reference
#
#------------------------------------------------------------------------

register(QUICKREPORT, 
id    = 'RepoRef',
name  = _("Show Repository Reference"),
description =  _("Display the repository reference for sources related to"
                 " the active repository"),
version = '1.0',
status = STABLE,
fname = 'Reporef.py',
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
id    = 'samesurnames',
name  = _("Same Surnames"),
description =  _("Display people with the same surname as a person."),
version = '1.0',
status = STABLE,
fname = 'SameSurnames.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )

register(QUICKREPORT, 
id    = 'samegivens',
name  = _("Same Given Names"),
description =  _("Display people with the same given name as a person."),
version = '1.0',
status = STABLE,
fname = 'SameSurnames.py',
authors = ["Douglas Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = CATEGORY_QR_PERSON,
runfunc = 'run_given'
  )

register(QUICKREPORT, 
id    = 'samegivens_misc',
name  = _("Same Given Names"),
description =  _("Display people with the same given name as a person."),
version = '1.0',
status = STABLE,
fname = 'SameSurnames.py',
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
id    = 'siblings',
name  = _("Siblings"),
description =  _("Display a person's siblings."),
version = '1.0',
status = STABLE,
fname = 'siblings.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = CATEGORY_QR_PERSON,
runfunc = 'run'
  )
