GoatGramps Changes
==================

This file lists the features in the `goatgramps/gg_beta` branch that are
**not** in Gramps `master`. It is maintained by hand and is the authoritative
answer to "what makes this fork different?".

The per-commit history is not useful for this purpose: the development
history contains work-in-progress commits (`Reverted last change`,
`Attempt 1 for pipeline fix`, `First trial, non-working`), so features are
grouped here by *what they do* rather than by commit.

Do **not** record these changes in `NEWS`. That file is generated from commit
messages by scripts and is overwritten by upstream on nearly every rebase
(upstream has modified it 166 times).


User-visible features
---------------------

* **Thumbnails in chart reports.** The ancestor, descendant and pedigree
  charts can render a small portrait for each person. Portraits are scaled to
  fit a fixed box rather than being placed at their native size, and an
  optional mask (SVG) can be applied to give them a rounded or oval shape.
  See the *Thumbnails* section of the report options.

* **Age at death and marriage duration in tree charts.** The descendant and
  ancestor charts show `d. 1975 (age 75)` beside a deceased person, and how
  long each marriage lasted (`m. 1925  (50 yrs)`). The marriage span is shown
  for every union that has ended, including the second and later marriages of
  a remarried partner. Both are controlled by a *Show age* option, which
  defaults to off and can be reverted to the old behaviour in Configure.

* **Instant chart updates.** Chart and report option boxes now apply their
  changes immediately instead of waiting for the dialog to close. A Configure
  option is provided to retain the previous on-close behaviour, and newlines
  are prevented from being entered into the boxes.

* **LDS-style GEDCOM extensions.** `libgedcom.py` parses a set of extra tags
  used by some third-party GEDCOM producers, including `_PREF`, `_PAREN`,
  `_ITALIC`, `_NAME`, `_PLAC_DEFN`, `_EVENT_DEFN` and the related definition
  record tags. Test data files exercising these tags are included.

* **GEDCOM import warnings.** Warnings for suppressed or unrecognised tags
  are reported once per distinct tag rather than once per occurrence, the
  message width has been adjusted, and all "ignored" flags are handled the
  same way. Several legacy import errors that previously aborted an import
  are now ignored, and the "Line ignored" message carries the line number.

* **FamilySearch fixes.** Persist FamilySearch ID links independently of the
  editor, avoid committing live editor edits, and fix the live-person Compare
  bug and the Open Person in FamilySearch button enable/disable state.
  *Merged from contributor dsblank (PR #2475).*


Build and packaging
-------------------

* **Windows AIO build fixed.** The NSIS script now reserves its Unicode
  plugin DLLs from `Plugins\amd64-unicode` instead of `Plugins\unicode`.
  Recent NSIS releases stopped installing them to the old path, which caused
  the build to abort. This matches the fix on the upstream `aio-test` branch.

* **`create_env.bash`** at the repository root sets up a development
  environment.

* **Python packaging.** bsddb files are included in the AIO build again, and
  a pure-Python PyPI wheel installer replaces the previous pip invocation.


Tests and continuous integration
--------------------------------

* **Draw report tests.** A new `displayage_test.py` in
  `gramps/plugins/drawreport/test/` covers the age and marriage-span
  formatting. It builds a family tree in an in-memory SQLite database and
  renders both charts to disk, asserting on the resulting SVG.

  The accompanying `test/__init__.py` is required: without it
  `unittest discover` skips the directory entirely and the tests never run.

* **CI test artifacts.** The Gramps CI workflow uploads
  `test/data/tree_report_age_output/` as a `test-generated-data` artifact for
  14 days, so the generated charts can be downloaded and inspected after a
  run. The upload step uses `if: always()`, so the artifact is produced even
  when the suite fails.


Other fixes
-----------

* **XML export no longer leaks a file handle.** `GrampsXmlWriter.write()` and
  `write_handle()` closed their output file only on the success path, so an
  exception mid-write left the file open. On Windows this prevented the file
  from being deleted. Both now use `try/finally`. This is a latent upstream
  bug and is a candidate for an upstream contribution.


Tracking conventions
--------------------

* Each feature gets one bullet. Say what the user can now do, not which
  function changed.
* Add the bullet when the feature is merged, not while it is in progress.
* If a feature is reverted from this branch, delete its bullet.
* Commit messages on this branch must still follow the AGENTS.md format,
  because the CommitLog generation scripts parse them.
