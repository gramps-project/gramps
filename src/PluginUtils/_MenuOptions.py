#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
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
# $Id: _MenuOptions.py 9422 2007-11-28 22:21:18Z dsblank $

"""
Abstracted option handling.
"""
#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gtk
import gobject
import Utils
import _Tool as Tool
import GrampsWidgets
import ManagedWindow
from Selectors import selector_factory
from BasicUtils import name_displayer as _nd

#------------------------------------------------------------------------
#
# Dialog window used to select a surname
#
#------------------------------------------------------------------------
class LastNameDialog(ManagedWindow.ManagedWindow):

    def __init__(self, database, uistate, track, surnames, skipList=set()):

        self.title = _('Select surname')
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)
        self.dlg = gtk.Dialog(
            None,
            uistate.window,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_window(self.dlg, None, self.title)
        self.window.set_default_size(400,400)

        # build up a container to display all of the people of interest
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        self.treeView = gtk.TreeView(self.model)
        col1 = gtk.TreeViewColumn(_('Surname'), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('Count'), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.treeView.append_column(col1)
        self.treeView.append_column(col2)
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add(self.treeView)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledWindow.set_shadow_type(gtk.SHADOW_OUT)
        self.dlg.vbox.pack_start(self.scrolledWindow, expand=True, fill=True)
        self.scrolledWindow.show_all()

        if len(surnames) == 0:
            # we could use database.get_surname_list(), but if we do that
            # all we get is a list of names without a count...therefore
            # we'll traverse the entire database ourself and build up a
            # list that we can use
#            for name in database.get_surname_list():
#                self.model.append([name, 0])

            # build up the list of surnames, keeping track of the count for each name
            # (this can be a lengthy process, so by passing in the dictionary we can
            # be certain we only do this once)
            progress = Utils.ProgressMeter(_('Finding surnames'))
            progress.set_pass(_('Finding surnames'), database.get_number_of_people())
            for personHandle in database.get_person_handles(False):
                progress.step()
                person = database.get_person_from_handle(personHandle)
                key = person.get_primary_name().get_surname()
                count = 0
                if key in surnames:
                    count = surnames[key]
                surnames[key] = count + 1
            progress.close()

        # insert the names and count into the model
        for key in surnames:
            if key.encode('iso-8859-1','xmlcharrefreplace') not in skipList:
                self.model.append([key, surnames[key]])

        # keep the list sorted starting with the most popular last name
        self.model.set_sort_column_id(1, gtk.SORT_DESCENDING)

        # the "OK" button should be enabled/disabled based on the selection of a row
        self.treeSelection = self.treeView.get_selection()
        self.treeSelection.set_mode(gtk.SELECTION_MULTIPLE)
        self.treeSelection.select_path(0)

    def run(self):
        response = self.dlg.run()
        surnameSet = set()
        if response == gtk.RESPONSE_ACCEPT:
            (mode, paths) = self.treeSelection.get_selected_rows()
            for path in paths:
                iter = self.model.get_iter(path)
                surname = self.model.get_value(iter, 0)
                surnameSet.add(surname)
        self.dlg.destroy()
        return surnameSet

#-------------------------------------------------------------------------
#
# Option class
#
#-------------------------------------------------------------------------
class Option:
    """
    This class serves as a base class for all options. All Options must 
    minimally provide the services provided by this class. Options are allowed 
    to add additional functionality.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @param value: An initial value for this option.
            Example: True
        @type value: The type will depend on the type of option.
        @return: nothing
        """
        self.__value = value
        self.__label = label
        self.__help_str = ""
        
    def get_label(self):
        """
        Get the friendly label for this option.
        
        @return: string
        """
        return self.__label
    
    def set_label(self,label):
        """
        Set the friendly label for this option.
        
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @return: nothing
        """
        self.__label = label
        
    def get_value(self):
        """
        Get the value of this option.
        
        @return: The option value.
        """
        return self.__value
    
    def set_value(self,value):
        """
        Set the value of this option.
        
        @param value: A value for this option.
            Example: True
        @type value: The type will depend on the type of option.
        @return: nothing
        """
        self.__value = value
        
    def get_help(self):
        """
        Get the help information for this option.
        
        @return: A string that provides additional help beyond the label.
        """
        return self.__help_str
        
    def set_help(self,help):
        """
        Set the help information for this option.
        
        @param help: A string that provides additional help beyond the label.
            Example: "Whether to include or exclude people who are calculated 
            to be alive at the time of the generation of this report"
        @type value: string
        @return: nothing
        """
        self.__help_str = help

    def add_dialog_category(self, dialog, category):
        """
        Add the GUI object to the dialog on the appropriate tab.
        """
        dialog.add_frame_option(category, self.get_label(), self.gobj)

    def add_tooltip(self, tooltip):
        """
        Add the option's help to the GUI object.
        """
        tooltip.set_tip(self.gobj, self.get_help())
        
        
#-------------------------------------------------------------------------
#
# StringOption class
#
#-------------------------------------------------------------------------
class StringOption(Option):
    """
    This class describes an option that is a simple one-line string.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Page header"
        @type label: string
        @param value: An initial value for this option.
            Example: "Generated by GRAMPS"
        @type value: string
        @return: nothing
        """
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a StringOption (single line text) to the dialog.
        """
        value = self.get_value()
        self.gobj = gtk.Entry()
        self.gobj.set_text(value)

    def parse(self):
        """
        Parse the string option (single line text).
        """
        return self.gobj.get_text()

#-------------------------------------------------------------------------
#
# ColourButtonOption class
#
#-------------------------------------------------------------------------
class ColourButtonOption(Option):
    """
    This class describes an option that allows the selection of a colour.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Males"
        @type label: string
        @param value: An initial value for this option.
            Example: "#ff00a0"
        @type value: string, interpreted as a colour by gtk.gdk.color_parse()
        @return: nothing
        """
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a ColorButton to the dialog.
        """
        value = self.get_value()
        self.gobj = gtk.ColorButton(gtk.gdk.color_parse(value))

    def parse(self):
        """
        Parse the colour and return as a string.
        """
        colour = self.gobj.get_color()
        value = '#%02x%02x%02x' % (
            int(colour.red      * 256 / 65536),
            int(colour.green    * 256 / 65536),
            int(colour.blue     * 256 / 65536))
        return value

#-------------------------------------------------------------------------
#
# NumberOption class
#
#-------------------------------------------------------------------------
class NumberOption(Option):
    """
    This class describes an option that is a simple number with defined maximum 
    and minimum values.
    """
    def __init__(self,label,value,min,max):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Number of generations to include"
        @type label: string
        @param value: An initial value for this option.
            Example: 5
        @type value: int
        @param min: The minimum value for this option.
            Example: 1
        @type min: int
        @param max: The maximum value for this option.
            Example: 10
        @type value: int
        @return: nothing
        """
        Option.__init__(self,label,value)
        self.__min = min
        self.__max = max
    
    def get_min(self):
        """
        Get the minimum value for this option.
        
        @return: an int that represents the minimum value for this option.
        """
        return self.__min
    
    def get_max(self):
        """
        Get the maximum value for this option.
        
        @return: an int that represents the maximum value for this option.
        """
        return self.__max

    def make_gui_obj(self, gtk, dialog):
        """
        Add a NumberOption to the dialog.
        """
        value = self.get_value()
        adj = gtk.Adjustment(1,self.get_min(),self.get_max(),1)

        self.gobj = gtk.SpinButton(adj)
        self.gobj.set_value(value)

    def parse(self):
        """
        Parse the object and return.
        """
        return int(self.gobj.get_value_as_int())
                

#-------------------------------------------------------------------------
#
# FloatOption class
#
#-------------------------------------------------------------------------
class FloatOption(NumberOption):
    """
    This class performs like NumberOption, but allows for float values
    for the minimum/maximum/increment.
    """
    def __init__(self, label, value, min, max):
        # Someone who knows python better than I will probably
        # want to add a parameter for the caller to specify how
        # many decimal points are needed.
        #
        # At the time this function was written, the only code
        # that needed this class required 2 decimals.
        NumberOption.__init__(self, label, value, min, max)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a FloatOption to the dialog.
        """
        value = self.get_value()
        adj = gtk.Adjustment(value, lower=self.get_min(), upper=self.get_max(), step_incr=0.01)

        self.gobj = gtk.SpinButton(adjustment=adj, digits=2)
        self.gobj.set_value(value)

    def parse(self):
        """
        Parse the object and return.
        """
        return float(self.gobj.get_value())


#-------------------------------------------------------------------------
#
# TextOption class
#
#-------------------------------------------------------------------------
class TextOption(Option):
    """
    This class describes an option that is a multi-line string.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Page header"
        @type label: string
        @param value: An initial value for this option.
            Example: "Generated by GRAMPS\nCopyright 2007"
        @type value: string
        @return: nothing
        """
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a TextOption to the dialog.
        """
        value = self.get_value()
        self.gtext = gtk.TextView()
        self.gtext.get_buffer().set_text("\n".join(value))
        self.gtext.set_editable(1)
        self.gobj = gtk.ScrolledWindow()
        self.gobj.set_shadow_type(gtk.SHADOW_IN)
        self.gobj.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.gobj.add(self.gtext)
        # Required for tooltip
        self.gobj.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        self.gobj.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)

    def parse(self):
        """
        Parse the text option (multi-line text).
        """
        b = self.gtext.get_buffer()
        text_val = unicode( b.get_text( b.get_start_iter(),
                                        b.get_end_iter(),
                                        False)             )
        return text_val.split('\n')
        
#-------------------------------------------------------------------------
#
# BooleanOption class
#
#-------------------------------------------------------------------------
class BooleanOption(Option):
    """
    This class describes an option that is a boolean (True or False).
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @param value: An initial value for this option.
            Example: True
        @type value: boolean
        @return: nothing
        """
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a BooleanOption to the dialog.
        """
        value = self.get_value()
        self.gobj = gtk.CheckButton(self.get_label())
        self.set_label("")
        self.gobj.set_active(value)
        
    def parse(self):
        """
        Parse the object and return.
        """
        return self.gobj.get_active()
        
#-------------------------------------------------------------------------
#
# EnumeratedListOption class
#
#-------------------------------------------------------------------------
class EnumeratedListOption(Option):
    """
    This class describes an option that provides a finite number of values.
    Each possible value is assigned a value and a description.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Paper Size"
        @type label: string
        @param value: An initial value for this option.
            Example: 5
        @type value: int
        @return: nothing
        """
        Option.__init__(self,label,value)
        self.__items = []

    def add_item(self,value,description):
        """
        Add an item to the list of possible values.
        
        @param value: The value that corresponds to this item.
            Example: 5
        @type value: int
        @param description: A description of this value.
            Example: "8.5 x 11"
        @type description: string
        @return: nothing
        """
        self.__items.append((value, description))
        
    def get_items(self):
        """
        Get all the possible values for this option.
        
        @return: an array of tuples containing (value,description) pairs.
        """
        return self.__items

    def make_gui_obj(self, gtk, dialog):
        """
        Add an EnumeratedListOption to the dialog.
        """
        v = self.get_value()
        active_index = 0
        current_index = 0 
        self.combo = gtk.combo_box_new_text()
        self.gobj = gtk.EventBox()
        self.gobj.add(self.combo)
        for (value,description) in self.get_items():
            self.combo.append_text(description)
            if value == v:
                active_index = current_index
            current_index += 1
        self.combo.set_active( active_index )

    def parse(self):
        """
        Parse the EnumeratedListOption and return.
        """
        index = self.combo.get_active()
        items = self.get_items()
        value,description = items[index]
        return value

#-------------------------------------------------------------------------
#
# PersonFilterOption class
#
#-------------------------------------------------------------------------
class PersonFilterOption(Option):
    """
    This class describes an option that provides a list of person filters.
    Each possible value represents one of the possible filters.
    """
    def __init__(self,label, dbstate, value=0, include_single=True):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Filter"
        @type label: string
        @param dbstate: A DbState instance
        @type dbstate: DbState
        @param value: A default value for the option.
            Example: 1
        @type label: int
        @param include_single: Whether a filter should be included for a 
            single person.
        @type include_single: bool
        @return: nothing
        """
        from ReportBase import ReportUtils
        Option.__init__(self,label,value)
        self.__dbstate = dbstate
        self.__include_single = include_single
        self.__person = self.__dbstate.get_active_person()
        self.__filters = ReportUtils.get_person_filters(self.__person,
                                                        self.__include_single)
        if self.get_value() > len(self.__filters):
            self.set_value(0)
            
    def get_center_person(self):
        return self.__person
    
    def get_filter(self):
        """
        Return the filter object.
        """
        return self.__filters[self.get_value()]

    def make_gui_obj(self, gtk, dialog):
        """
        Add an PersonFilterOption to the dialog.
        """
        self.dialog = dialog
        self.combo = gtk.combo_box_new_text()
        self.combo.connect('changed',self.__on_value_changed)
        self.gobj = gtk.HBox()
        self.change_button = gtk.Button("%s..." % _('C_hange') )
        self.change_button.connect('clicked',self.on_change_clicked)
        self.gobj.pack_start(self.combo, False)
        self.gobj.pack_start(self.change_button, False)
        
        self.update_gui_obj()
        
    def __on_value_changed(self, obj):
        self.set_value( int(self.combo.get_active()) )

    def on_change_clicked(self, *obj):
        from Selectors import selector_factory
        SelectPerson = selector_factory('Person')
        sel_person = SelectPerson(self.dialog.dbstate,
                                  self.dialog.uistate,
                                  self.dialog.track)
        new_person = sel_person.run()
        if new_person:
            self.__person = new_person
            self.update_gui_obj()

    def update_gui_obj(self):
        # update the gui object with new filter info
        from ReportBase import ReportUtils
        self.combo.get_model().clear()
        self.__filters = ReportUtils.get_person_filters(self.__person,
                                                        self.__include_single)
        for filter in self.__filters:
            self.combo.append_text(filter.get_name())
        
        if self.get_value() >= len(self.__filters):
            # Set the value to zero if it is not valid.
            self.set_value(0)
        self.combo.set_active(self.get_value())

    def parse(self):
        """
        Parse the object and return.
        """
        return self.get_value()
    
#-------------------------------------------------------------------------
#
# PersonOption class
#
#-------------------------------------------------------------------------
class PersonOption(Option):
    """
    This class describes an option that allows a person from the 
    database to be selected.
    """
    def __init__(self, label, value, dbstate):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Center Person"
        @type label: string
        @param value: A default Gramps ID of a person for this option.
            Example: "p11"
        @type value: string
        @param dbstate: The database state for the database to be used..
        @type value: DbState
        @return: nothing
        """
        self.dbstate = dbstate
        self.db = dbstate.get_database()
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        self.dialog = dialog
        self.gobj = gtk.HBox()
        self.person_label = gtk.Label()
        self.person_label.set_alignment(0.0,0.5)
        self.person_button   = GrampsWidgets.SimpleButton(gtk.STOCK_INDEX, 
                                                      self.get_person_clicked)
        self.person_button.set_relief(gtk.RELIEF_NORMAL)

        self.pevt = gtk.EventBox()
        self.pevt.add(self.person_label)
        
        self.gobj.pack_start(self.pevt, False)
        self.gobj.pack_end(self.person_button, False)
        
        person = self.db.get_person_from_gramps_id(self.get_value())
        if not person:
            person = self.dbstate.get_active_person()
        self.update_person(person)

    def parse(self):
        return self.get_value()

    def get_person_clicked(self, obj):
        from Filters import GenericFilter, Rules
        rfilter = GenericFilter()
        rfilter.set_logical_op('or')
        rfilter.add_rule(Rules.Person.IsBookmarked([]))
        
        default_person = self.db.get_default_person()
        if default_person:
            id = default_person.get_gramps_id()
            rfilter.add_rule(Rules.Person.HasIdOf([id]))
            
        active_person = self.dbstate.get_active_person()
        if active_person:
            id = active_person.get_gramps_id()
            rfilter.add_rule(Rules.Person.HasIdOf([id]))

        SelectPerson = selector_factory('Person')
        sel = SelectPerson(self.dbstate, self.dialog.uistate, 
                           self.dialog.track, 
                           title=_('Select a person for the report'), 
                           filter=rfilter )
        person = sel.run()
        self.update_person(person)
    
    def update_person(self,person):
        if person:
            name = _nd.display(person)
            gid = person.get_gramps_id()
            self.person_label.set_text( "%s (%s)" % (name,gid) )
            self.set_value(gid)
            
    def add_tooltip(self, tooltip):
        """
        Add the option's help to the GUI object.
        """
        tooltip.set_tip(self.pevt, self.get_help())
        tooltip.set_tip(self.person_button,  _('Select a different person'))

#-------------------------------------------------------------------------
#
# PersonListOption class
#
#-------------------------------------------------------------------------
class PersonListOption(Option):
    """
    This class describes a widget that allows multiple people from the 
    database to be selected.
    """
    def __init__(self, label, value, dbstate):
        """
        @param label: A friendly label to be applied to this option.
            Example: "People of interest"
        @type label: string
        @param value: A set of GIDs as initial values for this option.
            Example: "111 222 333 444"
        @type value: string
        @return: nothing
        """
        self.db = dbstate.get_database()
        self.dbstate = dbstate
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a "people picker" widget to the dialog.
        """
        self.dialog = dialog
        
        value = self.get_value()
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.treeView = gtk.TreeView(self.model)
        self.treeView.set_size_request(150, 150)
        col1 = gtk.TreeViewColumn(_('Name'  ), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('ID'    ), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.treeView.append_column(col1)
        self.treeView.append_column(col2)
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add(self.treeView)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledWindow.set_shadow_type(gtk.SHADOW_OUT)
        self.hbox = gtk.HBox()
        self.hbox.pack_start(self.scrolledWindow, expand=True, fill=True)

        for gid in value.split():
            person = self.db.get_person_from_gramps_id(gid)
            if person:
                name = _nd.display(person)
                self.model.append([name, gid])

        # now setup the '+' and '-' pushbutton for adding/removing people from the container
        self.addPerson = GrampsWidgets.SimpleButton(gtk.STOCK_ADD, self.addPersonClicked)
        self.delPerson = GrampsWidgets.SimpleButton(gtk.STOCK_REMOVE, self.delPersonClicked)
        self.vbbox = gtk.VButtonBox()
        self.vbbox.add(self.addPerson)
        self.vbbox.add(self.delPerson)
        self.vbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.hbox.pack_end(self.vbbox, expand=False)

        # parent expects the widget as "self.gobj"
        self.gobj = self.hbox

    def parse(self):
        """
        Parse the object and return.
        """
        gidlist = ''
        iter = self.model.get_iter_first()
        while (iter):
            gid = self.model.get_value(iter, 1)
            gidlist = gidlist + gid + ' '
            iter = self.model.iter_next(iter)
        return gidlist

    def addPersonClicked(self, obj):
        # people we already have must be excluded
        # so we don't list them multiple times
        skipList = set()
        iter = self.model.get_iter_first()
        while (iter):
            gid = self.model.get_value(iter, 1) # get the GID stored in column #1
            person = self.db.get_person_from_gramps_id(gid)
            skipList.add(person.get_handle())
            iter = self.model.iter_next(iter)

        SelectPerson = selector_factory('Person')
        sel = SelectPerson(self.dbstate, self.dialog.uistate, self.dialog.track, skip=skipList)
        person = sel.run()
        if person:
            name = _nd.display(person)
            gid = person.get_gramps_id()
            self.model.append([name, gid])

            # if this person has a spouse, ask if we should include the spouse
            # in the list of "people of interest"
            #
            # NOTE: we may want to make this an optional thing, determined
            # by the use of a parameter at the time this class is instatiated
            familyList = person.get_family_handle_list()
            if familyList:
                for familyHandle in familyList:
                    family = self.db.get_family_from_handle(familyHandle)
                    
                    if person.get_handle() == family.get_father_handle():
                        spouseHandle = family.get_mother_handle()
                    else:
                        spouseHandle = family.get_father_handle()

                    if spouseHandle:
                        if spouseHandle not in skipList:
                            import gtk
                            spouse = self.db.get_person_from_handle(spouseHandle)
                            text = _('Also include %s?') % spouse.get_primary_name().get_regular_name()
                            prompt = gtk.MessageDialog(parent=self.dialog.window, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format=text)
                            prompt.set_default_response(gtk.RESPONSE_YES)
                            prompt.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                            prompt.set_title(_('Select Person'))
                            button = prompt.run()
                            prompt.destroy()
                            if button == gtk.RESPONSE_YES:
                                name = _nd.display(spouse)
                                gid = spouse.get_gramps_id()
                                self.model.append([name, gid])

    def delPersonClicked(self, obj):
        (path, column) = self.treeView.get_cursor()
        if (path):
            iter = self.model.get_iter(path)
            self.model.remove(iter)

#-------------------------------------------------------------------------
#
# SurnameColourOption class
#
#-------------------------------------------------------------------------
class SurnameColourOption(Option):
    """
    This class describes a widget that allows multiple surnames to be
    selected from the database, and to assign a colour (not necessarily
    unique) to each one.
    """
    def __init__(self, label, value, dbstate):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Family lines"
        @type label: string
        @param value: A set of surnames and colours.
            Example: "surname1 colour1 surname2 colour2"
        @type value: string
        @return: nothing
        """
        self.db = dbstate.get_database()
        self.dbstate = dbstate
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a "surname-colour" widget to the dialog.
        """
        self.dialog = dialog
        self.surnames = {}  # list of surnames and count
        
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.treeView = gtk.TreeView(self.model)
        self.treeView.set_size_request(150, 150)
        self.treeView.connect('row-activated', self.clicked)
        col1 = gtk.TreeViewColumn(_('Surname'), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('Colour'), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sort_column_id(0)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.treeView.append_column(col1)
        self.treeView.append_column(col2)
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add(self.treeView)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledWindow.set_shadow_type(gtk.SHADOW_OUT)
        self.hbox = gtk.HBox()
        self.hbox.pack_start(self.scrolledWindow, expand=True, fill=True)

        self.addSurname = GrampsWidgets.SimpleButton(gtk.STOCK_ADD, self.addSurnameClicked)
        self.delSurname = GrampsWidgets.SimpleButton(gtk.STOCK_REMOVE, self.delSurnameClicked)
        self.vbbox = gtk.VButtonBox()
        self.vbbox.add(self.addSurname)
        self.vbbox.add(self.delSurname)
        self.vbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.hbox.pack_end(self.vbbox, expand=False)

        # populate the surname/colour treeview
        tmp = self.get_value().split()
        while len(tmp) > 1:
            surname = tmp.pop(0)
            colour = tmp.pop(0)
            self.model.append([surname, colour])

        # parent expects the widget as "self.gobj"
        self.gobj = self.hbox

    def parse(self):
        """
        Parse the object and return.
        """
        surnameColours = ''
        iter = self.model.get_iter_first()
        while (iter):
            surname = self.model.get_value(iter, 0) # .encode('iso-8859-1','xmlcharrefreplace')
            colour = self.model.get_value(iter, 1)
            # tried to use a dictionary, and tried to save it as a tuple,
            # but coulnd't get this to work right -- this is lame, but now
            # the surnames and colours are saved as a plain text string
            surnameColours += surname + ' ' + colour + ' '
            iter = self.model.iter_next(iter)
        return surnameColours

    def clicked(self, treeview, path, column):
        # get the surname and colour value for this family
        iter = self.model.get_iter(path)
        surname = self.model.get_value(iter, 0)
        colour = gtk.gdk.color_parse(self.model.get_value(iter, 1))

        colourDialog = gtk.ColorSelectionDialog('Select colour for %s' % surname)
        colourDialog.colorsel.set_current_color(colour)
        response = colourDialog.run()

        if response == gtk.RESPONSE_OK:
            colour = colourDialog.colorsel.get_current_color()
            colourName = '#%02x%02x%02x' % (
                int(colour.red  *256/65536),
                int(colour.green*256/65536),
                int(colour.blue *256/65536))
            self.model.set_value(iter, 1, colourName)

        colourDialog.destroy()

    def addSurnameClicked(self, obj):
        skipList = set()
        iter = self.model.get_iter_first()
        while (iter):
            surname = self.model.get_value(iter, 0)
            skipList.add(surname.encode('iso-8859-1','xmlcharrefreplace'))
            iter = self.model.iter_next(iter)

        ln = LastNameDialog(self.db, self.dialog.uistate, self.dialog.track, self.surnames, skipList)
        surnameSet = ln.run()
        for surname in surnameSet:
            self.model.append([surname, '#ffffff'])

    def delSurnameClicked(self, obj):
        (path, column) = self.treeView.get_cursor()
        if (path):
            iter = self.model.get_iter(path)
            self.model.remove(iter)

#-------------------------------------------------------------------------
#
# Menu class
#
#-------------------------------------------------------------------------
class Menu:
    """
    Introduction
    ============
    A Menu is used to maintain a collection of options that need to be 
    represented to the user in a non-implementation specific way. The options
    can be described using the various option classes. A menu contains many
    options and associates them with a unique name and category.
    
    Usage
    =====
    Menus are used in the following way.

      1. Create a option object and configure all the attributes of the option.
      2. Add the option to the menu by specifying the option, name and category.
      3. Add as many options as necessary.
      4. When all the options are added, the menu can be stored and passed to
         the part of the system that will actually represent the menu to 
         the user.
    """
    def __init__(self):
        self.__options = {}
    
    def add_option(self,category,name,option):
        """
        Add an option to the menu.
        
        @param category: A label that describes the category that the option 
            belongs to. 
            Example: "Report Options"
        @type category: string
        @param name: A name that is unique to this option.
            Example: "generations"
        @type name: string
        @param option: The option instance to be added to this menu.
        @type option: Option
        @return: nothing
        """
        if not self.__options.has_key(category):
            self.__options[category] = []
        self.__options[category].append((name,option))
        
    def get_categories(self):
        """
        Get a list of categories in this menu.
        
        @return: a list of strings
        """
        categories = []
        for category in self.__options:
            categories.append(category)
        return categories
    
    def get_option_names(self,category):
        """
        Get a list of option names for the specified category.
        
        @return: a list of strings
        """
        names = []
        for (name,option) in self.__options[category]:
            names.append(name)
        return names
    
    def get_option(self,category,name):
        """
        Get an option with the specified category and name.
        
        @return: an Option instance or None on failure.
        """
        for (oname,option) in self.__options[category]:
            if oname == name:
                return option
        return None
    
    def get_all_option_names(self):
        """
        Get a list of all the option names in this menu.
        
        @return: a list of strings
        """
        names = []
        for category in self.__options:
            for (name,option) in self.__options[category]:
                names.append(name)
        return names
    
    def get_option_by_name(self,name):
        """
        Get an option with the specified name.
        
        @return: an Option instance or None on failure.
        """
        for category in self.__options.keys():
            for (oname,option) in self.__options[category]:
                if oname == name:
                    return option
        return None

#------------------------------------------------------------------------
#
# MenuOptions class
#
#------------------------------------------------------------------------
class MenuOptions:
    def __init__(self,dbstate):
        self.menu = Menu()
        
        # Fill options_dict with report/tool defaults:
        self.options_dict = {}
        self.options_help = {}
        self.add_menu_options(self.menu,dbstate)
        for name in self.menu.get_all_option_names():
            option = self.menu.get_option_by_name(name)
            self.options_dict[name] = option.get_value()
            self.options_help[name] = option.get_help()

    def make_default_style(self,default_style):
        pass

    def add_menu_options(self,menu,dbstate):
        """
        Add the user defined options to the menu.
        
        @param menu: A menu class for the options to belong to.
        @type menu: Menu
        @return: nothing
        """
        raise NotImplementedError
    
    def add_menu_option(self,category,name,option):
        self.menu.add_option(category,name, option)
        self.options_dict[name] = option.get_value()
        self.options_help[name] = option.get_help()

    def add_user_options(self, dialog):
        """
        Generic method to add user options to the gui.
        """
        import gtk
        self.tooltips = gtk.Tooltips()
        for category in self.menu.get_categories():
            for name in self.menu.get_option_names(category):
                option = self.menu.get_option(category,name)
                # override option default with xml-saved value:
                if name in self.options_dict:
                    option.set_value(self.options_dict[name])
                option.make_gui_obj(gtk, dialog)
                option.add_dialog_category(dialog, category)
                option.add_tooltip(self.tooltips)
                
    def parse_user_options(self,dialog):
        """
        Generic method to parse the user options and cache result in options_dict.
        """
        for name in self.menu.get_all_option_names():
            self.options_dict[name] = self.menu.get_option_by_name(name).parse()

    def get_option_names(self):
        """
        Return all names of options.
        """
        return self.menu.get_all_option_names()

    def get_user_value(self, name):
        """
        Get and parse the users choice.
        """
        return self.menu.get_option_by_name(name).parse()

