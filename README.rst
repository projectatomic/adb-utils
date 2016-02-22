adb-utils
=========

Utility and Service scripts for the `Atomic-Developer-Bundle (ADB) <https://github.com/projectatomic/adb-atomic-developer-bundle>`_.

adb-utils provides following content to ADB Vagrant box

* OpenShift as a service

  adb-utils uses a systemd service unit file to launch and setup a containerized version of OpenShift. With the systemd unit file, OpenShift can be configured and run in the ADB by issuing the following command: *systemctl start openshift*.

* SCCLI

  SCCLI provides a single point of entry for managing services inside of the ADB. This is primarily of interest to users who use the ADB as a VM they access via *vagrant ssh*.

  This CLI can clean the environment and ensure that the requested service is set up properly.

  Currently SCCLI only provides an interface for managing OpenShift or a single node Kubernetes instance.

The usage of sccli is as below::

       $ sccli --help

       usage: sccli [service_name] || [clean]
       List of possible service_name:
                k8s openshift


These utilities and unit files are packaged as an RPM and included in `Atomic-Developer-Bundle (ADB) <https://github.com/projectatomic/adb-atomic-developer-bundle>`_ version 1.7.0 or later.

The public YUM repository is available at : http://mirror.centos.org/centos-7/7/atomic/x86_64/adb/

Steps to build the SRC RPM
==========================
* Create source tar ball

  spectool -g -R adb-utils.spec

* Build the SRPM for el7

  rpmbuild --define "_srcrpmdir $PWD" --define "dist .el7" -bs adb-utils.spec

Interested in Contributing to this project?
===========================================

We welcome issues and pull requests.  Want to be more involved, join us:

* Mailing List: `container-tools@redhat.com`_
* IRC: #atomic and #nulecule on `freenode`_
* Meetings:
   *  Planning and Integration Meeting:

      every Wednesday at 1230 UTC in a Bluejean `Video Conference`_.
      Alternately, a local `phone access number`_ may be available.
      (1 hour)

   *  Team Standup/Review

      every Monday at 1500 UTC in IRC `freenode`_ #nulecule (.5 hour)

**Note:** These meetings, mailing lists, and irc channels may include
discussion of other Project Atomic components.

Documentation is written using `reStructuredText`_. An `online
reStructuredText editor`_ is available.

.. _container-tools@redhat.com: https://www.redhat.com/mailman/listinfo/container-tools
.. _freenode: https://freenode.net/
.. _Video Conference: https://bluejeans.com/381583203
.. _phone access number: https://www.intercallonline.com/listNumbersByCode.action?confCode=8464006194
.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _online reStructuredText editor: http://rst.ninjs.org
