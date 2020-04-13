#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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
from gramps.gen.plug._pluginreg import newplugin, STABLE
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

MODULE_VERSION="5.2"

#------------------------------------------------------------------------
#
# Ascii docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'asciidoc'
plg.name = _("Plain Text")
plg.description = _("Generates documents in plain text format (.txt).")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'asciidoc.py'
plg.ptype = DOCGEN
plg.docclass = 'AsciiDoc'
plg.optionclass = 'AsciiDocOptions'
plg.paper = True
plg.style = True
plg.extension = "txt"

#------------------------------------------------------------------------
#
# GTKPrint docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'gtkprint'
plg.name = _('Print...')
plg.description = _("Generates documents and prints them directly.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'gtkprint.py'
plg.ptype = DOCGEN
plg.docclass = 'GtkPrint'
plg.optionclass = None
plg.paper = True
plg.style = True
plg.extension = ""

#------------------------------------------------------------------------
#
# HtmlDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'htmldoc'
plg.name = _('HTML')
plg.description = _("Generates documents in HTML format.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'htmldoc.py'
plg.ptype = DOCGEN
plg.docclass = 'HtmlDoc'
plg.optionclass = None
plg.paper = False
plg.style = True
plg.extension = "html"

#------------------------------------------------------------------------
#
# LaTeXDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'latexdoc'
plg.name = _('LaTeX')
plg.description = _("Generates documents in LaTeX format.")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'latexdoc.py'
plg.ptype = DOCGEN
plg.docclass = 'LaTeXDoc'
plg.optionoclass = None
plg.paper = True
plg.style = False
plg.extension = "tex"

#------------------------------------------------------------------------
#
# ODFDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'odfdoc'
plg.name = _('OpenDocument Text')
plg.description = _("Generates documents in OpenDocument "
                     "Text format (.odt).")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'odfdoc.py'
plg.ptype = DOCGEN
plg.docclass = 'ODFDoc'
plg.optionclass = None
plg.paper = True
plg.style = True
plg.extension = "odt"

#------------------------------------------------------------------------
#
# PdfDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'pdfdoc'
plg.name = _('PDF document')
plg.description = _("Generates documents in PDF format (.pdf).")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'cairodoc.py'
plg.ptype = DOCGEN
plg.docclass = 'PdfDoc'
plg.optionclass = None
plg.paper = True
plg.style = True
plg.extension = "pdf"

#------------------------------------------------------------------------
#
# PSDrawDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'psdrawdoc'
plg.name = _('PostScript')
plg.description = _("Generates documents in PostScript format (.ps).")
plg.version = '2.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'cairodoc.py'
plg.ptype = DOCGEN
plg.docclass = 'PsDoc'
plg.optionclass = None
plg.paper = True
plg.style = True
plg.extension = "ps"

#------------------------------------------------------------------------
#
# RTFDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'rftdoc'
plg.name = _('RTF document')
plg.description = _("Generates documents in Rich Text format (.rtf).")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'rtfdoc.py'
plg.ptype = DOCGEN
plg.docclass = 'RTFDoc'
plg.optionclass = None
plg.paper = True
plg.style = True
plg.extension = "rtf"

#------------------------------------------------------------------------
#
# SvgDrawDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id = 'SVG (Scalable Vector Graphics)'
plg.name = _('SVG document')
plg.description = _("Generates documents in Scalable "
                     "Vector Graphics format (.svg).")
plg.version = '1.0'
plg.gramps_target_version = MODULE_VERSION
plg.status = STABLE
plg.fname = 'svgdrawdoc.py'
plg.ptype = DOCGEN
plg.docclass = 'SvgDrawDoc'
plg.optionclass = 'SvgDrawDocOptions'
plg.paper = True
plg.style = True
plg.extension = "svg"
