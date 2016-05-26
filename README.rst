adb-utils
=========

Utility and Service scripts for the `Atomic-Developer-Bundle (ADB) <https://github.com/projectatomic/adb-atomic-developer-bundle>`_.

adb-utils provides the following content to the ADB Vagrant box:

* OpenShift as a service

  adb-utils uses a systemd service unit file to launch and setup a containerized version of OpenShift. With the systemd unit file, OpenShift can be configured and run in the ADB by issuing the following command: ``systemctl start openshift``.

* SCCLI

  The Service Change CLI (sccli) provides a single point of entry for managing services inside of the ADB. The Kubernetes and OpenShift services can not run simultaneously in the ADB because of port conflicts, the sccli provides an easy way to change and run a specific service.

  This is primarily of interest to users who use the ADB as a VM, which they access via ``vagrant ssh``.

  sccli enables the user to switch services easily in a running vagrant box. Currently, ``sccli`` only provides an interface for managing OpenShift or a single node Kubernetes instance.

  The ``sccli`` command does not generate any output, but provides the correct, specific return code which is consumed by the `vagrant-service-manager <https://github.com/projectatomic/vagrant-service-manager>`_. The vagrant-service-manager plugin calls upon the ``sccli`` to manage the services inside of the ADB.


  The usage of sccli is as below::

     sccli [-h] {kubernetes,openshift,docker} ...
 
     CLI for managing services in ADB/CDK
 
     optional arguments:
     -h, --help            show this help message and exit
 
     subcommands:
     Manage services for openshift|docker|kubernetes
 
     {kubernetes,openshift,docker}
     kubernetes          start|restart|status|stop (default:start)
     openshift           start|restart|status|stop (default:start)
     docker              start|restart|status|stop (default:start)


  For instance, to start Kubernetes service, use::

   # sccli kubernetes start
   # echo $?


  ``echo $?`` gives you the return code for the command and feeds it to the vagrant-service-manager. The vagrant-service-manager makes decisions based on these return codes.
  If the return code is 0, it implies that the service has behaved (started/restarted/stopped) as expected. If the return status is anything other than 0, it implies that the service has failed to behave as expected.


  sccli accepts environment variables to modify how services are configured and deployed.  
  For the OpenShift service, the following environment variables are recognized:

  ``DOCKER_REGISTRY``, defines which registry the OpenShift containers should be pulled from. The default value is ``"docker.io"``.

  ``IMAGE_NAME``, defines which OpenShift image should be used. The default value is ``"openshift/origin"``.

  ``IMAGE_TAG``, defines which version of OpenShift should be used. The default value is ``"v1.1.1"``.

  Thus, the version of OpenShift defaults to the containerized version at ``docker.io/openshift/origin:v1.1.1``.  If you desire a different version, pass the ``DOCKER_REGISTRY``, ``IMAGE_NAME`` and/or ``IMAGE_TAG`` environment variables.  
  
  An example of changing these would be::

   $ sudo DOCKER_REGISTRY="registry.mycompany.com" IMAGE_NAME="openshift_gold" IMAGE_TAG="v2016-01-03" sccli openshift start

 
  Or, to use the ``latest`` version::

     $ IMAGE_TAG="latest" sccli openshift start


These utilities and unit files are packaged as an RPM and included in `Atomic-Developer-Bundle (ADB) <https://github.com/projectatomic/adb-atomic-developer-bundle>`_ version 1.7.0 or later.

The public YUM repository is available at: http://mirror.centos.org/centos-7/7/atomic/x86_64/adb/

IP Detection Note
=================
This code uses the last IPv4 address available from the set of configured
addresses that are *up*.  i.e. if eth0, eth1, and eth2 are all up and
have IPv4 addresses, the address on eth2 is used.

Steps to build the SRC RPM
==========================
* Create source tar ball

  ``spectool -g -R adb-utils.spec``

* Build the SRPM for el7

  ``rpmbuild --define "_srcrpmdir $PWD" --define "dist .el7" -bs adb-utils.spec``

Interested in Contributing to this Project?
===========================================

We welcome issues and pull requests.  Want to be more involved, join us:

* Mailing List: `container-tools@redhat.com`_
* IRC: #atomic and #nulecule on `freenode`_
* Meetings:

  * Planning and Integration Meeting: Every Wednesday at 1230 UTC in a Bluejean `Video Conference`_. Alternately, a local `phone access number`_ may be available. (1 hour)
  * Team Standup/Review: Every Monday at 1500 UTC in IRC `freenode`_ #nulecule (.5 hour)


**Note:** These meetings, mailing lists, and irc channels may include
discussions on other Project Atomic components.

Documentation is written using `reStructuredText`_. An `online
reStructuredText editor`_ is available.

.. _container-tools@redhat.com: https://www.redhat.com/mailman/listinfo/container-tools
.. _freenode: https://freenode.net/
.. _Video Conference: https://bluejeans.com/381583203
.. _phone access number: https://www.intercallonline.com/listNumbersByCode.action?confCode=8464006194
.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _online reStructuredText editor: http://rst.ninjs.org
