
#------------------------------------------------------------------------
#
# EniroMaps
#
#------------------------------------------------------------------------

register(MAPSERVICE, 
id    = 'EniroMaps',
name  = _("EniroMaps"),
description =  _("Opens on kartor.eniro.se"),
version = '1.0',
status = STABLE,
fname = 'eniroswedenmap.py',
authors = ["Peter Landgren"],
authors_email = ["peter.talken@telia.com"],
mapservice = 'EniroSVMapService'
  )

#------------------------------------------------------------------------
#
# GoogleMaps
#
#------------------------------------------------------------------------

register(MAPSERVICE, 
id    = 'GoogleMaps',
name  = _("GoogleMaps"),
description =  _("Open on maps.google.com"),
version = '1.0',
status = STABLE,
fname = 'googlemap.py',
authors = ["Benny Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
mapservice = 'GoogleMapService'
  )

#------------------------------------------------------------------------
#
# OpenStreetMap
#
#------------------------------------------------------------------------

register(MAPSERVICE, 
id    = 'OpenStreetMap',
name  = _("OpenStreetMap"),
description =  _("Open on openstreetmap.org"),
version = '1.0',
status = STABLE,
fname = 'openstreetmap.py',
authors = ["Benny Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
mapservice = 'OpensStreetMapService'
  )
