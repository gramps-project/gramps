#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"""Tools/Database Processing/Find Possible Duplicate People"""

#-------------------------------------------------------------------------
#
# GNOME libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.lib import Event, Person
from gramps.gui.utils import ProgressMeter
from gramps.gui.plug import tool
from gramps.gen.soundex import soundex, compare
from gramps.gen.display.name import displayer as name_displayer
from gramps.gui.dialog import OkDialog
from gramps.gui.listmodel import ListModel
from gramps.gen.errors import WindowActiveError
from gramps.gui.merge import MergePerson
from gramps.gui.display import display_help
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.dialog import RunDatabaseRepair
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gui.glade import Glade

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_val2label = {
    0.25 : _("Low"),
    1.0  : _("Medium"),
    2.0  : _("High"),
    }

WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Find_Possible_Duplicate_People')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def is_initial(name):
    if len(name) > 2:
        return 0
    elif len(name) == 2:
        if name[0] == name[0].upper() and name[1] == '.':
            return 1
    else:
        return name[0] == name[0].upper()

#-------------------------------------------------------------------------
#
# The Actual tool.
#
#-------------------------------------------------------------------------
class DuplicatePeopleTool(tool.Tool, ManagedWindow):

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate

        tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.__init__(self, uistate, [],
                                             self.__class__)
        self.dbstate = dbstate
        self.uistate = uistate
        self.map = {}
        self.list = []
        self.index = 0
        self.merger = None
        self.mergee = None
        self.removed = {}
        self.update = callback
        self.use_soundex = 1

        top = Glade(toplevel="finddupes", also_load=["liststore1"])

        # retrieve options
        threshold = self.options.handler.options_dict['threshold']
        use_soundex = self.options.handler.options_dict['soundex']

        my_menu = Gtk.ListStore(str, object)
        for val in sorted(_val2label):
            my_menu.append([_val2label[val], val])

        self.soundex_obj = top.get_object("soundex")
        self.soundex_obj.set_active(use_soundex)
        self.soundex_obj.show()

        self.menu = top.get_object("menu")
        self.menu.set_model(my_menu)
        self.menu.set_active(0)

        window = top.toplevel
        self.set_window(window, top.get_object('title'),
                        _('Find Possible Duplicate People'))
        self.setup_configs('interface.duplicatepeopletool', 350, 220)

        top.connect_signals({
            "on_do_merge_clicked"   : self.__dummy,
            "on_help_show_clicked"  : self.__dummy,
            "on_delete_show_event"  : self.__dummy,
            "on_merge_ok_clicked"   : self.on_merge_ok_clicked,
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_delete_merge_event" : self.close,
            "on_delete_event"       : self.close,
            })

        self.show()

    def build_menu_names(self, obj):
        return (_("Tool settings"),_("Find Duplicates tool"))

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""

        display_help(WIKI_HELP_PAGE , WIKI_HELP_SEC)

    def ancestors_of(self, p1_id, id_list):
        if (not p1_id) or (p1_id in id_list):
            return
        id_list.append(p1_id)
        p1 = self.db.get_person_from_handle(p1_id)
        f1_id = p1.get_main_parents_family_handle()
        if f1_id:
            f1 = self.db.get_family_from_handle(f1_id)
            self.ancestors_of(f1.get_father_handle(),id_list)
            self.ancestors_of(f1.get_mother_handle(),id_list)

    def on_merge_ok_clicked(self, obj):
        threshold = self.menu.get_model()[self.menu.get_active()][1]
        self.use_soundex = int(self.soundex_obj.get_active())
        try:
            self.find_potentials(threshold)
        except AttributeError as msg:
            RunDatabaseRepair(str(msg), parent=self.window)
            return

        self.options.handler.options_dict['threshold'] = threshold
        self.options.handler.options_dict['soundex'] = self.use_soundex
        # Save options
        self.options.handler.save_options()

        if len(self.map) == 0:
            OkDialog(
                _("No matches found"),
                _("No potential duplicate people were found"),
                parent=self.window)
        else:
            try:
                DuplicatePeopleToolMatches(self.dbstate, self.uistate,
                                           self.track, self.list, self.map,
                                           self.update)
            except WindowActiveError:
                pass

    def find_potentials(self, thresh):
        self.progress = ProgressMeter(_('Find Duplicates'),
                                      _('Looking for duplicate people'),
                                      parent=self.window)

        index = 0
        males = {}
        females = {}

        length = self.db.get_number_of_people()

        self.progress.set_pass(_('Pass 1: Building preliminary lists'),
                               length)

        for p1_id in self.db.iter_person_handles():
            self.progress.step()
            p1 = self.db.get_person_from_handle(p1_id)
            key = self.gen_key(get_surnames(p1.get_primary_name()))
            if p1.get_gender() == Person.MALE:
                if key in males:
                    males[key].append(p1_id)
                else:
                    males[key] = [p1_id]
            else:
                if key in females:
                    females[key].append(p1_id)
                else:
                    females[key] = [p1_id]

        self.progress.set_pass(_('Pass 2: Calculating potential matches'),
                               length)

        for p1key in self.db.iter_person_handles():
            self.progress.step()
            p1 = self.db.get_person_from_handle(p1key)

            key = self.gen_key(get_surnames(p1.get_primary_name()))
            if p1.get_gender() == Person.MALE:
                remaining = males[key]
            else:
                remaining = females[key]

            #index = 0
            for p2key in remaining:
                #index += 1
                if p1key == p2key:
                    continue
                p2 = self.db.get_person_from_handle(p2key)
                if p2key in self.map:
                    (v,c) = self.map[p2key]
                    if v == p1key:
                        continue

                chance = self.compare_people(p1,p2)
                if chance >= thresh:
                    if p1key in self.map:
                        val = self.map[p1key]
                        if val[1] > chance:
                            self.map[p1key] = (p2key,chance)
                    else:
                        self.map[p1key] = (p2key,chance)

        self.list = sorted(self.map)
        self.length = len(self.list)
        self.progress.close()

    def gen_key(self, val):
        if self.use_soundex:
            try:
                return soundex(val)
            except UnicodeEncodeError:
                return val
        else:
            return val

    def compare_people(self, p1, p2):

        name1 = p1.get_primary_name()
        name2 = p2.get_primary_name()

        chance = self.name_match(name1, name2)
        if chance == -1  :
            return -1

        birth1_ref = p1.get_birth_ref()
        if birth1_ref:
            birth1 = self.db.get_event_from_handle(birth1_ref.ref)
        else:
            birth1 = Event()

        death1_ref = p1.get_death_ref()
        if death1_ref:
            death1 = self.db.get_event_from_handle(death1_ref.ref)
        else:
            death1 = Event()

        birth2_ref = p2.get_birth_ref()
        if birth2_ref:
            birth2 = self.db.get_event_from_handle(birth2_ref.ref)
        else:
            birth2 = Event()

        death2_ref = p2.get_death_ref()
        if death2_ref:
            death2 = self.db.get_event_from_handle(death2_ref.ref)
        else:
            death2 = Event()

        value = self.date_match(birth1.get_date_object(),
                                birth2.get_date_object())
        if value == -1 :
            return -1
        chance += value

        value = self.date_match(death1.get_date_object(),
                                death2.get_date_object())
        if value == -1 :
            return -1
        chance += value

        value = self.place_match(birth1.get_place_handle(),
                                 birth2.get_place_handle())
        if value == -1 :
            return -1
        chance += value

        value = self.place_match(death1.get_place_handle(),
                                 death2.get_place_handle())
        if value == -1 :
            return -1
        chance += value

        ancestors = []
        self.ancestors_of(p1.get_handle(),ancestors)
        if p2.get_handle() in ancestors:
            return -1

        ancestors = []
        self.ancestors_of(p2.get_handle(),ancestors)
        if p1.get_handle() in ancestors:
            return -1

        f1_id = p1.get_main_parents_family_handle()
        f2_id = p2.get_main_parents_family_handle()

        if f1_id and f2_id:
            f1 = self.db.get_family_from_handle(f1_id)
            f2 = self.db.get_family_from_handle(f2_id)
            dad1_id = f1.get_father_handle()
            if dad1_id:
                dad1 = get_name_obj(self.db.get_person_from_handle(dad1_id))
            else:
                dad1 = None
            dad2_id = f2.get_father_handle()
            if dad2_id:
                dad2 = get_name_obj(self.db.get_person_from_handle(dad2_id))
            else:
                dad2 = None

            value = self.name_match(dad1,dad2)

            if value == -1:
                return -1

            chance += value

            mom1_id = f1.get_mother_handle()
            if mom1_id:
                mom1 = get_name_obj(self.db.get_person_from_handle(mom1_id))
            else:
                mom1 = None
            mom2_id = f2.get_mother_handle()
            if mom2_id:
                mom2 = get_name_obj(self.db.get_person_from_handle(mom2_id))
            else:
                mom2 = None

            value = self.name_match(mom1,mom2)
            if value == -1:
                return -1

            chance += value

        for f1_id in p1.get_family_handle_list():
            f1 = self.db.get_family_from_handle(f1_id)
            for f2_id in p2.get_family_handle_list():
                f2 = self.db.get_family_from_handle(f2_id)
                if p1.get_gender() == Person.FEMALE:
                    father1_id = f1.get_father_handle()
                    father2_id = f2.get_father_handle()
                    if father1_id and father2_id:
                        if father1_id == father2_id:
                            chance += 1
                        else:
                            father1 = self.db.get_person_from_handle(father1_id)
                            father2 = self.db.get_person_from_handle(father2_id)
                            fname1 = get_name_obj(father1)
                            fname2 = get_name_obj(father2)
                            value = self.name_match(fname1,fname2)
                            if value != -1:
                                chance += value
                else:
                    mother1_id = f1.get_mother_handle()
                    mother2_id = f2.get_mother_handle()
                    if mother1_id and mother2_id:
                        if mother1_id == mother2_id:
                            chance += 1
                        else:
                            mother1 = self.db.get_person_from_handle(mother1_id)
                            mother2 = self.db.get_person_from_handle(mother2_id)
                            mname1 = get_name_obj(mother1)
                            mname2 = get_name_obj(mother2)
                            value = self.name_match(mname1,mname2)
                            if value != -1:
                                chance += value
        return chance

    def name_compare(self, s1, s2):
        if self.use_soundex:
            try:
                return compare(s1,s2)
            except UnicodeEncodeError:
                return s1 == s2
        else:
            return s1 == s2

    def date_match(self, date1, date2):
        if date1.is_empty() or date2.is_empty():
            return 0
        if date1.is_equal(date2):
            return 1

        if date1.is_compound() or date2.is_compound():
            return self.range_compare(date1,date2)

        if date1.get_year() == date2.get_year():
            if date1.get_month() == date2.get_month():
                return 0.75
            if not date1.get_month_valid() or not date2.get_month_valid():
                return 0.75
            else:
                return -1
        else:
            return -1

    def range_compare(self, date1, date2):
        start_date_1 = date1.get_start_date()[0:3]
        start_date_2 = date2.get_start_date()[0:3]
        stop_date_1 = date1.get_stop_date()[0:3]
        stop_date_2 = date2.get_stop_date()[0:3]
        if date1.is_compound() and date2.is_compound():
            if (start_date_2 <= start_date_1 <= stop_date_2 or
                start_date_1 <= start_date_2 <= stop_date_1 or
                start_date_2 <= stop_date_1 <= stop_date_2 or
                start_date_1 <= stop_date_2 <= stop_date_1):
                return 0.5
            else:
                return -1
        elif date2.is_compound():
            if start_date_2 <= start_date_1 <= stop_date_2:
                return 0.5
            else:
                return -1
        else:
            if start_date_1 <= start_date_2 <= stop_date_1:
                return 0.5
            else:
                return -1

    def name_match(self, name, name1):

        if not name1 or not name:
            return 0

        srn1 = get_surnames(name)
        sfx1 = name.get_suffix()
        srn2 = get_surnames(name1)
        sfx2 = name1.get_suffix()

        if not self.name_compare(srn1,srn2):
            return -1
        if sfx1 != sfx2:
            if sfx1 != "" and sfx2 != "":
                return -1

        if name.get_first_name() == name1.get_first_name():
            return 1
        else:
            list1 = name.get_first_name().split()
            list2 = name1.get_first_name().split()

            if len(list1) < len(list2):
                return self.list_reduce(list1,list2)
            else:
                return self.list_reduce(list2,list1)

    def place_match(self, p1_id, p2_id):
        if p1_id == p2_id:
            return 1

        if not p1_id:
            name1 = ""
        else:
            p1 = self.db.get_place_from_handle(p1_id)
            name1 = p1.get_title()

        if not p2_id:
            name2 = ""
        else:
            p2 = self.db.get_place_from_handle(p2_id)
            name2 = p2.get_title()

        if not (name1 and name2):
            return 0
        if name1 == name2:
            return 1

        list1 = name1.replace(","," ").split()
        list2 = name2.replace(","," ").split()

        value = 0
        for name in list1:
            for name2 in list2:
                if name == name2:
                    value += 0.5
                elif name[0] == name2[0] and self.name_compare(name, name2):
                    value += 0.25
        return min(value,1) if value else -1

    def list_reduce(self, list1, list2):
        value = 0
        for name in list1:
            for name2 in list2:
                if is_initial(name) and name[0] == name2[0]:
                    value += 0.25
                elif is_initial(name2) and name2[0] == name[0]:
                    value += 0.25
                elif name == name2:
                    value += 0.5
                elif name[0] == name2[0] and self.name_compare(name, name2):
                    value += 0.25
        return min(value,1) if value else -1

    def __dummy(self, obj):
        """dummy callback, needed because a shared glade file is used for
        both toplevel windows and all signals must be handled.
        """
        pass


