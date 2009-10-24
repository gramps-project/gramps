
#------------------------------------------------------------------------
#
# Ancestor Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'ancestor_report'
plg.name  = _("Ahnentafel Report")
plg.description =  _("Produces a textual ancestral report")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'AncestorReport.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'AncestorReport'
plg.optionclass = 'AncestorOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Birthday Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'birthday_report'
plg.name  = _("Birthday and Anniversary Report")
plg.description =  _("Produces a report of birthdays and anniversaries")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'AncestorReport.py'
plg.ptype = REPORT
plg.authors = ["Douglas S. Blank"]
plg.authors_email = ["dblank@cs.brynmawr.edu"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'CalendarReport'
plg.optionclass = 'CalendarOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Custem text BookItem
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'custom_text'
plg.name  = _("Custom Text")
plg.description =  _("Add custom text to the book report")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'CustomBookText.py'
plg.ptype = REPORT
plg.authors = ["The Gramps Project"]
plg.authors_email = [""]
plg.category = CATEGORY_TEXT
plg.reportclass = 'CustomText'
plg.optionclass = 'CustomTextOptions'
plg.report_modes = [REPORT_MODE_BKI]

#------------------------------------------------------------------------
#
# Descendant Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'descend_report'
plg.name  = _("Descendant Report")
plg.description =  _("Produces a list of descendants of the active person")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'DescendReport.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'DescendantReport'
plg.optionclass = 'DescendantOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Detailed Ancestral Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'det_ancestor_report'
plg.name  = _("Detailed Ancestral Report")
plg.description =  _("Produces a detailed ancestral report")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'DetAncestralReport.py'
plg.ptype = REPORT
plg.authors = ["Bruce DeGrasse"]
plg.authors_email = ["bdegrasse1@attbi.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'DetAncestorReport'
plg.optionclass = 'DetAncestorOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Detailed Descendant Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'det_descendant_report'
plg.name  = _("Detailed Descendant Report")
plg.description =  _("Produces a detailed descendant report")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'DetDescendantReport.py'
plg.ptype = REPORT
plg.authors = ["Bruce DeGrasse"]
plg.authors_email = ["bdegrasse1@attbi.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'DetDescendantReport'
plg.optionclass = 'DetDescendantOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# End of Line Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'endofline_report'
plg.name  = _("End of Line Report")
plg.description =  _("Produces a textual end of line report")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'EndOfLineReport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'EndOfLineReport'
plg.optionclass = 'EndOfLineOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Family Group Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'family_group'
plg.name  = _("Family Group Report")
plg.description =  _("Produces a family group report showing information "
                    "on a set of parents and their children.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'FamilyGroup.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'FamilyGroup'
plg.optionclass = 'FamilyGroupOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Complete Individual Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'indiv_complete'
plg.name  = _("Complete Individual Report")
plg.description =  _("Produces a complete report on the selected people")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'IndivComplete.py'
plg.ptype = REPORT
plg.authors = ["Donald N. Allingham"]
plg.authors_email = ["don@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'IndivCompleteReport'
plg.optionclass = 'IndivCompleteOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Kinship Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'kinship_report'
plg.name  = _("Kinship Report")
plg.description =  _("Produces a textual report of kinship for a given person")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'KinshipReport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'KinshipReport'
plg.optionclass = 'KinshipOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Marker Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'marker_report'
plg.name  = _("Marker Report")
plg.description =  _("Produces a list of people with a specified marker")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'MarkerReport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'MarkerReport'
plg.optionclass = 'MarkerOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Number of Ancestors Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'number_of_ancestors_report'
plg.name  = _("Number of Ancestors Report")
plg.description =  _("Counts number of ancestors of selected person")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'NumberOfAncestorsReport.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'NumberOfAncestorsReport'
plg.optionclass = 'NumberOfAncestorsOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

#------------------------------------------------------------------------
#
# Place Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'place_report'
plg.name  = _("Place Report")
plg.description =  _("Produces a textual place report")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'PlaceReport.py'
plg.ptype = REPORT
plg.authors = ["Gary Burton"]
plg.authors_email = ["gary.burton@zen.co.uk"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'PlaceReport'
plg.optionclass = 'PlaceOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False

#------------------------------------------------------------------------
#
# Book Title Page
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'simple_book_title'
plg.name  = _("Title Page")
plg.description =  _("Produces a title page for book reports.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'SimpleBookTitle.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'SimpleBookTitle'
plg.optionclass = 'SimpleBookTitleOptions'
plg.report_modes = [REPORT_MODE_BKI]

#------------------------------------------------------------------------
#
# Database Summary Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'summary'
plg.name  = _("Database Summary Report")
plg.description =  _("Provides a summary of the current database")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'Summary.py'
plg.ptype = REPORT
plg.authors = ["Brian G. Matherly"]
plg.authors_email = ["brian@gramps-project.org"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'SummaryReport'
plg.optionclass = 'SummaryOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False
