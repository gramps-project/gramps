@echo off
rem
rem Filename: gramps-build.bat
rem Author:   Steve Hall  [ digitect dancingpaper com ]
rem Date:     (See timestamp in :CHOOSE)
rem
rem Documentation
rem License {{{1
rem --------
rem This program is free software;  you  can  redistribute  it  and/or
rem modify it under the terms of the GNU  General  Public  License  as
rem published by the Free Software Foundation; either version 2 of the
rem License, or (at your option) any later version.
rem [ http://www.gnu.org/licenses/gpl.html ]
rem
rem This program is distributed in the hope that it  will  be  useful,
rem but WITHOUT ANY WARRANTY; without even  the  implied  warranty  of
rem MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See  the  GNU
rem General Public License for more details.
rem
rem You should have received a copy of the GNU General Public  License
rem along with this program;  if  not,  write  to  the  Free  Software
rem Foundation,  Inc.,  59  Temple  Place  -  Suite  330,  Boston,  MA
rem 02111-1307, USA.
rem

rem Usage {{{1
rem ------
rem This script automates the build process and creation of an
rem installer as much as possible, downloading sources and making
rem assumptions where necessary. To use it, the following are
rem required:
rem
rem o Windows NT/2K/XP (we no longer support 95/98/ME)
rem
rem o These GNU tools on path:
rem     - gzip/gunzip
rem     - tar (GNU version >= 1.13.10)
rem     - sed
rem     - wget
rem
rem o The Nullsoft Installer.
rem
rem o Adjust the variables in :ENVIRONMENT (below) to fit your
rem   preferences and installation conditions.
rem

rem 1}}}
rem Initialization
rem Version and Personal Environment (*** FIX ME!! ***) {{{1
echo -----------------------------------------------------------------
echo Version and Personal environment...
echo.

rem *****************************************************
rem *  MAKE ALL ADJUSTMENTS IN THIS SECTION!            *

rem version (also used for location
	set VERSION=3
	set VERSIONSUB=0
	set VERSIONPT=3
	set VERSIONBUILD=1

rem path to Nullsoft Installer (NSIS)
	set NSIS=C:\PROGRA~1\NSIS
rem path to Nullsoft customized files
	set CUSTOM=C:\DOCUME~1\halls\_seh\devel\gramps

rem path to Python
	if "%PYTHONPATH%"=="" echo   Manually setting $PYTHONPATH...
	if "%PYTHONPATH%"=="" set PYTHONPATH=C:\Python25

rem *  END OF ADJUSTMENTS SECTION                        *
rem ******************************************************

rem Initial Environment {{{1
echo -----------------------------------------------------------------
echo Initial environment...
echo.

rem force Win NT/2K/XP
	if not "%OS%"=="Windows_NT" echo  Windows NT/2K/XP required, unable to continue.
	if not "%OS%"=="Windows_NT" goto QUIT

rem program name
	set PROG=gramps
rem save system PATH
	set PATHORIG=%PATH%
rem set build path (location of this file and tarball)
	set BUILDPATH=%CD%
rem cat for general filename
	set VERSIONNAME=%PROG%-%VERSION%.%VERSIONSUB%.%VERSIONPT%

rem Verify {{{1
echo -----------------------------------------------------------------
echo Verifying environment and utilities available...
echo.

echo   %%BUILDPATH%%         : %BUILDPATH%
echo   %%VERSIONNAME%%       : %VERSIONNAME%
echo   %%NSIS%%              : %NSIS%
echo   %%CUSTOM%%         : %CUSTOM%

rem date
	for /F "TOKENS=1* DELIMS= " %%A in ('date/t') do set MYDAYNAME=%%A
	for /F "TOKENS=2* DELIMS= " %%A in ('date/t') do set MYMDY=%%A
	for /f "TOKENS=3* DELIMS=/" %%A in ('echo %MYMDY%') do set MYYEAR=%%A
	for /f "TOKENS=1* DELIMS=/" %%A in ('echo %MYMDY%') do set MYMONTH=%%A
	for /f "TOKENS=2* DELIMS=/" %%A in ('echo %MYMDY%') do set MYDAY=%%A
rem time
	for /F "TOKENS=1* DELIMS=:" %%A in ('time/t') do set MYHOUR=%%A
	for /F "TOKENS=2* DELIMS=: " %%A in ('time/t') do set MYMINUTE=%%A
echo   Date                : %MYYEAR%-%MYMONTH%-%MYDAY%
echo   Time                : %MYHOUR%:%MYMINUTE%
echo   Build version       : %VERSIONBUILD%
echo.

	set TRY=gzip.exe
	for %%A in (%TRY%) do set YES=%%~$PATH:A
	if "%YES%"=="" goto UTILHALT
echo   Found %TRY%...

	set TRY=gunzip.exe
	for %%A in (%TRY%) do set YES=%%~$PATH:A
	if "%YES%"=="" goto UTILHALT
echo   Found %TRY%...

	set TRY=sed.exe
	for %%A in (%TRY%) do set YES=%%~$PATH:A
	if "%YES%"=="" goto UTILHALT
echo   Found %TRY%...

	set TRY=tar.exe
	for %%A in (%TRY%) do set YES=%%~$PATH:A
	if "%YES%"=="" goto UTILHALT
echo   Found %TRY%...

	set TRY=wget.exe
	for %%A in (%TRY%) do set YES=%%~$PATH:A
	if "%YES%"=="" goto UTILHALT
echo   Found %TRY%...

echo.
	set /P CH=Continue? [Y/N]  
	if /I "%CH%"=="Y" goto CHOOSE

	:UTILHALT
	if "%YES%"=="" echo   Utility %TRY% not found on PATH, unable to continue.
echo.
echo Quitting...
echo.
	goto QUIT

rem }}}1
rem Procedures
rem CHOOSE {{{1
:CHOOSE
	cls
echo.
echo  ______________________________________________________________________________
echo  Updated: 2007-06-18 07:09:16-0400
echo.
echo   Please select a choice:
echo.
echo   [1] Clean build location
echo   [2] Extract source tarballs
echo   [3] Build source
echo   [4] Nullsoft Installer
echo.
echo   [R]emove existing installation
echo.
echo   [A]uto
echo   [Q]uit
echo.
echo  ______________________________________________________________________________
echo.

	:WinNT
	set /P CH=Please enter choice above...
	if /I "%CH%"=="Q" goto QUIT
	if /I "%CH%"=="A" goto AUTO
	if /I "%CH%"=="R" goto REMOVE
	if /I "%CH%"=="4" goto NSIS
	if /I "%CH%"=="3" goto BUILD
	if /I "%CH%"=="2" goto SOURCE
	if /I "%CH%"=="1" goto CLEAN
	goto WinNT

rem AUTO {{{1
:AUTO
echo -----------------------------------------------------------------
echo Setting Auto-Run...
echo.

	set RETURN=no

rem CLEAN {{{1
:CLEAN
echo -----------------------------------------------------------------
echo Cleaning up build location (removing all directories and files)
echo.

	if not exist %BUILDPATH%\%VERSIONNAME% echo   (Nothing to clean.)
	if exist %BUILDPATH%\%VERSIONNAME% rmdir /s /q %BUILDPATH%\%VERSIONNAME%

if not "%RETURN%"=="no" echo.
if not "%RETURN%"=="no" echo Build location cleaned. (Ctrl+C to quit)
if not "%RETURN%"=="no" pause
if not "%RETURN%"=="no" goto CHOOSE

rem SOURCE {{{1
:SOURCE
echo -----------------------------------------------------------------
echo Downloading and extracting source tarballs...
echo.

rem NOTE: tar -xzf does not always work

	:SOURCES
echo   %VERSIONNAME%.tar.gz...
	if exist "%VERSIONNAME%.tar" goto TARBALL
	if not exist "%VERSIONNAME%.tar.gz" echo.
	if not exist "%VERSIONNAME%.tar.gz" echo Tarball not found, downloading...
	if not exist "%VERSIONNAME%.tar.gz" echo.
	if not exist "%VERSIONNAME%.tar.gz" wget -c http://superb-east.dl.sourceforge.net/sourceforge/gramps/%VERSIONNAME%.tar.gz
	if not exist "%VERSIONNAME%.tar.gz" echo.
	if not exist "%VERSIONNAME%.tar.gz" echo Download failed, unable to continue.
	if not exist "%VERSIONNAME%.tar.gz" echo.
	if not exist "%VERSIONNAME%.tar.gz" goto CHOOSE
	if exist "%VERSIONNAME%.tar.gz" gunzip "%VERSIONNAME%.tar.gz"
echo   tarball unzipped.
	:TARBALL
	if not exist "%VERSIONNAME%.tar" echo.
	if not exist "%VERSIONNAME%.tar" echo Unable to continue, no tarball found.
	if not exist "%VERSIONNAME%.tar" echo.
	if not exist "%VERSIONNAME%.tar" goto CHOOSE
echo   extracting...
	tar -xvf %VERSIONNAME%.tar

if not "%RETURN%"=="no" echo.
if not "%RETURN%"=="no" echo Source tarballs unpacked. (Ctrl+C to quit)
if not "%RETURN%"=="no" pause
if not "%RETURN%"=="no" goto CHOOSE

rem BUILD {{{1
:BUILD
echo -----------------------------------------------------------------
echo Building...
echo.

rem TODO: This should happen on the user's machine, since the process
rem apparently embeds a number of paths into the result.

echo.
echo Translations...
echo.

rem TODO: Brian's script doesn't work for me...
rem     cd "%BUILDPATH%\%VERSIONNAME%"
rem     if exist "%CUSTOM%\grampsSetup.py" copy /Y "%CUSTOM%\grampsSetup.py" "%BUILDPATH%\%VERSIONNAME%"
rem     if exist "%CUSTOM%\grampsSetup.py" echo  Setting up language files (this could take a while)...
rem rem Use Brian's grampsSetup.py utility...
rem rem   switches:
rem rem   -r  :: release
rem rem   -c  :: compile
rem rem   -t  :: set up the language files
rem rem Note: we use only "-t", we don't want to compile
rem     if exist "%CUSTOM%\grampsSetup.py" python grampsSetup.py -t

echo.
echo  Setting up language files...
echo.
	cd "%BUILDPATH%\%VERSIONNAME%\po"
rem create the directories
	for %%A in (*.po) do if not exist lang\%%~nA\LC_MESSAGES mkdir lang\%%~nA\LC_MESSAGES
rem convert .po to gramps.mo (in directories)
	for %%A in (*.po) do %PYTHONPATH%\python %PYTHONPATH%\Tools\i18n\msgfmt.py -o lang\%%~nA\LC_MESSAGES\gramps.mo %%A & echo  processing language %%~nA...

echo.
echo  Attempting to update build level in const.py to "%VERSIONBUILD%"...
echo.
	cd "%BUILDPATH%\%VERSIONNAME%\src"
	sed -i -e "s/^\(version \s\+= \"%VERSION%\.%VERSIONSUB%\.%VERSIONPT%-\).\+\"/\1%VERSIONBUILD%\"/g" const.py
	rem ren sedDOSSUX const.py

if not "%RETURN%"=="no" echo.
if not "%RETURN%"=="no" echo Did we enjoy building?
if not "%RETURN%"=="no" pause
if not "%RETURN%"=="no" goto CHOOSE

rem NSIS {{{1
:NSIS
echo -----------------------------------------------------------------
echo Nullsoft Installer creation
echo.

if exist %NSIS%\CON goto NSISFOUND
	echo.
	echo   NSIS path not found. Unable to continue...
	pause
	goto CHOOSE
	:NSISFOUND

rem echo   copying customized NSIS files...
rem     if not exist "%BUILDPATH%\%VERSIONNAME%\nsis" mkdir "%BUILDPATH%\%VERSIONNAME%\nsis"
rem     copy /Y "%NSIS%\Contrib\Graphics\Icons\classic-install.ico" "%BUILDPATH%\%VERSIONNAME%\nsis\classic-install.ico"
rem     copy /Y "%NSIS%\Contrib\Graphics\Icons\classic-uninstall.ico" "%BUILDPATH%\%VERSIONNAME%\nsis\classic-uninstall.ico"
rem     copy /Y "%NSIS%\Contrib\Graphics\Header\win.bmp" "%BUILDPATH%\%VERSIONNAME%\nsis\win.bmp"
rem     if exist "%CUSTOM%\nsis-splash.bmp" copy /Y "%CUSTOM%\nsis-splash.bmp" "%BUILDPATH%\%VERSIONNAME%\nsis\nsis-splash.bmp"
rem     if exist "%CUSTOM%\nsis-checkboxes.bmp" copy /Y "%CUSTOM%\nsis-checkboxes.bmp" "%BUILDPATH%\%VERSIONNAME%\nsis\nsis-checkboxes.bmp"

rem TODO:
echo   copying temporary, should end up in next release (?)
	if not exist "%BUILDPATH%\%VERSIONNAME%\nsis\CON" mkdir "%BUILDPATH%\%VERSIONNAME%\nsis"
	if exist "%CUSTOM%\gramps.nsi" copy /Y "%CUSTOM%\gramps.nsi" /Y "%BUILDPATH%\%VERSIONNAME%\nsis\gramps.nsi"
	if exist "%CUSTOM%\ped24.ico" copy /Y "%CUSTOM%\ped24.ico" /Y "%BUILDPATH%\%VERSIONNAME%\src\images\ped24.ico"
	if exist "%CUSTOM%\gcheck.py" copy /Y "%CUSTOM%\gcheck.py" /Y "%BUILDPATH%\%VERSIONNAME%\nsis\gcheck.py"

echo   building installer...
	cd "%BUILDPATH%\%VERSIONNAME%\nsis"
	%NSIS%\makensis gramps.nsi

rem Open Windows Explorer to this directory
	explorer /e,"%BUILDPATH%\%VERSIONNAME%\nsis"

echo.
echo   Pausing... did we enjoy building the Nullsoft installer? (Ctrl+C to quit)
	pause
	goto CHOOSE

rem REMOVE {{{1
:REMOVE
rem this is NOT automatic
if "%RETURN%"=="no" goto CHOOSE

echo -----------------------------------------------------------------
echo Removing existing installation
echo.

echo   removing "%ProgramFiles%\gramps"
	if exist "%ProgramFiles%\gramps" rmdir /s /q "%ProgramFiles%\gramps"
echo   removing "%USERPROFILE%\Start Menu\Programs\GRAMPS"
	if exist "%USERPROFILE%\Start Menu\Programs\GRAMPS" rmdir /s /q "%USERPROFILE%\Start Menu\Programs\GRAMPS"
echo   removing "%TEMP%\gramps-install.ini"
	if exist "%TEMP%\gramps-install.ini" del "%TEMP%\gramps-install.ini"
echo   removing "%TEMP%\gcheck.py"
	if exist "%TEMP%\gcheck.py" del "%TEMP%\gcheck.py"

if not "%RETURN%"=="no" echo.
if not "%RETURN%"=="no" echo   Pausing... did we enjoy removing existing installation? (Ctrl+C to quit)
if not "%RETURN%"=="no" pause
if not "%RETURN%"=="no" goto CHOOSE

rem QUIT {{{1
:QUIT
echo.
echo Finished.
echo.

	cd "%BUILDPATH%"

rem clear variables
	set ARCHIVEDRIVE=
	set BUILDDRIVE=
	set BUILDPATH=
	set BUILDTYPE=
	set VERSION=
	set VERSIONNAME=
	set VERSIONSUB=
	set CH=
	set FNAME=
	set GCC=
	set LICENSEFILE=
	set MYDAY=
	set MYMONTH=
	set MYYEAR=
	set MYDAYNAME=
	set MDY=
	set NSIS=
	set CUSTOM=
rem set PATHORIG=
	set RETURN=
	set TRY=
	set YES=

rem reset path if backup exists
rem if "%PATHORIG%"=="" goto END
	set PATH=%PATHORIG%
	set PATHORIG=

rem 1}}}
:END
rem vim:foldmethod=marker
