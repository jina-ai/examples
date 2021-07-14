#!/bin/bash
# required for downloading data from S3
pip install -e git://github.com/jina-ai/cloud-helper.git@v0.0.2#egg=jinacld_tools

cd ..
reqs=`find . -name "requirements.txt"`
folders=()
for req in $reqs; do
  module=`dirname $req`
  if test -f "$module/setup_run.sh"; then
    echo "$module has 'setup_run.sh'. will be run"
    folders+=($module)
  fi
done

for folder in $folders; do
  cd $folder &&
  pip install -r requirements.txt && \
  bash setup_run.sh && \
  cd ..
done

if test -f "performance.txt"; then
  rm performance.txt
fi

metrics=`find . -name "metrics.txt"`
for file_m in $metrics; do
  echo `dirname $file_m` >> performance.txt &&
  cat $file_m | grep "QPS: " | grep "takes" >> performance.txt
done