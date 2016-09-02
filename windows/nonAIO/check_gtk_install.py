#
# Gramps - a GTK+ based genealogy program
#
# Copyright (C) 2010       Stephen George
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
# $Id: $
import sys
import os
import _winreg
from ctypes.util import find_library
import getopt
import string

NOT_FOUND_STR ='Not Found'
#small selection of DLL's to test
testdlls = ['libgdk-win32-2.0-0.dll', 'libglib-2.0-0.dll', 'libgobject-2.0-0.dll', 'libcairo-2.dll', ]

explain_exposed = '''    ***********************************************************
    * It seems that other installations are exposing GTK DLL's
    * to the operating system as they are in the environment
    * path variable BEFORE the runtime directory.
    * You should reorder the path variable to put your GTK
    * runtime path before these other installations on the path'''

explain_safe = '''    ***************************************************************
    * While there are other installations of GTK DLL's on the path,
    * it should be safe as they are on the path AFTER the runtime
    * directory. '''

def RunExeCommand( app, args ):
    cmd = app + ' ' + args
    #print("Running: ", cmd)
    stdin, stdout, stderr = os.popen3( cmd )
    output = string.strip(stdout.read())
    #print(output)
    err = stderr.read()
    if err:
        print(err)
    return output

def CheckGtkInReg():
    global gtkPathInRegistry, gtkVersionInRegistry, dllPathInRegistry, dllPathShort
    print('\n==== Checking Registry for GTK =====')
    try:
        with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\GTK\\2.0') as key:
            gtkVersionInRegistry = _winreg.QueryValueEx(key, 'Version')[0]
            gtkPathInRegistry = _winreg.QueryValueEx(key, 'Path')[0]
            dllPathInRegistry = _winreg.QueryValueEx(key, 'DllPath')[0]
            print('  Version   :', gtkVersionInRegistry)
            print('  Path      :', gtkPathInRegistry)
            print('  DllPath   :', dllPathInRegistry)

    except WindowsError as e:
        print('\n  GTK registry key not found in registry')
        print('''    ********************************************************************
    * This might not be an error, but means I don't know the directory to
    * your preferred GTK installation.
    *  - try passing in your GTK installation path.\n''')
        print('-' * 60)
        print(usage)
        sys.exit(0)

def WorkOutShortDosPath():
    global dllPathShort
    print('\n==== Use win32Api to query short path name for GTK =====')
    try:
        import win32api
        dllPathShort =  win32api.GetShortPathName(dllPathInRegistry)
        print('  DllPath8.3:', dllPathShort)
    except ImportError:
        print('  **Cant query short path name, Win32Api not installed')
        print('    install from http://python.net/crew/mhammond/win32/')
        print('    if you want this function to work')

def FindLibsWithCtypes():
    # use ctypes to check where windows finds it's DLL's
    print('\n==== Use ctypes to find dlls ====')
    other_paths = []
    for dll in testdlls:
        dllpathvalid = False
        cpath = find_library(dll)
        if cpath:
        #print(cpath)
            if cpath == os.path.join(dllPathInRegistry, dll) \
            or cpath == os.path.join(dllPathShort, dll):
                dllpathvalid = True

            if not dllpathvalid:
                pp = os.path.dirname(cpath)
                if pp not in other_paths:
                    other_paths.append(pp)
        else:
            print("  ERROR:... ctypes failed to find %s" % dll)
    if other_paths:
        for pth in other_paths:
            print("  ERROR: ctypes loaded some gtk dll's from %s" % pth)
    else:
        print("  OK ... ctypes found dll's in %s" % os.path.dirname(cpath))

