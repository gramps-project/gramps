#
# Gramps - a GTK+ based genealogy program
#
# Copyright (C) 2006-2008 Steve Hall <digitect dancingpaper com>
# Copyright (C) 2008 Stephen George
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
# $Id:  $
#
# Description: Nullsoft Installer (NSIS) file to build Windows installer:
#
# Requires:    NSIS version 2.0 or later.
# Notes:
# o WARNING: if you make changes to this script, look out for $INSTDIR
#   to be valid, because this line is very dangerous:  RMDir /r $INSTDIR
# o WARNING: Except the uninstaller. That re-paths for some reason.
#
!define GRAMPS_VERSION      $%GRAMPS_VER%
!define GRAMPS_BUILD_PATH   "$%GRAMPS_BUILD_DIR%"
!define GRAMPS_OUT_PATH     "$%GRAMPS_OUT_DIR%"

!define MIN_PYTHON_VERSION      "2.6.0"
!define MIN_GTK_VERSION         "2.12.9"
!define MIN_PYGTK_VERSION       "2.12.1"
!define MIN_GOBJECT_VERSION   "2.12.3"
!define MIN_CAIRO_VERSION     "1.2.6"

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME            "GRAMPS"
!define PRODUCT_VERSION         ${GRAMPS_VERSION}
!define PRODUCT_PUBLISHER       "The GRAMPS project"
!define PRODUCT_WEB_SITE        "http://gramps-project.org"
!define PRODUCT_UNINST_KEY      "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

!define DESKTOP_LINK "$DESKTOP\${PRODUCT_NAME} ${PRODUCT_VERSION}.lnk"

# output file
Name ${PRODUCT_NAME}
OutFile "${GRAMPS_OUT_PATH}\gramps-${PRODUCT_VERSION}.exe"

# self ensure we don't have a corrupted file
CRCCheck on
# don't allow installation into C:\ directory
AllowRootDirInstall false

!include "WordFunc.nsh"
!include nsDialogs.nsh
!insertmacro StrFilter

# adds an XP manifest
XPStyle on
# self ensure we don't have a corrupted file
CRCCheck on

# splash, header graphics (same for both!)
!define MUI_HEADERIMAGE
#!define MUI_HEADERIMAGE_BITMAP "win.bmp"
#!define MUI_WELCOMEFINISHPAGE_BITMAP "nsis-splash.bmp"


; MUI 1.67 compatible ------
!include "MUI2.nsh"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON        "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON      "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

Var PythonPath
Var PythonExe 

;------------ Pages
; Welcome page
!insertmacro MUI_PAGE_WELCOME

PageEx directory 
    ;!insertmacro MUI_HEADER_TEXT "page title" " sub title"
    DirVar $PythonPath
    PageCallbacks skipPythonPathDialog "" processAfterPythonDialog
    Caption ": Python installation directory"
    ;SubCaption "This is the best I can be"
    #DirText [text] [subtext] [browse_button_text] [browse_dlg_text]
    DirText "Installer cannot find a python installation, python is needed for GRAMPS to run.$\n$\nIf python is already installed please select the location of python below, otherwise cancel the installation and install python before proceeding.$\n$\nObtain Python from http:\\www.python.org" "Select location of python" "" "Browse to location python is installed"
PageExEnd
 ;Custom page - for dependancy checking
Page custom DependenciesPageFunction DependenciesPageLeave
; License page
!insertmacro MUI_PAGE_LICENSE "${GRAMPS_BUILD_PATH}\COPYING"
; Component Page
;!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\NEWS.TXT"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Greek"

