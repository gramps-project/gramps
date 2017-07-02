#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017   Alois Poettker
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

"Import from Pro-Gen"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os, time
from gi.repository import Gtk, Gdk

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

from gramps.gen.config import config

from gramps.gen.lib import Citation
from gramps.gen.lib.date import Date, Today
from gramps.gen.lib.datebase import DateBase
from gramps.gen.utils.libformatting import ImportInfo

from gramps.gui.dialog import InfoDialog
from gramps.gui.display import display_help
from gramps.gui.glade import Glade
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.widgets import (MonitoredCheckbox, MonitoredDate,
                                MonitoredEntry, MonitoredMenu, PrivacyButton)

from gramps.plugins.lib import libprogen

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Importer' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Import_from_another_genealogy_program')

#-------------------------------------------------------------------------
#
# importData
#
#-------------------------------------------------------------------------
class ImportPrivacy(object):
    """ Class for internal values of privacy objects """

    def __init__(self, value):
        """"""
        self.priv_value = value

    # sets / gets Privacy value
    def set_privacy(self, value):
        """ connects to 'set' method of PrivacyCheckbox """
        self.priv_value = value
    def get_privacy(self):
        """ connects to 'get' method of PrivacyCheckbox """
        return self.priv_value

class ImportValue(object):
    """ Class for internal values of objects """

    def __init__(self, value):
        """"""
        self.value = value

    # sets / gets Button value
    def set_value(self, value):
        """ connects to 'set' method of MonitoredCheckbox """
        self.value = value
    def get_value(self):
        """ connects to 'get' method of MonitoredCheckbox """
        return self.value

class ImportEntry(object):
    """ Class for internal entrys of objects """

    def __init__(self, entry):
        """"""
        self.entry = entry

    # sets / gets Entry text
    def set_entry(self, entry):
        """ connects to 'set' method of MonitoredEntry """
        self.entry = entry
    def get_entry(self):
        """ connects to 'get' method of MonitoredEntry """
        return self.entry

class ImportSourceCitation(object):
    """ Class for internal values for source / citation objects """

    def __init__(self, dflt_btn, dflt_text, text, fname, date):
        """"""
        self.source_btn = ImportValue(dflt_btn)
        self.source_title = ImportEntry(_('Import from Pro-Gen (%s)') % fname)
        self.source_priv = ImportPrivacy(False)
        self.citation_btn = ImportValue(dflt_btn)
        self.citation_page = ImportEntry('%s' % dflt_text)
        self.citation_priv = ImportPrivacy(False)
        self.citation_conf = ImportValue(Citation.CONF_HIGH)
        self.citation_attr = ImportEntry('%s (%s) %s' % (text, fname, date))

class ImportTagTextDefault(object):
    """ Class for internal values for default objects """

    def __init__(self, text, fname):
        """"""
        self.dflt_text = ImportEntry(text)
        self.dflt_file = ImportEntry(fname)
        self.dflt_date = Date()

    # sets / gets Default entries
    def set_dfltdate(self, date):
        """ connects to 'set' method of MonitoredDate """
        self.dflt_date = date
    def get_dfltdate(self):
        """ connects to 'get' method of MonitoredDate """
        return self.dflt_date.text

class ImportTagText(object):
    """ Class for internal values for tag objects """

    def __init__(self, text, fname, date):
        """"""
        self.tag_obj = ImportValue(True)
        self.tag_file = ImportValue(True)
        self.tag_date = ImportValue(True)
        self.act_text, self.dflt_file, self.dflt_date = text, fname, date
        self.tag_text = "%s(%s)%s" % (text, fname, date)

    def set_tagtext(self, text):
        """ connects to 'set' method of MonitoredEntry """
        # \xa0 as (non breakable) space to separate text elements
        self.act_text = text.split('\xa0')[0].rstrip()
    def get_tagtext(self):
        """ connects to 'get' method of MonitoredEntry """
        self.tag_text = self.act_text
        if self.tag_file.get_value():
            self.tag_text += '\xa0(%s)' % self.dflt_file
        if self.tag_date.get_value():
            self.tag_text += '\xa0%s' % self.dflt_date
        return self.tag_text

