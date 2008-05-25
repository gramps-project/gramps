#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"Export Report and Tools commandline parameters to DocBook XML"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import tempfile
from cgi import escape
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from PluginUtils import Tool, PluginManager
from ReportBase import CATEGORY_BOOK, CATEGORY_WEB
from ReportBase._CommandLineReport import CommandLineReport

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_tags = [
    'article',
    'sect1',
    'sect2',
    'sect3'
    ]

#-------------------------------------------------------------------------
#
# CmdRef
#
#-------------------------------------------------------------------------
class CmdRef(Tool.Tool):
    def __init__(self,dbstate, uistate, options_class, name, callback=None):
        Tool.Tool.__init__(self,dbstate, options_class, name)
        self.__db = dbstate.db

        # retrieve options
        include = self.options.handler.options_dict['include']
        target  = self.options.handler.options_dict['target']

        if include:
            level = 1
        else:
            level = 0

        f = tempfile.NamedTemporaryFile()
        fname = f.name
        id_counter = 0

        if not include:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<?yelp:chunk-depth 2?>\n')
            f.write('<!DOCTYPE book PUBLIC ')
            f.write('"-//OASIS//DTD DocBook XML V4.1.2//EN" ')
            f.write('   "http://www.oasis-open.org/docbook/'
                    'xml/4.1.2/docbookx.dtd">\n')
            
        # Top section and title
        f.write('<%s id="cmdplug-id%d">\n' % (_tags[level],id_counter) )
        id_counter = id_counter + 1
        f.write('  <title>Detailed plugin option reference</title>\n')

        # Reports
        f.write('  <%s id="cmdplug-reps">\n' % _tags[level+1])
        f.write('    <title>Reports</title>\n')

        # Common report options
        pmgr = PluginManager.get_instance()
        _cl_list = pmgr.get_cl_list()
        item = _cl_list[0]
        clr = CommandLineReport(self.__db, item[0], item[1], item[3], {}, True)
        self.write_ref(f,clr,level+2,id_counter,True)
        id_counter = id_counter + 1

        for item in _cl_list:
            unsupported = item[5]
            if unsupported is True:
                continue
            category = item[1]
            if category in [CATEGORY_BOOK]:
                self.write_ref(f,item,level+2,id_counter,category)
            else:
                self.write_ref(f,item,level+2,id_counter,None)
            id_counter = id_counter + 1
        f.write('  </%s>\n' % _tags[level+1] )

        # Tools
        f.write('  <%s id="cmdplug-tools">\n ' % _tags[level+1] )
        f.write('    <title>Tools</title>\n')

        # Common tool options
        _cl_tool_list = pmgr.get_cl_tool_list()
        item = _cl_tool_list[0]
        clr = Tool.CommandLineTool(self.__db, item[0], 
                                   item[1], item[3], {}, True)
        self.write_ref(f,clr,level+2,id_counter,True)
        id_counter = id_counter + 1

        for item in _cl_tool_list:
            self.write_ref(f,item,level+2,id_counter)
            id_counter = id_counter + 1
        f.write('  </%s>\n' % _tags[level+1] )
        f.write('  \n')
        f.write('</%s>\n' %_tags[level])
        f.flush()
        if include:
            os.spawnlp( os.P_WAIT, "cp", "cp", fname, target)
        else:
            os.spawnlp( os.P_WAIT, "yelp", "yelp", fname)
        f.close()

    def write_ref(self,f,item,level,id_counter,category=None):
        # Section and title
        f.write('<%s id="cmdplug-id%d">\n' % (_tags[level],id_counter) )
        if category:
            title = 'Common Options'
        else:
            title = item[4]
        f.write('  <title>%s</title>\n' % title)
        
        # Show command-line name
        f.write('    <variablelist>\n')

        if not category:
            f.write('        <varlistentry>\n')
            f.write('          <term><command>name</command>:</term>\n')
            f.write('          <listitem>\n')
            f.write('            <para>%s</para>\n' % item[0])
            f.write('          </listitem>\n')
            f.write('        </varlistentry>\n')

        # Instantiate options class
        if category is None:
            oclass = item[3](item[0], self.__db)
        elif category == CATEGORY_BOOK:
            import BookReport
            oclass = BookReport.BookOptions(item[0], self.__db)
        elif category:
            # This is the common options case
            # so class is already instantiated
            oclass = item
                
        # Spit out all options
        for arg in oclass.options_help.keys():
            f.write('        <varlistentry>\n')
            f.write('          <term><command>%s</command>: %s</term>\n'
                    % (escape(arg), escape(oclass.options_help[arg][0])))
            f.write('          <listitem>\n')
            f.write('            <para>%s</para>\n'
                    % escape(oclass.options_help[arg][1]))

            if len(oclass.options_help[arg])>2:
                if isinstance(oclass.options_help[arg][2], (list, tuple)):
                    if oclass.options_help[arg][3]:
                        f.write('          <orderedlist>\n')
                        for val in oclass.options_help[arg][2]:
                            f.write( "      <listitem><para>%s</para></listitem>\n"
                                     % escape(val))
                        f.write('          </orderedlist>\n')
                    else:
                        if oclass.options_help[arg][2]:
                            f.write('          <itemizedlist>\n')
                            for val in oclass.options_help[arg][2]:
                                f.write( "      <listitem><para>%s</para>"
                                         "</listitem>\n" % escape(val))
                            f.write('          </itemizedlist>\n')
                else:
                    f.write('            '
                            '<para>Value: <userinput>%s</userinput></para>\n'
                            % escape(oclass.options_help[arg][2]))
            f.write('          </listitem>\n')
            f.write('        </varlistentry>\n')

        f.write('    </variablelist>\n')
        f.write('</%s>\n' % _tags[level])
    
#------------------------------------------------------------------------
#
# CmdRefOptions
#
#------------------------------------------------------------------------
class CmdRefOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        Tool.ToolOptions.__init__(self, name,person_id)

        # Options specific for this report
        self.options_dict = {
            'include' : 0,
            'target'  : '../doc/gramps-manual/C/cmdplug.xml',
        }
        self.options_help = {
            'include' : ("=0/1","Whether to include into the manual",
                         ["Do not include","Include"],
                         True),
            'target'  : ("=str","Pathname to the target file",
                         "Any valid pathname")
            }

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
if __debug__:

    pmgr = PluginManager.get_instance()
    pmgr.register_tool(
        name = 'cmdref',
        category = Tool.TOOL_DEBUG,
        tool_class = CmdRef,
        options_class = CmdRefOptions,
        modes = Tool.MODE_GUI | Tool.MODE_CLI,
        translated_name = _("Generate Commandline Plugin Reference"),
        status = _("Stable"),
        author_name = "Martin Hawlisch",
        author_email = "martin@hawlisch.de",
        description= _("Produces a DocBook XML file that contains "
                       "a parameter reference of Reports and Tools.")
        )
