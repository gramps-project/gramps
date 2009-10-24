
#------------------------------------------------------------------------
#
# Ascii docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'asciidoc'
plg.name  = _("Plain Text")
plg.description =  _("Generates documents in plain text format (.txt).")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'AsciiDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'AsciiDoc'
plg.paper = True
plg.style = True
plg.extension = "txt"

#------------------------------------------------------------------------
#
# GTKPrint docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'gtkprint'
plg.name  = _('Print...')
plg.description =  _("Generates documents and prints them directly.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'GtkPrint.py'
plg.ptype = DOCGEN
plg.basedocclass = 'GtkPrint'
plg.paper = True
plg.style = True
plg.extension = ""

#------------------------------------------------------------------------
#
# HtmlDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'htmldoc'
plg.name  = _('HTML')
plg.description =  _("Generates documents in HTML format.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'HtmlDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'HtmlDoc'
plg.paper = False
plg.style = True
plg.extension = "html"

#------------------------------------------------------------------------
#
# LaTeXDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'latexdoc'
plg.name  = _('LaTeX')
plg.description =  _("Generates documents in LaTeX format.")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'LaTeXDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'LaTeXDoc'
plg.paper = True
plg.style = False
plg.extension = "tex"

#------------------------------------------------------------------------
#
# ODFDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'odfdoc'
plg.name  = _('Open Document Text')
plg.description =  _("Generates documents in Open "
                     "Document Text format (.odt).")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'ODFDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'ODFDoc'
plg.paper = True
plg.style = True
plg.extension = "odt"

#------------------------------------------------------------------------
#
# PdfDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'pdfdoc'
plg.name  = _('PDF document')
plg.description =  _("Generates documents in PDF format (.pdf).")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'PdfDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'PdfDoc'
plg.paper = True
plg.style = True
plg.extension = "pdf"

#------------------------------------------------------------------------
#
# PSDrawDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'psdrawdoc'
plg.name  = _('PostScript')
plg.description =  _("Generates documents in postscript format (.ps).")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'PSDrawDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'PSDrawDoc'
plg.paper = True
plg.style = True
plg.extension = "ps"

#------------------------------------------------------------------------
#
# RTFDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'rftdoc'
plg.name  = _('RTF document')
plg.description =  _("Generates documents in Rich Text format (.rtf).")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'RTFDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'RTFDoc'
plg.paper = True
plg.style = True
plg.extension = "rtf"

#------------------------------------------------------------------------
#
# SvgDrawDoc docgen
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'SVG (Scalable Vector Graphics)'
plg.name  = _('RTF document')
plg.description =  _("Generates documents in Scalable "
                     "Vector Graphics format (.svg).")
plg.version = '1.0'
plg.status = STABLE
plg.fname = 'SvgDrawDoc.py'
plg.ptype = DOCGEN
plg.basedocclass = 'SvgDrawDoc'
plg.paper = True
plg.style = True
plg.extension = "svg"
