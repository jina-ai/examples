#!/bin/bash
# find all the examples with changed code
# run the tests in that directory
changedExamples=()

for changed_file in $CHANGED_FILES; do
  echo changed $changed_file
  file_base_dir=$(echo $changed_file | cut -d/ -f1)
  # if the example has not yet been added
  if [[ ! " ${changedExamples[@]} " =~ " ${file_base_dir} " ]]; then
    echo adding $file_base_dir
    changedExamples+=(${file_base_dir})
  fi
done

echo will run tests on ${changedExamples[@]}

EXIT_CODE=0

root_dir=$(pwd)
# install reqs and run the tests
for example_dir in ${changedExamples[@]}; do
  cd $root_dir/$example_dir
  echo running tests in $example_dir
  pwd
  if test -f "tests/requirements.txt"; then
    if [[ -d "tests/" ]]; then
      python -m venv .venv
      source .venv/bin/activate
      pip install pytest pytest-mock
      pip install -r tests/requirements.txt
      pytest -s -v tests/
      local_exit_code=$?
      deactivate
      if [[ ! $local_exit_code == 0 ]]; then
        EXIT_CODE=$local_exit_code
        echo this one failed. local_exit_code = $local_exit_code, exit = $EXIT_CODE
      fi
    else
      echo 'no tests/ folder here. skipping...'
    fi
  else
    echo 'this is not an example. skipping...'
  fi
done

echo final exit code = $EXIT_CODE
exit $EXIT_CODE
