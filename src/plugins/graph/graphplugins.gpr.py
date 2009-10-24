
#------------------------------------------------------------------------
#
# Family Lines Graph
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'familylines_graph'
plg.name  = _("Family Lines Graph")
plg.description =  _("Produces family line graphs using GraphViz")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'GVFamilyLines.py'
plg.ptype = REPORT
plg.authors = ["Stephane Charette"]
plg.authors_email = ["stephanecharette@gmail.com"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = 'FamilyLinesReport'
plg.optionclass = 'FamilyLinesOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Hourglass Graph
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'hourglass_graph'
plg.name  = _("Hourglass Graph")
plg.description =  _("Produces an hourglass graph using Graphviz")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'GVHourGlass.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = 'HourGlassReport'
plg.optionclass = 'HourGlassOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Relationship Graph
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'rel_graph'
plg.name  = _("Relationship Graph")
plg.description =  _("Produces relationship graphs using Graphviz")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'GVRelGraph.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_GRAPHVIZ
plg.reportclass = 'RelGraphReport'
plg.optionclass = 'RelGraphOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
