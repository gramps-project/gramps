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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys
import html
import logging
_LOG = logging.getLogger(".dialog")

#-------------------------------------------------------------------------
#
# GNOME/GTK+ modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.const import ICON, URL_BUGHOME
from gramps.gen.config import config
from gramps.gen.constfunc import is_quartz
from .glade import Glade
from .display import display_url

try:
    ICON = GdkPixbuf.Pixbuf.new_from_file(ICON)
except:
    ICON = None

class SaveDialog:
    def __init__(self, msg1, msg2, task1, task2, parent=None):
        self.xml = Glade(toplevel='savedialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % msg1)

        self.dontask = self.xml.get_object('dontask')
        self.task1 = task1
        self.task2 = task2

        label1 = self.xml.get_object('sd_label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)

        label2 = self.xml.get_object('sd_label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)
        if parent:
            self.top.set_transient_for(parent)
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.top.show()
        response = self.top.run()
        if response == Gtk.ResponseType.NO:
            self.task1()
        elif response == Gtk.ResponseType.YES:
            self.task2()

        config.set('interface.dont-ask', self.dontask.get_active())
        self.top.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

class QuestionDialog:
    def __init__(self, msg1, msg2, label, task, parent=None):
        self.xml = Glade(toplevel='questiondialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % msg1)

        label1 = self.xml.get_object('qd_label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' %
                         html.escape(msg1))
        label1.set_use_markup(True)

        label2 = self.xml.get_object('qd_label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_object('okbutton').set_label(label)

        if parent:
            self.top.set_transient_for(parent)
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.top.show()
        response = self.top.run()
        self.top.destroy()
        if parent and parent_modal:
            parent.set_modal(True)
        if response == Gtk.ResponseType.ACCEPT:
            task()

def on_activate_link(label, uri):
    # see aboutdialog.py _show_url()
    display_url(uri)
    return True

class QuestionDialog2:
    def __init__(self, msg1, msg2, label_msg1, label_msg2, parent=None):
        self.xml = Glade(toplevel='questiondialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % msg1)

        label1 = self.xml.get_object('qd_label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' %
                        html.escape(msg1))
        label1.set_use_markup(True)

        label2 = self.xml.get_object('qd_label2')
        # see https://github.com/emesene/emesene/issues/723
        label2.connect('activate-link', on_activate_link)
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_object('okbutton').set_label(label_msg1)
        self.xml.get_object('okbutton').set_use_underline(True)
        self.xml.get_object('no').set_label(label_msg2)
        self.xml.get_object('no').set_use_underline(True)

        self.parent = parent
        if parent:
            self.top.set_transient_for(parent)
            self.parent_modal = parent.get_modal()
            if self.parent_modal:
                parent.set_modal(False)
        self.top.show()

    def run(self):
        response = self.top.run()
        self.top.destroy()
        if self.parent and self.parent_modal:
            self.parent.set_modal(True)
        return (response == Gtk.ResponseType.ACCEPT)

class QuestionDialog3:
    """ Like QuestionDialog2, but includes cancel button,
    returns: 1  (okbutton, label_msg1)
             0  (no button label_msg2)
             -1 (cancel button)
    """
    def __init__(self, msg1, msg2, label_msg1, label_msg2, parent=None):
        self.xml = Glade(toplevel='questiondialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % msg1)

        label1 = self.xml.get_object('qd_label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' %
                        html.escape(msg1))
        label1.set_use_markup(True)

        label2 = self.xml.get_object('qd_label2')
        # see https://github.com/emesene/emesene/issues/723
        label2.connect('activate-link', on_activate_link)
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_object('okbutton').set_label(label_msg1)
        self.xml.get_object('okbutton').set_use_underline(True)
        self.xml.get_object('no').set_label(label_msg2)
        self.xml.get_object('no').set_use_underline(True)
        self.xml.get_object('cancelbutton').show()

        self.parent = parent
        if parent:
            self.top.set_transient_for(parent)
            self.parent_modal = parent.get_modal()
            if self.parent_modal:
                parent.set_modal(False)
        self.top.show()

    def run(self):
        response = self.top.run()
        self.top.destroy()
        if self.parent and self.parent_modal:
            self.parent.set_modal(True)
        return (-1 if response == Gtk.ResponseType.DELETE_EVENT
                else response == Gtk.ResponseType.ACCEPT)

class OptionDialog:
    def __init__(self, msg1, msg2, btnmsg1, task1, btnmsg2, task2, parent=None):
        self.xml = Glade(toplevel='optiondialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % msg1)

        label1 = self.xml.get_object('od_label1')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)

        label2 = self.xml.get_object('od_label2')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        self.xml.get_object('option1').set_label(btnmsg1)
        self.xml.get_object('option2').set_label(btnmsg2)
        if parent:
            self.top.set_transient_for(parent)
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.top.show()
        self.response = self.top.run()
        if self.response == Gtk.ResponseType.NO:
            if task1:
                task1()
        else:
            if task2:
                task2()
        self.top.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

    def get_response(self):
        return self.response

class ErrorDialog(Gtk.MessageDialog):
    def __init__(self, msg1, msg2="", parent=None):

        Gtk.MessageDialog.__init__(self, transient_for=parent,
                                   modal=True,
                                   message_type=Gtk.MessageType.ERROR)
        self.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        self.set_markup('<span weight="bold" size="larger">%s</span>' % str(msg1))
        self.format_secondary_text(msg2)
        self.set_icon(ICON)
        self.set_title("%s - Gramps" % str(msg1))
        if parent:
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.show()
        self.run()
        self.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

class RunDatabaseRepair(ErrorDialog):
    def __init__(self, msg, parent=None):
        ErrorDialog.__init__(
            # These exact strings are also in cli/user.py -- keep them in sync
            self,
            _('Error detected in database'),
            _('Gramps has detected an error in the database. This can '
              'usually be resolved by running the "Check and Repair Database" '
              'tool.\n\nIf this problem continues to exist after running this '
              'tool, please file a bug report at '
              '%(gramps_bugtracker_url)s\n\n'
             ) % {'gramps_bugtracker_url' : URL_BUGHOME}
            + msg, parent)

class DBErrorDialog(ErrorDialog):
    def __init__(self, msg, parent=None):
        ErrorDialog.__init__(
            # These exact strings are also in cli/user.py -- keep them in sync
            self,
            _("Low level database corruption detected"),
            _("Gramps has detected a problem in the underlying "
              "Berkeley database. This can be repaired from "
              "the Family Tree Manager. Select the database and "
              'click on the Repair button') + '\n\n' + msg, parent)

class WarningDialog(Gtk.MessageDialog):
    def __init__(self, msg1, msg2="", parent=None):

        Gtk.MessageDialog.__init__(self, transient_for=parent,
                                   modal=True,
                                   message_type=Gtk.MessageType.WARNING)
        self.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        self.set_markup('<span weight="bold" size="larger">%s</span>' % msg1)
        self.format_secondary_markup(msg2)
        # FIXME: Hyper-links in the secondary text display as underlined text,
        # but clicking on the link fails with
        # GtkWarning: Unable to show 'http://www.gramps-project.org/wiki/index.php?title=How_to_make_a_backup': Operation not supported
        # self.connect('activate-link'... fails with
        # <WarningDialog object at 0x4880300 (GtkMessageDialog at 0x5686010)>: unknown signal name: activate-link
        self.set_icon(ICON)
        self.set_title("%s - Gramps" % msg1)
        if parent:
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.show()
        self.run()
        self.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

class OkDialog(Gtk.MessageDialog):
    def __init__(self, msg1, msg2="", parent=None):

        Gtk.MessageDialog.__init__(self, transient_for=parent,
                                   modal=True,
                                   message_type=Gtk.MessageType.INFO)
        self.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        self.set_markup('<span weight="bold" size="larger">%s</span>' % msg1)
        self.format_secondary_text(msg2)
        self.set_icon(ICON)
        self.set_title("%s - Gramps" % msg1)
        if parent:
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.show()
        self.run()
        self.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

class InfoDialog:
    """
    Non modal dialog to show selectable info in a scrolled window
    """
    def __init__(self, msg1, infotext, parent=None, monospaced=False):
        self.xml = Glade(toplevel='infodialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % msg1)

        label = self.xml.get_object('toplabel')
        label.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label.set_use_markup(True)

        infoview = self.xml.get_object('infoview')
        infobuffer = Gtk.TextBuffer()
        infobuffer.set_text(infotext)
        if monospaced:
            startiter, enditer = infobuffer.get_bounds()
            tag = infobuffer.create_tag(family="Monospace")
            infobuffer.apply_tag(tag, startiter, enditer)
        infoview.set_buffer(infobuffer)

        if parent:
            self.top.set_transient_for(parent)
        self.top.connect('response', self.destroy)
        self.top.show()

    def destroy(self, dialog, response_id):
        #no matter how it finishes, destroy dialog
        dialog.destroy()

class MissingMediaDialog:
    def __init__(self, msg1, msg2, task1, task2, task3, parent=None):
        self.xml = Glade(toplevel='missmediadialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % msg1)

        self.task1 = task1
        self.task2 = task2
        self.task3 = task3

        label1 = self.xml.get_object('label4')
        label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
        label1.set_use_markup(True)

        label2 = self.xml.get_object('label3')
        label2.set_text(msg2)
        label2.set_use_markup(True)

        check_button = self.xml.get_object('use_always')

        if parent:
            self.top.set_transient_for(parent)
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.top.show()
        self.top.connect('delete_event', self.warn)
        response = Gtk.ResponseType.DELETE_EVENT

        # Need some magic here, because an attempt to close the dialog
        # with the X button not only emits the 'delete_event' signal
        # but also exits with the RESPONSE_DELETE_EVENT
        while response == Gtk.ResponseType.DELETE_EVENT:
            response = self.top.run()

        if response == 1:
            self.task1()
        elif response == 2:
            self.task2()
        elif response == 3:
            self.task3()
        if check_button.get_active():
            self.default_action = response
        else:
            self.default_action = 0
        self.top.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

    def warn(self, obj, obj2):
        WarningDialog(
            _("Attempt to force closing the dialog"),
            _("Please do not force closing this important dialog.\n"
              "Instead select one of the available options"),
            parent=self.top)
        return True

class MultiSelectDialog:
    def __init__(self, msg1_func, msg2_func, items, lookup,
                 cancel_func=None, no_func=None, yes_func=None,
                 multi_yes_func=None, parent=None):
        """
        """
        self.xml = Glade(toplevel='multiselectdialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)

        self.msg1_func = msg1_func
        self.msg2_func = msg2_func
        self.items = items
        self.lookup = lookup
        self.cancel_func = cancel_func
        self.no_func = no_func
        self.yes_func = yes_func

        label1 = self.xml.get_object('label6')
        label2 = self.xml.get_object('label5')
        check_button = self.xml.get_object('apply_to_rest')

        if parent:
            self.top.set_transient_for(parent)
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.top.connect('delete_event', self.warn)

        default_action = 0
        for selected in items:
            item = self.lookup(selected)
            if default_action == 0:
                msg1 = self.msg1_func(item)
                msg2 = self.msg2_func(item)

                self.top.set_title("%s - Gramps" % msg1)
                label1.set_text('<span weight="bold" size="larger">%s</span>' % msg1)
                label1.set_use_markup(True)
                label2.set_text(msg2)
                label2.set_use_markup(True)
                self.top.show()

                # Need some magic here, because an attempt to close the dialog
                # with the X button not only emits the 'delete_event' signal
                # but also exits with the RESPONSE_DELETE_EVENT
                response = Gtk.ResponseType.DELETE_EVENT
                while response == Gtk.ResponseType.DELETE_EVENT:
                    response = self.top.run()

                if check_button.get_active():
                    # run the multiple yes if 'do remainder' is checked
                    if multi_yes_func and response == 3:
                        multi_yes_func(items)
                        break
                    default_action = response
            else:
                response = default_action
            ### Now do it
            if response == 1: # Cancel
                if self.cancel_func:
                    self.cancel_func(item)
                break
            elif response == 2: # No
                if self.no_func:
                    self.no_func(item)
            elif response == 3: # Yes
                if self.yes_func:
                    self.yes_func(item)
        self.top.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

    def warn(self, obj, obj2):
        WarningDialog(
            _("Attempt to force closing the dialog"),
            _("Please do not force closing this important dialog.\n"
              "Instead select one of the available options"),
            parent=self.top)
        return True

class MessageHideDialog:

    def __init__(self, title, message, key, parent=None):
        self.xml = Glade(toplevel='hidedialog')

        self.top = self.xml.toplevel
        self.top.set_icon(ICON)
        self.top.set_title("%s - Gramps" % title)

        dont_show = self.xml.get_object('dont_show')
        dont_show.set_active(config.get(key))
        title_label = self.xml.get_object('title')
        title_label.set_text(
            '<span size="larger" weight="bold">%s</span>' % title)
        title_label.set_use_markup(True)

        self.xml.get_object('message').set_text(message)

        dont_show.connect('toggled', self.update_checkbox, key)
        if parent:
            self.top.set_transient_for(parent)
            parent_modal = parent.get_modal()
            if parent_modal:
                parent.set_modal(False)
        self.top.run()
        self.top.destroy()
        if parent and parent_modal:
            parent.set_modal(True)

    def update_checkbox(self, obj, constant):
        config.set(constant, obj.get_active())
        config.save()

## Testing function of some of these dialogs
def main(args):

    win = Gtk.Window()
    win.set_title('Dialog test window')
    win.set_position(Gtk.WindowPosition.CENTER)
    #Set the mnemonic modifier on Macs to alt-ctrl so that it
    #doesn't interfere with the extended keyboard, see
    #https://gramps-project.org/bugs/view.php?id=6943
    if is_quartz():
        win.set_mnemonic_modifier(
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK)
    def cb(window, event):
        Gtk.main_quit()
    win.connect('delete-event', cb)


    def test_info(obj):
        InfoDialog('The title',
                   'This is a lot of info\n to show to all!',
                   parent=win)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    win.add(vbox)

    btn1 = Gtk.Button('Info dialog')
    btn1.connect('clicked', test_info)
    vbox.pack_start(btn1, True, True, 0)

    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    import sys
    # fall back to root logger for testing
    _LOG = logging
    sys.exit(main(sys.argv))
