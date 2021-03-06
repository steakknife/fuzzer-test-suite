#!/bin/bash
# Copyright 2016 Google Inc. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
. $(dirname $0)/../common.sh
set -x
rm -rf $CORPUS
mkdir $CORPUS

# seed.png was generated by this command:
# onvert -background white -size 80x label:"X" -trim +repage seed.png

test_source_location() {
  SRC_LOC="$1"
  echo "test_source_location: $SRC_LOC"
  rm -f *.log
  # This target has a 2Gb malloc oom, so we have to use rss_limit_mb=3000
  [ -e $EXECUTABLE_NAME_BASE ] && \
    ./$EXECUTABLE_NAME_BASE -seed=$SEED -max_total_time=$MAX_TOTAL_TIME -reload=$RELOAD -verbosity=$VERBOSITY -print_new_units=$PRINT_NEW_UNITS -print_pcs=$PRINT_PCS -print_funcs=$PRINT_FUNCS -print_final_stats=$PRINT_FINAL_STATS -print_corpus_stats=$PRINT_CORPUS_STATS -print_coverage=$PRINT_COVERAGE -close_fd_mask=3 -artifact_prefix=$CORPUS/ -exit_on_src_pos=$SRC_LOC  -jobs=$JOBS -workers=$JOBS $CORPUS $SCRIPT_DIR/seeds -rss_limit_mb=3000
    # -runs=100000000 
  grep "INFO: found line matching '$SRC_LOC'" fuzz-*.log || exit 1
}

# test_source_location png.c:1035
# test_source_location pngrutil.c:1041
# test_source_location pngread.c:757
# The following currently require too much time to find.
test_source_location pngrutil.c:1393
#test_source_location pngread.c:738
#test_source_location pngrutil.c:3182
#test_source_location pngrutil.c:139
