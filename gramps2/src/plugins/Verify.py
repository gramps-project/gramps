#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
A plugin to verify the data against user-adjsted tests.
This is the research tool, not the low-level data ingerity check.
"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _
import cPickle

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk
import gtk.glade 

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import RelLib
import Utils
import GrampsDisplay
from ManagedWindow import ManagedWindow
from BasicUtils import UpdateCallback
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# temp storage and related functions
#
#-------------------------------------------------------------------------
_person_cache = {}
_family_cache = {}
_event_cache = {}

def find_event(db,handle):
    try:
        obj = _event_cache[handle]
    except KeyError:
        obj = db.get_event_from_handle(handle)
        _event_cache[handle] = obj
    return obj

def find_person(db,handle):
    try:
        obj = _person_cache[handle]
    except KeyError:
        obj = db.get_person_from_handle(handle)
        _person_cache[handle] = obj
    return obj

def find_family(db,handle):
    try:
        obj = _family_cache[handle]
    except KeyError:
        obj = db.get_family_from_handle(handle)
        _family_cache[handle] = obj
    return obj

def clear_cache():
    _person_cache.clear()
    _family_cache.clear()
    _event_cache.clear()   

#-------------------------------------------------------------------------
#
# helper functions
#
#-------------------------------------------------------------------------
def get_date_from_event_handle(db,event_handle):
    if not event_handle:
        return 0
    event =  find_event(db,event_handle)
    date_obj = event.get_date_object()
    return date_obj.get_sort_value()

def get_date_from_event_type(db,person,event_type):
    if not person:
        return 0
    for event_ref in person.get_event_ref_list():
        event = find_event(db,event_ref.ref)
        if event.get_type() == event_type:
            date_obj = event.get_date_object()
            return date_obj.get_sort_value()
    return 0

def get_bapt_date(db,person):
    return get_date_from_event_type(db,person,RelLib.EventType.BAPTISM)

def get_bury_date(db,person):
    return get_date_from_event_type(db,person,RelLib.EventType.BURIAL)

def get_birth_date(db,person,estimate=False):
    if not person:
        return 0
    birth_ref = person.get_birth_ref()
    if not birth_ref:
        ret = 0
    else:
        ret = get_date_from_event_handle(db,birth_ref.ref)
    if estimate and (ret == 0):
        ret = get_bapt_date(db,person)
    return ret

def get_death_date(db,person,estimate=False):
    if not person:
        return 0
    death_ref = person.get_death_ref()
    if not death_ref:
        ret = 0
    else:
        ret = get_date_from_event_handle(db,death_ref.ref)
    if estimate and (ret == 0):
        ret = get_bury_date(db,person)
    return ret

def get_age_at_death(db,person,estimate):
    birth_date = get_birth_date(db,person,estimate)
    death_date = get_death_date(db,person,estimate)
    if (birth_date > 0) and (death_date > 0):
        return death_date - birth_date
    return 0

def get_father(db,family):
    if not family:
        return None
    father_handle = family.get_father_handle()
    if father_handle:
        return find_person(db,father_handle)
    return None

def get_mother(db,family):
    if not family:
        return None
    mother_handle = family.get_mother_handle()
    if mother_handle:
        return find_person(db,mother_handle)
    return None

def get_child_birth_dates(db,family,estimate):
    dates = []
    for child_ref in family.get_child_ref_list():
        child = find_person(db,child_ref.ref)
        child_birth_date = get_birth_date(db,child,estimate)
        if child_birth_date > 0:
            dates.append(child_birth_date)
    return dates

def get_n_children(db,person):
    n = 0
    for family_handle in person.get_family_handle_list():
        family = find_family(db,family_handle)
        n += len(family.get_child_ref_list())

