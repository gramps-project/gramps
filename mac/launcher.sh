#!/bin/sh

name="`basename $0`"
tmp="`pwd`/$0"
tmp=`dirname "$tmp"`
tmp=`dirname "$tmp"`
bundle=`dirname "$tmp"`
bundle_contents="$bundle"/Contents
bundle_res="$bundle_contents"/Resources
bundle_lib="$bundle_res"/lib
bundle_bin="$bundle_res"/bin
bundle_data="$bundle_res"/share
bundle_etc="$bundle_res"/etc

export XDG_DATA_DIRS="$bundle_data"

export DYLD_LIBRARY_PATH="$bundle_lib"
export LD_LIBRARY_PATH="$DYLD_LIBRARY_PATH"
export GTK_DATA_PREFIX="$bundle_res"
export GTK_EXE_PREFIX="$bundle_res"
export GTK_PATH="$bundle_res"

export GTK2_RC_FILES="$bundle_etc/gtk-2.0/gtkrc"
export GTK_IM_MODULE_FILE="$bundle_etc/gtk-2.0/gtk.immodules"
export GDK_PIXBUF_MODULE_FILE="$bundle_etc/gtk-2.0/gdk-pixbuf.loaders"
export PANGO_RC_FILE="$bundle_etc/pango/pangorc"
export GVBINDIR="$bundle_lib/graphviz"

#Set $PYTHON to point inside the bundle
export PYTHON="$bundle_contents/MacOS/python"
#Add the bundle's python modules
PYTHONPATH="$bundle_lib/python2.6:$PYTHONPATH"
PYTHONPATH="$bundle_lib/python2.6/site-packages:$PYTHONPATH"
PYTHONPATH="$bundle_lib/python2.6/site-packages/gtk-2.0:$PYTHONPATH"
PYTHONPATH="$bundle_lib/python2.6/lib-dynload:$PYTHONPATH"
#Add our program's modules to $PYTHONPATH. 
PYTHONPATH="$bundle_lib/pygtk/2.0:$PYTHONPATH"
export PYTHONPATH
export GRAMPSDIR="$bundle_data"/gramps
export GRAMPSI18N="$bundle_data"/locale
export GRAMPSHOME="$HOME/Library/Application Support"

# Strip out the argument added by the OS.
if [ x`echo "x$1" | sed -e "s/^x-psn_.*//"` == x ]; then
    shift 1
fi

#Note that we're calling $PYTHON here to override the version in
#pygtk-demo's shebang.
exec $PYTHON -O "$GRAMPSDIR/gramps.py" "$@"
