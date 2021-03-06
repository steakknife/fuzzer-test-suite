#!/bin/bash
# Copyright 2016 Google Inc. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
. $(dirname $0)/common.sh
# Get just the last component with basename, since we might call it with 'simpler/boringssl'
BUILD=$SCRIPT_DIR/$(basename $1)/build.sh
# TEST=$SCRIPT_DIR/$1/test-libfuzzer.sh

[ ! -e $BUILD ] && echo "NO SUCH FILE: $BUILD" && exit 1
# [ ! -e $TEST ]  && echo "NO SUCH FILE: $TEST" && exit 1

# RUNDIR="RUNDIR-$1"
RUNDIR="$1"
mkdir -p $RUNDIR
cd $RUNDIR
$BUILD # && $TEST

