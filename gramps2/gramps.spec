%define ver      0.9.1
%define rel      rc1
%define prefix   /usr

Summary: Genealogical Research and Analysis Management Programming System.
Name: gramps
Version: %ver
Release: %rel
Copyright: GPL
Group: Applications/Genealogy
Source: http://download.sourceforge.net/gramps/gramps-%{ver}.tar.gz
BuildRoot: /var/tmp/%{name}-%{version}-root

URL: http://gramps.sourceforge.net

Requires: python >= 2.2
Requires: gnome-python2 >= 1.99
Requires: gnome-python2-gconf >= 1.99
Requires: gnome-python2-canvas >= 1.99
Requires: pygtk2 >= 1.99
Requires: pygtk2-libglade >= 1.99

BuildRequires: scrollkeeper >= 0.3.5
BuildRequires: automake >= 1.6
BuildRequires: autoconf >= 2.52

%description
gramps (Genealogical Research and Analysis Management Programming
System) is a GNOME based genealogy program supporting a Python
based plugin system.

%prep
%setup

%build
if [ ! -f configure ]; then
  CFLAGS="$MYCFLAGS" ./autogen.sh $MYARCH_FLAGS --prefix=%prefix
else
  CFLAGS="$MYCFLAGS" ./configure $MYARCH_FLAGS --prefix=%prefix
fi

make


%install
rm -rf $RPM_BUILD_ROOT

make GNOME_DATADIR=$RPM_BUILD_ROOT%{prefix}/share prefix=$RPM_BUILD_ROOT%{prefix} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)

%doc README COPYING TODO INSTALL COPYING-DOCS

%{prefix}/bin/gramps

%{_datadir}/gramps/gnome/help/gramps/C/*
%{_datadir}/gnome/apps/Applications/gramps.desktop
%{_datadir}/pixmaps/gramps.png
%{_datadir}/locale/*/LC_MESSAGES/gramps.mo

%{_datadir}/gramps/*.xpm
%{_datadir}/gramps/*.jpg
%{_datadir}/gramps/gramps.desktop
%{_datadir}/gramps/*.png
%{_datadir}/gramps/*.py
%{_datadir}/gramps/*.pyo
%{_datadir}/gramps/*.glade
%{_datadir}/gramps/*.so
%{_datadir}/gramps/docgen/*.py
%{_datadir}/gramps/docgen/*.pyo
%{_datadir}/gramps/filters/*.py
%{_datadir}/gramps/filters/*.pyo
%{_datadir}/gramps/plugins/*.py
%{_datadir}/gramps/plugins/*.pyo
%{_datadir}/gramps/plugins/*.glade
%{_datadir}/gramps/data/gedcom.xml
%{_datadir}/gramps/data/templates/*.tpkg
%{_datadir}/gramps/data/templates/*.xml
%{_datadir}/gramps/example/*
%{_datadir}/omf/gramps

%{prefix}/man/man1/gramps.1*


%post
if which scrollkeeper-update>/dev/null 2>&1; then scrollkeeper-update -q -o %{_datadir}/omf/gramps; fi

%postun
if which scrollkeeper-update>/dev/null 2>&1; then scrollkeeper-update -q; fi
 
%changelog
* Mon Mar 24 2003 Alex Roitman <shura@alex.neuro.umn.edu>
- update scrollkeeper dependencies and add post and postun to enable install on a machine without scrollkeeper
* Fri Jun 14 2002 Donald Peterson <dpeterso@engr.ors.edu>
- add scrollkeeper dependencies and some file cleanup