; MUI end ------

 Function skipPythonPathDialog
     ; Search for pythonw.exe on the path (returns the full path + exe)
    SearchPath $3 pythonw.exe
    IfFileExists $3 HavePython 0
    ; Handle the case where python is installed but not on the path - So check Registry keys

    ; reg key (Python version 2.7)
    ReadRegStr $3 HKLM 'Software\Python\PythonCore\2.7\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0

    ; reg key (Python version 2.6)
    ReadRegStr $3 HKLM 'Software\Python\PythonCore\2.6\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    
    ; reg key (Python version 2.5)
    ReadRegStr $3 HKLM 'Software\Python\PythonCore\2.5\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython 0
    
    ; reg key (Python version 2.4)
    ReadRegStr $3 HKLM 'Software\Python\PythonCore\2.4\InstallPath' ""
    StrCpy $3 "$3pythonw.exe"  ; append "pythonw.exe"
    IfFileExists $3 HavePython NoPython
    
    HavePython:
        StrCpy $PythonExe $3
        Call TestDependancies
        Abort
    NoPython: ; show the dialog querying the path
 FunctionEnd

Function processAfterPythonDialog
    StrCpy $PythonExe "$PythonPath\pythonw.exe"
    IfFileExists $PythonExe GotPython 0
        MessageBox MB_OK "Sorry cannot find pythonw.exe at $PythonPath$\n$\nPlease re-enter a valid python path"
        Abort
    GotPython:
        Call TestDependancies
FunctionEnd
; fileassoc.nsh
; File association helper macros
; Written by Saivert
;
; Features automatic backup system and UPDATEFILEASSOC macro for
; shell change notification.
;
; |> How to use <|
; To associate a file with an application so you can double-click it in explorer, use
; the APP_ASSOCIATE macro like this:
;
;   Example:
;   !insertmacro APP_ASSOCIATE \
;      "txt" \
;      "myapp.textfile" \
;      "myapp tiny description" \
;     "$INSTDIR\myapp.exe,0" \
;     "Open with myapp" \
;     "$INSTDIR\myapp.exe $\"%1$\""
;
; Never insert the APP_ASSOCIATE macro multiple times, it is only ment
; to associate an application with a single file and using the
; the "open" verb as default. To add more verbs (actions) to a file
; use the APP_ASSOCIATE_ADDVERB macro.
;
;   Example:
;   !insertmacro APP_ASSOCIATE_ADDVERB "myapp.textfile" "edit" "Edit with myapp" \
;     "$INSTDIR\myapp.exe /edit $\"%1$\""
;
; To have access to more options when registering the file association use the
; APP_ASSOCIATE_EX macro. Here you can specify the verb and what verb is to be the
; standard action (default verb).
;
; And finally: To remove the association from the registry use the APP_UNASSOCIATE
; macro. Here is another example just to wrap it up:
;   !insertmacro APP_UNASSOCIATE "txt" "myapp.textfile"
;
; |> Note <|
; When defining your file class string always use the short form of your application title
; then a period (dot) and the type of file. This keeps the file class sort of unique.
;   Examples:
;   Winamp.Playlist
;   NSIS.Script
;   Photoshop.JPEGFile
;
; |> Tech info <|
; The registry key layout for a file association is:
; HKEY_CLASSES_ROOT
;     <applicationID> = <"description">
;         shell
;             <verb> = <"menu-item text">
;                 command = <"command string">
;

!macro APP_ASSOCIATE EXT FILECLASS DESCRIPTION ICON COMMANDTEXT COMMAND
  ; Backup the previously associated file class
  ReadRegStr $R0 HKCR ".${EXT}" ""
  WriteRegStr HKCR ".${EXT}" "${FILECLASS}_backup" "$R0"

  WriteRegStr HKCR ".${EXT}" "" "${FILECLASS}"

  WriteRegStr HKCR "${FILECLASS}" "" `${DESCRIPTION}`
  WriteRegStr HKCR "${FILECLASS}\DefaultIcon" "" `${ICON}`
  WriteRegStr HKCR "${FILECLASS}\shell" "" "open"
  WriteRegStr HKCR "${FILECLASS}\shell\open" "" `${COMMANDTEXT}`
  WriteRegStr HKCR "${FILECLASS}\shell\open\command" "" `${COMMAND}`
