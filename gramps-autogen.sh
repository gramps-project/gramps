#!/bin/sh
# Run this to generate all the initial makefiles, etc.
# $Id$

#name of package
PKG_NAME=${PKG_NAME:-Package}
srcdir=${srcdir:-.}

# default version requirements ...
REQUIRED_AUTOCONF_VERSION=${REQUIRED_AUTOCONF_VERSION:-2.53}
REQUIRED_AUTOMAKE_VERSION=${REQUIRED_AUTOMAKE_VERSION:-1.4}
REQUIRED_GLIB_GETTEXT_VERSION=${REQUIRED_GLIB_GETTEXT_VERSION:-2.2.0}
REQUIRED_INTLTOOL_VERSION=${REQUIRED_INTLTOOL_VERSION:-0.25}

# a list of required m4 macros.  Package can set an initial value
REQUIRED_M4MACROS=${REQUIRED_M4MACROS:-}
FORBIDDEN_M4MACROS=${FORBIDDEN_M4MACROS:-}

# Not all echo versions allow -n, so we check what is possible. This test is
# based on the one in autoconf.
case `echo "testing\c"; echo 1,2,3`,`echo -n testing; echo 1,2,3` in
  *c*,-n*) ECHO_N= ;;
  *c*,*  ) ECHO_N=-n ;;
  *)       ECHO_N= ;;
esac

# some terminal codes ...
boldface="`tput bold 2>/dev/null`"
normal="`tput sgr0 2>/dev/null`"
printbold() {
    echo $ECHO_N "$boldface"
    echo "$@"
    echo $ECHO_N "$normal"
}    

printerr() {
    echo "$@" >&2
}

autogen_options ()
{
  if test "x$1" = "x"; then
    return 0
  fi

  printbold "Checking command line options..."
  while test "x$1" != "x" ; do
    optarg=`expr "x$1" : 'x[^=]*=\(.*\)'`
    case "$1" in
      --noconfigure)
          NOCONFIGURE=defined
          AUTOGEN_EXT_OPT="$AUTOGEN_EXT_OPT --noconfigure"
          echo "  configure run disabled"
          shift
          ;;
      --nocheck)
          AUTOGEN_EXT_OPT="$AUTOGEN_EXT_OPT --nocheck"
          NOCHECK=defined
          echo "  autotools version check disabled"
          shift
          ;;
      --debug)
          DEBUG=defined
          AUTOGEN_EXT_OPT="$AUTOGEN_EXT_OPT --debug"
          echo "  debug output enabled"
          shift
          ;;
      -h|--help)
          echo "autogen.sh (autogen options) -- (configure options)"
          echo "autogen.sh help options: "
          echo " --noconfigure            don't run the configure script"
#          echo " --nocheck                don't do version checks"
          echo " --debug                  debug the autogen process"
          echo
          echo " --with-autoconf PATH     use autoconf in PATH"
          echo " --with-automake PATH     use automake in PATH"
          echo
          echo "Any argument either not in the above list or after a '--' will be "
          echo "passed to ./configure."
          exit 1
          ;;
      --with-automake=*)
          AUTOMAKE=$optarg
          echo "  using alternate automake in $optarg"
          CONFIGURE_DEF_OPT="$CONFIGURE_DEF_OPT --with-automake=$AUTOMAKE"
          shift
          ;;
      --with-autoconf=*)
          AUTOCONF=$optarg
          echo "  using alternate autoconf in $optarg"
          CONFIGURE_DEF_OPT="$CONFIGURE_DEF_OPT --with-autoconf=$AUTOCONF"
          shift
          ;;
      --) shift ; break ;;
      *)
          echo "  passing argument $1 to configure"
          CONFIGURE_EXT_OPT="$CONFIGURE_EXT_OPT $1"
          shift
          ;;
    esac
  done

  for arg do CONFIGURE_EXT_OPT="$CONFIGURE_EXT_OPT $arg"; done
  if test ! -z "$CONFIGURE_EXT_OPT"
  then
    echo "  options passed to configure: $CONFIGURE_EXT_OPT"
  fi
}

# Usage:
#     compare_versions MIN_VERSION ACTUAL_VERSION
# returns true if ACTUAL_VERSION >= MIN_VERSION
compare_versions() {
    ch_min_version=$1
    ch_actual_version=$2
    ch_status=0
    IFS="${IFS=         }"; ch_save_IFS="$IFS"; IFS="."
    set $ch_actual_version
    for ch_min in $ch_min_version; do
        ch_cur=`echo $1 | sed 's/[^0-9].*$//'`; shift # remove letter suffixes
        if [ -z "$ch_min" ]; then break; fi
        if [ -z "$ch_cur" ]; then ch_status=1; break; fi
        if [ $ch_cur -gt $ch_min ]; then break; fi
        if [ $ch_cur -lt $ch_min ]; then ch_status=1; break; fi
    done
    IFS="$ch_save_IFS"
    return $ch_status
}