def ScanDependencyFileForErrors(fname):
    fin = open(fname, 'r')
    lines = fin.readlines()
    fin.close()
    sysroot = os.environ["SystemRoot"]
    capture = False
    runtimedlls = {}
    for line in lines:
        if line.startswith("       Module"): # work out were paths end
            pthend_idx = line.find("File Time Stamp")
        acceptablePaths = [ dllPathShort.lower(),
                            dllPathInRegistry.lower(),
                            os.path.join(sysroot, 'system32').lower()
                          ]
        if line.startswith('-----  ------------'):
            capture = True
        if capture and line.startswith('['):
            filename = line[5:pthend_idx].strip()
            dirname = os.path.dirname(filename).strip()
            parts = line[pthend_idx:].split()
            OK = False
            if dirname.startswith(os.path.join(sysroot, 'winsxs').lower()) \
            or dirname.startswith(os.path.join(sys.prefix, 'lib\site-packages\gtk-2.0').lower()):
                OK = True

            for pth in acceptablePaths:
                if dirname == pth.lower():
                    OK = True

            if 'MSVCR90.DLL' in filename:
                if parts[0] == 'Error':
                    runtimedlls[filename] = "Error dll not found"
                else:
                    runtimedlls[filename] = parts[16]

            if OK == False:
                if parts[0] == 'Error':
                    print("    %s \tError dll not found" %( filename))
                else:
                    print("    ERROR: %s \tVersion %s" %( filename, parts[16]))
    for rtdll in runtimedlls:
        if runtimedlls[rtdll].startswith("Error"):
            print('\n    ERROR: MS runtime %s not found'%rtdll)
        else:
            print('\n    MS runtime Version %s loaded from' % runtimedlls[rtdll])
            print("    %s" %rtdll)
    print()

def CheckWithDependencyWalker():
    print('\n==== Checking with Dependency Walker ====')
    print('      Please be patient takes some time')
    exe = os.path.join(scriptpath, 'depends.exe')
    fout = os.path.join(scriptpath, 'depres.txt')
    f2check = [
                os.path.join(sys.prefix, 'Lib/site-packages/gtk-2.0/gtk/_Gtk.pyd' ),
                os.path.join(sys.prefix, 'Lib/site-packages/gtk-2.0/gobject/_GObject.pyd' ),
                os.path.join(sys.prefix, 'Lib/site-packages/gtk-2.0/pangocairo.pyd' ),
                ]
    if os.path.isfile( exe ):
        for ftest in f2check:
            if os.path.isfile( ftest ):
                #delete the output file before running command
                try:
                    os.remove(fout)
                except WindowsError as e:
                    pass
                print('  Testing file %s' % ftest)
                out = RunExeCommand(exe, '/c /f1 /ot "%s" "%s"' % (fout, ftest) )
                if os.path.isfile(fout):
                    ScanDependencyFileForErrors(fout)
            else:
                print("  ERROR: file %d does not exist", ftest)
    else:
        print('  Cannot check with dependency walker, not installed in local directory')
        print('  get dependency walker from http://www.dependencywalker.com/')
        print('  and unzip into this directory for it to work.')

def CheckPathForOtherGtkInstalls():
    print('\n====Checking environment path for other gtk installations====')
    ePath = os.environ['path']
    dirs = ePath.split(';')
    gtkpth_idx = 9999
    other_paths = []
    explain_level = 0
    for i, d in enumerate(dirs):
        #print('==%s==' %d)
        if d == gtkPathInRegistry or d == dllPathInRegistry\
        or d == dllPathShort:
            gtkpth_idx = i
            continue
        for fname in testdlls:
            f = os.path.join(d, fname)
            if os.path.isfile( f ):
                #print('   Found Erronous gtk DLL %s' % f)
                if d not in other_paths:
                    other_paths.append(d)
                    if i < gtkpth_idx: # path appears BEFORE runtime path
                        print('  ERROR: %s should not appear before runtime path' % d)
                        explain_level = 2
                    else:
                        print('  FOUND: %s, Probably OK as appears AFTER runtime path' % d)
                        if explain_level <= 1:
                            explain_level = 1
    if gtkpth_idx == 9999:
        print('\n  ERROR: Runtime directory not on enviroment path')
        print("         ** Runtime needs to be on path to load DLL's from\n")
    if explain_level == 2:
        print(explain_exposed)
    elif explain_level == 1:
        print(explain_safe)
    if len(other_paths) == 0:
        print('  No other gtk installatons found\n')

# ==== report what python thinks it's using =====
MIN_PYTHON_VER   = (2,5,1)
UNTESTED_PYTHON_VER = (3,0,0)

MIN_GTK_VER      = (2,10,11)
UNTESTED_GTK_VER = (2,16,7)

MIN_PYGTK_VER    = (2,10,6)
UNTESTED_PYGTK_VER    = (2,12,2)

MIN_GOBJECT_VER  = (2,12,3)
UNTESTED_GOBJECT_VER  = (2,14,3)

MIN_CAIRO_VER    = (1,2,6)
UNTESTED_CAIRO_VER    = (1,4,13)