def get_marriage_date(db,family):
    if not family:
        return 0
    for event_ref in family.get_event_ref_list():
        event = find_event(db,event_ref.ref)
        if event.get_type() == RelLib.EventType.MARRIAGE:
            date_obj = event.get_date_object()
            return date_obj.get_sort_value()
    return 0

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------
class Verify(Tool.Tool, ManagedWindow, UpdateCallback):

    def __init__(self, dbstate, uistate, options_class, name,callback=None):
        self.label = _('Database Verify tool')
        Tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.__init__(self,uistate,[],self.__class__)
        UpdateCallback.__init__(self,self.uistate.pulse_progressbar)

        if uistate:
            self.init_gui()
        else:
            self.add_results = self.add_results_cli
            self.run_tool(cli=True)

    def add_results_cli(self,results):
        # print data for the user, no GUI
        (msg,gramps_id,name,the_type,rule_id,severity,handle) = results
        if severity == Rule.WARNING:
            print "W: %s, %s: %s, %s" % (msg,the_type,gramps_id,name)
        elif severity == Rule.ERROR:
            print "E: %s, %s: %s, %s" % (msg,the_type,gramps_id,name)

    def init_gui(self):
        # Draw dialog and make it handle everything
        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "verify.glade"

        self.top = gtk.glade.XML(self.glade_file,"verify_settings","gramps")
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_verify_ok_clicked"  : self.on_apply_clicked
        })

        window = self.top.get_widget('verify_settings')
        self.set_window(window,self.top.get_widget('title'),self.label)

        self.top.get_widget("oldage").set_value(
            self.options.handler.options_dict['oldage'])
        self.top.get_widget("hwdif").set_value(
            self.options.handler.options_dict['hwdif'])
        self.top.get_widget("cspace").set_value(
            self.options.handler.options_dict['cspace'])
        self.top.get_widget("cbspan").set_value(
            self.options.handler.options_dict['cbspan'])
        self.top.get_widget("yngmar").set_value(
            self.options.handler.options_dict['yngmar'])
        self.top.get_widget("oldmar").set_value(
            self.options.handler.options_dict['oldmar'])
        self.top.get_widget("oldmom").set_value(
            self.options.handler.options_dict['oldmom'])
        self.top.get_widget("yngmom").set_value(
            self.options.handler.options_dict['yngmom'])
        self.top.get_widget("olddad").set_value(
            self.options.handler.options_dict['olddad'])
        self.top.get_widget("yngdad").set_value(
            self.options.handler.options_dict['yngdad'])
        self.top.get_widget("wedder").set_value(
            self.options.handler.options_dict['wedder'])
        self.top.get_widget("mxchildmom").set_value(
            self.options.handler.options_dict['mxchildmom'])
        self.top.get_widget("mxchilddad").set_value(
            self.options.handler.options_dict['mxchilddad'])
        self.top.get_widget("lngwdw").set_value(
            self.options.handler.options_dict['lngwdw'])
        self.top.get_widget("oldunm").set_value(
            self.options.handler.options_dict['oldunm'])
        self.top.get_widget("estimate").set_active(
            self.options.handler.options_dict['estimate_age'])
                                                          
        self.show()

    def build_menu_names(self,obj):
        return (_("Tool settings"),self.label)

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-other')

    def on_apply_clicked(self,obj):
        self.options.handler.options_dict['oldage'] = self.top.get_widget(
            "oldage").get_value_as_int()
        self.options.handler.options_dict['hwdif']  = self.top.get_widget(
            "hwdif").get_value_as_int()
        self.options.handler.options_dict['cspace'] = self.top.get_widget(
            "cspace").get_value_as_int()
        self.options.handler.options_dict['cbspan'] = self.top.get_widget(
            "cbspan").get_value_as_int()
        self.options.handler.options_dict['yngmar'] = self.top.get_widget(
            "yngmar").get_value_as_int()
        self.options.handler.options_dict['oldmar'] = self.top.get_widget(
            "oldmar").get_value_as_int()
        self.options.handler.options_dict['oldmom'] = self.top.get_widget(
            "oldmom").get_value_as_int()
        self.options.handler.options_dict['yngmom'] = self.top.get_widget(
            "yngmom").get_value_as_int()
        self.options.handler.options_dict['olddad'] = self.top.get_widget(
            "olddad").get_value_as_int()
        self.options.handler.options_dict['yngdad'] = self.top.get_widget(
            "yngdad").get_value_as_int()
        self.options.handler.options_dict['wedder'] = self.top.get_widget(
            "wedder").get_value_as_int()
        self.options.handler.options_dict['mxchildmom'] = self.top.get_widget(
            "mxchildmom").get_value_as_int()
        self.options.handler.options_dict['mxchilddad'] = self.top.get_widget(
            "mxchilddad").get_value_as_int()
        self.options.handler.options_dict['lngwdw'] = self.top.get_widget(
            "lngwdw").get_value_as_int()
        self.options.handler.options_dict['oldunm'] = self.top.get_widget(
            "oldunm").get_value_as_int()

        self.options.handler.options_dict['estimate_age'] = \
                                                          self.top.get_widget(
            "estimate").get_active()

        # FIXME: Initialize trees and models for normal and hidden warnings
        # Then create a new class here, fill things
        vr = VerifyResults(self.uistate, self.track)

        self.add_results = vr.add_results
       
        self.uistate.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.uistate.progress.show()
        self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        vr.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        self.run_tool(cli=False)

        self.uistate.progress.hide()
        self.uistate.window.window.set_cursor(None)
        self.window.window.set_cursor(None)
        vr.window.window.set_cursor(None)
        
        # Save options
        self.options.handler.save_options()

    def load_ignored(self,filename):
        try:
            f = open(filename)
            self.ignores = cPickle.load(f)
            f.close()
            return True
        except IOError:
            return False

    def save_ignored(self,filename):
        try:
            f = open(filename,'w')
            cPickle.dump(self.ignores,f)
            f.close()
            return True
        except IOError:
            return False

    def run_tool(self,cli=False):

        person_handles = self.db.get_person_handles(sort_handles=False)
        oldage = self.options.handler.options_dict['oldage']
        hwdif = self.options.handler.options_dict['hwdif']
        cspace = self.options.handler.options_dict['cspace']
        cbspan = self.options.handler.options_dict['cbspan']
        yngmar = self.options.handler.options_dict['yngmar']
        oldmar = self.options.handler.options_dict['oldmar']
        oldmom = self.options.handler.options_dict['oldmom']
        yngmom = self.options.handler.options_dict['yngmom']
        olddad = self.options.handler.options_dict['olddad']
        yngdad = self.options.handler.options_dict['yngdad']
        wedder = self.options.handler.options_dict['wedder']
        mxchildmom = self.options.handler.options_dict['mxchildmom']
        mxchilddad = self.options.handler.options_dict['mxchilddad']
        lngwdw = self.options.handler.options_dict['lngwdw']
        oldunm = self.options.handler.options_dict['oldunm']
        estimate_age = self.options.handler.options_dict['estimate_age']


        self.set_total(self.db.get_number_of_people() +
                       self.db.get_number_of_families())

        for person_handle in person_handles:
            person = find_person(self.db,person_handle)

            rule_list = [
                BirthAfterBapt(self.db,person),
                DeathBeforeBapt(self.db,person),
                BirthAfterBury(self.db,person),
                DeathAfterBury(self.db,person),
                BirthAfterDeath(self.db,person),
                BaptAfterBury(self.db,person),
                OldAge(self.db,person,oldage,estimate_age),
                UnknownGender(self.db,person),
                MultipleParents(self.db,person),
                MarriedOften(self.db,person,wedder),
                OldUnmarried(self.db,person,oldunm,estimate_age),
                TooManyChildren(self.db,person,mxchilddad,mxchildmom),
                ]

            for rule in rule_list:
                if rule.broken():
                    self.add_results(rule.report_itself())            
                
            clear_cache()
            self.update()

        # Family-based rules
        for family_handle in self.db.get_family_handles():
            family = find_family(self.db,family_handle)

            rule_list = [
                SameSexFamily(self.db,family),
                FemaleHusband(self.db,family),
                MaleWife(self.db,family),
                SameSurnameFamily(self.db,family),
                LargeAgeGapFamily(self.db,family,hwdif,estimate_age),
                MarriageBeforeBirth(self.db,family,estimate_age),
                MarriageAfterDeath(self.db,family,estimate_age),
                EarlyMarriage(self.db,family,yngmar,estimate_age),
                LateMarriage(self.db,family,oldmar,estimate_age),
                OldParent(self.db,family,oldmom,olddad,estimate_age),
                YoungParent(self.db,family,yngmom,yngdad,estimate_age),
                UnbornParent(self.db,family,estimate_age),
                DeadParent(self.db,family,estimate_age),
                LargeChildrenSpan(self.db,family,cbspan,estimate_age),
                LargeChildrenAgeDiff(self.db,family,cspace,estimate_age),
                ]

            for rule in rule_list:
                if rule.broken():
                    self.add_results(rule.report_itself())            
                
            clear_cache()
            self.update()

