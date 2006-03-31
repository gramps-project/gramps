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

"Database Processing/Extract information from names"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import popen2
import locale
import time
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from QuestionDialog import OkDialog, ErrorDialog
import GrampsDb
from PluginUtils import Tool, register_tool
import Utils
import GrampsDisplay

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

# Some message strings
rcs_setup_failure_msg = [
    _("Checkpoint Archive Creation Failed"),
    _("No checkpointing archive was found. "
      "An attempt to create it has failed with the "
      "following message:\n\n%s")
    ]

rcs_setup_success_msg = [
    _("Checkpoint Archive Created"),
    _("No checkpointing archive was found, "
      "so it was created to enable archiving.\n\n"
      "The archive file name is %s\n"
      "Deleting this file will lose the archive "
      "and make impossible to extract archived data "
      "from it.")
    ]

archive_failure_msg = [
    _("Checkpoint Failed"),
    _("An attempt to archive the data failed "
      "with the following message:\n\n%s")
    ]

archive_success_msg = [
    _("Checkpoint Succeeded "),
    _("The data was successfully archived.")
    ]

retrieve_failure_msg = [
    _("Checkpoint Failed"),
    _("An attempt to retrieve the data failed "
      "with the following message:\n\n%s")
    ]

retrieve_success_msg = [
    _("Checkpoint Succeeded "),
    _("The data was successfully retrieved.")
    ]

