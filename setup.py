# Gramps - a GTK+/GNOME based genealogy program
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# testing a setup.py for Gramps

from distutils.cmd import Command
from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_data import install_data
import distutils.command.clean
import sys
import glob
import os.path
import os
import subprocess
import platform
                        
name = 'gramps'
version = "trunk"

PO_DIR = 'po'
MO_DIR = os.path.join('build', 'mo')

if sys.version < '2.6':
    sys.exit('Error: Python-2.6 or newer is required. Current version:\n %s'
             % sys.version)
             
if os.name == 'nt':
    script = [os.path.join('windows','gramps.pyw')]
elif os.name == 'darwin':
    script = [os.path.join('mac','gramps.launcher.sh')]
else:
    # os.name == 'posix'
    script = [os.path.join('gramps.sh')]

if platform.system() == 'FreeBSD':
    man_dir = 'man'
else:
    man_dir = os.path.join('share', 'man')

def modules_check():
    '''Check if necessary modules is installed.
    The function is executed by distutils (by the install command).'''
    try:
        try:
            import gtk.glade
        except RuntimeError:
            print ("Error importing GTK - is there no windowing environment available ? \n"
                   "We're going to ignore this error and live dangerously. Please make \n"
                   "sure you have pygtk > 2.16 and gtk available!")
    except ImportError:
        raise
    mod_list = [
        ('pygtk','gtk'),
        ('pycairo','cairo'),
        'pygobject',
        ]
    ok = 1
    for m in mod_list:
        if type(m)==tuple:
            have_mod = False
            for mod in m:
                try:
                    exec('import %s'% mod)
                except ImportError:
                    pass
                else:
                    have_mod = True
            if not have_mod:
                ok = False
                print ('Error: %s is Python module is required to install %s'
                    % (' or '.join(m), name.title()))
        else:
            try:
                exec('import %s' % m)
            except ImportError:
                ok = False
                print ('Error: %s Python module is required to install %s'
                  % (m, name.title()))
    if not ok:
        sys.exit(1)

def gramps():
    # missing const.py (const.py.in)
    libs = {'gramps': [
            '*.py', 
            'DateHandler/*.py',
            'docgen/*.py',
            'Filters/*.py',
            'Filters/*/*.py',
            'Filters/Rules/*/*.py',
            'GrampsLocale/*.py',
            'GrampsLogger/*.py',
            'Merge/*.py',
            'Simple/*.py'],
            'gramps.cli': [
            '*.py',
            'plug/*.py'],
            'gramps.data': [
            '*.txt',
            '*.xml'],
            #'javascript/css/swanky-purse/images/*.png',
            #'javascript/css/swanky-purse/*.css',
            #'javascript/index.html',
            #'javascript/js/*.js',
            #'templates/*.html',
            #'templates/registration/login.html',
            #'templates/successful_data_change.html'],
            'gramps.gen': [
            '*.py',
            'db/*.py',
            'display/*.py',
            'lib/*.py',
            'mime/*.py',
            'plug/*.py',
            'plug/*/*.py',
            'proxy/*.py',
            'utils/*.py'],
            'gramps.glade': [
            '*.glade',
            'glade/catalog/*.py',
            'catalog/*.xml'],
            'gramps.gui': [
            '*.py',
            'editors/*.py',
            'editors/*/*.py',
            'plug/*.py',
            'plug/*/*.py',
            'selectors/*.py',
            'views/*.py',
            'views/treemodels/*.py',
            'widgets/*.py'],
            'gramps.images': [
            '*/*.png',
            '*/*.svg',
            '*.png',
            '*.jpg',
            '*.ico',
            '*.gif'],
            'gramps.plugins': [
            '*.py',
            '*/*.py',
            'lib/*.xml',
            'lib/maps/*.py',            
            '*.glade',
            '*/*.glade'],
            'gramps.webapp': [
            '*.py',
            'webstuff/css/*.css',
            'webstuff/images/*.svg',
            'webstuff/images/*.png',
            'webstuff/images/*.gif',
            'grampsdb/fixtures/initial_data.json',
            '*/*.py',
            'sqlite.db',
            'grampsdb/*.py',
            'fixtures/initial_data.json',
            'templatetags/*py'],
            }

    return libs

