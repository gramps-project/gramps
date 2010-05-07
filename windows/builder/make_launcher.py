# SetLanguage.py
#
# Gramps - a GTK+ based genealogy program
#
# Copyright (C) 2010 Stephen George
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
# $Id:  $
import locale
import _winreg
import sys
import os

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
                    datefmt='%H:%M',
                    filename= 'c:/launcher.log', #path.join(out_dir,'build.log'),
                    filemode='w')
#create a Handler for the console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
#Set a simle format for console
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
#add the console handler to the root handler
log = logging.getLogger('BuildApp')
log.addHandler(console)


langLookup = {
            'ar' : 'Arabic',
            'bg' : 'Bulgarian',
            'ca' : 'Catalan',
            'cs' : 'Czech',
            'da' : 'Danish ',
            'de' : 'German',
            'en' : 'English',
            'eo' : '',
            'es' : 'Spanish',
            'fi' : 'Finnish',
            'fr' : 'French',
            'he' : 'Hebrew',
            'hr' : 'Croatian',
            'hu' : 'Hungarian',
            'it' : 'Italian',
            'lt' : 'Lithuanian',
            'mk' : 'Macedonian',
            'nb' : '',
            'nl' : 'Dutch',
            'nn' : '',
            'pl' : 'Polish',
            'pt_BR' : 'Portuguese (Brazil)',
            'ro' : 'Romanian',
            'ru' : 'Russian',
            'sk' : 'Slovak',
            'sl' : 'Slovenian',
            'sq' : 'Albanian',
            'sr' : 'Serbian',
            'sv' : 'Swedish',
            'tr' : 'Turkish',
            'zh_CN' : 'Chinese (PRC)',
            }

def GetGtkPath():
    log.debug('GetGtkPath()')
    dllPathInRegistry = None
    try:
        with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\GTK\\2.0') as key:
            dllPathInRegistry = _winreg.QueryValueEx(key, 'DllPath')[0]
            # check a few key files exist at this location
            gtkfiles = ['libgdk-win32-2.0-0.dll', 'libglib-2.0-0.dll', 'libgobject-2.0-0.dll', 'libcairo-2.dll'] 
            for file in gtkfiles:
                if not os.path.isfile(os.path.join(dllPathInRegistry, file)):
                    dllPathInRegistry = None # one of the files not present, so assume path is wrong
                    break
    except WindowsError, e:
        dllPathInRegistry = None
    log.debug(' DLLPATH=%s'%dllPathInRegistry)
    return dllPathInRegistry

def GetGrampsPath():
    GrampsPathInRegistry = None
    try:  
        with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\GRAMPS') as key:
            GrampsPathInRegistry = _winreg.QueryValue(key, '')
            # check a few key files exist at this location
    except WindowsError, e:
        GrampsPathInRegistry = None
        
    log.debug(' GRAMPSPATH=%s'%GrampsPathInRegistry)
    return GrampsPathInRegistry
    
def GetLanguageFromLocale():
    lang = ' '
    try:
        lang = os.environ["LANG"]
        lang = lang.split('.')[0]
    except:
        # if LANG is not set
        lang = locale.getlocale()[0]
        if not lang:
            # if lang is empty/None
            lang = locale.getdefaultlocale()[0] 
    return lang

def writeLauncher(language, langcode, runtimepath, grampspath):
    lines = []
    lines.append('\n@rem Command file to set %s language for Gramps \n' % language)
    lines.append('SET LANG=$LANG$ \nSET LANGUAGE=$LANG$\n'.replace("$LANG$", langcode) )
    if runtimepath:
        path = '\npath="%s";%%PATH%%' % runtimepath
    else:
        path = "\n@rem path=PATH_TO_YOUR_GTK_RUNTIME;%%PATH%%\n" 
    lines.append(path)
    lines.append('\n@rem start Gramps')
    lines.append('\n"%s" "%s"\n' % (os.path.join(sys.prefix, 'pythonw.exe') , os.path.join(grampspath, 'gramps.py' ) ))
    fout = open( os.path.join(grampspath, 'gramps_locale.cmd'), 'w')
    fout.writelines(lines)
    fout.close()
    for line in lines:
        print line

gtkpath = GetGtkPath()
grampspath = GetGrampsPath()
lang = GetLanguageFromLocale()
if lang:
    try:
        lang_text = langLookup[lang.split('_', 1)[0]]
    except KeyError, e:
        try:
            lang_text = langLookup[lang]
        except KeyError, e:
            lang_text = "Unknown"
        
    writeLauncher(lang_text, "%s.UTF8"%lang, gtkpath, grampspath)    
