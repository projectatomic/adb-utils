#!/bin/bash

# sccli - Service Change CLI
# Script to switch openshift from k8s or vice-versa 

function single_node_k8s_setup ()
{
    # Clean before starting
    clean_setup

    # Check if the service account key for kube services is correctly set
    if ! [ grep 'serviceaccount.key' /etc/kubernetes/apiserver >/dev/null 2>&1 ] && \
      [ /etc/kubernetes/controller-manager >/dev/null 2>&1 ]; then
        setup_kube_service_account_key
    fi

    # Enable Kubernetes master services
    # etcd kube-apiserver kube-controller-manager kube-scheduler
    sudo systemctl enable etcd kube-apiserver kube-controller-manager kube-scheduler
    sudo systemctl start etcd kube-apiserver kube-controller-manager kube-scheduler
    sudo sleep 15

    # Enable Kubernetes minion services
    # kube-proxy kubelet docker
    sudo systemctl enable kube-proxy kubelet
    sudo systemctl start kube-proxy kubelet
    sudo systemctl restart docker
}

function setup_kube_service_account_key()
{
    sudo mkdir -p /etc/pki/kube-apiserver/
    sudo openssl genrsa -out /etc/pki/kube-apiserver/serviceaccount.key 2048

    sudo sed -i.back '/KUBE_API_ARGS=*/c\KUBE_API_ARGS="--service_account_key_file=/etc/pki/kube-apiserver/serviceaccount.key"' /etc/kubernetes/apiserver

    sudo sed -i.back '/KUBE_CONTROLLER_MANAGER_ARGS=*/c\KUBE_CONTROLLER_MANAGER_ARGS="--service_account_private_key_file=/etc/pki/kube-apiserver/serviceaccount.key"' /etc/kubernetes/controller-manager

}

function clean_setup ()
{

    if $(systemctl is-active kubelet > /dev/null); then
        echo "Stopping the Kubernetes services"
        #enable Kubernetes master services
        #etcd kube-apiserver kube-controller-manager kube-scheduler
        sudo systemctl disable etcd kube-apiserver kube-controller-manager kube-scheduler
        sudo systemctl stop kube-apiserver kube-controller-manager kube-scheduler
        sudo systemctl disable kube-proxy kubelet
        sudo systemctl stop kube-proxy kubelet
        sudo systemctl reset-failed kube-apiserver kube-controller-manager kube-scheduler kubelet kube-proxy
        sudo systemctl stop etcd
    fi
    if $(systemctl is-active openshift > /dev/null); then
        echo "Stopping the Openshift services"
        sudo systemctl stop openshift
        sudo systemctl disable openshift
        sudo systemctl reset-failed openshift
    fi
}

function usage()
{
    echo "usage: sccli [service_name] || [clean]"
    echo "List of possible service_name: "
    echo -e "\tk8s|kubernetes openshift"
}

function openshift()
{
    # Default OpenShift Image and Tag
    dockerRegistry=${DOCKER_REGISTRY:-docker.io}
    imageName=${IMAGE_NAME:-openshift/origin}
    imageTag=${IMAGE_TAG:-v1.1.3}

    clean_setup

    # Setup the systemd environment - desired image may have changed
    sudo sed -i.back "/^IMAGE=*/cIMAGE=\"${dockerRegistry}/${imageName}\:${imageTag}\"" /etc/sysconfig/openshift_option

    # ensure the docker containers are present
    if [[ "$(docker images -q  ${dockerRegistry}/${imageName}:${imageTag} 2> /dev/null)" == "" ]]; then
        docker pull ${dockerRegistry}/${imageName}:${imageTag}
        docker pull ${dockerRegistry}/${imageName}-haproxy-router:${imageTag}
        docker pull ${dockerRegistry}/${imageName}-deployer:${imageTag}
        docker pull ${dockerRegistry}/${imageName}-docker-registry:${imageTag}
        docker pull ${dockerRegistry}/${imageName}-sti-builder:${imageTag}
    fi

    sudo systemctl enable openshift
    sudo systemctl start openshift
}

if [ "$#" -ne 1 ]; then
    usage
elif [ "$1" == "k8s" ] || [ "$1" == "kubernetes" ]; then
    single_node_k8s_setup
elif [ "$1" == "openshift" ]; then
    openshift
elif [ "$1" == "clean" ]; then
    clean_setup
elif [ "$1" ]; then
    usage
fi
