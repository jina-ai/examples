#!/bin/sh
TEST_WORKDIR=/tmp/jina/flower/
mkdir -p ${TEST_WORKDIR}
cd ${TEST_WORKDIR}
curl https://www.robots.ox.ac.uk/~vgg/data/flowers/17/17flowers.tgz --output 17flowers.tgz
tar zxf 17flowers.tgz
