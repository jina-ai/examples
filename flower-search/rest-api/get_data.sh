#!/bin/sh
TEST_WORKDIR=/data
mkdir -p ${TEST_WORKDIR}
cd ${TEST_WORKDIR}
curl http://www.robots.ox.ac.uk/~vgg/data/flowers/17/17flowers.tgz --output 17flowers.tgz
tar zxf 17flowers.tgz