def os_files():
    if os.name == 'nt' or os.name == 'darwin':
        files = [
                # application icon
                (os.path.join('share', 'pixmaps'), [os.path.join('src', 'images', 'ped24.ico')]),
                (os.path.join('share', 'pixmaps'), [os.path.join('src', 'images', 'gramps.png')]),
                (os.path.join('share', 'icons', 'scalable'), glob.glob(os.path.join('src', 'images', 'scalable', '*.svg'))),
                (os.path.join('share', 'icons', '16x16'), glob.glob(os.path.join('src', 'images', '16x16', '*.png'))),
                (os.path.join('share', 'icons', '22x22'), glob.glob(os.path.join('src', 'images', '22x22' ,'*.png'))),
                (os.path.join('share', 'icons', '48x48'), glob.glob(os.path.join('src', 'images', '48x48', '*.png'))),
                # doc
                ('share', ['COPYING']),
                ('share', ['FAQ']),
                ('share', ['INSTALL']),
                ('share', ['NEWS']),
                ('share', ['README']),
                ('share', ['TODO'])
                ]
    else:
        files = [
                # XDG application description
                ('share/applications', ['data/gramps.desktop']),
                # XDG application icon
                ('share/pixmaps', ['src/images/gramps.png']),
                # XDG desktop mime types cache
                ('share/mime/packages', ['data/gramps.xml']),
                # mime.types
                ('share/mime-info', ['data/gramps.mime']),
                ('share/mime-info', ['data/gramps.keys']),
                ('share/icons/gnome/48x48/mimetypes', ['data/gnome-mime-application-x-gedcom.png']),
                ('share/icons/gnome/48x48/mimetypes', ['data/gnome-mime-application-x-geneweb.png']),
                ('share/icons/gnome/48x48/mimetypes', ['data/gnome-mime-application-x-gramps.png']),
                ('share/icons/gnome/48x48/mimetypes', ['data/gnome-mime-application-x-gramps-package.png']),
                ('share/icons/gnome/48x48/mimetypes', ['data/gnome-mime-application-x-gramps-xml.png']),
                ('share/icons/gnome/scalable/mimetypes', ['data/gnome-mime-application-x-gedcom.svg']),
                ('share/icons/gnome/scalable/mimetypes', ['data/gnome-mime-application-x-geneweb.svg']),
                ('share/icons/gnome/scalable/mimetypes', ['data/gnome-mime-application-x-gramps.svg']),
                ('share/icons/gnome/scalable/mimetypes', ['data/gnome-mime-application-x-gramps-package.svg']),
                ('share/icons/gnome/scalable/mimetypes', ['data/gnome-mime-application-x-gramps-xml.svg']),
                # man-page, /!\ should be gramps.1 with variables
                # migration to sphinx/docutils/gettext environment ?
                (os.path.join(man_dir, 'man1'), ['data/man/gramps.1.in']),
                (os.path.join(man_dir, 'cs', 'man1'), ['data/man/cs/gramps.1.in']),
                (os.path.join(man_dir, 'fr', 'man1'), ['data/man/fr/gramps.1.in']),
                (os.path.join(man_dir, 'nl', 'man1'), ['data/man/nl/gramps.1.in']),
                (os.path.join(man_dir, 'pl', 'man1'), ['data/man/pl/gramps.1.in']),
                (os.path.join(man_dir, 'sv', 'man1'), ['data/man/sv/gramps.1.in']),
                # icons 
                ('share/icons/hicolor/scalable/apps', glob.glob('src/images/scalable/*.svg')),
                ('share/icons/hicolor/16x16/apps', glob.glob('src/images/16x16/*.png')),
                ('share/icons/hicolor/22x22/apps', glob.glob('src/images/22x22/*.png')),
                ('share/icons/hicolor/48x48/apps', glob.glob('src/images/48x48/*.png')),
                # doc
                ('share/doc/gramps', ['COPYING']),
                ('share/doc/gramps', ['FAQ']),
                ('share/doc/gramps', ['INSTALL']),
                ('share/doc/gramps', ['NEWS']),
                ('share/doc/gramps', ['README']),
                ('share/doc/gramps', ['TODO'])
                ]
        return files  

def trans_files():
    '''
    List of available compiled translations; ready for installation
    '''
    translation_files = []
    for mo in glob.glob (os.path.join (MO_DIR, '*', 'gramps.mo')):
        lang = os.path.basename(os.path.dirname(mo))
        if os.name == 'posix':
            dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
        else :
            dest = os.path.join('locale', lang, 'LC_MESSAGES')
        translation_files.append((dest, [mo]))
           
    return translation_files

