Name:           risi-script
Version:        1.0
Release:        7%{?dist}
Summary:        risiOS's way of giving GUIs to bash scripts

License:        GPL v3
URL:            https://github.com/risiOS/risi-script
Source0:        https://github.com/risiOS/risi-script/archive/refs/heads/main.tar.gz

BuildArch:	noarch

BuildRequires:  python3-devel
Requires: 	python3
Requires:   python3-gobject

%description
Wraps around bash with simple yaml files and a library to create GUIs for them.

%package gtk
Summary:	Gtk client for reading risi-script files
Requires:	risi-script

%description gtk
Gtk client for .risisc (.yml) risi script files

%prep
%autosetup -n %{name}-main

%build
%install
mkdir -p %{buildroot}%{python3_sitelib}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/glib-2.0/schemas
mkdir -p %{buildroot}%{_datadir}/risi-script/scripts
mkdir -p %{buildroot}%{_datadir}/risi-script-gtk/
mkdir -p %{buildroot}%{_datadir}/mime/packages
mkdir -p %{buildroot}%{_datadir}/applications

install -m 0755 __main__.py %{buildroot}%{python3_sitelib}/risiscript.py
install -m 0755 risi-script-run.py %{buildroot}%{_bindir}/risi-script-run
cp io.risi.script.gschema.xml %{buildroot}%{_datadir}/glib-2.0/schemas
cp application-x-risisc.xml %{buildroot}%{_datadir}/mime/packages/application-x-risisc.xml

install -m 0755 risi-script-gtk/__main__.py %{buildroot}%{_bindir}/risi-script-gtk
cp risi-script-gtk/risi-script-gtk.ui %{buildroot}%{_datadir}/risi-script-gtk/risi-script-gtk.ui
cp risi-script-gtk/risi-script-gtk.desktop %{buildroot}%{_datadir}/applications

%files
# %license add-license-file-here
# %doc add-docs-here
%{_datadir}/risi-script
%{_datadir}/risi-script/scripts

%{python3_sitelib}/risiscript.py
%{python3_sitelib}/__pycache__/risiscript.cpython-%{python3_version_nodots}.opt-1.pyc
%{python3_sitelib}/__pycache__/risiscript.cpython-%{python3_version_nodots}.pyc
%{_bindir}/risi-script-run
%{_datadir}/glib-2.0/schemas/io.risi.script.gschema.xml
%{_datadir}/mime/packages/application-x-risisc.xml

%files gtk
%{_bindir}/risi-script-gtk
%{_datadir}/risi-script-gtk/risi-script-gtk.ui
%{_datadir}/applications/risi-script-gtk.desktop

%changelog
* Wed Feb 16 2022 PizzaLovingNerd
- First spec file