#-------------------------------------------------------------------------
#
# Display the results
#
#-------------------------------------------------------------------------
class VerifyResults(ManagedWindow):
    def __init__(self,uistate,track):
        self.title = _('Database Verification Results')

        ManagedWindow.__init__(self,uistate,track,self.__class__)

        base = os.path.dirname(__file__)
        self.glade_file = base + os.sep + "verify.glade"

        self.top = gtk.glade.XML(self.glade_file,"verify_result","gramps")
        window = self.top.get_widget("verify_result")
        self.set_window(window,self.top.get_widget('title'),self.title)
    
        self.top.signal_autoconnect({
            "destroy_passed_object"  : self.close,
            })

        self.warn_model = gtk.ListStore(str,str,str,str,int,str,str)
        self.hide_model = gtk.ListStore(str,str,str,str,int,str,str)
        self.warn_tree = self.top.get_widget('warn_tree') 
        self.hide_tree = self.top.get_widget('hide_tree')
        self.warn_tree.set_model(self.warn_model)
        self.hide_tree.set_model(self.hide_model)

        self.renderer = gtk.CellRendererText()
        self.img_renderer = gtk.CellRendererPixbuf()
        
        self.img_column = gtk.TreeViewColumn(None, self.img_renderer )
        self.warn_tree.append_column(self.img_column)
        self.img_column.set_cell_data_func(self.img_renderer,self.get_image)

        self.warn_tree.append_column(
            gtk.TreeViewColumn(_('Warning'), self.renderer,
                               text=0,foreground=6))
        self.warn_tree.append_column(
            gtk.TreeViewColumn(_('ID'), self.renderer,
                               text=1,foreground=6))
        self.warn_tree.append_column(
            gtk.TreeViewColumn(_('Name'), self.renderer,
                               text=2,foreground=6))

        self.hide_tree.append_column(
            gtk.TreeViewColumn(_('Warning'), self.renderer,
                               text=0,foreground=6))
        self.hide_tree.append_column(
            gtk.TreeViewColumn(_('ID'), self.renderer,
                               text=1,foreground=6))
        self.hide_tree.append_column(
            gtk.TreeViewColumn(_('Name'), self.renderer,
                               text=2,foreground=6))

        self.window.show_all()
        self.window_shown = False

    def get_image(self, column, cell, model, iter, user_data=None):
        the_type = model.get_value(iter, 3)
        if the_type == 'Person':
            cell.set_property('stock-id', 'gramps-person' )
        elif  the_type == 'Family':
            cell.set_property('stock-id', 'gramps-family' )

    def add_results(self,results):
        (msg,gramps_id,name,the_type,rule_id,severity,handle) = results
        if severity == Rule.ERROR:
            fg = 'red'
