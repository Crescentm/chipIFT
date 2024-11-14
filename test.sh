#!/usr/bin/env bash

TEST_PATH=$1

for dir in "$TEST_PATH"/*; do
    if [ -d $dir ] && [ -e $dir/config.json ]; then
        echo "processing $dir" >&2
        echo "processing $dir"
        base=$(basename $dir)
        filename_1=$(echo "$base" | cut -d'-' -f1)
        filename_2=$(echo "$base" | cut -d'-' -f2)
        python -m src.main \
            -f $dir/"$filename_1"_"$filename_2.v" \
            -c $dir/config.json \
            -o ./result \
            -I $dir
    fi
done
