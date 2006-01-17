from gettext import gettext as _

import gtk
import gobject

from PeopleModel import PeopleModel

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    _('Spouse'),
    _('Last Change'),
    _('Cause of Death'),
    ]


class PersonTreeFrame(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5


    def __init__(self,dbstate):
	gtk.Frame.__init__(self)

        self._dbstate = dbstate
        self._selection = None
        self._model = None

        self._tree = gtk.TreeView()
        self._tree.set_rules_hint(True)
        self._tree.set_headers_visible(True)
        #self._tree.connect('key-press-event',self.key_press)

        renderer = gtk.CellRendererText()

        column = gtk.TreeViewColumn(_('Name'), renderer,text=0)
        column.set_resizable(True)
        column.set_min_width(225)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._tree.append_column(column)
       
        for pair in self._dbstate.db.get_person_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, renderer, markup=pair[1])
            column.set_resizable(True)
            column.set_min_width(60)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            self._tree.append_column(column)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        scrollwindow.add(self._tree)

        self.add(scrollwindow)

        self.set_model(self._dbstate.db)

    def set_model(self,db):

        self._model = PeopleModel(db)

        self._tree.set_model(self._model)

        self._selection = self._tree.get_selection()

    def get_selection(self):
        return self._selection
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonTreeFrame)

if __name__ == "__main__":

    w = ObjectSelectorWindow()
    w.show_all()
    w.connect("destroy", gtk.main_quit)

    gtk.main()
