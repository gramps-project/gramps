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

# $Id: libhtml.py 10874 2009-03-03 18:00:00Z gbritton $

#------------------------------------------------------------------------
#
# Html
#
#------------------------------------------------------------------------

"""
HTML operations.

This module exports the Html class

"""

__all__ = ['Html']

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------

try:
    from gettext import gettext as _
    from gen.plug import PluginManager, Plugin
except ImportError:
    print 'Plugin manager not imported.'

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# XHTML DOCTYPE constants to be used in <!DOCTYPE ... > statements
#
#------------------------------------------------------------------------

_XHTML10_STRICT = '"-//W3C//DTD XHTML 1.0 Strict//EN"\n' \
                  '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'
_XTHML10_TRANS = '"-//W3C//DTD XHTML 1.0 Transitional//EN"\n' \
                 '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"'
_XHTML10_FRAME = '"-//W3C//DTD XHTML 1.0 Frameset//EN"\n' \
                 '\t"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"'
_XHTML11 = '"-//W3C//DTD XHTML 1.1//EN"\n' \
           '\t"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"'
_XHTML10_BASIC = '"-//W3C//DTD XHTML Basic 1.0//EN"\n' \
                 '\t"http://www.w3.org/TR/xhtml-basic/xhtml-basic10.dtd"'
_XHTML11_BASIC = '"-//W3C//DTD XHTML Basic 1.1//EN"\n ' \
                 '\t"http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd"'

#------------------------------------------------------------------------
#
# XML Namespace constant for use in <html xmlns=...> tags 
#
#------------------------------------------------------------------------

_XMLNS = "http://www.w3.org/1999/xhtml"

#------------------------------------------------------------------------
#
# Local constants.
#
#------------------------------------------------------------------------

_START_CLOSE = (
    'area', 
    'base', 
    'br', 
    'frame', 
    'hr',
    'img', 
    'input', 
    'link', 
    'meta', 
    'param'
    )

#------------------------------------------------------------------------
#
# Helper functions.
#
#------------------------------------------------------------------------

def print_(line):
    """
    Print function
    """
    print line

#------------------------------------------------------------------------
#
# Html class.
#
#------------------------------------------------------------------------

class Html(list):
    """
    HTML class: Manages a rooted tree of HTML objects
    """
    __slots__ = ['items', 'indent', 'inline', 'end']
#
    @staticmethod
    def xmldecl(version=1.0, encoding="UTF-8", standalone="no"):
        """
        Build and return an XML declaration statement

        :type  version: decimal number
        :param version: version of XML to be used. Defaults to 1.0
        :type  encoding: string
        :param encoding: encoding method to be used. Defaults to "UTF-8"
        :type  standalone: string
        :param standalone: "yes" or "no".  Defaults to "no"
        """
        return '<?xml %s %s %s?>' % (
            'version="%s"' % version,
            'encoding="%s"' % encoding,
            'standalone="%s"' % standalone
            )
#
    @staticmethod
    def doctype(name='html', public='PUBLIC', external_id=_XHTML10_STRICT):
        """
        Build and return a DOCTYPE statement

        :type  name: string
        :param name: name of this DOCTYPE. Defaults to "html"
        :type  public: string
        :param public: class of this DOCTYPE. Defaults to 'PUBLIC
        :type  external_id: string
        :param external_id: external identifier of this DOCTYPE. 
                            Defaults to XHTML 1.0 STRICT
        :type  args: object
        :param args: 0 or more positional parameters to be added to this    
                     DOCTYPE.
        """
        return '<!DOCTYPE %s %s %s>' % (
            name,
            public, 
            external_id,
            )
#
    @staticmethod
    def html(xmlns=_XMLNS, lang='en', *args, **keywargs):
        """
        Build and return a properly-formated <html> object

        :type  xmlns: string
        :param xmlns: XML namespace string. Default = 'http://www.w3.org/1999/xhtml'
        :type  lang: string
        :param lang: language to be used. Defaul = 'en'
        :rtype:   reference to new Html instance
        :returns:  reference to the newly-created Html instances for <html> object
        """      
        return Html('html',
            indent=False,
            xmlns=xmlns,
            attr='xml:lang="%s" lang="%s"' % ((lang,)*2),
            *args, **keywargs
            )
#
    @staticmethod
    def head(title=None, encoding='utf-8', *args, **keywargs):
        """
        Build and return a properly-formated <head> object
    
        :type  title: string or None
        :param title: title for HTML page. Default=None. If None no 
                    title tag is written
        :type  encoding: string
        :param encoding: encoding to be used. Default = 'utf-8'
        :rtype:  reference to new Html instance
        :returns: reference to the newly-created Html instances for <head> object
        """ 
        meta1 = 'http-equiv="content-type" content="text/html;charset=%s"'
        meta2 = 'http-equiv="Content-Style-Type" content="text/css"'
        head = Html('head', *args, **keywargs) 
        if title is not None: 
            head += (Html('title', title, inline=True, indent=True))
        head += Html('meta', attr=meta1 % encoding, indent=True)
        head += Html('meta', attr=meta2, indent=True)
        return head
