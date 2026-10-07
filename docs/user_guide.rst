User Guide
==========

Please consult the manual which you find on `our wiki <https://gramps-project.org/wiki/index.php?title=User_manual>`_\ .

Portable GEDCOM exports
----------------------

When I export to GEDCOM, I receive my ``.ged`` file and a new
``gramps-gedcom-...`` companion folder in the same directory. I keep these
together when moving or sharing my export. The GEDCOM uses relative links to
copies of my selected media files in that folder; my original media files and
family tree stay unchanged.

The companion folder also contains ``restore.gpkg``, a native Gramps package
with my selected records and their media. I import this package into Gramps
when I need to restore details that GEDCOM cannot represent, including tags,
custom attributes and media crop rectangles. Other genealogy applications may
not support these native details. My privacy, living-person and selection
filters apply to both the GEDCOM and its recovery package.

An export fails if a selected media file is missing, unreadable, changes during
copying or is only a remote URL. I store remote media locally and correct
missing links before exporting. A failed export leaves my previous GEDCOM
intact. Each successful export uses a new companion folder, so previous media
copies are preserved. This requires space for both the portable media copies
and the native recovery package.

My recovery package preserves the exported family-tree data; it does not back
up my application preferences, installed add-ons or undo history.

On the development branch, unfiltered native recovery also preserves DNA-test
and DNA-match records. Filtered exports of trees containing DNA records stop
with an error while native DNA filtering remains unsupported. My previous
export is retained.
