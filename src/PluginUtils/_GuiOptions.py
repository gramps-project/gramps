#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
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
# $Id:  $

"""
Specific option handling for a GUI.
"""
#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gtk
import gobject
import Utils
import GrampsWidgets
import ManagedWindow
from QuestionDialog import OptionDialog
from Selectors import selector_factory
from BasicUtils import name_displayer as _nd
from Filters import GenericFilter, Rules
import _MenuOptions

#------------------------------------------------------------------------
#
# Dialog window used to select a surname
#
#------------------------------------------------------------------------
class LastNameDialog(ManagedWindow.ManagedWindow):
    """
    A dialog that allows the selection of a surname from the database.
    """
    def __init__(self, database, uistate, track, surnames, skip_list=set()):

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | \
                gtk.DIALOG_NO_SEPARATOR
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, 
                   gtk.RESPONSE_ACCEPT)
        self.__dlg = gtk.Dialog(None, uistate.window, flags, buttons)
        self.__dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_window(self.__dlg, None, _('Select surname'))
        self.window.set_default_size(400, 400)

        # build up a container to display all of the people of interest
        self.__model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        self.__tree_view = gtk.TreeView(self.__model)
        col1 = gtk.TreeViewColumn(_('Surname'), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('Count'), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.__tree_view.append_column(col1)
        self.__tree_view.append_column(col2)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.add(self.__tree_view)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_OUT)
        self.__dlg.vbox.pack_start(scrolled_window, expand=True, fill=True)
        scrolled_window.show_all()

        if len(surnames) == 0:
            # we could use database.get_surname_list(), but if we do that
            # all we get is a list of names without a count...therefore
            # we'll traverse the entire database ourself and build up a
            # list that we can use
#            for name in database.get_surname_list():
#                self.__model.append([name, 0])

            # build up the list of surnames, keeping track of the count for each
            # name (this can be a lengthy process, so by passing in the 
            # dictionary we can be certain we only do this once)
            progress = Utils.ProgressMeter(_('Finding surnames'))
            progress.set_pass(_('Finding surnames'), 
                              database.get_number_of_people())
            for person_handle in database.get_person_handles(False):
                progress.step()
                person = database.get_person_from_handle(person_handle)
                key = person.get_primary_name().get_surname()
                count = 0
                if key in surnames:
                    count = surnames[key]
                surnames[key] = count + 1
            progress.close()

        # insert the names and count into the model
        for key in surnames:
            if key.encode('iso-8859-1','xmlcharrefreplace') not in skip_list:
                self.__model.append([key, surnames[key]])

        # keep the list sorted starting with the most popular last name
        self.__model.set_sort_column_id(1, gtk.SORT_DESCENDING)

        # the "OK" button should be enabled/disabled based on the selection of 
        # a row
        self.__tree_selection = self.__tree_view.get_selection()
        self.__tree_selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.__tree_selection.select_path(0)

    def run(self):
        """
        Display the dialog and return the selected surnames when done.
        """
        response = self.__dlg.run()
        surname_set = set()
        if response == gtk.RESPONSE_ACCEPT:
            (mode, paths) = self.__tree_selection.get_selected_rows()
            for path in paths:
                i = self.__model.get_iter(path)
                surname = self.__model.get_value(i, 0)
                surname_set.add(surname)
        self.__dlg.destroy()
        return surname_set

#-------------------------------------------------------------------------
#
# GuiStringOption class
#
#-------------------------------------------------------------------------
class GuiStringOption(gtk.Entry):
    """
    This class displays an option that is a simple one-line string.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        """
        @param option: The option to display.
        @type option: MenuOption.StringOption
        @return: nothing
        """
        gtk.Entry.__init__(self)
        self.__option = option
        self.set_text( self.__option.get_value() )
        self.connect('changed', self.__text_changed)
        tooltip.set_tip(self, self.__option.get_help())
        
    def __text_changed(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value.
        """
        self.__option.set_value( self.__entry.get_text() )

#-------------------------------------------------------------------------
#
# GuiColourOption class
#
#-------------------------------------------------------------------------
class GuiColourOption(gtk.ColorButton):
    """
    This class displays an option that allows the selection of a colour.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        self.__option = option
        value = self.__option.get_value()
        gtk.ColorButton.__init__( self, gtk.gdk.color_parse(value) )
        self.connect('color-set', self.__value_changed)
        tooltip.set_tip(self, self.__option.get_help())
        
    def __value_changed(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the change of color.
        """
        colour = self.get_color()
        value = '#%02x%02x%02x' % (
            int(colour.red      * 256 / 65536),
            int(colour.green    * 256 / 65536),
            int(colour.blue     * 256 / 65536))
        self.__option.set_value(value)