# Usage:
#     version_check PACKAGE VARIABLE CHECKPROGS MIN_VERSION SOURCE
# checks to see if the package is available
version_check() {
    vc_package=$1
    vc_variable=$2
    vc_checkprogs=$3
    vc_min_version=$4
    vc_source=$5
    vc_status=1

    vc_checkprog=`eval echo "\\$$vc_variable"`
    if [ -n "$vc_checkprog" ]; then
	printbold "using $vc_checkprog for $vc_package"
	return 0
    fi

    if test "x$vc_package" = "xautomake" -a "x$vc_min_version" = "x1.4"; then
	vc_comparator="="
    else
	vc_comparator=">="
    fi
    printbold "Checking for $vc_package $vc_comparator $vc_min_version..."
    for vc_checkprog in $vc_checkprogs; do
	echo $ECHO_N "  testing $vc_checkprog... "
	if $vc_checkprog --version < /dev/null > /dev/null 2>&1; then
	    vc_actual_version=`$vc_checkprog --version | head -n 1 | \
                               sed 's/^.*[ 	]\([0-9.]*[a-z]*\).*$/\1/'`
	    if compare_versions $vc_min_version $vc_actual_version; then
		echo "found $vc_actual_version"
		# set variables
		eval "$vc_variable=$vc_checkprog; \
			${vc_variable}_VERSION=$vc_actual_version"
		vc_status=0
		break
	    else
		echo "too old (found version $vc_actual_version)"
	    fi
	else
	    echo "not found."
	fi
    done
    if [ "$vc_status" != 0 ]; then
	printerr "***Error***: You must have $vc_package $vc_comparator $vc_min_version installed"
	printerr "  to build $PKG_NAME.  Download the appropriate package for"
	printerr "  from your distribution or get the source tarball at"
        printerr "    $vc_source"
	printerr
    fi
    return $vc_status
}

debug ()
# print out a debug message if DEBUG is a defined variable
{
  if test ! -z "$DEBUG"
  then
    echo "DEBUG: $1"
  fi
}

# Usage:
#     require_m4macro filename.m4
# adds filename.m4 to the list of required macros
require_m4macro() {
    case "$REQUIRED_M4MACROS" in
	$1\ * | *\ $1\ * | *\ $1) ;;
	*) REQUIRED_M4MACROS="$REQUIRED_M4MACROS $1" ;;
    esac
}

forbid_m4macro() {
    case "$FORBIDDEN_M4MACROS" in
	$1\ * | *\ $1\ * | *\ $1) ;;
	*) FORBIDDEN_M4MACROS="$FORBIDDEN_M4MACROS $1" ;;
    esac
}

# Usage:
#     add_to_cm_macrodirs dirname
# Adds the dir to $cm_macrodirs, if it's not there yet.
add_to_cm_macrodirs() {
    case $cm_macrodirs in
    "$1 "* | *" $1 "* | *" $1") ;;
    *) cm_macrodirs="$cm_macrodirs $1";;
    esac
}

# Usage:
#     check_m4macros
# Checks that all the requested macro files are in the aclocal macro path
# Uses REQUIRED_M4MACROS and ACLOCAL variables.
check_m4macros() {
    # construct list of macro directories
    cm_macrodirs=`$ACLOCAL --print-ac-dir`
    # aclocal also searches a version specific dir, eg. /usr/share/aclocal-1.9
    # but it contains only Automake's own macros, so we can ignore it.

    # Read the dirlist file, supported by Automake >= 1.7.
    if compare_versions 1.7 $AUTOMAKE_VERSION && [ -s $cm_macrodirs/dirlist ]; then
	cm_dirlist=`sed 's/[ 	]*#.*//;/^$/d' $cm_macrodirs/dirlist`
	if [ -n "$cm_dirlist" ] ; then
	    for cm_dir in $cm_dirlist; do
		if [ -d $cm_dir ]; then
		    add_to_cm_macrodirs $cm_dir
		fi
	    done
	fi
    fi

    # Parse $ACLOCAL_FLAGS
    set - $ACLOCAL_FLAGS
    while [ $# -gt 0 ]; do
	if [ "$1" = "-I" ]; then
	    add_to_cm_macrodirs "$2"
	    shift
	fi
	shift
    done

    cm_status=0
    if [ -n "$REQUIRED_M4MACROS" ]; then
	printbold "Checking for required M4 macros..."
	# check that each macro file is in one of the macro dirs
	for cm_macro in $REQUIRED_M4MACROS; do
	    cm_macrofound=false
	    for cm_dir in $cm_macrodirs; do
		if [ -f "$cm_dir/$cm_macro" ]; then
		    cm_macrofound=true
		    break
		fi
		# The macro dir in Cygwin environments may contain a file
		# called dirlist containing other directories to look in.
		if [ -f "$cm_dir/dirlist" ]; then
		    for cm_otherdir in `cat $cm_dir/dirlist`; do
			if [ -f "$cm_otherdir/$cm_macro" ]; then
			    cm_macrofound=true
		            break
			fi
		    done
		fi
	    done
	    if $cm_macrofound; then
		:
	    else
		printerr "  $cm_macro not found"
		cm_status=1
	    fi
	done
    fi
    if [ -n "$FORBIDDEN_M4MACROS" ]; then
	printbold "Checking for forbidden M4 macros..."
	# check that each macro file is in one of the macro dirs
	for cm_macro in $FORBIDDEN_M4MACROS; do
	    cm_macrofound=false
	    for cm_dir in $cm_macrodirs; do
		if [ -f "$cm_dir/$cm_macro" ]; then
		    cm_macrofound=true
		    break
		fi
	    done
	    if $cm_macrofound; then
		printerr "  $cm_macro found (should be cleared from macros dir)"
		cm_status=1
	    fi
	done
    fi
    if [ "$cm_status" != 0 ]; then
	printerr "***Error***: some autoconf macros required to build $PKG_NAME"
	printerr "  were not found in your aclocal path, or some forbidden"
	printerr "  macros were found.  Perhaps you need to adjust your"
	printerr "  ACLOCAL_FLAGS?"
	printerr
    fi
    return $cm_status
}

toplevel_check()
{
  srcfile=$1
  test -f $srcfile || {
        echo "You must run this script in the top-level $PKG_NAME directory"
        exit 1
  }
}


