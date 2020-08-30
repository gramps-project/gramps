#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
#               2008-2009  Benny Malengier
#               2009       Gary Burton
#               2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from copy import copy

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_SECT3
from gramps.gen.config import config
from gramps.gen.display.name import displayer as name_displayer
from .editsecondary import EditSecondary
from gramps.gen.lib import NoteType
from .displaytabs import GrampsTab, CitationEmbedList, NoteTab, SurnameTab
from ..widgets import (MonitoredEntry, MonitoredMenu, MonitoredDate,
                     MonitoredDataType, PrivacyButton)
from ..glade import Glade
from gramps.gen.errors import ValidationError

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT3


class GeneralNameTab(GrampsTab):
    """
    This class provides the tabpage of the general name tab
    """

    def __init__(self, dbstate, uistate, track, name, widget):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        @param widget: widget to be shown in the tab
        @type widge: gtk widget
        """
        GrampsTab.__init__(self, dbstate, uistate, track, name)
        eventbox = Gtk.EventBox()
        eventbox.add(widget)
        self.pack_start(eventbox, True, True, 0)
        self._set_label(show_image=False)
        widget.connect('key_press_event', self.key_pressed)
        self.show_all()

    def is_empty(self):
        """
        Override base class
        """
        return False

#-------------------------------------------------------------------------
#
# EditName class
#
#-------------------------------------------------------------------------
class EditName(EditSecondary):

    def __init__(self, dbstate, uistate, track, name, callback):

        EditSecondary.__init__(self, dbstate, uistate,
                               track, name, callback)

    def _local_init(self):

        self.top = Glade()

        self.set_window(self.top.toplevel, None, _("Name Editor"))
        self.setup_configs('interface.name', 600, 350)

        tblgnam = self.top.get_object('table23')
        notebook = self.top.get_object('notebook')
        hbox_surn = self.top.get_object('hboxmultsurnames')
        hbox_surn.set_size_request(-1,
                            int(config.get('interface.surname-box-height')))
        hbox_surn.pack_start(SurnameTab(self.dbstate, self.uistate, self.track,
                                        self.obj, top_label=None),
                             True, True, 0)
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.gennam = GeneralNameTab(self.dbstate, self.uistate, self.track,
                              _('_General'), tblgnam)

        self.original_group_as = self.obj.get_group_as()
        self.original_group_set = not (self.original_group_as == '')
        srn = self.obj.get_primary_surname().get_surname()
        self._get_global_grouping(srn)

        self.group_over = self.top.get_object('group_over')
        self.group_over.connect('toggled',self.on_group_over_toggled)
        self.group_over.set_sensitive(not self.db.readonly)

        self.toggle_dirty = False

    def _post_init(self):
        """if there is override, set the override toggle active
        """
        if self.original_group_set:
            self.group_over.set_active(True)
        else:
            # The glade file correctly sets group_as widget editable=False.
            # At this stage of initialization self.group_as.obj.get_editable()
            # is however still true, correct that.
            self.group_as.enable(False)

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_object('button119'))
        self.define_help_button(self.top.get_object('button131'),
                WIKI_HELP_PAGE,
                _('Name_Editor', 'manual'))
        self.define_ok_button(self.top.get_object('button118'), self.save)

    def _validate_call(self, widget, text):
        """ a callname must be a part of the given name, see if this is the
            case """
        validcall = self.given_field.obj.get_text().split()
        dummy = copy(validcall)
        for item in dummy:
            validcall += item.split('-')
        if text in validcall:
            return
        return ValidationError(_("Call name must be the given name that "
                                     "is normally used."))

    def _setup_fields(self):
        self.group_as = MonitoredEntry(
            self.top.get_object("group_as"),
            self.obj.set_group_as,
            self.obj.get_group_as,
            self.db.readonly)

        if not self.original_group_set:
            if self.global_group_set :
                self.group_as.force_value(self.global_group_as)
            else :
                self.group_as.force_value(self.obj.get_primary_surname().get_surname())

        format_list = [(name, number) for (number, name,fmt_str,act)
                       in name_displayer.get_name_format(also_default=True)]

        self.sort_as = MonitoredMenu(
            self.top.get_object('sort_as'),
            self.obj.set_sort_as,
            self.obj.get_sort_as,
            format_list,
            self.db.readonly)

        self.display_as = MonitoredMenu(
            self.top.get_object('display_as'),
            self.obj.set_display_as,
            self.obj.get_display_as,
            format_list,
            self.db.readonly)

        self.given_field = MonitoredEntry(
            self.top.get_object("given_name"),
            self.obj.set_first_name,
            self.obj.get_first_name,
            self.db.readonly)

        self.call_field = MonitoredEntry(
            self.top.get_object("call"),
            self.obj.set_call_name,
            self.obj.get_call_name,
            self.db.readonly)
        self.call_field.connect("validate", self._validate_call)
        #force validation now with initial entry
        self.call_field.obj.validate(force=True)

        self.title_field = MonitoredEntry(
            self.top.get_object("title_field"),
            self.obj.set_title,
            self.obj.get_title,
            self.db.readonly)

        self.suffix_field = MonitoredEntry(
            self.top.get_object("suffix"),
            self.obj.set_suffix,
            self.obj.get_suffix,
            self.db.readonly)

        self.nick = MonitoredEntry(
            self.top.get_object("nickname"),
            self.obj.set_nick_name,
            self.obj.get_nick_name,
            self.db.readonly)

        self.famnick = MonitoredEntry(
            self.top.get_object("familynickname"),
            self.obj.set_family_nick_name,
            self.obj.get_family_nick_name,
            self.db.readonly)

        #self.surname_field = MonitoredEntry(
        #    self.top.get_object("alt_surname"),
        #    self.obj.set_surname,
        #    self.obj.get_surname,
        #    self.db.readonly,
        #    autolist=self.db.get_surname_list() if not self.db.readonly else [],
        #    changed=self.update_group_as)

        self.date = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"),
            self.obj.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

        self.obj_combo = MonitoredDataType(
            self.top.get_object("ntype"),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            self.db.get_name_types(),
            )

        self.privacy = PrivacyButton(
            self.top.get_object("priv"), self.obj,
            self.db.readonly)

    def _create_tabbed_pages(self):

        notebook = self.top.get_object("notebook")

        self._add_tab(notebook, self.gennam)
        self.track_ref_for_deletion("gennam")

        self.srcref_list = CitationEmbedList(self.dbstate, self.uistate,
                                             self.track,
                                             self.obj.get_citation_list())
        self._add_tab(notebook, self.srcref_list)
        self.track_ref_for_deletion("srcref_list")

        self.note_tab = NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_list(),
                    notetype=NoteType.PERSONNAME)
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self._setup_notebook_tabs( notebook)

    def _get_global_grouping(self, srn):
        """ we need info on the global grouping of the surname on init,
            and on change of surname
            """
        self.global_group_as = self.db.get_name_group_mapping(srn)
        if srn == self.global_group_as:
            self.global_group_as = None
            self.global_group_set = False
        else:
            self.global_group_set = True


    def build_menu_names(self, name):
        if name:
            ntext = name_displayer.display_name(name)
            submenu_label = _('%(str1)s: %(str2)s') % {'str1' : _('Name'),
                                                       'str2' : ntext}
        else:
            submenu_label = _('New Name')
        menu_label = _('Name Editor')
        return (menu_label,submenu_label)

    def update_group_as(self, obj):
        """Callback if surname changes on GUI
            If overwrite is not set, we change the group name too
        """
        name = self.obj.get_primary_surname().get_surname()
        if not self.group_over.get_active():
            self.group_as.force_value(name)
        #new surname, so perhaps now a different grouping?
        self._get_global_grouping(name)
        if not self.group_over.get_active() and self.global_group_set :
            self.group_over.set_active(True)
            self.group_as.enable(True)
            self.toggle_dirty = True
            self.group_as.force_value(self.global_group_as)
        elif self.group_over.get_active() and self.toggle_dirty:
            #changing surname caused active group_over in past, change
            # group_over as we type
            if self.global_group_set :
                self.group_as.force_value(self.global_group_as)
            else:
                self.toggle_dirty = False
                self.group_as.force_value(name)
                self.group_over.set_active(False)
                self.group_as.enable(False)

    def on_group_over_toggled(self, obj):
        """ group over changes, if activated, enable edit,
            if unactivated, go back to surname/global_group_as.
        """
        self.toggle_dirty = False
        #enable group as box
        self.group_as.enable(obj.get_active())

        if not obj.get_active():
            if self.global_group_set:
                self.group_as.set_text(self.global_group_as)
            else:
                surname = self.obj.get_primary_surname().get_surname()
                self.group_as.set_text(surname)

    def save(self, *obj):
        """Save the name setting. All is ok, except grouping. We need to
           consider:
            1/     global set, not local set --> unset (ask if global unset)
            2/     global set,     local set --> unset (only local unset!)
            3/ not global set,     local set
            or not global set, not local set --> unset
            4/ not local set, not global set
            or not local set,     global set --> set val (ask global or local)
            5/     local set, not global set --> set (change local)
            6/     local set,     global set --> set (set to global if possible)
        """
        closeit = True
        surname = self.obj.get_primary_surname().get_surname()
        group_as= self.obj.get_group_as()
        grouping_active = self.group_over.get_active()

        if not grouping_active :
            #user wants to group with surname
            if self.global_group_set and not self.original_group_set :
                #warn that group will revert to surname
                from ..dialog import QuestionDialog2
                q = QuestionDialog2(
                    _("Break global name grouping?"),
                    _("All people with the name of %(surname)s will no longer "
                      "be grouped with the name of %(group_name)s."
                      ) % { 'surname' : surname,
                            'group_name':group_as},
                    _("Continue"),
                    _("Return to Name Editor"),
                    parent=self.window)
                val = q.run()
                if val:
                    #delete the grouping link on database
                    self.db.set_name_group_mapping(surname, None)
                    self.obj.set_group_as("")
                else :
                    closeit = False
            elif self.global_group_set and self.original_group_set:
                #we change it only back to surname locally, so store group_as
                # Note: if all surnames are locally changed to surname, we
                #       should actually unsed the global group here ....
                pass
            else :
                #global group not set, don't set local group too:
                self.obj.set_group_as("")
        else:
            #user wants to override surname, see what he wants
            if not self.original_group_set :
                #if changed, ask if this has to happen for the entire group,
                #this might be creation of group link, or change of group link
                if self.global_group_as != group_as:
                    from ..dialog import QuestionDialog2

                    q = QuestionDialog2(
                    _("Group all people with the same name?"),
                    _("You have the choice of grouping all people with the "
                      "name of %(surname)s with the name of %(group_name)s, or "
                      "just mapping this particular name."
                                       ) % { 'surname' : surname,
                                             'group_name':group_as},
                    _("Group all"),
                    _("Group this name only"),
                    parent=self.window)
                    val = q.run()
                    if val:
                        if group_as == surname :
                            self.db.set_name_group_mapping(surname, None)
                        else:
                            self.db.set_name_group_mapping(surname, group_as)
                        self.obj.set_group_as("")
                    else:
                        if self.global_group_set :
                            #allow smith to Dummy, but one person still Smith
                            self.obj.set_group_as(group_as)
                        elif group_as == surname :
                            self.obj.set_group_as("")
                        else:
                            self.obj.set_group_as(group_as)
                else:
                    #keep original value, no original group
                    self.obj.set_group_as("")
            elif not self.global_group_set :
                #don't ask user, group was set locally before,
                #change it locally only
                if group_as == surname :
                    #remove grouping
                    self.obj.set_group_as("")
                else:
                    pass

            else:
                #locally set group and global group set
                if group_as == self.global_group_as :
                    #unset local group, go with global one
                    self.obj.set_group_as("")
                else :
                    #local set is different from global, keep it like that
                    pass

        if closeit:
            if self.callback:
                self.callback(self.obj)
            self.callback = None
            self.close()

    def _cleanup_on_exit(self):
        """
        Somehow it was decided that a database value of group="" is represented
        in the GUI by a widget with a group="surname" which is disabled. So if
        the group_as widget is disabled then remove the group from the name
        otherwise gramps thinks the name has changed resulting in asking if
        data must be saved, and also bug 1892 occurs on reopening of the editor.
        """
        # can't use group_over, see Note in gen/lib/name/Name.set_group_as().
        if not self.group_as.obj.get_editable():
            self.obj.set_group_as("")
        EditSecondary._cleanup_on_exit(self)