!macroend

!macro APP_ASSOCIATE_EX EXT FILECLASS DESCRIPTION ICON VERB DEFAULTVERB SHELLNEW COMMANDTEXT COMMAND
  ; Backup the previously associated file class
  ReadRegStr $R0 HKCR ".${EXT}" ""
  WriteRegStr HKCR ".${EXT}" "${FILECLASS}_backup" "$R0"

  WriteRegStr HKCR ".${EXT}" "" "${FILECLASS}"
  StrCmp "${SHELLNEW}" "0" +2
  WriteRegStr HKCR ".${EXT}\ShellNew" "NullFile" ""

  WriteRegStr HKCR "${FILECLASS}" "" `${DESCRIPTION}`
  WriteRegStr HKCR "${FILECLASS}\DefaultIcon" "" `${ICON}`
  WriteRegStr HKCR "${FILECLASS}\shell" "" `${DEFAULTVERB}`
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}" "" `${COMMANDTEXT}`
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}\command" "" `${COMMAND}`
!macroend

!macro APP_ASSOCIATE_ADDVERB FILECLASS VERB COMMANDTEXT COMMAND
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}" "" `${COMMANDTEXT}`
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}\command" "" `${COMMAND}`
!macroend

!macro APP_ASSOCIATE_REMOVEVERB FILECLASS VERB
  DeleteRegKey HKCR `${FILECLASS}\shell\${VERB}`
!macroend


!macro APP_UNASSOCIATE EXT FILECLASS
  ; Backup the previously associated file class
  ReadRegStr $R0 HKCR ".${EXT}" `${FILECLASS}_backup`
  WriteRegStr HKCR ".${EXT}" "" "$R0"

  DeleteRegKey HKCR `${FILECLASS}`
!macroend

!macro APP_ASSOCIATE_GETFILECLASS OUTPUT EXT
  ReadRegStr ${OUTPUT} HKCR ".${EXT}" ""
!macroend


; !defines for use with SHChangeNotify
!ifdef SHCNE_ASSOCCHANGED
!undef SHCNE_ASSOCCHANGED
!endif
!define SHCNE_ASSOCCHANGED 0x08000000
!ifdef SHCNF_FLUSH
!undef SHCNF_FLUSH
!endif
!define SHCNF_FLUSH        0x1000

!macro UPDATEFILEASSOC
; Using the system.dll plugin to call the SHChangeNotify Win32 API function so we
; can update the shell.
  System::Call "shell32::SHChangeNotify(i,i,i,i) (${SHCNE_ASSOCCHANGED}, ${SHCNF_FLUSH}, 0, 0)"
!macroend

;EOF

Section "File Association" FileAssoc
SectionIn 1 3
# depends on FileAssoc.nsh, by Saivert (http://nsis.sourceforge.net/FileAssoc)

    # .grdb
    !insertmacro APP_ASSOCIATE \
    "grdb" \
    "application/x-gramps-database" \
    "GRAMPS database file" \
    "$INSTDIR\images\ped24.ico" \
    "Open with GRAMPS" \
    "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

    # .gramps
    !insertmacro APP_ASSOCIATE \
    "gramps" \
    "application/x-gramps-file" \
    "GRAMPS application file" \
    "$INSTDIR\images\ped24.ico" \
    "Open with GRAMPS" \
    "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

    # .gpkg
    !insertmacro APP_ASSOCIATE \
    "gpkg" \
    "application/x-gramps-package" \
    "GRAMPS package file" \
    "$INSTDIR\images\ped24.ico" \
    "Open with GRAMPS" \
    "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

    # .ged
    !insertmacro APP_ASSOCIATE \
    "ged" \
    "application/x-gramps-gedcom" \
    "GEnealogical Data COMmunication (GEDCOM) file" \
    "$INSTDIR\images\ped24.ico" \
    "Open with GRAMPS" \
    "$\"$3$\" $\"$INSTDIR\gramps.py$\" $\"%1$\""

