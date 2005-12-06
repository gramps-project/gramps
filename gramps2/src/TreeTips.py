# File: treetips.py
# Author: Toshio Kuratomi <toshio@tiki-lounge.com>
# Date: 6 April, 2004
# Copyright: Toshio Kuratomi
# License: GPL
# Id: $Id$
"""A tooltip class for TreeViews
"""
__revision__ = "$Rev$"


#
# Support for text markup added: March 05 - rjt-gramps <at> thegrindstone.me.uk
# Support for tooltips to be functions added: March 05 - rjt-gramps <at> thegrindstone.me.uk
#

import gtk
import gobject

class TreeTips(gtk.Widget):
    ''' A tooltips widget specialized to work with gtk.TreeView's.

    TreeTips associates a column in a TreeStore with tooltips that will be
    displayed when the mouse is over the row the column is for.  Each row can
    have one treetip.
    ''' 
    __gproperties__ = {
        'tip_window' : (gobject.TYPE_PYOBJECT,
                'The window that the tooltip is displayed in.',
                'The window that the tooltip is displayed in.',
                gobject.PARAM_READABLE),
        'tip_label' : (gobject.TYPE_PYOBJECT,
                'The label that displays the tooltip text.',
                'The label that displays the tooltip text.',
                gobject.PARAM_READABLE),
        'active_tips_data' : (gobject.TYPE_PYOBJECT,
                'The data associated with the active tooltip.',
                'The data associated with the active tooltip.',
                gobject.PARAM_READABLE),
        'delay' : (gobject.TYPE_INT,
                'MSecs before displaying the tooltip.',
                'The delay between the mouse pausing over the widget and the display of the tooltip in msec.',
                0, 60000, 2000,
                gobject.PARAM_READWRITE),
        'enabled' : (gobject.TYPE_BOOLEAN,
                'If TRUE the tooltips are enabled',
                'If TRUE the tooltips are enabled',
                True,
                gobject.PARAM_READABLE),
        'view' : (gobject.TYPE_PYOBJECT,
                'gtk.TreeView that we get our data from.',
                'The tip data comes from a column in a gtk.TreeView.',
                gobject.PARAM_READWRITE),
        'column' : (gobject.TYPE_INT,
                'Column from the gtk.TreeView that holds tip data.',
                'The tip data for each row is held by a column in the row.  This specifies which column that data is in.',
                0, 32000, 0,
                gobject.PARAM_READWRITE),
        'markup_enabled' : (gobject.TYPE_BOOLEAN,
                'If TRUE the tooltips are in Pango Markup',
                'If TRUE the tooltips are in Pango Markup',
                False,
                gobject.PARAM_READWRITE),

    }

    def __init__(self, treeview=None, column=None, markup_enabled=False):
        '''Create a new TreeTips Group.

        :Parameters:
            treeview : gtk.TreeView === Treeview for which the tips display,
                default is None.
            column : integer === Column id in the Treemodel holding the treetip
                    text, default is None.
            markup_enabled : bool === If True the tooltips are in Pango Markup,
                    if False the tooltips are in plain text.
        '''
        if treeview:
            try:
                treeview.connect('leave-notify-event', self.__tree_leave_notify)
                treeview.connect('motion-notify-event', self.__tree_motion_notify)
            except (AttributeError, TypeError):
                raise TypeError, ('The value of view must be an object that'
                        'implements leave-notify-event and motion-notify-event '
                        'gsignals such as gtk.TreeStore.')

        gobject.GObject.__init__(self)

        self.view = treeview or None
        self.delay = 2000
        self.enabled = True
        self.column = column or 0
        self.markup_enabled = markup_enabled
        self.tip_window = gtk.Window(gtk.WINDOW_POPUP)
        self.tip_window.set_app_paintable(True)
        self.tip_window.set_border_width(4)
        self.tip_window.connect('expose-event', self.__paint_window)
        self.tip_label = gtk.Label('')
        self.tip_label.set_line_wrap(True)
        self.tip_label.set_alignment(0.5, 0.5)
        self.active_tips_data = ''
        self.tip_window.add(self.tip_label)
        self.unique = 1 # Unique number used for timeouts
        self.timeoutID = 0
        self.path = None
        self.screenWidth = gtk.gdk.screen_width()
        self.screenHeight = gtk.gdk.screen_height()

    def enable(self):
        '''Enable showing of tooltips'''
        self.enabled = True

    def disable(self):
        '''Disable showing tooltips'''
        self.enabled = False
       
    def do_get_property(self, prop):
        '''Return the gproperty's value.'''
        if prop.name == 'delay':
            return self.delay
        elif prop.name == 'enabled':
            return self.enabled
        elif prop.name == 'view':
            return self.view
        elif prop.name == 'column':
            return self.column
        elif prop.name == 'active-tips-data':
            return self.active_tips_data
        elif prop.name == 'tip-label':
            return self.tip_label
        elif prop.name == 'tip-window':        
            return self.tip_window
        elif prop.name == 'markup_enabled':
            return self.markup_enabled
        else:
            raise AttributeError, 'unknown property %s' % prop.name

    def do_set_property(self, prop, value):
        '''Set the property of writable properties.

        '''
        if prop.name == 'delay':
            self.delay = value
        elif prop.name == 'view':
            try:
                value.connect('leave-notify-event', self.__tree_leave_notify)
                value.connect('motion-notify-event', self.__tree_motion_notify)
            except (AttributeError, TypeError):
                raise TypeError, ('The value of view must be an object that'
                        'implements leave-notify-event and motion-notify-event '
                        'gsignals')
            self.view = value
        elif prop.name == 'column':
            self.column = value
        elif prop.name == 'markup_enabled':
            self.markup_enabled = value
        else:
            raise AttributeError, 'unknown or read only property %s' % prop.name

    def __paint_window(self, window, event):
        window.style.paint_flat_box(window.window, gtk.STATE_NORMAL,
                gtk.SHADOW_OUT, None, window,
                'tooltip', 0, 0, -1, -1)
        
    def __tree_leave_notify(self, tree, event):
        '''Hide tooltips when we leave the tree.'''

        self.timeoutID = 0
        self.path = None
        self.tip_window.hide()

    def __tree_motion_notify(self, tree, event):
        '''Decide which tooltip to display when we move within the tree.'''

        if not self.enabled:
            return
        self.tip_window.hide()
        self.path = None
        self.unique += 1
        self.timeoutID = self.unique
        gobject.timeout_add(self.delay, self.__treetip_show, tree,
                int(event.x), int(event.y), self.timeoutID)

    def __treetip_show(self, tree, xEvent, yEvent, ID):
        '''Show the treetip window.'''
        if self.timeoutID != ID:
            return False
        pathReturn = tree.get_path_at_pos(xEvent, yEvent)
        model = tree.get_model()
        if pathReturn == None:
            self.path = None
        elif self.path != pathReturn[0]:
            self.path = pathReturn[0]
            rowIter = model.get_iter(self.path)
            tip = model.get_value(rowIter, self.column)
            # The tip can be either a string or
            # a function that returns a string.
            if type(tip) == str:
                text = tip
            elif callable(tip):
                text = tip()
            else:
                text = ""
            self.active_tips_data = text
            if not text:
                if self.markup_enabled:
                    self.tip_label.set_markup('')
                else:
                    self.tip_label.set_text('')
                return False

            if self.markup_enabled:
                self.tip_label.set_markup(text)
            else:
                self.tip_label.set_text(text)
            x, y = self.tip_label.size_request()
            self.tip_window.resize(x, y)
            windowWidth, windowHeight = self.tip_window.get_size()
            cellInfo = tree.get_cell_area(self.path, pathReturn[1])
            x, y = self.__compute_tooltip_position(cellInfo, windowWidth, windowHeight)
            self.tip_window.move(int(x), int(y))
            self.tip_window.show_all()

        return False

    def __compute_tooltip_position(self, cellInfo, popupWidth, popupHeight):
        '''Figures out where the tooltip should be placed on the page::

          [p] = pointer
          x =      [p]
               +---------+
          (half on each side)
  
          y =      [p]
              +------------+
              |____________|
          If it fits else:
              +------------+
              |____________|
                   [p]
        '''

        xOrigin, yOrigin = self.view.get_bin_window().get_origin()
        x = xOrigin + cellInfo.x + cellInfo.width/2 - popupWidth/2
        if x < 0:
            x = 0
        elif x + popupWidth > self.screenWidth:
            x = self.screenWidth - popupWidth

        y = yOrigin + cellInfo.y + cellInfo.height + 3
        if y + popupHeight > self.screenHeight:
            y = yOrigin + cellInfo.y - 3 - popupHeight
            if y < 0:
                y = 0

        return x, y


if gtk.pygtk_version < (2,8,0):
    gobject.type_register(TreeTips)
