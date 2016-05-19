#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2016  Praveen Kumar <kumarpraveen.nitdgp@gmail.com>
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# sccli - Service Change CLI for kubernetes, openshift and docker

"""
Standard Exit Codes (bash): http://tldp.org/LDP/abs/html/exitcodes.html
Return Code:
    110 - Service is not running
    111 - Docker image not pulled

Sample Usage:
    $ python sccli.py -h
    $ sudo python sccli.py kubernetes stop
    $ echo $? (if success return 0)
    $ sudo python sccli.py openshift start
    docker.io/openshift/origin:v1.1.9 Not Pulled (Message in stderr)
    $ echo $?
    111 (Exit code for Docker images pull issue)
"""

import os
import subprocess
import sys
import time
from argparse import ArgumentParser

OPERATION = ['start', 'status', 'restart', 'stop']
DOCKER_REGISTRY = "docker.io"
IMAGE_NAME = "openshift/origin"
IMAGE_TAG = "v1.1.3"


def system(cmd):
    """
    Runs a shell command, and returns the output, err, returncode
    :param cmd: The command to run.
    :return:  Tuple with (output, err, returncode).
    """
    ret = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    out, err = ret.communicate()
    returncode = ret.returncode
    return out, err, returncode

def service_status(service_name):
    if service_name == "kubernetes":
        status = 0
        services = ['etcd', 'kube-apiserver', 'kube-controller-manager',
                    'kube-scheduler', 'kube-proxy', 'kubelet']
        for service in services:
            status = status or system("systemctl is-active %s" % service)[2]
            if status:
                service_stop(service_name)
                break
        return status
    else:
        return system("systemctl is-active %s" % service_name)[2]

def service_restart(service_name):
    if service_status(service_name):
        return ('Start %s first' % service_name, 110)
    if service_name == "kubernetes":
        return system("systemctl restart etcd kube-apiserver"
                      " kube-controller-manager kube-scheduler"
                      " kube-proxy kubelet docker")[1:]
    else:
        return system("systemctl restart %s" % service_name)[1:]


def service_stop(service_name):
    if service_name == "kubernetes":
        system("systemctl disable etcd kube-apiserver "
               "kube-controller-manager kube-scheduler kube-proxy kubelet")
        if not system("systemctl is-active kube-apiserver")[2]:
            system("systemctl stop kube-apiserver")
        if not system("systemctl is-active kube-controller-manager")[2]:
            system("systemctl stop kube-controller-manager")
        if not system("systemctl is-active kube-scheduler")[2]:
            system("systemctl stop kube-scheduler")
        if not system("systemctl is-active kube-proxy")[2]:
            system("systemctl stop kube-proxy")
        if not system("systemctl is-active kubelet")[2]:
            system("systemctl stop kubelet")
        system("systemctl reset-failed kube-apiserver"
               " kube-controller-manager kube-scheduler kube-proxy kubelet")
        if not system("systemctl is-active etcd")[2]:
            system("systemctl stop etcd")
    elif service_name == "openshift":
        system("systemctl disable openshift")
        if not system("systemctl is-active openshift")[2]:
            system("systemctl stop openshift")
        system("systemctl reset-failed openshift")
    elif service_name == "docker":
        if not system("systemctl is-active docker")[2]:
            system("systemctl stop docker")
        system("systemctl reset-failed docker")

def setup_kube_service_account_key():
    system("mkdir -p /etc/pki/kube-apiserver/")
    system("openssl genrsa -out /etc/pki/kube-apiserver/serviceaccount.key 2048")
    system("sed -i.back '/KUBE_API_ARGS=*/c\KUBE_API_ARGS="
           "\"--service_account_key_file=/etc/pki/kube-apiserver/serviceaccount.key\"'"
           " /etc/kubernetes/apiserver")
    system("sed -i.back '/KUBE_CONTROLLER_MANAGER_ARGS=*/c\KUBE_CONTROLLER_MANAGER_ARGS="
           "\"--service_account_private_key_file=/etc/pki/kube-apiserver/serviceaccount.key\"'"
           "/etc/kubernetes/controller-manager")