class DuplicatePeopleToolMatches(ManagedWindow):

    def __init__(self, dbstate, uistate, track, the_list, the_map, callback):
        ManagedWindow.__init__(self,uistate,track,self.__class__)

        self.dellist = set()
        self.list = the_list
        self.map = the_map
        self.length = len(self.list)
        self.update = callback
        self.db = dbstate.db
        self.dbstate = dbstate
        self.uistate = uistate

        top = Glade(toplevel="mergelist")
        window = top.toplevel
        self.set_window(window, top.get_object('title'),
                        _('Potential Merges'))
        self.setup_configs('interface.duplicatepeopletoolmatches', 500, 350)

        self.mlist = top.get_object("mlist")
        top.connect_signals({
            "destroy_passed_object" : self.close,
            "on_do_merge_clicked"   : self.on_do_merge_clicked,
            "on_help_show_clicked"  : self.on_help_clicked,
            "on_delete_show_event"  : self.close,
            "on_merge_ok_clicked"   : self.__dummy,
            "on_help_clicked"       : self.__dummy,
            "on_delete_merge_event" : self.__dummy,
            "on_delete_event"       : self.__dummy,
            })
        self.db.connect("person-delete", self.person_delete)

        mtitles = [
                (_('Rating'),3,75),
                (_('First Person'),1,200),
                (_('Second Person'),2,200),
                ('',-1,0)
                ]
        self.list = ListModel(self.mlist,mtitles,
                              event_func=self.on_do_merge_clicked)

        self.redraw()
        self.show()

    def build_menu_names(self, obj):
        return (_("Merge candidates"), _("Merge persons"))

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""

        display_help(WIKI_HELP_PAGE , WIKI_HELP_SEC)
    def redraw(self):
        list = []
        for p1key, p1data in self.map.items():
            if p1key in self.dellist:
                continue
            (p2key,c) = p1data
            if p2key in self.dellist:
                continue
            if p1key == p2key:
                continue
            list.append((c,p1key,p2key))

        self.list.clear()
        for (c,p1key,p2key) in list:
            c1 = "%5.2f" % c
            c2 = "%5.2f" % (100-c)
            p1 = self.db.get_person_from_handle(p1key)
            p2 = self.db.get_person_from_handle(p2key)
            if not p1 or not p2:
                continue
            pn1 = name_displayer.display(p1)
            pn2 = name_displayer.display(p2)
            self.list.add([c1, pn1, pn2,c2],(p1key,p2key))

    def on_do_merge_clicked(self, obj):
        store,iter = self.list.selection.get_selected()
        if not iter:
            return

        (self.p1,self.p2) = self.list.get_object(iter)
        MergePerson(self.dbstate, self.uistate, self.track, self.p1, self.p2,
                    self.on_update, True)

    def on_update(self):
        if self.db.has_person_handle(self.p1):
            titanic = self.p2
        else:
            titanic = self.p1
        self.dellist.add(titanic)
        self.update()
        self.redraw()

    def update_and_destroy(self, obj):
        self.update(1)
        self.close()

    def person_delete(self, handle_list):
        """ deal with person deletes outside of the tool """
        self.dellist.update(handle_list)
        self.redraw()

    def __dummy(self, obj):
        """dummy callback, needed because a shared glade file is used for
        both toplevel windows and all signals must be handled.
        """
        pass


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def name_of(p):
    if not p:
        return ""
    return "%s (%s)" % (name_displayer.display(p),p.get_handle())

def get_name_obj(person):
    if person:
        return person.get_primary_name()
    else:
        return None

def get_surnames(name):
    """Construct a full surname of the surnames"""
    return ' '.join([surn.get_surname() for surn in name.get_surname_list()])

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class DuplicatePeopleToolOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        tool.ToolOptions.__init__(self, name,person_id)

        # Options specific for this report
        self.options_dict = {
            'soundex'   : 1,
            'threshold' : 0.25,
        }
        self.options_help = {
            'soundex'   : ("=0/1","Whether to use SoundEx codes",
                           ["Do not use SoundEx","Use SoundEx"],
                           True),
            'threshold' : ("=num","Threshold for tolerance",
                           "Floating point number")
            }
