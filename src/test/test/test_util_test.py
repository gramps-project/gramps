"""unittest (test_util_test.py) for test_util.py"""

import sys
import os
import tempfile
import unittest as U

usage_note="""
  **************************************************************
  Testing (and runing) Gramps requires that PYTHONPATH include
  the path to the top Gramps directory (where gramps.py resides).

  For example, in bash, a shell export would look like 
    export PYTHONPATH=/.../src
  with the ... filled in appropriately.
  **************************************************************
"""

# **************************************************************
#
# Since this module is used by other test modules, it is
# strongly advised to test this module to 100% coverage,
# and in all calling variations, eg:
#  run directly, from this dir with and without ./ prefix
#  run from other dirs (with path prefix) 
#  run from within regrtest.py 
#  run from regrtest.py with other test modules present
#    which use the test_util module itself
#
# **************************************************************

try:
    from test import test_util as tu
    ##here = tu.absdir()
except ImportError:
    print "Cannot import 'test_util'from package 'test'" + usage_note
    exit(1) 


# grouping into multiple TestCases (classes) is not required,
# but may be useful for various reasons, such as collecting 
# tests that share a setUp/tearDown mechanism or that share 
# some test data, or just because they're related.
#
# The test function name should not have docstrings, but should
# have names which add to the value of failure reporting, and 
# which make it easy to find them within the source.


# some enabling infrastructure features
class Test1(U.TestCase):
    def test1a_custom_exception(s):
        tmsg = "testing"
        try:
            err = None
            raise tu.TestError(tmsg)
        except tu.TestError,e:
            emsg = e.value
        s.assertEqual(emsg, tmsg,
            "raising TestError: g=%r e=%r" % (emsg, tmsg))

    def test1b_msg_reporting_utility(s):
        g,e = "got this", "expected that"
        m,p = "your message here", "pfx"
        tmsg0 = m + "\n .....got:'" + g + \
            "'\n expected:'" + e +"'"
        tmsg1 = p + ": " + tmsg0
        s.assertEqual(tu.msg(g,e,m), tmsg0, "non-prefix message")
        s.assertEqual(tu.msg(g,e,m,p), tmsg1, "prefix message")


# path-related features (note use of tu.msg tested above)
class Test2(U.TestCase):
    def test2a_context_via_traceback(s):
        e = __file__.rstrip(".co")   # eg in *.py[co]
        g = tu._caller_context()[0]
        g.rstrip('c')
        s.assertEqual(g,e, tu.msg(g,e, "_caller_context"))
  
    def test2b_absdir(s):
        here = tu.absdir();
        g=tu.absdir(__file__)
        s.assertEqual(g,here, tu.msg(g,here, "absdir"))
  
    def test2c_path_append_parent(s):
        here = tu.absdir();
        par = os.path.dirname(here)
        was_there = par in sys.path
        if was_there:
            while par in sys.path:
                sys.path.remove(par)
        np = len(sys.path)
        
        for p in (None, __file__):
            s.assertFalse(par in sys.path, "par not in initial path")
            if not p:
                g = tu.path_append_parent()
            else:
                g = tu.path_append_parent(p)
            s.assertEqual(g,par, tu.msg(g,par, "path_append_parent return"))
            s.assertTrue(par in sys.path, "actually appends")
            sys.path.remove(par)
            l= len(sys.path)
            s.assertEqual(l,np, tu.msg(l,np,"numpaths"))
        if was_there:
            # restore entry state (but no multiples needed!)
            sys.path.append(par)

# make and remove test dirs
class Test3(U.TestCase):
    here = tu.absdir()
    bases = (here, tempfile.gettempdir())
    asubs = map(lambda b: os.path.join(b,"test_sub"), bases)
    home= os.environ["HOME"]
    if home:
        home_junk = os.path.join(home,"test_junk")
    def _rmsubs(s):
        import shutil
        for sub in s.asubs:
            if os.path.isdir(sub):
                shutil.rmtree(sub)
  
    def setUp(s):
        s._rmsubs()
        if s.home and not os.path.isdir(s.home_junk):
            os.mkdir(s.home_junk)

    def tearDown(s):
        s._rmsubs()
        if s.home and os.path.isdir(s.home_junk):
            os.rmdir(s.home_junk)

    def test3a_subdir(s):
        for sub in s.asubs:
            s.assertFalse(os.path.isdir(sub), "init: no dir %r" % sub)
            b,d = os.path.dirname(sub), os.path.basename(sub)
            md = tu.make_subdir(d, b)
            s.assertTrue(os.path.isdir(sub), "made dir %r" % sub)
            s.assertEqual(md,sub, tu.msg(md,sub, 
                "make_subdir returns path"))

            s2 = os.path.join(sub,"sub2")
            tu.make_subdir("sub2", sub)
            s.assertTrue(os.path.isdir(s2), "made dir %r" % s2)
            f = os.path.join(s2,"test_file")

            open(f,"w").write("testing..")
            s.assertTrue(os.path.isfile(f), "file %r exists" % f)
            tu.delete_tree(sub)
            s.assertFalse(os.path.isdir(sub), 
                "delete_tree removes subdir %r" % sub )

    def test3b_delete_tree_constraint(s):
        if s.home:
            err = None
            try:
                tu.delete_tree(s.home_junk)
            except tu.TestError, e:
                err = e.value
            s.assertFalse(err is None, 
                "deltree on %r raises TestError" % (s.home_junk))
        else:
            s.fail("Skip deltree constraint test, no '$HOME' var")

if __name__ == "__main__":
    U.main()
#===eof===
