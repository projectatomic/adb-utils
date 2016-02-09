%global commit0 e5af099977f1a533ea825fdfa48e31fbe9f74ab9
%global gittag0 GIT-TAG
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       adb-utils
Version:    1
Release:    2%{?dist}
Summary:    Installs the necessary utils/service files to support ADB/CDK

License:    GPL
URL:        https://github.com/projectatomic/%{name}
BuildArch:  noarch
Source0:    https://github.com/projectatomic/%{name}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
BuildRequires: systemd

%description
Includes the utils files and service files that are required for the running
specific service and directly including it to kickstart file.

%prep
%setup -q -n %{name}-%{commit0}

%install
%{__mkdir_p} %{buildroot}/opt/adb/openshift
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig/
%{__mkdir_p} %{buildroot}%{_unitdir}
%{__mkdir_p} %{buildroot}%{_bindir}

%{__install} -pm644 services/openshift/openshift.service \
%{buildroot}%{_unitdir}/openshift.service
%{__cp} services/openshift/openshift_option \
%{buildroot}%{_sysconfdir}/sysconfig/openshift_option
%{__cp} services/openshift/scripts/* %{buildroot}/opt/adb/openshift/
%{__cp} utils/* %{buildroot}/opt/adb/
ln -s /opt/adb/sccli.sh %{buildroot}%{_bindir}/sccli

%files
%{_sysconfdir}/sysconfig/openshift_option
%{_unitdir}/openshift.service
%{_bindir}/sccli
/opt/adb/
%doc LICENSE  README.rst

%changelog
* Tue Feb 09 2016 Praveen Kumar <kumarpraveen.nitdgp@gmail.com> 1-3
- Add sccli changes

* Fri Feb 05 2016 Praveen Kumar <kumarpraveen.nitdgp@gmail.com> 1-2
- Update to latest source 

* Mon Feb 01 2016 Praveen Kumar <kumarpraveen.nitdgp@gmail.com> 1-1
- Initial attemp to create a rpm
