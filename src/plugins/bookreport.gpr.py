
#------------------------------------------------------------------------
#
# Book plugin
#
#------------------------------------------------------------------------

register(REPORT, 
id    = 'book',
name  = _("Book Report"),
description =  _("Produces a book containing several reports."),
version = '1.0',
status = STABLE,
fname = 'BookReport.py',
authors = ["Alex Roitman"],
authors_email = ["shura@gramps-project.org"],
category = CATEGORY_BOOK,
reportclass = 'BookReportSelector',
optionclass = 'cl_report',
report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI]
  )