SectionEnd



#Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
#OutFile ${GRAMPS_OUT_PATH}\gramps-${GRAMPS_VERSION}.exe
# default install path
InstallDir "$PROGRAMFILES\Gramps"
ShowInstDetails show
ShowUnInstDetails show

Function .onInit
    !insertmacro MUI_LANGDLL_DISPLAY

    SetOutPath $TEMP
    
    # default install directory ($INSTDIR)
    StrCpy $INSTDIR $PROGRAMFILES\gramps
    Call WarnSVNVersion
    Call RemovePrevious ;Move to a page leave function
    #  set our installed directory to the same as last version?
FunctionEnd

Var PythonVerText
Var GTKVerText
Var pyGTKVerText
Var GObjectVerText
Var CairoVerText

!insertmacro WordFind2X

Function TestDependancies
    SetOutPath $TEMP
    
    File test_dependencies.py
   
    nsExec::ExecToStack   '"$PythonExe" $TEMP\test_dependencies.py'
    Pop $0 # return value/error/timeout
    Pop $1 # printed text, up to ${NSIS_MAX_STRLEN}    
    ;                delim1     delim2  << Grab the text between delim1 and delim2
    ${WordFind2X} $1 "python:"   ";"   "+1" $PythonVerText
    ${WordFind2X} $1 "gtk++:"    ";"   "+1" $GTKVerText
    ${WordFind2X} $1 "pygtk:"    ";"   "+1" $pyGTKVerText
    ${WordFind2X} $1 "gobject:"  ";"   "+1" $GObjectVerText
    ${WordFind2X} $1 "cairo:"    ";"   "+1" $CairoVerText
    
;    MessageBox MB_OK "python: $PythonVerText $\ngtk++: $GTKVerText $\npygtk: $pyGTKVerText$\ngobject: $GObjectVerText$\ncario: $CairoVerText"
FunctionEnd

Function WriteGrampsLauncher
    SetOutPath $TEMP
    
    File make_launcher.py
    nsExec::ExecToStack   '"$PythonExe" $TEMP\make_launcher.py'
    Pop $0 # return value/error/timeout
    Pop $1 # printed text, up to ${NSIS_MAX_STRLEN}        
FunctionEnd


LangString PAGE_TITLE ${LANG_ENGLISH} "Summary of GRAMP's Dependencies"
LangString PAGE_SUBTITLE ${LANG_ENGLISH} ""
Var Dialog
Var Label

Var PythonVerTextHnd
Var GTKVerTextHnd
Var pyGTKVerTextHnd
Var GObjectVerTextHnd
Var CairoVerTextHnd

Var GTKDetailsBtn
Var pyGTKDetailsBtn
Var GObjectDetailsBtn
Var CairoDetailsBtn

Var PythonText
Var GTKText
Var PyGTKText
Var GObjectText
Var CairoText

!include LogicLib.nsh

