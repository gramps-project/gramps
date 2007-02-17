"""
This module provides a progess dialog for displaying the status of 
long running operations.
"""

import gtk
       
class _GtkProgressBar(gtk.VBox):
    """This widget displays the progress bar and labels for a progress
    indicator. It provides an interface to updating the progress bar.
    """
    
    def __init__(self, long_op_status):
        """@param long_op_status: the status of the operation.
           @type long_op_status: L{GrampsDb.LongOpStatus}
        """
        gtk.VBox.__init__(self)
        
        msg = long_op_status.get_msg()
        self._old_val = -1
        self._lbl = gtk.Label(msg)
        self._lbl.set_use_markup(True)
        #self.set_border_width(24)
        
        self._pbar = gtk.ProgressBar()
        self._hbox = gtk.HBox()
        
        # Only display the cancel button is the operation
        # can be canceled.
        if long_op_status.can_cancel():
            self._cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
            self._cancel.connect("clicked", 
                                 lambda x: long_op_status.cancel())
            self._cancel.show()
            self._hbox.pack_end(self._cancel)
        
        self._hbox.pack_start(self._pbar)
        
        self.pack_start(self._lbl, expand=False, fill=False)
        self.pack_start(self._hbox, expand=False, fill=False)
        
            
        self._pbar_max = (long_op_status.get_total_steps()/
                         long_op_status.get_interval())
        self._pbar_index = 0.0
        self._pbar.set_fraction(((100/float(long_op_status.get_total_steps())*
                                 float(long_op_status.get_interval())))/
                                 100.0)
        
        if msg != '':
            self._lbl.show()
        self._pbar.show()
        self._hbox.show()

    def step(self):
        """Move the progress bar on a step.
        """
        self._pbar_index = self._pbar_index + 1.0
        
        if self._pbar_index > self._pbar_max:
            self._pbar_index = self._pbar_max

        try:
            val = int(100*self._pbar_index/self._pbar_max)
        except ZeroDivisionError:
            val = 0

        if val != self._old_val:
            self._pbar.set_text("%d%%" % val)
            self._pbar.set_fraction(val/100.0)
            self._pbar.old_val = val
        
class GtkProgressDialog(gtk.Dialog):
    """A gtk window to display the status of a long running
    process."""
    
    def __init__(self, window_params, title):
        """@param title: The title to display on the top of the window.
           @type title: string
        """
        gtk.Dialog.__init__(self, *window_params)
        self.connect('delete_event', self._warn)
        self.set_has_separator(False)
        self.set_title(title)
        #self.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        #self.show()
        
        self._progress_bars = []
        
    def add(self,long_op_status):
        """Add a new status object to the progress dialog.
        
        @param long_op_status: the status object.        
        @type long_op_status: L{GrampsDb.LongOpStatus}
        @return: a key that can be used as the L{pbar_idx} 
                 to the other methods.
        @rtype: int
        """
        pbar = _GtkProgressBar(long_op_status)
        
        self.vbox.pack_start(pbar, expand=False, fill=False)
        
        pbar.show()
        
        self.resize_children()
        self._process_events()
            
        self._progress_bars.append(pbar)
        return len(self._progress_bars)-1
    
    def remove(self, pbar_idx):
        """Remove the specified status object from the progress dialog.
        
        @param pbar_idx: the index as returned from L{add}
        @type pbar_idx: int
        """
        pbar = self._progress_bars[pbar_idx]
        self.vbox.remove(pbar)
        del self._progress_bars[pbar_idx]
        
    def step(self, pbar_idx):
        """Click the progress bar over to the next value.  Be paranoid
        and insure that it doesn't go over 100%.
                
        @param pbar_idx: the index as returned from L{add}
        @type pbar_idx: int
        """
        
        self._progress_bars[pbar_idx].step()            
        self._process_events()
            
    def _process_events(self):
        while gtk.events_pending():
            gtk.main_iteration()

    def show(self):
        """Show the dialog and process any events.
        """
        gtk.Dialog.show(self)
        self._process_events()
        
    def hide(self):
        """Hide the dialog and process any events.
        """
        gtk.Dialog.hide(self)
        self._process_events()
        
    def _warn(self,x,y):
        return True
    
    def close(self):
        self.destroy()
        
if __name__ == '__main__':
    import time
    from GrampsDb import LongOpStatus, ProgressMonitor

    def test(a,b):
        d = ProgressMonitor(GtkProgressDialog)
        
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
        