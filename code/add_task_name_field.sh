#!/bin/bash

needed_files=$(bids-validator --verbose --json sourcedata/ | jq '.issues.errors[0].files[].file.relativePath' | sed 's/nii.gz"$/json/; s/^"/sourcedata/')

#Add TaskName field according to bids_validator error
for file in $needed_files;
do
    echo -e $(cat $file | jq '. += {"TaskName": "rest"}') > $file
    python -m json.tool $file > ${file}_tmp && rm $file && mv ${file}_tmp $file
done