#-------------------------------------------------------------------------
#
# Checkpoint class
#
#-------------------------------------------------------------------------
class Checkpoint(Tool.Tool):

    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        if parent:
            self.callback = self.callback_real
            self.init_gui(parent)
        else:
            self.callback = lambda a: None
            self.run_tool(cli=True)

    def init_gui(self,parent):
        # Draw dialog and make it handle everything
        self.parent = parent
        if self.parent.child_windows.has_key(self.__class__):
            self.parent.child_windows[self.__class__].present(None)
            return
        self.win_key = self.__class__

        base = os.path.dirname(__file__)
        glade_file = "%s/%s" % (base,"checkpoint.glade")
        self.glade = gtk.glade.XML(glade_file,"top","gramps")

        self.cust_arch_cb = self.glade.get_widget("cust_arch")
        self.cust_ret_cb = self.glade.get_widget("cust_ret")
        self.rcs_rb = self.glade.get_widget("rcs")
        self.cust_rb = self.glade.get_widget("custom")
        
        # Fill in the stored values
        self.cust_arch_cb.set_text(
            self.options.handler.options_dict['cacmd'])
        self.cust_ret_cb.set_text(
            self.options.handler.options_dict['crcmd'])

        # Display controls according to the state
        if self.options.handler.options_dict['rcs']:
            self.rcs_rb.set_active(1)
        else:
            self.cust_rb.set_active(1)
        self.cust_arch_cb.set_sensitive(self.cust_rb.get_active())
        self.cust_ret_cb.set_sensitive(self.cust_rb.get_active())

        self.rcs_rb.connect('toggled',self.rcs_toggled)

        self.title = _("Checkpoint Data")
        self.window = self.glade.get_widget('top')
        self.window.set_icon(self.parent.topWindow.get_icon())
        Utils.set_titles(self.window,
                         self.glade.get_widget('title'),
                         self.title)

        self.glade.signal_autoconnect({
            "on_close_clicked" : self.close,
            "on_delete_event"  : self.on_delete_event,
            "on_arch_clicked"  : self.on_archive_clicked,
            "on_ret_clicked"   : self.on_retrieve_clicked,
            "on_help_clicked"  : self.on_help_clicked,
            })

        self.add_itself_to_menu()
        self.window.show()

    def rcs_toggled(self,obj):
        self.cust_arch_cb.set_sensitive(not obj.get_active())
        self.cust_ret_cb.set_sensitive(not obj.get_active())

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('index')

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(self.title)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_archive_clicked(self,obj):
        self.options.handler.options_dict['cacmd'] = unicode(
            self.cust_arch_cb.get_text())
        self.options.handler.options_dict['rcs']  = int(
            self.rcs_rb.get_active())
        
        self.run_tool(archive=True,cli=False)
        # Save options
        self.options.handler.save_options()

    def on_retrieve_clicked(self,obj):
        self.options.handler.options_dict['crcmd'] = unicode(
            self.cust_ret_cb.get_text())
        self.options.handler.options_dict['rcs']  = int(
            self.rcs_rb.get_active())
        
        self.run_tool(archive=False,cli=False)
        # Save options
        self.options.handler.save_options()

    def run_tool(self,archive=True,cli=False):
        """
        RCS will be a builtin command, since we can handle all
        configuration on our own. This isn't true for most versioning
        systems, which usually require external setup, and external
        communication.
        """
        if not cli:
            self.parent.status_text(_("Checkpointing database..."))

        if self.options.handler.options_dict['rcs']:
            self.rcs(archive,cli)
        elif archive:
            self.custom(self.options.handler.options_dict['cacmd'],True,cli)
        else:
            self.custom(self.options.handler.options_dict['crcmd'],False,cli)
        
        if not cli:
            self.parent.progress.set_fraction(0)
            self.parent.modify_statusbar()

    def timestamp(self):
        return unicode(time.strftime('%x %X',time.localtime(time.time())))

    def custom(self,cmd,checkin,cli):
        """
        Passed the generated XML file to the specified command.
        """
        proc = popen2.Popen3(cmd, True)
        if checkin:
            xmlwrite = GrampsDb.XmlWriter(self.db,self.callback,False,False)
            xmlwrite.write_handle(proc.tochild)
        else:
            pass
        proc.tochild.close()
        status = proc.wait()
        message = "\n".join(proc.childerr.readlines())
        del proc
        
        if checkin:
            if status:
                msg1 = archive_failure_msg[0]
                msg2 = archive_failure_msg[1] % message
                dialog = ErrorDialog
            else:
                msg1 = archive_success_msg[0]
                msg2 = archive_success_msg[1]
                dialog = OkDialog
        else:
            if status:
                msg1 = retrieve_failure_msg[0]
                msg2 = retrieve_failure_msg[1] % message
                dialog = ErrorDialog
            else:
                msg1 = retrieve_success_msg[0]
                msg2 = retrieve_success_msg[1]
                dialog = OkDialog

        if cli:
            print msg1
            print msg2
        else:
            dialog(msg1,msg2)

    def rcs(self,checkin,cli):
        """
        Check the generated XML file into RCS. Initialize the RCS file if
        it does not already exist.
        """
        (archive_base,ext) = os.path.splitext(self.db.get_save_path())

        comment = self.timestamp()

        archive = archive_base + ",v"

        # If the archive file does not exist, we either set it up
        # or die trying
        if not os.path.exists(archive):
            proc = popen2.Popen3(
                'rcs -i -U -q -t-"GRAMPS database" %s' % archive,
                True)
            proc.tochild.close()
            status = proc.wait()
            message = "\n".join(proc.childerr.readlines())
            del proc

            if status:
                msg1 = rcs_setup_failure_msg[0]
                msg2 = rcs_setup_failure_msg[1] % message
                dialog = ErrorDialog
            else:
                msg1 = rcs_setup_success_msg[0]
                msg2 = rcs_setup_success_msg[1] % archive
                dialog = OkDialog
                           
            if cli:
                print msg1
                print msg2
            else:
                dialog(msg1,msg2)

            if status:
                return

        if checkin:
            # At this point, we have an existing archive file
            xmlwrite = WriteXML.XmlWriter(self.db,self.callback,False,False)
            xmlwrite.write(archive_base)

            proc = popen2.Popen3("ci %s" % archive_base,True)
            proc.tochild.write(comment)
            proc.tochild.close()
            status = proc.wait()
            message = "\n".join(proc.childerr.readlines())
            del proc

            if status:
                msg1 = archive_failure_msg[0]
                msg2 = archive_failure_msg[1] % message
                dialog = ErrorDialog
            else:
                msg1 = archive_success_msg[0]
                msg2 = archive_success_msg[1]
                dialog = OkDialog
                           
            if cli:
                print msg1
                print msg2
            else:
                dialog(msg1,msg2)
        else:
            proc = popen2.Popen3("co -p %s > %s.gramps"
                                 % (archive_base,archive_base),
                                 True)
            proc.tochild.close()
            status = proc.wait()
            message = "\n".join(proc.childerr.readlines())
            del proc
            if status:
                msg1 = retrieve_failure_msg[0]
                msg2 = retrieve_failure_msg[1] % message
                dialog = ErrorDialog
            else:
                msg1 = retrieve_success_msg[0]
                msg2 = retrieve_success_msg[1]
                dialog = OkDialog
                           
            if cli:
                print msg1
                print msg2
            else:
                dialog(msg1,msg2)

    def callback_real(self,value):
        """
        Call back function for the WriteXML function that updates the
        status progress bar.
        """
        self.parent.progress.set_fraction(value)
        while(gtk.events_pending()):
            gtk.main_iteration()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class CheckpointOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'rcs'     : 1,
            'archive' : 1,
            'cacmd'   : '',
            'crcmd'   : '',
        }
        self.options_help = {
            'rcs'     : ("=0/1",
                         "Whether to use RCS (ignores custom commands).",
                         ["Do not use RCS","Use RCS"],
                         True),
            'archive' : ("=0/1",
                         "Whether to archive or retrieve.",
                         ["Retrieve","Archive"],
                         True),
            'cacmd'   : ("=str","Custom command line for archiving",
                         "Custom command string"),
            'crcmd'   : ("=str","Custom command line for retrieval",
                         "Custom command string"),
        }

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_tool(
    name = 'chkpoint',
    category = Tool.TOOL_REVCTL,
    tool_class = Checkpoint,
    options_class = CheckpointOptions,
    modes = Tool.MODE_GUI | Tool.MODE_CLI,
    translated_name = _("Checkpoint the database"),
    status = _("Stable"),
    author_name = "Alex Roitman",
    author_email = "shura@gramps-project.org",
    description = _("Store a snapshot of the current database into "
                    "a revision control system")
    )
