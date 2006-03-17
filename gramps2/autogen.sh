#!/bin/sh
# Run this to generate all the initial makefiles, etc.
# shamelessly borrowed from the Galeon source distribution

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME="gramps"

(test -f $srcdir/configure.in \
  && test -f $srcdir/src/gramps_main.py) || {
    echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
    echo " top-level $PKG_NAME directory"
    exit 1
}

which gnome-autogen.sh || {
    echo "You need to install gnome-common package."
    exit 1
}
REQUIRED_AUTOMAKE_VERSION=1.6 USE_GNOME2_MACROS=1 . gnome-autogen.sh
