Name:           webapp-manager
Version:        1.1.9
Release:        1%{?dist}
Summary:        risiOS's fork of webapp-manager

License:        GPL v3
URL:            https://github.com/risiOS/webapp-manager
Source0:        https://github.com/risiOS/webapp-manager/archive/refs/heads/master.tar.gz
Source1:        https://raw.githubusercontent.com/risiOS/webstream/main/__main__.py

BuildArch:	noarch
BuildRequires:  python3-devel
Requires:	python
Requires:	python3-gobject
Requires:	python3-beautifulsoup4
Requires:	python3-configobj
Requires:	python3-pillow
Requires:	python3-setproctitle
Requires:	python3-tldextract
Requires:	xapps

%description
A fork of the Linux Mint web app manager with a store for web apps.

%prep
%autosetup -n %{name}-master

%build
%install
mkdir -p %{buildroot}%{_exec_prefix}
mkdir -p %{buildroot}%{python3_sitelib}
mkdir -p %{buildroot}%{python3_sitelib}/site-packages/

cp -a usr/bin %{buildroot}%{_bindir}
cp -a usr/lib %{buildroot}%{_libdir}
cp -a usr/share %{buildroot}%{_datadir}
cp -a etc %{buildroot}%{_sysconfdir}

# webstream
cp -a %{SOURCE1} %{buildroot}%{python3_sitelib}/webstream.py

%files
# %license add-license-file-here
# %doc add-docs-here
%{_sysconfdir}/xdg/menus/applications-merged/webapps.menu
%{_bindir}/webapp-manager
%{_libdir}/webapp-manager
%{_datadir}/applications/kde4/webapp-manager.desktop
%{_datadir}/applications/webapp-manager.desktop
%{_datadir}/desktop-directories/webapps-webapps.directory
%{_datadir}/glib-2.0/schemas/org.x.webapp-manager.gschema.xml
%{_datadir}/icons/hicolor/scalable/apps/webapp-default.svg
%{_datadir}/icons/hicolor/scalable/apps/webapp-manager.svg
%{_datadir}/icons/hicolor/scalable/categories/applications-webapps.svg
%{_datadir}/webapp-manager

# webstream
%{python3_sitelib}/webstream.py
%{python3_sitelib}/__pycache__/webstream.cpython-%{python3_version_nodots}.opt-1.pyc
%{python3_sitelib}/__pycache__/webstream.cpython-%{python3_version_nodots}.pyc

%changelog
* Tue Jul 13 2021 PizzaLovingNerd
- First spec file
