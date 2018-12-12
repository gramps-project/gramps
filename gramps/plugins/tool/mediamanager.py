#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       B. Malengier
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012       Nick Hall
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

# Written by Alex Roitman

"""Tools/Utilities/Media Manager"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GdkPixbuf

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import URL_MANUAL_PAGE, ICON, SPLASH
from gramps.gui.display import display_help
from gramps.gen.lib import Media
from gramps.gen.db import DbTxn
from gramps.gen.updatecallback import UpdateCallback
from gramps.gui.plug import tool
from gramps.gen.utils.file import media_path_full, relative_path, media_path
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.mime import get_type, is_image_type
from gramps.gui.managedwindow import ManagedWindow

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Media_Manager')

#-------------------------------------------------------------------------
#
# This is an Assistant implementation to guide the user
#
#-------------------------------------------------------------------------
class MediaMan(ManagedWindow, tool.Tool):

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate

        tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.callback = uistate.pulse_progressbar

        self.batch_ops = []
        self.build_batch_ops()

        self.assistant = Gtk.Assistant()
        self.set_window(self.assistant, None, _('Media Manager'))
        self.setup_configs('interface.mediaman', 780, 600)

        help_btn = Gtk.Button.new_with_label(_('Help'))
        help_btn.connect('clicked', self.on_help_clicked)
        self.assistant.add_action_widget(help_btn)

        self.assistant.connect('close', self.do_close)
        self.assistant.connect('cancel', self.do_close)
        self.assistant.connect('apply', self.run)
        self.assistant.connect('prepare', self.prepare)

        intro = IntroductionPage()
        self.add_page(intro, Gtk.AssistantPageType.INTRO, _('Introduction'))
        self.selection = SelectionPage(self.batch_ops)
        self.add_page(self.selection, Gtk.AssistantPageType.CONTENT,
                      _('Selection'))
        self.settings = SettingsPage(self.batch_ops, self.assistant)
        self.add_page(self.settings, Gtk.AssistantPageType.CONTENT)
        self.confirmation = ConfirmationPage(self.batch_ops)
        self.add_page(self.confirmation, Gtk.AssistantPageType.CONFIRM,
                      _('Final confirmation'))
        self.conclusion = ConclusionPage(self.assistant)
        self.add_page(self.conclusion, Gtk.AssistantPageType.SUMMARY)

        self.show()
        self.assistant.set_forward_page_func(self.forward_page, None)

    def build_menu_names(self, obj):
        """Override :class:`.ManagedWindow` method."""
        return (_('Media Manager'), None)

    def do_close(self, assistant):
        """
        Close the assistant.
        """
        position = self.window.get_position() # crock
        self.assistant.hide()
        self.window.move(position[0], position[1])
        self.close()

    def forward_page(self, page, data):
        """
        Specify the next page to be displayed.
        """
        if page == 1: # selection page
            index = self.selection.get_index()
            if self.settings.prepare(index):
                return page + 1
            else:
                return page + 2
        else:
            return page + 1

    def prepare(self, assistant, page):
        """
        Run page preparation code.
        """
        if self.assistant.get_current_page() == 3:
            index = self.selection.get_index()
            self.confirmation.prepare(index)
        self.assistant.set_page_complete(page, True)

    def add_page(self, page, page_type, title=''):
        """
        Add a page to the assistant.
        """
        page.show_all()
        self.assistant.append_page(page)
        self.assistant.set_page_title(page, title)
        self.assistant.set_page_type(page, page_type)

    def on_help_clicked(self, obj):
        """
        Display the relevant portion of Gramps manual.
        """
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def build_batch_ops(self):
        """
        Define the batch operations available.
        """
        batches_to_use = [
            PathChange,
            Convert2Abs,
            Convert2Rel,
            ImagesNotIncluded,
            ]

        for batch_class in batches_to_use:
            self.batch_ops.append(batch_class(self.db, self.callback))

    def run(self, assistant):
        """
        Run selected batch op with selected settings.
        """
        index = self.selection.get_index()
        self.pre_run()
        success = self.batch_ops[index].run_tool()
        self.conclusion.set_result(success)
        self.post_run()

    def pre_run(self):
        """
        Code to run prior to the batch op.
        """
        self.uistate.set_busy_cursor(True)
        self.uistate.progress.show()

    def post_run(self):
        """
        Code to run after to the batch op.
        """
        self.uistate.set_busy_cursor(False)
        self.uistate.progress.hide()

#------------------------------------------------------------------------
#
# Assistant pages
#
#------------------------------------------------------------------------
class IntroductionPage(Gtk.Box):
    """
    A page containing introductory text.
    """
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # Using set_page_side_image causes window sizing problems, so put the
        # image in the main page instead.
        image = Gtk.Image()
        image.set_from_file(SPLASH)

        label = Gtk.Label(label=self.__get_intro_text())
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.set_max_width_chars(60)

        self.pack_start(image, False, False, 0)
        self.pack_start(label, False, False, 5)

    def __get_intro_text(self):
        """
        Return the introductory text.
        """
        return _("This tool allows batch operations on media objects "
                 "stored in Gramps. "
                 "An important distinction must be made between a Gramps "
                 "media object and its file.\n\n"
                 "The Gramps media object is a collection of data about "
                 "the media object file: its filename and/or path, its "
                 "description, its ID, notes, source references, etc. "
                 "These data "
                 "%(bold_start)sdo not include the file itself%(bold_end)s.\n\n"
                 "The files containing image, sound, video, etc, exist "
                 "separately on your hard drive. These files are "
                 "not managed by Gramps and are not included in the Gramps "
                 "database. "
                 "The Gramps database only stores the path and file names.\n\n"
                 "This tool allows you to only modify the records within "
                 "your Gramps database. If you want to move or rename "
                 "the files then you need to do it on your own, outside of "
                 "Gramps. Then you can adjust the paths using this tool so "
                 "that the media objects store the correct file locations."
                ) % { 'bold_start' : '<b>' ,
                      'bold_end'   : '</b>' }

class SelectionPage(Gtk.Box):
    """
    A page with the radio buttons for every available batch op.
    """
    def __init__(self, batch_ops):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.batch_op_buttons = []

        self.set_spacing(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)

        button = None
        for index in range(len(batch_ops)):
            title = batch_ops[index].title
            description = batch_ops[index].description

            button = Gtk.RadioButton.new_with_mnemonic_from_widget(button, title)
            button.set_tooltip_text(description)
            self.batch_op_buttons.append(button)
            grid.attach(button, 0, 2 * index, 2, 1)

        self.add(grid)

    def get_index(self):
        """
        Query the selection radiobuttons and return the index number
        of the selected batch op.
        """
        for index in range(len(self.batch_op_buttons)):
            button = self.batch_op_buttons[index]
            if button.get_active():
                return index

        return 0

class SettingsPage(Gtk.Box):
    """
    An extra page with the settings specific for the chosen batch-op.
    """
    def __init__(self, batch_ops, assistant):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.assistant = assistant
        self.batch_ops = batch_ops

    def prepare(self, index):
        """
        Build the settings for the batch op.
        """
        config = self.batch_ops[index].build_config()
        if config:
            title, contents = config
            self.assistant.set_page_title(self, title)
            list(map(self.remove, self.get_children()))
            self.pack_start(contents, True, True, 0)
            self.show_all()
            return True
        else:
            self.assistant.set_page_title(self, '')
            return False

class ConfirmationPage(Gtk.Box):
    """
    A page to display the summary of the proposed action, as well as the
    list of affected paths.
    """
    def __init__(self, batch_ops):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.batch_ops = batch_ops

        self.set_spacing(12)
        self.set_border_width(12)

        self.confirm = Gtk.Label()
        self.confirm.set_halign(Gtk.Align.START)
        self.confirm.set_line_wrap(True)
        self.confirm.set_use_markup(True)
        self.pack_start(self.confirm, False, True, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        tree = Gtk.TreeView()
        self.path_model = Gtk.ListStore(GObject.TYPE_STRING)
        tree.set_model(self.path_model)
        tree_view_column = Gtk.TreeViewColumn(_('Affected path'),
                                              Gtk.CellRendererText(), text=0)
        tree_view_column.set_sort_column_id(0)
        tree.append_column(tree_view_column)
        scrolled_window.add(tree)
        self.pack_start(scrolled_window, True, True, 0)

        label3 = Gtk.Label(label=_('Press Apply to proceed, Cancel to abort, '
                                   'or Back to revisit your options.'))
        self.pack_start(label3, False, True, 0)

    def prepare(self, index):
        """
        Display a list of changes to be made.
        """
        confirm_text = self.batch_ops[index].build_confirm_text()
        path_list = self.batch_ops[index].build_path_list()

        self.confirm.set_text(confirm_text)

        self.path_model.clear()
        for path in path_list:
            self.path_model.append(row=[path])

class ConclusionPage(Gtk.Box):
    """
    A page to display the summary of the proposed action, as well as the
    list of affected paths.
    """
    def __init__(self, assistant):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.assistant = assistant

        image = Gtk.Image()
        image.set_from_file(SPLASH)

        self.label = Gtk.Label()
        self.label.set_line_wrap(True)

        self.pack_start(image, False, False, 0)
        self.pack_start(self.label, False, False, 5)

    def set_result(self, success):
        if success:
            conclusion_title =  _('Operation successfully finished')
            conclusion_text = _(
                'The operation you requested has finished successfully. '
                'You may press Close now to continue.')
        else:
            conclusion_title =  _('Operation failed')
            conclusion_text = _(
                'There was an error while performing the requested '
                'operation. You may try starting the tool again.')
        self.label.set_text(conclusion_text)
        self.assistant.set_page_title(self, conclusion_title)

#------------------------------------------------------------------------
#
# These are the actuall sub-tools (batch-ops) for use from Assistant
#
#------------------------------------------------------------------------
class BatchOp(UpdateCallback):
    """
    Base class for the sub-tools.
    """
    title       = 'Untitled operation'
    description = 'This operation needs to be described'

    def __init__(self, db, callback):
        UpdateCallback.__init__(self, callback)
        self.db = db
        self.prepared = False

    def build_config(self):
        """
        This method should return either None (if the batch op requires
        no settings to run) or a tuple (title,box) for the settings page.
        """
        return None

    def build_confirm_text(self):
        """
        This method should return either None (if the batch op requires
        no confirmation) or a string with the confirmation text.
        """
        text = _(
            'The following action is to be performed:\n\n'
            'Operation:\t%s') % self.title.replace('_','')
        return text

    def build_path_list(self):
        """
        This method returns a list of the path names that would be
        affected by the batch op. Typically it would rely on prepare()
        to do the actual job, but it does not have to be that way.
        """
        self.prepare()
        return self.path_list

    def run_tool(self):
        """
        This method runs the batch op, taking care of database signals
        and transactions before and after the running.
        Should not be overridden without good reasons.
        """
        self.db.disable_signals()
        with DbTxn(self.title, self.db, batch=True) as self.trans:
            success = self._run()
        self.db.enable_signals()
        self.db.request_rebuild()
        return success

    def _run(self):
        """
        This method is the beef of the tool.
        Needs to be overridden in the subclass.
        """
        print("This method needs to be written.")
        print("Running BatchOp tool... done.")
        return True

    def prepare(self):
        """
        This method should prepare the tool for the actual run.
        Typically this involves going over media objects and
        selecting the ones that will be affected by the batch op.

        This method should set self.prepared to True, to indicate
        that it has already ran.
        """
        self.handle_list = []
        self.path_list = []
        self._prepare()
        self.prepared = True

    def _prepare(self):
        print("This method needs to be written.")
        print("Preparing BatchOp tool... done.")

#------------------------------------------------------------------------
# Simple op to replace substrings in the paths
#------------------------------------------------------------------------
class PathChange(BatchOp):
    title       = _('Replace _substrings in the path')
    description = _('This tool allows replacing specified substring in the '
                    'path of media objects with another substring. '
                    'This can be useful when you move your media files '
                    'from one directory to another')

    def build_config(self):
        title = _("Replace substring settings")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_spacing(12)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)

        self.from_entry = Gtk.Entry()
        self.from_entry.set_hexpand(True)
        grid.attach(self.from_entry, 1, 0, 1, 1)

        from_label = Gtk.Label(label=_('_Replace:'))
        from_label.set_halign(Gtk.Align.START)
        from_label.set_use_underline(True)
        from_label.set_mnemonic_widget(self.from_entry)
        grid.attach(from_label, 0, 0, 1, 1)

        self.to_entry = Gtk.Entry()
        self.to_entry.set_hexpand(True)
        grid.attach(self.to_entry, 1, 1, 1, 1)

        to_label = Gtk.Label(label=_('_With:'))
        to_label.set_halign(Gtk.Align.START)
        to_label.set_use_underline(True)
        to_label.set_mnemonic_widget(self.to_entry)
        grid.attach(to_label, 0, 1, 1, 1)

        box.add(grid)

        return (title, box)

    def build_confirm_text(self):
        from_text = str(self.from_entry.get_text())
        to_text = str(self.to_entry.get_text())
        text = _(
            'The following action is to be performed:\n\n'
            'Operation:\t%(title)s\n'
            'Replace:\t\t%(src_fname)s\n'
            'With:\t\t%(dest_fname)s') % {
            'title' : self.title.replace('_',''),
            'src_fname' : from_text,
            'dest_fname' : to_text }
        return text

    def _prepare(self):
        from_text = str(self.from_entry.get_text())
        self.set_total(self.db.get_number_of_media())
        with self.db.get_media_cursor() as cursor:
            for handle, data in cursor:
                obj = Media()
                obj.unserialize(data)
                if obj.get_path().find(from_text) != -1:
                    self.handle_list.append(handle)
                    self.path_list.append(obj.path)
                self.update()
        self.reset()
        self.prepared = True

    def _run(self):
        if not self.prepared:
            self.prepare()
        self.set_total(len(self.handle_list))
        from_text = str(self.from_entry.get_text())
        to_text = str(self.to_entry.get_text())
        for handle in self.handle_list:
            obj = self.db.get_media_from_handle(handle)
            new_path = obj.get_path().replace(from_text, to_text)
            obj.set_path(new_path)
            self.db.commit_media(obj, self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#An op to convert relative paths to absolute
#------------------------------------------------------------------------
class Convert2Abs(BatchOp):
    title       = _('Convert paths from relative to _absolute')
    description = _("This tool allows converting relative media paths "
                    "to the absolute ones. It does this by prepending "
                    "the base path as given in the Preferences, or if "
                    "that is not set, it prepends user's directory.")

    def _prepare(self):
        self.set_total(self.db.get_number_of_media())
        with self.db.get_media_cursor() as cursor:
            for handle, data in cursor:
                obj = Media()
                obj.unserialize(data)
                if not os.path.isabs(obj.path):
                    self.handle_list.append(handle)
                    self.path_list.append(obj.path)
                self.update()
        self.reset()

    def _run(self):
        if not self.prepared:
            self.prepare()
        self.set_total(len(self.handle_list))
        for handle in self.handle_list:
            obj = self.db.get_media_from_handle(handle)
            new_path = media_path_full(self.db, obj.path)
            obj.set_path(new_path)
            self.db.commit_media(obj, self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#An op to convert absolute paths to relative
#------------------------------------------------------------------------
class Convert2Rel(BatchOp):
    title       = _('Convert paths from absolute to r_elative')
    description = _("This tool allows converting absolute media paths "
                    "to a relative path. The relative path is relative "
                    "viz-a-viz the base path as given in the Preferences, "
                    "or if that is not set, user's directory. "
                    "A relative path allows to tie the file location to "
                    "a base path that can change to your needs.")

    def _prepare(self):
        self.set_total(self.db.get_number_of_media())
        with self.db.get_media_cursor() as cursor:
            for handle, data in cursor:
                obj = Media()
                obj.unserialize(data)
                if os.path.isabs(obj.path):
                    self.handle_list.append(handle)
                    self.path_list.append(obj.path)
                self.update()
        self.reset()

    def _run(self):
        if not self.prepared:
            self.prepare()
        self.set_total(len(self.handle_list))
        base_dir = media_path(self.db)
        for handle in self.handle_list:
            obj = self.db.get_media_from_handle(handle)
            new_path = relative_path(obj.path, base_dir)
            obj.set_path(new_path)
            self.db.commit_media(obj, self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#An op to look for images that may have been forgotten.
#------------------------------------------------------------------------
class ImagesNotIncluded(BatchOp):
    title       = _('Add images not included in database')
    description = _("Check directories for images not included in database")
    description = _("This tool adds images in directories that are "
                    "referenced by existing images in the database.")

    def _prepare(self):
        """
        Get all of the fullpaths, and the directories of media
        objects in the database.
        """
        self.dir_list = set()
        self.set_total(self.db.get_number_of_media())
        with self.db.get_media_cursor() as cursor:
            for handle, data in cursor:
                obj = Media()
                obj.unserialize(data)
                self.handle_list.append(handle)
                full_path = media_path_full(self.db, obj.path)
                self.path_list.append(full_path)
                directory, filename = os.path.split(full_path)
                if directory not in self.dir_list:
                    self.dir_list.add(directory)
                self.update()
        self.reset()

    def build_path_list(self):
        """
        This method returns a list of the path names that would be
        affected by the batch op. Typically it would rely on prepare()
        to do the actual job, but it does not have to be that way.
        """
        self.prepare()
        return self.dir_list

    def _run(self):
        """
        Go through directories that are mentioned in the database via
        media files, and include all images that are not all ready
        included.
        """
        if not self.prepared:
            self.prepare()
        self.set_total(len(self.dir_list))
        for directory in self.dir_list:
            for (dirpath, dirnames, filenames) in os.walk(directory):
                if ".git" in dirnames:
                    dirnames.remove('.git')  # don't visit .git directories
                for filename in filenames:
                    media_full_path = os.path.join(dirpath, filename)
                    if media_full_path not in self.path_list:
                        self.path_list.append(media_full_path)
                        mime_type = get_type(media_full_path)
                        if is_image_type(mime_type):
                            obj = Media()
                            obj.set_path(media_full_path)
                            obj.set_mime_type(mime_type)
                            (root, ext) = os.path.splitext(filename)
                            obj.set_description(root)
                            self.db.add_media(obj, self.trans)
            self.update()
        return True

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class MediaManOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