##             fg = '#8b008b'
##         elif severity == Rule.WARNING:
##             fg = '#008b00'
        else:
            fg = None
        self.warn_model.append(row=[msg,gramps_id,name,
                                    the_type,rule_id,handle,fg])
        
        if not self.window_shown:
            self.show()
            self.window_shown = True

    def build_menu_names(self,obj):
        return (self.title,None)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class VerifyOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'oldage'       : 90,
            'hwdif'       : 30,
            'cspace'       : 8,
            'cbspan'       : 25,
            'yngmar'       : 17,
            'oldmar'       : 50,
            'oldmom'       : 48,
            'yngmom'       : 17,
            'yngdad'       : 18,
            'olddad'       : 65,
            'wedder'       : 3,
            'mxchildmom'   : 12,
            'mxchilddad'   : 15,
            'lngwdw'       : 30,
            'oldunm'       : 99,
            'estimate_age' : 0,
        }
        self.options_help = {
            'oldage'       : ("=num","Maximum age","Age in years"),
            'hwdif'       : ("=num","Maximum husband-wife age difference",
                              "Age difference in years"),
            'cspace'       : ("=num",
                              "Maximum number of years between children",
                              "Number of years"),
            'cbspan'       : ("=num",
                              "Maximum span of years for all children",
                              "Span in years"),
            'yngmar'       : ("=num","Minimum age to marry","Age in years"),
            'oldmar'       : ("=num","Maximum age to marry","Age in years"),
            'oldmom'       : ("=num","Maximum age to bear a child",
                              "Age in years"),
            'yngmom'       : ("=num","Minimum age to bear a child",
                              "Age in years"),
            'yngdad'       : ("=num","Minimum age to father a child",
                              "Age in years"),
            'olddad'       : ("=num","Maximum age to father a child",
                              "Age in years"),
            'wedder'       : ("=num","Maximum number of spouses for a person",
                              "Number of spouses"),
            'mxchildmom'   : ("=num","Maximum number of children for a woman",
                              "Number of children"),
            'mxchilddad'   : ("=num","Maximum  number of children for a man",
                              "Number of chidlren"),
            'lngwdw'       : ("=num","Maximum number of consecutive years "
                              "of widowhood before next marriage",
                              "Number of years"),
            'oldunm'       : ("=num","Maximum age for an unmarried person"
                              "Number of years"),
            'estimate_age' : ("=0/1","Whether to estimate missing dates",
                              ["Do not estimate","Estimate dates"],
                              True),
        }

