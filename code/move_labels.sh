#!/bin/bash
set -Eeuo pipefail

echo "*lesion_roi.nii.gz" >> .bidsignore

for file in $(ls tmp_labels)
do
    num=${file%.nii.gz}
    new_name=sub-${num}/ses-pre/anat/sub-${num}_ses-pre_T1w_label-lesion_roi.nii.gz

    mv tmp_labels/$file $new_name
done

rm tmp_labels -r 
