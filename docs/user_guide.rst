User Guide
==========

Please consult the manual which you find on `our wiki <https://gramps-project.org/wiki/index.php?title=User_manual>`_\ .

Package and import handling
--------------------------

When I export a native Gramps package, included media receives portable names
inside its ``media`` directory. This also works for media stored outside my
configured base directory. My source records and original files retain their
paths. Missing native-package media retains a reference to its original
location.

When I import a package, unsafe paths, symbolic links and special files are
rejected before its contents are written. Older package hard links to earlier
regular members are imported as independent file copies. Included media is
linked to the extracted files, preserving my tree's existing media base and
unrelated media links. If I have a package containing symbolic links, I
recreate it using this version's native exporter, which stores the linked
media contents.

On the development branch, unfiltered native packages also preserve DNA-test
and DNA-match records. Filtered exports of trees containing DNA records stop
with an error while native DNA filtering remains unsupported. My previous
package is retained.

Malformed vCard properties, cyclic Pro-Gen memo records and missing Pro-Gen
definitions no longer leave these import operations in an endless loop. XML
progress estimation uses bounded reads; unusually large input can be imported
without an advance line-count estimate.
