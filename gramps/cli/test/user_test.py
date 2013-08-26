# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Vassilii Khachaturov <vassilii@tarunz.org>
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

# $Id$

""" Unittest for user.py """

from __future__ import print_function

import unittest
from .. import user
from ...gen.test.user_test import TestUser
import sys

try:
    if sys.version_info < (3,3):
        from mock import Mock
    else:
        from unittest.mock import Mock

    MOCKING = True
    
except:
    MOCKING = False
    print ("Mocking disabled", sys.exc_info()[0:2])

class TestUser_prompt(unittest.TestCase):
    def setUp(self):
        self.real_user = user.User()
        if MOCKING:
            self.user = user.User()
            self.user._fileout = Mock()
            self.user._input = Mock()

    def test_default_fileout_has_write(self):
        assert hasattr(self.real_user._fileout, 'write')

    def test_default_input(self):
        assert self.real_user._input.__name__.endswith('input')

    @unittest.skipUnless(MOCKING, "Requires unittest.mock to run")
    def test_prompt_returns_True_if_ACCEPT_entered(self):
        self.user._input.configure_mock(return_value = TestUser.ACCEPT)
        assert self.user.prompt(
                TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT
                ), "True expected!"
        self.user._input.assert_called_once_with()

    @unittest.skipUnless(MOCKING, "Requires unittest.mock to run")
    def test_prompt_returns_False_if_REJECT_entered(self):
        self.user._input.configure_mock(return_value = TestUser.REJECT)
        assert not self.user.prompt(
                TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT
                ), "False expected!"
        self.user._input.assert_called_once_with()

    def assert_prompt_contains_text(self, text):
        self.user._input.configure_mock(return_value = TestUser.REJECT)
        self.user.prompt(TestUser.TITLE, TestUser.MSG, 
                TestUser.ACCEPT, TestUser.REJECT)
        for call in self.user._fileout.method_calls:
            name, args, kwargs = call
            for a in args:
                if a.find(text) >= 0:
                    return
        assert False,"'{}' never printed in prompt".format(text)

    @unittest.skipUnless(MOCKING, "Requires unittest.mock to run")
    def test_prompt_contains_title_text(self):
        self.assert_prompt_contains_text(TestUser.TITLE)

    @unittest.skipUnless(MOCKING, "Requires unittest.mock to run")
    def test_prompt_contains_msg_text(self):
        self.assert_prompt_contains_text(TestUser.MSG)

    @unittest.skipUnless(MOCKING, "Requires unittest.mock to run")
    def test_prompt_contains_accept_text(self):
        self.assert_prompt_contains_text(TestUser.ACCEPT)

    @unittest.skipUnless(MOCKING, "Requires unittest.mock to run")
    def test_prompt_contains_reject_text(self):
        self.assert_prompt_contains_text(TestUser.REJECT)

    if not MOCKING: #don't use SKIP, to avoid counting a skipped test
        def testManualRun(self):
            b = self.real_user.prompt(
                    TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT)
            print ("Returned: {}".format(b))

if __name__ == "__main__":
    unittest.main()