Function DependenciesPageFunction
    !insertmacro MUI_HEADER_TEXT $(PAGE_TITLE) $(PAGE_SUBTITLE)
    nsDialogs::Create  /NOUNLOAD 1018 
    Pop $Dialog
    ${If} $Dialog == error
        Abort
    ${EndIf}
    
    SetOutPath $TEMP
    
    ;TODO: Handle case of non-compatible python versions? (i.e. <2.5.1, >= 3.0)
    
    ${If} $Dialog == error
        Abort
    ${EndIf}
    ${NSD_CreateLabel} 0 0 100% 12u "GRAMPS relies on the software listed below which must be installed first."
    Pop $Label

    ${NSD_CreateLabel} 10u 13u 45% 8u "Python version ${MIN_PYTHON_VERSION} or above............" 
    Pop $PythonText

    ${NSD_CreateLabel} 10u 23u 45% 8u "GTK Version ${MIN_GTK_VERSION} or above............." 
    Pop $GTKText

    ${NSD_CreateLabel} 10u 33u 45% 8u "pygtk version ${MIN_PYGTK_VERSION} or above............." 
    Pop $PyGTKText

    ${NSD_CreateLabel} 10u 43u 45% 8u "pygobject version ${MIN_GOBJECT_VERSION} or above........." 
    Pop $GObjectText

    ${NSD_CreateLabel} 10u 53u 45% 8u "pycairo version ${MIN_CAIRO_VERSION} or above............" 
    Pop $CairoText
    
    ; glade == do we have it?, do we need to test it?
    
    ${NSD_CreateLabel} 49% 13u 30% 8u $PythonVerText #""
    Pop $PythonVerTextHnd
    ${NSD_CreateLabel} 49% 23u 30% 8u $GTKVerText #""
    Pop  $GTKVerTextHnd
    ${NSD_CreateLabel} 49% 33u 30% 8u $pyGTKVerText #""
    Pop  $pyGTKVerTextHnd
    ${NSD_CreateLabel} 49% 43u 30% 8u $GObjectVerText #""
    Pop  $GObjectVerTextHnd
    ${NSD_CreateLabel} 49% 53u 30% 8u $CairoVerText #""
    Pop $CairoVerTextHnd

    ;   # set background color to white and text color to red
    ; SetCtlColors $R0 FFFFFF FF0000
    ; Colors should be set in hexadecimal RGB format, like HTML but without the #.
    ;For parameters that are treated as numbers, use decimal (the number) 
    ;or hexadecimal (with 0x prepended to it, i.e. 0x12345AB), or octal (numbers beginning with a 0 and no x).
    ; SetCtlColors hwnd [/BRANDING] [text_color] [transparent|bg_color]
    ;SetCtlColors $CairoText   0x008000 "${MUI_BGCOLOR}" #0x80FFFF #'0x808080' '0x8F8F80'

    ;To make the control transparent specify "transparent" as the background color value. You can also specify /BRANDING with or without text color and background color to make the control completely gray (or any other color you choose). This is used by the branding text control in the MUI.

    ;FindWindow $0 "#32770" "" $HWNDPARENT
    ;GetDlgItem $0 $0 1006
    ;SetCtlColors $0 0xFF0000 0x00FF00
    ;Warning: setting the background color of check boxes to "transparent" may not function properly when using XPStlye on. The background may be completely black, instead of transparent, when using certain Windows themes.

    ;${VersionCompare} "[Version1]" "[Version2]" $var
    ;        "[Version1]"        ; First version
    ;        "[Version2]"        ; Second version
    ;        $var                ; Result:
    ;                            ;    $var=0  Versions are equal
    ;                            ;    $var=1  Version1 is newer
    ;                            ;    $var=2  Version2 is newer

    ${StrFilter} $PythonVerText "1"  "." "" $R3    
    
    ${VersionCompare} $R3 ${MIN_PYTHON_VERSION} $R5
    ;MessageBox MB_OK "R5 = $R5 $\nPython Ver=$PythonVerText $\nR3=$R3 $\nMIN=${MIN_PYTHON_VERSION}"
    ${If} $R5 == 2 ;
        ; Set color to indicate an error
        SetCtlColors $PythonVerTextHnd   0xFF0000 "transparent"#"${MUI_BGCOLOR}"   
    ${Else}
        SetCtlColors $PythonVerTextHnd   0x00CC00 "transparent"#"${MUI_BGCOLOR}"   
    ${EndIf}

    ; SetCtlColors hwnd [/BRANDING] [text_color] [transparent|bg_color]
    ${StrFilter} $GTKVerText "1"  "." "" $R3    
    ${VersionCompare} $R3 ${MIN_GTK_VERSION} $R5
    ;MessageBox MB_OK "R5 = $R5 $\nGTK Ver=$1 $\nR3=$R3 $\nMIN=${MIN_GTK_VERSION}"
    
    ${If} $R5 == 2 ;
        ; Set color to indicate an error
        SetCtlColors $GTKVerTextHnd   0xFF0000 "transparent"#"${MUI_BGCOLOR}"   
        ${NSD_CreateButton} 80% 22u 12% 10u "Details"
        Pop $GTKDetailsBtn
        ;${NSD_OnClick} control_HWND function_address
        ${NSD_OnClick} $GTKDetailsBtn GTKBtnCallback
    ${Else}
        SetCtlColors $GTKVerTextHnd   0x00CC00 "transparent"#"${MUI_BGCOLOR}"   
    ${EndIf}

    
    ${StrFilter} $pyGTKVerText "1"  "." "" $R3    
    ${VersionCompare} $R3 ${MIN_PYGTK_VERSION} $R5
    ;MessageBox MB_OK "R5 = $R5 $\npyGTK Ver=$1 $\nR3=$R3 $\nMIN=${MIN_PYGTK_VERSION}"
    ${If} $R5 == 2 ;
        ; Set color to indicate an error
        SetCtlColors $pyGTKVerTextHnd   0xFF0000 "transparent"#"${MUI_BGCOLOR}"   
        ${NSD_CreateButton} 80% 32u 12% 10u "Details"
        Pop $pyGTKDetailsBtn
        ;${NSD_OnClick} control_HWND function_address
        ${NSD_OnClick} $pyGTKDetailsBtn pyGTKBtnCallback
    ${Else}
        SetCtlColors $pyGTKVerTextHnd   0x00CC00 "transparent"#"${MUI_BGCOLOR}"   
    ${EndIf}

    
    ${StrFilter} $GObjectVerText "1"  "." "" $R3    
    ${VersionCompare} $R3 ${MIN_GOBJECT_VERSION} $R5
    ;MessageBox MB_OK "R5 = $R5 $\nGObjectVer Ver=$1 $\nR3=$R3 $\nMIN=${MIN_GOBJECT_VERSION}"
    ${If} $R5 == 2 ;
        ; Set color to indicate an error
        SetCtlColors $GObjectVerTextHnd   0xFF0000 "transparent"#"${MUI_BGCOLOR}"   
        ${NSD_CreateButton} 80% 42u 12% 10u "Details"
        Pop $GObjectDetailsBtn
        ;${NSD_OnClick} control_HWND function_address
        ${NSD_OnClick} $GObjectDetailsBtn GObjectBtnCallback
        
    ${Else}
        SetCtlColors $GObjectVerTextHnd   0x00CC00 "transparent"#"${MUI_BGCOLOR}"   
    ${EndIf}
    
    ${StrFilter} $CairoVerText "1"  "." "" $R3    
    ${VersionCompare} $R3 ${MIN_CAIRO_VERSION} $R5
    ;MessageBox MB_OK "R5 = $R5 $\nCario Ver=$1 $\nR3=$R3 $\nMIN=${MIN_CAIRO_VERSION}"
    ${If} $R5 == 2 ;
        ; Set color to indicate an error
        SetCtlColors $CairoVerTextHnd   0xFF0000 "transparent"#"${MUI_BGCOLOR}"   
        ${NSD_CreateButton} 80% 52u 12% 10u "Details"
        Pop $CairoDetailsBtn
        ;${NSD_OnClick} control_HWND function_address
        ${NSD_OnClick} $CairoDetailsBtn CairoBtnCallback
    ${Else}
        SetCtlColors $CairoVerTextHnd   0x00CC00 "transparent"#"${MUI_BGCOLOR}"   
    ${EndIf}

    nsDialogs::Show
    
