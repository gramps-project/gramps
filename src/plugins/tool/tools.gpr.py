
#------------------------------------------------------------------------
#
# Calculate Estimated Dates
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'calculateestimateddates',
name  = _("Calculate Estimated Dates"),
description =  _("Calculates estimated dates for birth and death."),
version = '0.90',
status = UNSTABLE,
fname = 'CalculateEstimatedDates.py',
authors = ["Douglas S. Blank"],
authors_email = ["dblank@cs.brynmawr.edu"],
category = TOOL_DBPROC,
toolclass = 'CalcToolManagedWindow',
optionclass = 'CalcEstDateOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Fix Capitalization of Family Names
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'chname',
name  = _("Fix Capitalization of Family Names"),
description =  _("Searches the entire database and attempts to "
                    "fix capitalization of the names."),
version = '1.0',
status = STABLE,
fname = 'ChangeNames.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBPROC,
toolclass = 'ChangeNames',
optionclass = 'ChangeNamesOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Rename Event Types
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'chtype',
name  = _("Rename Event Types"),
description =  _("Allows all the events of a certain name "
                    "to be renamed to a new name."),
version = '1.0',
status = STABLE,
fname = 'ChangeTypes.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBPROC,
toolclass = 'ChangeTypes',
optionclass = 'ChangeTypesOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Check and Repair Database
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'check',
name  = _("Check and Repair Database"),
description =  _("Checks the database for integrity problems, fixing the "
                   "problems that it can"),
version = '1.0',
status = STABLE,
fname = 'Check.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBFIX,
toolclass = 'Check',
optionclass = 'CheckOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Check Localized Date Displayer and Parser
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'test_for_date_parser_and_displayer',
name  = _("Check Localized Date Displayer and Parser"),
description =  _("This test tool will create many people showing all"
                        " different date variants as birth. The death date is"
                        " created by parsing the result of the date displayer for"
                        " the birth date. This way you can ensure that dates"
                        " printed can be parsed back in correctly."),
version = '1.0',
status = UNSTABLE,
fname = 'DateParserDisplayTest.py',
authors = ["Martin Hawlisch"],
authors_email = ["martin@hawlisch.de"],
category = TOOL_DEBUG,
toolclass = 'DateParserDisplayTest',
optionclass = 'DateParserDisplayTestOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Interactive Descendant Browser
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'dbrowse',
name  = _("Interactive Descendant Browser"),
description =  _("Provides a browsable hierarchy based on the active person"),
version = '1.0',
status = STABLE,
fname = 'Desbrowser.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_ANAL,
toolclass = 'DesBrowse',
optionclass = 'DesBrowseOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Dump Gender Statistics
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'dgenstats',
name  = _("Dump Gender Statistics"),
description =  _("Will dump the statistics for the gender guessing "
                        "from the first name."),
version = '1.0',
status = STABLE,
fname = 'DumpGenderStats.py',
authors = ["Donald N. Allingham", "Martin Hawlisch"],
authors_email = ["don@gramps-project.org", "martin@hawlisch.de"],
category = TOOL_DEBUG,
toolclass = 'DesBrowse',
optionclass = 'DesBrowseOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Python Evaluation Window
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'eval',
name  = _("Python Evaluation Window"),
description =  _("Provides a window that can evaluate python code"),
version = '1.0',
status = STABLE,
fname = 'Eval.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DEBUG,
toolclass = 'Eval',
optionclass = 'EvalOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Compare Individual Events
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'eventcmp',
name  = _("Compare Individual Events"),
description =  _("Aids in the analysis of data by allowing the "
                    "development of custom filters that can be applied "
                    "to the database to find similar events"),
version = '1.0',
status = STABLE,
fname = 'EventCmp.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_ANAL,
toolclass = 'EventComparison',
optionclass = 'EventComparisonOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Extract Event Descriptions from Event Data
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'evname',
name  = _("Extract Event Description"),
description =  _("Extracts event descriptions from the event data"),
version = '1.0',
status = STABLE,
fname = 'EventNames.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBPROC,
toolclass = 'EventNames',
optionclass = 'EventNamesOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Extract Place Data from a Place Title
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'excity',
name  = _("Extract Place Data from a Place Title"),
description =  _("Attempts to extract city and state/province "
                    "from a place title"),
version = '1.0',
status = STABLE,
fname = 'ExtractCity.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBPROC,
toolclass = 'ExtractCity',
optionclass = 'ExtractCityOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Find Possible Duplicate People
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'dupfind',
name  = _("Find Possible Duplicate People"),
description =  _("Searches the entire database, looking for "
                    "individual entries that may represent the same person."),
version = '1.0',
status = STABLE,
fname = 'FindDupes.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBPROC,
toolclass = 'Merge',
optionclass = 'MergeOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Show Uncollected Objects
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'leak',
name  = _("Show Uncollected Objects"),
description =  _("Provide a window listing all uncollected objects"),
version = '1.0',
status = STABLE,
fname = 'Leak.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DEBUG,
toolclass = 'Leak',
optionclass = 'LeakOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Media Manager
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'mediaman',
name  = _("Media Manager"),
description =  _("Manages batch operations on media files"),
version = '1.0',
status = UNSTABLE,
fname = 'MediaManager.py',
authors = ["Alex Roitman"],
authors_email = ["shura@gramps-project.org"],
category = TOOL_UTILS,
toolclass = 'MediaMan',
optionclass = 'MediaManOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Not Related
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'not_related',
name  = _("Not Related"),
description =  _("Find people who are not in any way related to the "
                    "selected person"),