#-------------------------------------------------------------------------
#
# GuiNumberOption class
#
#-------------------------------------------------------------------------
class GuiNumberOption(gtk.SpinButton):
    """
    This class displays an option that is a simple number with defined maximum 
    and minimum values.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        self.__option = option

        decimals = 0
        step = self.__option.get_step()
        adj = gtk.Adjustment(1, 
                             self.__option.get_min(), 
                             self.__option.get_max(), 
                             step)
        
        # Calculate the number of decimal places if necessary
        if step < 1:
            import math
            decimals = int(math.log10(step) * -1)
            
        gtk.SpinButton.__init__(self, adj, digits=decimals)

        self.set_value(self.__option.get_value())
        self.connect('changed', self.__value_changed)
        tooltip.set_tip(self, self.__option.get_help())
        
    def __value_changed(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value.
        """
        self.__option.set_value( int(self.get_value_as_int()) )

#-------------------------------------------------------------------------
#
# GuiTextOption class
#
#-------------------------------------------------------------------------
class GuiTextOption(gtk.ScrolledWindow):
    """
    This class displays an option that is a multi-line string.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        self.__option = option
        gtk.ScrolledWindow.__init__(self)
        self.set_shadow_type(gtk.SHADOW_IN)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # Add a TextView
        value = self.__option.get_value()
        gtext = gtk.TextView()
        gtext.get_buffer().set_text("\n".join(value))
        gtext.set_editable(1)
        self.add(gtext)

        # Required for tooltip
        gtext.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        gtext.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)
        tooltip.set_tip(gtext, self.__option.get_help())
        
        self.__buff = gtext.get_buffer()
        self.__buff.connect('changed', self.__value_changed)

    def __value_changed(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value.
        """
        text_val = unicode( self.__buff.get_text( self.__buff.get_start_iter(),
                                                  self.__buff.get_end_iter(),
                                                  False)             )
        self.__option.set_value( text_val.split('\n') )
        
#-------------------------------------------------------------------------
#
# GuiBooleanOption class
#
#-------------------------------------------------------------------------
class GuiBooleanOption(gtk.CheckButton):
    """
    This class displays an option that is a boolean (True or False).
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        self.__option = option
        gtk.CheckButton.__init__(self, self.__option.get_label())
        self.set_active(self.__option.get_value())
        self.connect('toggled', self.__value_changed)
        tooltip.set_tip(self, self.__option.get_help())
        
    def __value_changed(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value.
        """
        self.__option.set_value( self.get_active() )
        
#-------------------------------------------------------------------------
#
# GuiEnumeratedListOption class
#
#-------------------------------------------------------------------------
class GuiEnumeratedListOption(gtk.EventBox):
    """
    This class displays an option that provides a finite number of values.
    Each possible value is assigned a value and a description.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        gtk.EventBox.__init__(self)
        self.__option = option
        self.__combo = gtk.combo_box_new_text()
        self.add(self.__combo)
        
        self.__update_options()

        tooltip.set_tip(self, self.__option.get_help())
        
        self.__combo.connect('changed', self.__value_changed)
        self.__option.connect('options-changed', self.__update_options)
        self.__option.connect('avail-changed', self.__update_avail)
        self.__update_avail()
        
    def __value_changed(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the change of the value.
        """
        index = self.__combo.get_active()
        if index < 0:
            return
        items = self.__option.get_items()
        value, description = items[index] # IGNORE:W0612 - description is unused
        self.__option.set_value( value )
        
    def __update_options(self):
        """
        Handle the change of the available options.
        """
        self.__combo.get_model().clear()
        cur_val = self.__option.get_value()
        active_index = 0
        current_index = 0
        for (value, description) in self.__option.get_items():
            self.__combo.append_text(description)
            if value == cur_val:
                active_index = current_index
            current_index += 1
        self.__combo.set_active( active_index )
        
    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