#
    @staticmethod
    def page(title=None, encoding='utf-8', lang='en', *args, **keywargs):
        """
        This function prepares a new Html class based page and returns
    
        :type  title: string
        :param title: title for HTML page. Default=None
        :type  encoding: string
        :param encoding: encoding to be used. Default = 'utf-8'
        :type  lang: string
        :param lang: language to be used. Defaul = 'en'
        :rtype:   three object references
        :returns:  references to the newly-created Html instances for
                  page, head and body
        """
        page = Html.html(lang=lang, *args, **keywargs)
        page.addXML(encoding=encoding)
        page.addDOCTYPE()
#
        head = Html.head(title=title,
               encoding=encoding,
               lang=lang,
               indent=False,
               *args, **keywargs 
               )
#
        body = Html('body', indent=False, *args, **keywargs)
        page += (head, body)
        return page, head, body
#
    def __init__(self, tag='html', *args, **keywargs):
        """
        Class Constructor: Returns a new instance of the Html class
        
        :type  tag: string
        :param tag: The HTML tag. Default is 'html'
        :type  args: optional positional parameters
        :param args: 0 more positional arguments to be inserted between
                     opening and closing HTML tags.
        :type  indent: boolean or None
        :param indent: True  ==> indent this object with respect to its parent
                       False ==> do not indent this object
                       None  ==> no indent for this object (use eg for pre tag)
                       Defaults to True
        :type  inline: boolean
        :param inline: True  ==> instructs the write() method to output this
                                 object and any child objects as a single string
                       False ==> output this object and its contents one string
                                 at a time
                       Defaults to False
        :type  close: boolean or None
        :param close: True  ==> this tag should be closed normally
                                e.g. <tag>...</tag>
                      False ==> this tag should be automatically closed
                                e.g. <tag />
                      None  ==> do not provide any closing for this tag
        :type  keywargs: optional keyword parameters
        :param keywargs: 0 or more keyword=argument pairs that should be
                         copied into the opening tag as keyword="argument"
                         attributes
        :rtype:   object reference
        :returns:  reference to the newly-created Html instance
        
        For full usage of the Html class with examples, please see the wiki
        page at: http://www.gramps-project.org/wiki/index.php?title=Libhtml
        """
        super(Html, self).__init__([])                  # instantiate object
        attr, indent, close, inline = '', True, True, False
#
#       Handle keyword arguments passed to this constructor.
#       Keywords that we process directly are handled. 
#       Keywords we don't recognize are saved for later 
#       addition to the opening tag as attributes.
#
        for keyw, arg in keywargs.iteritems():
            if (keyw in ['indent', 'close', 'inline'] and
               arg in [True, False, None]):
                exec '%s = %s' % (keyw, arg)            # keep these settings
            elif keyw == 'attr':                        # pass attributes along
                attr += ' ' + arg
            elif keyw[-1] == '_':                       # avoid Python conflicts
                attr += ' %s="%s"' % (keyw[:-1], arg)   # pass keyword arg along
            else:
                attr += ' %s="%s"' % (keyw, arg)        # pass keyword arg along
#
        self.indent = indent                                
        self.inline = inline
        self.end = close
#
        if tag[0] == '<':               # if caller provided preformatted tag?
            self[0:] = [tag]            #   add it in
            self.end = None
        else: 
            if tag in _START_CLOSE:         # if tag in special list
                self.end = close = False    #   it needs no closing tag
            begin = '<%s%s%s>' % (      # build opening tag with attributes
                tag,
                attr,
                ('' if close or close is None else ' /')
                )
#
            self[0:] = [begin] + list(args)         # add beginning tag
            if close:                               # if need closing tab
                self[len(self):] = ['</%s>' % tag]         #   add it on the end
#
    def __add(self, value):
        """
        Helper function for +, +=, operators and append() and extend()
        methods

        :type  value: object
        :param value: object to be added

        :rtype:  object reference
        :returns: reference to object with new value added
        """
        if isinstance(value, Html) or not hasattr(value, '__iter__'):
            value = [value]
        index = len(self) - (1 if self.end else 0)
        self[index:index] = value
        return self
#
    def __add__(self, value):
        """
        Overload method for + and += operators
        """
        return self.__add(value)
    __iadd__ = __add__
#
    def append(self, value):
        """
        Append a new value
        """
        self.__add(value)
    extend = append
#
    def replace(self, cur_value, value):
        """
        Replace current value with new value

        :type  cur_value: object
        :param cur_value: value of object to be replaced
        :type  value: object
        :param value: replacement value

        :rtype:  object reference
        :returns: reference to object with new value added
        """
        self[self.index(cur_value)] = value
#
    def __sub__(self, value):
        """
        Overload function for - and -= operators
        :type  value: object
        :param value: object to be removed

        :rtype:  object reference
        :returns: reference to object with value removed
        """
        del self[self.index(value)]
        return self
#
    __isub__ = remove = __sub__
