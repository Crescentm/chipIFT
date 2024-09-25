#!/usr/bin/env bash

TEST_PATH=$1
script=./scripts/get_port_property.py 

for dir in "$TEST_PATH"/*; do
    if [ -d $dir ]; then
        echo "generate $dir"
        base=$(basename $dir)
        topname=$(echo $base | cut -d'-' -f1)
        $script $dir $topname
    fi
done
    