#-------------------------------------------------------------------------
#
# GuiPersonOption class
#
#-------------------------------------------------------------------------
class GuiPersonOption(gtk.HBox):
    """
    This class displays an option that allows a person from the 
    database to be selected.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        """
        @param option: The option to display.
        @type option: MenuOption.PersonOption
        @return: nothing
        """
        gtk.HBox.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.__person_label = gtk.Label()
        self.__person_label.set_alignment(0.0, 0.5)
        
        pevt = gtk.EventBox()
        pevt.add(self.__person_label)
        person_button = GrampsWidgets.SimpleButton(gtk.STOCK_INDEX, 
                                                   self.__get_person_clicked)
        person_button.set_relief(gtk.RELIEF_NORMAL)

        self.pack_start(pevt, False)
        self.pack_end(person_button, False)
        
        person = self.__db.get_person_from_gramps_id(self.__option.get_value())
        if not person:
            person = self.__dbstate.get_active_person()
            if not person:
                person = self.__db.get_default_person()
        self.__update_person(person)
        
        tooltip.set_tip(pevt, self.__option.get_help())
        tooltip.set_tip(person_button,  _('Select a different person'))
        
        self.__option.connect('avail-changed', self.__update_avail)
        self.__update_avail()

    def __get_person_clicked(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the button to choose a different person.
        """
        # Create a filter for the person selector.
        rfilter = GenericFilter()
        rfilter.set_logical_op('or')
        rfilter.add_rule(Rules.Person.IsBookmarked([]))
        rfilter.add_rule(Rules.Person.HasIdOf([self.__option.get_value()]))
        
        # Add the database home person if one exists.
        default_person = self.__db.get_default_person()
        if default_person:
            gid = default_person.get_gramps_id()
            rfilter.add_rule(Rules.Person.HasIdOf([gid]))
        
        # Add the selected person if one exists.
        active_person = self.__dbstate.get_active_person()
        if active_person:
            gid = active_person.get_gramps_id()
            rfilter.add_rule(Rules.Person.HasIdOf([gid]))

        select_class = selector_factory('Person')
        sel = select_class(self.__dbstate, self.__uistate, self.__track, 
                           title=_('Select a person for the report'), 
                           filter=rfilter )
        person = sel.run()
        self.__update_person(person)
    
    def __update_person(self, person):
        """
        Update the currently selected person.
        """
        if person:
            name = _nd.display(person)
            gid = person.get_gramps_id()
            self.__person_label.set_text( "%s (%s)" % (name, gid) )
            self.__option.set_value(gid)
            
    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)
        
#-------------------------------------------------------------------------
#
# GuiFamilyOption class
#
#-------------------------------------------------------------------------
class GuiFamilyOption(gtk.HBox):
    """
    This class displays an option that allows a family from the 
    database to be selected.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        """
        @param option: The option to display.
        @type option: MenuOption.FamilyOption
        @return: nothing
        """
        gtk.HBox.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track
        self.__family_label = gtk.Label()
        self.__family_label.set_alignment(0.0, 0.5)
        
        pevt = gtk.EventBox()
        pevt.add(self.__family_label)
        family_button = GrampsWidgets.SimpleButton(gtk.STOCK_INDEX, 
                                                   self.__get_family_clicked)
        family_button.set_relief(gtk.RELIEF_NORMAL)

        self.pack_start(pevt, False)
        self.pack_end(family_button, False)
        
        family = self.__db.get_family_from_gramps_id(self.__option.get_value())
        if not family:
            person = self.__dbstate.get_active_person()
            family_list = person.get_family_handle_list()
            if not family_list:
                person = self.__db.get_default_person()
                family_list = person.get_family_handle_list()
            family = self.__db.get_family_from_handle(family_list[0])
        self.__update_family(family)
        
        tooltip.set_tip(pevt, self.__option.get_help())
        tooltip.set_tip(family_button,  _('Select a different family'))
        
        self.__option.connect('avail-changed', self.__update_avail)
        self.__update_avail()

    def __get_family_clicked(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the button to choose a different family.
        """
        # Create a filter for the person selector.
        rfilter = GenericFilter()
        rfilter.set_logical_op('or')
        
        # Add the current family
        rfilter.add_rule(Rules.Family.HasIdOf([self.__option.get_value()]))
        
        # Add all bookmarked families
        rfilter.add_rule(Rules.Family.IsBookmarked([]))

        # Add the families of the database home person if one exists.
        default_person = self.__db.get_default_person()
        if default_person:
            family_list = default_person.get_family_handle_list()
            for family_handle in family_list:
                family = self.__db.get_family_from_handle(family_handle)
                gid = family.get_gramps_id()
                rfilter.add_rule(Rules.Family.HasIdOf([gid]))
            
        # Add the families of the selected person if one exists.
        active_person = self.__db.get_default_person()
        if active_person:
            family_list = active_person.get_family_handle_list()
            for family_handle in family_list:
                family = self.__db.get_family_from_handle(family_handle)
                gid = family.get_gramps_id()
                rfilter.add_rule(Rules.Family.HasIdOf([gid]))

        select_class = selector_factory('Family')
        sel = select_class(self.__dbstate, self.__uistate, self.__track, 
                           filter=rfilter )
        family = sel.run()
        self.__update_family(family)
    
    def __update_family(self, family):
        """
        Update the currently selected family.
        """
        if family:
            family_id = family.get_gramps_id()
            fhandle = family.get_father_handle()
            mhandle = family.get_mother_handle()
            
            if fhandle:
                father = self.__db.get_person_from_handle(fhandle)
                father_name = _nd.display(father)
            else:
                father_name = _("unknown father")
                
            if mhandle:
                mother = self.__db.get_person_from_handle(mhandle)
                mother_name = _nd.display(mother)
            else:
                mother_name = _("unknown mother")
                
            name = _("%s and %s (%s)") % (father_name, mother_name, family_id)

            self.__family_label.set_text( name )
            self.__option.set_value(family_id)
            
    def __update_avail(self):
        """
        Update the availability (sensitivity) of this widget.
        """
        avail = self.__option.get_available()
        self.set_sensitive(avail)

