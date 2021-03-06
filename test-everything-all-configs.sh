#!/bin/bash
# Copyright 2017 Google Inc. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");

. $(dirname $0)/common.sh

# PARENT_DIR="RUN_EVERY_BENCHMARK"
# #[[ -e "$PARENT_DIR" ]] && echo "Rename folder $PARENT_DIR to avoid deletion" && exit 1
# rm -rf $PARENT_DIR
# mkdir $PARENT_DIR
# echo "Created top directory $PARENT_DIR"

ABS_SCRIPT_DIR=$(readlink -f $SCRIPT_DIR)
BENCHMARKS=${ABS_SCRIPT_DIR}/*/

# Collect valid benchmarks
BS=()

for f in $BENCHMARKS
do
  file_name="$(basename $f)"
  [[ ! -d $f ]] && continue # echo "${file_name} isn't a directory" && continue
  [[ ! -e ${f}build.sh ]] && continue # echo "${file_name} has no build script" && continue
  [[ -e ${f}IGNORE ]] && continue # Explicitly ignored
  # echo "Running test $file_name"
  # (cd $PARENT_DIR && ${ABS_SCRIPT_DIR}/build-and-test.sh "${file_name}" > from-${file_name}.out 2>&1  &) # && sleep 10
  # (${ABS_SCRIPT_DIR}/test-only.sh "${file_name}" > run-${file_name}.out 2>&1  && sleep 5)
  BS+=("$file_name")
done

# Rund all configs and 2 benchmarks in parallel: 3 * 2 * 10 = 60 cores
CONFIGS=( "baseline" "cfd2" "cfd3" )
GROUP=1

for((i=0; i < ${#BS[@]}; i+=GROUP))
do
  BS_GROUP=( "${BS[@]:i:GROUP}" )
  echo ""
  echo "Running benchmarks in parallel: ${BS_GROUP[*]}"
  for file_name in ${BS_GROUP[*]}
  do
    for cfg in ${CONFIGS[@]}
    do
      path="$cfg/$file_name"
      echo "Running $path"
      (${ABS_SCRIPT_DIR}/test-only.sh "${path}" > "$cfg/run-${file_name}.out" 2>&1) &
    done
  done
  sleep $MAX_TOTAL_TIME
  sleep 10
done

# Collect results after running
rm -rf results
mkdir results

for cfg in ${CONFIGS[@]}
do
  echo "Collecting results for config: $cfg"
  cd $cfg
  ${ABS_SCRIPT_DIR}/collect-results.sh
  cd ..

  cp -r $cfg/results results/$cfg
done
