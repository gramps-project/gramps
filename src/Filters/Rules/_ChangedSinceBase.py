#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import re
import time

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules import Rule

#-------------------------------------------------------------------------
#
# ChangedSince
#
#-------------------------------------------------------------------------
class ChangedSinceBase(Rule):
    """
    Rule that checks for primary objects changed since a specific time.
    """

    labels      = [ _('Changed after:'), _('but before:') ]
    name        = _('Objects changed after <date time>')
    description = _("Matches object records changed after a specified "
                    "date/time (yyyy-mm-dd hh:mm:ss) or in range, if a second "
                    "date/time is given.")
    category    = _('General filters')

    def add_time(self, date):
        if re.search("\d.*\s+\d{1,2}:\d{2}:\d{2}", date):
            return date
        elif re.search("\d.*\s+\d{1,2}:\d{2}", date):
            return date + ":00"
        elif re.search("\d.*\s+\d{1,2}", date):
            return date + ":00:00"
        elif re.search("\d{4}-\d{1,2}-\d{1,2}", date):
            return date + " 00:00:00"
        elif re.search("\d{4}-\d{1,2}", date):
            return date + "-01 00:00:00"
        elif re.search("\d{4}", date):
            return date + "-01-01 00:00:00"
        else:
            return date

    def time_str_to_sec(self, time_str):
        time_sec = None
        iso_date_time = self.add_time(time_str)
        try:
            time_tup = time.strptime(iso_date_time, "%Y-%m-%d %H:%M:%S")
            time_sec = time.mktime(time_tup)
        except ValueError:
            from QuestionDialog import WarningDialog
            WarningDialog(_("Wrong format of date-time"),
                _("Only date-times in the iso format of yyyy-mm-dd "
                  "hh:mm:ss, where the time part is optional, are "
                  "accepted. %s does not satisfy.") % iso_date_time)
        return time_sec

    def prepare(self, db):
        self.since = None
        self.before = None
        if self.list[0]:
            self.since = self.time_str_to_sec(self.list[0])
        if self.list[1]:
            self.before = self.time_str_to_sec(self.list[1])

    def apply(self, db, obj):
        obj_time = obj.get_change_time()
        if self.since:
            if obj_time < self.since:
                return False
            if self.before:
                return obj_time < self.before
            return True
        if self.before:
            return obj_time < self.before
        return False