#-------------------------------------------------------------------------
#
# GuiPersonListOption class
#
#-------------------------------------------------------------------------
class GuiPersonListOption(gtk.HBox):
    """
    This class displays a widget that allows multiple people from the 
    database to be selected.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        """
        @param option: The option to display.
        @type option: MenuOption.PersonListOption
        @return: nothing
        """
        gtk.HBox.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track

        self.__model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.__tree_view = gtk.TreeView(self.__model)
        self.__tree_view.set_size_request(150, 150)
        col1 = gtk.TreeViewColumn(_('Name'  ), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('ID'    ), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.__tree_view.append_column(col1)
        self.__tree_view.append_column(col2)
        self.__scrolled_window = gtk.ScrolledWindow()
        self.__scrolled_window.add(self.__tree_view)
        self.__scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, 
                                          gtk.POLICY_AUTOMATIC)
        self.__scrolled_window.set_shadow_type(gtk.SHADOW_OUT)

        self.pack_start(self.__scrolled_window, expand=True, fill=True)

        value = self.__option.get_value()
        for gid in value.split():
            person = self.__db.get_person_from_gramps_id(gid)
            if person:
                name = _nd.display(person)
                self.__model.append([name, gid])

        # now setup the '+' and '-' pushbutton for adding/removing people from 
        # the container
        self.__add_person = GrampsWidgets.SimpleButton(gtk.STOCK_ADD, 
                                                 self.__add_person_clicked)
        self.__del_person = GrampsWidgets.SimpleButton(gtk.STOCK_REMOVE, 
                                                 self.__del_person_clicked)
        self.__vbbox = gtk.VButtonBox()
        self.__vbbox.add(self.__add_person)
        self.__vbbox.add(self.__del_person)
        self.__vbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.pack_end(self.__vbbox, expand=False)
        
        tooltip.set_tip(self.__tree_view, self.__option.get_help())

    def __update_value(self):
        """
        Parse the object and return.
        """
        gidlist = ''
        i = self.__model.get_iter_first()
        while (i):
            gid = self.__model.get_value(i, 1)
            gidlist = gidlist + gid + ' '
            i = self.__model.iter_next(i)
        self.__option.set_value(gidlist)

    def __add_person_clicked(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the add person button.
        """
        # people we already have must be excluded
        # so we don't list them multiple times
        skip_list = set()
        i = self.__model.get_iter_first()
        while (i):
            gid = self.__model.get_value(i, 1) # get the GID stored in column #1
            person = self.__db.get_person_from_gramps_id(gid)
            skip_list.add(person.get_handle())
            i = self.__model.iter_next(i)

        select_class = selector_factory('Person')
        sel = select_class(self.__dbstate, self.__uistate, 
                           self.__track, skip=skip_list)
        person = sel.run()
        if person:
            name = _nd.display(person)
            gid = person.get_gramps_id()
            self.__model.append([name, gid])

            # if this person has a spouse, ask if we should include the spouse
            # in the list of "people of interest"
            #
            # NOTE: we may want to make this an optional thing, determined
            # by the use of a parameter at the time this class is instatiated
            family_list = person.get_family_handle_list()
            for family_handle in family_list:
                family = self.__db.get_family_from_handle(family_handle)
                
                if person.get_handle() == family.get_father_handle():
                    spouse_handle = family.get_mother_handle()
                else:
                    spouse_handle = family.get_father_handle()

                if spouse_handle and (spouse_handle not in skip_list):
                    spouse = self.__db.get_person_from_handle(
                                                          spouse_handle)
                    spouse_name = _nd.display(spouse)
                    text = _('Also include %s?') % spouse_name

                    prompt = OptionDialog(_('Select Person'),
                                          text,
                                          _('No'), None,
                                          _('Yes'), None)
                    if prompt.get_response() == gtk.RESPONSE_YES:
                        gid = spouse.get_gramps_id()
                        self.__model.append([spouse_name, gid])
                        
            self.__update_value()
            
    def __del_person_clicked(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the delete person button.
        """
        (path, column) = self.__tree_view.get_cursor()
        if (path):
            i = self.__model.get_iter(path)
            self.__model.remove(i)
            self.__update_value()

#-------------------------------------------------------------------------
#
# GuiSurnameColourOption class
#
#-------------------------------------------------------------------------
class GuiSurnameColourOption(gtk.HBox):
    """
    This class displays a widget that allows multiple surnames to be
    selected from the database, and to assign a colour (not necessarily
    unique) to each one.
    """
    def __init__(self, option, dbstate, uistate, track, tooltip):
        """
        @param option: The option to display.
        @type option: MenuOption.SurnameColourOption
        @return: nothing
        """
        gtk.HBox.__init__(self)
        self.__option = option
        self.__dbstate = dbstate
        self.__db = dbstate.get_database()
        self.__uistate = uistate
        self.__track = track

        # This will get populated the first time the dialog is run,
        # and used each time after.
        self.__surnames = {}  # list of surnames and count
        
        self.__model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.__tree_view = gtk.TreeView(self.__model)
        self.__tree_view.set_size_request(150, 150)
        self.__tree_view.connect('row-activated', self.__row_clicked)
        col1 = gtk.TreeViewColumn(_('Surname'), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('Colour'), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sort_column_id(0)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.__tree_view.append_column(col1)
        self.__tree_view.append_column(col2)
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.add(self.__tree_view)
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, 
                                        gtk.POLICY_AUTOMATIC)
        self.scrolled_window.set_shadow_type(gtk.SHADOW_OUT)
        self.pack_start(self.scrolled_window, expand=True, fill=True)

        self.add_surname = GrampsWidgets.SimpleButton(gtk.STOCK_ADD, 
                                                     self.__add_clicked)
        self.del_surname = GrampsWidgets.SimpleButton(gtk.STOCK_REMOVE, 
                                                     self.__del_clicked)
        self.vbbox = gtk.VButtonBox()
        self.vbbox.add(self.add_surname)
        self.vbbox.add(self.del_surname)
        self.vbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.pack_end(self.vbbox, expand=False)

        # populate the surname/colour treeview
        tmp = self.__option.get_value().split()
        while len(tmp) > 1:
            surname = tmp.pop(0)
            colour = tmp.pop(0)
            self.__model.append([surname, colour])
            
        tooltip.set_tip(self.__tree_view, self.__option.get_help())

    def __value_changed(self):
        """
        Parse the object and return.
        """
        surname_colours = ''
        i = self.__model.get_iter_first()
        while (i):
            surname = self.__model.get_value(i, 0) 
            #surname = surname.encode('iso-8859-1','xmlcharrefreplace')
            colour = self.__model.get_value(i, 1)
            # tried to use a dictionary, and tried to save it as a tuple,
            # but coulnd't get this to work right -- this is lame, but now
            # the surnames and colours are saved as a plain text string
            surname_colours += surname + ' ' + colour + ' '
            i = self.__model.iter_next(i)
        self.__option.set_value( surname_colours )

    def __row_clicked(self, treeview, path, column):
        """
        Handle the case of a row being clicked on.
        """
        # get the surname and colour value for this family
        i = self.__model.get_iter(path)
        surname = self.__model.get_value(i, 0)
        colour = gtk.gdk.color_parse(self.__model.get_value(i, 1))

        title = 'Select colour for %s' % surname
        colour_dialog = gtk.ColorSelectionDialog(title)
        colorsel = colour_dialog.colorsel
        colorsel.set_current_color(colour)
        response = colour_dialog.run()

        if response == gtk.RESPONSE_OK:
            colour = colorsel.get_current_color()
            colour_name = '#%02x%02x%02x' % (
                int(colour.red  *256/65536),
                int(colour.green*256/65536),
                int(colour.blue *256/65536))
            self.__model.set_value(i, 1, colour_name)

        colour_dialog.destroy()
        self.__value_changed()

    def __add_clicked(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the the add surname button.
        """
        skip_list = set()
        i = self.__model.get_iter_first()
        while (i):
            surname = self.__model.get_value(i, 0)
            skip_list.add(surname.encode('iso-8859-1','xmlcharrefreplace'))
            i = self.__model.iter_next(i)

        ln_dialog = LastNameDialog(self.__db, self.__uistate, 
                                   self.__track, self.__surnames, skip_list)
        surname_set = ln_dialog.run()
        for surname in surname_set:
            self.__model.append([surname, '#ffffff'])
        self.__value_changed()

    def __del_clicked(self, obj): # IGNORE:W0613 - obj is unused
        """
        Handle the the delete surname button.
        """
        (path, column) = self.__tree_view.get_cursor()
        if (path):
            i = self.__model.get_iter(path)
            self.__model.remove(i)
            self.__value_changed()

#------------------------------------------------------------------------
#
# GuiMenuOptions class
#
#------------------------------------------------------------------------
class GuiMenuOptions:
    """
    Introduction
    ============
    A GuiMenuOptions is used to implement the necessary funtions for adding
    options to a GTK dialog.
    """
    def __init__(self, dbstate):
        self.menu = _MenuOptions.Menu()
        self.__dbstate = dbstate
        
        # Fill options_dict with report/tool defaults:
        self.options_dict = {}
        self.options_help = {}
        self.__tooltips = gtk.Tooltips()
        self.add_menu_options(self.menu, dbstate)
        for name in self.menu.get_all_option_names():
            option = self.menu.get_option_by_name(name)
            self.options_dict[name] = option.get_value()
            self.options_help[name] = option.get_help()

    def make_default_style(self, default_style):
        """
        This function is currently required by some reports.
        """
        pass

    def add_menu_options(self, menu, dbstate):
        """
        Add the user defined options to the menu.
        
        @param menu: A menu class for the options to belong to.
        @type menu: Menu
        @return: nothing
        """
        raise NotImplementedError
    
    def add_menu_option(self, category, name, option):
        """
        Add a single option to the menu.
        """
        self.menu.add_option(category, name, option)
        self.options_dict[name] = option.get_value()
        self.options_help[name] = option.get_help()

    def add_user_options(self, dialog):
        """
        Generic method to add user options to the gui.
        """
        for category in self.menu.get_categories():
            for name in self.menu.get_option_names(category):
                option = self.menu.get_option(category, name)
                
                # override option default with xml-saved value:
                if name in self.options_dict:
                    option.set_value(self.options_dict[name])
                    
                found = True
                label = True
                if isinstance(option, _MenuOptions.PersonOption):
                    widget = GuiPersonOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.NumberOption):
                    widget = GuiNumberOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.BooleanOption):
                    widget = GuiBooleanOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                    label = False
                elif isinstance(option, _MenuOptions.StringOption):
                    widget = GuiStringOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.EnumeratedListOption):
                    widget = GuiEnumeratedListOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.TextOption):
                    widget = GuiTextOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.FamilyOption):
                    widget = GuiFamilyOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.PersonListOption):
                    widget = GuiPersonListOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.ColourOption):
                    widget = GuiColourOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                elif isinstance(option, _MenuOptions.SurnameColourOption):
                    widget = GuiSurnameColourOption(option, self.__dbstate, 
                                             dialog.uistate, dialog.track, 
                                             self.__tooltips)
                else:
                    found = False
                    
                if not found:
                    print "UNKNOWN OPTION: ", option
                else:
                    if label:
                        dialog.add_frame_option(category, 
                            option.get_label(), 
                            widget)
                    else:
                        dialog.add_frame_option(category, "", widget)

    def parse_user_options(self, dialog): # IGNORE:W0613 - dialog is unused
        """
        Load the changed values into the saved options.
        """
        for name in self.menu.get_all_option_names():
            option = self.menu.get_option_by_name(name)
            self.options_dict[name] = option.get_value()