def PrintFailedImport(appl, minVersion, result):
    print(appl,)
    print('version %d.%d.%d or above.....\t' % minVersion ,)
    print(result)

def PrintVersionResult(appl, minVersion, actualVersion, untestedVersion):
    print(appl,)
    print('version %d.%d.%d or above.....\t' % minVersion ,)
    print('found %d.%d.%d' % actualVersion ,)
    if minVersion <= actualVersion < untestedVersion:
        print('...OK')
    elif  actualVersion >= untestedVersion:
        print('...UNTESTED VERSION')
    else:
        print('...FAILED')

def Import_pyGtkIntoPython():
    print('\n==== Test import into python ====')
    #py_str = 'found %d.%d.%d' %  sys.version_info[:3]
    PrintVersionResult('  Python ', MIN_PYTHON_VER, sys.version_info[:3], UNTESTED_PYTHON_VER)

    # Test the GTK version
    try:
        import gtk

        PrintVersionResult('  GTK+   ', MIN_GTK_VER, Gtk.gtk_version, UNTESTED_GTK_VER )

        #test the pyGTK version (which is in the gtk namespace)
        PrintVersionResult('  pyGTK  ', MIN_PYGTK_VER, Gtk.pygtk_version, UNTESTED_PYGTK_VER )

    except ImportError:
        PrintFailedImport('  GTK+   ', MIN_GTK_VER, NOT_FOUND_STR)
        PrintFailedImport('  pyGTK  ', MIN_PYGTK_VER, 'Cannot test, ...GTK+ missing')


    #test the gobject version
    try:
        import gobject
        PrintVersionResult('  gobject', MIN_GOBJECT_VER, GObject.pygobject_version, UNTESTED_GOBJECT_VER) 

    except ImportError:
        PrintFailedImport('  gobject', MIN_GOBJECT_VER, NOT_FOUND_STR)


    #test the cairo version
    try:
        import cairo
        PrintVersionResult('  cairo  ', MIN_CAIRO_VER, cairo.version_info, UNTESTED_CAIRO_VER )

    except ImportError:
        PrintFailedImport('  cairo  ', MIN_CAIRO_VER, NOT_FOUND_STR)

    #test for glade
    print('\n==== See if libglade installed ====')

    try:
        import Gtk.glade
        print('  Glade   tesing import of libglade .......\tOK\n')
    except ImportError as e:
        print('  Glade   importError: %s\n' % e)

if __name__ == '__main__':
    usage = '''Check for common problems in GTK/pyGTK installation.
Usage:
    python %s [options] [gtkPath]

Arguments:
    gtkPath                    Path to your GTK installation directory (not the bin dir)

Options:
    None
    ''' %(os.path.basename(__file__) )

    gtkPath = None
    gtkPathInRegistry = NOT_FOUND_STR
    gtkVersionInRegistry = NOT_FOUND_STR
    dllPathInRegistry = NOT_FOUND_STR
    dllPathShort = 'NoShortPath'
    scriptpath = os.path.dirname(sys.argv[0])
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                                  [])

        for o, a in opts:
            if o in ("-h", "--help"):
                print(usage)
                sys.exit(0)

        if len(args) > 1:
            raise getopt.GetoptError('\nERROR: Too many arguments')
        for arg in args:
            if os.path.isdir(arg):
                gtkPath = arg
            else:
                raise getopt.GetoptError('\nERROR: Not a valid GTK path %s' % arg)

    except getopt.GetoptError as msg:
        print(msg)
        print('\n %s' % usage)
        sys.exit(2)

    import platform
    winver = platform.win32_ver()
    if len(winver) == 4:
        print('''\n==== platform.win32_ver() reports ====
  Operating System: %s
  Version         : %s
  Service Pack    : %s
  OS type         : %s''' %  winver)
    else:
        print(winver)

    if gtkPath:
        gtkPathInRegistry = gtkPath
        dllPathInRegistry = os.path.join(gtkPath, 'bin')
        print('  Using %s as GTK install path' % gtkPathInRegistry)
        print('  Using %s as GTK dll path' % dllPathInRegistry)
    else:
        CheckGtkInReg()

    WorkOutShortDosPath()
    FindLibsWithCtypes()
    CheckPathForOtherGtkInstalls()
    Import_pyGtkIntoPython()

    CheckWithDependencyWalker()