FunctionEnd

Function DependenciesPageLeave
    ;MessageBox MB_OK "Leaving Dependancies Page"
FunctionEnd

Section "MainSection" SEC01
    Call WarnDirExists

    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer
#  File "${GRAMPS_BUILD_PATH}\gramps.py"
    SetOverwrite try
    #File /r ${GRAMPS_BUILD_PATH}\src\*.*
    File /r "${GRAMPS_BUILD_PATH}\*.*"
    WriteRegStr HKLM "SOFTWARE\${PRODUCT_NAME}" "" "$INSTDIR"
    WriteRegStr HKLM "SOFTWARE\${PRODUCT_NAME}" "version" ${PRODUCT_VERSION}
    Call WriteGrampsLauncher
SectionEnd



Function GTKBtnCallback
    Pop $1
    MessageBox MB_OK|MB_ICONEXCLAMATION "The GTK package needed for GRAMPS to run was not found.$\n Please install this package and run the installer again. $\n$\nGTK+ => ${MIN_GTK_VERSION} can be downloaded from http://gladewin32.sourceforge.net/"
FunctionEnd

Function pyGTKBtnCallback
    Pop $1
    MessageBox MB_OK|MB_ICONEXCLAMATION "The pyGTK package needed for GRAMPS to run was not found.$\n Please install this package and run the installer again. $\n$\npyGTK => ${MIN_PYGTK_VERSION} can be downloaded from http://www.pygtk.org/downloads.html"
