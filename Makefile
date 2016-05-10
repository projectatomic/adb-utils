# Copyright (c) 2016 Red Hat, Inc. All rights reserved. This copyrighted material
# is made available to anyone wishing to use, modify, copy, or
# redistribute it subject to the terms and conditions of the GNU General
# Public License v.2.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# 
# Author: Praveen Kumar <kumarpraveen.nitdgp@gmail.com>

TODAY := $(shell date +%Y%m%d)
UPSTREAM_NAME := adb-utils
VERSION := 20110506
DOWNSTREAM_NAME := cdk-utils
SOURCE := https://github.com/projectatomic/${UPSTREAM_NAME}/archive/v${VERSION}.tar.gz
MASTER_SOURCE := https://github.com/projectatomic/adb-utils/archive/master.tar.gz
UPSTREAM_IMAGE_VERSION := "v1\.1\.1"
DOWNSTREAM_IMAGE_VERSION := "v3\.1\.1\.6"

.PHONY: clean upstream downstream master


upstream:

	curl -sL -O ${SOURCE}
	rpmbuild --define "_sourcedir ${PWD}" --define "_srcrpmdir ${PWD}" --define "dist .el7" -bs ${UPSTREAM_NAME}.spec && \
	    rm -fr ${UPSTREAM_NAME}-${VERSION}.tar.gz

downstream:

	# Change to downstream name and source
	sed -i \
	    -e "s|Name:\(\s\+\)\(.*\)|Name:\1cdk-utils|" ${UPSTREAM_NAME}.spec \
	    -e "s|Source0:\(\s\+\)\(.*\)|Source0:\1\%{name}-\%{version}\.tar\.gz|" \
	    -e "s|Version:\(\s\+\)\(.*\)|Version:\1${VERSION}|"

	mv ${UPSTREAM_NAME}.spec ${DOWNSTREAM_NAME}.spec
	curl -sL -O ${SOURCE}
	tar -xvf v${VERSION}.tar.gz && rm v${VERSION}.tar.gz
	mv ${UPSTREAM_NAME}-${VERSION} ${DOWNSTREAM_NAME}-${VERSION}

	# Changes to openshift_option for downstream
	sed -i -e \
	    "s|IMAGE=\"docker\.io/openshift/origin:${UPSTREAM_IMAGE_VERSION}\"|IMAGE=\"registry\.access\.redhat\.com/openshift3/ose:${DOWNSTREAM_IMAGE_VERSION}\"|" \
	    ${DOWNSTREAM_NAME}-${VERSION}/services/openshift/openshift_option 

	# Changes to sccli for downstream
	sed -i -e \
	    "s|DOCKER_REGISTRY = \"docker\.io\"|DOCKER_REGISTRY = \"registry\.access\.redhat\.com\"|" \
	    ${DOWNSTREAM_NAME}-${VERSION}/utils/sccli.py \
	    -e "s|IMAGE_NAME = \"openshift/origin\"|IMAGE_NAME = \"openshift3/ose\"|" \
	    -e "s|IMAGE_TAG = \"${UPSTREAM_IMAGE_VERSION}\"|IMAGE_TAG = \"${DOWNSTREAM_IMAGE_VERSION}\"|"

	tar -cvf ${DOWNSTREAM_NAME}-${VERSION}.tar.gz ${DOWNSTREAM_NAME}-${VERSION} && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}
	rpmbuild --define "_sourcedir ${PWD}" --define "_srcrpmdir ${PWD}" --define "dist .el7" -bs ${DOWNSTREAM_NAME}.spec && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}.tar.gz
	git checkout ${UPSTREAM_NAME}.spec

master:

	# Change to downstream name and source
	sed -i \
	    -e "s|Name:\(\s\+\)\(.*\)|Name:\1cdk-utils|" ${UPSTREAM_NAME}.spec \
	    -e "s|Source0:\(\s\+\)\(.*\)|Source0:\1\%{name}-\%{version}\.tar\.gz|" \
	    -e "s|Version:\(\s\+\)\(.*\)|Version:\1${VERSION}|"

	mv ${UPSTREAM_NAME}.spec ${DOWNSTREAM_NAME}.spec
	curl -sL -O ${MASTER_SOURCE}
	tar -xvf master.tar.gz && rm master.tar.gz
	mv ${UPSTREAM_NAME}-master ${DOWNSTREAM_NAME}-${VERSION}

	# Changes to openshift_option for downstream
	sed -i -e \
	    "s|IMAGE=\"docker\.io/openshift/origin:${UPSTREAM_IMAGE_VERSION}\"|IMAGE=\"registry\.access\.redhat\.com/openshift3/ose:${DOWNSTREAM_IMAGE_VERSION}\"|" \
	    ${DOWNSTREAM_NAME}-${VERSION}/services/openshift/openshift_option 

	# Changes to sccli for downstream
	sed -i -e \
	    "s|DOCKER_REGISTRY = \"docker\.io\"|DOCKER_REGISTRY = \"registry\.access\.redhat\.com\"|" \
	    ${DOWNSTREAM_NAME}-${VERSION}/utils/sccli.py \
	    -e "s|IMAGE_NAME = \"openshift/origin\"|IMAGE_NAME = \"openshift3/ose\"|" \
	    -e "s|IMAGE_TAG = \"${UPSTREAM_IMAGE_VERSION}\"|IMAGE_TAG = \"${DOWNSTREAM_IMAGE_VERSION}\"|"

	tar -cvf ${DOWNSTREAM_NAME}-${VERSION}.tar.gz ${DOWNSTREAM_NAME}-${VERSION} && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}
	rpmbuild --define "_sourcedir ${PWD}" --define "_srcrpmdir ${PWD}" --define "dist .el7" -bs ${DOWNSTREAM_NAME}.spec && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}.tar.gz
	git checkout ${UPSTREAM_NAME}.spec

clean:

	rm -fr *.tar.gz
	rm -fr *.src.rpm