# This is not used "need discussion"
def vagrant_box_variant():
    try:
        with open("/etc/os-release") as fh:
            for line in fh.readlines():
                if "Container Development Kit" in line:
                    return False
        return True
    except IOError as err:
        return (err, 37)

def pull_openshift_images():
    docker_registry = os.getenv('DOCKER_REGISTRY', DOCKER_REGISTRY)
    image_name = os.getenv('IMAGE_NAME', IMAGE_NAME)
    image_tag = os.getenv('IMAGE_TAG', IMAGE_TAG)
    if system(('sed -i.back "/^IMAGE=*/cIMAGE=\"%s/%s\:%s\""'
            ' /etc/sysconfig/openshift_option') % (docker_registry, image_name, image_tag))[2]:
        return ("Permisison denined: /etc/sysconfig/openshift_option", 37)
    image_pull_list = ("{0}/{1}:{2} "
                       "{0}/{1}-haproxy-router:{2} "
                       "{0}/{1}-deployer:{2} "
                       "{0}/{1}-docker-registry:{2} "
                       "{0}/{1}-sti-builder:{2}").format(docker_registry, image_name, image_tag)
    for image in image_pull_list.split():
        if system("docker pull %s" % image)[2]:
            return ("%s Not Pulled" % image, 111)
    return ('', 0)

def service_start(service_name):
    if service_name == "kubernetes":
        service_stop("openshift")
        # This is required because openshift does create kubeconfig for 8443 port
        subprocess.call("rm -fr /home/vagrant/.kube", shell=True)
        subprocess.call("rm -fr /root/.kube", shell=True)
        if not subprocess.call("grep 'serviceaccount.key' /etc/kubernetes/apiserver"
                               " > /dev/null 2>&1", shell=True):
            setup_kube_service_account_key()
        err, returncode = system("systemctl start etcd kube-apiserver "
                                 "kube-controller-manager kube-scheduler")[1:]
        if returncode:
            return err, returncode
        else:
            time.sleep(15)
            return system("systemctl start kube-proxy kubelet")[1:]
    if service_name == "openshift":
        service_stop("kubernetes")
        output, returncode = pull_openshift_images()
        if returncode:
            return (output, returncode)
        return system("systemctl start openshift")[1:]
    if service_name == "docker":
        return system("systemctl start docker")[1:]


def service_operation(service_name, service_ops):
    if os.getuid():
        print "Execution Permision Denied (use sudo)"
        sys.exit(1)
    if service_ops not in OPERATION:
        return sys.exit(1)
    if service_ops == 'start':
        err, returncode = service_start(service_name)
        sys.stderr.write(err)
        sys.exit(returncode)
    if args.sub_command == 'restart':
        err, returncode = service_restart(service_name)
        sys.stderr.write(err)
        sys.exit(returncode)
    if args.sub_command == 'status':
        sys.exit(service_status(service_name))
    if args.sub_command == 'stop':
        sys.exit(service_stop(service_name))


def kube_ops(args):
    service_operation('kubernetes', args.sub_command)

def openshift_ops(args):
    service_operation('openshift', args.sub_command)

def docker_ops(args):
    service_operation('docker', args.sub_command)


if __name__ == '__main__':
    parser = ArgumentParser(prog='sccli', description='CLI for managing services in ADB/CDK')
    subparsers = parser.add_subparsers(description = 'Manage services for openshift|docker|kubernetes')
    k8s_parser = subparsers.add_parser('kubernetes', help='start|restart|status|stop (default:start)')
    k8s_parser.add_argument('sub_command', nargs='?',
                            help='start|restart|status|stop (default:start)', default='start')
    k8s_parser.set_defaults(func=kube_ops)
    openshift_parser = subparsers.add_parser('openshift', help='start|restart|status|stop (default:start)')
    openshift_parser.add_argument('sub_command', nargs='?',
                                  help='start|restart|status|stop (default:start)', default='start')
    openshift_parser.set_defaults(func=openshift_ops)
    docker_parser = subparsers.add_parser('docker', help='start|restart|status|stop (default:start)')
    docker_parser.add_argument('sub_command', nargs='?',
                               help='start|restart|status|stop default:start', default='start')
    docker_parser.set_defaults(func=docker_ops)
    args = parser.parse_args()
    args.func(args)