FunctionEnd

Function GObjectBtnCallback
    Pop $1
    MessageBox MB_OK|MB_ICONEXCLAMATION "The pyObject package needed for GRAMPS to run was not found.$\n Please install this package and run the installer again. $\n$\npyObject => ${MIN_GOBJECT_VERSION} can be downloaded from http://www.pygtk.org/downloads.html"
FunctionEnd

Function CairoBtnCallback
    Pop $1
    MessageBox MB_OK|MB_ICONEXCLAMATION "The Cairo package needed for GRAMPS to run was not found.$\n Please install this package and run the installer again. $\n$\nCairo => ${MIN_CAIRO_VERSION} can be downloaded from http://www.pygtk.org/downloads.html"
FunctionEnd

Function RemovePrevious
    #check if gramps exists in registry
    ClearErrors
    Var /GLOBAL PreviousPath
    ReadRegStr $PreviousPath HKLM "SOFTWARE\${PRODUCT_NAME}" ""
    # do some tests to find an installed version
    ifErrors NoPreviousVersion
    #upgrade of a family tree from 3.1 to 3.2 needs to happen via export to a gramps-xml file.  Other users (linux, Win XP, ...)
    #have not indicated such problems, but doing a backup to gramps-xml before upgrade is _always_ the wisest action.
        MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION  \
        "Backup family trees BEFORE upgrading GRAMPS.$\n$\n \
        To ensure you don't experience data loss make sure you $\n \
        backup your family trees using Gramps XML format $\n$\n \
        Click 'Cancel to abort installation or 'OK' to proceed." IDCANCEL Exit IDOK Proceed
    Exit:
        Abort
    Proceed:
        IfFileExists $PreviousPath\uninstall.exe 0 NoPreviousVersion #Check uninstall.exe from previous version exists on HD
        Var /GLOBAL PreviousVersion
        ReadRegStr $PreviousVersion HKLM "SOFTWARE\${PRODUCT_NAME}" "Version"
        #  query OK to delete old version
        MessageBox MB_OKCANCEL|MB_ICONQUESTION|MB_DEFBUTTON2 \
        "${PRODUCT_NAME} $PreviousVersion is already installed$\n$\nClick 'OK' to uninstall previous version or 'Cancel' to install over the top of current installation" \
        IDCANCEL NoPreviousVersion
        #  uninstall old version
        CopyFiles $PreviousPath\uninstall.exe $TEMP
        ExecWait '"$TEMP\uninstall.exe" _?=$PreviousPath' $0
        StrCpy $INSTDIR $PreviousPath #set the previous path as the default install path <= worth while or not?
        ;DetailPrint "uninstaller set error level $0"
    NoPreviousVersion:
FunctionEnd

