#!/bin/bash

# This script is used to build downstream srpm for adb-utils after minor update
# to upstream.
# Note: Make sure you update *version* detail before run this script.

UPSTREAM_NAME=adb-utils
VERSION=1.1
DOWNSTREAM_NAME=cdk-utils
SOURCE=https://github.com/projectatomic/$UPSTREAM_NAME/archive/v${VERSION}.tar.gz
SPEC_SRC="https:\/\/github.com\/projectatomic\/\%{name}\/archive\/v\%{version}\.tar\.gz"

# Change to downstream name and source
sed -i -e "s/Name:\(.*\)adb-utils/Name:\1cdk-utils/" ${UPSTREAM_NAME}.spec \
       -e "s/Source0:\(\s.*\)${SPEC_SRC}/Source0:\1\%{name}-\%{version}\.tar\.gz/"

mv ${UPSTREAM_NAME}.spec ${DOWNSTREAM_NAME}.spec
wget $SOURCE
tar -xvf v${VERSION}.tar.gz && rm v${VERSION}.tar.gz
mv $UPSTREAM_NAME-$VERSION $DOWNSTREAM_NAME-$VERSION

# Changes to openshift_option for downstream
sed -i -e \
    "s/IMAGE=\"docker\.io\/openshift\/origin:v1\.1\.1\"/IMAGE=\"registry\.access\.redhat\.com\/openshift3\/ose:v3\.1\.0\.4\"/" \
    $DOWNSTREAM_NAME-$VERSION/services/openshift/openshift_option \
    -e "s/OPTIONS=\"-host adb\.vm\"/OPTIONS=\"-host cdk\.vm\"/"

# Changes to sccli for downstream
sed -i -e \
    "s/dockerRegistry=\${DOCKER_REGISTRY:-docker\.io}/dockerRegistry=\${DOCKER_REGISTRY:-registry\.access\.redhat\.com}/" \
    $DOWNSTREAM_NAME-$VERSION/utils/sccli.sh \
    -e "s/imageName=\${IMAGE_NAME:-openshift\/origin}/imageName=\${IMAGE_NAME:-openshift3\/ose}/" \
    -e "s/imageTag=\${IMAGE_TAG:-v1\.1\.1}/imageTag=\${IMAGE_TAG:-v3\.1\.0\.4}/"

tar -cvf ${DOWNSTREAM_NAME}-${VERSION}.tar.gz $DOWNSTREAM_NAME-$VERSION && \
    rm -fr $DOWNSTREAM_NAME-$VERSION
rpmbuild --define "_srcrpmdir $PWD" --define "dist .el7" -bs $DOWNSTREAM_NAME.spec && \
    rm -fr ${DOWNSTREAM_NAME}-${VERSION}.tar.gz
git checkout ${UPSTREAM_NAME}.spec
