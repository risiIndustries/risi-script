Name:           risi-script
Version:        1.0
Release:        1%{?dist}
Summary:        risiOS's way of giving GUIs to bash scripts

License:        GPL v3
URL:            https://github.com/risiOS/risi-script
Source0:        https://github.com/risiOS/risi-script/archive/refs/heads/main.tar.gz

BuildArch:	noarch

Requires: 	python
Requires:	python3-gobject

%description
Wraps around bash with simple yaml files and a library to create GUIs for them.

%package gtk
Summary:	Gtk client for reading risi-script files
Requires:	risi-script

%description
Gtk client for .risisc (.yml) risi script files

%prep
%autosetup -n %{name}-main

%build
%install
mkdir %{buildroot}%{_exec_prefix}

cp risi-script.py %{buildroot}%{_lib}/python3.10/site-packages
cp risi-script-run.py %{buildroot}%{_bindir}/risi-script-run
cp io.risi.script.gschema.xml %{_datadir}/glib-2.0/schemas
cp risi-script-gtk/__main__.py %{buildroot}%{_bindir}/risi-script-gtk
cp risi-script-gtk/risi-script-gtk.ui %{buildroot}%{_datadir}/risi-script-gtk/risi-script-gtk.ui

%files
# %license add-license-file-here
# %doc add-docs-here
%{_lib}/python3.10/site-packages/risi-script.py
%{_bindir}/risi-script-run
%{_datadir}/glib-2.0/schemas/io.risi.script.gschema.xml

%files gtk
%{_bindir}/risi-script-gtk
%{_datadir}/risi-script-gtk/risi-script-gtk.ui

%changelog
* Wed Feb 16 2022 PizzaLovingNerd
- First spec file

