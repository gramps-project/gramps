"""
This module provides a progess dialog for displaying the status of 
long running operations.
"""
import logging
log = logging.getLogger(".GrampsDb")

from gettext import gettext as _

class _StatusObjectFacade(object):
    """This provides a simple structure for recording the information
    needs about a status object."""
    
    def __init__(self, status_obj, heartbeat_cb_id=None, end_cb_id=None):
        """
        @param status_obj: 
        @type status_obj: L{GrampsDb.LongOpStatus}
        
        @param heartbeat_cb_id: (default: None)
        @type heartbeat_cb_id: int
        
        @param end_cb_id: (default: None)
        @type end_cb_id: int
        """
        self.status_obj = status_obj
        self.heartbeat_cb_id = heartbeat_cb_id
        self.end_cb_id = end_cb_id
        self.pbar_idx = None
        self.active = False
        
class ProgressMonitor(object):
    """A dialog for displaying the status of long running operations.
    
    It will work with L{GrampsDb.LongOpStatus} objects to track the 
    progress of long running operations. If the operations is going to 
    take longer than I{popup_time} it will pop up a dialog with a 
    progress bar so that the user gets some feedback about what is 
    happening.
    """
    
    __default_popup_time = 5 # seconds
    
    def __init__(self, dialog_class, dialog_class_params=(),
                 title=_("Progress Information"), 
                 popup_time = None):
        """
        @param dialog_class: A class used to display the progress dialog.
        @type dialog_class: L{_GtkProgressDialog} or the same interface.
        
        @param dialog_class_params: A tuple that will be used as the initial
        arguments to the dialog_class, this might be used for passing in 
        a parent window handle.
        @type dialog_class_params: tuple
        
        @param title: The title of the progress dialog
        @type title: string
        
        @param popup_time: number of seconds to wait before popup.
        @type popup_time: int
        """
        self._dialog_class = dialog_class
        self._dialog_class_params = dialog_class_params
        self._title = title
        self._popup_time = popup_time
        
        if self._popup_time == None:
            self._popup_time = self.__class__.__default_popup_time
            
        self._status_stack = [] # list of current status objects
        self._dlg = None
    
    def _get_dlg(self):
        if self._dlg == None:
            self._dlg = self._dialog_class(self._dialog_class_params,
                                           self._title)
            
        self._dlg.show()
        
        return self._dlg
    
    def add_op(self, op_status):
        """Add a new status object to the progress dialog.
        
        @param op_status: the status object.        
        @type op_status: L{GrampsDb.LongOpStatus}
        """
        
        log.debug("adding op to Progress Monitor")
        facade = _StatusObjectFacade(op_status)
        self._status_stack.append(facade)
        idx = len(self._status_stack)-1
        
        # wrap up the op_status object idx into the callback calls
        def heartbeat_cb():
            self._heartbeat(idx)
        def end_cb():
            self._end(idx)
            
        facade.heartbeat_cb_id = op_status.connect('op-heartbeat', 
                                                   heartbeat_cb)
        facade.end_cb_id = op_status.connect('op-end', end_cb)
        
    def _heartbeat(self, idx):
        # check the estimated time to complete to see if we need
        # to pop up a progress dialog.
        
        log.debug("heartbeat in ProgressMonitor")
        
        facade = self._status_stack[idx]
        
        if facade.status_obj.estimated_secs_to_complete() > self._popup_time:
            facade.active = True
        
        if facade.active:
            dlg = self._get_dlg()
            
            if facade.pbar_idx == None:
                facade.pbar_idx = dlg.add(facade.status_obj)
                
            dlg.step(facade.pbar_idx)
            
    def _end(self, idx):
        # hide any progress dialog
        # remove the status object from the stack
        
        log.debug("received end in ProgressMonitor")
        facade = self._status_stack[idx]
        if facade.active:
            dlg = self._get_dlg()
        
            if len(self._status_stack) == 1:
                dlg.hide()
                
            dlg.remove(facade.pbar_idx)
            
        facade.status_obj.disconnect(facade.heartbeat_cb_id)
        facade.status_obj.disconnect(facade.end_cb_id)
        del self._status_stack[idx]
        
        
if __name__ == '__main__':
    import time
    from GrampsDb import LongOpStatus

    def test(a,b):
        d = ProgressDialog(_GtkProgressDialog, "Test Progress")
        
        s = LongOpStatus("Doing very long operation", 100, 10)
    
        d.add_op(s)
        
        for i in xrange(0, 99):
            time.sleep(0.1)
            if i == 30:
                t = LongOpStatus("doing a shorter one", 100, 10,
                                 can_cancel=True)
                d.add_op(t)
                for j in xrange(0, 99):
                    if t.should_cancel():
                        break
                    time.sleep(0.1)
                    t.heartbeat()
                t.end()
            if i == 60:
                t = LongOpStatus("doing another shorter one", 100, 10)
                d.add_op(t)
                for j in xrange(0, 99):
                    time.sleep(0.1)
                    t.heartbeat()
                t.end()
            s.heartbeat()
        s.end()
    
    w = gtk.Window(gtk.WINDOW_TOPLEVEL)
    w.connect('destroy', gtk.main_quit)
    button = gtk.Button("Test")
    button.connect("clicked", test, None)
    w.add(button)
    button.show()
    w.show()
    gtk.main()
    print 'done'
        