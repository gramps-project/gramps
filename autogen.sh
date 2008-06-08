#!/bin/sh
# Run this to generate all the initial makefiles, etc.
# $Id$

PKG_NAME="gramps"
srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.
srcfile=$srcdir/src/gramps_main.py

REQUIRED_AUTOMAKE_VERSION=1.9
DIE=0

# source helper functions
if test ! -f gramps-autogen.sh;
then
  echo There is something wrong with your source tree.
  echo You are missing gramps-autogen.sh
  exit 1
fi
. gramps-autogen.sh

CONFIGURE_DEF_OPT='--enable-maintainer-mode'

autogen_options $@

#echo -n "+ check for build tools"
#if test ! -z "$NOCHECK"; then echo ": skipped version checks"; else  echo; fi

#tell Mandrake autoconf wrapper we want autoconf 2.5x, not 2.13
WANT_AUTOCONF_2_5=1
export WANT_AUTOCONF_2_5
version_check autoconf AUTOCONF 'autoconf2.50 autoconf autoconf-2.53' $REQUIRED_AUTOCONF_VERSION \
    "http://ftp.gnu.org/pub/gnu/autoconf/autoconf-$REQUIRED_AUTOCONF_VERSION.tar.gz" || DIE=1
AUTOHEADER=`echo $AUTOCONF | sed s/autoconf/autoheader/`

automake_progs="automake automake-1.10 automake-1.9"
version_check automake AUTOMAKE "$automake_progs" $REQUIRED_AUTOMAKE_VERSION \
    "http://ftp.gnu.org/pub/gnu/automake/automake-$REQUIRED_AUTOMAKE_VERSION.tar.gz" || DIE=1
ACLOCAL=`echo $AUTOMAKE | sed s/automake/aclocal/`

version_check glib-gettext GLIB_GETTEXTIZE glib-gettextize $REQUIRED_GLIB_GETTEXT_VERSION \
    "ftp://ftp.gtk.org/pub/gtk/v2.2/glib-$REQUIRED_GLIB_GETTEXT_VERSION.tar.gz" || DIE=1
require_m4macro glib-gettext.m4

version_check intltool INTLTOOLIZE intltoolize $REQUIRED_INTLTOOL_VERSION \
    "http://ftp.gnome.org/pub/GNOME/sources/intltool/" || DIE=1
require_m4macro intltool.m4


check_m4macros || DIE=1

if [ "$DIE" -eq 1 ]; then
  exit 1
fi

if [ "$#" = 0 ]; then
  printerr "**Warning**: I am going to run .configure with no arguments."
  printerr "If you wish to pass any to it, please specify them on the"
  printerr "$0 command line."
  printerr
fi

toplevel_check $srcfile

# Note that the order these tools are called should match what
# autoconf's "autoupdate" package does.  See bug 138584 for
# details.

# programs that might install new macros get run before aclocal

printbold "Running $GLIB_GETTEXTIZE... Ignore non-fatal messages."
echo "no" | $GLIB_GETTEXTIZE --force --copy || exit 1

printbold "Running $INTLTOOLIZE..."
$INTLTOOLIZE --force --copy --automake || exit 1

# Now run aclocal to pull in any additional macros needed
printbold "Running $ACLOCAL..."
$ACLOCAL -I m4 $ACLOCAL_FLAGS || exit 1

# Now that all the macros are sorted, run autoconf and autoheader ...
printbold "Running $AUTOCONF..."
$AUTOCONF || exit 1

# Finally, run automake to create the makefiles ...
printbold "Running $AUTOMAKE..."
cp -pf COPYING COPYING.autogen_bak
cp -pf INSTALL INSTALL.autogen_bak
$AUTOMAKE --gnu --add-missing --force --copy || exit 1
cmp COPYING COPYING.autogen_bak || cp -pf COPYING.autogen_bak COPYING
cmp INSTALL INSTALL.autogen_bak || cp -pf INSTALL.autogen_bak INSTALL
rm -f COPYING.autogen_bak INSTALL.autogen_bak


if test x$NOCONFIGURE = x; then
    printbold Running ./configure $CONFIGURE_DEF_OPT $CONFIGURE_EXT_OPT ...
    ./configure $CONFIGURE_DEF_OPT $CONFIGURE_EXT_OPT \
        && echo Now type \`make\' to compile $PKG_NAME || exit 1
else
    echo Skipping configure process.
fi