Function WarnDirExists
    # warn if dir already exists
    IfFileExists $INSTDIR\*.* DirExists DirExistsOK
    DirExists:
    MessageBox MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2 \
        "Install over existing installation?" \
        IDYES DirExistsOK
    Quit
    DirExistsOK:
FunctionEnd

Function WarnSVNVersion
    ;${StrFilter} "[string]" "[options]" "[symbols1]" "[symbols2]" $var
    ;"[string]" ;[string]
    ; input string
    ;
    ;"[options]" ;[+|-][1|2|3|12|23|31][eng|rus]
    ; + : convert string to uppercase
    ; - : convert string to lowercase
    ; 1 : only Digits
    ; 2 : only Letters
    ; 3 : only Special
    ; 12 : only Digits + Letters
    ; 23 : only Letters + Special
    ; 31 : only Special + Digits
    ; eng : English symbols (default)
    ; rus : Russian symbols
    ;
    ;"[symbols1]" ;[symbols1]
    ; symbols include (not changeable)
    ;
    ;"[symbols2]" ;[symbols2]
    ; symbols exclude
    ;
    ;$var ;output (result)
    ${StrFilter} "${PRODUCT_VERSION}" "2"  "" "" $R3
    ;MessageBox MB_OK "$R3 was found"
    StrCmp $R3 "SVN" SVNVersion 0
    StrCmp $R3 "SVNM" SVNVersion 0
    StrCmp $R3 "beta" BetaVersion ContinueInstall
    SVNVersion:
    MessageBox MB_YESNO|MB_ICONEXCLAMATION|MB_DEFBUTTON2 \
        "${PRODUCT_NAME} ${PRODUCT_VERSION} is a development ($R3) version$\n$\nAre you sure you want to proceed with installation?" \
        IDYES ContinueInstall
    Quit
    BetaVersion:
    MessageBox MB_YESNO|MB_ICONEXCLAMATION|MB_DEFBUTTON2 \
        "${PRODUCT_NAME} ${PRODUCT_VERSION} is a $R3 version$\n$\nAre you sure you want to proceed with installation?" \
        IDYES ContinueInstall
    Quit
    ContinueInstall:
FunctionEnd

Section -AdditionalIcons
    SetOutPath $INSTDIR
    WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    
    IfFileExists '$INSTDIR\gramps_locale.cmd' 0 NoLocaleFile
    # $3 should contain the path to python, .. then pass gramps.py as an argument
    #CreateShortCut link.lnk target.file [parameters [icon.file [icon_index_number [start_options[keyboard_shortcut [description]]]]]]    
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME} (locale) ${PRODUCT_VERSION}.lnk" CMD "/C $\"$INSTDIR\gramps_locale.cmd$\"" "$INSTDIR\images\ped24.ico" "0" "" "" "GRAMPS"
    NoLocaleFile:
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME} ${PRODUCT_VERSION}.lnk" "$3" "$\"$INSTDIR\gramps.py$\"" "$INSTDIR\images\ped24.ico" "0" "" "" "GRAMPS"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

Section -Post
    WriteUninstaller "$INSTDIR\uninstall.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
    HideWindow
    MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
    Abort
FunctionEnd


Function un.StartMenu
    IfFileExists "$SMPROGRAMS\GRAMPS" 0 unStartMenuFine
    RMDir /r "$SMPROGRAMS\GRAMPS\"
    unStartMenuFine:
FunctionEnd

Function un.Desktop
    IfFileExists "${DESKTOP_LINK}" 0 unNoDesktop
    Delete "${DESKTOP_LINK}"
    unNoDesktop:
FunctionEnd

Section Uninstall
    Delete "$INSTDIR\${PRODUCT_NAME}.url"
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR"
    Call un.StartMenu
    Call un.Desktop
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"

    DeleteRegKey HKLM "SOFTWARE\${PRODUCT_NAME}"
    SetAutoClose true
SectionEnd
