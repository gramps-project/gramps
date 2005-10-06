#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

import os

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import tempfile
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Tool
import Utils
import PluginMgr

#-------------------------------------------------------------------------
#
# runTool
#
#-------------------------------------------------------------------------
class CmdRef(Tool.Tool):
    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        cli = int(parent == None)

        f = tempfile.NamedTemporaryFile()
        fname = f.name
        f.write('<?xml version="1.0" encoding="UTF-8"?>')
        f.write('<?yelp:chunk-depth 3?>')
        f.write('<!DOCTYPE book PUBLIC "-//OASIS//DTD DocBook XML V4.1.2//EN" ')
        f.write('   "http://www.oasis-open.org/docbook/xml/4.1.2/docbookx.dtd">')
        f.write('<book id="index" lang="en">')
        f.write('  <title>Reports and Tools parameter reference</title>')
        f.write('  <sect1>')
        f.write('    <title>Reports</title>')
        for item in PluginMgr.cl_list:
	    pass
            #self.write_ref( f, item)
        f.write('  </sect1>')
        f.write('  <sect1>')
        f.write('    <title>Tools</title>')
        for item in PluginMgr.cli_tool_list:
            self.write_ref( f, item)
        f.write('  </sect1>')
        f.write('  ')
        f.write('  ')
        f.write('  ')
        f.write('</book>')
        f.flush()
        os.spawnlp( os.P_WAIT, "yelp", "yelp", fname)
        f.close()

    def write_ref( self, f, item):
        f.write('<sect2>')
        f.write('  <title>%s</title>' % item[0])
        f.write('  <simlesect>')
        f.write('    <title>Options</title>')
        f.write('    <variablelist>')
        oclass = item[3]( item[0])
        print oclass
        for arg in oclass.options_help.keys():
            f.write('      <variablelist>')
            f.write('        <varlistentry>')
            f.write('          <term><command>%s</command>: %s</term>' % (arg, oclass.options_help[arg][0]))
            f.write('          <listitem>')
            f.write('            <para>%s</para>' % oclass.options_help[arg][1])
            if type(oclass.options_help[arg][2]) in [list,tuple]:
                if oclass.options_help[arg][3]:
                    f.write('          <orderedlist>')
                    for val in oclass.options_help[arg][2]:
                        f.write( "      <listitem>%s</listitem>" % val)
                    f.write('          </orderedlist>')
                else:
                    f.write('          <itemizedlist>')
                    for val in oclass.options_help[arg][2]:
                        f.write( "      <listitem>%s</listitem>" % val)
                    f.write('          </itemizedlist>')
            else:
                f.write('            <para>Value: <userinput>%s</userinput></para>' % oclass.options_help[arg][2])
            f.write('          </listitem>')
            f.write('        </varlistentry>')
            f.write('      </variablelist>')

        f.write('    </variablelist>')
        f.write('  </simlesect>')
        f.write('</sect2>')
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    name = 'cmdref',
    category = Tool.TOOL_DEBUG,
    tool_class = CmdRef,
    options_class = Tool.ToolOptions,
    modes = Tool.MODE_GUI | Tool.MODE_CLI,
    translated_name = _("Generate Commandline Reference for Reports and Tools"),
    author_name = "Martin Hawlisch",
    author_email = "martin@hawlisch.de",
    description=_("Generates a DocBook XML file that contains a parameter reference of Reports and Tools.")
    )