#
    def __str__(self):
        """
        Returns string representation

        :rtype:  string
        :returns: string representation of object
        """
        return '%s'*len(self) % tuple(self[:])
#
    def __iter__(self):
        """
        Iterator function: returns a generator that performs an
        insertion-order tree traversal and yields each item found.
        """
        for item in self[:]:                    # loop through all list elements
            if isinstance(item, Html):     # if nested list found
                for sub_item in item:           #     recurse
                    yield sub_item
            else:
                yield item
#
    iterkeys = itervalues = iteritems = __iter__
#
    def write(self, method=print_, indent='\t', tabs=''):
        """
        Output function: performs an insertion-order tree traversal
        and calls supplied method for each item found.

        :type  method: function reference
        :param method: function to call with each item found
        :type  indent: string
        :param indenf: string to use for indentation. Default = '\t' (tab)
        :type  tabs: string
        :param tabs: starting indentation
        """
        if self.indent is None:
            tabs = ''
        elif self.indent: 
            tabs += indent
        if self.inline:                         # if inline, write all list and
            method('%s%s' % (tabs, self))       # nested list elements
#
        else:
            for item in self[:]:                # else write one at a time
                if isinstance(item, Html):      # recurse if nested Html class
                    item.write(method=method, indent=indent, tabs=tabs)
                else:
                    method('%s%s' % (tabs, item))         # else write the line
#
    def addXML(self, version=1.0, encoding="UTF-8", standalone="no"):
        """
        Add an XML statement to the start of the list for this object

        :type  version: decimal number
        :param version: version of XML to be used. Defaults to 1.0
        :type  encoding: string
        :param encoding: encoding method to be used. Defaults to "UTF-8"
        :type  standalone: string
        :param standalone: "yes" or "no".  Defaults to "no"
        """
        xmldecl = Html.xmldecl(
            version=version,
            encoding=encoding,
            standalone=standalone
            )
        self[0:0] = [xmldecl]
#
    def addDOCTYPE(self, name='html', external_id=_XHTML10_STRICT, *args):
        """
        Add a DOCTYPE statement to the start of the list

        :type  name: string
        :param name: name of this DOCTYPE. Defaults to "html"
        :type  external_id: string
        :param external_id: external identifier of this DOCTYPE. 
                            Defaults to XHTML 1.0 STRICT
        :type  args: object
        :param args: 0 or more positional parameters to be added to this    
                     DOCTYPE.
        """
        doctype = '<!DOCTYPE %s %s%s>' % (
            name, 
            external_id,
            ' %s'*len(args) % args
            )
        # Note: DOCTYPE declaration must follow XML declaration

        if len(self) and self[0][:6] == '<?xml ':
            self[1:1] = [doctype]
        else:
            self[0:0] = [doctype]
#
    def __gettag(self):
        """
        Returns HTML tag for this object

        :rtype:  string
        :returns: HTML tag
        """
        return self[0].split()[0].strip('< >')
#
    def __settag(self, newtag):
        """
        Sets a new HTML tag for this object

        :type  name: string
        :param name: new HTML tag
        """
        curtag = self.tag
        if self[-1] == '</%s>' % curtag:
            self[-1] = '</%s>' % newtag
        self[0] = self[0].replace('<' + curtag, '<' + newtag)
    tag = property(__gettag, __settag)
#
    def __getattr(self):
        """
        Returns HTML attributes for this object

        :rtype:  string
        :returns: HTML attributes
        """
        attr = self[0].strip('<!?>').split(None, 1)
        return attr[1] if len(attr) > 1 else ''
#
    def __setattr(self, value):
        """
        Sets new HTML attributes for this object

        :type  name: string
        :param name: new HTML attributes
        """
        self[0] = self[0][:len(self.tag)+1] + ' ' + value + self[0][-1:]
#
    def __delattr(self):
        """
        Removes HTML attributes for this object
        """
        self[0] = '<' + self.tag + '>'
    attr = property(__getattr,  __setattr, __delattr)
#
    def __getinside(self):
        """
        Returns list of items between opening and closing tags

        :rtype:  list
        :returns: list of items between opening and closing HTML tags 
        """
        return self[1:-1]
#
    def __setinside(self, value):
        """
        Sets new contents between opening and closing tags

        :type  name: list
        :param name: new HTML contents
        """
        if len(self) < 2:
            raise AttributeError, 'No closing tag. Cannot set inside value' 
        if isinstance(value, Html) or not hasattr(value, '__iter__'):
            value = [value]
        self[1:-1] = value
#
    def __delinside(self):
        """
        Removes contents between opening and closing tag
        """
        if len(self) > 2:
            self[:] = self[:1] + self[-1:]
    inside = property(__getinside, __setinside, __delinside)
#
    def __enter__(self):
        return self
#
    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is None

# ------------------------------------------
#
#            Register Plugin
#
# -------------------------------------------

try:
    PluginManager.get_instance().register_plugin( 
    Plugin(
        name = __name__,
        description = _("Manages an HTML DOM tree."),
        module_name = __name__ 
        )
    )
except NameError:
    print 'Plugin not registered.'