#-------------------------------------------------------------------------
#
# Base classes for different tests -- the rules
#
#-------------------------------------------------------------------------
class Rule:
    """
    Basic class for use in this tool.

    Other rules must inherit from this.
    """
    ID = 0
    TYPE = ''
    
    ERROR   = 1
    WARNING = 2

    SEVERITY = WARNING

    def __init__(self,db,obj):
        self.db = db
        self.obj = obj

    def broken(self):
        """
        Return boolean indicating whether this rule is violated.
        """
        return False

    def get_message(self):
        assert False, "Need to be overriden in the derived class"

    def get_name(self):
        assert False, "Need to be overriden in the derived class"

    def get_handle(self):
        return self.obj.handle

    def get_id(self):
        return self.obj.gramps_id

    def get_level(self):
        return Rule.WARNING

    def report_itself(self):
        handle = self.get_handle()
        the_type = self.TYPE
        rule_id = self.ID
        severity = self.SEVERITY
        name = self.get_name()
        gramps_id = self.get_id()
        msg = self.get_message()
        return (msg,gramps_id,name,the_type,rule_id,severity,handle)

class PersonRule(Rule):
    """
    Person-based class.
    """
    TYPE = 'Person'
    def get_name(self):
        return self.obj.get_primary_name().get_name()

class FamilyRule(Rule):
    """
    Family-based class.
    """
    TYPE = 'Family'
    def get_name(self):
        return Utils.family_name(self.obj,self.db)

#-------------------------------------------------------------------------
#
# Actual rules for testing
#
#-------------------------------------------------------------------------
class BirthAfterBapt(PersonRule):
    ID = 1
    SEVERITY = Rule.ERROR
    def broken(self):
        birth_date = get_birth_date(self.db,self.obj)
        bapt_date = get_bapt_date(self.db,self.obj)
        birth_ok = birth_date > 0
        bapt_ok = bapt_date > 0
        birth_after_death = birth_date > bapt_date
        return (birth_ok and bapt_ok and birth_after_death)

    def get_message(self):
        return _("Baptism before birth")

class DeathBeforeBapt(PersonRule):
    ID = 2
    SEVERITY = Rule.ERROR
    def broken(self):
        death_date = get_death_date(self.db,self.obj)
        bapt_date = get_bapt_date(self.db,self.obj)
        bapt_ok = bapt_date > 0
        death_ok = death_date > 0
        death_before_bapt = bapt_date > death_date
        return (death_ok and bapt_ok and death_before_bapt)

    def get_message(self):
        return _("Death before baptism")

class BirthAfterBury(PersonRule):
    ID = 3
    SEVERITY = Rule.ERROR
    def broken(self):
        birth_date = get_birth_date(self.db,self.obj)
        bury_date = get_bury_date(self.db,self.obj)
        birth_ok = birth_date > 0
        bury_ok = bury_date > 0
        birth_after_bury = birth_date > bury_date
        return (birth_ok and bury_ok and birth_after_bury)

    def get_message(self):
        return _("Burial before birth")

class DeathAfterBury(PersonRule):
    ID = 4
    SEVERITY = Rule.ERROR
    def broken(self):
        death_date = get_death_date(self.db,self.obj)
        bury_date = get_bury_date(self.db,self.obj)
        death_ok = death_date > 0
        bury_ok = bury_date > 0
        death_after_bury = death_date > bury_date
        return (death_ok and bury_ok and death_after_bury)

    def get_message(self):
        return _("Burial before death")

