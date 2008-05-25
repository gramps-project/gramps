import unittest

from test import test_util as tu
tu.path_append_parent()

from gen.utils import Callback

try:
    log
except NameError:
    log = None


class TestCallback(unittest.TestCase):

    def test_simple(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-signal' : (int,)
                        }

        rl = []
        def fn(i,r=rl):
            rl.append(i)

        t = TestSignals()
        t.connect('test-signal',fn)
        t.emit('test-signal',(1,))

        
        assert len(rl) == 1, "No signal emitted"
        assert rl[0] == 1, "Wrong argument recieved"


    def test_exception_catch(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-signal' : (int,)
                        }

        rl = []
        def fn(i,r=rl):
            rl.append(i)

        def borked(i):
            """
            this intentionally raises a NameError exception
            FIXME: could use an explanation
              or perhaps some explicit Try/Except code
            """
            rubish.append(i)

        t = TestSignals()

        def null(s):
            pass

        
        global log
        _log = log
        log = null
        
        t.connect('test-signal',borked)
        t.connect('test-signal',fn)
        t.emit('test-signal',(1,))
        log = _log
        
        assert len(rl) == 1, "No signal emitted"
        assert rl[0] == 1, "Wrong argument recieved"

    def test_disconnect(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-signal' : (int,)
                        }

        rl = []
        def fn(i,r=rl):
            rl.append(i)

        t = TestSignals()
        key = t.connect('test-signal',fn)
        t.emit('test-signal',(1,))

        
        assert len(rl) == 1, "No signal emitted"
        assert rl[0] == 1, "Wrong argument recieved"

        t.disconnect(key)

        t.emit('test-signal',(1,))
            
        assert len(rl) == 1, "Callback not disconnected"
        assert rl[0] == 1, "Callback not disconnected"

    def test_noargs(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-noargs' : None
                        }

        rl = []
        def fn(r=rl):
            rl.append(1)

        t = TestSignals()
        t.connect('test-noargs',fn)
        t.emit('test-noargs')

        
        assert len(rl) == 1, "No signal emitted"
        assert rl[0] == 1, "Wrong argument recieved"

    def test_no_callback(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-noargs' : None
                        }

        t = TestSignals()
        t.emit('test-noargs')

    def test_subclassing(self):

        class TestSignals(Callback):
            __signals__ = {
                        'test-signal' : (int,)
                        }
            
        class TestSignalsSubclass(TestSignals):
            __signals__ = {
                        'test-sub-signal' : (int,),
                        }

        rl = []
        def fn(i,r=rl):
            rl.append(i)

        t = TestSignalsSubclass()
        t.connect('test-signal',fn)
        t.emit('test-signal',(1,))
            
        assert len(rl) == 1, "No signal emitted"
        assert rl[0] == 1, "Wrong argument recieved"

        t.connect('test-sub-signal',fn)
        t.emit('test-sub-signal',(1,))
            
        assert len(rl) == 2, "No subclass signal emitted"
        assert rl[1] == 1, "Wrong argument recieved in subclass"

    def test_signal_block(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-signal' : (int,)
                        }

        rl = []
        def fn(i,r=rl):
            rl.append(i)

        t = TestSignals()
        t.connect('test-signal',fn)
        t.emit('test-signal',(1,))    
        
        assert len(rl) == 1, "No signal emitted"
        assert rl[0] == 1, "Wrong argument recieved"

        Callback.disable_all_signals()
        t.emit('test-signal',(1,))    
        assert len(rl) == 1, "Signal emitted while class blocked"

        Callback.enable_all_signals()
        t.emit('test-signal',(1,))    
        assert len(rl) == 2, "Signals not class unblocked"

        t.disable_signals()
        t.emit('test-signal',(1,))    
        assert len(rl) == 2, "Signal emitted while instance blocked"

        t.enable_signals()
        t.emit('test-signal',(1,))    
        assert len(rl) == 3, "Signals not instance unblocked"

    def test_type_checking(self):

        class TestSignals(Callback):
            __signals__ = {
                        'test-int' : (int,),
                        'test-list': (list,),
                        'test-object': (object,),
                        'test-str': (str,),
                        'test-float': (float,),
                        'test-dict': (dict,),
                        'test-lots': (int,str,list, object,float)
                        }

        rl = []
        def fn(i,r=rl):
            rl.append(i)

        t = TestSignals()
        t.connect('test-int',fn), t.emit('test-int',(1,))
        assert isinstance(rl[0], int), "not int"

        t.connect('test-list',fn), t.emit('test-list',([1,2],))
        assert isinstance(rl[1], list), "not list"

        t.connect('test-object',fn), t.emit('test-object',(t,))
        assert isinstance(rl[2], object), "not object"

        t.connect('test-float',fn), t.emit('test-float',(2.3,))
        assert isinstance(rl[3], float), "not float"

        t.connect('test-dict',fn), t.emit('test-dict',({1:2},))
        assert isinstance(rl[4], dict), "not dict"

        rl = []
        def fn2(i,s,l, o,f,r=rl):
            rl.append(i)

        t.connect('test-lots',fn2), t.emit('test-lots',(1,'a',[1,2],t,1.2))
        assert isinstance(rl[0], int), "not lots"

        # This should fail because the type of arg1 is wrong
        res=[]
        def fn3(s,r=res):
            res.append(s)
        t._warn = fn3
        t.connect('test-lots',fn2), t.emit('test-lots',('a','a',[1,2],t,1.2))
        assert res[0][0:6] == "Signal", "Type error not detected"

    def test_recursion_block(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-recursion' : (Callback,)
                        }

        def fn(cb):
            cb.emit('test-recursion',(t,))

        res=[]
        def fn2(s,r=res):
            res.append(s)

        t = TestSignals()
        t._warn = fn2
        t.connect('test-recursion',fn)

        try:
            t.emit('test-recursion',(t,))
        except RuntimeError:
            assert False, "signal recursion not blocked1."

        assert res[0][0:6] == "Signal", "signal recursion not blocked"


    def test_multisignal_recursion_block(self):

        class TestSignals(Callback):

            __signals__ = {
                        'test-top' : (Callback,),
                        'test-middle' : (Callback,),
                        'test-bottom' : (Callback,)
                        }

        def top(cb):
            cb.emit('test-middle',(t,))
        def middle(cb):
            cb.emit('test-bottom',(t,))
        def bottom(cb):
            cb.emit('test-top',(t,))

        res=[]
        def fn2(s,r=res):
            res.append(s)

        t = TestSignals()
        t._warn = fn2
        t.connect('test-top',top)
        t.connect('test-middle',middle)
        t.connect('test-bottom',bottom)

        try:
            t.emit('test-top',(t,))
        except RuntimeError:
            assert False, "multisignal recursion not blocked1."

        assert res[0][0:6] == "Signal", "multisignal recursion not blocked"

if __name__ == "__main__":
    unittest.main()

