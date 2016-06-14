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
    112 - openshift_option file not found or it's syntax changed.

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
import netifaces
import socket
from argparse import ArgumentParser
from urllib import quote_plus

OPERATION = ['start', 'status', 'restart', 'stop']
OPENSHIFT_OPTION = '/etc/sysconfig/openshift_option'


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

def get_all_interface_ip():
    interface_list = ''
    for interface in netifaces.interfaces():
        addr = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
        if addr:
            interface_list += "%s," % addr[0].get('addr')
    return interface_list

def set_proxy():
    proxy = os.getenv('PROXY', '')
    if proxy:
        interface_ip_list = get_all_interface_ip()
        predefine_no_proxy_list = ".xip.io,172.30.0.0/16,172.17.0.0/16,%s" % socket.gethostname()
        proxy_user = quote_plus(os.getenv('PROXY_USER',''))
        if proxy_user:
            proxy_password = quote_plus(os.getenv('PROXY_PASSWORD',''))
            http_proxy_url = "http://%s:%s@%s" % (proxy_user, proxy_password, proxy)
            https_proxy_url = "https://%s:%s@%s" % (proxy_user, proxy_password, proxy)
        else:
            http_proxy_url = "http://%s" % proxy
            https_proxy_url = "https://%s" % proxy
        # openshift proxy setup
        if system(('sed -i -e "/^#HTTP_PROXY=*/cHTTP_PROXY=%s"'
                   ' -e "/^#HTTPS_PROXY=*/cHTTPS_PROXY=%s"'
                   ' -e "/^#NO_PROXY=*/cNO_PROXY=%s%s"'
                ' %s') % (http_proxy_url, http_proxy_url, interface_ip_list,
                          predefine_no_proxy_list, OPENSHIFT_OPTION))[2]:
            return ("Permisison denined: %s" % OPENSHIFT_OPTION)
        # docker daemon proxy setup
        if not os.path.isdir('/etc/systemd/system/docker.service.d'):
            subprocess.call("mkdir /etc/systemd/system/docker.service.d", shell=True)
        env_file_content = ('[Service]\n'
                'Environment="HTTP_PROXY=%s" "NO_PROXY=localhost,127.0.0.1,::1,.xip.io"\n') \
                        % (http_proxy_url)
        try:
            with open('/etc/systemd/system/docker.service.d/http-proxy.conf', 'w') as fh:
                fh.write(env_file_content)
            subprocess.call('systemctl daemon-reload', shell=True)
            return subprocess.call('systemctl restart docker', shell=True)
        except IOError as err:
            return err

def get_registry_image_tag_defaults():
    try:
        with open(OPENSHIFT_OPTION) as fh:
            file_content = fh.readlines()
        for content in file_content:
            if 'IMAGE' in content:
                content = content.strip()
                docker_registry = content.split('/', 1)[0].split('=')[-1]
                image_name, image_tag = tuple(content.split('/', 1)[1].split(':'))
                return (docker_registry, image_name, image_tag)
    except IOError as err:
        return

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
    try:
        DOCKER_REGISTRY, IMAGE_NAME, IMAGE_TAG = get_registry_image_tag_defaults()
    except ValueError:
        return("Not able to find: %s or syntax changed" % OPENSHIFT_OPTION, 112)
    docker_registry = os.getenv('DOCKER_REGISTRY', DOCKER_REGISTRY)
    image_name = os.getenv('IMAGE_NAME', IMAGE_NAME)
    image_tag = os.getenv('IMAGE_TAG', IMAGE_TAG)
    if system(('sed -i.back "/^IMAGE=*/cIMAGE=\"%s/%s\:%s\""'
            ' %s') % (docker_registry, image_name, image_tag, OPENSHIFT_OPTION))[2]:
        return ("Permisison denined: %s" % OPENSHIFT_OPTION, 37)
    image_pull_list = ("{0}/{1}:{2} "
                       "{0}/{1}-haproxy-router:{2} "
                       "{0}/{1}-deployer:{2} "
                       "{0}/{1}-docker-registry:{2} "
                       "{0}/{1}-sti-builder:{2}").format(docker_registry, image_name, image_tag)
    sys.stdout.write("Downloading OpenShift docker images" + "\n")
    sys.stdout.flush()
    for image in image_pull_list.split():
        sys.stdout.write("docker pull %s" % image + "\n")
        sys.stdout.flush()
        if system("docker pull %s" % image)[2]:
            return ("%s Not Pulled" % image, 111)
    return ('', 0)

def service_start(service_name):
    if set_proxy():
        return ("Proxy setup failed", 113)
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
        output, returncode =  system("systemctl start openshift")[1:]
        if output:
            return (output, returncode)
        # This is required because of proxy configurations.
        return system("systemctl restart docker")[1:]
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
