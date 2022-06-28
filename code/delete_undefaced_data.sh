#!/bin/bash

subs=$(awk '$5=="data2" {print $2}' sourcedata/name2id.tsv)
for sub in $subs
do
    for ses in $sub/*
    do
        defaced_file=$(ls $ses/anat/deface*nii.gz)
        undefaced_file=$(ls $ses/anat/sub*nii.gz)
        rm $undefaced_file
        mv $defaced_file $undefaced_file
    done
done