class BuildData(build):
    '''
    Custom command for 'python setup.py build' ...
    '''
    
    def initialize_options (self):
        
        if os.name == 'posix':
            # initial makefiles ... create launcher and generate const.py
            # see script !
            #os.system('./autogen.sh')
            # related translations files
            os.system('intltool-merge -d po/ data/gramps.desktop.in data/gramps.desktop')
            os.system('intltool-merge -x po/ data/gramps.xml.in data/gramps.xml')
            os.system('intltool-merge -k po/ data/gramps.keys.in data/gramps.keys')
            
    def run (self):
        
        # Run upgrade pre script
        # /!\ should be gramps.sh with variables
        # missing const.py (const.py.in)
        
        for po in glob.glob(os.path.join(PO_DIR, '*.po')):
            lang = os.path.basename(po[:-3])
            mo = os.path.join(MO_DIR, lang, 'gramps.mo')
            directory = os.path.dirname(mo)
            if not os.path.exists(directory):
                os.makedirs(directory)
            if os.name == 'posix':
                os.system('msgfmt %s/%s.po -o %s' % (PO_DIR, lang, mo))
            print (directory)
                
    def finalize_options (self):
        pass
            
class InstallData(install_data):
    '''
    Custom command for 'python setup.py install' ...
    '''
    
    def run (self):
        
        install_data.run(self)
    
    def finalize_options (self):
        
        if os.name == 'posix':
            #update the XDG Shared MIME-Info database cache
            sys.stdout.write('Updating the Shared MIME-Info database cache.\n')
            subprocess.call(["update-mime-database", os.path.join(sys.prefix, 'share', 'mime')])

            #update the mime.types database (debian, ubuntu)
            #sys.stdout.write('Updating the mime.types database\n')
            #subprocess.call("update-mime")

            # update the XDG .desktop file database
            sys.stdout.write('Updating the .desktop file database.\n')
            subprocess.call(["update-desktop-database"])
            
            #ldconfig
            
class Install(Command):
    '''
    Standard command for 'python setup.py install' ...
    '''
    
    description = "Attempt an install and generate a log file"
    
    user_options = [('fake', None, 'Override')]
    
    def initialize_options(self):
        pass
    
    def run (self):
        pass
        
    def finalize_options (self):
        pass

class Uninstall(Command):
    '''
    Custom command for uninstalling
    '''
    
    description = "Attempt an uninstall from an install log file"

    user_options = [('log=', None, 'Installation record filename')]

    def initialize_options(self):
        self.log = 'log'

    def finalize_options(self):
        pass

    def get_command_name(self):
        return 'uninstall'

    def run(self):
        f = None
        self.ensure_filename('log')
        try:
            try:
                f = open(self.log)
                files = [file.strip() for file in f]
            except IOError, e:
                raise DistutilsFileError("unable to open log: %s", str(e))
        finally:
            if f:
                f.close()

        for file in files:
            if os.path.isfile(file) or os.path.islink(file):
                print ("removing %s" % repr(file))
            if not self.dry_run:
                try:
                    os.unlink(file)
                except OSError, e:
                    warn("could not delete: %s" % repr(file))
            elif not os.path.isdir(file):
                print ("skipping %s" % repr(file))

        dirs = set()
        for file in reversed(sorted(files)):
            dir = os.path.dirname(file)
            if dir not in dirs and os.path.isdir(dir) and len(os.listdir(dir)) == 0:
                dirs.add(dir)
                # Only nuke empty Python library directories, else we could destroy
                # e.g. locale directories we're the only app with a .mo installed for.
            if dir.find("dist-packages") > 0:
                print ("removing %s" % repr(dir))
                if not self.dry_run:
                    try:
                        os.rmdir(dir)
                    except OSError, e:
                        warn("could not remove directory: %s" % str(e))
            else:
                print ("skipping empty directory %s" % repr(dir))
                  
    
result = setup(
    name         = name,
    version      = version,
    description  = 'Gramps (Genealogical Research and Analysis Management Programming System)',
    author       = 'Gramps Development Team',
    author_email = 'don@gramps-project.org',
    url          = 'http://gramps-project.org',
    license      = 'GNU GPL v2 or greater',
    packages     = ['gramps',
                    'gramps.cli',
                    'gramps.data',
                    'gramps.gen',
                    'gramps.glade',
                    'gramps.gui',
                    'gramps.images',
                    'gramps.plugins',
                    'gramps.webapp',
                  ],
    package_dir  = {'gramps' : 'src'},
    package_data = gramps(),
    data_files   = trans_files() + os_files(),
    platforms    = ['Linux', 'FreeBSD', 'MacOS', 'Windows'],
    scripts      = script,
    requires     = ['pygtk', 'pycairo', 'pygobject'],
    cmdclass     = {
                    'build': BuildData,
                    'install': InstallData, # override Install!
                    #'install_data': InstallData, # python setup.py --help-commands
                    'uninstall': Uninstall}
    )