class BirthAfterDeath(PersonRule):
    ID = 5
    SEVERITY = Rule.ERROR
    def broken(self):
        birth_date = get_birth_date(self.db,self.obj)
        death_date = get_death_date(self.db,self.obj)
        birth_ok = birth_date > 0
        death_ok = death_date > 0
        birth_after_death = birth_date > death_date
        return (birth_ok and death_ok and birth_after_death)

    def get_message(self):
        return _("Death before birth")

class BaptAfterBury(PersonRule):
    ID = 6
    SEVERITY = Rule.ERROR
    def broken(self):
        bapt_date = get_bapt_date(self.db,self.obj)
        bury_date = get_bury_date(self.db,self.obj)
        bapt_ok = bapt_date > 0
        bury_ok = bury_date > 0
        bapt_after_bury = bapt_date > bury_date
        return (bapt_ok and bury_ok and bapt_after_bury)

    def get_message(self):
        return _("Burial before baptism")

class OldAge(PersonRule):
    ID = 7
    SEVERITY = Rule.WARNING
    def __init__(self,db,person,old_age,est):
        PersonRule.__init__(self,db,person)
        self.old_age = old_age
        self.est = est

    def broken(self):
        age_at_death = get_age_at_death(self.db,self.obj,self.est)
        return (age_at_death > self.old_age)

    def get_message(self):
        return _("Old age at death")

class UnknownGender(PersonRule):
    ID = 8
    SEVERITY = Rule.WARNING
    def broken(self):
        female = self.obj.get_gender() == RelLib.Person.FEMALE
        male = self.obj.get_gender() == RelLib.Person.MALE
        return (male or female)

    def get_message(self):
        return _("Unknown gender")

class MultipleParents(PersonRule):
    ID = 9
    SEVERITY = Rule.WARNING
    def broken(self):
        n_parent_sets = len(self.obj.get_parent_family_handle_list())
        return (n_parent_sets>1)

    def get_message(self):
        return _("Multiple parents")

class MarriedOften(PersonRule):
    ID = 10
    SEVERITY = Rule.WARNING
    def __init__(self,db,person,wedder):
        PersonRule.__init__(self,db,person)
        self.wedder = wedder

    def broken(self):
        n_spouses = len(self.obj.get_family_handle_list())
        return (n_spouses>self.wedder)

    def get_message(self):
        return _("Married often")

class OldUnmarried(PersonRule):
    ID = 11
    SEVERITY = Rule.WARNING
    def __init__(self,db,person,old_unm,est):
        PersonRule.__init__(self,db,person)
        self.old_unm = old_unm
        self.est = est

    def broken(self):
        age_at_death = get_age_at_death(self.db,self.obj,self.est)
        n_spouses = len(self.obj.get_family_handle_list())
        return (age_at_death>self.old_unm and n_spouses==0)

    def get_message(self):
        return _("Old and unmarried")

class TooManyChildren(PersonRule):
    ID = 12
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,mx_child_dad,mx_child_mom):
        PersonRule.__init__(self,db,obj)
        self.mx_child_dad = mx_child_dad
        self.mx_child_mom = mx_child_mom

    def broken(self):
        n_child = get_n_children(self.db,self.obj)

        if (self.obj.get_gender == RelLib.Person.MALE) \
               and (n_child > self.mx_child_dad):
            return True

        if (self.obj.get_gender == RelLib.Person.FEMALE) \
               and (n_child > self.mx_child_mom):
            return True

        return False

    def get_message(self):
        return _("Too many children")

class SameSexFamily(FamilyRule):
    ID = 13
    SEVERITY = Rule.WARNING
    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        same_sex = (mother and father and
                    (mother.get_gender() == father.get_gender()))
        unknown_sex = (mother and
                       (mother.get_gender() == RelLib.Person.UNKNOWN))
        return (same_sex and not unknown_sex)

    def get_message(self):
        return _("Same sex marriage")

class FemaleHusband(FamilyRule):
    ID = 14
    SEVERITY = Rule.WARNING
    def broken(self):
        father = get_father(self.db,self.obj)
        return (father and (father.get_gender() == RelLib.Person.FEMALE))

    def get_message(self):
        return _("Female husband")