def _importData(database, filename, user):
    """
    Imports the files corresponding to the specified Database, Filename & User.
    """
    data = ProgenOptions(database, filename, user)
    if data.fail:   # 'Cancel' button pressed
        return

    data = libprogen.ProgenParser(database, filename, user, data.option)
    try:
        info = libprogen.ProgenParser.parse_progen_file(data)
    except libprogen.ProgenError as msg:
        user.notify_error(_("Pro-Gen data error"), str(msg))
        return
    except IOError as msg:
        user.notify_error(_("%s could not be opened") % filename, str(msg))
        return

    if info:   # successful import
        # display qualified/standard statistic window
        if user.uistate:
            InfoDialog(_('Import Statistics'), info.info_text(),
                       parent=user.parent)
        else:
            return ImportInfo({_("Results"): _("done")})

class ProgenOptions(ManagedWindow):
    """ Class for Pro-Gen files import optons"""

    def __init__(self, database, filename, user):
        """ Useful options for Pro-Gen import """
        self.dbase = database
        self.fname = filename
        self.user = user
        self.uistate = user.uistate
        self.option = {}

        # default: Pro-Gen import failed
        self.fail = True

        # initial values
        fname = os.path.basename(filename).split('\\')[-1]
        date = time.strftime("%Y-%m-%d")
        text = "Pro-Gen Import"

        # add import source title/confidence
        #            citation page/confidence/privacy/attribute
        self.import_methods = {}
        dflt = config.get('preferences.default-source')
        if config.get('preferences.tag-on-import'):
            dflt_text = config.get('preferences.tag-on-import-format')
        else:
            dflt_text = '%s %s' % (text, date)
        self.imp_values = ImportSourceCitation \
            (dflt, dflt_text, text, fname, date)

        # add default text / filename / current date
        self.default_methods = {}
        self.default_values = ImportTagTextDefault(text, fname)

        # add tagobjects text / filename / date
        self.tagobj_status = True
        self.tagobj_values, self.tagobj_methods = {}, {}
        self.tagtext_methods = {}
        self.tagfile_status, self.tagfile_methods = True, {}
        self.tagdate_status, self.tagdate_methods = True, {}
        for obj in libprogen.TAGOBJECTS:
            self.tagobj_values[obj] = ImportTagText(text, fname, date)

        # add primary object values
        self.primobj_values, self.primobj_methods = {}, {}
        for obj in libprogen.PRIMOBJECTS:
            self.primobj_values[obj] = ImportValue(True)

        # add options values
        self.option_values, self.option_methods = {}, {}
        for obj in libprogen.OPTOBJECTS:
            if obj in ['person-ident', 'family-ident', \
                       'surname-female', 'death-cause']:
                self.option_values[obj] = ImportValue(True)
            else:
                self.option_values[obj] = ImportValue(False)

        # prepare option dictionary
        self._collect()

        # display window if GUI active
        if self.uistate:
            ManagedWindow.__init__(self, self.uistate, [], self.__class__)
            self._display()

    def __on_source_button_toggled(self, widget):
        """ compute the source button and toggle the 'Sensitive' attribute """
        obj_state = widget.get_active()
        for obj in ['title', 'priv']:
            imp_obj = self.glade.get_object('imp_source_%s' % obj)
            imp_obj.set_sensitive(obj_state)

    def __on_citation_button_toggled(self, widget):
        """ compute the citation button and toggle the 'Sensitive' attribute """
        obj_state = widget.get_active()
        for obj in ['page', 'attr', 'conf', 'priv']:
            imp_obj = self.glade.get_object('imp_citation_%s' % obj)
            imp_obj.set_sensitive(obj_state)

    def __on_import_entry_keyrelease(self, widget, event, data=None):
        """ activated on all return's of an entry"""
        if event.keyval in [Gdk.KEY_Return]:
            obj_name = Gtk.Buildable.get_name(widget).split('_', 1)[1]
            if obj_name == 'citation_page':
                obj_next = self.glade.get_object('imp_citation_attr')
                obj_next.grab_focus()

    def __on_object_button_clicked(self, widget=None):
        """ compute all primary objects and toggle the 'Active' attribute """
        self.tagobj_status = not self.tagobj_status

        for obj in libprogen.TAGOBJECTS:
            tag_obj = self.glade.get_object('tag_%s_obj' % obj)
            tag_obj.set_active(self.tagobj_status)

    def __on_object_button_toggled(self, widget):
        """ compute the primary object and toggle the 'Sensitive' attribute """
        obj_state = widget.get_active()
        obj_name = Gtk.Buildable.get_name(widget)
        obj_name = obj_name.split('_', 1)[1].split('_', 1)[0]

        for obj in ['file', 'date', 'text']:
            tag_obj = self.glade.get_object('tag_%s_%s' % (obj_name, obj))
            tag_obj.set_sensitive(obj_state)

    def __on_text_button_clicked(self, widget=None):
        """ compute all primary objects and flush the 'text' field """
        self.__on_tagtext_entry_resume(default=True)   # Resume tag text

    def __on_tagtext_entry_keyrelease(self, widget, event, data=None):
        """ activated on all return's of an entry """
        if event.keyval in [Gdk.KEY_Return]:
            obj_name = Gtk.Buildable.get_name(widget)
            obj_name = obj_name.split('_', 1)[1].split('_', 1)[0]
            obj_index = libprogen.TAGOBJECTS.index(obj_name)
            if obj_index < len(libprogen.TAGOBJECTS) -1:
                obj_index = obj_index +1
            obj_next = self.glade.get_object('tag_%s_text' % \
                                             libprogen.TAGOBJECTS[obj_index])
            obj_next.grab_focus()

    def __on_tagtext_entry_resume(self, default=True):
        """ resume new tagtext from old + file & date variables"""
        for obj in libprogen.TAGOBJECTS:
            tag_obj = self.glade.get_object('tag_%s_text' % obj)
            if not tag_obj.get_sensitive():
                continue

            if default:
                obj_entry = self.default_values.dflt_text.get_entry()
            else:
                obj_entry = self.tagobj_values[obj].act_text
            self.tagobj_values[obj].set_tagtext(obj_entry)
            self.tagtext_methods[obj].update()

    def __on_file_button_clicked(self, widget=None):
        """ compute all primary objects and toggle the 'file' attribute """
        self.tagfile_status = not self.tagfile_status

        for obj in libprogen.TAGOBJECTS:
            tag_obj = self.glade.get_object('tag_%s_file' % obj)
            if not tag_obj.get_sensitive():
                continue

            self.tagfile_methods[obj].set_val(self.tagfile_status)
            tag_obj.set_active(self.tagfile_status)

        self.__on_tagtext_entry_resume(default=False)   # Resume tag text

    def __on_file_button_toggled(self, widget):
        """ compute the primary object and toggle the 'Sensitive' attribute """
        self.__on_tagtext_entry_resume(default=False)

        obj_name = Gtk.Buildable.get_name(widget)
        obj_name = obj_name.split('_', 1)[1].split('_', 1)[0]
        obj_index = libprogen.TAGOBJECTS.index(obj_name)
        if obj_index < len(libprogen.TAGOBJECTS) -1:
            obj_index = obj_index +1
        obj_next = self.glade.get_object('tag_%s_file' % \
                                         libprogen.TAGOBJECTS[obj_index])
        obj_next.grab_focus()

    def __on_date_button_clicked(self, widget=None):
        """ compute all primary objects and toggle the 'date' attribute """
        self.tagdate_status = not self.tagdate_status

        for obj in libprogen.TAGOBJECTS:
            tag_obj = self.glade.get_object('tag_%s_date' % obj)
            if not tag_obj.get_sensitive():
                continue

            self.tagdate_methods[obj].set_val(self.tagdate_status)
            tag_obj.set_active(self.tagdate_status)

        self.__on_tagtext_entry_resume(default=False)   # Resume tag text

    def __on_date_button_toggled(self, widget):
        """ compute the primary object and toggle the 'Sensitive' attribute """
        self.__on_tagtext_entry_resume(default=False)

        obj_name = Gtk.Buildable.get_name(widget)
        obj_name = obj_name.split('_', 1)[1].split('_', 1)[0]
        obj_index = libprogen.TAGOBJECTS.index(obj_name)
        if obj_index < len(libprogen.TAGOBJECTS) -1:
            obj_index = obj_index +1
        obj_next = self.glade.get_object('tag_%s_date' % \
                                         libprogen.TAGOBJECTS[obj_index])
        obj_next.grab_focus()

    def __on_primobj_button_toggled(self, widget):
        """ compute all primary objects and toggle the 'primobj' attribute """
        obj_name = Gtk.Buildable.get_name(widget)
        obj_name = obj_name.split('_', 1)[1].split('_', 1)[0]

        for i, obj_i in enumerate(libprogen.PRIMOBJECTS):
            if obj_name == libprogen.PRIMOBJECTS[i]:
                prim_obj = self.glade.get_object('prim_%s_btn' % obj_i)
                if not prim_obj.get_active():
                    # Prim. object deactivated:
                    # check all in list below and deactivate
                    for obj_ii in libprogen.PRIMOBJECTS[(i +1):]:
                        sec_obj = self.glade.get_object('prim_%s_btn' % obj_ii)
                        sec_obj.set_active(False)
                    break
                else:
                    # Prim. object activated: check all in list above
                    # if one prim. object is deactive:
                    # deactivate this prim. object too
                    for obj_ii in libprogen.PRIMOBJECTS[:i]:
                        sec_obj = self.glade.get_object('prim_%s_btn' % obj_ii)
                        if not sec_obj.get_active():
                            prim_obj.set_active(False)
                            break

    def __on_surname_button_toggled(self, widget):
        """ compute surname objects and """
        obj_name = Gtk.Buildable.get_name(widget)
        obj_name = obj_name.split('_', 1)[1].split('_', 1)[0]
        obj_status = widget.get_active()

        if (obj_name == 'name-surmale') and (obj_status == True):
            sec_obj = self.glade.get_object('opt_surname-female_btn')
            sec_obj.set_active(False)
        if (obj_name == 'name-surfemale') and (obj_status == True):
            sec_obj = self.glade.get_object('opt_surname-male_btn')
            sec_obj.set_active(False)

    def __on_x_button_clicked(self, widget=None):
        """ cancel the import and close """
        self.fail = True   # Pro-Gen import canceled

    def __on_ok_button_clicked(self, widget=None):
        """ execute the import and close """
        self._collect()
        self.close()

        self.fail = False   # Pro-Gen import proceed

    def __on_cancel_button_clicked(self, widget=None):
        """ cancel the import and close """
        self.close()

        self.fail = True   # Pro-Gen import canceled

    def __on_help_button_clicked(self, widget=None):
        """ display the relevant portion of Gramps manual """
        self.fail = True

        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def build_menu_names_(self, widget=None):
        """ The menu name """
        return (_('Main window'), _("Import Pro-Gen"))

    def _display(self):
        """ organize Glade 'Import Pro-Gen' window """

        # get the main window from glade
        self.glade = Glade('importprogen.glade')
        self.set_window(self.glade.toplevel, self.glade.get_object('title'),
                        _('Import Pro-Gen'))

        # calculate all entries and update Glade window
        # Text for Source / Citation objects
        for obj in ('source_btn', 'citation_btn'):
            widget = self.glade.get_object('imp_%s' % obj)
            set_import = eval('self.imp_values.%s.set_value' % obj)
            get_import = eval('self.imp_values.%s.get_value' % obj)
            self.import_methods[obj] = MonitoredCheckbox(\
                widget, widget, set_import, get_import, self.dbase.readonly)
        for obj in ('source_title', 'citation_page', 'citation_attr'):
            widget = self.glade.get_object('imp_%s' % obj)
            set_import = eval('self.imp_values.%s.set_entry' % obj)
            get_import = eval('self.imp_values.%s.get_entry' % obj)
            self.import_methods[obj] = MonitoredEntry(\
                widget, set_import, get_import, self.dbase.readonly)
        widget = self.glade.get_object('imp_citation_conf')
        self.import_methods['conf'] = MonitoredMenu(widget,
            self.imp_values.citation_conf.set_value,
            self.imp_values.citation_conf.get_value,
            [(_('Very Low'), Citation.CONF_VERY_LOW),
             (_('Low'), Citation.CONF_LOW),
             (_('Normal'), Citation.CONF_NORMAL),
             (_('High'), Citation.CONF_HIGH),
             (_('Very High'), Citation.CONF_VERY_HIGH)],
            self.dbase.readonly)
        widget = self.glade.get_object('imp_source_priv')
        get_import = eval('self.imp_values.source_priv')
        self.import_methods['source_priv'] = PrivacyButton(\
            widget, get_import, self.dbase.readonly)
        widget = self.glade.get_object('imp_citation_priv')
        get_import = eval('self.imp_values.citation_priv')
        self.import_methods['citation_priv'] = PrivacyButton(\
            widget, get_import, self.dbase.readonly)

        # Text (w. Defaults) for Tags
        for obj in ('text', 'file'):
            widget = self.glade.get_object('tag_default_%s' % obj)
            set_import = eval('self.default_values.dflt_%s.set_entry' % obj)
            get_import = eval('self.default_values.dflt_%s.get_entry' % obj)
            self.default_methods[obj] = MonitoredEntry(\
                widget, set_import, get_import, self.dbase.readonly)
        date = Today()
        datebase = DateBase()
        datebase.set_date_object(date)
        self.default_methods['date'] = MonitoredDate(\
            self.glade.get_object('tag_default_date'),
            self.glade.get_object('tag_default_date_btn'),
            datebase.get_date_object(),
            self.uistate, [], self.dbase.readonly)
        self.default_values.set_dfltdate(date)

        for obj in libprogen.TAGOBJECTS:
            # populate object fields with values
            widget = self.glade.get_object('tag_%s_obj' % obj)
            self.tagobj_methods[obj] = MonitoredCheckbox(widget, widget,
                self.tagobj_values[obj].tag_obj.set_value,
                self.tagobj_values[obj].tag_obj.get_value)
            widget = self.glade.get_object('tag_%s_text' % obj)
            self.tagtext_methods[obj] = MonitoredEntry(widget,
                self.tagobj_values[obj].set_tagtext,
                self.tagobj_values[obj].get_tagtext)
            widget = self.glade.get_object('tag_%s_file' % obj)
            self.tagfile_methods[obj] = MonitoredCheckbox(widget, widget,
                self.tagobj_values[obj].tag_file.set_value,
                self.tagobj_values[obj].tag_file.get_value)
            widget = self.glade.get_object('tag_%s_date' % obj)
            self.tagdate_methods[obj] = MonitoredCheckbox(widget, widget,
                self.tagobj_values[obj].tag_date.set_value,
                self.tagobj_values[obj].tag_date.get_value)

        # button's for primary objects
        for obj in libprogen.PRIMOBJECTS:
            # populate pirm. Object buttons with values
            widget = self.glade.get_object('prim_%s_btn' % obj)
            set_import = eval("self.primobj_values['%s'].set_value" % obj)
            get_import = eval("self.primobj_values['%s'].get_value" % obj)
            self.primobj_methods[obj] = MonitoredCheckbox(\
                widget, widget, set_import, get_import, self.dbase.readonly)

        # button's for miscallaneous option's
        for obj in libprogen.OPTOBJECTS:
            # populate option buttons with values
            widget = self.glade.get_object('opt_%s_btn' % obj)
            set_import = eval("self.option_values['%s'].set_value" % obj)
            get_import = eval("self.option_values['%s'].get_value" % obj)
            self.option_methods[obj] = MonitoredCheckbox(\
                widget, widget, set_import, get_import, self.dbase.readonly)

        # connect signals
        self.glade.connect_signals({
            "on_source_button_toggled" : self.__on_source_button_toggled,
            "on_citation_button_toggled" : self.__on_citation_button_toggled,
            "on_import_entry_keyrelease" : self.__on_import_entry_keyrelease,
            "on_tagtext_entry_keyrelease" : self.__on_tagtext_entry_keyrelease,
            "on_object_button_clicked" : self.__on_object_button_clicked,
            "on_object_button_toggled" : self.__on_object_button_toggled,
            "on_text_button_clicked" : self.__on_text_button_clicked,
            "on_file_button_clicked" : self.__on_file_button_clicked,
            "on_file_button_toggled" : self.__on_file_button_toggled,
            "on_date_button_clicked" : self.__on_date_button_clicked,
            "on_date_button_toggled" : self.__on_date_button_toggled,
            "on_primobj_button_toggled" : self.__on_primobj_button_toggled,
            "on_surname_button_toggled" : self.__on_surname_button_toggled,
            "on_x_button_clicked" : self.__on_x_button_clicked,
            "on_help_button_clicked" : self.__on_help_button_clicked,
            "on_cancel_button_clicked" : self.__on_cancel_button_clicked,
            "on_ok_button_clicked" : self.__on_ok_button_clicked
        })

        # state of two objects trigged form configuration
        widget = self.glade.get_object('imp_source_btn')
        self.__on_source_button_toggled(widget)
        widget = self.glade.get_object('imp_citation_btn')
        self.__on_citation_button_toggled(widget)
        widget = self.glade.get_object('import_ok')
        widget.grab_focus()

        # creates a modal window and display immediatly!
        self.glade.toplevel.run()

    def _collect(self):
        """ collect all options """

        self.option['imp_source_title'] = self.imp_values.source_title.get_entry() \
            if self.imp_values.source_btn.get_value() else ''
        self.option['imp_source_priv'] = self.imp_values.source_priv.get_privacy() \
            if self.imp_values.source_btn.get_value() else False
        self.option['imp_citation_page'] = self.imp_values.citation_page.get_entry() \
            if self.imp_values.citation_btn.get_value() else ''
        self.option['imp_citation_attr'] = self.imp_values.citation_attr.get_entry() \
            if self.imp_values.citation_btn.get_value() else ''
        self.option['imp_citation_conf'] = self.imp_values.citation_conf.get_value() \
            if self.imp_values.citation_btn.get_value() else Citation.CONF_HIGH
        self.option['imp_citation_priv'] = self.imp_values.citation_priv.get_privacy() \
            if self.imp_values.citation_btn.get_value() else False

        for obj in libprogen.TAGOBJECTS:
            self.option['tag_%s' % obj] = self.tagobj_values[obj].get_tagtext() \
            if self.tagobj_values[obj].tag_text else ''

        for obj in libprogen.PRIMOBJECTS:
            self.option['prim_%s' % obj] = self.primobj_values[obj].get_value()

        for obj in libprogen.OPTOBJECTS:
            self.option['opt_%s' % obj] = self.option_values[obj].get_value()

        self.fail = False   # Pro-Gen import proceed
