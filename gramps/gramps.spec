%define ver      0.6.0
%define rel      1
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

Requires: python = 1.5.2
Requires: pygnome >= 1.0.53
Requires: pygnome-libglade
Requires: PyXML

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

%doc README COPYING TODO
%{prefix}/share/gnome/help/gramps-manual/C/*
%{prefix}/share/gnome/help/extending-gramps/C/*
%{prefix}/bin/gramps
%{prefix}/share/gnome/apps/Applications/gramps.desktop
%{prefix}/share/pixmaps/gramps.png
%{prefix}/share/locale/*/LC_MESSAGES/gramps.mo
%{prefix}/share/gramps/example/gedcom/*
%{prefix}/share/gramps/example/gramps/*
%{prefix}/share/gramps/*.py
%{prefix}/share/gramps/*.pyo
%{prefix}/share/gramps/*.so
%{prefix}/share/gramps/*.glade
%{prefix}/share/gramps/*.xpm
%{prefix}/share/gramps/*.jpg
%{prefix}/share/gramps/*.png
%{prefix}/share/gramps/filters/*.py
%{prefix}/share/gramps/filters/*.pyo
%{prefix}/share/gramps/plugins/*.py
%{prefix}/share/gramps/plugins/*.glade
%{prefix}/share/gramps/plugins/*.pyo

