import time
import gtk
import gobject

import sys, os
sys.path.append("../src")

#from Models import PersonModel,PersonFilterModel
from TreeViews import PersonTreeView
import GenericFilter

## class ProxyPerson(object):
##     """
##     This class provides a wrapper around the real object that
##     is stored in the model. 
##     """
    
##     def __init__(self,id,db):
##         self._id = id
##         self._db = db
##         self._obj = None

##     def row_ref(self):
##         """This should return the value that is used
##         as the row reference in the model."""
##         return self._id

##     def __getattr__(self, name):
##         """
##         Delegate to the real object.
##         """

##         # Fetch the object from the database if we
##         # don't already have it
##         if self._obj is None:
##             self._obj = self._get_object()

##         # Call the method that we were asked
##         # for on the real object.
##         return getattr(self._obj, name)

##     def _get_object(self):
##         """
##         Fetch the real object from the database.
##         """
##         print "getting object = ", self._id
##         return self._db.get_person_from_handle(self._id)

    
class PersonWindow(gtk.Window):

    def __init__(self,db):
        gtk.Window.__init__(self)

        self.set_default_size(700,300)

        self._db = db

        fil = GenericFilter.GenericFilter()
        fil.add_rule(GenericFilter.SearchName(["Taylor"]))

        person_tree = PersonTreeView(db,fil)        
        person_tree.show()

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrollwindow.show()        
        scrollwindow.add(person_tree)        
        self.add(scrollwindow)

        person_tree.clear_filter()
        
        #person_tree.set_filter(fil)
        #person_model = PersonFilterModel(db,fil)
	#person_tree.set_model(person_model)

        self._person_tree = person_tree
        #self._person_model = person_model

	#gobject.idle_add(self.load_tree().next)
        
        self._expose_count = 0

##     def load_tree(self):
##         self._person_tree.freeze_child_notify()

##         for i in self._db.get_person_handles():
##             self._person_model.add(ProxyPerson(i,self._db))
##             yield True
            
##         self._person_tree.thaw_child_notify()
        
##         self._person_tree.set_model(self._person_model)

##         yield False

if __name__ == "__main__":
    import sys, os
    sys.path.append("..")
    
    import GrampsDb
    import const
    import logging
    
    form = logging.Formatter(fmt="%(relativeCreated)d: %(levelname)s: %(filename)s: line %(lineno)d: %(message)s")
    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setFormatter(form)
    stderrh.setLevel(logging.DEBUG)

    # everything.
    l = logging.getLogger()
    l.setLevel(logging.DEBUG)
    l.addHandler(stderrh)


    def cb(d):
        pass

    def main():
	print "start", sys.argv[1]
        
        db = GrampsDb.gramps_db_factory(const.app_gramps)()
        db.load(os.path.realpath(sys.argv[1]),
                cb, # callback
                "w")

	print "window"
        w = PersonWindow(db)
        w.show()

        w.connect("destroy", gtk.main_quit)

	print "main"
        gtk.main()

    #import profile
    #profile.run('main()','profile.out')

    main()
