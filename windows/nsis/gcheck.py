import sys

fn = sys.argv[1]
f = open(fn,"w")

f.write('[tests]\n')

try:
    import gtk
    f.write('gtk=yes\n')
    f.write('gtkver=%d.%d.%d\n' % gtk.gtk_version)
    f.write('pygtk=yes\n')
    f.write('pygtkver=%d.%d.%d\n' % gtk.pygtk_version)
except ImportError:
    f.write('gtk=no\n')
    f.write('gtkver=no\n')
    f.write('pygtk=no\n')
    f.write('pygtkver=no\n')

try:
    import gtk.glade
    f.write('glade=yes\n')
except ImportError:
    f.write('glade=no\n')

try:
    import cairo
    f.write('pycairo=yes\n')
    f.write('pycairover=%s\n' % cairo.version_info)
except ImportError:
    f.write('pycairo=no\n')
    f.write('pycairover=no\n')
f.close()
