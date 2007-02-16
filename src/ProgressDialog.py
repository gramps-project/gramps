"""
This module provides a progess dialog for displaying the status of 
long running operations.
"""

import gtk

       
class _GtkProgressBar(object):
    """This is just a structure to hold the visual elements of a 
    progress indicator."""
    
    def __init__(self):
        self.pbar = None
        self.label = None
        self.pbar_max = 0
        self.pbar_index = 0.0
        self.old_val = -1
        
class _GtkProgressDialog(gtk.Dialog):
    """A gtk window to display the status of a long running
    process."""
    
    def __init__(self, title):
        gtk.Dialog.__init__(self)
        self.connect('delete_event', self.warn)
        self.set_has_separator(False)
        self.set_title(title)
        self.set_border_width(12)
        self.vbox.set_spacing(10)
        lbl = gtk.Label('<span size="larger" weight="bold">%s</span>' % title)
        lbl.set_use_markup(True)
        self.vbox.pack_start(lbl)
        #self.set_size_request(350,125)
        self.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.show_all()
        
        self._progress_bars = []
        
    def add(self,long_op_status):
        # Create a new progress bar
        pbar = _GtkProgressBar()
        pbar.lbl = gtk.Label(long_op_status.get_msg())
        pbar.lbl.set_use_markup(True)
        self.vbox.set_border_width(24)
        pbar.pbar = gtk.ProgressBar()
        
        self.vbox.pack_start(pbar.lbl, expand=False, fill=False)
        self.vbox.pack_start(pbar.pbar, expand=False, fill=False)
        if long_op_status.get_msg() == '':
            pbar.lbl.hide()
            
        pbar.pbar_max = (long_op_status.get_total_steps()/
                         long_op_status.get_interval())
        pbar.pbar_index = 0.0
        pbar.pbar.set_fraction((float(long_op_status.get_total_steps())/
                               (float(long_op_status.get_interval())))/
                               100.0)
        pbar.lbl.show()
        pbar.pbar.show()
        
        self.resize_children()
        self.process_events()
            
        self._progress_bars.append(pbar)
        return len(self._progress_bars)-1
    
    def remove(self, pbar_idx):
        pbar = self._progress_bars[pbar_idx]
        self.vbox.remove(pbar.pbar)
        self.vbox.remove(pbar.lbl)
        del self._progress_bars[pbar_idx]
        
    def step(self, pbar_idx):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%."""
        
        pbar = self._progress_bars[pbar_idx]
        
        pbar.pbar_index = pbar.pbar_index + 1.0
        
        if pbar.pbar_index > pbar.pbar_max:
            pbar.pbar_index = pbar.pbar_max

        try:
            val = int(100*pbar.pbar_index/pbar.pbar_max)
        except ZeroDivisionError:
            val = 0

        if val != pbar.old_val:
            pbar.pbar.set_text("%d%%" % val)
            pbar.pbar.set_fraction(val/100.0)
            pbar.old_val = val
            
        self.process_events()
            
    def process_events(self):
        while gtk.events_pending():
            gtk.main_iteration()

    def show(self):
        gtk.Dialog.show(self)
        self.process_events()
        
    def hide(self):
        gtk.Dialog.hide(self)
        self.process_events()
        
    def warn(self):
        return True
    
    def close(self):
        self.destroy()

class _StatusObjectFacade(object):
    """This provides a simple structure for recording the information
    needs about a status object."""
    
    def __init__(self, status_obj, heartbeat_cb_id=None, end_cb_id=None):
        self.status_obj = status_obj
        self.heartbeat_cb_id = heartbeat_cb_id
        self.end_cb_id = end_cb_id
        self.pbar_idx = None
        self.active = False
        
class ProgressDialog(object):
    """A dialog for displaying the status of long running operations.
    
    It will work with L{GrampsDb.LongOpStatus} objects to track the 
    progress of long running operations. If the operations is going to 
    take longer than I{popup_time} it will pop up a dialog with a 
    progress bar so that the user gets some feedback about what is 
    happening.
    """
    
    __default_popup_time = 5 # seconds
    
    def __init__(self, popup_time = None):
        self._popup_time = popup_time
        if self._popup_time == None:
            self._popup_time = self.__class__.__default_popup_time
            
        self._status_stack = [] # list of current status objects
        self._dlg = None
    
    def _get_dlg(self):
        if self._dlg == None:
            self._dlg = _GtkProgressDialog("Long running operation.")
            self._dlg.show()
        
        return self._dlg
    
    def add_op(self, op_status):
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
        d = ProgressDialog()
        
        s = LongOpStatus("Doing very long operation", 100, 10)
    
        d.add_op(s)
        
        for i in xrange(0, 99):
            time.sleep(0.1)
            if i == 30:
                t = LongOpStatus("doing a shorter one", 100, 10)
                d.add_op(t)
                for j in xrange(0, 99):
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
        