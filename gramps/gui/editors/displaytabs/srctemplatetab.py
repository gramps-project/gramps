#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2013       Tim G L Lyons
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger('.template')

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------
from gramps.gen.lib.srcattrtype import (SrcAttributeType, REF_TYPE_F, 
                                REF_TYPE_S, REF_TYPE_L, EMPTY)
from gramps.gen.lib import SrcAttribute, SrcTemplate, SrcTemplateList
from gramps.gen.plug.report.utils import get_address_ref_str
from ...autocomp import StandardCustomSelector
from ...widgets.srctemplatetreeview import SrcTemplateTreeView
from ...widgets import (UndoableEntry, MonitoredEntryIndicator, MonitoredDate,
                        ValidatableMaskedEntry)
from .grampstab import GrampsTab
from gramps.gen.constfunc import STRTYPE

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------
class SrcTemplateTab(GrampsTab):
    """
    This class provides the tabpage for template generation of attributes.
    """
    def __init__(self, dbstate, uistate, track, src, glade,
                 callback_src_changed):
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
        @param src: source which we manage in this tab
        @type src: gen.lib.Source
        @param glade: glade objects with the needed widgets
        """
        self.src = src
        self.glade = glade
        self.callback_src_changed = callback_src_changed
        self.readonly = dbstate.db.readonly

        self.autoset_title = False

        GrampsTab.__init__(self, dbstate, uistate, track, _("Source Template"))
        eventbox = Gtk.EventBox()
        widget = self.glade.get_object('gridtemplate')
        eventbox.add(widget)
        self.pack_start(eventbox, True, True, 0)
        self._set_label(show_image=False)
        widget.connect('key_press_event', self.key_pressed)
        
        self.tmplfields = TemplateFields(self.dbstate.db, self.uistate,
                self.track, self.glade.get_object('gridfields'),
                self.src, None, self.callback_src_changed, None)
        self.autotitle = self.glade.get_object("autotitle_checkbtn")
        #self.vbox_fields_label = self.glade.get_object('fields_01')
        #self.vbox_fields_input = self.glade.get_object('fields_02')
        self.setup_interface(self.glade.get_object('scrolledtemplates'))
        self.show_all()

    def make_active(self):
        """
        Called by using editor to focus on correct field in the tab
        """
        self.temp_tv.grab_focus()

    def is_empty(self):
        """
        Override base class
        """
        return False

    def setup_interface(self, scrolled):
        """
        Set all information on the widgets
        * template selection
        * setting attribute fields
        
        :param scrolled: GtkScrolledWindow to which to add treeview with templates
        """
        templ = self.src.get_template()
        self.temp_tv = SrcTemplateTreeView(templ,
                                sel_callback=self.on_template_selected)
        scrolled.add(self.temp_tv)
        
        #autotitle checkbox
        self.autotitle.set_active(self.autotitle_get_orig_val())
        self.autotitle.set_sensitive(not self.dbstate.db.readonly)
        self.autotitle.connect('toggled', self.autotitle_on_toggle)

    def autotitle_get_orig_val(self):
        """
        If title of the source is what we would set with autotitle, we set
        the checkbox to true. Otherwise to False
        """
        srctemp = SrcTemplateList().get_template_from_name(self.src.get_template())
        srctemp.set_attr_list(self.src.get_attribute_list())
        title = srctemp.title_gedcom()
        if self.src.get_title() == title:
            self.autoset_title = True
        else:
            self.autoset_title = False
        return self.autoset_title

    def autotitle_on_toggle(self, obj):
        """ the autoset_title attribute will be used in editsource to 
        determine that title must be set
        """
        self.autoset_title = obj.get_active()
        #it might be that the title must be changed, so we trigger the callback
        # which will update the title in the source object
        self.callback_src_changed()

    def on_template_selected(self, key):
        """
        Selected template changed, we save this and update interface
        """
        self.src.set_template(key)
        self.callback_src_changed(templatechanged=True)
        
        #a predefined template, 
        self.tmplfields.reset_template_fields(key)

#-------------------------------------------------------------------------
#
# TemplateFields Class
#
#-------------------------------------------------------------------------
class TemplateFields(object):
    """
    Class to manage fields of a source template.
    Can be used on source and on citation level.
    """
    def __init__(self, db, uistate, track, grid, src, cite,
                 callback_src_changed, callback_cite_changed):
        """
        grid: The Gtk.Grid that should hold the fields
        src : The source to which the fields belong
        cite: The citation to which the fields belong (set None if only source)
        """
        self.gridfields = grid
        self.db = db
        self.uistate = uistate
        self.track = track
        self.src = src
        self.cite = cite
        self.callback_src_changed = callback_src_changed
        self.callback_cite_changed = callback_cite_changed
        
        #storage
        self.lbls = []
        self.inpts = []
        self.btns = []
        self.monentry = []

    def reset_template_fields(self, key):
        """
        Method that constructs the actual fields where user can enter data.
        Template must be the index of the template.
        """
        show_default_cite_fields = False #we don't do this for now
        #obtain the template of the key
        if SrcTemplateList().template_defined(key):
            #a predefined template, 
            template = SrcTemplateList().get_template_from_name(key).get_structure()
            telist = SrcTemplateList().get_template_from_name(key).get_template_element_list()
        else:
            LOG.warn("template not defined %s" % key)
            return
        
        # first remove old fields
        for lbl in self.lbls:
            self.gridfields.remove(lbl)
        for inpt in self.inpts:
            self.gridfields.remove(inpt)
        for mon in self.monentry:
            del mon
        for btn in self.btns:
            self.gridfields.remove(btn)
        self.lbls = []
        self.inpts = []
        self.monentry = []
        self.btns = []
        row = 1
        # now add new fields
        long_source_fields = [x for x in telist
                              if not x.get_short() and not x.get_citation()]
        short_source_fields = [x for x in telist
                               if x.get_short() and not x.get_citation()]
        long_citation_fields = [x for x in telist
                                if not x.get_short() and x.get_citation()]
        short_citation_fields = [x for x in telist
                                 if x.get_short() and x.get_citation()]
        
        if self.cite is None:
            # source long fileds
            for te in long_source_fields:
                self._add_entry(row, te.get_name(), _(te.get_display()),
                                _(te.get_hint()), _(te.get_tooltip()))
                row += 1
            
            # now add short source fields (if any)
            if short_source_fields:
                self.gridfields.insert_row(row)
                lbl = Gtk.Label('')
                lbl.set_markup(_("<b>Optional Short Versions:</b>"))
                lbl.set_halign(Gtk.Align.START)
                self.gridfields.attach(lbl, 0, row-1, 2, 1)
                self.lbls.append(lbl)
                row += 1
                for te in short_source_fields:
                    self._add_entry(row, te.get_name(), _(te.get_display()),
                                    _(te.get_hint()), _(te.get_tooltip()))
                    row += 1
            
            # At source level add a header for the default citation values
            if (long_citation_fields+short_citation_fields) and \
                            show_default_cite_fields:
                self.gridfields.insert_row(row)
                lbl = Gtk.Label('')
                lbl.set_markup(_("<b>Optional Default Citation Fields:</b>"))
                lbl.set_halign(Gtk.Align.START)
                self.gridfields.attach(lbl, 0, row-1, 2, 1)
                self.lbls.append(lbl)
                row += 1
        
        # Either show citation fields or at source level the default values
        if show_default_cite_fields or (not self.cite is None):
            for te in long_citation_fields:
                self._add_entry(row, te.get_name(), _(te.get_display()),
                                _(te.get_hint()), _(te.get_tooltip()))
                row += 1
            
        # Finally the short citation fields (if any)
        if not self.cite is None:
            #we indicate with a text these are the short versions
            if short_citation_fields:
                self.gridfields.insert_row(row)
                lbl = Gtk.Label('')
                lbl.set_markup(_("<b>Optional Short Versions:</b>"))
                lbl.set_halign(Gtk.Align.START)
                self.gridfields.attach(lbl, 0, row-1, 2, 1)
                self.lbls.append(lbl)
                row += 1
        if show_default_cite_fields or (not self.cite is None):
            for te in short_citation_fields:
                self._add_entry(row, te.get_name(), _(te.get_display()),
                                _(te.get_hint()), _(te.get_tooltip()))
                row += 1
        
        self.gridfields.show_all()

    def _add_entry(self, row, srcattrtype, alt_label, hint=None, tooltip=None):
        """
        Add an entryfield to the grid of fields at row row, to edit the given
        srcattrtype value. Use alt_label if given to indicate the field
        (otherwise the srcattrtype string description is used)
        Note srcattrtype should actually be the integer key of the type!
        """
        self.gridfields.insert_row(row)
        field = srcattrtype
        if isinstance(field, STRTYPE):
            raise NotImplementedError("type must be the integer key")
        #setup label
        if alt_label:
            label = alt_label
        else:
            srcattr = SrcAttributeType(field)
            label = str(srcattr)
        lbl = Gtk.Label(_("%s:") % label)
        lbl.set_halign(Gtk.Align.START)
        self.gridfields.attach(lbl, 0, row-1, 1, 1)
        self.lbls.append(lbl)
        if srcattrtype in [SrcAttributeType.REPOSITORY,
                SrcAttributeType.REPOSITORY_ADDRESS,
                SrcAttributeType.REPOSITORY_CALL_NUMBER]:
            self._add_repo_entry(srcattrtype, row)
        elif self.cite and srcattrtype == SrcAttributeType.DATE:
            #the DATE on level citation is not an attribute but stored
            #as date in the citation
            self._add_cite_date(row)
        else:
            #setup entry
            self._add_normal_entry(srcattrtype, row, hint, tooltip)

    def _add_normal_entry(self, srcattrtype, row, hint, tooltip):
        """
        add an entryfield that sets the required SrcAttribute
        """
        inpt = UndoableEntry()
        inpt.set_halign(Gtk.Align.FILL)
        inpt.set_hexpand(True)
        if tooltip:
            inpt.set_tooltip_text(tooltip)
        self.gridfields.attach(inpt, 1, row-1, 1, 1)
        self.inpts.append(inpt)
        if self.cite:
            MonitoredEntryIndicator(inpt, self.set_cite_field, self.get_cite_field,
                           hint or "",
                           read_only=self.db.readonly, 
                           parameter=srcattrtype)
        else:
            MonitoredEntryIndicator(inpt, self.set_src_field, self.get_src_field,
                           hint or "",
                           read_only=self.db.readonly, 
                           parameter=srcattrtype)

    def _add_cite_date(self, row):
        """
        Add the entry corresponding to the date field on citation level
        """
        inpt = ValidatableMaskedEntry()
        inpt.set_halign(Gtk.Align.FILL)
        inpt.set_hexpand(True)
        inpt.set_tooltip_text("The date of the entry in the source you are"
            " referencing with this citation. E.g. the date a house was visited"
            " during a census , or the date an entry was made in a"
            " birth log/registry")
        self.gridfields.attach(inpt, 1, row-1, 1, 1)
        self.inpts.append(inpt)
        btn = self.make_btn('gramps-date')
        self.gridfields.attach(btn, 2, row-1, 1, 1)
        self.btns.append(btn)
        MonitoredDate(
            inpt,
            btn, 
            self.cite.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

    def _add_repo_entry(self, srcattrtype, row):
        """
        Add a field that obtains info from repository
        """
        repo_list = self.src.get_reporef_list()
        if repo_list:
            reporef = repo_list[0]
            repo = self.db.get_repository_from_handle(reporef.get_reference_handle())
        else:
            reporef = None
            repo = None
        if not reporef:
            lbl = Gtk.Label("")
            lbl.set_markup(_("<i>No repository added to the source</i>"))
            lbl.set_halign(Gtk.Align.START)
            self.gridfields.attach(lbl, 1, row-1, 1, 1)
            self.lbls.append(lbl)
        else:
            #we show the data as defined by the field
            if srcattrtype == SrcAttributeType.REPOSITORY:
                text = repo.get_name()
            elif srcattrtype == SrcAttributeType.REPOSITORY_ADDRESS:
                text = _("<i>No Address attached to the repository</i>")
                addrlist = repo.get_address_list()
                if addrlist:
                    text = get_address_ref_str(addrlist[0])
            elif srcattrtype == SrcAttributeType.REPOSITORY_CALL_NUMBER:
                text = reporef.get_call_number().strip()
                if not text:
                    text = _("<i>No call number given in the repository reference</i>")
            lbl = Gtk.Label("")
            lbl.set_markup(text)
            lbl.set_halign(Gtk.Align.START)
            self.gridfields.attach(lbl, 1, row-1, 1, 1)
            self.lbls.append(lbl)

    def make_btn(self, stockid):
        """
        Create a button for use with a stock image
        """
        image = Gtk.Image.new_from_stock('gramps-date', Gtk.IconSize.MENU)
        btn = Gtk.Button()
        btn.set_image(image)
        btn.set_always_show_image(True)
        return btn

    def get_src_field(self, srcattrtype):
        return self.__get_field(srcattrtype, self.src)

    def get_cite_field(self, srcattrtype):
        return self.__get_field(srcattrtype, self.cite)

    def __get_field(self, srcattrtype, obj):
        """
        Obtain srcattribute with type srcattrtype, where srcattrtype is an
        integer key!
        """
        val = ''
        for attr in obj.attribute_list:
            if int(attr.get_type()) == srcattrtype:
                val = attr.get_value()
                break
        return val

    def set_src_field(self, value, srcattrtype):
        self.__set_field(value, srcattrtype, self.src)
        #indicate source object changed
        self.callback_src_changed()

    def set_cite_field(self, value, srcattrtype):
        self.__set_field(value, srcattrtype, self.cite)
        #indicate source object changed
        self.callback_cite_changed()

    def __set_field(self, value, srcattrtype, obj):
        """
        Set attribute of source of type srcattrtype (which is integer!) to 
        value. If not present, create attribute. If value == '', remove
        """
        value = value.strip()
        foundattr = None
        for attr in obj.attribute_list:
            if int(attr.get_type()) == srcattrtype:
                attr.set_value(value)
                foundattr = attr
                break
        if foundattr and value == '':
            obj.remove_attribute(foundattr)
        if foundattr is None and value != '':
            foundattr = SrcAttribute()
            foundattr.set_type(srcattrtype)
            foundattr.set_value(value)
            obj.add_attribute(foundattr)
