
#------------------------------------------------------------------------
#
# Narrated Web Site
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'navwebpage'
plg.name  = _("Narrated Web Site")
plg.description =  _("Produces web (HTML) pages for individuals, or a set of "
                     "individuals")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'NarrativeWeb.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category =  CATEGORY_WEB
plg.reportclass = 'NavWebReport'
plg.optionclass = 'NavWebOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]


#------------------------------------------------------------------------
#
# Web Calendar
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'WebCal'
plg.name  = _("Web Calendar")
plg.description =  _("Produces web (HTML) calendars.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'WebCal.py'
plg.ptype = REPORT
plg.authors = ["Thom Sturgill"]
plg.authors_email = ["thsturgill@yahoo.com"]
plg.category =  CATEGORY_WEB
plg.reportclass = 'WebCalReport'
plg.optionclass = 'WebCalOptions'
plg.report_modes = [REPORT_MODE_GUI]