version = '1.0',
status = STABLE,
fname = 'NotRelated.py',
authors = ["Stephane Charette"],
authors_email = ["stephanecharette@gmail.com"],
category = TOOL_UTILS,
toolclass = 'NotRelated',
optionclass = 'NotRelatedOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Edit Database Owner Information
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'editowner',
name  = _("Edit Database Owner Information"),
description =  _("Allow editing database owner information."),
version = '1.0',
status = UNSTABLE,
fname = 'OwnerEditor.py',
authors = ["Zsolt Foldvari"],
authors_email = ["zfoldvar@users.sourceforge.net"],
category = TOOL_DBPROC,
toolclass = 'OwnerEditor',
optionclass = 'OwnerEditorOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Extract Information from Names
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'patchnames',
name  = _("Extract Information from Names"),
description =  _("Allow editing database owner information."),
version = '1.0',
status = STABLE,
fname = 'PatchNames.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBPROC,
toolclass = 'PatchNames',
optionclass = 'PatchNamesOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Rebuild Secondary Indices
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'rebuild',
name  = _("Rebuild Secondary Indices"),
description =  _("Rebuilds secondary indices"),
version = '1.0',
status = STABLE,
fname = 'Rebuild.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBFIX,
toolclass = 'Rebuild',
optionclass = 'RebuildOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Rebuild Secondary Indices
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'rebuild_refmap',
name  = _("Rebuild Reference Maps"),
description =  _("Rebuilds reference maps"),
version = '1.0',
status = STABLE,
fname = 'RebuildRefMap.py',
authors = ["Alex Roitman"],
authors_email = ["shura@gramps-project.org"],
category = TOOL_DBFIX,
toolclass = 'RebuildRefMap',
optionclass = 'RebuildRefMapOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Relationship Calculator
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'relcalc',
name  = _("Relationship Calculator"),
description =  _("Calculates the relationship between two people"),
version = '1.0',
status = STABLE,
fname = 'RelCalc.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_UTILS,
toolclass = 'RelCalc',
optionclass = 'RelCalcOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Remove Unused Objects
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'remove_unused',
name  = _("Remove Unused Objects"),
description =  _("Removes unused objects from the database"),
version = '1.0',
status = STABLE,
fname = 'RemoveUnused.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBFIX,
toolclass = 'RemoveUnused',
optionclass = 'CheckOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Reorder GRAMPS IDs
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'reorder_ids',
name  = _("Reorder GRAMPS IDs"),
description =  _("Reorders the gramps IDs "
                    "according to Gramps' default rules."),
version = '1.0',
status = STABLE,
fname = 'ReorderIds.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_DBPROC,
toolclass = 'ReorderIds',
optionclass = 'ReorderIdsOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Sorts events
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'sortevents',
name  = _("Sorts events"),
description =  _("Sorts events"),
version = '1.0',
status = STABLE,
fname = 'SortEvents.py',
authors = ["Gary Burton"],
authors_email = ["gary.burton@zen.co.uk"],
category = TOOL_DBPROC,
toolclass = 'SortEvents',
optionclass = 'SortEventOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Generate SoundEx Codes
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'soundgen',
name  = _("Generate SoundEx Codes"),
description =  _("Generates SoundEx codes for names"),
version = '1.0',
status = STABLE,
fname = 'SoundGen.py',
authors = ["Donald N. Allingham"],
authors_email = ["don@gramps-project.org"],
category = TOOL_UTILS,
toolclass = 'SoundGen',
optionclass = 'SoundGenOptions',
tool_modes = [TOOL_MODE_GUI]
  )

#------------------------------------------------------------------------
#
# Generate Testcases for Persons and Families
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'testcasegenerator',
name  = _("Generate Testcases for Persons and Families"),
description =  _("The testcase generator will generate some persons "
                        "and families that have broken links in the database "
                        "or data that is in conflict to a relation."),
version = '1.0',
status = UNSTABLE,
fname = 'TestcaseGenerator.py',
authors = ["Martin Hawlisch"],
authors_email = ["martin@hawlisch.de"],
category = TOOL_DEBUG,
toolclass = 'TestcaseGenerator',
optionclass = 'TestcaseGeneratorOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )

#------------------------------------------------------------------------
#
# Verify the Data
#
#------------------------------------------------------------------------

register(TOOL, 
id    = 'verify',
name  = _("Verify the Data"),
description =  _("Verifies the data against user-defined tests"),
version = '1.0',
status = STABLE,
fname = 'Verify.py',
authors = ["Alex Roitman"],
authors_email = ["shura@gramps-project.org"],
category = TOOL_UTILS,
toolclass = 'Verify',
optionclass = 'VerifyOptions',
tool_modes = [TOOL_MODE_GUI, TOOL_MODE_CLI]
  )