class MaleWife(FamilyRule):
    ID = 15
    SEVERITY = Rule.WARNING
    def broken(self):
        mother = get_mother(self.db,self.obj)
        return (mother and (mother.get_gender() == RelLib.Person.MALE))

    def get_message(self):
        return _("Male wife")

class SameSurnameFamily(FamilyRule):
    ID = 16
    SEVERITY = Rule.WARNING
    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        same_surname = (father and mother and
                        (mother.get_primary_name().get_surname() ==
                         father.get_primary_name().get_surname()))
        empty_surname = mother and \
                        (len(mother.get_primary_name().get_surname())==0)
        return (same_surname and not empty_surname)

    def get_message(self):
        return _("Husband and wife with the same surname")

class LargeAgeGapFamily(FamilyRule):
    ID = 17
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,hw_diff,est):
        FamilyRule.__init__(self,db,obj)
        self.hw_diff = hw_diff
        self.est = est

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother,self.est)
        father_birth_date = get_birth_date(self.db,father,self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0
        large_diff = abs(father_birth_date-mother_birth_date) > self.hw_diff
        return (mother_birth_date_ok and father_birth_date_ok and large_diff)

    def get_message(self):
        return _("Large age difference between spouses")

class MarriageBeforeBirth(FamilyRule):
    ID = 18
    SEVERITY = Rule.ERROR
    def __init__(self,db,obj,est):
        FamilyRule.__init__(self,db,obj)
        self.est = est

    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother,self.est)
        father_birth_date = get_birth_date(self.db,father,self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (father_birth_date_ok and marr_date_ok
                         and (father_birth_date > marr_date))
        mother_broken = (mother_birth_date_ok and marr_date_ok
                         and (mother_birth_date > marr_date))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Marriage before birth")

class MarriageAfterDeath(FamilyRule):
    ID = 19
    SEVERITY = Rule.ERROR
    def __init__(self,db,obj,est):
        FamilyRule.__init__(self,db,obj)
        self.est = est

    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_death_date = get_death_date(self.db,mother,self.est)
        father_death_date = get_death_date(self.db,father,self.est)
        mother_death_date_ok = mother_death_date > 0
        father_death_date_ok = father_death_date > 0

        father_broken = (father_death_date_ok and marr_date_ok
                         and (father_death_date > marr_date))
        mother_broken = (mother_death_date_ok and marr_date_ok
                         and (mother_death_date > marr_date))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Marriage after death")

class EarlyMarriage(FamilyRule):
    ID = 20
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,yng_mar,est):
        FamilyRule.__init__(self,db,obj)
        self.yng_mar = yng_mar
        self.est = est

    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother,self.est)
        father_birth_date = get_birth_date(self.db,father,self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (father_birth_date_ok and marr_date_ok
                         and (marr_date - father_birth_date < self.yng_mar))
        mother_broken = (mother_birth_date_ok and marr_date_ok
                         and (marr_date - mother_birth_date < self.yng_mar))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Early marriage")

class LateMarriage(FamilyRule):
    ID = 21
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,old_mar,est):
        FamilyRule.__init__(self,db,obj)
        self.old_mar = old_mar
        self.est = est

    def broken(self):
        marr_date = get_marriage_date(self.db,self.obj)
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother,self.est)
        father_birth_date = get_birth_date(self.db,father,self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (father_birth_date_ok and marr_date_ok
                         and (marr_date - father_birth_date > self.old_mar))
        mother_broken = (mother_birth_date_ok and marr_date_ok
                         and (marr_date - mother_birth_date > self.old_mar))

        return (father_broken or mother_broken)

    def get_message(self):
        return _("Late marriage")

## class MarriageBeforePrefiousMarrChild(PersonRule):
##     def broken(self):
##         marr_date = get_marriage_date(self.obj)
##         prev_marr_child_date = get_prev_marr_child_date(self.obj)
##         return (prev_marr_child_date>marr_date)

##     def get_message(self):
##         return _("Marriage before having a child from previous marriage")

## class LongWidowhood(FamilyRule):
##     def broken(self):
##         marr_date = get_marriage_date(self.obj)
##         prev_marr_spouse_death_date = get_prev_marr_spouse_death_date(self.obj)
##         birth_date = get_birth_date(self.obj)
##         return (marr_date-prev_marr_spouse_death_date>lngwdw)

##     def get_message(self):
##         return _("Long Windowhood")

class OldParent(FamilyRule):
    ID = 22
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,old_mom,old_dad,est):
        FamilyRule.__init__(self,db,obj)
        self.old_mom = old_mom
        self.old_dad = old_dad
        self.est = est

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother,self.est)
        father_birth_date = get_birth_date(self.db,father,self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child,self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_birth_date_ok and (
                father_birth_date - child_birth_date > self.old_dad))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_birth_date_ok and (
                mother_birth_date - child_birth_date > self.old_mom))
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        return _("Old father")

    def mother_message(self):
        return _("Old mother")

