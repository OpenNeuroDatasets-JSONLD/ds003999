#!/bin/bash

for sub in data/sub-*
do
    echo ${sub}
    if ! [[ -d nii_data/${sub} ]]; then mkdir -p nii_data/${sub}; fi
    dcm2niix -b o -f '%n_%f_%p_%t_%s' -o nii_data/${sub} ${sub}
done

mv nii_data/data/* nii_data/ && rm nii_data/data/ -r
