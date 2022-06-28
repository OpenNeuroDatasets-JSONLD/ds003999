#!/bin/bash

subs=$(cat sourcedata/name2id.tsv | awk '$7=="TRUE" {print $2}' | sed 's/^/rawdata\//')

for sub in $subs;
do
    id=$(basename $sub)
    id=${id#"sub-"}
    echo -e "Subject $id is processing now..."
    for ses in ${sub}/*;
    do
        session_name=$(basename $ses)
        session_name=${session_name%"ses"}
        echo "...work on ${session_name}-session.."

        dcm2bids -d $ses -p $id -s $session_name -c code/dcm2bids.conf.json -o $(pwd) --clobber && echo done
    done
done