class YoungParent(FamilyRule):
    ID = 23
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,yng_mom,yng_dad,est):
        FamilyRule.__init__(self,db,obj)
        self.yng_dad = yng_dad
        self.yng_mom = yng_mom
        self.est = est

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother,self.est)
        father_birth_date = get_birth_date(self.db,father,self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child,self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_birth_date_ok and (
                father_birth_date - child_birth_date < self.yng_dad))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_birth_date_ok and (
                mother_birth_date - child_birth_date < self.yng_mom))
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        return _("Young father")

    def mother_message(self):
        return _("Young mother")

class UnbornParent(FamilyRule):
    ID = 24
    SEVERITY = Rule.ERROR
    def __init__(self,db,obj,est):
        FamilyRule.__init__(self,db,obj)
        self.est = est

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_birth_date = get_birth_date(self.db,mother,self.est)
        father_birth_date = get_birth_date(self.db,father,self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child,self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_birth_date_ok
                             and (father_birth_date > child_birth_date))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_birth_date_ok
                             and (mother_birth_date > child_birth_date))
            if mother_broken:
                self.get_message = self.mother_message
                return True

    def father_message(self):
        return _("Unborn father")

    def mother_message(self):
        return _("Unborn mother")

class DeadParent(FamilyRule):
    ID = 25
    SEVERITY = Rule.ERROR
    def __init__(self,db,obj,est):
        FamilyRule.__init__(self,db,obj)
        self.est = est

    def broken(self):
        mother = get_mother(self.db,self.obj)
        father = get_father(self.db,self.obj)
        mother_death_date = get_death_date(self.db,mother,self.est)
        father_death_date = get_death_date(self.db,father,self.est)
        mother_death_date_ok = mother_death_date > 0
        father_death_date_ok = father_death_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db,child_ref.ref)
            child_birth_date = get_birth_date(self.db,child,self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = (father_death_date_ok
                             and (father_death_date < child_birth_date))
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (mother_death_date_ok
                             and (mother_death_date < child_birth_date))
            if mother_broken:
                self.get_message = self.mother_message
                return True

    def father_message(self):
        return _("Dead father")

    def mother_message(self):
        return _("Dead mother")

class LargeChildrenSpan(FamilyRule):
    ID = 26
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,cb_span,est):
        FamilyRule.__init__(self,db,obj)
        self.cb_span = cb_span
        self.est = est

    def broken(self):
        child_birh_dates = get_child_birth_dates(self.db,self.obj,self.est)
        child_birh_dates.sort()
        
        return (child_birh_dates and
                (child_birh_dates[-1] - child_birh_dates[0] > self.cb_span))

    def get_message(self):
        return _("Large year span for all children")

class LargeChildrenAgeDiff(FamilyRule):
    ID = 27
    SEVERITY = Rule.WARNING
    def __init__(self,db,obj,c_space,est):
        FamilyRule.__init__(self,db,obj)
        self.c_space = c_space
        self.est = est

    def broken(self):
        child_birh_dates = get_child_birth_dates(self.db,self.obj,self.est)
        child_birh_dates_diff = [child_birh_dates[i+1] - child_birh_dates[i]
                                 for i in range(len(child_birh_dates)-1) ]
        
        return (child_birh_dates_diff and
                max(child_birh_dates_diff) < self.c_space)

    def get_message(self):
        return _("Large age differences between children")

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_tool(
    name = 'verify',
    category = Tool.TOOL_UTILS,
    tool_class = Verify,
    options_class = VerifyOptions,
    modes = Tool.MODE_GUI | Tool.MODE_CLI,
    translated_name = _("Verify the database"),
    description = _("Lists exceptions to assertions or checks "
                    "about the database")
    )
