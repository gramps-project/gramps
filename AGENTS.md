# Agent Guidelines for Gramps

This document specifies rules and conventions that agents should follow when making changes to the Gramps codebase.

## Code Style & Formatting

### Black

All changed Python files must be formatted with [Black](https://black.readthedocs.io/) before committing. CI enforces this on every PR. Run:

```bash
git diff --name-only --diff-filter=ACMR origin/master...HEAD | grep '\.py$' | xargs --no-run-if-empty black
```

### Type Hints

All functions and methods must have type hints using Python 3.10+ syntax:

- Use `X | None` instead of `Optional[X]`
- Use `X | Y` instead of `Union[X, Y]`
- Use `list[X]`, `dict[K, V]`, `tuple[X, ...]` instead of `List`, `Dict`, `Tuple` from `typing`
+ Use handle types from `gramps/gen/types.py` (e.g., `PersonHandle`, `FamilyHandle`) rather than bare `str` for handles
+ Use Gramps ID types from `gramps/gen/types.py` (e.g., `PersonGrampsID`, `FamilyGrampsID`) rather than bare `str` for gramps_id

### Docstrings

All functions and methods must have docstrings using Sphinx format:

```python
def get_person_from_gramps_id(self, gramps_id: PersonGrampsID) -> Person | None:
    """
    Return a Person from the database using the given gramps ID.

    :param gramps_id: The gramps ID of the Person to retrieve.
    :type gramps_id: PersonGrampsID
    :returns: The Person object, or ``None`` if not found.
    :rtype: :py:class:`Person`
    """
```

### Import Grouping

Imports must be organized into three sections, each separated by a blank line and preceded by a comment header:

```python
# ------------------------
# Python modules
# ------------------------
import os
import logging

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.db.base import DbReadBase

# ------------------------
# Gramps specific
# ------------------------
from .mymodule import MyClass
```

### PEP 8 and Indentation

Code should be PEP 8 compatible, except where that conflicts with Black formatting. Black takes precedence. Use 4 spaces for indentation — never TABs.

### Pylint

Run pylint on new code. Ideally new code should score 9 or higher and changes should not reduce the overall pylint score. This is not strictly enforced and should never come at the expense of code clarity, Black formatting, or any other rule in this guide.

### Class Headers

Each class must have a simple header comment to help locate it when multiple classes exist in the same file. This is for navigation, not documentation:

```python
#------------------------------------------------------------
#
# MyClass
#
#------------------------------------------------------------
class MyClass:
    ...
```

### Callbacks

Callback function names must be prefixed with `cb_`. For example: `cb_my_callback`.

### Logging

Use module-level loggers; do not use `print()` for diagnostic output:

```python
import logging
LOG = logging.getLogger(__name__)
```

### Internationalization

All user-visible strings must be wrapped with `_()` for translation support:

```python
raise ValueError(_("Invalid handle: %s") % handle)
```
The alias `_(string , context)` is preferred to `pgettext(context, message)`.
Use `ngettext(singular, plural, n)` for plural forms.
## Submodule Import Rules

Files in the `gen` submodule must not import from any other Gramps submodule (e.g., `gui`, `plugins`). The `gen` submodule must remain self-contained.

## File Headers

Every new `.py` file must include a GPL-2.0-or-later license header with copyright:

```python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) <YEAR>  <Author Name>
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
```

## Testing

### Requirements

- Write tests for each distinct flow of logic (happy path, error cases, edge cases).
- Tests must use the `unittest` framework — do not use `pytest`.
- Test files must be named with the `_test.py` suffix (e.g., `mymodule_test.py`). CI discovers tests using `*_test.py`.
- Place test files in a `test/` subdirectory alongside the module being tested.

### Running Tests

```bash
GRAMPS_RESOURCES=. python3 -m unittest discover -p "*_test.py"
```

### Type Checking

Changes must pass mypy static analysis:

```bash
mypy
```

Note: `*.gpr.py` plugin registration files are excluded from mypy checks.

## Commit Messages

Commit messages are parsed by scripts that update Mantis BT and generate
ChangeLog and News files, so formatting must be followed precisely.

- The first line is a short summary of the change — maximum 70 characters.
- All other lines must be wrapped at 80 characters.
- Describe how the change affects functionality from the user's perspective.
- Use complete sentences when possible.
- To reference another commit, use the full commit hash (not a short hash).
- The last line must link to or resolve a bug report using the Mantis BT
  integration keywords. Example:

```
Fix crash when opening event editor with empty date field.

When a date field was left blank, the event editor raised an unhandled
AttributeError. This change adds a guard so the field is treated as an
empty string instead.

Fixes #12345.
```

To mark a bug as fixed use the Mantis BT special keywords `Fixes`, `Fixed`, `Resolves` or `Resolved` followed by a `#` and then the bug number without leading zeros. e.g. `Fixes #12345.`.
To reference an issue the keywords `Bug`, `Bugs`, `Issue`, `Issues`, `Report` or `Reports` may be used with a bug number in the same format for bugs. e.g. `Issue #12345`.
Multiple issues may be referenced. e.g. `Resolves #12345, #12346.` 
These references should be used in the last line of a commit message.

## Translation Files

When adding or removing Python source files, update the translation file
lists accordingly:

- `po/POTFILES.in` — list of files that contain translatable strings.
- `po/POTFILES.skip` — list of files that intentionally have no translatable
  strings and should be excluded from translation checks.

## Error Handling

- Prefer existing exceptions from `gramps/gen/errors.py` and `gramps/gen/db/exceptions.py` over creating new ones.
- Only introduce a new exception class when none of the existing ones accurately represent the error condition.
- Raise `HandleError` for invalid or missing handles.
## Branch merges

Branch merges are not allowed in pull requests.  Rebase rather than merging.
