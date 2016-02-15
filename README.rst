adb-utils
=========

Utility and Service scripts for the `Atomic-Developer-Bundle (ADB) <https://github.com/projectatomic/adb-atomic-developer-bundle>`_.

Steps to build the SRC RPM
--------------------------
* Create source tar ball

  spectool -g -R adb-utils.spec

* Build the SRPM for el7

  rpmbuild --define "_srcrpmdir $PWD" --define "dist .el7" -bs adb-utils.spec
