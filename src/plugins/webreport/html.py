#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Gerald Britton <gerald.britton@gmail.com>
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

# $Id: html.py 10874 2009-03-03 18:00:00Z gbritton $

"""
HTML operations.

This module exports one class:

class Html: HTML generator
"""
#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import sys

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_XHTML1_STRICT = 'PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n' \
          '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'

class Html(object):
    """
    HTML class.
    """
    __slots__ = ['items','indent','inline','end']
#
    def __init__(self, tag='html', *args, **keywargs):
        attr, indent, close, inline = '', False, True, False
        for keyw, arg in keywargs.iteritems():
            if keyw in ['indent','close','inline'] and arg in [True,False,None]:
                exec '%s = %s' % (keyw, arg)
            elif keyw == 'attr':
                attr += ' ' + arg
            elif keyw[0] == '_':
                attr += ' %s="%s"' % (keyw[1:], arg)
            else:
                attr += ' %s="%s"' % (keyw, arg)
#
        if tag[0] == '<':
            self.items = (tag,)
            self.indent = indent
            self.inline = inline
            self.end = None
            return
#
        begin = '<%s%s%s>' % (
            tag,
            attr,
            ('' if close or close is None else ' /')
            )
#
        self.items = (begin,) + args
        self.end = '</%s>' % tag if close else None
        self.indent = indent
        self.inline = inline
#
    def __add__(self, data):
        self.items += data if isinstance(data,tuple) else (data,)
        return self
#
    append = extend = __add__
#
    def index(self,data):
        i = 0
        for item in self.items:
            if item == data:
                return i
            i += 1
        else:
            import sys
            raise ValueError, "Html.index: item not found", sys.exc_info()[2]
#
    def replace(self,data,newdata):
        i = self.index(data)
        self.items = self.items[:i] + (newdata,) + self.items[i+1:]
#
    def __sub__(self, data):
        i = self.index(data)
        self.items = self.items[:i] + self.items[i+1:]
        return self
#
    def _print(data):
        print data
#
    def write(self, method=_print, tabs=''):
        tabs += '\t' if self.indent else ''
        if self.inline:
            method('%s%s' % (tabs,self))
#
        else:
            for item in self.items:
                if isinstance(item, self.__class__):
                    item.write(tabs=tabs)
                else:
                    method('%s%s' % (tabs, item))
            if self.end is not None:
                method('%s%s' % (tabs, self.end))
#
    def __str__(self):
        return '%s'*len(self.items) % self.items + \
            (self.end or '')
#
    def __iter__(self):
        for item in self.items:
            if isinstance(item, self.__class__):
                for j in item:
                    yield j
            else:
                yield item
        if self.end is not None:
            yield self.end
#
    def XML(self,version=1.0, encoding="UTF-8", standalone="no"):
        return '<?xml %s %s %s?>' % (
            'version="%s"' % version,
            'encoding="%s"' % encoding,
            'standalone="%s"' % standalone
            )
#
    def addXML(self,version=1.0, encoding="UTF-8", standalone="no"):
        xml = self.XML(version=version, encoding=encoding, standalone=standalone)
        self.items = (xml,) + self.items
#
    def DOCTYPE(self,name='html', external_id=_XHTML1_STRICT, *args):
        return '<!DOCTYPE %s %s%s>' % (
            name, 
            external_id,
            ' %s'*len(args) % args
            )
#
    def addDOCTYPE(self,name='html', external_id=_XHTML1_STRICT, *args):
        doctype = self.DOCTYPE(name='html', external_id=_XHTML1_STRICT, *args)
        if len(self.items) > 0 and self.items[0][:6] == '<?xml ':
            self.items = self.items[:1] + (doctype,) + self.items[1:]
        else:
            self.items = (doctype,) + self.items


