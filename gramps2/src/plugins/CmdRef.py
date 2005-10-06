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
import Tool
import Utils
import PluginMgr
import Report

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
        f.write('<?yelp:chunk-depth 2?>\n')
        f.write('<!DOCTYPE book PUBLIC "-//OASIS//DTD DocBook XML V4.1.2//EN" ')
        f.write('   "http://www.oasis-open.org/docbook/xml/4.1.2/docbookx.dtd">\n')
        f.write('<article id="index" lang="en">\n')
        f.write('  <title>Reports and Tools parameter reference</title>\n')
        f.write('  <sect1 id="reps">\n')
        f.write('    <title>Reports</title>\n')
        counter=0
        for item in PluginMgr.cl_list:
            category = item[1]
            if category in (Report.CATEGORY_BOOK,
                            Report.CATEGORY_CODE,
                            Report.CATEGORY_WEB):
                self.write_ref(f,item,counter,category)
            else:
                self.write_ref( f, item, counter, None)
            counter = counter + 1
        f.write('  </sect1>\n')
        f.write('  <sect1 id="tools">\n')
        f.write('    <title>Tools</title>\n')
        for item in PluginMgr.cli_tool_list:
            self.write_ref( f, item, counter)
            counter = counter + 1
        f.write('  </sect1>\n')
        f.write('  \n')
        f.write('  \n')
        f.write('  \n')
        f.write('</article>\n')
        f.flush()
        os.spawnlp( os.P_WAIT, "yelp", "yelp", fname)
        f.close()

    def write_ref( self, f, item,counter,category=None):
        f.write('<sect2 id="sect2id%d">\n' % counter)
        f.write('  <title>%s</title>\n' % item[0])
        f.write('  <simplesect>\n')
        f.write('    <title>Options</title>\n')
        f.write('    <variablelist>\n')
        if category == None:
            oclass = item[3]( item[0])
        elif category == Report.CATEGORY_BOOK:
            import BookReport
            oclass = BookReport.BookOptions(item[0])
        elif category == Report.CATEGORY_CODE:
            import GraphViz
            oclass = GraphViz.GraphVizOptions(item[0])
        elif category == Report.CATEGORY_WEB:
            if item[0] == "webpage":
                import WebPage
                oclass = WebPage.WebReportOptions(item[0])
            elif item[0] == "navwebpage":
                import NavWebPage
                oclass = NavWebPage.WebReportOptions(item[0])
                
        for arg in oclass.options_help.keys():
            f.write('      <variablelist>\n')
            f.write('        <varlistentry>\n')
            f.write('          <term><command>%s</command>: %s</term>\n'
                    % (escape(arg), escape(oclass.options_help[arg][0])))
            f.write('          <listitem>\n')
            f.write('            <para>%s</para>\n'
                    % escape(oclass.options_help[arg][1]))
            if type(oclass.options_help[arg][2]) in [list,tuple]:
                if oclass.options_help[arg][3]:
                    f.write('          <orderedlist>\n')
                    for val in oclass.options_help[arg][2]:
                        f.write( "      <listitem>%s</listitem>\n"
                                 % escape(val))
                    f.write('          </orderedlist>\n')
                else:
                    f.write('          <itemizedlist>\n')
                    for val in oclass.options_help[arg][2]:
                        f.write( "      <listitem>%s</listitem>\n"
                                 % escape(val))
                    f.write('          </itemizedlist>\n')
            else:
                f.write('            <para>Value: <userinput>%s</userinput></para>\n'
                        % escape(oclass.options_help[arg][2]))
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
    translated_name = _("Generate Commandline Reference "
                        "for Reports and Tools"),
    author_name = "Martin Hawlisch",
    author_email = "martin@hawlisch.de",
    description=_("Generates a DocBook XML file that contains "
                  "a parameter reference of Reports and Tools.")
    )
