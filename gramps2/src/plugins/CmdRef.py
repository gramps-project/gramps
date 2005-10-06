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
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<!DOCTYPE book PUBLIC "-//OASIS//DTD DocBook XML V4.1.2//EN" ')
        f.write('   "http://www.oasis-open.org/docbook/xml/4.1.2/docbookx.dtd">\n')
        f.write('<appendix id="plugin_ref" lang="en">\n')
        f.write('  <title>Reports and Tools parameter reference</title>\n')
        f.write('  <sect1 id="reps">\n')
        f.write('    <title>Reports</title>\n')
        for item in PluginMgr.cl_list:
            self.write_ref( f, item)
        f.write('  </sect1>\n')
        f.write('  <sect1 id="plugin_ref_tools">\n')
        f.write('    <title>Tools</title>\n')
        for item in PluginMgr.cli_tool_list:
            self.write_ref( f, item)
        f.write('  </sect1>')
        f.write('  ')
        f.write('  ')
        f.write('  ')
        f.write('</appendix>')
        f.flush()
        os.spawnlp( os.P_WAIT, "yelp", "yelp", fname)
        f.close()

    def fix(self,line):
        l = line.strip()
        l = l.replace('&','&amp;')
        l = l.replace('>','&gt;')
        l = l.replace('<','&lt;')
        return l.replace('"','&quot;')

    def write_ref( self, f, item):
        f.write('<sect2 id="tool_opt_%s">\n' % item[0])
        f.write('  <title>%s</title>\n' % self.fix(item[0]))
        try:    # For Tools
            oclass = item[3]( item[0])
        except: # For Reports
            oclass = item[3]
        try:
            ohelp = oclass.options_help
        except:
            ohelp = None
        if ohelp:
            f.write('  <simplesect>\n')
            f.write('    <title>Options</title>\n')
            f.write('    <variablelist>\n')
            for arg in ohelp.keys():
                f.write('      <variablelist>\n')
                f.write('        <varlistentry>\n')
                f.write('          <term><command>%s</command>: %s</term>\n' % (self.fix(arg), self.fix(ohelp[arg][0])))
                f.write('          <listitem>\n')
                f.write('            <para>%s</para>\n' % self.fix(ohelp[arg][1]))
                if type(ohelp[arg][2]) in [list,tuple]:
                    if ohelp[arg][3]:
                        f.write('          <orderedlist>\n')
                        for val in ohelp[arg][2]:
                            f.write( "      <listitem>%s</listitem>\n" % self.fix(val))
                        f.write('          </orderedlist>\n')
                    else:
                        f.write('          <itemizedlist>\n')
                        for val in ohelp[arg][2]:
                            f.write( "      <listitem>%s</listitem>\n" % self.fix(val))
                        f.write('          </itemizedlist>\n')
                else:
                    f.write('            <para>Value: <userinput>%s</userinput></para>\n' % self.fix(ohelp[arg][2]))
                f.write('          </listitem>\n')
                f.write('        </varlistentry>\n')
                f.write('      </variablelist>\n')

            f.write('    </variablelist>\n')
            f.write('  </simplesect>\n')
        f.write('</sect2>\n')
    
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
