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

UPSTREAM_NAME := adb-utils
VERSION := 2.1
DOWNSTREAM_NAME := cdk-utils
SOURCE := https://github.com/projectatomic/${UPSTREAM_NAME}/archive/v${VERSION}.tar.gz
MASTER_SOURCE := https://github.com/projectatomic/adb-utils/archive/master.tar.gz

.PHONY: clean upstream downstream master


upstream:

	# Create SRPM for upstream release as per VERSION variable.
	sed -i ${UPSTREAM_NAME}.spec \
	    -e "s|^Source0:\(\s\+\)\(.*\)$ |Source0:\1\%{name}-\%{version}\.tar\.gz|" \
	    -e "s|^Version:\(\s\+\)\(.*\)$ |Version:\1${VERSION}|"
	git archive --format tar.gz --prefix ${UPSTREAM_NAME}-${VERSION}/ HEAD -o ${UPSTREAM_NAME}-${VERSION}.tar.gz
	rm -fr ${UPSTREAM_NAME}-${VERSION}
	rpmbuild --define "_sourcedir ${PWD}" --define "_srcrpmdir ${PWD}" --define "dist .el7" -bs ${UPSTREAM_NAME}.spec && \
	    rm -fr ${UPSTREAM_NAME}-${VERSION}.tar.gz
	git checkout ${UPSTREAM_NAME}.spec

downstream:

	# Create SRPM for downstream with a proper release of upstream
	sed -i \
	    -e "s|^Name:\(\s\+\)\(.*\)$ |Name:\1cdk-utils|" ${UPSTREAM_NAME}.spec \
	    -e "s|^Source0:\(\s\+\)\(.*\)$ |Source0:\1\%{name}-\%{version}\.tar\.gz|" \
	    -e "s|^Version:\(\s\+\)\(.*\)$ |Version:\1${VERSION}|"

	mv ${UPSTREAM_NAME}.spec ${DOWNSTREAM_NAME}.spec
	curl -sL -O ${SOURCE}
	tar -xvf v${VERSION}.tar.gz && rm v${VERSION}.tar.gz
	mv ${UPSTREAM_NAME}-${VERSION} ${DOWNSTREAM_NAME}-${VERSION}
	
	tar -cvf ${DOWNSTREAM_NAME}-${VERSION}.tar.gz ${DOWNSTREAM_NAME}-${VERSION} && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}
	rpmbuild --define "_sourcedir ${PWD}" --define "_srcrpmdir ${PWD}" \
	    --define "dist .el7" -bs ${DOWNSTREAM_NAME}.spec && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}.tar.gz
	git checkout ${UPSTREAM_NAME}.spec

downstream_local:

	# Create SRPM for downstream which include local changes without commit
	sed -i \
	    -e "s|^Name:\(\s\+\)\(.*\)$ |Name:\1cdk-utils|" ${UPSTREAM_NAME}.spec \
	    -e "s|^Source0:\(\s\+\)\(.*\)$ |Source0:\1\%{name}-\%{version}\.tar\.gz|" \
	    -e "s|^Version:\(\s\+\)\(.*\)$ |Version:\1${VERSION}|"

	mv ${UPSTREAM_NAME}.spec ${DOWNSTREAM_NAME}.spec
	mkdir -p ${DOWNSTREAM_NAME}-${VERSION}
	tar cf - --exclude=${DOWNSTREAM_NAME}-${VERSION} --exclude=.git . | (cd ${DOWNSTREAM_NAME}-${VERSION} && tar xvf - )

	tar -cvf ${DOWNSTREAM_NAME}-${VERSION}.tar.gz ${DOWNSTREAM_NAME}-${VERSION} && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}
	rpmbuild --define "_sourcedir ${PWD}" --define "_srcrpmdir ${PWD}" \
	    --define "dist .el7" -bs ${DOWNSTREAM_NAME}.spec && \
	    rm -fr ${DOWNSTREAM_NAME}-${VERSION}.tar.gz
	git checkout ${UPSTREAM_NAME}.spec

update_autocomplete:
	# Clone latest autocomplete script and put required location
	curl -sL https://github.com/openshift/origin/raw/master/contrib/completions/bash/oadm > bash_completions/oadm
	curl -sL https://github.com/openshift/origin/raw/master/contrib/completions/bash/oc > bash_completions/oc
	curl -sL https://github.com/openshift/origin/raw/master/contrib/completions/bash/openshift > bash_completions/openshift
	
update_template:
	# Clone from upstream and put required location.
	# Nodejs
	curl -sL https://github.com/openshift/nodejs-ex/raw/master/openshift/templates/nodejs-mongodb.json > services/openshift/templates/common/nodejs-mongodb.json
	curl -sL https://github.com/openshift/nodejs-ex/raw/master/openshift/templates/nodejs.json > services/openshift/templates/common/nodejs.json
	# Cakephp
	curl -sL https://github.com/openshift/cakephp-ex/raw/master/openshift/templates/cakephp.json > services/openshift/templates/common/cakephp.json
	curl -sL https://github.com/openshift/cakephp-ex/raw/master/openshift/templates/cakephp-mysql.json > services/openshift/templates/common/cakephp-mysql.json
	# Jenkins
	curl -sL https://github.com/openshift/origin/raw/master/examples/jenkins/master-slave/jenkins-slave-template.json > services/openshift/templates/common/jenkins-slave-template.json
	curl -sL https://github.com/openshift/origin/raw/master/examples/jenkins/pipeline/samplepipeline.json > services/openshift/templates/adb/samplepipeline.json
	curl -sL https://github.com/openshift/origin/raw/master/examples/jenkins/jenkins-ephemeral-template.json > services/openshift/templates/cdk/jenkins-ephemeral-template.json
	curl -sL https://github.com/openshift/origin/raw/master/examples/jenkins/jenkins-persistent-template.json > services/openshift/templates/cdk/jenkins-persistent-template.json
	# EAP
	curl -sL https://github.com/jboss-openshift/application-templates/raw/master/eap/eap64-mysql-persistent-s2i.json > services/openshift/templates/common/eap64-mysql-persistent-s2i.json
	curl -sL https://github.com/jboss-openshift/application-templates/raw/master/eap/eap64-basic-s2i.json > services/openshift/templates/common/eap64-basic-s2i.json
	# JWS tomcat
	curl -sL https://github.com/jboss-openshift/application-templates/raw/master/webserver/jws30-tomcat7-mysql-persistent-s2i.json > services/openshift/templates/common/jws30-tomcat7-mysql-persistent-s2i.json
	# Jboss Image Stream
	curl -sL https://github.com/jboss-openshift/application-templates/raw/master/jboss-image-streams.json > services/openshift/templates/common/jboss-image-streams.json
	# Image stream CentOS
	curl -sL https://github.com/openshift/origin/raw/master/examples/image-streams/image-streams-centos7.json > services/openshift/templates/adb/image-streams-centos7.json
	# Image stream RHEL
	curl -sL https://github.com/openshift/origin/raw/master/examples/image-streams/image-streams-rhel7.json > services/openshift/templates/cdk/image-streams-rhel7.json

clean:

	rm -fr *.tar.gz
	rm -fr *.src.rpm
	rm -fr cdk-utils.spec

