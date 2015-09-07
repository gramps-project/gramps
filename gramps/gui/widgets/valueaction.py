#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
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

"ValueAction class."

__all__ = ["ValueAction"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.valueaction")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .valuetoolitem import ValueToolItem

#-------------------------------------------------------------------------
#
# ValueAction class
#
#-------------------------------------------------------------------------
class ValueAction(Gtk.Action):
    """
    Value action class.

    (A ValueAction with menu item doesn't make any sense.)
    """
    __gtype_name__ = "ValueAction"

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST,
                    None, #return value
                    ()), # arguments
    }

    def __init__(self, name, tooltip, default, itemtype, *args):
        """
        Create a new ValueAction instance.

        :param name: the name of the action
        :type name: str
        :param tooltip: tooltip string
        :type tooltip: str
        :param default: default value for the action, it will set the type of
                        the action and thus the type of all the connected
                        proxies.
        :type default: set by itemtype
        :param itemtype: default tool item class
        :type itemtype: :class:`.ValueToolItem` subclass
        :param args: arguments to be passed to the default toolitem class
                     at creation. see: :meth:`do_create_tool_item`
        :type args: list
        """
        Gtk.Action.__init__(self, name=name, label='', tooltip=tooltip,
                            stock_id=None)

        self._value = default
        self._data_type = type(default)

        # have to be remembered, because we can't access
        # GtkAction->toolbar_item_type later.
        self._default_toolitem_type = itemtype
##TODO GTK3: following is deprecated, must be replaced by
##        itemtype.set_related_action(ValueAction) in calling class?
##        self.set_tool_item_type(itemtype)
        self._args_for_toolitem = args

        self._handlers = {}

    def do_changed(self):
        """
        Default signal handler for 'changed' signal.

        Synchronize all the proxies with the active value.
        """
        for proxy in self.get_proxies():
            proxy.handler_block(self._handlers[proxy])
            proxy.set_value(self._value)
            proxy.handler_unblock(self._handlers[proxy])

    def do_create_tool_item(self):
        """
        Create a 'default' toolbar item widget.

        Override the default method, to be able to pass the required
        parameters to the proxy's constructor.

        This method is called from Gtk.UIManager.ensure_update(), when a
        'toolitem' is found in the UI definition with a name refering to a
        ValueAction. Thus, to use the action via the UIManager a 'default'
        toolitem type has to be set with the Gtk.Action.set_tool_item_type()
        method, before invoking the Gtk.UIManager.ensure_update() method.

        Widgets other than the default type has to be created and added
        manually with the Gtk.Action.connect_proxy() method.

        :returns: a toolbar item connected to the action.
        :rtype: :class:`.ValueToolItem` subclass
        """
        proxy = self._default_toolitem_type(self._data_type,
                                            self._args_for_toolitem)
        self.connect_proxy(proxy)
        return proxy

    def _on_proxy_changed(self, proxy):
        """Signal handler for the proxies' 'changed' signal."""
        value = proxy.get_value()
        if value is not None:
            self.set_value(value)

    def connect_proxy(self, proxy):
        """
        Connect a widget to an action object as a proxy.

        :param proxy: widget to be connected
        :type proxy: :class:`.ValueToolItem` subclass
        """
        if not isinstance(proxy, ValueToolItem):
            raise TypeError

        # do this before connecting, so that we don't call the handler
        proxy.set_value(self._value)
        self._handlers[proxy] = proxy.connect('changed', self._on_proxy_changed)

        # if this is called the proxy will appear on the proxy list twice. why?
        #Gtk.Action.connect_proxy(self, proxy)

    def set_value(self, value):
        """Set value to action."""
        if not isinstance(value, self._data_type):
            raise TypeError

        self._value = value
        self.emit('changed')

    def get_value(self):
        """Get the value from the action."""
        return self._value
