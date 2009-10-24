# encoding:utf-8

#------------------------------------------------------------------------
#
# records gramplet and text report
#
#------------------------------------------------------------------------

register(REPORT, 
id    = 'records',
name  = _("Records Report"),
description =  _("Shows some interesting records about people and families"),
version = '1.0',
status = STABLE,
fname = 'Records.py',
authors = [u"Reinhard Müller"],
authors_email = ["reinhard.mueller@bytewise.at"],
category = CATEGORY_TEXT,
reportclass = 'RecordsReport',
optionclass = 'RecordsReportOptions',
report_modes = [REPORT_MODE_GUI, REPORT_MODE_CLI, REPORT_MODE_BKI]
  )

register(GRAMPLET, 
id    = 'Records Gramplet',
name  = _("Records Gramplet"),
description =  _("Shows some interesting records about people and families"),
version = '1.0',
status = STABLE,
fname = 'Records.py',
authors = [u"Reinhard Müller"],
authors_email = ["reinhard.mueller@bytewise.at"],
gramplet = 'RecordsGramplet',
height = 230,
expand = True,
gramplet_title = _("Records")
  )
