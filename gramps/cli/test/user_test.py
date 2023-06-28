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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

""" Unittest for user.py """

import unittest
from unittest.mock import Mock, patch
from .. import user
import sys

class TestUser:
    TITLE = "Testing prompt"
    MSG = "Choices are hard. Nevertheless, please choose!"
    ACCEPT = "To be"
    REJECT = "Not to be"

class TestUser_prompt(unittest.TestCase):
    def setUp(self):
        self.real_user = user.User()
        self.user = user.User()
        self.user._fileout = Mock(spec=sys.stderr)
        self.user._input = Mock(spec=input)

    def test_default_fileout_has_write(self):
        assert hasattr(self.real_user._fileout, 'write')

    def test_default_input(self):
        assert self.real_user._input.__name__.endswith('input')

    def test_prompt_returns_True_if_ACCEPT_entered(self):
        self.user._input.configure_mock(return_value = TestUser.ACCEPT)
        assert self.user.prompt(
                TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT
                ), "True expected!"
        self.user._input.assert_called_once_with()

    def test_prompt_returns_False_if_REJECT_entered(self):
        self.user._input.configure_mock(return_value = TestUser.REJECT)
        assert not self.user.prompt(
                TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT
                ), "False expected!"
        self.user._input.assert_called_once_with()

    def assert_prompt_contains_text(self, text,
            title=TestUser.TITLE, msg=TestUser.MSG,
            accept=TestUser.ACCEPT, reject=TestUser.REJECT):
        self.user._input.configure_mock(return_value = TestUser.REJECT)
        self.user.prompt(title, msg, accept, reject)
        for call in self.user._fileout.method_calls:
            name, args, kwargs = call
            for a in args:
                if a.find(text) >= 0:
                    return
        self.assertTrue(False,
                "'{}' never printed in prompt: {}".format(
                    text, self.user._fileout.method_calls))

    def test_prompt_contains_title_text(self):
        self.assert_prompt_contains_text(TestUser.TITLE)

    def test_prompt_contains_msg_text(self):
        self.assert_prompt_contains_text(TestUser.MSG)

    def test_prompt_contains_accept_text(self):
        self.assert_prompt_contains_text(TestUser.ACCEPT)

    def test_prompt_contains_reject_text(self):
        self.assert_prompt_contains_text(TestUser.REJECT)

    def test_prompt_strips_underscore_in_accept(self):
        self.assert_prompt_contains_text("accepT", accept="accep_T")

    def test_prompt_strips_underscore_in_reject(self):
        self.assert_prompt_contains_text("reJect", reject="re_Ject")

    def test_auto_accept_accepts_without_prompting(self):
        u = user.User(auto_accept=True)
        u._fileout = Mock(spec=sys.stderr)
        assert u.prompt(
                TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT
                ), "True expected!"
        assert len(u._fileout.method_calls) == 0, list(u._fileout.method_calls)

    def test_EOFError_in_prompt_caught_as_False(self):
        self.user._input.configure_mock(
                side_effect = EOFError,
                return_value = TestUser.REJECT)
        assert not self.user.prompt(
                TestUser.TITLE, TestUser.MSG, TestUser.ACCEPT, TestUser.REJECT
                ), "False expected!"
        self.user._input.assert_called_once_with()

class TestUser_quiet(unittest.TestCase):
    def setUp(self):
        self.user = user.User(quiet=True)
        self.user._fileout = Mock(spec=sys.stderr)

    def test_progress_can_begin_step_end(self):
        self.user.begin_progress("Foo", "Bar", 0)
        for i in range(10):
            self.user.step_progress()
        self.user.end_progress()

    def tearDown(self):
        assert len(self.user._fileout.method_calls
                ) == 0, list(self.user._fileout.method_calls)

class TestUser_progress(unittest.TestCase):

    def setUp(self):
        self.user = user.User()
        self.user._fileout = Mock(spec=sys.stderr)

    def test_can_step_using_with(self):
        # Collect baseline output from the old-style interface (begin/step/end)
        self._progress_begin_step_end()
        self.expected_output = list(self.user._fileout.method_calls)
        self.user._fileout.reset_mock()
        self.assertTrue(
                len(self.user._fileout.method_calls) == 0,
                list(self.user._fileout.method_calls))

        with self.user.progress("Foo", "Bar", 0) as step:
            for i in range(10):
                step()

        # Output using `with' differs from one with `progress_...'
        self.assertEqual(self.expected_output,
                list(self.user._fileout.method_calls))

    def test_ends_progress_upon_exception_in_with(self):
        with patch('gramps.cli.user.User.end_progress') as MockEP:
            try:
                with self.user.progress("Foo", "Bar", 0) as step:
                    raise Exception()
            except Exception:
                pass
        self.assertTrue(MockEP.called)

    def _progress_begin_step_end(self):
        self.user.begin_progress("Foo", "Bar", 0)
        for i in range(10):
            self.user.step_progress()
        self.user.end_progress()

if __name__ == "__main__":
    unittest.main()
