#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gabriel Rios
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
"""Tests for cleanup after FamilySearch import failures."""

# ------------------------
# Python modules
# ------------------------
import ast
import logging
from pathlib import Path
from typing import Any
import unittest
from unittest.mock import MagicMock


# ------------------------------------------------------------
#
# ImportCleanupTest
#
# ------------------------------------------------------------
class ImportCleanupTest(unittest.TestCase):
    """Check transaction ownership and progress cleanup."""

    def setUp(self) -> None:
        """Load the import entry point with isolated interface dependencies."""
        filename = (
            Path(__file__).resolve().parents[1] / "fs" / "fs_import" / "importer.py"
        )
        self.progress = MagicMock()
        self.warning = MagicMock()
        namespace: dict[str, Any] = {
            "Any": Any,
            "_": lambda text: text,
            "ProgressMeter": MagicMock(return_value=self.progress),
            "WarningDialog": self.warning,
            "LOG": logging.getLogger(__name__),
        }
        source = ast.parse(filename.read_text(encoding="utf-8"))
        importer_class = next(
            node
            for node in source.body
            if isinstance(node, ast.ClassDef) and node.name == "FSToGrampsImporter"
        )
        method = next(
            node
            for node in importer_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "import_tree"
        )
        module = ast.Module(body=[method], type_ignores=[])
        exec(compile(module, str(filename), "exec"), namespace)
        self.import_tree = namespace["import_tree"]
        self.importer = MagicMock()
        self.importer.refresh_signals = True
        self.caller = MagicMock()
        self.caller.dbstate.db.transaction = None

    def cb_fail_import(self, _caller: Any, _fsid: str, _progress: Any) -> None:
        """
        Fail after opening the import's own transaction.

        :param _caller: The caller containing database and UI state.
        :param _fsid: The starting FamilySearch person ID.
        :param _progress: The progress dialog.
        """
        self.importer.txn = "import-transaction"
        raise ValueError("place resolution failed")

    def test_failure_rolls_back_and_restores_interface(self) -> None:
        """Import errors roll back owned work and close the progress dialog."""
        self.importer._import_tree.side_effect = self.cb_fail_import
        with self.assertLogs(__name__, level="ERROR"):
            with self.assertRaises(ValueError):
                self.import_tree(self.importer, self.caller, "ABCD-EFG")
        self.caller.dbstate.db.transaction_abort.assert_called_once_with(
            "import-transaction"
        )
        self.caller.dbstate.db.enable_signals.assert_called_once()
        self.caller.uistate.set_busy_cursor.assert_called_with(False)
        self.progress.close.assert_called_once()
        self.warning.assert_called_once()
        self.assertIsNone(self.importer.txn)
